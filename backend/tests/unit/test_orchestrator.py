"""
Pruebas unitarias para DeploymentOrchestrator.

Estrategia: mock de todos los colaboradores para aislar la lógica
de coordinación del orquestador de las dependencias externas.
Los tests verifican el orden de los ProgressEvents y que cada
colaborador es invocado correctamente.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.orchestrator import DeploymentOrchestrator
from app.domain.services.interactive_content_detector import (
    InteractiveContentDetector,
)
from app.domain.value_objects.deployment_config import CourseOption, DeploymentConfig
from app.domain.value_objects.progress_event import EventStatus, ProgressEvent
from app.infrastructure.canvas.course_repository import (
    CourseInfo,
    CourseRepository,
    MigrationResult,
)
from app.infrastructure.canvas.file_repository import FileRepository, UploadSummary
from app.infrastructure.canvas.page_repository import PageRepository
from app.infrastructure.composers.page_composer_factory import PageComposerFactory


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _zip_real(tmp_path: Path) -> Path:
    """Crea un ZIP mínimo válido con estructura correcta."""
    zip_path = tmp_path / "curso.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("1. Archivos/1. Presentación/index.html", "<html>p</html>")
        zf.writestr(
            "1. Archivos/2. Material fundamental/U1_Lectura_Fundamental.pdf",
            b"pdf",
        )
        zf.writestr(
            "1. Archivos/2. Material fundamental/U1_Actividad_Formativa.pdf",
            b"pdf",
        )
    return zip_path


def _info_curso(course_id: int = 9876) -> CourseInfo:
    return CourseInfo(
        id=course_id,
        name="Curso Test",
        course_code="TEST",
        workflow_state="available",
        url=f"https://poli.instructure.com/courses/{course_id}",
    )


def _summary_exitoso(files_map: dict[str, int] | None = None) -> UploadSummary:
    return UploadSummary(
        exitosos=files_map or {
            "1. Presentación/index.html":                         101,
            "2. Material fundamental/U1_Lectura_Fundamental.pdf": 102,
            "2. Material fundamental/U1_Actividad_Formativa.pdf": 103,
        },
        fallidos=[],
    )


def _mock_course_repo() -> MagicMock:
    mock = MagicMock(spec=CourseRepository)
    mock.create_course = AsyncMock(return_value=_info_curso())
    mock.copy_template = AsyncMock(
        return_value=MigrationResult(42, 9876, "running", False)
    )
    mock.poll_migration = AsyncMock(return_value=None)
    mock.get_course      = AsyncMock(return_value=_info_curso())
    mock.list_assignments = AsyncMock(return_value=[])
    return mock


def _mock_file_repo() -> MagicMock:
    mock = MagicMock(spec=FileRepository)
    mock.upload_all = AsyncMock(return_value=_summary_exitoso())
    return mock


def _mock_page_repo() -> MagicMock:
    mock = MagicMock(spec=PageRepository)
    mock.update_page = AsyncMock(
        return_value=MagicMock(url="test", title="Test", course_id=9876, edit_url="")
    )
    mock.update_or_create_page = AsyncMock(
        return_value=MagicMock(url="test", title="Test", course_id=9876, edit_url="")
    )
    mock.link_pdfs_bulk = AsyncMock(return_value=[])
    return mock


def _mock_detector() -> MagicMock:
    mock = MagicMock(spec=InteractiveContentDetector)
    mock.detect.return_value = {}
    return mock


def _mock_factory() -> MagicMock:
    mock = MagicMock(spec=PageComposerFactory)
    composer_mock = MagicMock()
    composer_mock.compose.return_value = "<p>html</p>"
    mock.create.return_value = composer_mock
    return mock


def _crear_orchestrator(
    tmp_path: Path,
    course_repo=None,
    file_repo=None,
    page_repo=None,
    detector=None,
    factory=None,
) -> DeploymentOrchestrator:
    return DeploymentOrchestrator(
        course_repo=course_repo or _mock_course_repo(),
        file_repo=file_repo   or _mock_file_repo(),
        page_repo=page_repo   or _mock_page_repo(),
        detector=detector     or _mock_detector(),
        factory=factory       or _mock_factory(),
        tmp_dir=tmp_path,
    )


def _config_new(zip_path: Path) -> DeploymentConfig:
    return DeploymentConfig(
        zip_path=zip_path,
        course_option=CourseOption.NEW,
        course_name="Curso de Test",
        template_id=99001,
    )


def _config_existing(zip_path: Path) -> DeploymentConfig:
    return DeploymentConfig(
        zip_path=zip_path,
        course_option=CourseOption.EXISTING,
        course_id=12345,
    )


async def _collect_events(
    orchestrator: DeploymentOrchestrator,
    config: DeploymentConfig,
) -> list[ProgressEvent]:
    """Recolecta todos los ProgressEvents del generator en una lista."""
    eventos = []
    async for event in orchestrator.deploy(config):
        eventos.append(event)
    return eventos


# ──────────────────────────────────────────────────────────────────────────────
# Tests: InteractiveContentDetector
# ──────────────────────────────────────────────────────────────────────────────

class TestInteractiveContentDetector:

    def test_detecta_story_html_en_material_fundamental(self) -> None:
        detector = InteractiveContentDetector()
        files_map = {
            "2. Material fundamental/MF_U1/story.html":           111,
            "2. Material fundamental/U1_Lectura_Fundamental.pdf": 112,
        }
        resultado = detector.detect(files_map)
        assert 1 in resultado
        assert resultado[1][0]["file_id"] == 111

    def test_ignora_story_html_fuera_de_material_fundamental(self) -> None:
        detector = InteractiveContentDetector()
        files_map = {
            "1. Presentación/story.html": 999,
        }
        resultado = detector.detect(files_map)
        assert resultado == {}

    def test_detecta_multiples_unidades(self) -> None:
        detector = InteractiveContentDetector()
        files_map = {
            "2. Material fundamental/MF_U1/story.html": 101,
            "2. Material fundamental/MF_U2/story.html": 202,
            "2. Material fundamental/MF_U3/story.html": 303,
        }
        resultado = detector.detect(files_map)
        assert 1 in resultado
        assert 2 in resultado
        assert 3 in resultado

    def test_detecta_multiples_contenidos_misma_unidad(self) -> None:
        detector = InteractiveContentDetector()
        files_map = {
            "2. Material fundamental/MF_U1_1/story.html": 111,
            "2. Material fundamental/MF_U1_2/story.html": 112,
        }
        resultado = detector.detect(files_map)
        assert len(resultado[1]) == 2

    def test_retorna_dict_vacio_sin_scorm(self) -> None:
        detector = InteractiveContentDetector()
        files_map = {
            "2. Material fundamental/U1_Lectura.pdf": 1,
            "1. Presentación/index.html":             2,
        }
        resultado = detector.detect(files_map)
        assert resultado == {}

    def test_ordena_por_numero_de_contenido(self) -> None:
        detector = InteractiveContentDetector()
        files_map = {
            "2. Material fundamental/MF_U1_3/story.html": 103,
            "2. Material fundamental/MF_U1_1/story.html": 101,
            "2. Material fundamental/MF_U1_2/story.html": 102,
        }
        resultado = detector.detect(files_map)
        numeros = [c["numero"] for c in resultado[1]]
        assert numeros == [1, 2, 3]

    @pytest.mark.parametrize("carpeta,unidad_esperada,numero_esperado", [
    ("MF_U1",         1, 1),
    ("MF_U2_3",       2, 3),
    ("U1_Material fundamental",   1, 1),
    ("U3_Material_fundamental_2", 3, 2),
    ("U4_MF2",        4, 2),
    ("U1_MF_1",       1, 1),   # ← nuevo
    ("U1_MF_2",       1, 2),   # ← nuevo
    ("U4_MF_2",       4, 2),   # ← nuevo
])
    def test_parsear_carpeta(
        self, carpeta: str, unidad_esperada: int, numero_esperado: int
    ) -> None:
        resultado = InteractiveContentDetector._parsear_carpeta(carpeta)
        assert resultado is not None
        unidad, numero, _ = resultado
        assert unidad == unidad_esperada
        assert numero == numero_esperado

    def test_parsear_carpeta_invalida_retorna_none(self) -> None:
        resultado = InteractiveContentDetector._parsear_carpeta(
            "carpeta_sin_patron"
        )
        assert resultado is None


# ──────────────────────────────────────────────────────────────────────────────
# Tests: DeploymentOrchestrator — flujo principal
# ──────────────────────────────────────────────────────────────────────────────

class TestDeploymentOrchestratorFlujo:

    @pytest.mark.asyncio
    async def test_primer_evento_es_iniciando(self, tmp_path: Path) -> None:
        zip_path = _zip_real(tmp_path)
        orc = _crear_orchestrator(tmp_path)
        eventos = await _collect_events(orc, _config_new(zip_path))

        assert len(eventos) > 0
        assert eventos[0].status == EventStatus.PENDING
        assert eventos[0].step == 0

    @pytest.mark.asyncio
    async def test_ultimo_evento_es_completado(self, tmp_path: Path) -> None:
        zip_path = _zip_real(tmp_path)
        orc = _crear_orchestrator(tmp_path)
        eventos = await _collect_events(orc, _config_new(zip_path))

        assert eventos[-1].status == EventStatus.COMPLETED
        assert eventos[-1].percentage == 100.0

    @pytest.mark.asyncio
    async def test_eventos_en_orden_de_porcentaje(self, tmp_path: Path) -> None:
        zip_path = _zip_real(tmp_path)
        orc = _crear_orchestrator(tmp_path)
        eventos = await _collect_events(orc, _config_new(zip_path))

        # Los eventos principales deben ir de menor a mayor porcentaje
        eventos_principales = [e for e in eventos if e.status != EventStatus.RUNNING
                               or e.step in [0, 1, 2, 3, 4, 5]]
        for i in range(len(eventos_principales) - 1):
            assert (
                eventos_principales[i].percentage
                <= eventos_principales[i + 1].percentage
            ), (
                f"Evento {i} ({eventos_principales[i].percentage}%) "
                f"mayor que evento {i+1} ({eventos_principales[i+1].percentage}%)"
            )

    @pytest.mark.asyncio
    async def test_ultimo_evento_tiene_course_id(self, tmp_path: Path) -> None:
        zip_path = _zip_real(tmp_path)
        orc = _crear_orchestrator(tmp_path)
        eventos = await _collect_events(orc, _config_new(zip_path))

        assert eventos[-1].course_id == 9876

    @pytest.mark.asyncio
    async def test_total_minimo_de_eventos(self, tmp_path: Path) -> None:
        """Debe haber al menos: iniciando, curso_listo, zip, archivos, páginas, completado."""
        zip_path = _zip_real(tmp_path)
        orc = _crear_orchestrator(tmp_path)
        eventos = await _collect_events(orc, _config_new(zip_path))

        assert len(eventos) >= 5


# ──────────────────────────────────────────────────────────────────────────────
# Tests: DeploymentOrchestrator — curso nuevo vs existente
# ──────────────────────────────────────────────────────────────────────────────

class TestSetupCurso:

    @pytest.mark.asyncio
    async def test_curso_nuevo_llama_create_course(
        self, tmp_path: Path
    ) -> None:
        zip_path    = _zip_real(tmp_path)
        course_repo = _mock_course_repo()
        orc = _crear_orchestrator(tmp_path, course_repo=course_repo)

        await _collect_events(orc, _config_new(zip_path))

        course_repo.create_course.assert_called_once_with("Curso de Test")

    @pytest.mark.asyncio
    async def test_curso_nuevo_llama_copy_template(
        self, tmp_path: Path
    ) -> None:
        zip_path    = _zip_real(tmp_path)
        course_repo = _mock_course_repo()
        orc = _crear_orchestrator(tmp_path, course_repo=course_repo)

        await _collect_events(orc, _config_new(zip_path))

        course_repo.copy_template.assert_called_once_with(
            src_id=99001, dst_id=9876
        )

    @pytest.mark.asyncio
    async def test_curso_nuevo_llama_poll_migration(
        self, tmp_path: Path
    ) -> None:
        zip_path    = _zip_real(tmp_path)
        course_repo = _mock_course_repo()
        orc = _crear_orchestrator(tmp_path, course_repo=course_repo)

        await _collect_events(orc, _config_new(zip_path))

        course_repo.poll_migration.assert_called_once()

    @pytest.mark.asyncio
    async def test_curso_existente_llama_get_course(
        self, tmp_path: Path
    ) -> None:
        zip_path    = _zip_real(tmp_path)
        course_repo = _mock_course_repo()
        orc = _crear_orchestrator(tmp_path, course_repo=course_repo)

        await _collect_events(orc, _config_existing(zip_path))

        course_repo.get_course.assert_called_once_with(12345)

    @pytest.mark.asyncio
    async def test_curso_existente_no_llama_create_course(
        self, tmp_path: Path
    ) -> None:
        zip_path    = _zip_real(tmp_path)
        course_repo = _mock_course_repo()
        orc = _crear_orchestrator(tmp_path, course_repo=course_repo)

        await _collect_events(orc, _config_existing(zip_path))

        course_repo.create_course.assert_not_called()


# ──────────────────────────────────────────────────────────────────────────────
# Tests: DeploymentOrchestrator — subida de archivos
# ──────────────────────────────────────────────────────────────────────────────

class TestSubidaArchivos:

    @pytest.mark.asyncio
    async def test_llama_upload_all(self, tmp_path: Path) -> None:
        zip_path  = _zip_real(tmp_path)
        file_repo = _mock_file_repo()
        orc = _crear_orchestrator(tmp_path, file_repo=file_repo)

        await _collect_events(orc, _config_new(zip_path))

        file_repo.upload_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_all_recibe_course_id_correcto(
        self, tmp_path: Path
    ) -> None:
        zip_path  = _zip_real(tmp_path)
        file_repo = _mock_file_repo()
        orc = _crear_orchestrator(tmp_path, file_repo=file_repo)

        await _collect_events(orc, _config_new(zip_path))

        args = file_repo.upload_all.call_args
        assert args[0][0] == 9876  # course_id

    @pytest.mark.asyncio
    async def test_evento_archivos_subidos_refleja_total(
        self, tmp_path: Path
    ) -> None:
        zip_path  = _zip_real(tmp_path)
        file_repo = _mock_file_repo()
        file_repo.upload_all.return_value = UploadSummary(
            exitosos={"a.pdf": 1, "b.pdf": 2, "c.pdf": 3},
            fallidos=[],
        )
        orc = _crear_orchestrator(tmp_path, file_repo=file_repo)

        eventos = await _collect_events(orc, _config_new(zip_path))

        evento_archivos = next(
            (e for e in eventos if e.step == 3 and "3" in (e.detail or "")),
            None,
        )
        if evento_archivos:
            assert "3" in (evento_archivos.detail or "")


# ──────────────────────────────────────────────────────────────────────────────
# Tests: DeploymentOrchestrator — actualización de páginas
# ──────────────────────────────────────────────────────────────────────────────

class TestActualizacionPaginas:

    @pytest.mark.asyncio
    async def test_llama_update_page_para_presentacion(
        self, tmp_path: Path
    ) -> None:
        zip_path  = _zip_real(tmp_path)
        page_repo = _mock_page_repo()
        file_repo = _mock_file_repo()
        file_repo.upload_all.return_value = UploadSummary(
            exitosos={
                "1. Presentación/index.html":                         101,
                "2. Material fundamental/U1_Lectura_Fundamental.pdf": 102,
            },
            fallidos=[],
        )
        orc = _crear_orchestrator(
            tmp_path, file_repo=file_repo, page_repo=page_repo
        )

        await _collect_events(orc, _config_new(zip_path))

        slugs_actualizados = [
            call[0][1]  # segundo arg posicional = page_slug
            for call in page_repo.update_page.call_args_list
        ]
        assert "inicio-presentacion" in slugs_actualizados

    @pytest.mark.asyncio
    async def test_llama_update_page_para_material_fundamental(
        self, tmp_path: Path
    ) -> None:
        zip_path  = _zip_real(tmp_path)
        page_repo = _mock_page_repo()
        orc = _crear_orchestrator(tmp_path, page_repo=page_repo)

        await _collect_events(orc, _config_new(zip_path))

        slugs = [
            call[0][1]
            for call in page_repo.update_page.call_args_list
        ]
        assert any("material-fundamental" in s for s in slugs)

    @pytest.mark.asyncio
    async def test_usa_factory_para_crear_composers(
        self, tmp_path: Path
    ) -> None:
        zip_path = _zip_real(tmp_path)
        factory  = _mock_factory()
        orc = _crear_orchestrator(tmp_path, factory=factory)

        await _collect_events(orc, _config_new(zip_path))

        assert factory.create.call_count >= 1


# ──────────────────────────────────────────────────────────────────────────────
# Tests: DeploymentOrchestrator — manejo de errores
# ──────────────────────────────────────────────────────────────────────────────

class TestManejoErrores:

    @pytest.mark.asyncio
    async def test_error_en_create_course_emite_evento_failed(
        self, tmp_path: Path
    ) -> None:
        zip_path    = _zip_real(tmp_path)
        course_repo = _mock_course_repo()
        course_repo.create_course.side_effect = Exception(
            "Error de Canvas"
        )
        orc = _crear_orchestrator(tmp_path, course_repo=course_repo)

        eventos = await _collect_events(orc, _config_new(zip_path))

        assert eventos[-1].status == EventStatus.FAILED

    @pytest.mark.asyncio
    async def test_error_en_upload_emite_evento_failed(
        self, tmp_path: Path
    ) -> None:
        zip_path  = _zip_real(tmp_path)
        file_repo = _mock_file_repo()
        file_repo.upload_all.side_effect = Exception("Error de subida")
        orc = _crear_orchestrator(tmp_path, file_repo=file_repo)

        eventos = await _collect_events(orc, _config_new(zip_path))

        assert eventos[-1].status == EventStatus.FAILED
        assert "Error de subida" in (eventos[-1].error or "")

    @pytest.mark.asyncio
    async def test_evento_failed_contiene_numero_de_paso(
        self, tmp_path: Path
    ) -> None:
        zip_path    = _zip_real(tmp_path)
        course_repo = _mock_course_repo()
        course_repo.create_course.side_effect = Exception("Fallo paso 1")
        orc = _crear_orchestrator(tmp_path, course_repo=course_repo)

        eventos = await _collect_events(orc, _config_new(zip_path))

        evento_fallido = eventos[-1]
        assert evento_fallido.status == EventStatus.FAILED
        assert evento_fallido.step == 1  # falló en paso 1

    @pytest.mark.asyncio
    async def test_cleanup_se_llama_siempre_incluso_en_error(
        self, tmp_path: Path
    ) -> None:
        """ZipProcessor.cleanup() debe ejecutarse aunque falle el proceso."""
        zip_path    = _zip_real(tmp_path)
        course_repo = _mock_course_repo()
        course_repo.create_course.side_effect = Exception("Error")
        orc = _crear_orchestrator(tmp_path, course_repo=course_repo)

        with patch(
            "app.application.orchestrator.ZipProcessor.cleanup"
        ) as mock_cleanup:
            await _collect_events(orc, _config_new(zip_path))
            mock_cleanup.assert_called_once()


# ──────────────────────────────────────────────────────────────────────────────
# Tests: helpers privados del orquestador
# ──────────────────────────────────────────────────────────────────────────────

class TestHelpersPrivados:

    def test_extraer_secuencia_sin_numero_retorna_1(self) -> None:
        seq = DeploymentOrchestrator._extraer_secuencia(
            "U1_Lectura_Fundamental.pdf"
        )
        assert seq == 1

    def test_extraer_secuencia_con_numero_2(self) -> None:
        seq = DeploymentOrchestrator._extraer_secuencia(
            "U1_Lectura_Fundamental_2.pdf"
        )
        assert seq == 2

    def test_buscar_complemento_existente(self) -> None:
        files_map = {
            "4. Complementos/U1_Complemento.pdf": 111,
            "4. Complementos/U2_Complemento.pdf": 222,
        }
        result = DeploymentOrchestrator._buscar_complemento(1, files_map)
        assert result == 111

    def test_buscar_complemento_inexistente_retorna_none(self) -> None:
        files_map = {"4. Complementos/U2_Complemento.pdf": 222}
        result = DeploymentOrchestrator._buscar_complemento(1, files_map)
        assert result is None

    def test_buscar_complemento_ignora_otras_carpetas(self) -> None:
        files_map = {
            "2. Material fundamental/U1_Lectura.pdf": 999,
        }
        result = DeploymentOrchestrator._buscar_complemento(1, files_map)
        assert result is None