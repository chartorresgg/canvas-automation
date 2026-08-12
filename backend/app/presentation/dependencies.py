"""
Dependencias de FastAPI para inyección de repositorios y orquestador.

Centraliza la creación de CanvasHttpClient, repositorios y orquestador
para que los routers no tengan que conocer los detalles de construcción.

Capa: Presentación
"""

from __future__ import annotations

import os
from pathlib import Path

from app.domain.services.interactive_content_detector import (
    InteractiveContentDetector,
)
from app.infrastructure.persistence.sqlite_audit_repository import (
    SQLiteAuditRepository,
)
from app.domain.interfaces.i_audit_repository import IAuditRepository
from app.infrastructure.canvas.course_repository import CourseRepository
from app.infrastructure.canvas.file_repository import FileRepository
from app.infrastructure.canvas.http_client import CanvasHttpClient
from app.infrastructure.canvas.page_repository import PageRepository
from app.infrastructure.composers.page_composer_factory import PageComposerFactory

# Directorio temporal para ZIPs extraídos
TMP_DIR = Path(__file__).parent.parent.parent / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)


def get_tmp_dir() -> Path:
    """Retorna el directorio temporal configurado."""
    return TMP_DIR


def get_page_composer_factory() -> PageComposerFactory:
    """Crea una instancia de PageComposerFactory con los composers registrados."""
    return PageComposerFactory()


def get_interactive_detector() -> InteractiveContentDetector:
    """Crea una instancia del detector de contenido interactivo."""
    return InteractiveContentDetector()


async def crear_orchestrator_context(
    tmp_dir:      Path,
    canvas_token: str | None = None,
) -> tuple[CanvasHttpClient, "DeploymentOrchestrator"]:  # noqa: F821
    """
    Crea el orquestador con todos sus colaboradores.

    Args:
        tmp_dir:      Directorio temporal para ZIPs.
        canvas_token: Token Canvas de la sesión activa.
                      Si es None, usa la variable de entorno
                      CANVAS_ACCESS_TOKEN (modo desarrollo local).
    """
    from app.application.orchestrator import DeploymentOrchestrator

    http = CanvasHttpClient(token=canvas_token)
    await http.__aenter__()

    course_repo = CourseRepository(http)
    file_repo   = FileRepository(http)
    page_repo   = PageRepository(http)
    detector    = get_interactive_detector()
    factory     = get_page_composer_factory()

    orchestrator = DeploymentOrchestrator(
        course_repo=course_repo,
        file_repo=file_repo,
        page_repo=page_repo,
        detector=detector,
        factory=factory,
        tmp_dir=tmp_dir,
    )

    return http, orchestrator

# Ruta del archivo SQLite — configurable por variable de entorno
# para facilitar migración a nube con disco persistente.
#
# El valor por defecto vive FUERA del árbol del repositorio. La auditoría
# de seguridad de agosto 2026 encontró que backend/data/audit_log.db se
# había versionado con registros reales de despliegues (IDs y nombres de
# cursos institucionales). Con la ruta por defecto en el directorio del
# usuario, un `git add` accidental ya no puede volver a exponerlos.
#
# En producción se sobrescribe con AUDIT_DB_PATH (ver render.yaml).
_DB_PATH = Path(
    os.getenv(
        "AUDIT_DB_PATH",
        str(Path.home() / ".canvas-automation" / "audit_log.db"),
    )
)


def get_audit_repository() -> IAuditRepository:
    """
    Retorna la implementación activa del repositorio de auditoría.

    Para migrar a PostgreSQL:
        1. Crear PostgresAuditRepository(IAuditRepository)
        2. Retornar esa instancia aquí
        3. Sin más cambios en el sistema
    """
    return SQLiteAuditRepository(_DB_PATH)


# Instancia singleton — un solo repositorio por proceso
audit_repository: IAuditRepository = get_audit_repository()

def get_canvas_token_from_session(session_id: str) -> str:
    """
    Recupera el token Canvas de una sesión activa.

    Raises:
        HTTPException 401 si la sesión no existe o expiró.
    """
    from fastapi import HTTPException
    from app.presentation.session_manager import session_manager

    token = session_manager.obtener_token(session_id)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Sesión no encontrada. Por favor inicia sesión nuevamente.",
        )
    return token