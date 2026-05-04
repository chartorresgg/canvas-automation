"""
Pruebas para el router de deploy y el TaskManager.
Usa TestClient de FastAPI para evitar levantar un servidor real.
"""

from __future__ import annotations

import asyncio
import io
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.domain.value_objects.progress_event import EventStatus, ProgressEvent
from app.main import app
from app.presentation.task_manager import TaskManager


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _crear_zip_bytes() -> bytes:
    """Crea un ZIP mínimo válido en memoria."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("1. Archivos/1. Presentación/index.html", "<html/>")
        zf.writestr(
            "1. Archivos/2. Material fundamental/U1_Lectura_Fundamental.pdf",
            b"pdf",
        )
    return buf.getvalue()


def _form_data_nuevo() -> dict:
    return {
        "course_option":         "new",
        "course_name":           "Fundamentos de Python",
        "template_id":           "99001",
        "modelo_instruccional":  "Unidades",
        "nivel_formacion":       "Pregrado",
    }


def _form_data_existente() -> dict:
    return {
        "course_option":        "existing",
        "course_id":            "12345",
        "modelo_instruccional": "Unidades",
        "nivel_formacion":      "Pregrado",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Tests: TaskManager
# ──────────────────────────────────────────────────────────────────────────────

class TestTaskManager:

    def test_registrar_crea_queue(self) -> None:
        mgr   = TaskManager()
        queue = mgr.registrar("abc-123")
        assert isinstance(queue, asyncio.Queue)

    def test_obtener_queue_existente(self) -> None:
        mgr = TaskManager()
        q1  = mgr.registrar("abc")
        q2  = mgr.obtener_queue("abc")
        assert q1 is q2

    def test_obtener_queue_inexistente_retorna_none(self) -> None:
        mgr = TaskManager()
        assert mgr.obtener_queue("no-existe") is None

    def test_existe_true_para_tarea_registrada(self) -> None:
        mgr = TaskManager()
        mgr.registrar("tarea-1")
        assert mgr.existe("tarea-1") is True

    def test_existe_false_para_tarea_no_registrada(self) -> None:
        mgr = TaskManager()
        assert mgr.existe("tarea-2") is False

    def test_marcar_completada_envia_sentinel(self) -> None:
        mgr   = TaskManager()
        queue = mgr.registrar("tarea-3")
        mgr.marcar_completada("tarea-3")
        # El sentinel None debe estar en la queue
        item = queue.get_nowait()
        assert item is None

    def test_marcar_completada_marca_entry(self) -> None:
        mgr = TaskManager()
        mgr.registrar("tarea-4")
        mgr.marcar_completada("tarea-4")
        assert mgr._tasks["tarea-4"].completada is True

    def test_limpiar_completadas(self) -> None:
        mgr = TaskManager()
        mgr.registrar("t1")
        mgr.registrar("t2")
        mgr.marcar_completada("t1")
        eliminadas = mgr.limpiar_completadas()
        assert eliminadas == 1
        assert mgr.existe("t1") is False
        assert mgr.existe("t2") is True


# ──────────────────────────────────────────────────────────────────────────────
# Tests: POST /api/v1/deploy/upload (sprint 1 — sin cambios)
# ──────────────────────────────────────────────────────────────────────────────

class TestUploadEndpoint:

    def test_upload_zip_valido_retorna_200(self) -> None:
        client = TestClient(app)
        resp = client.post(
            "/api/v1/deploy/upload",
            files={"zip_file": ("curso.zip", _crear_zip_bytes(), "application/zip")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert data["total_files"] > 0

    def test_upload_archivo_no_zip_retorna_400(self) -> None:
        client = TestClient(app)
        resp = client.post(
            "/api/v1/deploy/upload",
            files={"zip_file": ("curso.txt", b"no es zip", "text/plain")},
        )
        assert resp.status_code == 400

    def test_upload_retorna_folders_renamed(self) -> None:
        # ZIP con nombre de carpeta alternativo
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("1 Archivos/presentacion/index.html", "<html/>")
        client = TestClient(app)
        resp = client.post(
            "/api/v1/deploy/upload",
            files={"zip_file": ("test.zip", buf.getvalue(), "application/zip")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "folders_renamed" in data


# ──────────────────────────────────────────────────────────────────────────────
# Tests: POST /api/v1/deploy
# ──────────────────────────────────────────────────────────────────────────────

class TestDeployEndpoint:

    def _mock_background_task(self):
        """Context manager que parchea _ejecutar_deploy_background."""
        return patch(
            "app.presentation.routers.deploy._ejecutar_deploy_background",
            new_callable=lambda: lambda *a, **kw: AsyncMock(),
        )

    def test_deploy_nuevo_retorna_202(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        with patch(
            "app.presentation.routers.deploy._ejecutar_deploy_background",
            new=AsyncMock(),
        ):
            resp = client.post(
                "/api/v1/deploy",
                data=_form_data_nuevo(),
                files={"zip_file": ("curso.zip", _crear_zip_bytes(), "application/zip")},
            )
        assert resp.status_code == 202

    def test_deploy_retorna_task_id(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        with patch(
            "app.presentation.routers.deploy._ejecutar_deploy_background",
            new=AsyncMock(),
        ):
            resp = client.post(
                "/api/v1/deploy",
                data=_form_data_nuevo(),
                files={"zip_file": ("curso.zip", _crear_zip_bytes(), "application/zip")},
            )
        data = resp.json()
        assert "task_id" in data
        assert len(data["task_id"]) > 0

    def test_deploy_retorna_stream_url(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        with patch(
            "app.presentation.routers.deploy._ejecutar_deploy_background",
            new=AsyncMock(),
        ):
            resp = client.post(
                "/api/v1/deploy",
                data=_form_data_nuevo(),
                files={"zip_file": ("curso.zip", _crear_zip_bytes(), "application/zip")},
            )
        data = resp.json()
        assert "stream_url" in data
        assert "stream" in data["stream_url"]

    def test_deploy_sin_zip_retorna_422(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/v1/deploy",
            data=_form_data_nuevo(),
            # Sin archivo ZIP
        )
        assert resp.status_code in (400, 422)

    def test_deploy_archivo_no_zip_retorna_400(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/v1/deploy",
            data=_form_data_nuevo(),
            files={"zip_file": ("curso.txt", b"no zip", "text/plain")},
        )
        assert resp.status_code == 400

    def test_deploy_existente_retorna_202(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        with patch(
            "app.presentation.routers.deploy._ejecutar_deploy_background",
            new=AsyncMock(),
        ):
            resp = client.post(
                "/api/v1/deploy",
                data=_form_data_existente(),
                files={"zip_file": ("curso.zip", _crear_zip_bytes(), "application/zip")},
            )
        assert resp.status_code == 202


# ──────────────────────────────────────────────────────────────────────────────
# Tests: GET /api/v1/deploy/stream/{task_id}
# ──────────────────────────────────────────────────────────────────────────────

class TestStreamEndpoint:

    def test_stream_task_id_inexistente_retorna_404(self) -> None:
        client = TestClient(app)
        resp = client.get("/api/v1/deploy/stream/id-que-no-existe")
        assert resp.status_code == 404

    def test_stream_emite_eventos_sse(self) -> None:
        """
        Verifica que el stream SSE emite eventos con formato correcto.
        Usa un task_id real registrado en el TaskManager.
        """
        from app.presentation.task_manager import task_manager

        task_id = "test-stream-123"
        queue   = task_manager.registrar(task_id)

        # Pre-cargar eventos en la queue
        evento_inicio = ProgressEvent.iniciando()
        evento_fin    = ProgressEvent.completado(course_id=9876)
        queue.put_nowait(evento_inicio)
        queue.put_nowait(evento_fin)
        queue.put_nowait(None)  # sentinel

        client = TestClient(app)
        resp = client.get(
            f"/api/v1/deploy/stream/{task_id}",
            headers={"Accept": "text/event-stream"},
        )

        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")

        contenido = resp.text
        assert "data:" in contenido
        assert "pending" in contenido or "completed" in contenido

    def test_stream_contiene_formato_sse_correcto(self) -> None:
        """Los eventos deben seguir el formato 'data: {...}\\n\\n'."""
        from app.presentation.task_manager import task_manager

        task_id = "test-formato-sse"
        queue   = task_manager.registrar(task_id)

        queue.put_nowait(ProgressEvent.iniciando())
        queue.put_nowait(None)

        client = TestClient(app)
        resp = client.get(f"/api/v1/deploy/stream/{task_id}")

        lines = resp.text.split("\n")
        data_lines = [l for l in lines if l.startswith("data:")]
        assert len(data_lines) >= 1

    def test_stream_task_id_registrado_retorna_200(self) -> None:
        from app.presentation.task_manager import task_manager

        task_id = "test-existe-456"
        queue   = task_manager.registrar(task_id)
        queue.put_nowait(ProgressEvent.completado(course_id=1))
        queue.put_nowait(None)

        client = TestClient(app)
        resp = client.get(f"/api/v1/deploy/stream/{task_id}")
        assert resp.status_code == 200