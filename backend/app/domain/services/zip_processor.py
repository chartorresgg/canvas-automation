"""
Servicio de procesamiento de archivos ZIP para aulas Canvas LMS.
Orquesta la extracción y delega la normalización en FileNormalizer.

Capa: Dominio
Patrón: ninguno (servicio de dominio — orquesta FileNormalizer)
Colaboradores: FileNormalizer
Dependencias externas: zipfile (stdlib), shutil (stdlib)
"""

from __future__ import annotations

import logging
import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from app.domain.services.file_normalizer import FileNormalizer, NormalizationResult

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Value Objects de resultado
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ExtractionResult:
    """
    Métricas de la operación de extracción del ZIP.
    Permite al orquestador registrar en auditoría sin acoplar lógica de logging.
    """
    extract_dir: Path
    total_files: int
    total_size_bytes: int

    @property
    def total_size_mb(self) -> float:
        """Tamaño total de los archivos extraídos en megabytes."""
        return round(self.total_size_bytes / (1024 * 1024), 2)


@dataclass
class ProcessingResult:
    """
    Resultado completo del procesamiento: extracción + normalización.
    Agrega los resultados de ambas fases para que el orquestador
    pueda registrarlos y emitirlos como ProgressEvent.
    """
    extraction: ExtractionResult
    normalization_folders: NormalizationResult
    normalization_pdfs: NormalizationResult
    content_path: Path

    @property
    def success(self) -> bool:
        """True si ninguna fase de normalización tuvo errores."""
        return (
            self.normalization_folders.success
            and self.normalization_pdfs.success
        )

    @property
    def all_warnings(self) -> list[str]:
        """Unión de advertencias de ambas fases de normalización."""
        return (
            self.normalization_folders.warnings
            + self.normalization_pdfs.warnings
        )

    @property
    def total_changes(self) -> int:
        """Total de carpetas y archivos renombrados en ambas fases."""
        return (
            self.normalization_folders.total_changes
            + self.normalization_pdfs.total_changes
        )


# ──────────────────────────────────────────────────────────────────────────────
# Servicio principal
# ──────────────────────────────────────────────────────────────────────────────

