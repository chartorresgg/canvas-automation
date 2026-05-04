"""
Repositorio de operaciones sobre archivos en Canvas LMS.

Gestiona la subida de archivos usando el protocolo de tres fases de Canvas:
    Fase 1 — Solicitar URL prefirmada al servidor de Canvas
    Fase 2 — Subir el binario a la URL prefirmada (S3/CDN)
    Fase 3 — Confirmar la subida para que Canvas registre el archivo

Capa: Infraestructura
Patrón: Repository
Colaboradores: CanvasHttpClient
"""

from __future__ import annotations

import asyncio
import logging
import mimetypes
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass, field
from pathlib import Path

from app.infrastructure.canvas.http_client import CanvasHttpClient

logger = logging.getLogger(__name__)

# Mapa de extensiones que Canvas a veces no reconoce correctamente
_MIME_OVERRIDES: dict[str, str] = {
    ".html":  "text/html",
    ".htm":   "text/html",
    ".pdf":   "application/pdf",
    ".xlsx":  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls":   "application/vnd.ms-excel",
    ".mp4":   "video/mp4",
    ".mp3":   "audio/mpeg",
    ".zip":   "application/zip",
    ".png":   "image/png",
    ".jpg":   "image/jpeg",
    ".jpeg":  "image/jpeg",
    ".gif":   "image/gif",
    ".svg":   "image/svg+xml",
    ".css":   "text/css",
    ".js":    "application/javascript",
    ".json":  "application/json",
    ".woff":  "font/woff",
    ".woff2": "font/woff2",
    ".ttf":   "font/ttf",
}

# Número máximo de reintentos por archivo individual
MAX_REINTENTOS_POR_ARCHIVO: int = 3

# Pausa entre reintentos de un archivo fallido (segundos)
PAUSA_REINTENTO_SEG: float = 2.0


# ──────────────────────────────────────────────────────────────────────────────
# Value Objects
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ArchivoSubido:
    """Resultado exitoso de subida de un archivo individual a Canvas."""
    file_id: int
    nombre: str
    ruta_relativa: str
    size_bytes: int
    content_type: str
    url_descarga: str


@dataclass
class UploadSummary:
    """
    Resumen agregado del proceso de subida masiva.
    Mutable durante el proceso; se congela al retornar al orquestador.
    """
    exitosos: dict[str, int] = field(default_factory=dict)
    fallidos: list[str]      = field(default_factory=list)

    @property
    def total_exitosos(self) -> int:
        return len(self.exitosos)

    @property
    def total_fallidos(self) -> int:
        return len(self.fallidos)

    @property
    def total_archivos(self) -> int:
        return self.total_exitosos + self.total_fallidos

    @property
    def porcentaje_exito(self) -> float:
        if self.total_archivos == 0:
            return 0.0
        return round((self.total_exitosos / self.total_archivos) * 100, 1)

    @property
    def todo_exitoso(self) -> bool:
        return self.total_fallidos == 0


# ──────────────────────────────────────────────────────────────────────────────
# Excepción específica
# ──────────────────────────────────────────────────────────────────────────────

class FileUploadError(Exception):
    """Fallo irrecuperable al subir un archivo a Canvas."""


# ──────────────────────────────────────────────────────────────────────────────
# Repositorio principal
# ──────────────────────────────────────────────────────────────────────────────

