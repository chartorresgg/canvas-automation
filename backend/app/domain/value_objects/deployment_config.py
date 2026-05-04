"""
Value Object que encapsula la configuración de entrada para un despliegue.

Representa el contrato entre la capa de Presentación (FastAPI router)
y la capa de Aplicación (DeploymentOrchestrator). Inmutable por diseño:
una vez construido y validado, ningún colaborador puede modificarlo.

Capa: Dominio — value_objects
Dependencias: Pydantic v2 (validación en la frontera del sistema)
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ──────────────────────────────────────────────────────────────────────────────
# Enumeraciones de dominio
# ──────────────────────────────────────────────────────────────────────────────

class CourseOption(str, Enum):
    """
    Modo de operación del despliegue respecto al curso Canvas destino.

    NEW      — Se crea un curso nuevo duplicando una plantilla Canvas.
    EXISTING — Se usa un curso ya existente; solo se sube contenido.
    """
    NEW      = "new"
    EXISTING = "existing"


# ──────────────────────────────────────────────────────────────────────────────
# Value Object principal
# ──────────────────────────────────────────────────────────────────────────────

class DeploymentConfig(BaseModel):
    """
    Configuración inmutable y validada de un despliegue de aula virtual.

    Reglas de validación cruzada (model_validator):
        - Si course_option = NEW:      course_name y template_id son obligatorios.
        - Si course_option = EXISTING: course_id es obligatorio.

    Atributos:
        zip_path:      Ruta al archivo ZIP con los materiales del aula.
        course_option: Modo de operación (NEW o EXISTING).
        course_name:   Nombre del nuevo curso en Canvas (solo para NEW).
        template_id:   ID del curso Canvas usado como plantilla (solo para NEW).
        course_id:     ID del curso Canvas existente (solo para EXISTING).
        excel_path:    Ruta al Excel con datos del front del curso (opcional).
    """

    model_config = ConfigDict(frozen=True, use_enum_values=False)

    zip_path: Path = Field(
        description="Ruta absoluta al archivo ZIP ya almacenado en el servidor."
    )
    course_option: CourseOption = Field(
        description="Indica si se crea un curso nuevo o se usa uno existente."
    )
    course_name: str | None = Field(
        default=None,
        min_length=5,
        max_length=255,
        description="Nombre oficial del nuevo curso. Obligatorio si course_option=NEW.",
    )
    template_id: int | None = Field(
        default=None,
        gt=0,
        description="ID Canvas del curso plantilla. Obligatorio si course_option=NEW.",
    )
    course_id: int | None = Field(
        default=None,
        gt=0,
        description="ID Canvas del curso existente. Obligatorio si course_option=EXISTING.",
    )
    excel_path: Path | None = Field(
        default=None,
        description=(
            "Ruta al Excel con textos del front del curso (URL video, párrafos). "
            "Opcional. Si no se provee, la página 'front-del-curso' no se actualiza."
        ),
    )

    # ──────────────────────────────────────────────────────────────
    # Validaciones cruzadas
    # ──────────────────────────────────────────────────────────────

    @model_validator(mode="after")
    def validar_campos_segun_opcion(self) -> DeploymentConfig:
        """
        Aplica reglas de negocio que involucran más de un campo.

        Para course_option=NEW:
            - course_name  es obligatorio
            - template_id  es obligatorio

        Para course_option=EXISTING:
            - course_id    es obligatorio
        """
        if self.course_option == CourseOption.NEW:
            errores: list[str] = []

            if not self.course_name:
                errores.append(
                    "course_name es obligatorio cuando course_option='new'."
                )
            if self.template_id is None:
                errores.append(
                    "template_id es obligatorio cuando course_option='new'."
                )
            if errores:
                raise ValueError(" | ".join(errores))

        elif self.course_option == CourseOption.EXISTING:
            if self.course_id is None:
                raise ValueError(
                    "course_id es obligatorio cuando course_option='existing'."
                )

        return self

    @model_validator(mode="after")
    def validar_rutas_existen(self) -> DeploymentConfig:
        """
        Verifica que las rutas de archivos apunten a archivos reales en disco.

        No valida en construcción de mocks de test: solo cuando los archivos
        deben existir en un contexto de producción. La validación se hace
        aquí y no en el router para mantener la lógica en el dominio.
        """
        if not self.zip_path.exists():
            raise ValueError(
                f"El archivo ZIP no existe en la ruta indicada: '{self.zip_path}'"
            )
        if self.excel_path is not None and not self.excel_path.exists():
            raise ValueError(
                f"El archivo Excel no existe en la ruta indicada: '{self.excel_path}'"
            )
        return self

    # ──────────────────────────────────────────────────────────────
    # Propiedades de conveniencia
    # ──────────────────────────────────────────────────────────────

    @property
    def is_new_course(self) -> bool:
        """True si el despliegue crea un curso nuevo en Canvas."""
        return self.course_option == CourseOption.NEW

    @property
    def requires_front_page_update(self) -> bool:
        """
        True si se debe actualizar la página 'front-del-curso'.
        Solo aplica para cursos nuevos con Excel proporcionado.
        """
        return self.is_new_course and self.excel_path is not None

    def __repr__(self) -> str:
        if self.is_new_course:
            return (
                f"DeploymentConfig(option=NEW, course='{self.course_name}', "
                f"template_id={self.template_id}, zip='{self.zip_path.name}')"
            )
        return (
            f"DeploymentConfig(option=EXISTING, course_id={self.course_id}, "
            f"zip='{self.zip_path.name}')"
        )