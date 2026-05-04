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
    tmp_dir: Path,
) -> tuple[CanvasHttpClient, "DeploymentOrchestrator"]:  # noqa: F821
    """
    Crea el orquestador con todos sus colaboradores.

    Retorna el cliente HTTP para que el llamador pueda gestionar
    su ciclo de vida con `async with`.

    Returns:
        Tupla (http_client, orchestrator) — el cliente debe cerrarse
        con await http_client.__aexit__(None, None, None) al terminar.
    """
    from app.application.orchestrator import DeploymentOrchestrator

    http = CanvasHttpClient()
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