"""
Repositorio de operaciones sobre cursos en Canvas LMS.

Abstrae las llamadas REST de Canvas relacionadas con cursos:
creación, duplicación por content migration y consulta.

Capa: Infraestructura
Patrón: Repository (Martin Fowler / GoF estructural)
Colaboradores: CanvasHttpClient (único medio de comunicación HTTP)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from app.infrastructure.canvas.http_client import (
    CanvasHttpClient,
    CanvasNotFoundError,
)

logger = logging.getLogger(__name__)

# Segundos máximos esperando que una migración de plantilla complete
MIGRATION_TIMEOUT_SEG: int = 600  # 10 minutos
MIGRATION_POLL_INTERVAL_SEG: float = 5.0


# ──────────────────────────────────────────────────────────────────────────────
# Value Objects de resultado — exclusivos de este repositorio
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CourseInfo:
    """
    Información básica de un curso Canvas.
    Usado como retorno de get_course() y create_course().
    """
    id: int
    name: str
    course_code: str
    workflow_state: str
    url: str

    @classmethod
    def desde_respuesta_canvas(cls, data: dict) -> CourseInfo:
        """Construye un CourseInfo desde la respuesta JSON de Canvas."""
        course_id = data["id"]
        return cls(
            id=course_id,
            name=data.get("name", ""),
            course_code=data.get("course_code", ""),
            workflow_state=data.get("workflow_state", ""),
            url=f"https://poli.instructure.com/courses/{course_id}",
        )


@dataclass(frozen=True)
class MigrationResult:
    """
    Resultado de una operación de content migration en Canvas.
    """
    migration_id: int
    course_id: int
    workflow_state: str
    completada: bool

    @property
    def fallida(self) -> bool:
        return self.workflow_state == "failed"


# ──────────────────────────────────────────────────────────────────────────────
# Excepción específica del repositorio
# ──────────────────────────────────────────────────────────────────────────────

class MigrationTimeoutError(Exception):
    """La migración de plantilla no completó dentro del tiempo máximo."""


class MigrationFailedError(Exception):
    """Canvas reportó que la migración de plantilla falló."""


# ──────────────────────────────────────────────────────────────────────────────
# Repositorio principal
# ──────────────────────────────────────────────────────────────────────────────

class CourseRepository:
    """
    Repositorio de operaciones sobre cursos Canvas LMS.

    Responsabilidad única (SRP): traducir conceptos de dominio
    (crear curso, copiar plantilla) a llamadas REST concretas de Canvas.
    No conoce la lógica de negocio ni el proceso de despliegue.

    Colaboradores:
        CanvasHttpClient — único medio de comunicación HTTP permitido.

    Uso típico dentro de DeploymentOrchestrator:
        repo = CourseRepository(http_client)
        info = await repo.create_course("Fundamentos de Programación")
        await repo.copy_template(src_id=10001, dst_id=info.id)
    """

    def __init__(self, http: CanvasHttpClient) -> None:
        """
        Args:
            http: Instancia activa de CanvasHttpClient (dentro de su context manager).
        """
        self._http = http

    # ──────────────────────────────────────────────────────────────
    # API pública
    # ──────────────────────────────────────────────────────────────

    async def create_course(self, name: str) -> CourseInfo:
        """
        Crea un nuevo curso en Canvas LMS bajo la cuenta configurada.

        El curso se crea como privado, sin matrícula pública.
        El analista queda automáticamente inscrito como instructor.

        Args:
            name: Nombre oficial del curso (aparece en Canvas LMS).

        Returns:
            CourseInfo con el ID y datos del curso recién creado.

        Raises:
            CanvasAuthError:   Token sin permisos de creación de cursos.
            CanvasClientError: Nombre inválido u otro error de validación.
        """
        logger.info("Creando curso en Canvas: '%s'", name)

        data = {
            "course[name]":      name,
            "course[course_code]": name,
            "course[is_public]": "false",
            "course[license]":   "private",
            "enroll_me":         "true",
        }

        respuesta = await self._http.post(
            f"accounts/{self._http.account_id}/courses",
            data=data,
        )

        info = CourseInfo.desde_respuesta_canvas(respuesta)
        logger.info(
            "Curso creado exitosamente: '%s' (ID: %d)", info.name, info.id
        )
        return info

    async def copy_template(
        self, src_id: int, dst_id: int
    ) -> MigrationResult:
        """
        Copia la estructura de un curso plantilla hacia un curso destino.

        Usa el mecanismo de Content Migration de Canvas, que copia
        módulos, páginas, actividades y archivos del curso origen.
        Esta operación es asíncrona en Canvas: retorna inmediatamente
        con un migration_id, y el estado real se consulta con poll_migration().

        Args:
            src_id: ID del curso Canvas que actúa como plantilla origen.
            dst_id: ID del curso Canvas destino (recién creado).

        Returns:
            MigrationResult con el migration_id para hacer polling.

        Raises:
            CanvasNotFoundError: Si src_id o dst_id no existen en Canvas.
            CanvasAuthError:     Sin permisos sobre los cursos.
        """
        logger.info(
            "Iniciando migración de plantilla: %d → %d", src_id, dst_id
        )

        payload = {
            "migration_type": "course_copy_importer",
            "settings": {
                "source_course_id": src_id,
            },
        }

        respuesta = await self._http.post(
            f"courses/{dst_id}/content_migrations",
            json=payload,
        )

        migration_id = respuesta["id"]
        logger.info(
            "Migración iniciada (ID: %d). Esperando completación...", migration_id
        )

        return MigrationResult(
            migration_id=migration_id,
            course_id=dst_id,
            workflow_state=respuesta.get("workflow_state", "running"),
            completada=False,
        )

    async def poll_migration(
        self,
        course_id: int,
        migration_id: int,
        timeout_seg: int = MIGRATION_TIMEOUT_SEG,
        poll_interval: float = MIGRATION_POLL_INTERVAL_SEG,
    ) -> MigrationResult:
        """
        Espera activamente a que una content migration de Canvas complete.

        Hace polling cada `poll_interval` segundos hasta que el
        workflow_state sea "completed" o "failed", o se supere el timeout.

        Args:
            course_id:     ID del curso destino de la migración.
            migration_id:  ID de la migración retornado por copy_template().
            timeout_seg:   Segundos máximos de espera. Default 600 s (10 min).
            poll_interval: Segundos entre cada consulta. Default 5 s.

        Returns:
            MigrationResult con workflow_state="completed".

        Raises:
            MigrationFailedError:  Canvas reportó que la migración falló.
            MigrationTimeoutError: Se superó el tiempo máximo de espera.
        """
        endpoint = f"courses/{course_id}/content_migrations/{migration_id}"
        tiempo_transcurrido: float = 0.0

        while tiempo_transcurrido < timeout_seg:
            respuesta = await self._http.get(endpoint)
            estado = respuesta.get("workflow_state", "")  # type: ignore[union-attr]

            logger.debug(
                "Migración %d — estado: '%s' (%.0fs transcurridos)",
                migration_id, estado, tiempo_transcurrido,
            )

            if estado == "completed":
                logger.info(
                    "Migración %d completada exitosamente (%.0fs)",
                    migration_id, tiempo_transcurrido,
                )
                return MigrationResult(
                    migration_id=migration_id,
                    course_id=course_id,
                    workflow_state=estado,
                    completada=True,
                )

            if estado == "failed":
                raise MigrationFailedError(
                    f"Canvas reportó que la migración {migration_id} falló. "
                    f"Revisa el log de Canvas en el curso {course_id}."
                )

            await asyncio.sleep(poll_interval)
            tiempo_transcurrido += poll_interval

        raise MigrationTimeoutError(
            f"La migración {migration_id} no completó en {timeout_seg} segundos. "
            f"Puede continuar revisando el curso {course_id} en Canvas directamente."
        )

    async def get_course(self, course_id: int) -> CourseInfo:
        """
        Consulta y valida que un curso existente es accesible en Canvas.

        Usado cuando course_option=EXISTING para verificar que el ID
        ingresado por el analista corresponde a un curso real y accesible.

        Args:
            course_id: ID del curso Canvas a consultar.

        Returns:
            CourseInfo con los datos del curso.

        Raises:
            CanvasNotFoundError: El curso no existe o el token no tiene acceso.
            CanvasAuthError:     Token sin permisos sobre este curso.
        """
        logger.info("Consultando curso existente ID: %d", course_id)

        try:
            respuesta = await self._http.get(f"courses/{course_id}")
            info = CourseInfo.desde_respuesta_canvas(respuesta)  # type: ignore[arg-type]
            logger.info(
                "Curso encontrado: '%s' (ID: %d, estado: %s)",
                info.name, info.id, info.workflow_state,
            )
            return info

        except CanvasNotFoundError:
            raise CanvasNotFoundError(
                f"No se encontró el curso con ID {course_id} en Canvas. "
                f"Verifica que el ID es correcto y que el token tiene acceso."
            )

    async def list_assignments(self, course_id: int) -> list[dict]:
        """
        Lista todas las actividades de un curso Canvas.

        Usa paginación automática para retornar la lista completa
        independientemente de la cantidad de actividades.

        Args:
            course_id: ID del curso Canvas.

        Returns:
            Lista de dicts con los datos de cada actividad.
        """
        logger.info("Listando actividades del curso %d", course_id)

        actividades = await self._http.get_paginated(
            f"courses/{course_id}/assignments",
            params={"per_page": 100},
        )

        logger.info(
            "Curso %d: %d actividad(es) encontrada(s)",
            course_id, len(actividades),
        )
        return actividades