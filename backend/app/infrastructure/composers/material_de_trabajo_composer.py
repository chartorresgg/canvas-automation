"""
Composer de la página de Material de Trabajo.

Genera el HTML con banner institucional, botones dinámicos por unidad
para los PDFs de Material de Trabajo, botones de Storyline interactivo
y los botones estáticos de CREA y Caja de Herramientas.

Capa: Infraestructura — composers
Patrón: Strategy (implementa IPageComposer)
"""

from __future__ import annotations

from app.domain.interfaces.i_page_composer import IPageComposer

_POLI_BASE = "https://poli.instructure.com"
_CDN_BASE  = "https://imgact.poligran.edu.co/dise_Instruc_v1"

_BANNER_TRABAJO = f"{_CDN_BASE}/Bannermaterialtrabajo.png"

# Botones de PDF por unidad
_BOTON_TRABAJO: dict[int, str] = {
    1: f"{_CDN_BASE}/05MT01.png",
    2: f"{_CDN_BASE}/05MT02.png",
    3: f"{_CDN_BASE}/05MT03.png",
    4: f"{_CDN_BASE}/05MT04.png",
}

# Botones de Storyline interactivo (misma serie, por número de recurso)
_BOTON_INTERACTIVO_MT: dict[int, str] = {
    1: f"{_CDN_BASE}/05MT01.png",
    2: f"{_CDN_BASE}/05MT02.png",
    3: f"{_CDN_BASE}/05MT03.png",
    4: f"{_CDN_BASE}/05MT04.png",
}

# Botones estáticos institucionales
_BOTON_CREA         = f"{_CDN_BASE}/btn_crea.png"
_BOTON_HERRAMIENTAS = f"{_CDN_BASE}/btn_herramientas.png"
_URL_CREA           = "https://www.poli.edu.co/crea"
_URL_HERRAMIENTAS   = "https://www.poli.edu.co/crea/caja-de-herramientas"


class MaterialDeTrabajoComposer(IPageComposer):
    """
    Genera el HTML de la página de Material de Trabajo.

    Responsabilidad única: componer el banner, los botones dinámicos
    de PDFs y Storylines, y los botones estáticos institucionales.

    Contexto esperado (ctx):
        archivos   (list[dict]): PDFs → {file_id: int, unidad: int}
        storylines (list[dict]): Storylines → {page_url: str, numero: int,
                                               titulo: str}

    Orden en la página:
        Banner → PDFs por unidad → Storylines → CREA → Herramientas
    """

    def compose(self, course_id: int, ctx: dict) -> str:
        archivos:   list[dict] = ctx.get("archivos",   [])
        storylines: list[dict] = ctx.get("storylines", [])

        banner = (
            f'<p><span class="iconos">'
            f'<img id="20600" src="{_BANNER_TRABAJO}" '
            f'alt="Bannermaterialtrabajo.png" '
            f'data-api-endpoint="{_BANNER_TRABAJO}" '
            f'data-api-returntype="File" /></span></p>'
        )

        partes = [banner, "<p>"]

        # ── Botones PDF por unidad ────────────────────────────────────
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
                f'<a class="toModal" '
                f'title="Material de trabajo Unidad {unidad}" '
                f'href="{file_url}" target="_blank" rel="noopener" '
                f'data-api-endpoint="{api_url}" data-api-returntype="File">'
                f'<span class="iconos">'
                f'<img id="20594" style="width: 185px;" '
                f'src="{imagen}" alt="material de trabajo" '
                f'data-api-endpoint="{imagen}" data-api-returntype="File" />'
                f'</span></a>'
            )

        # ── Botones Storyline interactivo ─────────────────────────────
        for storyline in sorted(storylines, key=lambda x: x.get("numero", 0)):
            numero   = storyline["numero"]
            page_url = storyline["page_url"]
            titulo   = storyline.get("titulo", f"Material de Trabajo - Interactivo {numero}")
            imagen   = _BOTON_INTERACTIVO_MT.get(numero, _BOTON_INTERACTIVO_MT[1])

            url_pagina = f"{_POLI_BASE}/courses/{course_id}/pages/{page_url}"

            partes.append(
                f'<a class="toModal" title="{titulo}" '
                f'href="{url_pagina}" target="_blank" rel="noopener">'
                f'<span class="iconos">'
                f'<img id="20594" style="width: 185px;" '
                f'src="{imagen}" alt="contenido interactivo" '
                f'data-api-endpoint="{imagen}" data-api-returntype="File" />'
                f'</span></a>'
            )

        # ── Botón estático CREA ───────────────────────────────────────
        partes.append(
            f'<a title="CREA" href="{_URL_CREA}" '
            f'target="_blank" rel="noopener">'
            f'<span class="iconos">'
            f'<img id="20594" style="width: 185px;" '
            f'src="{_BOTON_CREA}" alt="CREA" '
            f'data-api-endpoint="{_BOTON_CREA}" data-api-returntype="File" />'
            f'</span></a>'
        )

        # ── Botón estático Caja de Herramientas ───────────────────────
        partes.append(
            f'<a title="Caja de Herramientas" href="{_URL_HERRAMIENTAS}" '
            f'target="_blank" rel="noopener">'
            f'<span class="iconos">'
            f'<img id="20594" style="width: 185px;" '
            f'src="{_BOTON_HERRAMIENTAS}" alt="Caja de Herramientas" '
            f'data-api-endpoint="{_BOTON_HERRAMIENTAS}" '
            f'data-api-returntype="File" />'
            f'</span></a>'
        )

        partes.append("</p>")
        return "\n".join(partes)