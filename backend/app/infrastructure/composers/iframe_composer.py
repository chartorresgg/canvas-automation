"""
Composer de páginas que incrustan un archivo HTML mediante iframe.

Usado para las páginas de Presentación y Cierre del aula virtual,
donde el contenido es un archivo HTML subido al curso en Canvas.

Capa: Infraestructura — composers
Patrón: Strategy (implementa IPageComposer)
"""

from __future__ import annotations

from app.domain.interfaces.i_page_composer import IPageComposer

_BASE_URL = "https://poli.instructure.com"


class IframeComposer(IPageComposer):
    """
    Genera HTML con un iframe que apunta a un archivo del curso Canvas.

    Responsabilidad única: generar el HTML de incrustación mediante
    iframe para páginas de tipo presentación o cierre.

    Contexto esperado (ctx):
        file_id (int): ID del archivo HTML en Canvas.

    Páginas donde se usa:
        - "inicio-presentacion"       → 1. Presentación/index.html
        - "cierre-retroalimentacion"  → 5. Cierre/index.html
    """

    def compose(self, course_id: int, ctx: dict) -> str:
        """
        Genera HTML con iframe al 100% de ancho y altura de viewport.

        El iframe apunta a la URL de descarga del archivo en Canvas,
        que Canvas redirige al visor integrado de archivos HTML.

        Args:
            course_id: ID del curso Canvas.
            ctx:       Debe contener 'file_id' (int).

        Returns:
            HTML con iframe configurado para visualización inline.

        Raises:
            KeyError: Si 'file_id' no está en ctx.
        """
        file_id = ctx["file_id"]

        download_url = (
            f"{_BASE_URL}/courses/{course_id}"
            f"/files/{file_id}/download"
        )
        api_endpoint = (
            f"{_BASE_URL}/api/v1"
            f"/courses/{course_id}/files/{file_id}"
        )

        return (
            f'<p>\n'
            f'    <iframe\n'
            f'        style="width: 100%; height: 100vh; border: none;"\n'
            f'        src="{download_url}"\n'
            f'        data-api-endpoint="{api_endpoint}"\n'
            f'        data-api-returntype="File">\n'
            f'    </iframe>\n'
            f'</p>'
        )