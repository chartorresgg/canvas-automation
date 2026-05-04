"""
Cliente HTTP para la API REST de Canvas LMS.

Centraliza toda comunicación con Canvas: autenticación, headers,
rate limiting, reintentos con backoff exponencial y manejo de errores.

Capa: Infraestructura
Patrón: ninguno — servicio de infraestructura base
Colaboradores: CourseRepository, FileRepository, PageRepository
               (únicos consumidores permitidos)
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Excepciones de dominio para errores de Canvas
# ──────────────────────────────────────────────────────────────────────────────

class CanvasAuthError(Exception):
    """Token inválido o sin permisos suficientes (401 / 403)."""


class CanvasNotFoundError(Exception):
    """Recurso no encontrado en Canvas (404)."""


class CanvasRateLimitError(Exception):
    """Canvas rechazó la petición por exceso de requests (403 rate limit)."""


class CanvasServerError(Exception):
    """Error interno del servidor Canvas (5xx)."""


class CanvasClientError(Exception):
    """Error de cliente no manejado específicamente (4xx genérico)."""


# ──────────────────────────────────────────────────────────────────────────────
# Configuración de reintentos
# ──────────────────────────────────────────────────────────────────────────────

# Códigos HTTP que justifican un reintento automático
_RETRY_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503, 504})

# Segundos de espera entre reintentos: [1s, 2s, 4s]
_BACKOFF_SEGUNDOS: list[float] = [1.0, 2.0, 4.0]


# ──────────────────────────────────────────────────────────────────────────────
# Cliente principal
# ──────────────────────────────────────────────────────────────────────────────

class CanvasHttpClient:
    """
    Cliente HTTP asíncrono para la API REST de Canvas LMS.

    Responsabilidad única (SRP): abstraer toda comunicación HTTP con
    Canvas LMS. Ningún otro componente del sistema conoce la URL base,
    el token, ni el formato de autenticación.

    Características:
        - Autenticación automática con Bearer Token
        - Reintentos con backoff exponencial (hasta 3 intentos)
        - Clasificación de errores HTTP en excepciones de dominio
        - Paginación automática mediante el header Link de Canvas
        - Logging estructurado de cada operación

    Uso:
        async with CanvasHttpClient() as client:
            datos = await client.get("courses/12345")

    Colaboradores permitidos:
        CourseRepository, FileRepository, PageRepository
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        account_id: int | None = None,
        timeout_segundos: float = 30.0,
    ) -> None:
        """
        Inicializa el cliente leyendo configuración del archivo .env.

        Args:
            base_url:         URL base de la API. Por defecto lee CANVAS_BASE_URL.
            token:            Token de acceso. Por defecto lee CANVAS_ACCESS_TOKEN.
            account_id:       ID de la cuenta Canvas. Por defecto lee CANVAS_ACCOUNT_ID.
            timeout_segundos: Timeout por petición en segundos. Default 30 s.
        """
        self._base_url: str = (
            base_url or os.getenv("CANVAS_BASE_URL", "")
        ).rstrip("/")

        self._token: str = token or os.getenv("CANVAS_ACCESS_TOKEN", "")

        self._account_id: int = account_id or int(
            os.getenv("CANVAS_ACCOUNT_ID", "1")
        )

        if not self._base_url:
            raise ValueError(
                "CANVAS_BASE_URL no está configurada. "
                "Verifica el archivo backend/.env"
            )
        if not self._token:
            raise ValueError(
                "CANVAS_ACCESS_TOKEN no está configurada. "
                "Verifica el archivo backend/.env"
            )

        self._timeout = httpx.Timeout(timeout_segundos)
        self._headers: dict[str, str] = {
            "Authorization": f"Bearer {self._token}",
            "User-Agent": "CanvasAutomation-PoliGran/1.0",
            "Accept": "application/json",
        }
        self._client: httpx.AsyncClient | None = None

    # ──────────────────────────────────────────────────────────────
    # Gestión del ciclo de vida del cliente HTTP
    # ──────────────────────────────────────────────────────────────

    async def __aenter__(self) -> CanvasHttpClient:
        """Abre la sesión HTTP reutilizable."""
        self._client = httpx.AsyncClient(
            headers=self._headers,
            timeout=self._timeout,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *_: object) -> None:
        """Cierra la sesión HTTP y libera recursos."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def account_id(self) -> int:
        """ID de la cuenta Canvas configurada."""
        return self._account_id

    # ──────────────────────────────────────────────────────────────
    # API pública — métodos HTTP
    # ──────────────────────────────────────────────────────────────

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Ejecuta GET sobre un endpoint de Canvas.

        Args:
            endpoint: Ruta relativa a la base URL (ej. "courses/123").
            params:   Parámetros de query string opcionales.

        Returns:
            Respuesta JSON de Canvas (dict o list).

        Raises:
            CanvasAuthError, CanvasNotFoundError, CanvasServerError,
            CanvasClientError según el código HTTP.
        """
        url = self._construir_url(endpoint)
        response = await self._ejecutar_con_reintentos("GET", url, params=params)
        return response.json()

    async def get_paginated(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> list[Any]:
        """
        Ejecuta GET con paginación automática usando el header Link de Canvas.

        Canvas devuelve máximo 100 items por página. Este método recorre
        automáticamente todas las páginas y retorna la lista completa.

        Args:
            endpoint: Ruta relativa a la base URL.
            params:   Parámetros adicionales. Se añade per_page=100 automáticamente.

        Returns:
            Lista completa de items de todas las páginas.
        """
        params = {**(params or {}), "per_page": 100}
        url = self._construir_url(endpoint)
        todos: list[Any] = []

        while url:
            response = await self._ejecutar_con_reintentos("GET", url, params=params)
            datos = response.json()

            if isinstance(datos, list):
                todos.extend(datos)
            else:
                todos.append(datos)

            # Canvas indica la siguiente página en el header Link
            url = self._extraer_siguiente_pagina(response)
            params = {}  # Los params de paginación van en la URL de Link

        return todos

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Ejecuta POST sobre un endpoint de Canvas.

        Args:
            endpoint: Ruta relativa a la base URL.
            data:     Payload como form-data (application/x-www-form-urlencoded).
            json:     Payload como JSON (application/json).
            files:    Archivos para multipart/form-data.

        Returns:
            Respuesta JSON de Canvas como dict.
        """
        url = self._construir_url(endpoint)
        response = await self._ejecutar_con_reintentos(
            "POST", url, data=data, json=json, files=files
        )
        return response.json()

    async def put(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Ejecuta PUT sobre un endpoint de Canvas.

        Args:
            endpoint: Ruta relativa a la base URL.
            json:     Payload como JSON.
            data:     Payload como form-data.

        Returns:
            Respuesta JSON de Canvas como dict.
        """
        url = self._construir_url(endpoint)
        response = await self._ejecutar_con_reintentos(
            "PUT", url, json=json, data=data
        )
        return response.json()

    async def post_binary(
        self,
        url: str,
        content: bytes,
        content_type: str,
    ) -> httpx.Response:
        """
        Sube contenido binario a una URL externa prefirmada.

        Canvas usa un protocolo de dos fases para subir archivos:
            1. POST /courses/{id}/files  → Canvas retorna una URL prefirmada
            2. POST {url_prefirmada}     → este método sube el binario real

        A diferencia de los otros métodos, aquí la URL es absoluta
        (no relativa a la base) y NO lleva el header de autorización
        de Canvas (la URL prefirmada ya incluye las credenciales).

        Args:
            url:          URL prefirmada completa retornada por Canvas.
            content:      Bytes del archivo a subir.
            content_type: MIME type del archivo (ej. "application/pdf").

        Returns:
            Respuesta HTTP cruda de la URL prefirmada.
        """
        cliente = self._obtener_cliente()
        response = await cliente.post(
            url,
            content=content,
            headers={"Content-Type": content_type},
        )
        response.raise_for_status()
        return response

    # ──────────────────────────────────────────────────────────────
    # Privados — infraestructura de reintentos y manejo de errores
    # ──────────────────────────────────────────────────────────────

    async def _ejecutar_con_reintentos(
        self,
        metodo: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Ejecuta una petición HTTP con reintentos automáticos y backoff.

        Reintenta hasta 3 veces para códigos en _RETRY_STATUS_CODES.
        Entre reintentos espera 1s, 2s y 4s respectivamente.

        Args:
            metodo: Verbo HTTP ("GET", "POST", "PUT").
            url:    URL completa de la petición.
            **kwargs: Argumentos adicionales para httpx (data, json, files).

        Returns:
            Respuesta HTTP exitosa.

        Raises:
            Excepciones específicas de Canvas según el código de error final.
        """
        cliente = self._obtener_cliente()
        ultimo_error: Exception | None = None

        for intento, espera in enumerate([0.0] + _BACKOFF_SEGUNDOS, start=1):
            if espera > 0:
                logger.info(
                    "Reintento %d/%d para %s %s — esperando %.1fs",
                    intento, len(_BACKOFF_SEGUNDOS) + 1, metodo, url, espera
                )
                await asyncio.sleep(espera)

            try:
                response = await cliente.request(metodo, url, **kwargs)

                if response.status_code not in _RETRY_STATUS_CODES:
                    self._verificar_respuesta(response, url)
                    logger.debug(
                        "%s %s → %d", metodo, url, response.status_code
                    )
                    return response

                ultimo_error = CanvasServerError(
                    f"Canvas retornó {response.status_code} en {url}"
                )

            except httpx.TimeoutException as exc:
                ultimo_error = exc
                logger.warning("Timeout en intento %d: %s", intento, url)
            except httpx.ConnectError as exc:
                ultimo_error = exc
                logger.warning("Error de conexión en intento %d: %s", intento, url)

        raise CanvasServerError(
            f"Falló después de {len(_BACKOFF_SEGUNDOS) + 1} intentos: {url}. "
            f"Último error: {ultimo_error}"
        )

    def _verificar_respuesta(self, response: httpx.Response, url: str) -> None:
        """
        Mapea códigos HTTP de error a excepciones de dominio específicas.

        Args:
            response: Respuesta HTTP de Canvas.
            url:      URL de la petición (para mensajes de error).

        Raises:
            CanvasAuthError:     401 o 403
            CanvasNotFoundError: 404
            CanvasRateLimitError: 403 con mensaje de rate limit
            CanvasClientError:   otros 4xx
            CanvasServerError:   5xx
        """
        if response.is_success:
            return

        codigo = response.status_code
        cuerpo = self._extraer_mensaje_error(response)

        if codigo == 401:
            raise CanvasAuthError(
                f"Token inválido o expirado. Verifica CANVAS_ACCESS_TOKEN en .env. "
                f"URL: {url}"
            )
        if codigo == 403:
            if "rate limit" in cuerpo.lower():
                raise CanvasRateLimitError(
                    f"Canvas limitó las peticiones. Espera unos segundos. URL: {url}"
                )
            raise CanvasAuthError(
                f"Sin permisos para esta operación. "
                f"Verifica que el token tenga permisos de administrador. "
                f"URL: {url} | Detalle: {cuerpo}"
            )
        if codigo == 404:
            raise CanvasNotFoundError(
                f"Recurso no encontrado en Canvas: {url} | Detalle: {cuerpo}"
            )
        if 400 <= codigo < 500:
            raise CanvasClientError(
                f"Error de cliente Canvas {codigo}: {url} | Detalle: {cuerpo}"
            )
        if codigo >= 500:
            raise CanvasServerError(
                f"Error interno de Canvas {codigo}: {url} | Detalle: {cuerpo}"
            )

    @staticmethod
    def _extraer_mensaje_error(response: httpx.Response) -> str:
        """
        Extrae el mensaje de error del cuerpo JSON de Canvas.

        Canvas puede retornar el error como:
            {"errors": [{"message": "..."}]}
            {"message": "..."}
            texto plano

        Returns:
            Mensaje de error legible o el texto crudo si no es JSON.
        """
        try:
            cuerpo = response.json()
            if isinstance(cuerpo, dict):
                if "errors" in cuerpo and isinstance(cuerpo["errors"], list):
                    errores = [
                        e.get("message", str(e))
                        for e in cuerpo["errors"]
                        if isinstance(e, dict)
                    ]
                    return " | ".join(errores)
                if "message" in cuerpo:
                    return str(cuerpo["message"])
            return str(cuerpo)
        except Exception:
            return response.text[:200]

    @staticmethod
    def _extraer_siguiente_pagina(response: httpx.Response) -> str | None:
        """
        Extrae la URL de la siguiente página del header Link de Canvas.

        Canvas usa el estándar RFC 5988 para paginación:
            Link: <https://...?page=2>; rel="next", <https://...?page=1>; rel="first"

        Returns:
            URL de la siguiente página, o None si es la última página.
        """
        link_header = response.headers.get("Link", "")
        if not link_header:
            return None

        for parte in link_header.split(","):
            if 'rel="next"' in parte:
                inicio = parte.find("<") + 1
                fin = parte.find(">")
                if inicio > 0 and fin > inicio:
                    return parte[inicio:fin].strip()

        return None

    def _construir_url(self, endpoint: str) -> str:
        """
        Construye la URL completa a partir de un endpoint relativo.

        Args:
            endpoint: Ruta relativa (ej. "courses/123" o "/courses/123").

        Returns:
            URL absoluta completa.
        """
        endpoint = endpoint.lstrip("/")
        return f"{self._base_url}/{endpoint}"

    def _obtener_cliente(self) -> httpx.AsyncClient:
        """
        Retorna el cliente HTTP activo.

        Raises:
            RuntimeError: Si se usa el cliente fuera del context manager.
        """
        if self._client is None:
            raise RuntimeError(
                "CanvasHttpClient debe usarse como context manager async. "
                "Usa: async with CanvasHttpClient() as client: ..."
            )
        return self._client