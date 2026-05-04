"""
Interfaz del patrón Strategy para composers de páginas Canvas.

Define el contrato que deben cumplir todas las implementaciones
de generación de HTML para páginas del aula virtual.

Capa: Dominio — interfaces
Patrón: Strategy (GoF — Comportamental)
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IPageComposer(ABC):
    """
    Contrato de generación de HTML para páginas de Canvas LMS.

    Cada implementación concreta conoce cómo generar el HTML
    para un tipo específico de página del aula virtual.

    El orquestador y PageRepository dependen de esta abstracción,
    no de ninguna implementación concreta (principio DIP).

    Implementaciones disponibles:
        IframeComposer              — presentación y cierre
        MaterialFundamentalComposer — material por unidad
        ComplementaryPageComposer   — material complementario
        FrontPageComposer           — front del curso
    """

    @abstractmethod
    def compose(self, course_id: int, ctx: dict) -> str:
        """
        Genera el HTML completo para una página de Canvas.

        Args:
            course_id: ID del curso Canvas destino.
            ctx:       Contexto con los datos necesarios para generar
                       el HTML. El esquema varía por implementación
                       y está documentado en cada clase concreta.

        Returns:
            HTML completo listo para ser enviado a Canvas vía PageRepository.
        """