class FileRepository:
    """
    Repositorio de subida masiva de archivos a Canvas LMS.

    Responsabilidad única (SRP): gestionar la transferencia de archivos
    locales al sistema de archivos de un curso Canvas usando el protocolo
    de tres fases. No conoce la estructura del aula ni la lógica de páginas.

    Protocolo de subida Canvas (3 fases):
        1. POST /courses/{id}/files
           → Canvas valida permisos y retorna {upload_url, upload_params}
        2. POST {upload_url} con el binario del archivo
           → S3/CDN retorna confirmación o redirect
        3. GET {confirm_url} si Canvas retorna redirect 301/302
           → Canvas registra el archivo y retorna {id, display_name}

    Colaboradores:
        CanvasHttpClient — único medio de comunicación HTTP.
    """

    def __init__(self, http: CanvasHttpClient) -> None:
        self._http = http

    # ──────────────────────────────────────────────────────────────
    # API pública
    # ──────────────────────────────────────────────────────────────

    async def upload_all(
        self,
        course_id: int,
        content_path: Path,
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> UploadSummary:
        """
        Sube recursivamente todos los archivos de una carpeta a Canvas.

        Recorre content_path de forma recursiva, sube cada archivo
        manteniendo la ruta relativa como estructura de carpetas en Canvas.
        Aplica reintentos automáticos por archivo (hasta 3 veces).

        Args:
            course_id:    ID del curso Canvas destino.
            content_path: Directorio raíz de los archivos a subir
                          (normalmente la carpeta "1. Archivos" normalizada).
            on_progress:  Callback opcional invocado tras cada archivo:
                          on_progress(archivos_completados, total, ruta_relativa)
                          Usado por el orquestador para emitir ProgressEvents.

        Returns:
            UploadSummary con el mapa {ruta_relativa: file_id} de exitosos
            y la lista de rutas que fallaron tras todos los reintentos.
        """
        archivos = self._listar_archivos(content_path)
        total = len(archivos)
        summary = UploadSummary()

        logger.info(
            "Iniciando subida masiva: %d archivos desde '%s' → curso %d",
            total, content_path, course_id,
        )

        for idx, (ruta_abs, ruta_rel) in enumerate(archivos, start=1):
            exito = await self._subir_con_reintentos(
                course_id, ruta_abs, ruta_rel, summary
            )

            if on_progress:
                on_progress(idx, total, ruta_rel)

            logger.debug(
                "Progreso: %d/%d (%s) — %s",
                idx, total, ruta_rel,
                "OK" if exito else "FALLÓ",
            )

        logger.info(
            "Subida completada: %d exitosos, %d fallidos (%.1f%% éxito)",
            summary.total_exitosos,
            summary.total_fallidos,
            summary.porcentaje_exito,
        )

        if summary.total_fallidos > 0:
            logger.warning(
                "Archivos fallidos: %s", summary.fallidos
            )

        return summary

    async def upload_one(
        self,
        course_id: int,
        file_path: Path,
        relative_path: str,
    ) -> ArchivoSubido:
        """
        Sube un único archivo a Canvas usando el protocolo de tres fases.

        Args:
            course_id:     ID del curso Canvas destino.
            file_path:     Ruta absoluta al archivo en disco local.
            relative_path: Ruta relativa que se usará como nombre/carpeta
                           en Canvas (ej. "2. Material fundamental/U1_LF.pdf").

        Returns:
            ArchivoSubido con el file_id y metadatos del archivo en Canvas.

        Raises:
            FileUploadError: Si el archivo no existe o falla la subida.
            CanvasAuthError: Sin permisos de subida en el curso.
        """
        if not file_path.exists():
            raise FileUploadError(
                f"Archivo no encontrado en disco: '{file_path}'"
            )

        contenido = file_path.read_bytes()
        content_type = self._detectar_content_type(file_path)
        nombre_canvas = Path(relative_path).name
        carpeta_canvas = str(Path(relative_path).parent).replace("\\", "/")

        if carpeta_canvas == ".":
            carpeta_canvas = ""

        # ── Fase 1: solicitar token de subida a Canvas ────────────────────
        token_respuesta = await self._http.post(
            f"courses/{course_id}/files",
            data={
                "name":             nombre_canvas,
                "size":             str(len(contenido)),
                "content_type":     content_type,
                "parent_folder_path": carpeta_canvas,
                "on_duplicate":     "overwrite",
            },
        )

        upload_url:    str  = token_respuesta["upload_url"]
        upload_params: dict = token_respuesta.get("upload_params", {})

        # ── Fase 2: subir el binario a la URL prefirmada (S3/CDN) ─────────
        file_id = await self._subir_binario(
            upload_url=upload_url,
            upload_params=upload_params,
            contenido=contenido,
            content_type=content_type,
            nombre=nombre_canvas,
        )

        logger.debug(
            "Archivo subido: '%s' → file_id=%d", relative_path, file_id
        )

        return ArchivoSubido(
            file_id=file_id,
            nombre=nombre_canvas,
            ruta_relativa=relative_path,
            size_bytes=len(contenido),
            content_type=content_type,
            url_descarga=(
                f"https://poli.instructure.com/courses/{course_id}"
                f"/files/{file_id}/download"
            ),
        )

    # ──────────────────────────────────────────────────────────────
    # Privados — lógica de subida
    # ──────────────────────────────────────────────────────────────

    async def _subir_con_reintentos(
        self,
        course_id: int,
        ruta_abs: Path,
        ruta_rel: str,
        summary: UploadSummary,
    ) -> bool:
        """
        Intenta subir un archivo hasta MAX_REINTENTOS_POR_ARCHIVO veces.

        Registra el resultado en el UploadSummary proporcionado.

        Returns:
            True si la subida fue exitosa, False si falló tras todos los reintentos.
        """
        ultimo_error: Exception | None = None

        for intento in range(1, MAX_REINTENTOS_POR_ARCHIVO + 1):
            try:
                archivo_subido = await self.upload_one(
                    course_id, ruta_abs, ruta_rel
                )
                summary.exitosos[ruta_rel] = archivo_subido.file_id
                return True

            except Exception as exc:
                ultimo_error = exc
                if intento < MAX_REINTENTOS_POR_ARCHIVO:
                    logger.warning(
                        "Reintento %d/%d para '%s': %s",
                        intento, MAX_REINTENTOS_POR_ARCHIVO, ruta_rel, exc,
                    )
                    await asyncio.sleep(PAUSA_REINTENTO_SEG)

        logger.error(
            "Falló definitivamente '%s' tras %d intentos: %s",
            ruta_rel, MAX_REINTENTOS_POR_ARCHIVO, ultimo_error,
        )
        summary.fallidos.append(ruta_rel)
        return False

    async def _subir_binario(
        self,
        upload_url: str,
        upload_params: dict,
        contenido: bytes,
        content_type: str,
        nombre: str,
    ) -> int:
        """
        Ejecuta la Fase 2 y Fase 3 del protocolo de subida de Canvas.

        Canvas puede retornar:
            - 201 Created con el file_id directamente en el JSON
            - 301/302 Redirect hacia una URL de confirmación

        En ambos casos retorna el file_id definitivo del archivo en Canvas.

        Args:
            upload_url:    URL prefirmada retornada en Fase 1.
            upload_params: Parámetros adicionales requeridos por Canvas/S3.
            contenido:     Bytes del archivo a subir.
            content_type:  MIME type del archivo.
            nombre:        Nombre del archivo.

        Returns:
            file_id del archivo registrado en Canvas.

        Raises:
            FileUploadError: Si la respuesta no contiene un file_id válido.
        """
        # Construir el form-data multipart con los params de Canvas
        files_data: dict = {}
        for key, value in upload_params.items():
            files_data[key] = (None, str(value))

        files_data["file"] = (nombre, contenido, content_type)

        # Canvas/S3 puede retornar 201 con JSON o 301/302 redirect
        cliente = self._http._obtener_cliente()
        response = await cliente.post(
            upload_url,
            files=files_data,
        )

        # Fase 3: si hay redirect, seguir la URL de confirmación
        if response.status_code in (301, 302):
            confirm_url = response.headers.get("Location", "")
            if not confirm_url:
                raise FileUploadError(
                    f"Canvas retornó redirect sin Location header "
                    f"para upload_url={upload_url}"
                )
            response = await cliente.get(confirm_url)

        if not response.is_success:
            raise FileUploadError(
                f"Error en subida binaria: HTTP {response.status_code} "
                f"para '{nombre}'"
            )

        datos = response.json()
        file_id = datos.get("id")

        if not file_id:
            raise FileUploadError(
                f"Canvas no retornó file_id tras subir '{nombre}'. "
                f"Respuesta: {datos}"
            )

        return int(file_id)

    # ──────────────────────────────────────────────────────────────
    # Privados — utilidades
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _listar_archivos(content_path: Path) -> list[tuple[Path, str]]:
        """
        Recorre recursivamente content_path y retorna lista de archivos.

        Returns:
            Lista de (ruta_absoluta, ruta_relativa_con_slash) ordenada
            por ruta relativa para subida determinista.
        """
        if not content_path.is_dir():
            raise FileUploadError(
                f"El directorio de contenido no existe: '{content_path}'"
            )

        archivos: list[tuple[Path, str]] = []

        for ruta_abs in sorted(content_path.rglob("*")):
            if ruta_abs.is_file():
                ruta_rel = (
                    ruta_abs.relative_to(content_path)
                    .as_posix()  # Siempre usa / independiente del SO
                )
                archivos.append((ruta_abs, ruta_rel))

        return archivos

    @staticmethod
    def _detectar_content_type(file_path: Path) -> str:
        """
        Detecta el MIME type de un archivo por su extensión.

        Usa _MIME_OVERRIDES para extensiones que mimetypes no maneja
        correctamente, con fallback a application/octet-stream.

        Args:
            file_path: Ruta al archivo.

        Returns:
            MIME type como string (ej. "application/pdf").
        """
        extension = file_path.suffix.lower()
        if extension in _MIME_OVERRIDES:
            return _MIME_OVERRIDES[extension]

        tipo, _ = mimetypes.guess_type(str(file_path))
        return tipo or "application/octet-stream"