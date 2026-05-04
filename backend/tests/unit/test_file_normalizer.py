"""
Pruebas unitarias para FileNormalizer.

Estrategia: usar el fixture tmp_path de pytest para crear estructuras de
directorios reales en disco. No se usan mocks porque FileNormalizer opera
directamente sobre el sistema de archivos — el comportamiento real ES el test.
"""

import pytest
from pathlib import Path
from app.domain.services.file_normalizer import FileNormalizer, NormalizationResult


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def normalizer() -> FileNormalizer:
    """Instancia limpia de FileNormalizer para cada test."""
    return FileNormalizer()


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    """
    Directorio temporal raíz que simula el contenido extraído de un ZIP.
    tmp_path es provisto por pytest y se elimina automáticamente al finalizar.
    """
    return tmp_path


def crear_estructura_valida(base: Path) -> Path:
    """
    Helper: crea una estructura de carpetas válida con nombre canónico.
    Retorna la ruta a "1. Archivos".
    """
    ruta_archivos = base / "1. Archivos"
    ruta_archivos.mkdir()
    (ruta_archivos / "1. Presentación").mkdir()
    (ruta_archivos / "2. Material fundamental").mkdir()
    (ruta_archivos / "3. Material de trabajo").mkdir()
    (ruta_archivos / "4. Complementos").mkdir()
    (ruta_archivos / "5. Cierre").mkdir()
    return ruta_archivos


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _clean_text
# ──────────────────────────────────────────────────────────────────────────────

class TestCleanText:
    """Pruebas para el método utilitario _clean_text."""

    def test_elimina_tildes(self, normalizer: FileNormalizer) -> None:
        assert normalizer._clean_text("Presentación") == "presentacion"

    def test_convierte_a_minusculas(self, normalizer: FileNormalizer) -> None:
        assert normalizer._clean_text("MATERIAL") == "material"

    def test_elimina_espacios(self, normalizer: FileNormalizer) -> None:
        assert normalizer._clean_text("Material de Trabajo") == "materialdetrabajo"

    def test_elimina_guiones_bajos(self, normalizer: FileNormalizer) -> None:
        assert normalizer._clean_text("material_fundamental") == "materialfundamental"

    def test_elimina_puntos(self, normalizer: FileNormalizer) -> None:
        assert normalizer._clean_text("1. Archivos") == "1archivos"

    def test_cadena_vacia(self, normalizer: FileNormalizer) -> None:
        assert normalizer._clean_text("") == ""

    def test_combinacion_completa(self, normalizer: FileNormalizer) -> None:
        assert normalizer._clean_text("  Ñoño_Ü ") == "nonou"


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _detect_unit
# ──────────────────────────────────────────────────────────────────────────────

class TestDetectUnit:
    """Pruebas para la detección de número de unidad en nombres de archivo."""

    @pytest.mark.parametrize("filename,expected", [
        ("U1_Material_Fundamental",       "1"),
        ("u2_Lectura_Fundamental",        "2"),
        ("U 3_Actividad_Formativa",       "3"),
        ("Unidad4_Material",              "4"),
        ("Unidad 1 Lectura",              "1"),
        ("MF_U2_contenido",               "2"),
        ("GM_U3_complemento",             "3"),
    ])
    def test_patrones_validos(
        self, normalizer: FileNormalizer, filename: str, expected: str
    ) -> None:
        assert normalizer._detect_unit(filename) == expected

    @pytest.mark.parametrize("filename", [
        "Material_Fundamental",
        "Lectura_sin_unidad",
        "complemento",
        "",
    ])
    def test_retorna_none_sin_unidad(
        self, normalizer: FileNormalizer, filename: str
    ) -> None:
        assert normalizer._detect_unit(filename) is None

    def test_no_coincide_con_u_dentro_de_palabra(
        self, normalizer: FileNormalizer
    ) -> None:
        """'fundamental' contiene 'u' pero no debe detectar unidad."""
        resultado = normalizer._detect_unit("Material_Fundamental")
        assert resultado is None


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _detect_pdf_type
# ──────────────────────────────────────────────────────────────────────────────

class TestDetectPdfType:
    """Pruebas para la detección del tipo canónico de PDF."""

    @pytest.mark.parametrize("filename,expected", [
        ("U1_Material_Fundamental",    "Material_Fundamental"),
        ("U1_MF",                      "Material_Fundamental"),
        ("U2_Lectura_Fundamental",     "Lectura_Fundamental"),
        ("U2_Lectura",                 "Lectura_Fundamental"),
        ("U3_Actividad_Formativa",     "Actividad_Formativa"),
        ("U3_Formativa",               "Actividad_Formativa"),
        ("U2_Actividad_Sumativa",      "Actividad_Sumativa"),
        ("U4_Sumativa",                "Actividad_Sumativa"),
        ("U1_Actividad",               "Actividad"),
    ])
    def test_tipos_reconocidos(
        self, normalizer: FileNormalizer, filename: str, expected: str
    ) -> None:
        assert normalizer._detect_pdf_type(filename) == expected

    def test_material_fundamental_tiene_precedencia_sobre_actividad(
        self, normalizer: FileNormalizer
    ) -> None:
        """'Material_Fundamental' no debe confundirse con 'Actividad'."""
        assert normalizer._detect_pdf_type("U1_Material_Fundamental") == "Material_Fundamental"

    def test_retorna_none_si_no_reconoce(
        self, normalizer: FileNormalizer
    ) -> None:
        assert normalizer._detect_pdf_type("U1_Desconocido_XYZ") is None

    def test_retorna_none_cadena_vacia(
        self, normalizer: FileNormalizer
    ) -> None:
        assert normalizer._detect_pdf_type("") is None


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _detect_sequence_number
# ──────────────────────────────────────────────────────────────────────────────

