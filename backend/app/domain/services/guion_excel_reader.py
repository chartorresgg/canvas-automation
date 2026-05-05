"""
Lector del archivo Excel de Guion de módulo.

Extrae las URLs de recursos multimedia y los párrafos de texto
que se inyectan en las páginas del aula virtual Canvas.

Capa: Dominio — services
Colaboradores: FrontPageComposer, MaterialFundamentalComposer
               (a través del orquestador)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook

logger = logging.getLogger(__name__)

# Nombre esperado de la hoja principal del Excel
_NOMBRE_HOJA = "Guion de módulo"


# ──────────────────────────────────────────────────────────────────────────────
# Value Objects de resultado
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class UnidadGuion:
    """Datos extraídos del Guion Excel para una unidad del módulo."""
    numero:             int
    video_intro_url:    str | None = None
    parrafo_intro:      str        = ""
    podcast_url:        str | None = None
    vimeo_mat_fund_url: str | None = None


@dataclass
class GuionData:
    """
    Datos completos extraídos del Guion Excel de un módulo.

    Agrupa todos los recursos multimedia y textos que deben
    inyectarse en el front del curso y las páginas de Material
    Fundamental.
    """
    video_inicial_url: str | None              = None
    texto_inicio:      str                     = ""
    texto_cierre:      str                     = ""
    unidades:          dict[int, UnidadGuion]  = field(default_factory=dict)

    def unidad(self, numero: int) -> UnidadGuion:
        """Retorna los datos de una unidad o un objeto vacío si no existe."""
        return self.unidades.get(numero, UnidadGuion(numero=numero))


# ──────────────────────────────────────────────────────────────────────────────
# Lector principal
# ──────────────────────────────────────────────────────────────────────────────

class GuionExcelReader:
    """
    Lee y parsea el archivo Excel 'Guion de módulo'.

    Responsabilidad única (SRP): extraer datos del Excel de contenidos
    y exponerlos como GuionData para que los Composers los usen.

    La estructura del Excel tiene labels en columnas A/B y valores
    en columnas C/D. El lector busca palabras clave en cualquier celda
    y extrae URLs y textos de las celdas adyacentes.

    Colaboradores: ninguno (servicio de dominio puro).
    """

    def __init__(self, excel_path: Path) -> None:
        self._path = excel_path

    def read(self) -> GuionData:
        """
        Lee el Excel y retorna el GuionData completo.

        Returns:
            GuionData con todos los recursos multimedia y textos.

        Raises:
            FileNotFoundError: Si el archivo Excel no existe.
            ValueError:        Si la hoja esperada no se encuentra.
        """
        if not self._path.exists():
            raise FileNotFoundError(
                f"Guion Excel no encontrado: '{self._path}'"
            )

        wb = load_workbook(str(self._path), read_only=True, data_only=True)

        # Buscar la hoja por nombre exacto o usar la primera
        ws = None
        for nombre in wb.sheetnames:
            if _NOMBRE_HOJA.lower() in nombre.lower():
                ws = wb[nombre]
                break
        if ws is None:
            ws = wb.active
            logger.warning(
                "No se encontró hoja '%s'. Usando hoja activa: '%s'",
                _NOMBRE_HOJA, ws.title,
            )

        filas = self._leer_filas(ws)
        wb.close()

        return self._parsear(filas)

    # ──────────────────────────────────────────────────────────────
    # Privados — lectura y parsing
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _leer_filas(ws) -> list[list[str]]:
        """
        Convierte el worksheet a una lista de filas con strings limpios.
        Ignora filas completamente vacías.
        """
        filas: list[list[str]] = []
        for fila in ws.iter_rows(values_only=True):
            celdas = [str(c).strip() if c is not None else "" for c in fila]
            # Solo incluir filas que tienen al menos una celda no vacía
            if any(c for c in celdas):
                filas.append(celdas)
        return filas

    def _parsear(self, filas: list[list[str]]) -> GuionData:
        """
        Parsea todas las filas y construye el GuionData.

        Estrategia: iterar las filas una vez buscando palabras clave
        en cualquier celda para extraer los datos correspondientes.
        """
        datos = GuionData()
        unidad_actual: int | None = None

        for idx, fila in enumerate(filas):
            fila_texto = " ".join(fila).lower()

            # ── URL del video inicial ─────────────────────────────
            if "url video inicial" in fila_texto:
                url = self._extraer_url_de_fila(fila)
                if url:
                    datos.video_inicial_url = url
                    logger.info("Video inicial: %s", url)

            # ── Texto de inicio / bienvenida ──────────────────────
            if self._celda_exacta("inicio", fila) and not datos.texto_inicio:
                texto = self._extraer_texto_largo(fila, excluir_url=True)
                if texto:
                    datos.texto_inicio = texto

            # ── Número de unidad activo ───────────────────────────
            for u in range(1, 5):
                col_a = fila[0].lower() if fila else ""
                if (f"unidad {u}" in col_a or
                        f"título de la unidad {u}" in col_a):
                    unidad_actual = u
                    if u not in datos.unidades:
                        datos.unidades[u] = UnidadGuion(numero=u)

            # ── Datos por unidad ──────────────────────────────────
            if unidad_actual is not None:
                unidad = datos.unidades[unidad_actual]

                # Video de introducción de la unidad
                if ("video introducción" in fila_texto or
                        "video introduccion" in fila_texto):
                    url = self._extraer_url_de_fila(fila)
                    if url and unidad.video_intro_url is None:
                        unidad.video_intro_url = url
                        logger.info(
                            "Video intro U%d: %s", unidad_actual, url
                        )

                # Párrafo de introducción de la unidad
                if ("párrafo de introducción" in fila_texto or
                        "parrafo de introduccion" in fila_texto):
                    texto = self._extraer_texto_largo(fila, excluir_url=True)
                    if texto and not unidad.parrafo_intro:
                        unidad.parrafo_intro = texto

                # Material fundamental multimedia (video/podcast)
                if "material_fundamental_1" in fila_texto.replace(" ", "_"):
                    # Buscar URL en la misma fila
                    url = self._extraer_url_de_fila(fila)
                    if url:
                        self._clasificar_url_multimedia(url, unidad)
                    else:
                        # Buscar en la siguiente fila (SoundCloud suele ir separado)
                        if idx + 1 < len(filas):
                            url_siguiente = self._extraer_url_de_fila(filas[idx + 1])
                            if url_siguiente:
                                self._clasificar_url_multimedia(url_siguiente, unidad)

            # ── Párrafo de cierre ─────────────────────────────────
            if "párrafo de cierre" in fila_texto or "parrafo de cierre" in fila_texto:
                texto = self._extraer_texto_largo(fila, excluir_url=True)
                if texto and not datos.texto_cierre:
                    datos.texto_cierre = texto

        logger.info(
            "Guion leído: video_inicial=%s, unidades=%s",
            bool(datos.video_inicial_url),
            list(datos.unidades.keys()),
        )
        return datos

    # ──────────────────────────────────────────────────────────────
    # Privados — utilidades de extracción
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _extraer_url(texto: str) -> str | None:
        """
        Extrae la primera URL HTTP/HTTPS de un texto.
        Limpia prefijos como 'Enlace de vimeo:' o 'No diligencie...'.

        Returns:
            URL limpia o None si no se encuentra.
        """
        if not texto:
            return None
        match = re.search(r"https?://\S+", texto)
        if match:
            url = match.group(0).rstrip(".,;)")
            # Ignorar URLs de Shutterstock (son imágenes de referencia)
            if "shutterstock" in url.lower():
                return None
            return url
        return None

    def _extraer_url_de_fila(self, fila: list[str]) -> str | None:
        """Busca la primera URL válida en cualquier celda de la fila."""
        for celda in fila:
            url = self._extraer_url(celda)
            if url:
                return url
        return None

    @staticmethod
    def _extraer_texto_largo(
        fila: list[str],
        excluir_url: bool = True,
        min_chars: int = 40,
    ) -> str:
        """
        Extrae el primer texto largo de la fila que no sea una instrucción.

        Descarta:
            - Celdas de menos de min_chars caracteres
            - Celdas que contienen 'No diligencie'
            - URLs (si excluir_url=True)
            - Celdas que son solo nombres de archivo (U1_Lectura...)

        Returns:
            Texto limpio o cadena vacía si no se encuentra.
        """
        for celda in fila:
            if len(celda) < min_chars:
                continue
            if "no diligencie" in celda.lower():
                continue
            if excluir_url and re.search(r"https?://", celda):
                continue
            if re.match(r"^U\d+_", celda):
                continue
            return celda
        return ""

    @staticmethod
    def _celda_exacta(valor: str, fila: list[str]) -> bool:
        """
        Verifica si alguna celda de la fila contiene exactamente el valor
        (ignorando mayúsculas y espacios extra).
        """
        return any(c.strip().lower() == valor.lower() for c in fila if c)

    @staticmethod
    def _clasificar_url_multimedia(url: str, unidad: UnidadGuion) -> None:
        """
        Clasifica una URL como podcast (SoundCloud) o video (Vimeo)
        y la asigna al campo correspondiente de la unidad.
        """
        url_lower = url.lower()
        if "soundcloud" in url_lower:
            unidad.podcast_url = url
            logger.info("Podcast U%d: %s", unidad.numero, url[:60])
        elif "vimeo" in url_lower or "player" in url_lower:
            unidad.vimeo_mat_fund_url = url
            logger.info("Vimeo mat.fund U%d: %s", unidad.numero, url[:60])