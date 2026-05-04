"""
Value Object que representa el estado puntual de progreso de un despliegue.

Es el objeto que DeploymentOrchestrator emite en cada etapa significativa
y que FastAPI serializa como evento SSE hacia el frontend React.

Capa: Dominio — value_objects
Dependencias: Pydantic v2
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ──────────────────────────────────────────────────────────────────────────────
# Enumeraciones de dominio
# ──────────────────────────────────────────────────────────────────────────────

class EventStatus(str, Enum):
    """
    Estado del proceso de despliegue en un momento dado.

    PENDING   — La tarea fue aceptada pero aún no ha comenzado.
    RUNNING   — El proceso está en ejecución activa.
    COMPLETED — Todos los pasos finalizaron exitosamente.
    FAILED    — El proceso terminó con un error irrecuperable.
    CANCELLED — El analista canceló el proceso manualmente.
    """
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"
    CANCELLED = "cancelled"


# ──────────────────────────────────────────────────────────────────────────────
# Nombres legibles de cada paso del despliegue
# ──────────────────────────────────────────────────────────────────────────────

STEP_LABELS: dict[int, str] = {
    0: "Iniciando proceso",
    1: "Creando curso en Canvas",
    2: "Procesando archivo ZIP",
    3: "Subiendo archivos al aula",
    4: "Actualizando páginas del curso",
    5: "Vinculando PDFs a actividades",
}

TOTAL_STEPS: int = len(STEP_LABELS) - 1  # 5 pasos reales (0 es el inicio)


# ──────────────────────────────────────────────────────────────────────────────
# Value Object principal
# ──────────────────────────────────────────────────────────────────────────────

class ProgressEvent(BaseModel):
    """
    Snapshot inmutable del estado de progreso en un instante del despliegue.

    El orquestador hace `yield ProgressEvent(...)` en cada etapa.
    El router SSE lo serializa con `.model_dump_json()` y lo envía
    al frontend como `data: {...}\\n\\n`.

    Atributos:
        step:        Número del paso actual (0 = inicio, 5 = último).
        total_steps: Total de pasos (siempre 5 para este sistema).
        message:     Mensaje descriptivo legible para el analista.
        percentage:  Porcentaje de avance (0.0 – 100.0).
        status:      Estado del proceso en este momento.
        detail:      Información adicional opcional (ej. "archivo 12/47").
        course_id:   ID del curso Canvas, disponible desde el paso 1.
        error:       Descripción del error si status=FAILED.
    """

    model_config = ConfigDict(frozen=True, use_enum_values=False)

    step: int = Field(
        ge=0,
        le=TOTAL_STEPS,
        description=f"Paso actual (0 a {TOTAL_STEPS}).",
    )
    total_steps: int = Field(
        default=TOTAL_STEPS,
        description="Total de pasos del proceso.",
    )
    message: str = Field(
        min_length=1,
        max_length=500,
        description="Mensaje descriptivo del estado actual.",
    )
    percentage: float = Field(
        ge=0.0,
        le=100.0,
        description="Porcentaje de avance del proceso (0.0 – 100.0).",
    )
    status: EventStatus = Field(
        default=EventStatus.RUNNING,
        description="Estado del proceso en este momento.",
    )
    detail: str | None = Field(
        default=None,
        max_length=500,
        description="Información adicional (ej. progreso de subida de archivos).",
    )
    course_id: int | None = Field(
        default=None,
        gt=0,
        description="ID del curso Canvas. Disponible desde el paso 1.",
    )
    error: str | None = Field(
        default=None,
        max_length=1000,
        description="Descripción del error. Solo presente si status=FAILED.",
    )

    # ──────────────────────────────────────────────────────────────
    # Validaciones de campo
    # ──────────────────────────────────────────────────────────────

    @field_validator("percentage")
    @classmethod
    def redondear_porcentaje(cls, v: float) -> float:
        """Garantiza que el porcentaje tenga exactamente un decimal."""
        return round(v, 1)

    # ──────────────────────────────────────────────────────────────
    # Constructores de fábrica (métodos de clase)
    # Los constructores de fábrica centralizan la lógica de creación
    # de eventos típicos del proceso. El orquestador los usa en lugar
    # de construir ProgressEvent directamente, lo que hace el código
    # del orquestador más legible y evita porcentajes hardcodeados.
    # ──────────────────────────────────────────────────────────────

    @classmethod
    def iniciando(cls) -> ProgressEvent:
        """Evento inicial al comenzar el proceso."""
        return cls(
            step=0,
            message=STEP_LABELS[0],
            percentage=0.0,
            status=EventStatus.PENDING,
        )

    @classmethod
    def curso_listo(cls, course_id: int) -> ProgressEvent:
        """Paso 1 completado: curso creado o verificado en Canvas."""
        return cls(
            step=1,
            message=STEP_LABELS[1],
            percentage=20.0,
            status=EventStatus.RUNNING,
            course_id=course_id,
        )

    @classmethod
    def zip_procesado(cls, course_id: int, cambios: int) -> ProgressEvent:
        """Paso 2 completado: ZIP extraído y normalizado."""
        return cls(
            step=2,
            message=STEP_LABELS[2],
            percentage=35.0,
            status=EventStatus.RUNNING,
            course_id=course_id,
            detail=f"{cambios} elemento(s) normalizados en el ZIP.",
        )

    @classmethod
    def subiendo_archivo(
        cls, course_id: int, actual: int, total: int
    ) -> ProgressEvent:
        """
        Progreso durante la subida de archivos (paso 3).
        El porcentaje escala dinámicamente entre 35% y 65%.
        """
        fraccion = actual / total if total > 0 else 1.0
        porcentaje = 35.0 + (fraccion * 30.0)  # rango [35, 65]
        return cls(
            step=3,
            message=STEP_LABELS[3],
            percentage=porcentaje,
            status=EventStatus.RUNNING,
            course_id=course_id,
            detail=f"Archivo {actual} de {total}.",
        )

    @classmethod
    def archivos_subidos(cls, course_id: int, total: int) -> ProgressEvent:
        """Paso 3 completado: todos los archivos subidos a Canvas."""
        return cls(
            step=3,
            message=STEP_LABELS[3],
            percentage=65.0,
            status=EventStatus.RUNNING,
            course_id=course_id,
            detail=f"{total} archivo(s) subidos exitosamente.",
        )

    @classmethod
    def paginas_actualizadas(cls, course_id: int) -> ProgressEvent:
        """Paso 4 completado: páginas HTML actualizadas en Canvas."""
        return cls(
            step=4,
            message=STEP_LABELS[4],
            percentage=85.0,
            status=EventStatus.RUNNING,
            course_id=course_id,
        )

    @classmethod
    def completado(cls, course_id: int) -> ProgressEvent:
        """Proceso finalizado exitosamente."""
        return cls(
            step=TOTAL_STEPS,
            message="¡Aula virtual desplegada exitosamente!",
            percentage=100.0,
            status=EventStatus.COMPLETED,
            course_id=course_id,
        )

    @classmethod
    def fallido(cls, step: int, message: str, error: str) -> ProgressEvent:
        """Proceso terminado con error irrecuperable."""
        porcentaje = (step / TOTAL_STEPS) * 100.0
        return cls(
            step=step,
            message=message,
            percentage=porcentaje,
            status=EventStatus.FAILED,
            error=error,
        )

    @classmethod
    def cancelado(cls, step: int) -> ProgressEvent:
        """Proceso cancelado por el analista."""
        porcentaje = (step / TOTAL_STEPS) * 100.0
        return cls(
            step=step,
            message="Despliegue cancelado por el usuario.",
            percentage=porcentaje,
            status=EventStatus.CANCELLED,
        )

    # ──────────────────────────────────────────────────────────────
    # Propiedades de conveniencia
    # ──────────────────────────────────────────────────────────────

    @property
    def step_label(self) -> str:
        """Nombre legible del paso actual según STEP_LABELS."""
        return STEP_LABELS.get(self.step, f"Paso {self.step}")

    @property
    def is_terminal(self) -> bool:
        """
        True si el evento es terminal: el proceso no emitirá más eventos.
        El router SSE usa esta propiedad para cerrar la conexión.
        """
        return self.status in {
            EventStatus.COMPLETED,
            EventStatus.FAILED,
            EventStatus.CANCELLED,
        }

    @property
    def progress_fraction(self) -> float:
        """Porcentaje expresado como fracción (0.0 – 1.0) para barras de progreso."""
        return self.percentage / 100.0

    def to_sse_data(self) -> str:
        """
        Serializa el evento al formato SSE listo para ser enviado por FastAPI.

        Formato: 'data: {json}\\n\\n'

        El router hace:
            yield event.to_sse_data()
        """
        return f"data: {self.model_dump_json()}\n\n"