class TestDetectSequenceNumber:
    """Pruebas para la detección del número secuencial al final del nombre."""

    @pytest.mark.parametrize("filename,expected", [
        ("Lectura_Fundamental_2",  2),
        ("Lectura_Fundamental_02", 2),
        ("LF02",                   2),
        ("Material1",              1),
        ("Actividad_3",            3),
    ])
    def test_detecta_numero_final(
        self, normalizer: FileNormalizer, filename: str, expected: int
    ) -> None:
        assert normalizer._detect_sequence_number(filename) == expected

    @pytest.mark.parametrize("filename", [
        "Lectura_Fundamental",
        "Material_Fundamental",
        "",
    ])
    def test_retorna_none_sin_numero(
        self, normalizer: FileNormalizer, filename: str
    ) -> None:
        assert normalizer._detect_sequence_number(filename) is None


# ──────────────────────────────────────────────────────────────────────────────
# Tests: normalize_folders — carpeta raíz
# ──────────────────────────────────────────────────────────────────────────────

class TestNormalizeFoldersRaiz:
    """Pruebas para la normalización de la carpeta raíz '1. Archivos'."""

    def test_no_renombra_si_ya_es_correcto(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        (base_dir / "1. Archivos").mkdir()
        result = normalizer.normalize_folders(base_dir)
        assert result.success
        assert len(result.folders_renamed) == 0

    def test_renombra_variante_con_numero(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        (base_dir / "1 Archivos").mkdir()
        result = normalizer.normalize_folders(base_dir)
        assert (base_dir / "1. Archivos").is_dir()
        assert any("1 Archivos" in msg for msg in result.folders_renamed)

    def test_renombra_variante_con_tilde(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        (base_dir / "1. Archivós").mkdir()
        result = normalizer.normalize_folders(base_dir)
        assert (base_dir / "1. Archivos").is_dir()

    def test_lanza_error_si_no_encuentra_carpeta_raiz(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        (base_dir / "otra_carpeta").mkdir()
        with pytest.raises(FileNotFoundError, match="1. Archivos"):
            normalizer.normalize_folders(base_dir)


# ──────────────────────────────────────────────────────────────────────────────
# Tests: normalize_folders — subcarpetas
# ──────────────────────────────────────────────────────────────────────────────

class TestNormalizeFoldersSubcarpetas:
    """Pruebas para la normalización de subcarpetas dentro de '1. Archivos'."""

    @pytest.mark.parametrize("nombre_original,nombre_canonico", [
        ("presentacion",              "1. Presentación"),
        ("Presentacion",              "1. Presentación"),
        ("presentación",              "1. Presentación"),
        ("Material Fundamental",      "2. Material fundamental"),
        ("material_fundamental",      "2. Material fundamental"),
        ("MaterialFundamental",       "2. Material fundamental"),
        ("Material de Trabajo",       "3. Material de trabajo"),
        ("materialdetrabajo",         "3. Material de trabajo"),
        ("Material Complementario",   "4. Complementos"),
        ("complementos",              "4. Complementos"),
        ("Complementarios",           "4. Complementos"),
        ("cierre",                    "5. Cierre"),
        ("Cierre",                    "5. Cierre"),
    ])
    def test_renombra_variante_a_canonico(
        self,
        normalizer: FileNormalizer,
        base_dir: Path,
        nombre_original: str,
        nombre_canonico: str,
    ) -> None:
        ruta_archivos = base_dir / "1. Archivos"
        ruta_archivos.mkdir()
        (ruta_archivos / nombre_original).mkdir()

        result = normalizer.normalize_folders(base_dir)

        assert (ruta_archivos / nombre_canonico).is_dir(), (
            f"Se esperaba '{nombre_canonico}' pero no existe. "
            f"Carpetas: {[e.name for e in ruta_archivos.iterdir()]}"
        )
        assert result.success

    def test_agrega_warning_si_subcarpeta_desconocida(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        ruta_archivos = base_dir / "1. Archivos"
        ruta_archivos.mkdir()
        (ruta_archivos / "carpeta_sin_nombre_reconocido").mkdir()

        result = normalizer.normalize_folders(base_dir)

        assert any("no reconocida" in w.lower() for w in result.warnings)

    def test_no_renombra_si_destino_ya_existe(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        ruta_archivos = base_dir / "1. Archivos"
        ruta_archivos.mkdir()
        (ruta_archivos / "cierre").mkdir()
        (ruta_archivos / "5. Cierre").mkdir()  # destino ya existe

        result = normalizer.normalize_folders(base_dir)

        assert any("ya existe" in w for w in result.warnings)


# ──────────────────────────────────────────────────────────────────────────────
# Tests: normalize_pdfs — Material fundamental
# ──────────────────────────────────────────────────────────────────────────────

class TestNormalizePdfsMaterialFundamental:
    """Pruebas para la normalización de PDFs en Material fundamental."""

    def test_renombra_pdf_unico_sin_secuencia(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        ruta_archivos = crear_estructura_valida(base_dir)
        ruta_mf = ruta_archivos / "2. Material fundamental"
        (ruta_mf / "MF_U1_contenido.pdf").touch()

        result = normalizer.normalize_pdfs(ruta_archivos)

        assert (ruta_mf / "U1_Material_Fundamental.pdf").exists()
        assert result.success

    def test_renombra_lectura_fundamental(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        ruta_archivos = crear_estructura_valida(base_dir)
        ruta_mf = ruta_archivos / "2. Material fundamental"
        (ruta_mf / "U2_Lectura_Fundamental.pdf").touch()

        result = normalizer.normalize_pdfs(ruta_archivos)

        # Ya tiene el nombre correcto, no debe renombrarse
        assert (ruta_mf / "U2_Lectura_Fundamental.pdf").exists()
        assert len(result.files_renamed) == 0

    def test_renombra_multiples_lecturas_con_secuencia(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        ruta_archivos = crear_estructura_valida(base_dir)
        ruta_mf = ruta_archivos / "2. Material fundamental"
        (ruta_mf / "U1_Lectura_v1.pdf").touch()
        (ruta_mf / "U1_Lectura_v2.pdf").touch()

        normalizer.normalize_pdfs(ruta_archivos)

        archivos = {f.name for f in ruta_mf.iterdir()}
        assert "U1_Lectura_Fundamental_1.pdf" in archivos or \
               "U1_Lectura_Fundamental_2.pdf" in archivos

    def test_warning_si_no_detecta_unidad(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        ruta_archivos = crear_estructura_valida(base_dir)
        ruta_mf = ruta_archivos / "2. Material fundamental"
        (ruta_mf / "sin_unidad_lectura.pdf").touch()

        result = normalizer.normalize_pdfs(ruta_archivos)

        assert any("unidad" in w.lower() for w in result.warnings)

    def test_warning_si_no_hay_carpeta_material_fundamental(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        ruta_archivos = base_dir / "1. Archivos"
        ruta_archivos.mkdir()
        # No se crea "2. Material fundamental"

        result = normalizer.normalize_pdfs(ruta_archivos)

        assert any("material fundamental" in w.lower() for w in result.warnings)


# ──────────────────────────────────────────────────────────────────────────────
# Tests: normalize_pdfs — Complementos
# ──────────────────────────────────────────────────────────────────────────────

class TestNormalizePdfsComplementos:
    """Pruebas para la normalización de PDFs en Complementos."""

    def test_renombra_complemento_unico(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        ruta_archivos = crear_estructura_valida(base_dir)
        ruta_comp = ruta_archivos / "4. Complementos"
        (ruta_comp / "lectura_complementaria_u3.pdf").touch()

        normalizer.normalize_pdfs(ruta_archivos)

        assert (ruta_comp / "U3_Complemento.pdf").exists()

    def test_renombra_multiples_complementos_por_unidad(
        self, normalizer: FileNormalizer, base_dir: Path
    ) -> None:
        ruta_archivos = crear_estructura_valida(base_dir)
        ruta_comp = ruta_archivos / "4. Complementos"
        (ruta_comp / "U1_complemento_a.pdf").touch()
        (ruta_comp / "U1_complemento_b.pdf").touch()

        normalizer.normalize_pdfs(ruta_archivos)

        archivos = {f.name for f in ruta_comp.iterdir()}
        assert len([a for a in archivos if a.startswith("U1_Complemento")]) == 2


# ──────────────────────────────────────────────────────────────────────────────
# Tests: NormalizationResult
# ──────────────────────────────────────────────────────────────────────────────

class TestNormalizationResult:
    """Pruebas para el value object NormalizationResult."""

    def test_success_true_sin_errores(self) -> None:
        result = NormalizationResult()
        assert result.success is True

    def test_success_false_con_errores(self) -> None:
        result = NormalizationResult(errors=["algo falló"])
        assert result.success is False

    def test_total_changes_suma_ambas_listas(self) -> None:
        result = NormalizationResult(
            folders_renamed=["a → b"],
            files_renamed=["x.pdf → y.pdf", "z.pdf → w.pdf"],
        )
        assert result.total_changes == 3