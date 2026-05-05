"""
Composer de páginas de Material Fundamental por unidad.

Genera el HTML complejo de cada página de unidad: banner institucional,
botones de lecturas, PDFs de material fundamental, videos de introducción,
contenido interactivo SCORM, podcasts y actividades evaluativas.

Capa: Infraestructura — composers
Patrón: Strategy (implementa IPageComposer)
"""

from __future__ import annotations

from app.domain.interfaces.i_page_composer import IPageComposer

_POLI_BASE = "https://poli.instructure.com"
_CDN_BASE  = "https://imgact.poligran.edu.co/dise_Instruc_v1"

# ── Códigos de imagen institucionales ────────────────────────────────────────
_BANNER_MAT_FUND = f"{_CDN_BASE}/cabezote_mat_fund.png"

# Video de introducción por unidad
_VIDEO_INTRO: dict[int, str] = {
    1: f"{_CDN_BASE}/012VINT01.png",
    2: f"{_CDN_BASE}/012VINT02.png",
    3: f"{_CDN_BASE}/012VINT03.png",
    4: f"{_CDN_BASE}/012VINT04.png",
}

# Lecturas fundamentales por secuencia (hasta 3 lecturas por unidad)
_LECTURA_FUNDAMENTAL: dict[int, str] = {
    1: f"{_CDN_BASE}/02LF01.png",
    2: f"{_CDN_BASE}/02LF02.png",
    3: f"{_CDN_BASE}/02LF03.png",
}

# PDF de Material Fundamental (cartilla, infografía, etc.)
_MATERIAL_FUNDAMENTAL_PDF = f"{_CDN_BASE}/013INF00.png"

# Actividades formativas por unidad
_ACTIVIDAD_FORMATIVA: dict[int, str] = {
    1: f"{_CDN_BASE}/04AF01.png",
    2: f"{_CDN_BASE}/04AF02.png",
    3: f"{_CDN_BASE}/04AF03.png",
    4: f"{_CDN_BASE}/04AF04.png",
}

# Actividades sumativas (solo U2 y U4 según la institución)
_ACTIVIDAD_SUMATIVA: dict[int, str] = {
    2: f"{_CDN_BASE}/03AE01.png",
    4: f"{_CDN_BASE}/03AE02.png",
}

# Contenido interactivo SCORM (hasta 4 por unidad)
_CONTENIDO_INTERACTIVO: dict[int, str] = {
    1: f"{_CDN_BASE}/022ri01.png",
    2: f"{_CDN_BASE}/022ri02.png",
    3: f"{_CDN_BASE}/022ri03.png",
    4: f"{_CDN_BASE}/022ri04.png",
}


