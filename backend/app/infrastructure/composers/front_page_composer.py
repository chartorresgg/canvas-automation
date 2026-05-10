"""
Composer de la página principal 'front-del-curso'.
Versión corregida: template sin saltos de línea dentro de etiquetas <a>,
y regex ajustado a la estructura real del HTML institucional.
"""

from __future__ import annotations
import re
from app.domain.interfaces.i_page_composer import IPageComposer


class FrontPageComposer(IPageComposer):

    def compose(self, course_id: int, ctx: dict) -> str:
        html = self._template_base()

        # Reemplazar course_id de referencia (81673) por el real
        html = html.replace("courses/81673", f"courses/{course_id}")
        html = html.replace("/api/v1/courses/81673", f"/api/v1/courses/{course_id}")

        # Nombre del curso
        # Nombre del curso — solo la parte después del '/' si existe
        nombre_completo = ctx.get("course_name", "")
        nombre_display  = self._extraer_nombre_display(nombre_completo) if nombre_completo else ""
        if nombre_display:
            html = html.replace("INSERTAR NOMBRE DEL CURSO", nombre_display)

        # URL del video inicial — reemplaza el placeholder del iframe
        video_url = ctx.get("video_url", "")
        if video_url:
            html = html.replace(
                'src="INSERTAR URL DEL VÍDEO"',
                f'src="{video_url}"',
            )

        # Párrafos por módulo
        reemplazos = {
            "INICIO":   ctx.get("texto_inicio",  ""),
            "UNIDAD 1": ctx.get("texto_u1",      ""),
            "UNIDAD 2": ctx.get("texto_u2",      ""),
            "UNIDAD 3": ctx.get("texto_u3",      ""),
            "UNIDAD 4": ctx.get("texto_u4",      ""),
            "CIERRE":   ctx.get("texto_cierre",  ""),
        }
        for modulo, texto in reemplazos.items():
            if texto:
                html = self._reemplazar_modulo(html, modulo, texto)

        return html
    
    @staticmethod
    def _extraer_nombre_display(course_name: str) -> str:
        """
        Extrae el nombre visible del curso para el front.

        Si el nombre contiene '/', retorna solo la parte después del '/'.
        Ejemplo: "SEGUNDO BLOQUE/ANÁLISIS DE CASOS" → "ANÁLISIS DE CASOS"
        Si no contiene '/', retorna el nombre completo.
        """
        if "/" in course_name:
            return course_name.split("/", 1)[1].strip()
        return course_name.strip()

    @staticmethod
    def _reemplazar_modulo(html: str, modulo: str, nuevo_texto: str) -> str:
        """
        Reemplaza el contenido del div.modulo-desc del módulo indicado.

        Usa una función lambda como reemplazo (en lugar de un string)
        para evitar que Python interprete caracteres como \\1, \\g<N>
        en nuevo_texto como referencias a grupos de captura, lo que
        provoca IndexError cuando el texto viene de Excel.
        """
        pattern = (
            rf'(<p class="modulo-title-2">\s*{re.escape(modulo)}\s*</p>'
            rf'[\s\S]*?<div class="modulo-desc">)'
            rf'([\s\S]*?)'
            rf'(</div>)'
        )
        return re.sub(
            pattern,
            lambda m: m.group(1) + nuevo_texto + m.group(3),
            html,
            flags=re.IGNORECASE,
        )

    @staticmethod
    def _template_base() -> str:
        """
        Template institucional real del Politécnico Grancolombiano.

        IMPORTANTE: Todos los atributos de cada <a> van en UNA SOLA LÍNEA.
        Canvas HTML sanitizer elimina etiquetas <a> que tienen saltos de
        línea entre el <a y sus atributos.
        """
        return (
            '<div id="plantilla_2023">'
            '<div class="POLI_contenedorGeneral">'
            '<div class="text-right">'
            '<a class="btn POLI-btn-close-right-side-wrapper" title="Ocultar menú derecho">'
            '<img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-chevron-right-blanco.png" alt="close sidebar rigth" />'
            '</a></div></div>'
            '<div class="POLI_contenedorGeneral">'
            '<div class="POLI_banner_header">'
            '<div class="col span_6_of_8">'
            '<h2 class="course_title">INSERTAR NOMBRE DEL CURSO</h2>'
            '</div>'
            '<div class="col span_2_of_8">'
            '<div class="POLI_content_icons">'
            '<a class="toModal" href="https://poli.instructure.com/courses/81673/external_tools/38" data-api-endpoint="/api/v1/courses/81673/external_tools/38" data-api-returntype="[Quiz]"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-chat-blanco.svg" alt="Chat del curso" /><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-chat-azulclaro.svg" alt="Chat del curso" /></a> '
            '<a class="toModal" href="https://poli.instructure.com/conversations" data-api-endpoint="https://poli.test.instructure.com/api/v1/conversations" data-api-returntype="[Quiz]"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-correo-blanco.svg" alt="Mensajería del curso" /><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-correo-azulclaro.svg" alt="Mensajería del curso" /></a> '
            '<a class="POLI-btn-menu-secciones"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-menu-blanco.svg" alt="Abrir menú secciones" /><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-menu-azulclaro.svg" alt="Cerrar menú secciones" /></a>'
            '</div></div></div></div>'
            '<div class="POLI_contenedorGeneral">'
            '<div class="POLI_content_course bg-course">'
            '<div class="div-unidades col span_4_of_8" style="margin: auto; padding: 0 20px;">'
            '<div id="content-unidades"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon_hexagonos.svg" alt="icono unidad" /></div>'
            '<div id="enlaces-unidades">'
            '<a class="POLI-btn-menu-secciones btn-close-menu-secciones btn">X</a>'
            '<h1 class="title-menu">MENÚ</h1>'
            # ── hexagon_0: INICIO ──
            '<div id="hexagon_0" class="subitems-content">'
            '<div class="modulo-header"><img class="icon-modulo" src="https://canvas-rsc.ilumno.com/poli/prod/img/icon_unidad_0.svg" alt="icono" />'
            '<div class="modulo-title subitems-btn"><br /><p class="modulo-title-2">INICIO</p></div></div>'
            '<div class="modulo-desc">Bienvenido al módulo.</div>'
            '<div class="modulo-buttons subitems-links">'
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/inicio-presentacion" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/inicio-presentacion" data-api-returntype="Page">PRESENTACIÓN</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/assignments" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/assignments" data-api-returntype="[Assignment]">EVALUACIÓN DIAGNÓSTICA</a>'
            '</div></div>'
            # ── hexagon_1: UNIDAD 1 ──
            '<div id="hexagon_1" class="subitems-content">'
            '<div class="modulo-header"><img class="icon-modulo" src="https://canvas-rsc.ilumno.com/poli/prod/img/icon_unidad_1.svg" alt="icono unidad" />'
            '<div class="modulo-title subitems-btn"><br /><p class="modulo-title-2">UNIDAD 1</p></div></div>'
            '<div class="modulo-desc">Introducción a la unidad 1.</div>'
            '<div class="modulo-buttons subitems-links">'
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/unidad-1-material-fundamental" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/unidad-1-material-fundamental" data-api-returntype="Page">MATERIAL FUNDAMENTAL</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/assignments" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/assignments" data-api-returntype="[Assignment]">ACTIVIDADES</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/unidad-1-complementario" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/unidad-1-complementario" data-api-returntype="Page">COMPLEMENTOS</a>'
            '</div></div>'
            # ── hexagon_2: UNIDAD 2 ──
            '<div id="hexagon_2" class="subitems-content">'
            '<div class="modulo-header"><img class="icon-modulo" src="https://canvas-rsc.ilumno.com/poli/prod/img/icon_unidad_2.svg" alt="icono unidad" />'
            '<div class="modulo-title subitems-btn"><br /><p class="modulo-title-2">UNIDAD 2</p></div></div>'
            '<div class="modulo-desc">Introducción a la unidad 2.</div>'
            '<div class="modulo-buttons subitems-links">'
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/unidad-2-material-fundamental" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/unidad-2-material-fundamental" data-api-returntype="Page">MATERIAL FUNDAMENTAL</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/assignments" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/assignments" data-api-returntype="[Assignment]">ACTIVIDADES</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/unidad-2-complementario" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/unidad-2-complementario" data-api-returntype="Page">COMPLEMENTOS</a>'
            '</div></div>'
            # ── hexagon_3: UNIDAD 3 ──
            '<div id="hexagon_3" class="subitems-content">'
            '<div class="modulo-header"><img class="icon-modulo" src="https://canvas-rsc.ilumno.com/poli/prod/img/icon_unidad_3.svg" alt="icono unidad" />'
            '<div class="modulo-title subitems-btn"><br /><p class="modulo-title-2">UNIDAD 3</p></div></div>'
            '<div class="modulo-desc">Introducción a la unidad 3.</div>'
            '<div class="modulo-buttons subitems-links">'
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/unidad-3-material-fundamental" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/unidad-3-material-fundamental" data-api-returntype="Page">MATERIAL FUNDAMENTAL</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/assignments" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/assignments" data-api-returntype="[Assignment]">ACTIVIDADES</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/unidad-3-complementario" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/unidad-3-complementario" data-api-returntype="Page">COMPLEMENTOS</a>'
            '</div></div>'
            # ── hexagon_4: UNIDAD 4 ──
            '<div id="hexagon_4" class="subitems-content">'
            '<div class="modulo-header"><img class="icon-modulo" src="https://canvas-rsc.ilumno.com/poli/prod/img/icon_unidad_4.svg" alt="icono unidad" />'
            '<div class="modulo-title subitems-btn"><br /><p class="modulo-title-2">UNIDAD 4</p></div></div>'
            '<div class="modulo-desc">Introducción a la unidad 4.</div>'
            '<div class="modulo-buttons subitems-links">'
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/unidad-4-material-fundamental" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/unidad-4-material-fundamental" data-api-returntype="Page">MATERIAL FUNDAMENTAL</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/assignments" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/assignments" data-api-returntype="[Assignment]">ACTIVIDADES</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/unidad-4-complementario" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/unidad-4-complementario" data-api-returntype="Page">COMPLEMENTOS</a>'
            '</div></div>'
            # ── hexagon_5: CIERRE ──
            '<div id="hexagon_5" class="subitems-content">'
            '<div class="modulo-header"><img class="icon-modulo" src="https://canvas-rsc.ilumno.com/poli/prod/img/icon_unidad_5.svg" alt="icono unidad" />'
            '<div class="modulo-title subitems-btn"><br /><p class="modulo-title-2">CIERRE</p></div></div>'
            '<div class="modulo-desc">Cierre del módulo.</div>'
            '<div class="modulo-buttons subitems-links">'
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/pages/cierre-retroalimentacion" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/cierre-retroalimentacion" data-api-returntype="Page">RETROALIMENTACIÓN</a> '
            '<a class="btn btn-small btn-verde-2023 toModal" href="https://poli.instructure.com/courses/81673/assignments" data-dismiss="modal" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/assignments" data-api-returntype="[Assignment]">AUTOEVALUACIÓN</a>'
            '</div></div>'
            '</div></div>'
            # ── Columna del video ──
            '<div class="div-video col span_4_of_8" style="margin: auto;">'
            '<div class="POLI_home_content_iframe">'
            '<iframe title="vimeo-player" src="INSERTAR URL DEL VÍDEO" width="100%" height="100%" loading="lazy" allowfullscreen="allowfullscreen"></iframe>'
            '</div></div>'
            '</div></div>'
            # ── Footer ──
            '<div class="POLI_contenedorGeneral"><div class="POLI_footer"><ul>'
            '<li class="icono-footer-accion bg-verde-oscuro"><a class="toModal" href="https://poli.instructure.com/courses/81673/pages/material-de-trabajo" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/pages/material-de-trabajo" data-api-returntype="Page"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-material-verde.svg" alt="Material de Trabajo" /><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-material-blanco.svg" alt="Material de Trabajo" /><span class="texto"> MATERIAL <br />DE TRABAJO </span></a></li>'
            '<li class="icono-footer-accion"><a class="toModal" href="https://poli.instructure.com/courses/81673/announcements"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-anuncios-verde.svg" alt="Anuncios" /><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-anuncios-blanco.svg" alt="Anuncios" /><span class="texto"> ANUNCIOS </span></a></li>'
            '<li class="icono-footer-accion"><a class="toModal" href="https://poli.instructure.com/courses/81673/discussion_topics" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/discussion_topics" data-api-returntype="[Discussion]"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-foros-verde.svg" alt="Foros de discusión" /><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-foros-blanco.svg" alt="Foros de discusión" /><span class="texto"> FOROS DE <br />DISCUSIÓN </span></a></li>'
            '<li class="icono-footer-accion"><a class="toModal" href="https://poli.instructure.com/courses/81673/external_tools/3036"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-encuentros-verde.svg" alt="Encuentros Sincrónicos" /><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-encuentros-blanco.svg" alt="Encuentros Sincrónicos" /><span class="texto"> ENCUENTROS <br />SINCRÓNICOS </span></a></li>'
            '<li class="icono-footer-accion"><a class="toModal icono-footer-accion" title="Actividades Evaluativas" href="https://poli.instructure.com/courses/81673/assignments" data-api-endpoint="https://poli.instructure.com/api/v1/courses/81673/assignments" data-api-returntype="[Assignment]"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-actividades-verde.svg" alt="Actividades Evaluativas" /><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-actividades-blanco.svg" alt="Actividades Evaluativas" /><span class="texto"> ACTIVIDADES <br />EVALUATIVAS </span></a></li>'
            '<li class="icono-footer-accion"><a class="toModal" href="https://poli.instructure.com/courses/81673/grades"><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-calificaciones-verde.svg" alt="Calificaciones del Módulo" /><img src="https://canvas-rsc.ilumno.com/poli/prod/img/icon-calificaciones-blanco.svg" alt="Calificaciones del Módulo" /><span class="texto"> CALIFICACIONES <br />DEL MÓDULO </span></a></li>'
            '<li class="logo"><a title="Ir a la universidad" href="https://www.poli.edu.co/content/estudiantes" target="_blank" rel="noopener"><img class="logo_poli" src="https://canvas-rsc.ilumno.com/poli/prod/img/logo-poli-blanco.svg" alt="Logo Poli" /></a></li>'
            '</ul></div></div>'
            '</div>'
        )