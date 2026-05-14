"""
Router de benchmark de procesamiento local.

Mide el tiempo de cada etapa del pipeline de procesamiento
sin hacer ninguna llamada a Canvas LMS.

Etapas medidas:
    1. Extracción del ZIP
    2. Normalización de carpetas y PDFs
    3. Detección de contenido SCORM
    4. Lectura del Guion Excel (si se proporciona)

Capa: Presentación
HU-13: Pruebas de carga masiva y simulación de escenarios
"""

from __future__ import annotations

import logging
import shutil
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.domain.services.file_normalizer import FileNormalizer
from app.domain.services.interactive_content_detector import (
    InteractiveContentDetector,
)
from app.domain.services.zip_processor import ZipProcessor
from app.infrastructure.canvas.file_repository import FileRepository
from app.presentation.dependencies import TMP_DIR

router = APIRouter()
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Value objects del reporte
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class EtapaBenchmark:
    """Resultado de una etapa individual del benchmark."""
    nombre:      str
    duracion_ms: float
    detalle:     str
    exitosa:     bool = True
    error:       str | None = None

    def to_dict(self) -> dict:
        return {
            "nombre":           self.nombre,
            "duracion_ms":      round(self.duracion_ms, 2),
            "duracion_display": _ms_a_display(self.duracion_ms),
            "detalle":          self.detalle,
            "exitosa":          self.exitosa,
            "error":            self.error,
        }


@dataclass
class BenchmarkReport:
    """Reporte completo de un benchmark de procesamiento local."""
    zip_filename:          str
    total_archivos:        int
    total_size_mb:         float
    scorm_detectados:      int
    carpetas_normalizadas: int
    pdfs_normalizados:     int
    con_excel:             bool
    etapas:                list[EtapaBenchmark] = field(default_factory=list)

    @property
    def total_procesamiento_ms(self) -> float:
        return sum(e.duracion_ms for e in self.etapas if e.exitosa)

    @property
    def total_procesamiento_display(self) -> str:
        return _ms_a_display(self.total_procesamiento_ms)

    def to_dict(self) -> dict:
        return {
            "zip_filename":                self.zip_filename,
            "total_archivos":              self.total_archivos,
            "total_size_mb":               self.total_size_mb,
            "scorm_detectados":            self.scorm_detectados,
            "carpetas_normalizadas":       self.carpetas_normalizadas,
            "pdfs_normalizados":           self.pdfs_normalizados,
            "con_excel":                   self.con_excel,
            "total_procesamiento_ms":      round(self.total_procesamiento_ms, 2),
            "total_procesamiento_display": self.total_procesamiento_display,
            "etapas":                      [e.to_dict() for e in self.etapas],
        }


