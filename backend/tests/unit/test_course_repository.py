"""
Pruebas unitarias para CourseRepository.

Estrategia: mock de CanvasHttpClient para aislar el repositorio
de las llamadas HTTP reales. Se prueban los contratos de dominio,
no los detalles de la API de Canvas.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.canvas.course_repository import (
    CourseInfo,
    CourseRepository,
    MigrationFailedError,
    MigrationResult,
    MigrationTimeoutError,
)
from app.infrastructure.canvas.http_client import (
    CanvasHttpClient,
    CanvasNotFoundError,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _mock_http(account_id: int = 1) -> MagicMock:
    """Crea un mock de CanvasHttpClient con account_id configurado."""
    mock = MagicMock(spec=CanvasHttpClient)
    mock.account_id = account_id
    mock.get  = AsyncMock()
    mock.post = AsyncMock()
    mock.put  = AsyncMock()
    return mock


def _respuesta_curso(
    course_id: int = 9876,
    name: str = "Fundamentos de Programación",
    workflow_state: str = "available",
) -> dict:
    return {
        "id": course_id,
        "name": name,
        "course_code": name,
        "workflow_state": workflow_state,
    }


def _respuesta_migracion(
    migration_id: int = 42,
    workflow_state: str = "running",
) -> dict:
    return {
        "id": migration_id,
        "workflow_state": workflow_state,
        "migration_type": "course_copy_importer",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Tests: CourseInfo
# ──────────────────────────────────────────────────────────────────────────────

class TestCourseInfo:

    def test_desde_respuesta_canvas_construye_correctamente(self) -> None:
        data = _respuesta_curso(course_id=1234, name="Mi Curso")
        info = CourseInfo.desde_respuesta_canvas(data)

        assert info.id == 1234
        assert info.name == "Mi Curso"
        assert "1234" in info.url

    def test_url_contiene_dominio_poli(self) -> None:
        info = CourseInfo.desde_respuesta_canvas(_respuesta_curso(course_id=5678))
        assert "poli.instructure.com" in info.url
        assert "5678" in info.url

    def test_es_inmutable(self) -> None:
        info = CourseInfo.desde_respuesta_canvas(_respuesta_curso())
        with pytest.raises(Exception):
            info.id = 999  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────────────────────
# Tests: MigrationResult
# ──────────────────────────────────────────────────────────────────────────────

class TestMigrationResult:

    def test_fallida_true_cuando_estado_es_failed(self) -> None:
        result = MigrationResult(42, 1, "failed", False)
        assert result.fallida is True

    def test_fallida_false_cuando_estado_es_completed(self) -> None:
        result = MigrationResult(42, 1, "completed", True)
        assert result.fallida is False

    def test_completada_false_cuando_running(self) -> None:
        result = MigrationResult(42, 1, "running", False)
        assert result.completada is False


# ──────────────────────────────────────────────────────────────────────────────
# Tests: create_course()
# ──────────────────────────────────────────────────────────────────────────────

class TestCreateCourse:

    @pytest.mark.asyncio
    async def test_retorna_course_info_con_id_correcto(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_curso(course_id=9876)
        repo = CourseRepository(http)

        info = await repo.create_course("Fundamentos de Programación")

        assert info.id == 9876
        assert info.name == "Fundamentos de Programación"

    @pytest.mark.asyncio
    async def test_llama_endpoint_correcto(self) -> None:
        http = _mock_http(account_id=1)
        http.post.return_value = _respuesta_curso()
        repo = CourseRepository(http)

        await repo.create_course("Curso Test")

        http.post.assert_called_once()
        endpoint_llamado = http.post.call_args[0][0]
        assert "accounts/1/courses" in endpoint_llamado

    @pytest.mark.asyncio
    async def test_envia_nombre_en_data(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_curso()
        repo = CourseRepository(http)

        await repo.create_course("Mi Curso Especial")

        kwargs = http.post.call_args[1]
        data = kwargs.get("data", {})
        assert data.get("course[name]") == "Mi Curso Especial"

    @pytest.mark.asyncio
    async def test_curso_se_crea_como_privado(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_curso()
        repo = CourseRepository(http)

        await repo.create_course("Curso Privado")

        kwargs = http.post.call_args[1]
        data = kwargs.get("data", {})
        assert data.get("course[is_public]") == "false"
        assert data.get("course[license]") == "private"

    @pytest.mark.asyncio
    async def test_propaga_excepcion_de_canvas(self) -> None:
        from app.infrastructure.canvas.http_client import CanvasAuthError
        http = _mock_http()
        http.post.side_effect = CanvasAuthError("Sin permisos")
        repo = CourseRepository(http)

        with pytest.raises(CanvasAuthError):
            await repo.create_course("Curso Test")


# ──────────────────────────────────────────────────────────────────────────────
# Tests: copy_template()
# ──────────────────────────────────────────────────────────────────────────────

class TestCopyTemplate:

    @pytest.mark.asyncio
    async def test_retorna_migration_result_con_id(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_migracion(migration_id=42)
        repo = CourseRepository(http)

        result = await repo.copy_template(src_id=10001, dst_id=9876)

        assert result.migration_id == 42
        assert result.course_id == 9876
        assert result.completada is False

    @pytest.mark.asyncio
    async def test_llama_endpoint_del_curso_destino(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_migracion()
        repo = CourseRepository(http)

        await repo.copy_template(src_id=10001, dst_id=9876)

        endpoint = http.post.call_args[0][0]
        assert "courses/9876/content_migrations" in endpoint

    @pytest.mark.asyncio
    async def test_envia_tipo_de_migracion_correcto(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_migracion()
        repo = CourseRepository(http)

        await repo.copy_template(src_id=10001, dst_id=9876)

        kwargs = http.post.call_args[1]
        json_payload = kwargs.get("json", {})
        assert json_payload["migration_type"] == "course_copy_importer"
        assert json_payload["settings"]["source_course_id"] == 10001


# ──────────────────────────────────────────────────────────────────────────────
# Tests: poll_migration()
# ──────────────────────────────────────────────────────────────────────────────

class TestPollMigration:

    @pytest.mark.asyncio
    async def test_retorna_cuando_estado_es_completed(self) -> None:
        http = _mock_http()
        http.get.return_value = _respuesta_migracion(
            migration_id=42, workflow_state="completed"
        )
        repo = CourseRepository(http)

        with patch("asyncio.sleep"):
            result = await repo.poll_migration(
                course_id=9876,
                migration_id=42,
                poll_interval=0.01,
            )

        assert result.completada is True
        assert result.workflow_state == "completed"

    @pytest.mark.asyncio
    async def test_hace_polling_hasta_completar(self) -> None:
        """Primer polling retorna 'running', segundo retorna 'completed'."""
        http = _mock_http()
        http.get.side_effect = [
            _respuesta_migracion(workflow_state="running"),
            _respuesta_migracion(workflow_state="running"),
            _respuesta_migracion(workflow_state="completed"),
        ]
        repo = CourseRepository(http)

        with patch("asyncio.sleep"):
            result = await repo.poll_migration(
                course_id=9876,
                migration_id=42,
                poll_interval=0.01,
            )

        assert result.completada is True
        assert http.get.call_count == 3

    @pytest.mark.asyncio
    async def test_lanza_error_cuando_estado_es_failed(self) -> None:
        http = _mock_http()
        http.get.return_value = _respuesta_migracion(workflow_state="failed")
        repo = CourseRepository(http)

        with patch("asyncio.sleep"):
            with pytest.raises(MigrationFailedError):
                await repo.poll_migration(
                    course_id=9876,
                    migration_id=42,
                    poll_interval=0.01,
                )

    @pytest.mark.asyncio
    async def test_lanza_timeout_si_nunca_completa(self) -> None:
        http = _mock_http()
        # Siempre retorna "running" — nunca completa
        http.get.return_value = _respuesta_migracion(workflow_state="running")
        repo = CourseRepository(http)

        with patch("asyncio.sleep"):
            with pytest.raises(MigrationTimeoutError):
                await repo.poll_migration(
                    course_id=9876,
                    migration_id=42,
                    # timeout de 0.1s y poll de 0.2s → expira en el primer ciclo
                    timeout_seg=0.1,
                    poll_interval=0.2,
                )

    @pytest.mark.asyncio
    async def test_llama_endpoint_correcto(self) -> None:
        http = _mock_http()
        http.get.return_value = _respuesta_migracion(workflow_state="completed")
        repo = CourseRepository(http)

        with patch("asyncio.sleep"):
            await repo.poll_migration(
                course_id=9876,
                migration_id=42,
                poll_interval=0.01,
            )

        endpoint = http.get.call_args[0][0]
        assert "courses/9876/content_migrations/42" in endpoint


# ──────────────────────────────────────────────────────────────────────────────
# Tests: get_course()
# ──────────────────────────────────────────────────────────────────────────────

class TestGetCourse:

    @pytest.mark.asyncio
    async def test_retorna_course_info_para_curso_existente(self) -> None:
        http = _mock_http()
        http.get.return_value = _respuesta_curso(
            course_id=12345, name="Álgebra Lineal"
        )
        repo = CourseRepository(http)

        info = await repo.get_course(12345)

        assert info.id == 12345
        assert info.name == "Álgebra Lineal"

    @pytest.mark.asyncio
    async def test_lanza_not_found_para_curso_inexistente(self) -> None:
        http = _mock_http()
        http.get.side_effect = CanvasNotFoundError("Course not found")
        repo = CourseRepository(http)

        with pytest.raises(CanvasNotFoundError, match="99999"):
            await repo.get_course(99999)

    @pytest.mark.asyncio
    async def test_llama_endpoint_correcto(self) -> None:
        http = _mock_http()
        http.get.return_value = _respuesta_curso()
        repo = CourseRepository(http)

        await repo.get_course(12345)

        endpoint = http.get.call_args[0][0]
        assert "courses/12345" in endpoint


# ──────────────────────────────────────────────────────────────────────────────
# Tests: list_assignments()
# ──────────────────────────────────────────────────────────────────────────────

class TestListAssignments:

    @pytest.mark.asyncio
    async def test_retorna_lista_de_actividades(self) -> None:
        http = _mock_http()
        http.get_paginated = AsyncMock(return_value=[
            {"id": 1, "name": "Actividad Formativa U1"},
            {"id": 2, "name": "Actividad Sumativa U2"},
        ])
        repo = CourseRepository(http)

        actividades = await repo.list_assignments(9876)

        assert len(actividades) == 2
        assert actividades[0]["name"] == "Actividad Formativa U1"

    @pytest.mark.asyncio
    async def test_usa_paginacion(self) -> None:
        http = _mock_http()
        http.get_paginated = AsyncMock(return_value=[])
        repo = CourseRepository(http)

        await repo.list_assignments(9876)

        http.get_paginated.assert_called_once()
        endpoint = http.get_paginated.call_args[0][0]
        assert "courses/9876/assignments" in endpoint

    @pytest.mark.asyncio
    async def test_retorna_lista_vacia_si_no_hay_actividades(self) -> None:
        http = _mock_http()
        http.get_paginated = AsyncMock(return_value=[])
        repo = CourseRepository(http)

        actividades = await repo.list_assignments(9876)

        assert actividades == []