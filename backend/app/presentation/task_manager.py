"""
Gestor de tareas de despliegue en memoria.

Mantiene queues y referencias a asyncio.Task para permitir
cancelación activa desde el endpoint DELETE /deploy/cancel/{task_id}.

Capa: Presentación
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.value_objects.progress_event import ProgressEvent

logger = logging.getLogger(__name__)


@dataclass
class TaskEntry:
    """Entrada del registro de tareas activas."""
    task_id:      str
    queue:        asyncio.Queue[ProgressEvent | None]
    creada_en:    datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completada:   bool = False
    cancelada:    bool = False
    asyncio_task: asyncio.Task | None = None  # referencia para task.cancel()


class TaskManager:
    """
    Registro en memoria de tareas de despliegue activas.

    Responsabilidad única: gestionar el ciclo de vida de las queues
    asyncio y las referencias a tasks para cancelación.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, TaskEntry] = {}

    def registrar(self, task_id: str) -> asyncio.Queue[ProgressEvent | None]:
        """Registra una nueva tarea y retorna su queue."""
        queue: asyncio.Queue[ProgressEvent | None] = asyncio.Queue()
        self._tasks[task_id] = TaskEntry(task_id=task_id, queue=queue)
        logger.info("Tarea registrada: %s", task_id)
        return queue

    def registrar_asyncio_task(
        self, task_id: str, task: asyncio.Task
    ) -> None:
        """
        Asocia el asyncio.Task real al TaskEntry.

        Llamado desde _ejecutar_deploy_background() inmediatamente
        después de arrancar, para que cancelar() pueda usar task.cancel().

        Args:
            task_id: Identificador de la tarea.
            task:    asyncio.Task actual (asyncio.current_task()).
        """
        entry = self._tasks.get(task_id)
        if entry:
            entry.asyncio_task = task

    def obtener_queue(
        self, task_id: str
    ) -> asyncio.Queue[ProgressEvent | None] | None:
        """Retorna la queue de una tarea existente."""
        entry = self._tasks.get(task_id)
        return entry.queue if entry else None

    def cancelar(self, task_id: str) -> bool:
        """
        Solicita la cancelación de una tarea activa.

        Llama a task.cancel() sobre el asyncio.Task del BackgroundTask,
        lo que inyecta CancelledError en la siguiente operación await
        del orquestador.

        Args:
            task_id: Identificador de la tarea a cancelar.

        Returns:
            True si la cancelación fue solicitada con éxito.
            False si la tarea no existe, ya terminó o ya fue cancelada.
        """
        entry = self._tasks.get(task_id)
        if not entry:
            return False
        if entry.completada or entry.cancelada:
            return False

        entry.cancelada = True

        if entry.asyncio_task and not entry.asyncio_task.done():
            entry.asyncio_task.cancel()
            logger.info("Cancelación solicitada: %s", task_id)
            return True

        return False

    def marcar_completada(self, task_id: str) -> None:
        """Marca la tarea como completada y envía el sentinel."""
        entry = self._tasks.get(task_id)
        if entry:
            entry.completada = True
            entry.queue.put_nowait(None)
            logger.info("Tarea completada: %s", task_id)

    def existe(self, task_id: str) -> bool:
        """Retorna True si la tarea existe en el registro."""
        return task_id in self._tasks

    def esta_cancelada(self, task_id: str) -> bool:
        """Retorna True si se solicitó cancelación de la tarea."""
        entry = self._tasks.get(task_id)
        return entry.cancelada if entry else False

    def limpiar_completadas(self) -> int:
        """Elimina tareas completadas del registro."""
        eliminadas = [
            tid for tid, entry in self._tasks.items()
            if entry.completada
        ]
        for tid in eliminadas:
            del self._tasks[tid]
        return len(eliminadas)


task_manager = TaskManager()