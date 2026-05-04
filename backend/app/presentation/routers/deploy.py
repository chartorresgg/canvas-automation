"""
Router de despliegue — Capa de Presentación.

Expone el endpoint de carga y validación del ZIP.
El procesamiento pesado (Sprint 2) se añade aquí sin modificar
los endpoints existentes (OCP).

Capa: Presentación
Colaboradores: ZipProcessor, FileNormalizer
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.domain.services.file_normalizer import FileNormalizer
from app.domain.services.zip_processor import ZipProcessor

router = APIRouter()

# Directorio temporal donde se almacenan los ZIPs recibidos
TMP_DIR = Path(__file__).parent.parent.parent.parent / "tmp"


class UploadResponse(BaseModel):
    """Respuesta del endpoint de carga de archivo ZIP."""
    task_id: str
    filename: str
    total_files: int
    total_size_mb: float
    folders_renamed: list[str]
    files_renamed: list[str]
    warnings: list[str]
    message: str


@router.post(
    "/deploy/upload",
    response_model=UploadResponse,
    summary="Cargar y validar archivo ZIP del aula virtual",
    description=(
        "Recibe el archivo ZIP, lo extrae en un directorio temporal, "
        "aplica normalización de carpetas y PDFs, y retorna las "
        "métricas del proceso. El task_id identifica esta sesión "
        "de despliegue en los pasos siguientes."
    ),
)
async def upload_zip(
    zip_file: UploadFile = File(
        ..., description="Archivo ZIP con los materiales del aula virtual."
    ),
    excel_file: UploadFile | None = File(
        default=None,
        description="Excel con los textos del front del curso (opcional).",
    ),
) -> UploadResponse:
    """
    Paso 1 del despliegue: carga y validación del archivo ZIP.

    Flujo:
        1. Valida que el archivo sea .zip
        2. Genera un task_id único para esta sesión
        3. Almacena el ZIP en tmp/{task_id}/
        4. Ejecuta ZipProcessor.extract() + normalize()
        5. Retorna métricas de la operación

    Raises:
        HTTPException 400: Si el archivo no es .zip o está corrupto.
        HTTPException 500: Si falla la extracción o normalización.
    """
    # Validar extensión
    if not zip_file.filename or not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener extensión .zip",
        )

    # Generar identificador único de sesión
    task_id = str(uuid.uuid4())
    task_dir = TMP_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    zip_path = task_dir / zip_file.filename
    extract_dir = task_dir / "extracted"

    try:
        # Persistir el ZIP en disco
        with zip_path.open("wb") as buffer:
            shutil.copyfileobj(zip_file.file, buffer)

        # Persistir el Excel si fue enviado
        if excel_file and excel_file.filename:
            excel_path = task_dir / excel_file.filename
            with excel_path.open("wb") as buffer:
                shutil.copyfileobj(excel_file.file, buffer)

        # Procesar con ZipProcessor
        processor = ZipProcessor(
            zip_path=zip_path,
            extract_dir=extract_dir,
            normalizer=FileNormalizer(),
        )

        extraction = processor.extract()
        proc_result = processor.normalize()

    except FileNotFoundError as exc:
        _limpiar_directorio(task_dir)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        _limpiar_directorio(task_dir)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        _limpiar_directorio(task_dir)
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando el archivo: {str(exc)}",
        ) from exc

    return UploadResponse(
        task_id=task_id,
        filename=zip_file.filename,
        total_files=extraction.total_files,
        total_size_mb=extraction.total_size_mb,
        folders_renamed=proc_result.normalization_folders.folders_renamed,
        files_renamed=proc_result.normalization_pdfs.files_renamed,
        warnings=proc_result.all_warnings,
        message=(
            f"ZIP procesado exitosamente. "
            f"{extraction.total_files} archivos listos para despliegue."
        ),
    )


def _limpiar_directorio(path: Path) -> None:
    """Elimina el directorio temporal si falla el procesamiento."""
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)