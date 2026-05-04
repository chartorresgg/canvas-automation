"""
Router de despliegue — endpoints POST /deploy y GET /deploy/stream.

Expone dos endpoints:
    POST /api/v1/deploy
        → Inicia el despliegue como BackgroundTask
        → Retorna 202 Accepted con task_id y URL del stream SSE

    GET /api/v1/deploy/stream/{task_id}
        → Abre conexión SSE
        → Emite ProgressEvents hasta que el proceso termine

Capa: Presentación
Patrón: Facade (consume DeploymentOrchestrator como caja negra)
"""

from __future__ import annotations

import asyncio
import logging
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.domain.value_objects.deployment_config import (
    CourseOption,
    DeploymentConfig,
)
from app.domain.value_objects.progress_event import EventStatus, ProgressEvent
from app.presentation.dependencies import TMP_DIR, crear_orchestrator_context
from app.presentation.schemas import DeployStartResponse
from app.presentation.task_manager import task_manager

router = APIRouter()
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/v1/deploy
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/deploy",
    response_model=DeployStartResponse,
    status_code=202,
    summary="Iniciar despliegue asíncrono del aula virtual",
    description=(
        "Inicia el proceso completo de despliegue como tarea en segundo plano. "
        "Retorna inmediatamente con el task_id y la URL del stream SSE. "
        "El progreso se monitorea en GET /deploy/stream/{task_id}."
    ),
)
async def iniciar_deploy(
    background_tasks: BackgroundTasks,
    zip_file:     UploadFile = File(..., description="ZIP con los materiales del aula."),
    excel_file:   UploadFile | None = File(default=None, description="Excel del guion (opcional)."),
    course_option:        str = Form(..., description="'new' o 'existing'."),
    course_name:          str | None = Form(default=None, description="Nombre del curso (si course_option=new)."),
    template_id:          int | None = Form(default=None, description="ID de plantilla Canvas (si course_option=new)."),
    course_id:            int | None = Form(default=None, description="ID del curso existente (si course_option=existing)."),
    modelo_instruccional: str = Form(default="Unidades", description="Modelo instruccional del aula."),
    nivel_formacion:      str = Form(default="Pregrado",  description="Nivel de formación del curso."),
) -> DeployStartResponse:
    """
    Endpoint principal de despliegue.

    Flujo:
        1. Validar extensión del ZIP.
        2. Guardar archivos en disco (tmp/{task_id}/).
        3. Crear DeploymentConfig validado por Pydantic v2.
        4. Registrar task_id en TaskManager.
        5. Lanzar BackgroundTask con el orquestador.
        6. Retornar 202 con task_id y URL del stream SSE.

    El BackgroundTask corre de forma asíncrona: el cliente recibe la
    respuesta 202 antes de que el orquestador haya procesado un solo archivo.
    """
    # 1. Validar extensión
    if not zip_file.filename or not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener extensión .zip",
        )

    # 2. Persistir archivos en disco
    task_id  = str(uuid.uuid4())
    task_dir = TMP_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    zip_path: Path   = task_dir / (zip_file.filename or "curso.zip")
    excel_path: Path | None = None

    try:
        with zip_path.open("wb") as buf:
            shutil.copyfileobj(zip_file.file, buf)

        if excel_file and excel_file.filename:
            excel_path = task_dir / excel_file.filename
            with excel_path.open("wb") as buf:
                shutil.copyfileobj(excel_file.file, buf)

    except Exception as exc:
        shutil.rmtree(task_dir, ignore_errors=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error guardando archivos: {exc}",
        ) from exc

    # 3. Construir DeploymentConfig con validación Pydantic
    try:
        # Sanitizar campos según la opción de curso para evitar
        # que Swagger envíe valores por defecto que violen las
        # validaciones cruzadas de DeploymentConfig.
        # Si course_option=new  → ignorar course_id aunque venga 0
        # Si course_option=existing → ignorar template_id y course_name
        opcion = CourseOption(course_option)

        course_id_limpio    = course_id    if opcion == CourseOption.EXISTING and course_id and course_id > 0 else None
        template_id_limpio  = template_id  if opcion == CourseOption.NEW else None
        course_name_limpio  = course_name  if opcion == CourseOption.NEW else None

        config = DeploymentConfig(
            zip_path=zip_path,
            course_option=opcion,
            course_name=course_name_limpio,
            template_id=template_id_limpio,
            course_id=course_id_limpio,
            excel_path=excel_path,
        )
        object.__setattr__(config, "modelo_instruccional", modelo_instruccional)
        object.__setattr__(config, "nivel_formacion",      nivel_formacion)

    except Exception as exc:
        shutil.rmtree(task_dir, ignore_errors=True)
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # 4. Registrar queue en TaskManager
    queue = task_manager.registrar(task_id)

    # 5. Lanzar BackgroundTask
    background_tasks.add_task(
        _ejecutar_deploy_background,
        task_id=task_id,
        config=config,
        queue=queue,
    )

    logger.info("Despliegue iniciado — task_id: %s", task_id)

    # 6. Retornar 202 Accepted
    return DeployStartResponse(
        task_id=task_id,
        stream_url=f"/api/v1/deploy/stream/{task_id}",
        message=(
            "Despliegue iniciado. Conecta al stream SSE para monitorear el progreso."
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/v1/deploy/stream/{task_id}
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/deploy/stream/{task_id}",
    summary="Stream SSE del progreso de un despliegue",
    description=(
        "Abre una conexión Server-Sent Events que emite ProgressEvents "
        "hasta que el despliegue finaliza (status: completed o failed). "
        "El cliente debe conectar con EventSource o fetch con stream."
    ),
    response_class=StreamingResponse,
)
async def stream_progreso(task_id: str) -> StreamingResponse:
    """
    Endpoint SSE para monitorear el progreso de un despliegue.

    Retorna una StreamingResponse de tipo text/event-stream.
    Cada evento tiene el formato estándar SSE:
        data: {json del ProgressEvent}\\n\\n

    La conexión se cierra automáticamente cuando el orquestador
    emite un evento con is_terminal=True (completed, failed o cancelled).

    Si el task_id no existe, retorna 404.
    """
    if not task_manager.existe(task_id):
        raise HTTPException(
            status_code=404,
            detail=f"No existe ninguna tarea activa con id '{task_id}'.",
        )

    queue = task_manager.obtener_queue(task_id)
    if queue is None:
        raise HTTPException(
            status_code=404,
            detail=f"Queue no disponible para la tarea '{task_id}'.",
        )

    return StreamingResponse(
        _generar_stream_sse(task_id, queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "Connection":                  "keep-alive",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/v1/deploy/upload  (mantenido de Sprint 1 — validación previa)
# ──────────────────────────────────────────────────────────────────────────────

from app.domain.services.file_normalizer import FileNormalizer
from app.domain.services.zip_processor import ZipProcessor
from app.presentation.schemas import DeployStartResponse as UploadResponse


class _UploadOnlyResponse(DeployStartResponse):
    filename:      str
    total_files:   int
    total_size_mb: float
    folders_renamed: list[str]
    files_renamed:   list[str]
    warnings:        list[str]


@router.post(
    "/deploy/upload",
    summary="Cargar y validar ZIP (paso previo al despliegue)",
    description="Extrae y normaliza el ZIP localmente. No interactúa con Canvas.",
)
async def upload_zip(
    zip_file:   UploadFile = File(...),
    excel_file: UploadFile | None = File(default=None),
) -> JSONResponse:
    """Valida el ZIP localmente sin iniciar el despliegue completo."""
    if not zip_file.filename or not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="El archivo debe ser .zip")

    task_id  = str(uuid.uuid4())
    task_dir = TMP_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    zip_path    = task_dir / zip_file.filename
    extract_dir = task_dir / "extracted"
    excel_path  = None

    try:
        with zip_path.open("wb") as buf:
            shutil.copyfileobj(zip_file.file, buf)

        if excel_file and excel_file.filename:
            excel_path = task_dir / excel_file.filename
            with excel_path.open("wb") as buf:
                shutil.copyfileobj(excel_file.file, buf)

        processor   = ZipProcessor(zip_path, extract_dir, FileNormalizer())
        extraction  = processor.extract()
        proc_result = processor.normalize()

    except (FileNotFoundError, ValueError) as exc:
        shutil.rmtree(task_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        shutil.rmtree(task_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return JSONResponse({
        "task_id":        task_id,
        "filename":       zip_file.filename,
        "total_files":    extraction.total_files,
        "total_size_mb":  extraction.total_size_mb,
        "folders_renamed": proc_result.normalization_folders.folders_renamed,
        "files_renamed":   proc_result.normalization_pdfs.files_renamed,
        "warnings":        proc_result.all_warnings,
        "message": (
            f"ZIP procesado exitosamente. "
            f"{extraction.total_files} archivos listos."
        ),
    })


# ──────────────────────────────────────────────────────────────────────────────
# Funciones internas — BackgroundTask y SSE generator
# ──────────────────────────────────────────────────────────────────────────────

async def _ejecutar_deploy_background(
    task_id: str,
    config:  DeploymentConfig,
    queue:   asyncio.Queue,
) -> None:
    """
    Función que corre como BackgroundTask de FastAPI.

    Crea el orquestador, ejecuta el deploy() como async generator,
    deposita cada ProgressEvent en la queue, y envía el sentinel
    al terminar (con éxito o con error).

    La gestión del ciclo de vida de CanvasHttpClient se hace aquí
    con `async with` para garantizar el cierre correcto.
    """
    http = None
    try:
        http, orchestrator = await crear_orchestrator_context(TMP_DIR)

        async for event in orchestrator.deploy(config):
            queue.put_nowait(event)
            logger.debug(
                "Task %s — evento: step=%d pct=%.1f status=%s",
                task_id, event.step, event.percentage, event.status,
            )
            # Si el evento es terminal, no hace falta esperar más
            if event.is_terminal:
                break

    except Exception as exc:
        # Error inesperado fuera del orquestador — emitir evento de fallo
        logger.error(
            "Error en BackgroundTask %s: %s", task_id, exc, exc_info=True
        )
        evento_fallo = ProgressEvent.fallido(
            step=0,
            message="Error interno del servidor",
            error=str(exc),
        )
        queue.put_nowait(evento_fallo)

    finally:
        # Sentinel — indica al generador SSE que debe cerrar la conexión
        task_manager.marcar_completada(task_id)
        if http:
            await http.__aexit__(None, None, None)
        logger.info("BackgroundTask %s finalizado", task_id)


async def _generar_stream_sse(
    task_id: str,
    queue:   asyncio.Queue,
):
    """
    Generador asíncrono que convierte la queue en un stream SSE.

    Protocolo SSE:
        - Cada evento: "data: {json}\\n\\n"
        - Heartbeat cada 10 s para mantener la conexión activa
        - Cierre: cuando recibe sentinel None o evento terminal

    El heartbeat previene que proxies y browsers cierren la conexión
    por inactividad durante pasos largos (ej. migración de plantilla).
    """
    logger.info("SSE stream abierto — task_id: %s", task_id)

    try:
        while True:
            try:
                # Esperar evento con timeout para enviar heartbeat
                item = await asyncio.wait_for(queue.get(), timeout=10.0)

                if item is None:
                    # Sentinel — proceso terminado
                    logger.info("SSE stream cerrado — task_id: %s", task_id)
                    return

                # Emitir el evento como SSE
                yield item.to_sse_data()

                # Si el evento es terminal, cerrar el stream
                if item.is_terminal:
                    logger.info(
                        "SSE stream terminal (status=%s) — task_id: %s",
                        item.status, task_id,
                    )
                    return

            except asyncio.TimeoutError:
                # Heartbeat — mantiene la conexión activa
                yield ": heartbeat\n\n"

    except asyncio.CancelledError:
        # El cliente cerró la conexión antes de que terminara el proceso
        logger.info("SSE stream cancelado por cliente — task_id: %s", task_id)