"""
Pruebas unitarias para CanvasHttpClient.

Estrategia: usar httpx.MockTransport para interceptar peticiones HTTP
sin hacer llamadas reales a Canvas. Esto garantiza que los tests son
deterministas, rápidos y no requieren conexión a internet.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from app.infrastructure.canvas.http_client import (
    CanvasAuthError,
    CanvasClientError,
    CanvasHttpClient,
    CanvasNotFoundError,
    CanvasRateLimitError,
    CanvasServerError,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers — MockTransport
# ──────────────────────────────────────────────────────────────────────────────

def _hacer_respuesta(
    status_code: int,
    body: Any = None,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    """
    Crea una respuesta HTTP simulada con cuerpo JSON.
    Usa httpx.Response con transport real para compatibilidad completa.
    """
    content = json.dumps(body or {}).encode()
    return httpx.Response(
        status_code=status_code,
        headers={"Content-Type": "application/json", **(headers or {})},
        content=content,
        request=httpx.Request("GET", "https://test.instructure.com/api/v1/test"),
    )


class MockTransport(httpx.AsyncBaseTransport):
    """
    Transport mock que intercepta peticiones y retorna respuestas controladas.
    Permite definir secuencias de respuestas para simular reintentos.
    """

    def __init__(self, respuestas: list[httpx.Response]) -> None:
        self._respuestas = list(respuestas)
        self._indice = 0
        self.peticiones_realizadas: list[httpx.Request] = []

    async def handle_async_request(
        self, request: httpx.Request
    ) -> httpx.Response:
        self.peticiones_realizadas.append(request)

        if self._indice >= len(self._respuestas):
            raise RuntimeError("MockTransport: se agotaron las respuestas simuladas")

        respuesta = self._respuestas[self._indice]
        self._indice += 1
        return respuesta


# ──────────────────────────────────────────────────────────────────────────────
# Fixture
# ──────────────────────────────────────────────────────────────────────────────

def _crear_cliente(
    respuestas: list[httpx.Response],
) -> tuple[CanvasHttpClient, MockTransport]:
    """
    Crea un CanvasHttpClient con transport mock inyectado.
    Retorna tanto el cliente como el transport para inspeccionar peticiones.
    """
    transport = MockTransport(respuestas)
    cliente = CanvasHttpClient(
        base_url="https://test.instructure.com/api/v1",
        token="token-de-test",
        account_id=1,
    )
    # Inyectar el transport mock directamente en el cliente httpx
    cliente._client = httpx.AsyncClient(
        headers=cliente._headers,
        transport=transport,
    )
    return cliente, transport


# ──────────────────────────────────────────────────────────────────────────────
# Tests: construcción y configuración
# ──────────────────────────────────────────────────────────────────────────────

class TestConstruccion:

    def test_lanza_error_si_no_hay_base_url(self) -> None:
        with patch.dict("os.environ", {
            "CANVAS_BASE_URL": "",
            "CANVAS_ACCESS_TOKEN": "token",
        }):
            with pytest.raises(ValueError, match="CANVAS_BASE_URL"):
                CanvasHttpClient()

    def test_lanza_error_si_no_hay_token(self) -> None:
        with patch.dict("os.environ", {
            "CANVAS_BASE_URL": "https://test.instructure.com/api/v1",
            "CANVAS_ACCESS_TOKEN": "",
        }):
            with pytest.raises(ValueError, match="CANVAS_ACCESS_TOKEN"):
                CanvasHttpClient()

    def test_lee_configuracion_del_entorno(self) -> None:
        with patch.dict("os.environ", {
            "CANVAS_BASE_URL": "https://poli.instructure.com/api/v1/",
            "CANVAS_ACCESS_TOKEN": "mi-token",
            "CANVAS_ACCOUNT_ID": "42",
        }):
            cliente = CanvasHttpClient()
            assert cliente.account_id == 42
            assert "mi-token" in cliente._headers["Authorization"]

    def test_elimina_slash_final_de_base_url(self) -> None:
        cliente = CanvasHttpClient(
            base_url="https://test.instructure.com/api/v1/",
            token="token",
        )
        assert not cliente._base_url.endswith("/")

    def test_lanza_error_si_se_usa_sin_context_manager(self) -> None:
        cliente = CanvasHttpClient(
            base_url="https://test.instructure.com/api/v1",
            token="token",
        )
        with pytest.raises(RuntimeError, match="context manager"):
            cliente._obtener_cliente()


# ──────────────────────────────────────────────────────────────────────────────
# Tests: método GET
# ──────────────────────────────────────────────────────────────────────────────

class TestGet:

    @pytest.mark.asyncio
    async def test_get_exitoso_retorna_dict(self) -> None:
        respuesta = _hacer_respuesta(200, {"id": 123, "name": "Curso Test"})
        cliente, _ = _crear_cliente([respuesta])

        resultado = await cliente.get("courses/123")

        assert resultado == {"id": 123, "name": "Curso Test"}

    @pytest.mark.asyncio
    async def test_get_construye_url_correctamente(self) -> None:
        respuesta = _hacer_respuesta(200, {"id": 1})
        cliente, transport = _crear_cliente([respuesta])

        await cliente.get("courses/456")

        url_llamada = str(transport.peticiones_realizadas[0].url)
        assert "courses/456" in url_llamada

    @pytest.mark.asyncio
    async def test_get_incluye_header_autorizacion(self) -> None:
        respuesta = _hacer_respuesta(200, {})
        cliente, transport = _crear_cliente([respuesta])

        await cliente.get("courses/1")

        headers = dict(transport.peticiones_realizadas[0].headers)
        assert "authorization" in headers
        assert "Bearer token-de-test" in headers["authorization"]

    @pytest.mark.asyncio
    async def test_get_404_lanza_not_found(self) -> None:
        respuesta = _hacer_respuesta(404, {"message": "Course not found"})
        cliente, _ = _crear_cliente([respuesta])

        with pytest.raises(CanvasNotFoundError):
            await cliente.get("courses/99999")

    @pytest.mark.asyncio
    async def test_get_401_lanza_auth_error(self) -> None:
        respuesta = _hacer_respuesta(401, {"errors": [{"message": "Invalid token"}]})
        cliente, _ = _crear_cliente([respuesta])

        with pytest.raises(CanvasAuthError, match="Token inválido"):
            await cliente.get("courses/1")

    @pytest.mark.asyncio
    async def test_get_403_sin_rate_limit_lanza_auth_error(self) -> None:
        respuesta = _hacer_respuesta(403, {"message": "Forbidden"})
        cliente, _ = _crear_cliente([respuesta])

        with pytest.raises(CanvasAuthError, match="permisos"):
            await cliente.get("courses/1")

    @pytest.mark.asyncio
    async def test_get_403_rate_limit_lanza_rate_limit_error(self) -> None:
        respuesta = _hacer_respuesta(403, {"message": "Rate limit exceeded"})
        cliente, _ = _crear_cliente([respuesta])

        with pytest.raises(CanvasRateLimitError):
            await cliente.get("courses/1")

    @pytest.mark.asyncio
    async def test_get_500_lanza_server_error(self) -> None:
        # 3 reintentos + 1 intento original = 4 respuestas
        respuestas = [_hacer_respuesta(500, {"message": "Internal error"})] * 4
        cliente, _ = _crear_cliente(respuestas)

        with pytest.raises(CanvasServerError):
            await cliente.get("courses/1")

    @pytest.mark.asyncio
    async def test_get_reintenta_en_500_y_tiene_exito(self) -> None:
        """Primer intento falla con 500, segundo tiene éxito con 200."""
        respuestas = [
            _hacer_respuesta(500, {}),
            _hacer_respuesta(200, {"id": 1}),
        ]
        cliente, transport = _crear_cliente(respuestas)

        # Parchamos asyncio.sleep para no esperar en tests
        with patch("asyncio.sleep"):
            resultado = await cliente.get("courses/1")

        assert resultado == {"id": 1}
        assert transport._indice == 2  # Se usaron 2 respuestas


# ──────────────────────────────────────────────────────────────────────────────
# Tests: método POST
# ──────────────────────────────────────────────────────────────────────────────

class TestPost:

    @pytest.mark.asyncio
    async def test_post_exitoso_retorna_dict(self) -> None:
        respuesta = _hacer_respuesta(201, {"id": 9876, "name": "Nuevo Curso"})
        cliente, _ = _crear_cliente([respuesta])

        resultado = await cliente.post(
            "accounts/1/courses",
            data={"course[name]": "Nuevo Curso"},
        )

        assert resultado["id"] == 9876

    @pytest.mark.asyncio
    async def test_post_con_json_serializa_correctamente(self) -> None:
        respuesta = _hacer_respuesta(200, {"id": 42})
        cliente, transport = _crear_cliente([respuesta])

        await cliente.post(
            "courses/1/content_migrations",
            json={"migration_type": "course_copy_importer"},
        )

        request = transport.peticiones_realizadas[0]
        assert request.method == "POST"

    @pytest.mark.asyncio
    async def test_post_422_lanza_client_error(self) -> None:
        respuesta = _hacer_respuesta(422, {"message": "Validation failed"})
        cliente, _ = _crear_cliente([respuesta])

        with pytest.raises(CanvasClientError):
            await cliente.post("accounts/1/courses", data={})


# ──────────────────────────────────────────────────────────────────────────────
# Tests: método PUT
# ──────────────────────────────────────────────────────────────────────────────

class TestPut:

    @pytest.mark.asyncio
    async def test_put_exitoso_retorna_dict(self) -> None:
        respuesta = _hacer_respuesta(200, {"url": "front-del-curso", "body": "<p>ok</p>"})
        cliente, _ = _crear_cliente([respuesta])

        resultado = await cliente.put(
            "courses/1/pages/front-del-curso",
            json={"wiki_page": {"body": "<p>ok</p>"}},
        )

        assert resultado["url"] == "front-del-curso"

    @pytest.mark.asyncio
    async def test_put_404_lanza_not_found(self) -> None:
        respuesta = _hacer_respuesta(404, {"message": "Page not found"})
        cliente, _ = _crear_cliente([respuesta])

        with pytest.raises(CanvasNotFoundError):
            await cliente.put("courses/1/pages/pagina-inexistente", json={})


# ──────────────────────────────────────────────────────────────────────────────
# Tests: paginación
# ──────────────────────────────────────────────────────────────────────────────

class TestPaginacion:

    def _respuesta_con_link(
        self, body: list, siguiente_url: str | None = None
    ) -> httpx.Response:
        """Crea respuesta con header Link de paginación."""
        headers: dict[str, str] = {}
        if siguiente_url:
            headers["Link"] = f'<{siguiente_url}>; rel="next"'
        return _hacer_respuesta(200, body, headers=headers)

    @pytest.mark.asyncio
    async def test_get_paginated_una_pagina(self) -> None:
        respuesta = self._respuesta_con_link([{"id": 1}, {"id": 2}])
        cliente, _ = _crear_cliente([respuesta])

        resultado = await cliente.get_paginated("courses")

        assert len(resultado) == 2

    @pytest.mark.asyncio
    async def test_get_paginated_multiples_paginas(self) -> None:
        respuesta_1 = self._respuesta_con_link(
            [{"id": 1}],
            siguiente_url="https://test.instructure.com/api/v1/courses?page=2",
        )
        respuesta_2 = self._respuesta_con_link([{"id": 2}])
        cliente, _ = _crear_cliente([respuesta_1, respuesta_2])

        resultado = await cliente.get_paginated("courses")

        assert len(resultado) == 2
        assert resultado[0]["id"] == 1
        assert resultado[1]["id"] == 2

    def test_extraer_siguiente_pagina_presente(self) -> None:
        response = _hacer_respuesta(
            200, {},
            headers={
                "Link": (
                    '<https://test.com?page=2>; rel="next", '
                    '<https://test.com?page=1>; rel="first"'
                )
            },
        )
        url = CanvasHttpClient._extraer_siguiente_pagina(response)
        assert url == "https://test.com?page=2"

    def test_extraer_siguiente_pagina_ausente(self) -> None:
        response = _hacer_respuesta(200, {})
        url = CanvasHttpClient._extraer_siguiente_pagina(response)
        assert url is None


# ──────────────────────────────────────────────────────────────────────────────
# Tests: extracción de mensajes de error
# ──────────────────────────────────────────────────────────────────────────────

class TestExtraccionErrores:

    def test_extrae_mensaje_de_errors_array(self) -> None:
        response = _hacer_respuesta(
            401, {"errors": [{"message": "Invalid token"}, {"message": "Expired"}]}
        )
        mensaje = CanvasHttpClient._extraer_mensaje_error(response)
        assert "Invalid token" in mensaje
        assert "Expired" in mensaje

    def test_extrae_mensaje_de_message_directo(self) -> None:
        response = _hacer_respuesta(403, {"message": "Forbidden"})
        mensaje = CanvasHttpClient._extraer_mensaje_error(response)
        assert "Forbidden" in mensaje

    def test_maneja_cuerpo_no_json(self) -> None:
        response = httpx.Response(
            status_code=500,
            content=b"Internal Server Error",
            request=httpx.Request("GET", "https://test.com"),
        )
        mensaje = CanvasHttpClient._extraer_mensaje_error(response)
        assert len(mensaje) > 0


# ──────────────────────────────────────────────────────────────────────────────
# Tests: construcción de URLs
# ──────────────────────────────────────────────────────────────────────────────

class TestConstruccionUrls:

    def test_endpoint_sin_slash_inicial(self) -> None:
        cliente = CanvasHttpClient(
            base_url="https://test.instructure.com/api/v1",
            token="token",
        )
        url = cliente._construir_url("courses/123")
        assert url == "https://test.instructure.com/api/v1/courses/123"

    def test_endpoint_con_slash_inicial(self) -> None:
        cliente = CanvasHttpClient(
            base_url="https://test.instructure.com/api/v1",
            token="token",
        )
        url = cliente._construir_url("/courses/123")
        assert url == "https://test.instructure.com/api/v1/courses/123"