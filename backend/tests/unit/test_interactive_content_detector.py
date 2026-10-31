"""
Tests unitarios para InteractiveContentDetector.

Complementan los casos básicos de TestInteractiveContentDetector en
test_orchestrator.py: precedencia story.html/index.html, rutas ignoradas,
formatos de carpeta y la detección en Material de trabajo.

Los casos marcados con xfail(strict=True) describen el comportamiento correcto
de defectos conocidos: fallan hoy y avisarán cuando alguien los corrija.
"""

import logging

import pytest

from app.domain.services.interactive_content_detector import (
    InteractiveContentDetector,
)

MF = "2. Material fundamental"
MT = "3. Material de trabajo"


@pytest.fixture
def detector() -> InteractiveContentDetector:
    """Retorna una instancia del detector (servicio sin estado)."""
    return InteractiveContentDetector()


class TestDetect:

    def test_omite_carpeta_no_reconocida_y_conserva_las_validas(
        self,
        detector: InteractiveContentDetector,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        files_map = {
            f"{MF}/Carpeta_rara/story.html": 1,
            f"{MF}/MF_U1/story.html": 2,
        }

        with caplog.at_level(logging.WARNING):
            resultado = detector.detect(files_map)

        assert list(resultado) == [1]
        assert resultado[1][0]["file_id"] == 2
        assert "Carpeta_rara" in caplog.text

    def test_ignora_story_html_sin_subcarpeta_de_contenido(
        self, detector: InteractiveContentDetector
    ) -> None:
        assert detector.detect({f"{MF}/story.html": 1}) == {}

    @pytest.mark.parametrize("files_map", [
        {f"{MF}/MF_U1/story.html": 1, f"{MF}/MF_U1/index.html": 2},
        {f"{MF}/MF_U1/index.html": 2, f"{MF}/MF_U1/story.html": 1},
    ], ids=["story_primero", "index_primero"])
    def test_story_html_tiene_prioridad_sobre_index_html(
        self,
        detector: InteractiveContentDetector,
        files_map: dict[str, int],
    ) -> None:
        resultado = detector.detect(files_map)

        assert len(resultado[1]) == 1
        assert resultado[1][0]["file_id"] == 1

    def test_usa_index_html_cuando_no_hay_story_html(
        self, detector: InteractiveContentDetector
    ) -> None:
        resultado = detector.detect({f"{MF}/MF_U1/index.html": 7})

        assert resultado[1][0]["file_id"] == 7

    def test_reconoce_rutas_sin_distinguir_mayusculas(
        self, detector: InteractiveContentDetector
    ) -> None:
        resultado = detector.detect(
            {"2. MATERIAL FUNDAMENTAL/mf_u2/STORY.HTML": 9}
        )

        assert resultado[2][0]["file_id"] == 9

    def test_retorna_todos_los_datos_del_contenido_detectado(
        self, detector: InteractiveContentDetector
    ) -> None:
        ruta = f"{MF}/MF_U1_2/story.html"

        resultado = detector.detect({ruta: 5})

        assert resultado == {
            1: [{
                "numero": 2,
                "file_id": 5,
                "carpeta": "MF_U1_2",
                "ruta_completa": ruta,
                "es_enumerado": True,
            }],
        }

    def test_duplica_numero_si_dos_carpetas_apuntan_al_mismo_contenido(
        self, detector: InteractiveContentDetector
    ) -> None:
        # Caracterización: documenta el comportamiento actual, no el deseado.
        resultado = detector.detect({
            f"{MF}/U1_MF/story.html": 1,
            f"{MF}/MF_U1/story.html": 2,
        })

        assert [(c["numero"], c["file_id"]) for c in resultado[1]] == [
            (1, 1),
            (1, 2),
        ]

    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason="Defecto: la ruta se parte sin normalizar el separador '\\'",
    )
    def test_acepta_rutas_con_separador_de_windows(
        self, detector: InteractiveContentDetector
    ) -> None:
        resultado = detector.detect({f"{MF}\\MF_U1\\story.html": 1})

        assert 1 in resultado

    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason="Defecto: un story.html anidado sustituye al de la raíz",
    )
    def test_story_html_de_la_raiz_del_paquete_gana_al_anidado(
        self, detector: InteractiveContentDetector
    ) -> None:
        resultado = detector.detect({
            f"{MF}/U1_MF/story.html": 1,
            f"{MF}/U1_MF/backup/story.html": 2,
        })

        assert resultado[1][0]["file_id"] == 1


