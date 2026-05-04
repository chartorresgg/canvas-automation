"""
Pruebas unitarias para ZipProcessor.

Estrategia:
    - ZIPs reales creados en tmp_path para tests de extracción.
    - Mock de FileNormalizer para tests unitarios puros (sin acoplamiento).
    - FileNormalizer real para el test de integración del flujo completo.
"""

from __future__ import annotations

import io
import shutil
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from app.domain.services.file_normalizer import FileNormalizer, NormalizationResult
from app.domain.services.zip_processor import (
    ExtractionResult,
    ProcessingResult,
    ZipProcessor,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _crear_zip(destino: Path, archivos: dict[str, str]) -> Path:
    """
    Crea un archivo ZIP real en disco con los archivos indicados.

    Args:
        destino:  Directorio donde se escribe el ZIP.
        archivos: {ruta_dentro_del_zip: contenido_str}

    Returns:
        Path al archivo ZIP creado.
    """
    zip_path = destino / "curso.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for ruta, contenido in archivos.items():
            zf.writestr(ruta, contenido)
    return zip_path


def _zip_estructura_minima(destino: Path) -> Path:
    """ZIP con la estructura mínima válida que espera el sistema."""
    return _crear_zip(destino, {
        "1. Archivos/1. Presentación/index.html": "<html>presentacion</html>",
        "1. Archivos/2. Material fundamental/U1_Lectura_Fundamental.pdf": "pdf",
        "1. Archivos/3. Material de trabajo/U1_Actividad.pdf": "pdf",
        "1. Archivos/5. Cierre/index.html": "<html>cierre</html>",
    })


def _normalizer_mock() -> MagicMock:
    """Mock de FileNormalizer con resultados exitosos por defecto."""
    mock = MagicMock(spec=FileNormalizer)
    mock.normalize_folders.return_value = NormalizationResult(
        folders_renamed=["variante → 1. Archivos"]
    )
    mock.normalize_pdfs.return_value = NormalizationResult(
        files_renamed=["viejo.pdf → U1_Lectura_Fundamental.pdf"]
    )
    return mock


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_zip(tmp_path: Path) -> Path:
    """ZIP válido con estructura mínima correcta."""
    return _zip_estructura_minima(tmp_path)


@pytest.fixture
def extract_dir(tmp_path: Path) -> Path:
    """Directorio de extracción (no existe todavía — ZipProcessor lo crea)."""
    return tmp_path / "extracted"


@pytest.fixture
def processor(tmp_zip: Path, extract_dir: Path) -> ZipProcessor:
    """ZipProcessor con FileNormalizer mockeado — tests unitarios puros."""
    return ZipProcessor(
        zip_path=tmp_zip,
        extract_dir=extract_dir,
        normalizer=_normalizer_mock(),
    )


@pytest.fixture
def processor_extraido(processor: ZipProcessor) -> ZipProcessor:
    """ZipProcessor con extract() ya ejecutado — tests de normalize/cleanup."""
    processor.extract()
    return processor


# ──────────────────────────────────────────────────────────────────────────────
# Tests: ExtractionResult
# ──────────────────────────────────────────────────────────────────────────────

class TestExtractionResult:
    """Pruebas para el value object ExtractionResult."""

    def test_total_size_mb_convierte_correctamente(self, tmp_path: Path) -> None:
        result = ExtractionResult(
            extract_dir=tmp_path,
            total_files=5,
            total_size_bytes=1_048_576,  # 1 MB exacto
        )
        assert result.total_size_mb == 1.0

    def test_total_size_mb_redondea_a_dos_decimales(self, tmp_path: Path) -> None:
        result = ExtractionResult(
            extract_dir=tmp_path,
            total_files=1,
            total_size_bytes=1_500_000,
        )
        assert result.total_size_mb == 1.43

    def test_total_size_mb_cero(self, tmp_path: Path) -> None:
        result = ExtractionResult(
            extract_dir=tmp_path,
            total_files=0,
            total_size_bytes=0,
        )
        assert result.total_size_mb == 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Tests: ProcessingResult
# ──────────────────────────────────────────────────────────────────────────────

class TestProcessingResult:
    """Pruebas para el value object ProcessingResult."""

    def _make_result(
        self,
        tmp_path: Path,
        folder_errors: list[str] | None = None,
        pdf_errors: list[str] | None = None,
        folder_warnings: list[str] | None = None,
        pdf_warnings: list[str] | None = None,
    ) -> ProcessingResult:
        return ProcessingResult(
            extraction=ExtractionResult(tmp_path, 0, 0),
            normalization_folders=NormalizationResult(
                errors=folder_errors or [],
                warnings=folder_warnings or [],
                folders_renamed=["a → b"],
            ),
            normalization_pdfs=NormalizationResult(
                errors=pdf_errors or [],
                warnings=pdf_warnings or [],
                files_renamed=["x.pdf → y.pdf"],
            ),
            content_path=tmp_path / "1. Archivos",
        )

    def test_success_true_sin_errores(self, tmp_path: Path) -> None:
        result = self._make_result(tmp_path)
        assert result.success is True

    def test_success_false_si_carpetas_tienen_error(self, tmp_path: Path) -> None:
        result = self._make_result(tmp_path, folder_errors=["fallo"])
        assert result.success is False

    def test_success_false_si_pdfs_tienen_error(self, tmp_path: Path) -> None:
        result = self._make_result(tmp_path, pdf_errors=["fallo pdf"])
        assert result.success is False

    def test_all_warnings_combina_ambas_fases(self, tmp_path: Path) -> None:
        result = self._make_result(
            tmp_path,
            folder_warnings=["w1"],
            pdf_warnings=["w2", "w3"],
        )
        assert result.all_warnings == ["w1", "w2", "w3"]

    def test_all_warnings_vacio_sin_advertencias(self, tmp_path: Path) -> None:
        result = self._make_result(tmp_path)
        assert result.all_warnings == []

    def test_total_changes_suma_ambas_fases(self, tmp_path: Path) -> None:
        # 1 carpeta renombrada + 1 PDF renombrado = 2
        result = self._make_result(tmp_path)
        assert result.total_changes == 2


# ──────────────────────────────────────────────────────────────────────────────
# Tests: ZipProcessor — content_path
# ──────────────────────────────────────────────────────────────────────────────

class TestContentPath:
    """Pruebas para la propiedad content_path."""

    def test_lanza_error_antes_de_extract(self, processor: ZipProcessor) -> None:
        with pytest.raises(RuntimeError, match="extract\\(\\)"):
            _ = processor.content_path

    def test_retorna_ruta_correcta_despues_de_extract(
        self, processor_extraido: ZipProcessor, extract_dir: Path
    ) -> None:
        assert processor_extraido.content_path == extract_dir / "1. Archivos"

    def test_es_path_absoluto(
        self, processor_extraido: ZipProcessor
    ) -> None:
        assert processor_extraido.content_path.is_absolute()


# ──────────────────────────────────────────────────────────────────────────────
# Tests: ZipProcessor.extract()
# ──────────────────────────────────────────────────────────────────────────────

class TestExtract:
    """Pruebas para el método extract()."""

    def test_retorna_extraction_result(
        self, processor: ZipProcessor
    ) -> None:
        result = processor.extract()
        assert isinstance(result, ExtractionResult)

    def test_crea_directorio_si_no_existe(
        self, processor: ZipProcessor, extract_dir: Path
    ) -> None:
        assert not extract_dir.exists()
        processor.extract()
        assert extract_dir.is_dir()

    def test_extrae_archivos_al_directorio(
        self, processor: ZipProcessor, extract_dir: Path
    ) -> None:
        processor.extract()
        archivos = list(extract_dir.rglob("*"))
        assert len(archivos) > 0

    def test_cuenta_archivos_correctamente(
        self, tmp_path: Path, extract_dir: Path
    ) -> None:
        zip_path = _crear_zip(tmp_path, {
            "1. Archivos/a.pdf": "a",
            "1. Archivos/b.pdf": "b",
            "1. Archivos/c.html": "c",
        })
        proc = ZipProcessor(zip_path, extract_dir, _normalizer_mock())
        result = proc.extract()
        assert result.total_files == 3

    def test_calcula_tamanio_correctamente(
        self, tmp_path: Path, extract_dir: Path
    ) -> None:
        contenido = "x" * 1024  # 1 KB exacto
        zip_path = _crear_zip(tmp_path, {"1. Archivos/archivo.txt": contenido})
        proc = ZipProcessor(zip_path, extract_dir, _normalizer_mock())
        result = proc.extract()
        assert result.total_size_bytes == 1024

    def test_lanza_error_si_zip_no_existe(
        self, extract_dir: Path
    ) -> None:
        proc = ZipProcessor(
            zip_path=Path("/no/existe/archivo.zip"),
            extract_dir=extract_dir,
            normalizer=_normalizer_mock(),
        )
        with pytest.raises(FileNotFoundError, match="No se encontró"):
            proc.extract()

    def test_lanza_error_si_archivo_no_es_zip(
        self, tmp_path: Path, extract_dir: Path
    ) -> None:
        archivo_falso = tmp_path / "falso.zip"
        archivo_falso.write_text("esto no es un zip")
        proc = ZipProcessor(archivo_falso, extract_dir, _normalizer_mock())
        with pytest.raises(ValueError, match="no es un ZIP válido"):
            proc.extract()

    def test_habilita_extracted_flag(
        self, processor: ZipProcessor
    ) -> None:
        assert processor._extracted is False
        processor.extract()
        assert processor._extracted is True

    def test_zip_vacio_no_lanza_error(
        self, tmp_path: Path, extract_dir: Path
    ) -> None:
        zip_vacio = tmp_path / "vacio.zip"
        with zipfile.ZipFile(zip_vacio, "w"):
            pass  # ZIP sin contenido
        proc = ZipProcessor(zip_vacio, extract_dir, _normalizer_mock())
        result = proc.extract()
        assert result.total_files == 0


# ──────────────────────────────────────────────────────────────────────────────
# Tests: ZipProcessor — seguridad Zip Slip
# ──────────────────────────────────────────────────────────────────────────────

class TestZipSlipSecurity:
    """Pruebas de seguridad contra ataques de path traversal."""

    def _zip_con_ruta_peligrosa(self, tmp_path: Path, ruta: str) -> Path:
        zip_path = tmp_path / "peligroso.zip"
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr(ruta, "contenido malicioso")
        zip_path.write_bytes(buffer.getvalue())
        return zip_path

    def test_rechaza_ruta_con_punto_punto(
        self, tmp_path: Path, extract_dir: Path
    ) -> None:
        zip_path = self._zip_con_ruta_peligrosa(tmp_path, "../../../etc/passwd")
        proc = ZipProcessor(zip_path, extract_dir, _normalizer_mock())
        with pytest.raises(ValueError, match="peligrosa"):
            proc.extract()

    def test_rechaza_ruta_absoluta(
        self, tmp_path: Path, extract_dir: Path
    ) -> None:
        zip_path = self._zip_con_ruta_peligrosa(tmp_path, "/etc/passwd")
        proc = ZipProcessor(zip_path, extract_dir, _normalizer_mock())
        with pytest.raises(ValueError, match="peligrosa"):
            proc.extract()

    def test_acepta_rutas_normales(
        self, processor: ZipProcessor
    ) -> None:
        # No debe lanzar excepción con rutas normales
        result = processor.extract()
        assert result.total_files > 0


# ──────────────────────────────────────────────────────────────────────────────
# Tests: ZipProcessor.normalize()
# ──────────────────────────────────────────────────────────────────────────────

class TestNormalize:
    """Pruebas para el método normalize()."""

    def test_lanza_error_antes_de_extract(
        self, processor: ZipProcessor
    ) -> None:
        with pytest.raises(RuntimeError, match="extract\\(\\)"):
            processor.normalize()

    def test_retorna_processing_result(
        self, processor_extraido: ZipProcessor
    ) -> None:
        result = processor_extraido.normalize()
        assert isinstance(result, ProcessingResult)

    def test_llama_normalize_folders_con_extract_dir(
        self, processor_extraido: ZipProcessor, extract_dir: Path
    ) -> None:
        processor_extraido.normalize()
        processor_extraido._normalizer.normalize_folders.assert_called_once_with(
            extract_dir
        )

    def test_llama_normalize_pdfs_con_content_path(
        self, processor_extraido: ZipProcessor, extract_dir: Path
    ) -> None:
        processor_extraido.normalize()
        processor_extraido._normalizer.normalize_pdfs.assert_called_once_with(
            extract_dir / "1. Archivos"
        )

    def test_normalize_folders_se_llama_antes_que_normalize_pdfs(
        self, processor_extraido: ZipProcessor
    ) -> None:
        """El orden de las llamadas es crítico: carpetas primero, PDFs después."""
        manager = MagicMock()
        manager.attach_mock(
            processor_extraido._normalizer.normalize_folders, "normalize_folders"
        )
        manager.attach_mock(
            processor_extraido._normalizer.normalize_pdfs, "normalize_pdfs"
        )
        processor_extraido.normalize()
        llamadas = [c[0] for c in manager.mock_calls]
        assert llamadas.index("normalize_folders") < llamadas.index("normalize_pdfs")

    def test_result_incluye_content_path_correcto(
        self, processor_extraido: ZipProcessor, extract_dir: Path
    ) -> None:
        result = processor_extraido.normalize()
        assert result.content_path == extract_dir / "1. Archivos"

    def test_result_refleja_cambios_del_normalizer(
        self, processor_extraido: ZipProcessor
    ) -> None:
        result = processor_extraido.normalize()
        # El mock devuelve 1 carpeta + 1 PDF renombrado
        assert result.total_changes == 2

    def test_warnings_del_normalizer_se_propagan(
        self, tmp_zip: Path, extract_dir: Path
    ) -> None:
        mock = _normalizer_mock()
        mock.normalize_pdfs.return_value = NormalizationResult(
            warnings=["PDF sin unidad detectada: archivo.pdf"]
        )
        proc = ZipProcessor(tmp_zip, extract_dir, mock)
        proc.extract()
        result = proc.normalize()
        assert len(result.all_warnings) == 1


# ──────────────────────────────────────────────────────────────────────────────
# Tests: ZipProcessor.cleanup()
# ──────────────────────────────────────────────────────────────────────────────

class TestCleanup:
    """Pruebas para el método cleanup()."""

    def test_elimina_directorio_existente(
        self, processor_extraido: ZipProcessor, extract_dir: Path
    ) -> None:
        assert extract_dir.exists()
        processor_extraido.cleanup()
        assert not extract_dir.exists()

    def test_no_lanza_error_si_directorio_no_existe(
        self, processor: ZipProcessor, extract_dir: Path
    ) -> None:
        assert not extract_dir.exists()
        # No debe lanzar excepción
        processor.cleanup()

    def test_resetea_extracted_flag(
        self, processor_extraido: ZipProcessor
    ) -> None:
        assert processor_extraido._extracted is True
        processor_extraido.cleanup()
        assert processor_extraido._extracted is False

    def test_content_path_no_disponible_tras_cleanup(
        self, processor_extraido: ZipProcessor
    ) -> None:
        processor_extraido.cleanup()
        with pytest.raises(RuntimeError):
            _ = processor_extraido.content_path

    def test_cleanup_es_idempotente(
        self, processor_extraido: ZipProcessor
    ) -> None:
        """Llamar cleanup() dos veces no debe lanzar error."""
        processor_extraido.cleanup()
        processor_extraido.cleanup()  # segunda llamada segura


# ──────────────────────────────────────────────────────────────────────────────
# Test de integración — flujo completo con FileNormalizer real
# ──────────────────────────────────────────────────────────────────────────────

class TestIntegracionFlujoCompleto:
    """
    Prueba el flujo completo con FileNormalizer real (sin mocks).
    Valida que ZipProcessor y FileNormalizer colaboran correctamente.
    """

    def test_flujo_extract_normalize_cleanup(self, tmp_path: Path) -> None:
        """
        Happy path completo:
        extract() → normalize() → verificar content_path → cleanup()
        """
        zip_path = _crear_zip(tmp_path, {
            "1 Archivos/presentacion/index.html":      "<html>p</html>",
            "1 Archivos/Material Fundamental/U1_Lectura_Fundamental.pdf": "pdf1",
            "1 Archivos/material de trabajo/U1_Actividad.pdf":            "pdf2",
            "1 Archivos/cierre/index.html":             "<html>c</html>",
        })

        extract_dir = tmp_path / "output"
        proc = ZipProcessor(
            zip_path=zip_path,
            extract_dir=extract_dir,
            normalizer=FileNormalizer(),  # real, sin mock
        )

        # 1. Extraer
        ext_result = proc.extract()
        assert ext_result.total_files == 4
        assert extract_dir.is_dir()

        # 2. Normalizar
        proc_result = proc.normalize()
        assert proc_result.success

        # 3. Verificar que "1. Archivos" existe con nombre canónico
        assert proc.content_path.is_dir()
        assert proc.content_path.name == "1. Archivos"

        # 4. Verificar subcarpetas normalizadas
        nombres_subcarpetas = {e.name for e in proc.content_path.iterdir()}
        assert "1. Presentación" in nombres_subcarpetas
        assert "2. Material fundamental" in nombres_subcarpetas

        # 5. Cleanup
        proc.cleanup()
        assert not extract_dir.exists()
        assert proc._extracted is False