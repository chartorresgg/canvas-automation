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
    re.compile(r"U(\d+)_MF_(\d+)$",                            re.IGNORECASE),  # ← U3_MF_3
    re.compile(r"U(\d+)_MF(\d+)$",                             re.IGNORECASE),  # U3_MF3
    re.compile(r"U(\d+)_MF$",                                  re.IGNORECASE),  # U3_MF
    re.compile(r"U(\d+)_MF(?:_(\d+))?$",                         re.IGNORECASE),
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

        Busca story.html (o index.html como fallback) dentro de subcarpetas
        de "2. Material fundamental/" que sigan las convenciones de nombre.
        Comparaciones siempre en minúsculas para ser resiliente a diferencias
        de casing en Windows (filesystems case-insensitive).

        Args:
            files_map: Mapa {ruta_relativa: file_id} de FileRepository.

        Returns:
            Mapa {unidad: [{"numero", "file_id", "carpeta", "es_enumerado"}]}
            ordenado por número de contenido dentro de cada unidad.
        """
        contenido: dict[int, list[dict]] = {}

        # Primera pasada: buscar story.html (principal) e index.html (fallback)
        # Guardamos el mejor candidato por carpeta: story.html > index.html
        mejores: dict[str, dict] = {}  # clave=carpeta_normalizada → info

        for ruta, file_id in files_map.items():
            ruta_lower = ruta.lower().replace("\\", "/")

            # Solo archivos HTML dentro de "2. Material fundamental/"
            if not ruta_lower.startswith("2. material fundamental/"):
                continue

            nombre_archivo = ruta_lower.split("/")[-1]
            if nombre_archivo not in ("story.html", "index.html"):
                continue

            partes = ruta.split("/")
            # Necesitamos al menos: carpeta_raiz / carpeta_scorm / archivo
            if len(partes) < 3:
                continue

            carpeta_contenido = partes[1]  # Ej: "U3_MF_3"
            clave = carpeta_contenido.lower()

            # story.html tiene prioridad sobre index.html
            es_story = nombre_archivo == "story.html"
            if clave in mejores and mejores[clave]["es_story"] and not es_story:
                continue  # ya tenemos story.html, ignorar index.html

            mejores[clave] = {
                "carpeta":   carpeta_contenido,
                "file_id":   file_id,
                "es_story":  es_story,
                "ruta":      ruta,
            }

        # Segunda pasada: parsear cada carpeta y construir el mapa por unidad
        for clave, info in mejores.items():
            carpeta_contenido = info["carpeta"]
            file_id           = info["file_id"]

            parsed = self._parsear_carpeta(carpeta_contenido)
            if not parsed:
                logger.warning(
                    "Carpeta SCORM no reconocida: '%s' — omitiendo",
                    carpeta_contenido,
                )
                continue

            unidad, numero, es_enumerado = parsed

            contenido.setdefault(unidad, []).append({
                "numero":        numero,
                "file_id":       file_id,
                "carpeta":       carpeta_contenido,
                "ruta_completa": info["ruta"],
                "es_enumerado":  es_enumerado,
            })

            logger.info(
                "SCORM detectado: Unidad %d — Contenido %d (carpeta='%s', file_id=%d)",
                unidad, numero, carpeta_contenido, file_id,
            )

        # Ordenar por número de contenido dentro de cada unidad
        for unidad in contenido:
            contenido[unidad].sort(key=lambda x: x["numero"])

        total = sum(len(v) for v in contenido.values())
        logger.info("Total contenidos interactivos detectados: %d", total)

        return contenido

    @staticmethod
    def _parsear_carpeta(carpeta: str) -> tuple[int, int, bool] | None:
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
                # Acceso seguro: no todos los patrones tienen grupo 2
                try:
                    numero_raw = m.group(2)
                except IndexError:
                    numero_raw = None
                if numero_raw is not None:
                    return (unidad, int(numero_raw), True)
                return (unidad, 1, False)
        return None