class TestParsearCarpeta:

    @pytest.mark.parametrize("carpeta,esperado", [
        ("U3_MF", (3, 1, False)),
        ("U3_MF3", (3, 3, True)),
        ("U1_MF 1", (1, 1, True)),
        ("U10_MF_2", (10, 2, True)),
        ("mf_u2", (2, 1, False)),
    ])
    def test_extrae_unidad_numero_y_enumeracion(
        self, carpeta: str, esperado: tuple[int, int, bool]
    ) -> None:
        assert InteractiveContentDetector._parsear_carpeta(carpeta) == esperado

    @pytest.mark.parametrize("carpeta", ["", "Unidad1", "U1_MF "])
    def test_rechaza_nombres_fuera_de_la_convencion(
        self, carpeta: str
    ) -> None:
        assert InteractiveContentDetector._parsear_carpeta(carpeta) is None


class TestDetectMaterialTrabajo:

    def test_retorna_lista_vacia_sin_archivos(
        self, detector: InteractiveContentDetector
    ) -> None:
        assert detector.detect_material_trabajo({}) == []

    def test_ignora_archivos_fuera_de_material_de_trabajo(
        self, detector: InteractiveContentDetector
    ) -> None:
        files_map = {f"{MF}/U1_lab/story.html": 1}

        assert detector.detect_material_trabajo(files_map) == []

    def test_ignora_archivos_que_no_son_punto_de_entrada(
        self, detector: InteractiveContentDetector
    ) -> None:
        files_map = {f"{MT}/U1_lab/guia.pdf": 1}

        assert detector.detect_material_trabajo(files_map) == []

    def test_ignora_story_html_sin_subcarpeta(
        self, detector: InteractiveContentDetector
    ) -> None:
        assert detector.detect_material_trabajo({f"{MT}/story.html": 1}) == []

    def test_acepta_cualquier_nombre_de_carpeta(
        self, detector: InteractiveContentDetector
    ) -> None:
        ruta = f"{MT}/Simulador/index.html"

        resultado = detector.detect_material_trabajo({ruta: 4})

        assert resultado == [{
            "numero": 1,
            "file_id": 4,
            "carpeta": "Simulador",
            "ruta_completa": ruta,
            "unidad": None,
        }]

    @pytest.mark.parametrize("files_map", [
        {f"{MT}/Sim/story.html": 1, f"{MT}/Sim/index.html": 2},
        {f"{MT}/Sim/index.html": 2, f"{MT}/Sim/story.html": 1},
    ], ids=["story_primero", "index_primero"])
    def test_story_html_tiene_prioridad_sobre_index_html(
        self,
        detector: InteractiveContentDetector,
        files_map: dict[str, int],
    ) -> None:
        resultado = detector.detect_material_trabajo(files_map)

        assert [item["file_id"] for item in resultado] == [1]

    def test_numera_desde_uno_en_orden_alfabetico_sin_distinguir_mayusculas(
        self, detector: InteractiveContentDetector
    ) -> None:
        resultado = detector.detect_material_trabajo({
            f"{MT}/Zeta/story.html": 1,
            f"{MT}/beta/story.html": 2,
            f"{MT}/Alpha/story.html": 3,
        })

        assert [(r["numero"], r["carpeta"]) for r in resultado] == [
            (1, "Alpha"),
            (2, "beta"),
            (3, "Zeta"),
        ]

    def test_ordena_numeros_de_carpeta_como_texto(
        self, detector: InteractiveContentDetector
    ) -> None:
        # Caracterización: documenta el comportamiento actual, no el deseado.
        resultado = detector.detect_material_trabajo({
            f"{MT}/Sim2/story.html": 1,
            f"{MT}/Sim10/story.html": 2,
        })

        assert [r["carpeta"] for r in resultado] == ["Sim10", "Sim2"]

    def test_detecta_unidad_desde_el_nombre_de_carpeta(
        self, detector: InteractiveContentDetector
    ) -> None:
        resultado = detector.detect_material_trabajo(
            {f"{MT}/U2_lab/story.html": 1}
        )

        assert resultado[0]["unidad"] == 2

    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason="Defecto: la regex de unidad acepta cualquier 'u' + un dígito",
    )
    @pytest.mark.parametrize("carpeta,unidad_esperada", [
        ("Menu3_recurso", None),
        ("U12_lab", 12),
    ])
    def test_interpreta_correctamente_la_unidad(
        self,
        detector: InteractiveContentDetector,
        carpeta: str,
        unidad_esperada: int | None,
    ) -> None:
        resultado = detector.detect_material_trabajo(
            {f"{MT}/{carpeta}/story.html": 1}
        )

        assert resultado[0]["unidad"] == unidad_esperada

    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason="Defecto: la ruta se parte sin normalizar el separador '\\'",
    )
    def test_acepta_rutas_con_separador_de_windows(
        self, detector: InteractiveContentDetector
    ) -> None:
        resultado = detector.detect_material_trabajo(
            {f"{MT}\\U1_lab\\story.html": 1}
        )

        assert len(resultado) == 1
