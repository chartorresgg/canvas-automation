"""
Composer de la página de Material de Trabajo.

Genera el HTML con banner institucional, botones dinámicos por unidad
para los PDFs de Material de Trabajo, y los botones estáticos
de CREA y Caja de Herramientas.

Capa: Infraestructura — composers
Patrón: Strategy (implementa IPageComposer)
"""

from __future__ import annotations

from app.domain.interfaces.i_page_composer import IPageComposer

_POLI_BASE = "https://poli.instructure.com"
_CDN_BASE  = "https://imgact.poligran.edu.co/dise_Instruc_v1"

_BANNER_TRABAJO = f"{_CDN_BASE}/Bannermaterialtrabajo.png"

# Botones dinámicos por unidad
_BOTON_TRABAJO: dict[int, str] = {
    1: f"{_CDN_BASE}/05MT01.png",
    2: f"{_CDN_BASE}/05MT02.png",
    3: f"{_CDN_BASE}/05MT03.png",
    4: f"{_CDN_BASE}/05MT04.png",
}

# Botones estáticos institucionales
_BOTON_CREA       = f"{_CDN_BASE}/btn_crea.png"
_BOTON_HERRAMIENTAS = f"{_CDN_BASE}/btn_herramientas.png"
_URL_CREA         = "https://www.poli.edu.co/crea"
_URL_HERRAMIENTAS = "https://www.poli.edu.co/crea/caja-de-herramientas"


class MaterialDeTrabajoComposer(IPageComposer):
    """
    Genera el HTML de la página de Material de Trabajo.

    Responsabilidad única: componer el banner, los botones dinámicos
    por unidad y los botones estáticos de CREA y Caja de Herramientas.

    Contexto esperado (ctx):
        archivos (list[dict]): Cada dict con {file_id: int, unidad: int}.
                               Ordenados por unidad ascendente.
    """

    def compose(self, course_id: int, ctx: dict) -> str:
        archivos: list[dict] = ctx.get("archivos", [])

        banner = (
            f'<p><span class="iconos">'
            f'<img id="20600" src="{_BANNER_TRABAJO}" '
            f'alt="Bannermaterialtrabajo.png" '
            f'data-api-endpoint="{_BANNER_TRABAJO}" '
            f'data-api-returntype="File" /></span></p>'
        )

        partes = [banner, "<p>"]

        # Botones dinámicos — uno por archivo de Material de trabajo
        for item in sorted(archivos, key=lambda x: x.get("unidad", 0)):
            file_id = item["file_id"]
            unidad  = item.get("unidad", 1)
            imagen  = _BOTON_TRABAJO.get(unidad, _BOTON_TRABAJO[1])

            file_url = (
                f"{_POLI_BASE}/courses/{course_id}"
                f"/files/{file_id}?wrap=1"
            )
            api_url = (
                f"{_POLI_BASE}/api/v1"
                f"/courses/{course_id}/files/{file_id}"
            )

            partes.append(
                f'<a class="toModal" title="Material de trabajo Unidad {unidad}" '
                f'href="{file_url}" target="_blank" rel="noopener" '
                f'data-api-endpoint="{api_url}" data-api-returntype="File">'
                f'<span class="iconos">'
                f'<img id="20594" style="width: 185px;" '
                f'src="{imagen}" alt="material de trabajo" '
                f'data-api-endpoint="{imagen}" data-api-returntype="File" />'
                f'</span></a>'
            )

        # Botones estáticos — CREA
        partes.append(
            f'<a title="CREA" href="{_URL_CREA}" '
            f'target="_blank" rel="noopener" '
            f'data-api-endpoint="{_URL_CREA}" data-api-returntype="File">'
            f'<span class="iconos">'
            f'<img id="20594" style="width: 185px;" '
            f'src="{_BOTON_CREA}" alt="CREA" '
            f'data-api-endpoint="{_BOTON_CREA}" data-api-returntype="File" />'
            f'</span></a>'
        )

        # Botón estático — Caja de Herramientas
        partes.append(
            f'<a title="Caja de Herramientas" href="{_URL_HERRAMIENTAS}" '
            f'target="_blank" rel="noopener" '
            f'data-api-endpoint="{_URL_HERRAMIENTAS}" data-api-returntype="File">'
            f'<span class="iconos">'
            f'<img id="20594" style="width: 185px;" '
            f'src="{_BOTON_HERRAMIENTAS}" alt="Caja de Herramientas" '
            f'data-api-endpoint="{_BOTON_HERRAMIENTAS}" data-api-returntype="File" />'
            f'</span></a>'
        )

        partes.append("</p>")
        return "\n".join(partes)