"""
Fábrica de composers de páginas Canvas.

Centraliza la creación de instancias de IPageComposer según el tipo
de página, desacoplando al DeploymentOrchestrator de las clases concretas.

Capa: Infraestructura — composers
Patrón: Simple Factory + Registry (GoF — Creacional)
Colaboradores: IPageComposer y todas sus implementaciones
"""

from __future__ import annotations

from app.domain.interfaces.i_page_composer import IPageComposer
from app.infrastructure.composers.iframe_composer import IframeComposer
from app.infrastructure.composers.material_fundamental_composer import (
    MaterialFundamentalComposer,
)
from app.infrastructure.composers.complementary_page_composer import (
    ComplementaryPageComposer,
)
from app.infrastructure.composers.front_page_composer import FrontPageComposer
from app.infrastructure.composers.material_de_trabajo_composer import (
    MaterialDeTrabajoComposer,
)


# ── Tipos de página soportados ────────────────────────────────────────────────

class PageType:
    """
    Constantes de tipos de página para usar con PageComposerFactory.
    Evita strings mágicos en el código del orquestador.
    """
    IFRAME:                str = "iframe"
    MATERIAL_FUNDAMENTAL:  str = "material_fundamental"
    COMPLEMENTARY:         str = "complementary"
    FRONT:                 str = "front"
    MATERIAL_TRABAJO:      str = "material_trabajo"


class PageComposerFactory:
    """
    Fábrica con registro de composers de páginas Canvas.

    Responsabilidad única: instanciar el IPageComposer correcto
    según el tipo de página solicitado. El registro es extensible
    sin modificar el orquestador (principio OCP).

    Uso en DeploymentOrchestrator:
        factory = PageComposerFactory()
        composer = factory.create(PageType.IFRAME)
        html = composer.compose(course_id, ctx)

    Extensión (sin modificar código existente):
        factory.register("nuevo_tipo", NuevoComposer)
    """

    def __init__(self) -> None:
        # Registro interno: tipo → clase concreta de IPageComposer
        self._registry: dict[str, type[IPageComposer]] = {
            PageType.IFRAME:               IframeComposer,
            PageType.MATERIAL_FUNDAMENTAL: MaterialFundamentalComposer,
            PageType.COMPLEMENTARY:        ComplementaryPageComposer,
            PageType.FRONT:                FrontPageComposer,
            PageType.MATERIAL_TRABAJO: MaterialDeTrabajoComposer,
        }

    def register(
        self,
        page_type: str,
        composer_class: type[IPageComposer],
    ) -> None:
        """
        Registra un nuevo tipo de composer en la fábrica.

        Permite añadir nuevos tipos de página sin modificar
        ninguna clase existente (principio OCP).

        Args:
            page_type:      Identificador único del tipo de página.
            composer_class: Clase que implementa IPageComposer.

        Raises:
            TypeError: Si composer_class no es subclase de IPageComposer.
        """
        if not (
            isinstance(composer_class, type)
            and issubclass(composer_class, IPageComposer)
        ):
            raise TypeError(
                f"{composer_class} debe ser una subclase de IPageComposer"
            )
        self._registry[page_type] = composer_class

    def create(self, page_type: str) -> IPageComposer:
        """
        Instancia y retorna el composer correspondiente al tipo de página.

        Args:
            page_type: Tipo de página (usar constantes de PageType).

        Returns:
            Instancia de IPageComposer lista para usar.

        Raises:
            ValueError: Si el tipo de página no está registrado.
        """
        composer_class = self._registry.get(page_type)

        if not composer_class:
            tipos_disponibles = list(self._registry.keys())
            raise ValueError(
                f"Tipo de página '{page_type}' no registrado. "
                f"Tipos disponibles: {tipos_disponibles}"
            )

        return composer_class()

    def tipos_registrados(self) -> list[str]:
        """Retorna la lista de tipos de página registrados."""
        return list(self._registry.keys())