class ZipProcessor:
    """
    Orquesta la extracción y normalización estructural del archivo ZIP
    que contiene los materiales de un aula virtual Canvas.

    Responsabilidad única (SRP): coordinar extracción + delegación a
    FileNormalizer. No conoce las reglas de normalización ni los detalles
    de Canvas LMS.

    Ciclo de vida esperado (impuesto por DeploymentOrchestrator):
        1. result   = zip_proc.extract()    → extrae en directorio temporal
        2. proc_res = zip_proc.normalize()  → normaliza estructura
        3.            zip_proc.content_path → Path a "1. Archivos"
        4.            zip_proc.cleanup()    → elimina temporales al finalizar

    Colaboradores:
        FileNormalizer — aplica convenciones institucionales de nombres
    """

    def __init__(
        self,
        zip_path: Path,
        extract_dir: Path,
        normalizer: FileNormalizer | None = None,
    ) -> None:
        """
        Args:
            zip_path:    Ruta al archivo .zip a procesar.
            extract_dir: Directorio donde se extraerá el contenido.
            normalizer:  Instancia de FileNormalizer. Si es None se crea
                         una por defecto. Inyectarla facilita el testing.
        """
        self._zip_path = zip_path
        self._extract_dir = extract_dir
        self._normalizer: FileNormalizer = normalizer or FileNormalizer()
        self._extracted: bool = False

    # ──────────────────────────────────────────────────────────────
    # Propiedades públicas
    # ──────────────────────────────────────────────────────────────

    @property
    def content_path(self) -> Path:
        """
        Ruta a la carpeta "1. Archivos" dentro del directorio extraído.

        Esta propiedad es el contrato que FileRepository consume para
        saber desde dónde recorrer los archivos a subir a Canvas.

        Raises:
            RuntimeError: Si se accede antes de llamar a extract().
        """
        if not self._extracted:
            raise RuntimeError(
                "content_path no está disponible antes de llamar a extract(). "
                "Ejecuta extract() primero."
            )
        return self._extract_dir / "1. Archivos"

    # ──────────────────────────────────────────────────────────────
    # API pública
    # ──────────────────────────────────────────────────────────────

    def extract(self) -> ExtractionResult:
        """
        Extrae el contenido del archivo ZIP en el directorio de destino.

        Crea el directorio de extracción si no existe. Valida seguridad
        contra ataques de path traversal (Zip Slip) antes de extraer.

        Returns:
            ExtractionResult con métricas de la extracción.

        Raises:
            FileNotFoundError: Si zip_path no existe en disco.
            ValueError:        Si el archivo no es un ZIP válido o contiene
                               rutas peligrosas (Zip Slip).
            zipfile.BadZipFile: Si el archivo ZIP está corrupto.
        """
        if not self._zip_path.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo ZIP: {self._zip_path}"
            )

        if not zipfile.is_zipfile(self._zip_path):
            raise ValueError(
                f"El archivo no es un ZIP válido: {self._zip_path.name}"
            )

        self._extract_dir.mkdir(parents=True, exist_ok=True)

        total_files = 0
        total_size_bytes = 0

        with zipfile.ZipFile(self._zip_path, "r") as zf:
            self._validar_seguridad_zip(zf)

            infos = zf.infolist()

            if not infos:
                logger.warning(
                    "El archivo ZIP está vacío: %s", self._zip_path.name
                )

            for info in infos:
                if not info.is_dir():
                    total_files += 1
                    total_size_bytes += info.file_size

            zf.extractall(self._extract_dir)

        self._extracted = True

        result = ExtractionResult(
            extract_dir=self._extract_dir,
            total_files=total_files,
            total_size_bytes=total_size_bytes,
        )

        logger.info(
            "ZIP extraído: %d archivos (%.2f MB) → '%s'",
            total_files,
            result.total_size_mb,
            self._extract_dir,
        )

        return result

    def normalize(self) -> ProcessingResult:
        """
        Normaliza la estructura de carpetas y archivos PDF extraídos.

        Delega completamente en FileNormalizer. Debe llamarse después
        de extract(). Los warnings se registran en el log pero no
        detienen el procesamiento.

        Returns:
            ProcessingResult con el detalle de todos los cambios realizados.

        Raises:
            RuntimeError:      Si se llama antes de extract().
            FileNotFoundError: Si FileNormalizer no encuentra "1. Archivos".
        """
        if not self._extracted:
            raise RuntimeError(
                "Debe llamar a extract() antes de normalize()."
            )

        logger.info(
            "Normalizando estructura de carpetas en: '%s'", self._extract_dir
        )

        result_folders = self._normalizer.normalize_folders(self._extract_dir)

        for warning in result_folders.warnings:
            logger.warning("Carpetas: %s", warning)

        logger.info(
            "Normalizando PDFs en: '%s'", self.content_path
        )

        result_pdfs = self._normalizer.normalize_pdfs(self.content_path)

        for warning in result_pdfs.warnings:
            logger.warning("PDFs: %s", warning)

        processing_result = ProcessingResult(
            extraction=ExtractionResult(
                extract_dir=self._extract_dir,
                total_files=0,
                total_size_bytes=0,
            ),
            normalization_folders=result_folders,
            normalization_pdfs=result_pdfs,
            content_path=self.content_path,
        )

        logger.info(
            "Normalización completada: %d cambio(s) totales, %d advertencia(s).",
            processing_result.total_changes,
            len(processing_result.all_warnings),
        )

        return processing_result

    def cleanup(self) -> None:
        """
        Elimina el directorio de extracción temporal y todo su contenido.

        Operación idempotente: si el directorio ya no existe no lanza error.
        Debe llamarse siempre al finalizar el despliegue (éxito o fallo)
        para liberar espacio en disco.
        """
        if self._extract_dir.exists():
            shutil.rmtree(self._extract_dir)
            logger.info(
                "Directorio temporal eliminado: '%s'", self._extract_dir
            )
        else:
            logger.debug(
                "cleanup() llamado pero el directorio ya no existe: '%s'",
                self._extract_dir,
            )

        self._extracted = False

    # ──────────────────────────────────────────────────────────────
    # Privados
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _validar_seguridad_zip(zf: zipfile.ZipFile) -> None:
        """
        Protege contra ataques Zip Slip (path traversal).

        Un ZIP malicioso puede contener rutas absolutas o con ".." que al
        extraerse sobreescriben archivos fuera del directorio destino.
        Este método rechaza el ZIP completo si detecta alguna ruta peligrosa.

        Args:
            zf: Archivo ZIP abierto en modo lectura.

        Raises:
            ValueError: Si cualquier entrada contiene ruta peligrosa.
        """
        for nombre in zf.namelist():
            # Ruta absoluta o path traversal con ".."
            if nombre.startswith("/") or ".." in nombre.split("/"):
                raise ValueError(
                    f"ZIP contiene ruta peligrosa (Zip Slip): '{nombre}'. "
                    "Extracción cancelada por seguridad."
                )