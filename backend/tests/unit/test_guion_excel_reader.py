"""
Pruebas unitarias para GuionExcelReader.

Estrategia: construir filas de Excel sintéticas que replican la
estructura real del Guion de módulo sin depender del archivo real.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.domain.services.guion_excel_reader import (
    GuionData,
    GuionExcelReader,
    UnidadGuion,
    _PREFIJOS_INSTRUCCION,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers — constructores de filas sintéticas
# ──────────────────────────────────────────────────────────────────────────────

def _fila(*celdas: str) -> list[str]:
    """Construye una fila con exactamente 4 columnas."""
    resultado = list(celdas)
    while len(resultado) < 4:
        resultado.append("")
    return resultado


def _filas_modulo_completo() -> list[list[str]]:
    """
    Replica la estructura real del Excel de Guion de módulo.
    Cubre todos los datos que el reader debe extraer.
    """
    return [
        _fila("Código del módulo",   "ESC535", "Nombre del módulo", "Fundamentos de Derecho"),
        _fila("URL video inicial",
              "No diligencie nada en este espacio\nEnlace de vimeo: https://player.vimeo.com/video/999",
              "", ""),
        _fila("Bloque de información de módulo", "Inicio",
              "Bienvenidos al módulo de Fundamentos de Derecho, donde exploraremos los pilares del sistema jurídico.",
              ""),
        _fila("", "Orientaciones",
              "Este módulo se desarrollará a partir del estudio de casos prácticos.", ""),
        _fila("Unidades", "", "", ""),

        # Unidad 1
        _fila("Título de la unidad 1", "", "El sistema procesal colombiano", ""),
        _fila("Unidad 1", "Video introducción a la unidad",
              "No diligencie nada en este espacio\nU1_video_introducción",
              "https://player.vimeo.com/video/1001"),
        _fila("", "Párrafo de introducción",
              "En esta unidad se estudiarán los fundamentos del proceso judicial colombiano y sus etapas.",
              ""),
        _fila("", "Material fundamental ",
              "No diligencie nada en este espacio\nU1_Lectura_Fundamental_1", "Título lectura 1"),
        _fila("", "",
              "No diligencie nada en este espacio\nU1_material_fundamental_1 (Video, pódcast, infografía)",
              "Título del video"),
        _fila("", "", "", "No diligencie nada en este espacio\nEnlace de vimeo: "),

        # Unidad 2
        _fila("Título de la unidad 2", "", "Procedimientos civiles", ""),
        _fila("Unidad 2", "Video introducción a la unidad",
              "No diligencie nada en este espacio\nU2_video_introducción",
              "https://player.vimeo.com/video/1002"),
        _fila("", "Párrafo de introducción",
              "Esta unidad profundiza en los procedimientos civiles y sus aplicaciones en el derecho colombiano.",
              ""),
        _fila("", "",
              "No diligencie nada en este espacio\nU2_material_fundamental_1 (Video, pódcast, infografía)",
              "Título"),
        _fila("", "", "",
              "https://player.vimeo.com/video/2002"),  # Vimeo en siguiente fila

        # Unidad 3
        _fila("Unidad 3", "Video introducción a la unidad",
              "No diligencie nada en este espacio\nU3_video_introducción",
              "https://player.vimeo.com/video/1003"),
        _fila("", "Párrafo de introducción",
              "La oralidad como esquema procesal y su aplicación práctica en los tribunales colombianos.",
              ""),
        _fila("", "",
              "No diligencie nada en este espacio\nU3_material_fundamental_1 (Video, pódcast, infografía)",
              "N/A"),
        _fila("", "", "", "No diligencie nada en este espacio\nEnlace de vimeo: "),

        # Unidad 4 — tiene SoundCloud
        _fila("Unidad 4", "Video introducción a la unidad",
              "No diligencie nada en este espacio\nU4_video_introducción",
              "https://player.vimeo.com/video/1004"),
        _fila("", "Párrafo de introducción",
              "Habilidades comunicativas para una intervención oral efectiva en el ámbito jurídico.",
              ""),
        _fila("", "",
              "No diligencie nada en este espacio\nU4_material_fundamental_1 (Video, pódcast, infografía)",
              "Título del podcast"),
        _fila("", "", "",
              "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/12345"),

        # Cierre
        _fila("Cierre", "", "", ""),
        _fila("", "Párrafo de cierre",
              "Solo diligencie el nombre del módulo\n¡Estamos llegando al final! En este módulo hemos explorado los fundamentos del sistema procesal.",
              ""),
    ]


def _reader_con_filas(filas: list[list[str]]) -> GuionData:
    """Crea un GuionExcelReader y lo ejecuta con filas sintéticas."""
    reader = GuionExcelReader.__new__(GuionExcelReader)
    return reader._parsear(filas)


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _extraer_url
# ──────────────────────────────────────────────────────────────────────────────

class TestExtraerUrl:

    def test_extrae_url_vimeo_con_prefijo(self) -> None:
        texto = "No diligencie nada en este espacio\nEnlace de vimeo: https://player.vimeo.com/video/123"
        url = GuionExcelReader._extraer_url(texto)
        assert url == "https://player.vimeo.com/video/123"

    def test_extrae_url_soundcloud(self) -> None:
        texto = "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/456"
        url = GuionExcelReader._extraer_url(texto)
        assert url is not None
        assert "soundcloud" in url

    def test_ignora_url_shutterstock(self) -> None:
        texto = "https://www.shutterstock.com/image/123"
        url = GuionExcelReader._extraer_url(texto)
        assert url is None

    def test_retorna_none_para_texto_sin_url(self) -> None:
        assert GuionExcelReader._extraer_url("Sin URL aquí") is None
        assert GuionExcelReader._extraer_url("") is None
        assert GuionExcelReader._extraer_url("N/A") is None

    def test_elimina_puntuacion_al_final(self) -> None:
        url = GuionExcelReader._extraer_url("Ver https://player.vimeo.com/video/789.")
        assert url == "https://player.vimeo.com/video/789"


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _limpiar_texto
# ──────────────────────────────────────────────────────────────────────────────

class TestLimpiarTexto:

    def test_elimina_prefijo_no_diligencie(self) -> None:
        texto = "No diligencie nada en este espacio\nContenido real del párrafo aquí."
        resultado = GuionExcelReader._limpiar_texto(texto)
        assert "No diligencie" not in resultado
        assert "Contenido real del párrafo aquí." in resultado

    def test_elimina_prefijo_solo_diligencie(self) -> None:
        texto = "Solo diligencie el nombre del módulo\n¡Estamos llegando al final de este recorrido académico!"
        resultado = GuionExcelReader._limpiar_texto(texto)
        assert "Solo diligencie" not in resultado
        assert "¡Estamos llegando" in resultado

    def test_retorna_vacio_si_texto_corto(self) -> None:
        resultado = GuionExcelReader._limpiar_texto("Corto", min_chars=30)
        assert resultado == ""

    def test_texto_sin_prefijo_retorna_intacto(self) -> None:
        texto = "En este módulo de derecho se estudiarán los procedimientos civiles y penales."
        resultado = GuionExcelReader._limpiar_texto(texto)
        assert resultado == texto

    def test_maneja_texto_con_multiples_lineas(self) -> None:
        texto = "No diligencie nada en este espacio\nLínea 1 del contenido real\nLínea 2 del contenido real"
        resultado = GuionExcelReader._limpiar_texto(texto)
        assert "No diligencie" not in resultado
        assert "Línea 1" in resultado
        assert "Línea 2" in resultado

    def test_retorna_vacio_para_texto_vacio(self) -> None:
        assert GuionExcelReader._limpiar_texto("") == ""


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _parsear — video inicial y textos globales
# ──────────────────────────────────────────────────────────────────────────────

class TestParsearDatosGlobales:

    def test_extrae_video_inicial_url(self) -> None:
        datos = _reader_con_filas(_filas_modulo_completo())
        assert datos.video_inicial_url == "https://player.vimeo.com/video/999"

    def test_extrae_texto_inicio(self) -> None:
        datos = _reader_con_filas(_filas_modulo_completo())
        assert "Bienvenidos al módulo" in datos.texto_inicio
        assert len(datos.texto_inicio) >= 30

    def test_extrae_texto_cierre_sin_prefijo(self) -> None:
        datos = _reader_con_filas(_filas_modulo_completo())
        assert datos.texto_cierre != ""
        assert "Solo diligencie" not in datos.texto_cierre
        assert "¡Estamos llegando al final!" in datos.texto_cierre

    def test_detecta_cuatro_unidades(self) -> None:
        datos = _reader_con_filas(_filas_modulo_completo())
        assert set(datos.unidades.keys()) == {1, 2, 3, 4}

    def test_unidad_inexistente_retorna_vacio(self) -> None:
        datos = _reader_con_filas(_filas_modulo_completo())
        u5 = datos.unidad(5)
        assert u5.video_intro_url is None
        assert u5.parrafo_intro == ""


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _parsear — datos por unidad
# ──────────────────────────────────────────────────────────────────────────────

class TestParsearDatosPorUnidad:

    def test_video_intro_url_todas_las_unidades(self) -> None:
        datos = _reader_con_filas(_filas_modulo_completo())
        assert datos.unidad(1).video_intro_url == "https://player.vimeo.com/video/1001"
        assert datos.unidad(2).video_intro_url == "https://player.vimeo.com/video/1002"
        assert datos.unidad(3).video_intro_url == "https://player.vimeo.com/video/1003"
        assert datos.unidad(4).video_intro_url == "https://player.vimeo.com/video/1004"

    def test_parrafo_intro_todas_las_unidades(self) -> None:
        datos = _reader_con_filas(_filas_modulo_completo())
        assert "fundamentos del proceso judicial" in datos.unidad(1).parrafo_intro
        assert "procedimientos civiles" in datos.unidad(2).parrafo_intro
        assert "oralidad" in datos.unidad(3).parrafo_intro
        assert "intervención oral" in datos.unidad(4).parrafo_intro

    def test_sin_multimedia_cuando_no_hay_url(self) -> None:
        datos = _reader_con_filas(_filas_modulo_completo())
        # U1 no tiene URL en material_fundamental (texto "Enlace de vimeo: " vacío)
        assert datos.unidad(1).podcast_url is None
        assert datos.unidad(1).vimeo_mat_fund_url is None

    def test_vimeo_en_siguiente_fila(self) -> None:
        """U2 tiene Vimeo en la fila siguiente al material_fundamental_1."""
        datos = _reader_con_filas(_filas_modulo_completo())
        assert datos.unidad(2).vimeo_mat_fund_url == "https://player.vimeo.com/video/2002"
        assert datos.unidad(2).podcast_url is None

    def test_sin_multimedia_con_valor_na(self) -> None:
        """U3 tiene 'N/A' en material_fundamental_1 → no debe asignar multimedia."""
        datos = _reader_con_filas(_filas_modulo_completo())
        assert datos.unidad(3).podcast_url is None
        assert datos.unidad(3).vimeo_mat_fund_url is None

    def test_soundcloud_en_siguiente_fila(self) -> None:
        """U4 tiene SoundCloud en la fila siguiente al material_fundamental_1."""
        datos = _reader_con_filas(_filas_modulo_completo())
        u4 = datos.unidad(4)
        assert u4.podcast_url is not None
        assert "soundcloud" in u4.podcast_url
        assert u4.vimeo_mat_fund_url is None


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _asignar_multimedia
# ──────────────────────────────────────────────────────────────────────────────

class TestAsignarMultimedia:

    def test_asigna_soundcloud_a_podcast_url(self) -> None:
        unidad = UnidadGuion(numero=1)
        GuionExcelReader._asignar_multimedia(
            "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/123",
            unidad,
        )
        assert unidad.podcast_url is not None
        assert unidad.vimeo_mat_fund_url is None

    def test_asigna_vimeo_a_vimeo_mat_fund_url(self) -> None:
        unidad = UnidadGuion(numero=1)
        GuionExcelReader._asignar_multimedia(
            "https://player.vimeo.com/video/456",
            unidad,
        )
        assert unidad.vimeo_mat_fund_url is not None
        assert unidad.podcast_url is None

    def test_ignora_url_na(self) -> None:
        unidad = UnidadGuion(numero=1)
        GuionExcelReader._asignar_multimedia("N/A", unidad)
        assert unidad.podcast_url is None
        assert unidad.vimeo_mat_fund_url is None

    def test_ignora_url_vacia(self) -> None:
        unidad = UnidadGuion(numero=1)
        GuionExcelReader._asignar_multimedia("", unidad)
        assert unidad.podcast_url is None


# ──────────────────────────────────────────────────────────────────────────────
# Tests: read() — integración con archivo real
# ──────────────────────────────────────────────────────────────────────────────

class TestReadConArchivoReal:
    """
    Pruebas de integración con el archivo Excel real.
    Se omiten si el archivo no está disponible en el entorno de CI.
    """

    EXCEL_PATH = Path("tests/fixtures/Guion_de_modulo.xlsx")

    @pytest.mark.skipif(
        not Path("tests/fixtures/Guion_de_modulo.xlsx").exists(),
        reason="Archivo real no disponible en entorno de pruebas",
    )
    def test_lee_video_inicial_del_excel_real(self) -> None:
        datos = GuionExcelReader(self.EXCEL_PATH).read()
        assert datos.video_inicial_url is not None
        assert "vimeo" in datos.video_inicial_url.lower()

    @pytest.mark.skipif(
        not Path("tests/fixtures/Guion_de_modulo.xlsx").exists(),
        reason="Archivo real no disponible en entorno de pruebas",
    )
    def test_detecta_cuatro_unidades_del_excel_real(self) -> None:
        datos = GuionExcelReader(self.EXCEL_PATH).read()
        assert len(datos.unidades) == 4

    @pytest.mark.skipif(
        not Path("tests/fixtures/Guion_de_modulo.xlsx").exists(),
        reason="Archivo real no disponible en entorno de pruebas",
    )
    def test_cierre_sin_prefijo_en_excel_real(self) -> None:
        datos = GuionExcelReader(self.EXCEL_PATH).read()
        if datos.texto_cierre:
            assert "Solo diligencie" not in datos.texto_cierre
            assert "No diligencie" not in datos.texto_cierre
    
    def test_detecta_unidades_con_formato_titulo(self) -> None:
        """Replica el formato ESC339 donde col[0] es 'Título de la unidad N'."""
        filas = [
            _fila("Título de la unidad 1", "", "Aspectos fundamentales", ""),
            _fila("", "Párrafo de introducción",
                "En esta unidad se estudiarán los fundamentos del proceso judicial colombiano.",
                ""),
            _fila("Título de la unidad 2", "", "Procedimientos civiles", ""),
            _fila("", "Párrafo de introducción",
                "Esta unidad profundiza en los procedimientos civiles y sus aplicaciones.",
                ""),
        ]
        datos = _reader_con_filas(filas)
        assert 1 in datos.unidades
        assert 2 in datos.unidades
        assert "fundamentos" in datos.unidad(1).parrafo_intro
        assert "procedimientos civiles" in datos.unidad(2).parrafo_intro