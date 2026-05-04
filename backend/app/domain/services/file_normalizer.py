"""
Servicio de normalización de estructura de archivos para aulas Canvas LMS.
Aplica las convenciones institucionales del Politécnico Grancolombiano.

Capa: Dominio
Patrón: ninguno (servicio de dominio puro)
Dependencias externas: ninguna
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Value Object de resultado — queda en este módulo porque es exclusivo de
# FileNormalizer. Si en el futuro otros servicios lo usan, se mueve a
# domain/value_objects/
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class NormalizationResult:
    """
    Encapsula el resultado de una operación de normalización.

    Permite al orquestador y a los tests inspeccionar qué cambios se hicieron
    sin depender de efectos secundarios ni logs.
    """
    folders_renamed: list[str] = field(default_factory=list)
    files_renamed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Retorna True si no hubo errores durante la normalización."""
        return len(self.errors) == 0

    @property
    def total_changes(self) -> int:
        """Número total de carpetas y archivos renombrados."""
        return len(self.folders_renamed) + len(self.files_renamed)


# ──────────────────────────────────────────────────────────────────────────────
# Servicio principal
# ──────────────────────────────────────────────────────────────────────────────

class FileNormalizer:
    """
    Aplica las reglas de normalización de nombres de carpetas y archivos PDF
    según la convención institucional del Politécnico Grancolombiano.

    Responsabilidad única (SRP): transformar nombres de carpetas y archivos
    al formato canónico esperado por el sistema Canvas LMS.

    Convenciones aplicadas:
      - Carpeta raíz del ZIP: debe llamarse exactamente "1. Archivos"
      - Subcarpetas canónicas:
            "1. Presentación"
            "2. Material fundamental"
            "3. Material de trabajo"
            "4. Complementos"
            "5. Cierre"
      - PDFs en Material fundamental: U{n}_{tipo}.pdf
      - PDFs en Complementos:        U{n}_Complemento.pdf

    Colaboradores: ZipProcessor (único consumidor de esta clase)
    """

    # Mapa de palabras clave (texto limpio) → nombre canónico de subcarpeta.
    # El orden importa: las claves más específicas deben ir primero para evitar
    # falsos positivos en la búsqueda por subcadena.
    _SUBFOLDER_KEYWORD_MAP: ClassVar[dict[str, str]] = {
        # Presentación
        "presentacion":          "1. Presentación",
        # Material fundamental — variantes más específicas primero
        "materialfundamental":   "2. Material fundamental",
        "matfund":               "2. Material fundamental",
        # Material de trabajo — variantes más específicas primero
        "materialdetrabajo":     "3. Material de trabajo",
        "materialtrabajo":       "3. Material de trabajo",
        "materialdtrabajo":      "3. Material de trabajo",
        # Complementos
        "materialcomplementario":"4. Complementos",
        "complementario":        "4. Complementos",
        "complementarios":       "4. Complementos",
        "complemento":           "4. Complementos",
        "complementos":          "4. Complementos",
        # Cierre
        "cierre":                "5. Cierre",
    }

    # Mapa de tipo de PDF (texto limpio) → tipo canónico.
    # El orden define la precedencia: "materialfundamental" antes que "material".
    _PDF_TYPE_PRECEDENCE: ClassVar[list[tuple[str, str]]] = [
    ("materialfundamental",  "Material_Fundamental"),
    ("matfund",              "Material_Fundamental"),
    ("mf",                   "Material_Fundamental"),   # ← línea nueva
    ("lecturafundamental",   "Lectura_Fundamental"),
    ("actividadformativa",   "Actividad_Formativa"),
    ("actividadsumativa",    "Actividad_Sumativa"),
    ("lectura",              "Lectura_Fundamental"),
    ("formativa",            "Actividad_Formativa"),
    ("sumativa",             "Actividad_Sumativa"),
    ("actividad",            "Actividad"),
    ]

    # ──────────────────────────────────────────────────────────────
    # API pública
    # ──────────────────────────────────────────────────────────────

    def normalize_folders(self, base: Path) -> NormalizationResult:
        """
        Normaliza los nombres de carpetas en la ruta base del ZIP extraído.

        Pasos:
            1. Renombra la carpeta raíz (variantes de "1. Archivos").
            2. Renombra las subcarpetas a sus nombres canónicos.

        Args:
            base: Ruta al directorio raíz del ZIP extraído.

        Returns:
            NormalizationResult con el detalle de cambios realizados.

        Raises:
            FileNotFoundError: Si no se encuentra la carpeta raíz de archivos.
        """
        result = NormalizationResult()

        ruta_archivos = self._normalizar_carpeta_raiz(base, result)
        self._normalizar_subcarpetas(ruta_archivos, result)

        return result

    def normalize_pdfs(self, ruta_archivos: Path) -> NormalizationResult:
        """
        Normaliza los nombres de archivos PDF dentro de las carpetas de contenido.

        Aplica la convención U{n}_{tipo}.pdf en:
            - "2. Material fundamental"
            - "4. Complementos"

        Args:
            ruta_archivos: Ruta a la carpeta "1. Archivos" ya normalizada.

        Returns:
            NormalizationResult con el detalle de cambios realizados.
        """
        result = NormalizationResult()

        ruta_mat_fund = ruta_archivos / "2. Material fundamental"
        if ruta_mat_fund.is_dir():
            self._normalizar_pdfs_material_fundamental(ruta_mat_fund, result)
        else:
            result.warnings.append(
                "No se encontró '2. Material fundamental'. "
                "Se omite normalización de PDFs de material fundamental."
            )

        ruta_complementos = ruta_archivos / "4. Complementos"
        if ruta_complementos.is_dir():
            self._normalizar_pdfs_complementos(ruta_complementos, result)
        else:
            result.warnings.append(
                "No se encontró '4. Complementos'. "
                "Se omite normalización de PDFs de complementos."
            )

        return result

    # ──────────────────────────────────────────────────────────────
    # Privados — normalización de carpetas
    # ──────────────────────────────────────────────────────────────

    def _normalizar_carpeta_raiz(
        self, base: Path, result: NormalizationResult
    ) -> Path:
        """
        Localiza y renombra la carpeta raíz del contenido del ZIP.

        Busca cualquier carpeta cuyo nombre empiece por "1" y contenga la
        palabra "archivo" (en texto limpio). Si ya se llama "1. Archivos",
        no hace nada.

        Returns:
            Path a la carpeta "1. Archivos" (ya normalizada).

        Raises:
            FileNotFoundError: Si no existe ninguna carpeta candidata.
        """
        destino = base / "1. Archivos"

        if destino.is_dir():
            logger.info("Carpeta '1. Archivos' ya tiene el nombre correcto.")
            return destino

        candidatas = [
            entry for entry in base.iterdir()
            if entry.is_dir()
            and entry.name.startswith("1")
            and "archivo" in self._clean_text(entry.name)
        ]

        if not candidatas:
            disponibles = [e.name for e in base.iterdir() if e.is_dir()]
            raise FileNotFoundError(
                f"No se encontró carpeta tipo '1. Archivos' en: {base}. "
                f"Carpetas disponibles: {disponibles}"
            )

        original = candidatas[0]
        original.rename(destino)

        msg = f"'{original.name}' → '1. Archivos'"
        result.folders_renamed.append(msg)
        logger.info("Carpeta raíz renombrada: %s", msg)

        return destino

    def _normalizar_subcarpetas(
        self, ruta_archivos: Path, result: NormalizationResult
    ) -> None:
        """
        Itera las subcarpetas de "1. Archivos" y las renombra al nombre canónico.

        Usa list() sobre iterdir() para evitar problemas con renombrar durante
        la iteración.
        """
        for subcarpeta in list(ruta_archivos.iterdir()):
            if not subcarpeta.is_dir():
                continue

            nombre_limpio = self._clean_text(subcarpeta.name)
            nombre_canonico = self._resolver_nombre_canonico_subcarpeta(nombre_limpio)

            if nombre_canonico is None:
                msg = f"Subcarpeta no reconocida, se deja intacta: '{subcarpeta.name}'"
                result.warnings.append(msg)
                logger.warning(msg)
                continue

            destino = ruta_archivos / nombre_canonico

            if subcarpeta.resolve() == destino.resolve():
                logger.info("Subcarpeta ya correcta: '%s'", nombre_canonico)
                continue

            if destino.exists():
                msg = (
                    f"No se renombró '{subcarpeta.name}' → '{nombre_canonico}': "
                    f"el destino ya existe."
                )
                result.warnings.append(msg)
                logger.warning(msg)
                continue

            subcarpeta.rename(destino)
            msg = f"'{subcarpeta.name}' → '{nombre_canonico}'"
            result.folders_renamed.append(msg)
            logger.info("Subcarpeta renombrada: %s", msg)

    def _resolver_nombre_canonico_subcarpeta(self, nombre_limpio: str) -> str | None:
        """
        Resuelve el nombre canónico de una subcarpeta buscando keywords
        por subcadena dentro del texto limpio.

        Args:
            nombre_limpio: Nombre procesado con _clean_text().

        Returns:
            Nombre canónico o None si no se reconoce.
        """
        for keyword, canonico in self._SUBFOLDER_KEYWORD_MAP.items():
            if keyword in nombre_limpio:
                return canonico
        return None

    # ──────────────────────────────────────────────────────────────
    # Privados — normalización de PDFs
    # ──────────────────────────────────────────────────────────────

    def _normalizar_pdfs_material_fundamental(
        self, ruta: Path, result: NormalizationResult
    ) -> None:
        """
        Normaliza PDFs en "2. Material fundamental".

        Patrón de salida:
            - Un solo archivo:       U{n}_{tipo}.pdf
            - Múltiples del mismo tipo: U{n}_{tipo}_{seq}.pdf
        """
        pdfs = [f for f in ruta.iterdir() if f.suffix.lower() == ".pdf"]
        grupos: dict[str, list[dict]] = {}

        for pdf in pdfs:
            unidad = self._detect_unit(pdf.stem)
            if unidad is None:
                result.warnings.append(
                    f"Sin número de unidad en: '{pdf.name}'. Se omite."
                )
                continue

            tipo = self._detect_pdf_type(pdf.stem)
            if tipo is None:
                result.warnings.append(
                    f"Sin tipo reconocido en: '{pdf.name}'. Se omite."
                )
                continue

            clave = f"U{unidad}_{tipo}"
            grupos.setdefault(clave, []).append({
                "path": pdf,
                "seq": self._detect_sequence_number(pdf.stem),
            })

        for clave, archivos in grupos.items():
            archivos.sort(key=lambda x: x["seq"] or 0)

            for idx, info in enumerate(archivos):
                pdf: Path = info["path"]
                seq: int | None = info["seq"]
                multiples = len(archivos) > 1

                if multiples:
                    numero = seq if seq is not None else idx + 1
                    nuevo_nombre = f"{clave}_{numero}.pdf"
                else:
                    nuevo_nombre = f"{clave}.pdf"

                self._renombrar_pdf(pdf, ruta / nuevo_nombre, result)

    def _normalizar_pdfs_complementos(
        self, ruta: Path, result: NormalizationResult
    ) -> None:
        """
        Normaliza PDFs en "4. Complementos".

        Patrón de salida:
            - Un solo archivo por unidad: U{n}_Complemento.pdf
            - Múltiples por unidad:       U{n}_Complemento_{seq}.pdf
        """
        pdfs = [f for f in ruta.iterdir() if f.suffix.lower() == ".pdf"]
        grupos: dict[str, list[dict]] = {}

        for pdf in pdfs:
            unidad = self._detect_unit(pdf.stem)
            if unidad is None:
                result.warnings.append(
                    f"Sin número de unidad en complemento: '{pdf.name}'. Se omite."
                )
                continue

            clave = f"U{unidad}_Complemento"
            grupos.setdefault(clave, []).append({
                "path": pdf,
                "seq": self._detect_sequence_number(pdf.stem),
            })

        for clave, archivos in grupos.items():
            archivos.sort(key=lambda x: x["seq"] or 0)

            for idx, info in enumerate(archivos):
                pdf: Path = info["path"]
                seq: int | None = info["seq"]
                multiples = len(archivos) > 1

                if multiples:
                    numero = seq if seq is not None else idx + 1
                    nuevo_nombre = f"{clave}_{numero}.pdf"
                else:
                    nuevo_nombre = f"{clave}.pdf"

                self._renombrar_pdf(pdf, ruta / nuevo_nombre, result)

    def _renombrar_pdf(
        self, origen: Path, destino: Path, result: NormalizationResult
    ) -> None:
        """
        Renombra un archivo PDF registrando el cambio en el resultado.
        Método auxiliar para evitar duplicación entre los dos normalizadores de PDF.
        """
        if origen.resolve() == destino.resolve():
            logger.info("PDF ya correcto: '%s'", origen.name)
            return

        if destino.exists():
            result.warnings.append(
                f"No se renombró '{origen.name}' → '{destino.name}': destino existe."
            )
            return

        origen.rename(destino)
        msg = f"'{origen.name}' → '{destino.name}'"
        result.files_renamed.append(msg)
        logger.info("PDF renombrado: %s", msg)

    # ──────────────────────────────────────────────────────────────
    # Privados — utilidades de texto (sin estado, métodos estáticos)
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Normaliza un texto para comparación flexible:
            - Convierte a minúsculas
            - Elimina tildes y diacríticos
            - Elimina espacios, guiones, puntos y guiones bajos

        Ejemplos:
            "Presentación"        → "presentacion"
            "Material_de_Trabajo" → "materialdetrabajo"
            "1. Archivos"         → "1archivos"

        Args:
            text: Texto original.

        Returns:
            Texto normalizado para comparación.
        """
        text = text.lower()
        # NFD descompone caracteres acentuados en base + diacrítico
        text = unicodedata.normalize("NFD", text)
        # Eliminar categoría Mn (Mark, Nonspacing) = diacríticos
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")
        # Eliminar separadores comunes
        text = re.sub(r"[\s_\-\.]", "", text)
        return text

    @staticmethod
    def _detect_unit(filename: str) -> str | None:
        """
        Detecta el número de unidad en el nombre de un archivo.

        Patrones soportados:
            "U1_...", "U 1_...", "u1...", "Unidad1...", "Unidad 1..."

        No coincide con "u" dentro de palabras como "fundamental".

        Args:
            filename: Nombre del archivo sin extensión.

        Returns:
            Número de unidad como string ("1", "2", "3", "4"), o None.
        """
        lower = filename.lower()

        # Lookbehind negativo: "u" no debe estar precedida de letra
        # (maneja U1, _U2, "U 3" y evita "u" en "fundamental")
        match = re.search(r"(?<![a-z])u\s?(\d)", lower)
        if match:
            return match.group(1)

        # Patrón explícito "unidad" seguido de dígito
        match = re.search(r"unidad\s?(\d)", lower)
        if match:
            return match.group(1)

        return None

    def _detect_pdf_type(self, filename: str) -> str | None:
        """
        Detecta el tipo canónico de un PDF evaluando keywords en orden
        de especificidad (más específico primero).

        Args:
            filename: Nombre del archivo sin extensión.

        Returns:
            Tipo canónico ("Material_Fundamental", "Lectura_Fundamental",
            "Actividad_Formativa", "Actividad_Sumativa", "Actividad"), o None.
        """
        nombre_limpio = self._clean_text(filename)

        for keyword, tipo_canonico in self._PDF_TYPE_PRECEDENCE:
            if keyword in nombre_limpio:
                return tipo_canonico

        return None

    @staticmethod
    def _detect_sequence_number(filename: str) -> int | None:
        """
        Detecta un número secuencial al final del nombre de un archivo.

        Patrones soportados:
            "Lectura_Fundamental_2" → 2
            "LF02"                  → 2
            "Material_Fundamental1" → 1

        Args:
            filename: Nombre del archivo sin extensión.

        Returns:
            Número secuencial como int, o None si no existe.
        """
        match = re.search(r"[_\s]?(\d+)$", filename)
        if match:
            return int(match.group(1))
        return None