def _ms_a_display(ms: float) -> str:
    """Formatea milisegundos para visualización."""
    if ms < 1000:
        return f"{ms:.0f} ms"
    segundos = ms / 1000
    if segundos < 60:
        return f"{segundos:.2f} s"
    minutos = int(segundos // 60)
    segs    = segundos % 60
    return f"{minutos}m {segs:.0f}s"


# ──────────────────────────────────────────────────────────────────────────────
# Endpoint principal
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/benchmark",
    summary="Benchmark de procesamiento local",
    description=(
        "Ejecuta el pipeline de procesamiento local (sin llamar a Canvas) "
        "y retorna el tiempo de cada etapa. "
        "Usado para medir el rendimiento del sistema y validar la HU-13."
    ),
)
async def ejecutar_benchmark(
    zip_file:   UploadFile = File(..., description="ZIP del aula a procesar."),
    excel_file: UploadFile | None = File(
        default=None,
        description="Excel del Guion (opcional).",
    ),
) -> JSONResponse:
    """
    Mide el tiempo de procesamiento local de un aula virtual.

    Etapas:
        1. Extracción ZIP   — descomprimir y listar archivos
        2. Normalización    — renombrar carpetas y PDFs al estándar institucional
        3. Detección SCORM  — identificar paquetes Storyline
        4. Lectura Excel    — parsear Guion de módulo (si se provee)

    Returns:
        JSON con tiempos por etapa y resumen total.
    """
    if not zip_file.filename or not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener extensión .zip",
        )

    run_id   = str(uuid.uuid4())
    work_dir = TMP_DIR / f"benchmark_{run_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    zip_path:    Path       = work_dir / (zip_file.filename or "curso.zip")
    excel_path:  Path | None = None

    try:
        # Guardar archivos en disco
        with zip_path.open("wb") as buf:
            shutil.copyfileobj(zip_file.file, buf)

        if excel_file and excel_file.filename:
            excel_path = work_dir / excel_file.filename
            with excel_path.open("wb") as buf:
                shutil.copyfileobj(excel_file.file, buf)

        reporte = BenchmarkReport(
            zip_filename=zip_file.filename or "curso.zip",
            total_archivos=0,
            total_size_mb=0.0,
            scorm_detectados=0,
            carpetas_normalizadas=0,
            pdfs_normalizados=0,
            con_excel=excel_path is not None,
        )

        extract_dir = work_dir / "extracted"
        normalizer  = FileNormalizer()
        zip_proc    = ZipProcessor(
            zip_path=zip_path,
            extract_dir=extract_dir,
            normalizer=normalizer,
        )

        # ── Etapa 1: Extracción ───────────────────────────────────────────
        t0 = time.perf_counter()
        try:
            extraction = zip_proc.extract()
            duracion_extraccion = (time.perf_counter() - t0) * 1000

            reporte.total_archivos = extraction.total_files
            reporte.total_size_mb  = extraction.total_size_mb

            reporte.etapas.append(EtapaBenchmark(
                nombre="Extracción ZIP",
                duracion_ms=duracion_extraccion,
                detalle=(
                    f"{extraction.total_files} archivos extraídos "
                    f"({extraction.total_size_mb} MB)"
                ),
            ))
        except Exception as exc:
            reporte.etapas.append(EtapaBenchmark(
                nombre="Extracción ZIP",
                duracion_ms=(time.perf_counter() - t0) * 1000,
                detalle="Falló la extracción",
                exitosa=False,
                error=str(exc),
            ))
            return JSONResponse(content=reporte.to_dict())

        # ── Etapa 2: Normalización ────────────────────────────────────────
        t0 = time.perf_counter()
        try:
            proc_result = zip_proc.normalize()
            duracion_norm = (time.perf_counter() - t0) * 1000

            carpetas = proc_result.normalization_folders.total_changes
            pdfs     = proc_result.normalization_pdfs.total_changes
            reporte.carpetas_normalizadas = carpetas
            reporte.pdfs_normalizados     = pdfs

            reporte.etapas.append(EtapaBenchmark(
                nombre="Normalización",
                duracion_ms=duracion_norm,
                detalle=(
                    f"{carpetas} carpeta(s) renombrada(s), "
                    f"{pdfs} PDF(s) renombrado(s)"
                ),
            ))
        except Exception as exc:
            reporte.etapas.append(EtapaBenchmark(
                nombre="Normalización",
                duracion_ms=(time.perf_counter() - t0) * 1000,
                detalle="Falló la normalización",
                exitosa=False,
                error=str(exc),
            ))

        # ── Etapa 3: Detección SCORM ──────────────────────────────────────
        t0 = time.perf_counter()
        try:
            archivos_locales = FileRepository._listar_archivos(
                zip_proc.content_path
            )
            file_map_local = {
                ruta: idx
                for idx, (_, ruta) in enumerate(archivos_locales)
            }

            detector  = InteractiveContentDetector()
            scorm_map = detector.detect(file_map_local)
            duracion_scorm = (time.perf_counter() - t0) * 1000

            total_scorm = sum(len(v) for v in scorm_map.values())
            reporte.scorm_detectados = total_scorm

            if total_scorm > 0:
                unidades_str = ", ".join(
                    f"U{u}: {len(v)} paquete(s)"
                    for u, v in sorted(scorm_map.items())
                )
                detalle_scorm = (
                    f"{total_scorm} paquete(s) Storyline detectado(s) → {unidades_str}"
                )
            else:
                detalle_scorm = "Sin contenido SCORM"

            reporte.etapas.append(EtapaBenchmark(
                nombre="Detección SCORM",
                duracion_ms=duracion_scorm,
                detalle=detalle_scorm,
            ))
        except Exception as exc:
            reporte.etapas.append(EtapaBenchmark(
                nombre="Detección SCORM",
                duracion_ms=(time.perf_counter() - t0) * 1000,
                detalle="Falló la detección SCORM",
                exitosa=False,
                error=str(exc),
            ))

        # ── Etapa 4: Lectura Excel (opcional) ─────────────────────────────
        if excel_path:
            t0 = time.perf_counter()
            try:
                from app.domain.services.guion_excel_reader import (
                    GuionExcelReader,
                )
                guion = GuionExcelReader(excel_path).read()
                duracion_excel = (time.perf_counter() - t0) * 1000

                unidades_con_video   = sum(
                    1 for u in guion.unidades.values() if u.video_intro_url
                )
                unidades_con_podcast = sum(
                    1 for u in guion.unidades.values() if u.podcast_url
                )
                unidades_con_vimeo   = sum(
                    1 for u in guion.unidades.values() if u.vimeo_mat_fund_url
                )

                reporte.etapas.append(EtapaBenchmark(
                    nombre="Lectura Guion Excel",
                    duracion_ms=duracion_excel,
                    detalle=(
                        f"{len(guion.unidades)} unidades | "
                        f"video_inicial={'✓' if guion.video_inicial_url else '✗'} | "
                        f"videos_intro={unidades_con_video} | "
                        f"podcasts={unidades_con_podcast} | "
                        f"vimeo_mf={unidades_con_vimeo}"
                    ),
                ))
            except Exception as exc:
                reporte.etapas.append(EtapaBenchmark(
                    nombre="Lectura Guion Excel",
                    duracion_ms=(time.perf_counter() - t0) * 1000,
                    detalle="Falló la lectura del Excel",
                    exitosa=False,
                    error=str(exc),
                ))

        logger.info(
            "Benchmark completado: %s — %d archivos, %.1f MB, %d SCORM, total=%.0f ms",
            zip_file.filename,
            reporte.total_archivos,
            reporte.total_size_mb,
            reporte.scorm_detectados,
            reporte.total_procesamiento_ms,
        )

        return JSONResponse(content=reporte.to_dict())

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)