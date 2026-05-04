"""
Servicio de detección de contenido interactivo SCORM en el FileMap.

Identifica paquetes Articulate Storyline dentro de la estructura
de Material Fundamental buscando archivos story.html con rutas
que sigan las convenciones institucionales del Politécnico.

Capa: Dominio — services
Colaboradores: ninguno (servicio de dominio puro)
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Patrones de carpeta soportados (en orden de precedencia)
_PATRONES_CARPETA = [
    re.compile(r"MF_U(\d+)(?:_(\d+))?$",                      re.IGNORECASE),
    re.compile(r"U(\d+)_Material[_\s]*fundamental(?:_(\d+))?$", re.IGNORECASE),
    re.compile(r"U(\d+)_MF(\d+)$",                              re.IGNORECASE),
]


class InteractiveContentDetector:
    """
    Detecta paquetes de contenido interactivo SCORM en el FileMap.

    Responsabilidad única (SRP): escanear el mapa de archivos subidos
    a Canvas buscando archivos story.html dentro de carpetas de Material
    Fundamental y construir el mapa de contenido interactivo por unidad.

    El resultado se pasa al MaterialFundamentalComposer para generar
    los botones de contenido interactivo en cada página de unidad.

    Colaboradores:
        PageRepository — crea las páginas para cada contenido detectado.
    """

    def detect(self, files_map: dict[str, int]) -> dict[int, list[dict]]:
        """
        Detecta contenido interactivo SCORM en el FileMap.

        Busca archivos story.html dentro de subcarpetas de
        "2. Material fundamental/" que sigan las convenciones de nombre.

        Args:
            files_map: Mapa {ruta_relativa: file_id} de FileRepository.

        Returns:
            Mapa {unidad: [{"numero", "file_id", "carpeta", "es_enumerado"}]}
            ordenado por número de contenido dentro de cada unidad.
            Retorna dict vacío si no hay contenido interactivo.
        """
        contenido: dict[int, list[dict]] = {}

        for ruta, file_id in files_map.items():
            if not ruta.endswith("/story.html"):
                continue

            partes = ruta.split("/")
            # Estructura esperada: "2. Material fundamental/U1_MF1/story.html"
            if len(partes) < 3:
                continue
            if partes[0] != "2. Material fundamental":
                continue

            carpeta_contenido = partes[1]
            info = self._parsear_carpeta(carpeta_contenido)
            if not info:
                logger.warning(
                    "Carpeta SCORM no reconocida: '%s' — omitiendo",
                    carpeta_contenido,
                )
                continue

            unidad, numero, es_enumerado = info

            contenido.setdefault(unidad, []).append({
                "numero":       numero,
                "file_id":      file_id,
                "carpeta":      carpeta_contenido,
                "ruta_completa": ruta,
                "es_enumerado": es_enumerado,
            })

            logger.info(
                "SCORM detectado: Unidad %d — Contenido %d (file_id=%d)",
                unidad, numero, file_id,
            )

        # Ordenar por número de contenido dentro de cada unidad
        for unidad in contenido:
            contenido[unidad].sort(key=lambda x: x["numero"])

        total = sum(len(v) for v in contenido.values())
        logger.info("Total contenidos interactivos detectados: %d", total)

        return contenido

    @staticmethod
    def _parsear_carpeta(
        carpeta: str,
    ) -> tuple[int, int, bool] | None:
        """
        Parsea el nombre de una carpeta SCORM y extrae unidad y número.

        Formatos soportados:
            MF_U1           → (1, 1, False)
            MF_U1_2         → (1, 2, True)
            U1_MF2          → (1, 2, True)
            U1_Material_fundamental      → (1, 1, False)
            U1_Material_fundamental_2   → (1, 2, True)

        Args:
            carpeta: Nombre de la subcarpeta dentro de Material fundamental.

        Returns:
            Tupla (unidad, numero_contenido, es_enumerado) o None si no
            coincide con ningún patrón conocido.
        """
        for patron in _PATRONES_CARPETA:
            m = patron.match(carpeta)
            if m:
                unidad = int(m.group(1))
                numero_raw = m.group(2)
                if numero_raw is not None:
                    return (unidad, int(numero_raw), True)
                return (unidad, 1, False)
        return None