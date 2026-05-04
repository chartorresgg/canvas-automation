"""
Gestor de tareas de despliegue en memoria.

Mantiene un registro de queues asyncio por task_id para que el
endpoint SSE pueda consumir los ProgressEvents emitidos por el
DeploymentOrchestrator corriendo como BackgroundTask.

Capa: Presentación
Patrón: ninguno — infraestructura de mensajería in-process
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.value_objects.progress_event import ProgressEvent

logger = logging.getLogger(__name__)

# Tiempo máximo que una tarea permanece en memoria tras completar (segundos)
_TTL_COMPLETADA_SEG: int = 300  # 5 minutos


@dataclass
class TaskEntry:
    """Entrada del registro de tareas activas."""
    task_id:    str
    queue:      asyncio.Queue[ProgressEvent | None]
    creada_en:  datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completada: bool = False


class TaskManager:
    """
    Registro en memoria de tareas de despliegue activas.

    Responsabilidad única: gestionar el ciclo de vida de las queues
    asyncio que conectan los BackgroundTasks con los endpoints SSE.

    Cada tarea tiene:
        - Una queue donde el orquestador deposita ProgressEvents.
        - Un endpoint SSE que consume esa queue y la transmite al cliente.

    El sentinel None en la queue indica que la tarea terminó
    y el endpoint SSE debe cerrar la conexión.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, TaskEntry] = {}

    def registrar(self, task_id: str) -> asyncio.Queue[ProgressEvent | None]:
        """
        Registra una nueva tarea y retorna su queue.

        Args:
            task_id: Identificador único de la tarea de despliegue.

        Returns:
            Queue donde el BackgroundTask depositará ProgressEvents.
        """
        queue: asyncio.Queue[ProgressEvent | None] = asyncio.Queue()
        self._tasks[task_id] = TaskEntry(task_id=task_id, queue=queue)
        logger.info("Tarea registrada: %s", task_id)
        return queue

    def obtener_queue(
        self, task_id: str
    ) -> asyncio.Queue[ProgressEvent | None] | None:
        """
        Retorna la queue de una tarea existente.

        Args:
            task_id: Identificador de la tarea.

        Returns:
            Queue de la tarea o None si no existe.
        """
        entry = self._tasks.get(task_id)
        return entry.queue if entry else None

    def marcar_completada(self, task_id: str) -> None:
        """
        Marca una tarea como completada y envía el sentinel a su queue.

        El sentinel None indica al endpoint SSE que debe cerrar
        la conexión con el cliente.

        Args:
            task_id: Identificador de la tarea.
        """
        entry = self._tasks.get(task_id)
        if entry:
            entry.completada = True
            entry.queue.put_nowait(None)
            logger.info("Tarea completada: %s", task_id)

    def existe(self, task_id: str) -> bool:
        """Retorna True si la tarea existe en el registro."""
        return task_id in self._tasks

    def limpiar_completadas(self) -> int:
        """
        Elimina tareas completadas del registro.

        Operación de limpieza que puede llamarse periódicamente.
        No elimina tareas activas.

        Returns:
            Número de tareas eliminadas.
        """
        eliminadas = [
            tid for tid, entry in self._tasks.items()
            if entry.completada
        ]
        for tid in eliminadas:
            del self._tasks[tid]
        return len(eliminadas)


# ── Instancia global compartida por toda la aplicación ──────────────────────
# FastAPI es single-process en desarrollo — una instancia es suficiente.
# En producción multi-worker se necesitaría Redis Pub/Sub.
task_manager = TaskManager()