class MaterialFundamentalComposer(IPageComposer):
    """
    Genera el HTML de la página de Material Fundamental para una unidad.

    Responsabilidad única: componer el HTML con todos los botones y
    recursos de una unidad según los archivos subidos a Canvas y los
    datos del Guion Excel.

    Contexto esperado (ctx):
        unidad          (int):        Número de unidad (1-4).
        lecturas        (list[dict]): Cada dict: {file_id, secuencia}.
        mat_fund_pdfs   (list[dict]): Cada dict: {file_id}.
        actividades     (list[dict]): Cada dict: {file_id, tipo}
                                      tipo: "formativa" | "sumativa".
        paginas_interactivas (list[dict]): Cada dict:
                              {page_url, numero, es_enumerado}.
        video_intro_url (str | None): URL Vimeo del video de introducción.
        podcast_url     (str | None): URL SoundCloud del podcast.
        vimeo_url       (str | None): URL Vimeo de material fundamental.

    Orden de botones en la página (convención institucional):
        Banner → Video intro → Lecturas → Contenido interactivo
        → Podcast → Vimeo content → Material PDF → Actividades
    """

    def compose(self, course_id: int, ctx: dict) -> str:
        """
        Genera el HTML completo de la página de material fundamental.

        Args:
            course_id: ID del curso Canvas.
            ctx:       Ver esquema en el docstring de la clase.

        Returns:
            HTML completo con banner y todos los botones de la unidad.
        """
        unidad: int = ctx["unidad"]

        partes: list[str] = [
            self._banner(),
            "<p>",
        ]

        # 1. Video de introducción (Vimeo)
        video_intro_url: str | None = ctx.get("video_intro_url")
        if video_intro_url:
            partes.append(
                self._boton_video_externo(
                    url=video_intro_url,
                    titulo=f"Video de introducción Unidad {unidad}",
                    imagen_url=_VIDEO_INTRO.get(unidad, _VIDEO_INTRO[1]),
                )
            )

        # 2. Lecturas fundamentales (PDFs)
        for lectura in ctx.get("lecturas", []):
            secuencia = lectura.get("secuencia", 1)
            imagen = _LECTURA_FUNDAMENTAL.get(secuencia, _LECTURA_FUNDAMENTAL[1])
            partes.append(
                self._boton_archivo(
                    course_id=course_id,
                    file_id=lectura["file_id"],
                    titulo=f"Lectura Fundamental {secuencia} — Unidad {unidad}",
                    imagen_url=imagen,
                )
            )

        # 3. Contenido interactivo SCORM
        for pagina in ctx.get("paginas_interactivas", []):
            numero = pagina.get("numero", 1)
            imagen = _CONTENIDO_INTERACTIVO.get(numero, _CONTENIDO_INTERACTIVO[1])
            page_url = pagina["page_url"]
            partes.append(
                self._boton_pagina_canvas(
                    course_id=course_id,
                    page_url=page_url,
                    titulo=f"Contenido Interactivo {numero} — Unidad {unidad}",
                    imagen_url=imagen,
                )
            )

        # 4. Podcast (SoundCloud embed)
        podcast_url: str | None = ctx.get("podcast_url")
        if podcast_url:
            partes.append(self._embed_podcast(podcast_url))

        # 5. Video de material fundamental (Vimeo — diferente al intro)
        vimeo_url: str | None = ctx.get("vimeo_url")
        if vimeo_url:
            partes.append(
                self._embed_vimeo(
                    vimeo_url=vimeo_url,
                    titulo=f"Video Material Fundamental — Unidad {unidad}",
                )
            )

        # 6. PDFs de Material Fundamental (cartillas, infografías)
        for mat in ctx.get("mat_fund_pdfs", []):
            partes.append(
                self._boton_archivo(
                    course_id=course_id,
                    file_id=mat["file_id"],
                    titulo=f"Material Fundamental — Unidad {unidad}",
                    imagen_url=_MATERIAL_FUNDAMENTAL_PDF,
                )
            )

        # 7. Actividades evaluativas
        for actividad in ctx.get("actividades", []):
            tipo    = actividad.get("tipo", "formativa")
            file_id = actividad["file_id"]
            imagen  = self._imagen_actividad(tipo, unidad)
            titulo  = (
                f"Actividad Formativa — Unidad {unidad}"
                if tipo == "formativa"
                else f"Actividad Sumativa — Unidad {unidad}"
            )
            partes.append(
                self._boton_archivo(
                    course_id=course_id,
                    file_id=file_id,
                    titulo=titulo,
                    imagen_url=imagen,
                )
            )

        partes.append("</p>")
        return "\n".join(partes)

    # ──────────────────────────────────────────────────────────────
    # Privados — bloques HTML reutilizables
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _banner() -> str:
        """Banner superior institucional de Material Fundamental."""
        url = f"{_CDN_BASE}/cabezote_mat_fund.png"
        return (
            f'<p><img id="22169" role="banner de página" '
            f'src="{url}" '
            f'alt="" '
            f'data-api-endpoint="{url}" '
            f'data-api-returntype="File" /></p>'
        )

    @staticmethod
    def _boton_archivo(
        course_id: int,
        file_id:   int,
        titulo:    str,
        imagen_url: str,
    ) -> str:
        """
        Botón que abre un archivo del curso en modal (toModal).
        Usado para PDFs de lecturas, material fundamental y actividades.
        """
        file_url  = f"{_POLI_BASE}/courses/{course_id}/files/{file_id}?wrap=1"
        api_url   = (
            f"{_POLI_BASE}/api/v1/courses/{course_id}/files/{file_id}"
        )
        return (
            f'<a class="toModal" title="{titulo}" '
            f'href="{file_url}" '
            f'target="_blank" rel="noopener" '
            f'data-api-endpoint="{api_url}" '
            f'data-api-returntype="File">'
            f'<span class="iconos">'
            f'<img id="20594" style="width: 185px;" '
            f'src="{imagen_url}" '
            f'alt="{titulo}" '
            f'data-api-endpoint="{imagen_url}" '
            f'data-api-returntype="File" /></span></a>'
        )

    @staticmethod
    def _boton_video_externo(
        url:        str,
        titulo:     str,
        imagen_url: str,
    ) -> str:
        """
        Botón que abre una URL externa (Vimeo) en una nueva pestaña.
        Usado para videos de introducción de unidad.
        """
        return (
            f'<a class="toModal" title="{titulo}" '
            f'href="{url}" '
            f'target="_blank" rel="noopener">'
            f'<span class="iconos">'
            f'<img id="20605" style="width: 190px;" '
            f'src="{imagen_url}" '
            f'alt="video" '
            f'data-api-endpoint="{imagen_url}" '
            f'data-api-returntype="File" /></span></a>'
        )

    @staticmethod
    def _boton_pagina_canvas(
        course_id: int,
        page_url:  str,
        titulo:    str,
        imagen_url: str,
    ) -> str:
        """
        Botón que navega a una página wiki interna del curso.
        Usado para contenido interactivo SCORM.
        """
        url = f"{_POLI_BASE}/courses/{course_id}/pages/{page_url}"
        return (
            f'<a class="toModal" title="{titulo}" '
            f'href="{url}" '
            f'target="_blank" rel="noopener">'
            f'<span class="iconos">'
            f'<img id="20594" style="width: 185px;" '
            f'src="{imagen_url}" '
            f'alt="contenido interactivo" '
            f'data-api-endpoint="{imagen_url}" '
            f'data-api-returntype="File" /></span></a>'
        )

    @staticmethod
    def _embed_vimeo(vimeo_url: str, titulo: str) -> str:
        """
        Botón que abre el video Vimeo de material fundamental en nueva pestaña.
        La imagen es siempre 06MFV00.png independiente de la unidad.
        """
        imagen_url = f"{_CDN_BASE}/06MFV00.png"

        return (
            f'<a class="toModal" title="Vídeo" '
            f'href="{vimeo_url}" '
            f'target="_blank" rel="noopener">'
            f'<span class="iconos">'
            f'<img id="20605" style="width: 190px;" '
            f'src="{imagen_url}" '
            f'alt="video" '
            f'data-api-endpoint="{imagen_url}" '
            f'data-api-returntype="File" />'
            f'</span></a>'
        )

    @staticmethod
    def _embed_podcast(soundcloud_url: str) -> str:
        """
        Botón que abre el podcast de SoundCloud en una nueva pestaña.
        La imagen es siempre 07MFP00.png independiente de la unidad.
        """
        imagen_url = f"{_CDN_BASE}/07MFP00.png"

        return (
            f'<a class="toModal" title="Podcast" '
            f'href="{soundcloud_url}" '
            f'target="_blank" rel="noopener">'
            f'<span class="iconos">'
            f'<img id="20594" style="width: 185px;" '
            f'src="{imagen_url}" '
            f'alt="podcast" '
            f'data-api-endpoint="{imagen_url}" '
            f'data-api-returntype="File" />'
            f'</span></a>'
        )

    @staticmethod
    def _imagen_actividad(tipo: str, unidad: int) -> str:
        """
        Retorna la URL de imagen institucional para el botón de actividad.
        Formativa: imagen por unidad. Sumativa: imagen específica (U2/U4).
        """
        if tipo == "formativa":
            return _ACTIVIDAD_FORMATIVA.get(unidad, _ACTIVIDAD_FORMATIVA[1])
        # sumativa
        return _ACTIVIDAD_SUMATIVA.get(unidad, _ACTIVIDAD_SUMATIVA[2])