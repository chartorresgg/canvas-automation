"""
Pruebas unitarias para DeploymentConfig y ProgressEvent.

Estrategia: los value objects son inmutables y su comportamiento
es puramente funcional. No requieren fixtures complejos ni mocks.
Se usan archivos reales (tmp_path) solo donde la validación de rutas
hace necesario que el archivo exista en disco.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.domain.value_objects.deployment_config import (
    CourseOption,
    DeploymentConfig,
)
from app.domain.value_objects.progress_event import (
    EventStatus,
    ProgressEvent,
    STEP_LABELS,
    TOTAL_STEPS,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _zip_real(tmp_path: Path) -> Path:
    """Crea un archivo ZIP vacío real en disco para superar la validación de ruta."""
    import zipfile
    p = tmp_path / "curso.zip"
    with zipfile.ZipFile(p, "w"):
        pass
    return p


def _excel_real(tmp_path: Path) -> Path:
    """Crea un archivo Excel ficticio real en disco."""
    p = tmp_path / "guion.xlsx"
    p.write_bytes(b"PK")  # cabecera mínima
    return p


def _config_new(tmp_path: Path, **kwargs) -> DeploymentConfig:
    """Factory de DeploymentConfig para course_option=NEW."""
    defaults = dict(
        zip_path=_zip_real(tmp_path),
        course_option=CourseOption.NEW,
        course_name="Fundamentos de Ingeniería",
        template_id=12345,
    )
    return DeploymentConfig(**(defaults | kwargs))


def _config_existing(tmp_path: Path, **kwargs) -> DeploymentConfig:
    """Factory de DeploymentConfig para course_option=EXISTING."""
    defaults = dict(
        zip_path=_zip_real(tmp_path),
        course_option=CourseOption.EXISTING,
        course_id=99999,
    )
    return DeploymentConfig(**(defaults | kwargs))


# ══════════════════════════════════════════════════════════════════════════════
# Tests: CourseOption
# ══════════════════════════════════════════════════════════════════════════════

class TestCourseOption:

    def test_valores_string(self) -> None:
        assert CourseOption.NEW.value == "new"
        assert CourseOption.EXISTING.value == "existing"

    def test_es_subclase_de_str(self) -> None:
        assert isinstance(CourseOption.NEW, str)


# ══════════════════════════════════════════════════════════════════════════════
# Tests: DeploymentConfig — construcción válida
# ══════════════════════════════════════════════════════════════════════════════

class TestDeploymentConfigConstruccionValida:

    def test_new_con_campos_minimos(self, tmp_path: Path) -> None:
        config = _config_new(tmp_path)
        assert config.course_option == CourseOption.NEW
        assert config.course_name == "Fundamentos de Ingeniería"
        assert config.template_id == 12345

    def test_existing_con_campos_minimos(self, tmp_path: Path) -> None:
        config = _config_existing(tmp_path)
        assert config.course_option == CourseOption.EXISTING
        assert config.course_id == 99999

    def test_new_con_excel_path(self, tmp_path: Path) -> None:
        excel = _excel_real(tmp_path)
        config = _config_new(tmp_path, excel_path=excel)
        assert config.excel_path == excel

    def test_existing_sin_excel_path(self, tmp_path: Path) -> None:
        config = _config_existing(tmp_path)
        assert config.excel_path is None

    def test_acepta_course_option_como_string(self, tmp_path: Path) -> None:
        """Pydantic debe coercionar el string 'new' al enum CourseOption.NEW."""
        config = DeploymentConfig(
            zip_path=_zip_real(tmp_path),
            course_option="new",
            course_name="Curso Test",
            template_id=1,
        )
        assert config.course_option == CourseOption.NEW


# ══════════════════════════════════════════════════════════════════════════════
# Tests: DeploymentConfig — validaciones de negocio
# ══════════════════════════════════════════════════════════════════════════════

class TestDeploymentConfigValidaciones:

    def test_new_sin_course_name_lanza_error(self, tmp_path: Path) -> None:
        with pytest.raises(ValidationError, match="course_name"):
            DeploymentConfig(
                zip_path=_zip_real(tmp_path),
                course_option=CourseOption.NEW,
                template_id=1,
            )

    def test_new_sin_template_id_lanza_error(self, tmp_path: Path) -> None:
        with pytest.raises(ValidationError, match="template_id"):
            DeploymentConfig(
                zip_path=_zip_real(tmp_path),
                course_option=CourseOption.NEW,
                course_name="Curso Test",
            )

    def test_existing_sin_course_id_lanza_error(self, tmp_path: Path) -> None:
        with pytest.raises(ValidationError, match="course_id"):
            DeploymentConfig(
                zip_path=_zip_real(tmp_path),
                course_option=CourseOption.EXISTING,
            )

    def test_course_name_demasiado_corto_lanza_error(self, tmp_path: Path) -> None:
        with pytest.raises(ValidationError):
            _config_new(tmp_path, course_name="abc")  # menos de 5 chars

    def test_template_id_negativo_lanza_error(self, tmp_path: Path) -> None:
        with pytest.raises(ValidationError):
            _config_new(tmp_path, template_id=-1)

    def test_course_id_cero_lanza_error(self, tmp_path: Path) -> None:
        with pytest.raises(ValidationError):
            _config_existing(tmp_path, course_id=0)

    def test_zip_path_inexistente_lanza_error(self, tmp_path: Path) -> None:
        with pytest.raises(ValidationError, match="ZIP no existe"):
            DeploymentConfig(
                zip_path=tmp_path / "no_existe.zip",
                course_option=CourseOption.NEW,
                course_name="Curso Test",
                template_id=1,
            )

    def test_excel_path_inexistente_lanza_error(self, tmp_path: Path) -> None:
        with pytest.raises(ValidationError, match="Excel no existe"):
            _config_new(tmp_path, excel_path=tmp_path / "no_existe.xlsx")

    def test_es_inmutable(self, tmp_path: Path) -> None:
        config = _config_new(tmp_path)
        with pytest.raises(ValidationError):
            config.course_name = "otro nombre"  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# Tests: DeploymentConfig — propiedades
# ══════════════════════════════════════════════════════════════════════════════

class TestDeploymentConfigPropiedades:

    def test_is_new_course_true_para_new(self, tmp_path: Path) -> None:
        assert _config_new(tmp_path).is_new_course is True

    def test_is_new_course_false_para_existing(self, tmp_path: Path) -> None:
        assert _config_existing(tmp_path).is_new_course is False

    def test_requires_front_page_update_true_con_excel(self, tmp_path: Path) -> None:
        excel = _excel_real(tmp_path)
        config = _config_new(tmp_path, excel_path=excel)
        assert config.requires_front_page_update is True

    def test_requires_front_page_update_false_sin_excel(self, tmp_path: Path) -> None:
        assert _config_new(tmp_path).requires_front_page_update is False

    def test_requires_front_page_update_false_para_existing(
        self, tmp_path: Path
    ) -> None:
        excel = _excel_real(tmp_path)
        config = _config_existing(tmp_path, excel_path=excel)
        assert config.requires_front_page_update is False

    def test_repr_new(self, tmp_path: Path) -> None:
        config = _config_new(tmp_path)
        r = repr(config)
        assert "NEW" in r
        assert "Fundamentos de Ingeniería" in r

    def test_repr_existing(self, tmp_path: Path) -> None:
        config = _config_existing(tmp_path)
        r = repr(config)
        assert "EXISTING" in r
        assert "99999" in r


# ══════════════════════════════════════════════════════════════════════════════
# Tests: EventStatus
# ══════════════════════════════════════════════════════════════════════════════

class TestEventStatus:

    def test_valores_string(self) -> None:
        assert EventStatus.COMPLETED.value == "completed"
        assert EventStatus.FAILED.value == "failed"
        assert EventStatus.CANCELLED.value == "cancelled"

    def test_es_subclase_de_str(self) -> None:
        assert isinstance(EventStatus.RUNNING, str)


# ══════════════════════════════════════════════════════════════════════════════
# Tests: ProgressEvent — construcción válida
# ══════════════════════════════════════════════════════════════════════════════

class TestProgressEventConstruccion:

    def test_construccion_minima(self) -> None:
        event = ProgressEvent(step=0, message="inicio", percentage=0.0)
        assert event.step == 0
        assert event.status == EventStatus.RUNNING
        assert event.course_id is None

    def test_porcentaje_se_redondea_a_un_decimal(self) -> None:
        event = ProgressEvent(step=1, message="x", percentage=33.333333)
        assert event.percentage == 33.3

    def test_step_fuera_de_rango_lanza_error(self) -> None:
        with pytest.raises(ValidationError):
            ProgressEvent(step=6, message="x", percentage=100.0)

    def test_step_negativo_lanza_error(self) -> None:
        with pytest.raises(ValidationError):
            ProgressEvent(step=-1, message="x", percentage=0.0)

    def test_porcentaje_mayor_100_lanza_error(self) -> None:
        with pytest.raises(ValidationError):
            ProgressEvent(step=1, message="x", percentage=100.1)

    def test_porcentaje_negativo_lanza_error(self) -> None:
        with pytest.raises(ValidationError):
            ProgressEvent(step=1, message="x", percentage=-0.1)

    def test_message_vacio_lanza_error(self) -> None:
        with pytest.raises(ValidationError):
            ProgressEvent(step=0, message="", percentage=0.0)

    def test_es_inmutable(self) -> None:
        event = ProgressEvent(step=0, message="inicio", percentage=0.0)
        with pytest.raises(ValidationError):
            event.step = 1  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# Tests: ProgressEvent — constructores de fábrica
# ══════════════════════════════════════════════════════════════════════════════

class TestProgressEventFactories:

    def test_iniciando(self) -> None:
        e = ProgressEvent.iniciando()
        assert e.step == 0
        assert e.percentage == 0.0
        assert e.status == EventStatus.PENDING

    def test_curso_listo(self) -> None:
        e = ProgressEvent.curso_listo(course_id=1234)
        assert e.step == 1
        assert e.percentage == 20.0
        assert e.course_id == 1234
        assert e.status == EventStatus.RUNNING

    def test_zip_procesado(self) -> None:
        e = ProgressEvent.zip_procesado(course_id=1, cambios=7)
        assert e.step == 2
        assert e.percentage == 35.0
        assert "7" in e.detail

    def test_subiendo_archivo_escala_porcentaje(self) -> None:
        inicio = ProgressEvent.subiendo_archivo(course_id=1, actual=1,  total=10)
        medio  = ProgressEvent.subiendo_archivo(course_id=1, actual=5,  total=10)
        fin    = ProgressEvent.subiendo_archivo(course_id=1, actual=10, total=10)
        assert inicio.percentage == pytest.approx(38.0, abs=0.5)
        assert medio.percentage  == pytest.approx(50.0, abs=0.5)
        assert fin.percentage    == pytest.approx(65.0, abs=0.1)

    def test_subiendo_archivo_total_cero_no_divide_por_cero(self) -> None:
        e = ProgressEvent.subiendo_archivo(course_id=1, actual=0, total=0)
        assert e.percentage == pytest.approx(65.0, abs=0.1)

    def test_archivos_subidos(self) -> None:
        e = ProgressEvent.archivos_subidos(course_id=1, total=47)
        assert e.step == 3
        assert e.percentage == 65.0
        assert "47" in e.detail

    def test_paginas_actualizadas(self) -> None:
        e = ProgressEvent.paginas_actualizadas(course_id=1)
        assert e.step == 4
        assert e.percentage == 85.0

    def test_completado(self) -> None:
        e = ProgressEvent.completado(course_id=9876)
        assert e.step == TOTAL_STEPS
        assert e.percentage == 100.0
        assert e.status == EventStatus.COMPLETED
        assert e.course_id == 9876

    def test_fallido(self) -> None:
        e = ProgressEvent.fallido(step=2, message="Error ZIP", error="Archivo corrupto")
        assert e.status == EventStatus.FAILED
        assert e.error == "Archivo corrupto"
        assert e.step == 2

    def test_cancelado(self) -> None:
        e = ProgressEvent.cancelado(step=3)
        assert e.status == EventStatus.CANCELLED
        assert e.percentage == pytest.approx(60.0, abs=0.1)


# ══════════════════════════════════════════════════════════════════════════════
# Tests: ProgressEvent — propiedades
# ══════════════════════════════════════════════════════════════════════════════

class TestProgressEventPropiedades:

    def test_is_terminal_completed(self) -> None:
        assert ProgressEvent.completado(course_id=1).is_terminal is True

    def test_is_terminal_failed(self) -> None:
        assert ProgressEvent.fallido(1, "x", "err").is_terminal is True

    def test_is_terminal_cancelled(self) -> None:
        assert ProgressEvent.cancelado(1).is_terminal is True

    def test_is_terminal_running(self) -> None:
        e = ProgressEvent(step=2, message="x", percentage=35.0)
        assert e.is_terminal is False

    def test_progress_fraction(self) -> None:
        e = ProgressEvent.paginas_actualizadas(course_id=1)
        assert e.progress_fraction == pytest.approx(0.85)

    def test_step_label_retorna_nombre_legible(self) -> None:
        e = ProgressEvent.curso_listo(course_id=1)
        assert e.step_label == STEP_LABELS[1]

    def test_step_label_paso_desconocido(self) -> None:
        # model_construct omite la validación para poder usar step=99 (fuera del rango normal)
        # y así ejercer el fallback f"Paso {self.step}" de step_label.
        e = ProgressEvent.model_construct(
            step=99, message="x", percentage=0.0,
            status=EventStatus.RUNNING, total_steps=5,
        )
        assert "99" in e.step_label

    def test_to_sse_data_formato_correcto(self) -> None:
        e = ProgressEvent.iniciando()
        sse = e.to_sse_data()
        assert sse.startswith("data: {")
        assert sse.endswith("\n\n")
        assert '"step":0' in sse

    def test_to_sse_data_incluye_status(self) -> None:
        e = ProgressEvent.completado(course_id=1)
        sse = e.to_sse_data()
        assert "completed" in sse

    def test_to_sse_data_incluye_course_id(self) -> None:
        e = ProgressEvent.completado(course_id=9876)
        sse = e.to_sse_data()
        assert "9876" in sse


# ══════════════════════════════════════════════════════════════════════════════
# Tests: STEP_LABELS y TOTAL_STEPS — constantes
# ══════════════════════════════════════════════════════════════════════════════

class TestConstantes:

    def test_total_steps_es_cinco(self) -> None:
        assert TOTAL_STEPS == 5

    def test_step_labels_tiene_entrada_para_cada_paso(self) -> None:
        for paso in range(TOTAL_STEPS + 1):
            assert paso in STEP_LABELS

    def test_step_labels_valores_no_vacios(self) -> None:
        for label in STEP_LABELS.values():
            assert len(label) > 0