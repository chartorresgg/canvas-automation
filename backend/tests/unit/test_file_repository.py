"""
Pruebas unitarias para FileRepository.

Estrategia: mock de CanvasHttpClient para aislar la lógica del repositorio
de las llamadas HTTP reales. Tests de sistema de archivos usan tmp_path.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from app.infrastructure.canvas.file_repository import (
    ArchivoSubido,
    FileRepository,
    FileUploadError,
    UploadSummary,
    _MIME_OVERRIDES,
)
from app.infrastructure.canvas.http_client import CanvasHttpClient


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _mock_http() -> MagicMock:
    mock = MagicMock(spec=CanvasHttpClient)
    mock.get  = AsyncMock()
    mock.post = AsyncMock()

    # El cliente httpx interno que usa _subir_binario
    mock_cliente = AsyncMock()
    mock._obtener_cliente.return_value = mock_cliente
    return mock


def _respuesta_token_subida(
    upload_url: str = "https://s3.amazonaws.com/upload",
    upload_params: dict | None = None,
) -> dict:
    """Simula la respuesta de Fase 1 de Canvas."""
    return {
        "upload_url":    upload_url,
        "upload_params": upload_params or {"key": "valor"},
    }


def _respuesta_confirmacion(file_id: int = 111) -> MagicMock:
    """Simula la respuesta de Fase 2 (subida exitosa con 201)."""
    mock = MagicMock()
    mock.status_code = 201
    mock.is_success  = True
    mock.json.return_value = {"id": file_id, "display_name": "archivo.pdf"}
    mock.headers = {}
    return mock


def _crear_estructura_archivos(base: Path) -> Path:
    """
    Crea una estructura de carpetas realista para tests de upload_all.

    Retorna la ruta al directorio de contenido.
    """
    content = base / "1. Archivos"
    (content / "1. Presentación").mkdir(parents=True)
    (content / "2. Material fundamental").mkdir(parents=True)
    (content / "3. Material de trabajo").mkdir(parents=True)

    (content / "1. Presentación" / "index.html").write_text("<html>p</html>")
    (content / "2. Material fundamental" / "U1_Lectura_Fundamental.pdf").write_bytes(b"pdf1")
    (content / "2. Material fundamental" / "U1_Material_Fundamental.pdf").write_bytes(b"pdf2")
    (content / "3. Material de trabajo" / "U1_Actividad.pdf").write_bytes(b"pdf3")

    return content


# ──────────────────────────────────────────────────────────────────────────────
# Tests: UploadSummary
# ──────────────────────────────────────────────────────────────────────────────

class TestUploadSummary:

    def test_total_exitosos_cuenta_correctamente(self) -> None:
        s = UploadSummary(exitosos={"a.pdf": 1, "b.pdf": 2})
        assert s.total_exitosos == 2

    def test_total_fallidos_cuenta_correctamente(self) -> None:
        s = UploadSummary(fallidos=["c.pdf", "d.pdf"])
        assert s.total_fallidos == 2

    def test_total_archivos_suma_ambos(self) -> None:
        s = UploadSummary(exitosos={"a.pdf": 1}, fallidos=["b.pdf"])
        assert s.total_archivos == 2

    def test_porcentaje_exito_cien_por_ciento(self) -> None:
        s = UploadSummary(exitosos={"a.pdf": 1, "b.pdf": 2})
        assert s.porcentaje_exito == 100.0

    def test_porcentaje_exito_cero_archivos(self) -> None:
        s = UploadSummary()
        assert s.porcentaje_exito == 0.0

    def test_porcentaje_exito_mixto(self) -> None:
        s = UploadSummary(
            exitosos={"a.pdf": 1},
            fallidos=["b.pdf", "c.pdf", "d.pdf"],
        )
        assert s.porcentaje_exito == 25.0

    def test_todo_exitoso_true_sin_fallidos(self) -> None:
        s = UploadSummary(exitosos={"a.pdf": 1})
        assert s.todo_exitoso is True

    def test_todo_exitoso_false_con_fallidos(self) -> None:
        s = UploadSummary(exitosos={"a.pdf": 1}, fallidos=["b.pdf"])
        assert s.todo_exitoso is False


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _detectar_content_type
# ──────────────────────────────────────────────────────────────────────────────

class TestDetectarContentType:

    @pytest.mark.parametrize("extension,expected", [
        (".pdf",   "application/pdf"),
        (".html",  "text/html"),
        (".htm",   "text/html"),
        (".png",   "image/png"),
        (".jpg",   "image/jpeg"),
        (".mp4",   "video/mp4"),
        (".xlsx",  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        (".zip",   "application/zip"),
        (".js",    "application/javascript"),
        (".css",   "text/css"),
        (".woff2", "font/woff2"),
    ])
    def test_detecta_tipos_conocidos(
        self, tmp_path: Path, extension: str, expected: str
    ) -> None:
        archivo = tmp_path / f"archivo{extension}"
        archivo.touch()
        resultado = FileRepository._detectar_content_type(archivo)
        assert resultado == expected

    def test_retorna_octet_stream_para_extension_desconocida(
        self, tmp_path: Path
    ) -> None:
        archivo = tmp_path / "archivo.xyz_desconocido"
        archivo.touch()
        resultado = FileRepository._detectar_content_type(archivo)
        assert resultado == "application/octet-stream"


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _listar_archivos
# ──────────────────────────────────────────────────────────────────────────────

class TestListarArchivos:

    def test_lista_archivos_recursivamente(self, tmp_path: Path) -> None:
        content = _crear_estructura_archivos(tmp_path)
        archivos = FileRepository._listar_archivos(content)

        rutas_rel = [rel for _, rel in archivos]
        assert "1. Presentación/index.html" in rutas_rel
        assert "2. Material fundamental/U1_Lectura_Fundamental.pdf" in rutas_rel

    def test_retorna_solo_archivos_no_carpetas(self, tmp_path: Path) -> None:
        content = _crear_estructura_archivos(tmp_path)
        archivos = FileRepository._listar_archivos(content)

        for ruta_abs, _ in archivos:
            assert ruta_abs.is_file()

    def test_usa_separador_slash_en_rutas_relativas(self, tmp_path: Path) -> None:
        content = _crear_estructura_archivos(tmp_path)
        archivos = FileRepository._listar_archivos(content)

        for _, ruta_rel in archivos:
            assert "\\" not in ruta_rel

    def test_lanza_error_si_directorio_no_existe(self, tmp_path: Path) -> None:
        with pytest.raises(FileUploadError, match="no existe"):
            FileRepository._listar_archivos(tmp_path / "no_existe")

    def test_orden_determinista(self, tmp_path: Path) -> None:
        content = _crear_estructura_archivos(tmp_path)
        lista_1 = FileRepository._listar_archivos(content)
        lista_2 = FileRepository._listar_archivos(content)

        rutas_1 = [r for _, r in lista_1]
        rutas_2 = [r for _, r in lista_2]
        assert rutas_1 == rutas_2

    def test_cuenta_total_archivos(self, tmp_path: Path) -> None:
        content = _crear_estructura_archivos(tmp_path)
        archivos = FileRepository._listar_archivos(content)
        assert len(archivos) == 4


# ──────────────────────────────────────────────────────────────────────────────
# Tests: upload_one()
# ──────────────────────────────────────────────────────────────────────────────

class TestUploadOne:

    @pytest.mark.asyncio
    async def test_retorna_archivo_subido_con_file_id(
        self, tmp_path: Path
    ) -> None:
        archivo = tmp_path / "U1_Lectura.pdf"
        archivo.write_bytes(b"contenido pdf")

        http = _mock_http()
        http.post.return_value = _respuesta_token_subida()
        http._obtener_cliente.return_value.post = AsyncMock(
            return_value=_respuesta_confirmacion(file_id=555)
        )

        repo = FileRepository(http)
        resultado = await repo.upload_one(
            course_id=9876,
            file_path=archivo,
            relative_path="2. Material fundamental/U1_Lectura.pdf",
        )

        assert isinstance(resultado, ArchivoSubido)
        assert resultado.file_id == 555
        assert resultado.ruta_relativa == "2. Material fundamental/U1_Lectura.pdf"

    @pytest.mark.asyncio
    async def test_llama_endpoint_correcto_en_fase_1(
        self, tmp_path: Path
    ) -> None:
        archivo = tmp_path / "test.pdf"
        archivo.write_bytes(b"pdf")

        http = _mock_http()
        http.post.return_value = _respuesta_token_subida()
        http._obtener_cliente.return_value.post = AsyncMock(
            return_value=_respuesta_confirmacion()
        )

        repo = FileRepository(http)
        await repo.upload_one(9876, archivo, "test.pdf")

        endpoint = http.post.call_args[0][0]
        assert "courses/9876/files" in endpoint

    @pytest.mark.asyncio
    async def test_envia_nombre_correcto_en_fase_1(
        self, tmp_path: Path
    ) -> None:
        archivo = tmp_path / "U1_Lectura_Fundamental.pdf"
        archivo.write_bytes(b"pdf")

        http = _mock_http()
        http.post.return_value = _respuesta_token_subida()
        http._obtener_cliente.return_value.post = AsyncMock(
            return_value=_respuesta_confirmacion()
        )

        repo = FileRepository(http)
        await repo.upload_one(
            9876, archivo,
            "2. Material fundamental/U1_Lectura_Fundamental.pdf"
        )

        data_enviada = http.post.call_args[1]["data"]
        assert data_enviada["name"] == "U1_Lectura_Fundamental.pdf"

    @pytest.mark.asyncio
    async def test_envia_carpeta_padre_correcta(
        self, tmp_path: Path
    ) -> None:
        archivo = tmp_path / "index.html"
        archivo.write_bytes(b"<html/>")

        http = _mock_http()
        http.post.return_value = _respuesta_token_subida()
        http._obtener_cliente.return_value.post = AsyncMock(
            return_value=_respuesta_confirmacion()
        )

        repo = FileRepository(http)
        await repo.upload_one(
            9876, archivo,
            "1. Presentación/index.html"
        )

        data_enviada = http.post.call_args[1]["data"]
        assert data_enviada["parent_folder_path"] == "1. Presentación"

    @pytest.mark.asyncio
    async def test_lanza_error_si_archivo_no_existe(
        self, tmp_path: Path
    ) -> None:
        http = _mock_http()
        repo = FileRepository(http)

        with pytest.raises(FileUploadError, match="no encontrado"):
            await repo.upload_one(
                9876,
                tmp_path / "no_existe.pdf",
                "no_existe.pdf",
            )

    @pytest.mark.asyncio
    async def test_url_descarga_contiene_file_id(
        self, tmp_path: Path
    ) -> None:
        archivo = tmp_path / "test.pdf"
        archivo.write_bytes(b"pdf")

        http = _mock_http()
        http.post.return_value = _respuesta_token_subida()
        http._obtener_cliente.return_value.post = AsyncMock(
            return_value=_respuesta_confirmacion(file_id=777)
        )

        repo = FileRepository(http)
        resultado = await repo.upload_one(9876, archivo, "test.pdf")

        assert "777" in resultado.url_descarga
        assert "9876" in resultado.url_descarga

    @pytest.mark.asyncio
    async def test_maneja_redirect_en_fase_2(
        self, tmp_path: Path
    ) -> None:
        """Canvas puede retornar 302 redirect en la subida binaria."""
        archivo = tmp_path / "test.pdf"
        archivo.write_bytes(b"pdf")

        # Respuesta de redirect
        mock_redirect = MagicMock()
        mock_redirect.status_code = 302
        mock_redirect.is_success  = False
        mock_redirect.headers     = {"Location": "https://canvas.com/confirm/123"}

        # Respuesta de confirmación tras el redirect
        mock_confirm = MagicMock()
        mock_confirm.status_code = 200
        mock_confirm.is_success  = True
        mock_confirm.json.return_value = {"id": 888}
        mock_confirm.headers = {}

        http = _mock_http()
        http.post.return_value = _respuesta_token_subida()

        mock_cliente = AsyncMock()
        mock_cliente.post = AsyncMock(return_value=mock_redirect)
        mock_cliente.get  = AsyncMock(return_value=mock_confirm)
        http._obtener_cliente.return_value = mock_cliente

        repo = FileRepository(http)
        resultado = await repo.upload_one(9876, archivo, "test.pdf")

        assert resultado.file_id == 888


# ──────────────────────────────────────────────────────────────────────────────
# Tests: upload_all()
# ──────────────────────────────────────────────────────────────────────────────

class TestUploadAll:

    def _setup_http_exitoso(self, file_id_start: int = 100) -> MagicMock:
        """Configura HTTP mock para simular subidas exitosas."""
        contador = [file_id_start]

        async def post_side_effect(*args, **kwargs):
            endpoint = args[0] if args else ""
            if "files" in endpoint:
                # Fase 1: retornar token de subida
                return _respuesta_token_subida()
            return {}

        http = _mock_http()
        http.post.side_effect = post_side_effect

        def nuevo_file_id():
            fid = contador[0]
            contador[0] += 1
            mock = _respuesta_confirmacion(file_id=fid)
            return mock

        http._obtener_cliente.return_value.post = AsyncMock(
            side_effect=lambda *a, **kw: nuevo_file_id()
        )
        return http

    @pytest.mark.asyncio
    async def test_sube_todos_los_archivos(self, tmp_path: Path) -> None:
        content = _crear_estructura_archivos(tmp_path)
        http = self._setup_http_exitoso()
        repo = FileRepository(http)

        summary = await repo.upload_all(course_id=9876, content_path=content)

        assert summary.total_exitosos == 4
        assert summary.total_fallidos == 0

    @pytest.mark.asyncio
    async def test_retorna_mapa_ruta_file_id(self, tmp_path: Path) -> None:
        content = _crear_estructura_archivos(tmp_path)
        http = self._setup_http_exitoso(file_id_start=200)
        repo = FileRepository(http)

        summary = await repo.upload_all(9876, content)

        assert len(summary.exitosos) == 4
        for ruta, fid in summary.exitosos.items():
            assert isinstance(ruta, str)
            assert isinstance(fid, int)
            assert fid >= 200

    @pytest.mark.asyncio
    async def test_registra_archivos_fallidos(self, tmp_path: Path) -> None:
        content = _crear_estructura_archivos(tmp_path)
        http = _mock_http()

        # Fase 1 siempre falla
        http.post.side_effect = Exception("Error de conexión")

        repo = FileRepository(http)

        with patch("asyncio.sleep"):
            summary = await repo.upload_all(9876, content)

        assert summary.total_fallidos == 4
        assert summary.total_exitosos == 0
        assert not summary.todo_exitoso

    @pytest.mark.asyncio
    async def test_llama_callback_de_progreso(self, tmp_path: Path) -> None:
        content = _crear_estructura_archivos(tmp_path)
        http = self._setup_http_exitoso()
        repo = FileRepository(http)

        llamadas: list[tuple] = []

        def on_progress(actual: int, total: int, ruta: str) -> None:
            llamadas.append((actual, total, ruta))

        await repo.upload_all(9876, content, on_progress=on_progress)

        assert len(llamadas) == 4
        # El último callback debe tener actual == total
        ultimo_actual, ultimo_total, _ = llamadas[-1]
        assert ultimo_actual == ultimo_total

    @pytest.mark.asyncio
    async def test_reintenta_archivos_fallidos(self, tmp_path: Path) -> None:
        """Primer intento falla, segundo tiene éxito."""
        content = _crear_estructura_archivos(tmp_path)
        http = _mock_http()

        contador_llamadas = [0]

        async def post_con_fallo_inicial(*args, **kwargs):
            endpoint = args[0] if args else ""
            if "files" in str(endpoint):
                contador_llamadas[0] += 1
                if contador_llamadas[0] <= 4:
                    # Primeros 4 llamados fallan (1 por archivo)
                    raise Exception("Error temporal")
                return _respuesta_token_subida()
            return {}

        http.post.side_effect = post_con_fallo_inicial
        http._obtener_cliente.return_value.post = AsyncMock(
            return_value=_respuesta_confirmacion()
        )

        repo = FileRepository(http)

        with patch("asyncio.sleep"):
            summary = await repo.upload_all(9876, content)

        # Algunos exitosos en el segundo intento
        assert summary.total_archivos == 4

    @pytest.mark.asyncio
    async def test_lanza_error_si_content_path_no_existe(
        self, tmp_path: Path
    ) -> None:
        http = _mock_http()
        repo = FileRepository(http)

        with pytest.raises(FileUploadError, match="no existe"):
            await repo.upload_all(9876, tmp_path / "no_existe")