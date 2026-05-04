"""
Composer de páginas de Material Complementario por unidad.

Genera el HTML con el banner institucional y el botón de descarga
del PDF de material complementario correspondiente a la unidad.

Capa: Infraestructura — composers
Patrón: Strategy (implementa IPageComposer)
"""

from __future__ import annotations

from app.domain.interfaces.i_page_composer import IPageComposer

_POLI_BASE = "https://poli.instructure.com"
_CDN_BASE  = "https://imgact.poligran.edu.co/dise_Instruc_v1"

_BANNER_COMPLEMENTO = f"{_CDN_BASE}/Bannermaterialcomplementario.png"

# Botones de lectura complementaria por unidad
_BOTON_COMPLEMENTO: dict[int, str] = {
    1: f"{_CDN_BASE}/00LC01.png",
    2: f"{_CDN_BASE}/00LC02.png",
    3: f"{_CDN_BASE}/00LC03.png",
    4: f"{_CDN_BASE}/00LC04.png",
}


class ComplementaryPageComposer(IPageComposer):
    """
    Genera el HTML de la página de Material Complementario por unidad.

    Responsabilidad única: componer el HTML con el banner institucional
    y el botón de acceso al PDF de lecturas complementarias.

    Contexto esperado (ctx):
        unidad   (int): Número de unidad (1-4).
        file_id  (int): ID del PDF de complementos en Canvas.
        filename (str): Nombre del archivo (para el título del botón).
    """

    def compose(self, course_id: int, ctx: dict) -> str:
        """
        Genera HTML con banner + botón de PDF complementario.

        Args:
            course_id: ID del curso Canvas.
            ctx:       Debe contener 'unidad', 'file_id', 'filename'.

        Returns:
            HTML completo de la página de material complementario.
        """
        unidad:   int = ctx["unidad"]
        file_id:  int = ctx["file_id"]
        filename: str = ctx.get("filename", f"U{unidad}_Complemento.pdf")

        imagen_url = _BOTON_COMPLEMENTO.get(unidad, _BOTON_COMPLEMENTO[1])

        file_url = (
            f"{_POLI_BASE}/courses/{course_id}"
            f"/files/{file_id}?wrap=1"
        )
        api_url = (
            f"{_POLI_BASE}/api/v1"
            f"/courses/{course_id}/files/{file_id}"
        )

        banner = (
            f'<p><img id="22169" role="presentation" '
            f'src="{_BANNER_COMPLEMENTO}" '
            f'alt="" '
            f'data-api-endpoint="{_BANNER_COMPLEMENTO}" '
            f'data-api-returntype="File" /></p>'
        )

        boton = (
            f'<p>'
            f'<a class="toModal" title="Lectura Complementaria" '
            f'href="{file_url}" '
            f'target="_blank" rel="noopener" '
            f'data-api-endpoint="{api_url}" '
            f'data-api-returntype="File">'
            f'<span class="iconos">'
            f'<img id="20594" style="width: 185px;" '
            f'src="{imagen_url}" '
            f'alt="lectura" '
            f'data-api-endpoint="{imagen_url}" '
            f'data-api-returntype="File" />'
            f'</span></a>'
            f'</p>'
        )

        return f"{banner}\n{boton}"