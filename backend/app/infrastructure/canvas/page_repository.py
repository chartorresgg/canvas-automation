"""
Repositorio de operaciones sobre páginas y actividades en Canvas LMS.

Gestiona la actualización de páginas wiki, creación de páginas nuevas
y vinculación de PDFs a actividades con vista previa en línea.

Capa: Infraestructura
Patrón: Repository
Colaboradores: CanvasHttpClient
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.infrastructure.canvas.http_client import (
    CanvasHttpClient,
    CanvasNotFoundError,
)

logger = logging.getLogger(__name__)

# URL base institucional — constante de infraestructura
_BASE_URL_POLI = "https://poli.instructure.com"


# ──────────────────────────────────────────────────────────────────────────────
# Value Objects de resultado
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PageInfo:
    """Información de una página wiki de Canvas."""
    url:        str    # slug de la página (ej. "front-del-curso")
    title:      str    # título visible en Canvas
    course_id:  int
    edit_url:   str    # URL de edición en Canvas

    @classmethod
    def desde_respuesta_canvas(
        cls, data: dict, course_id: int
    ) -> PageInfo:
        slug = data.get("url", "")
        return cls(
            url=slug,
            title=data.get("title", ""),
            course_id=course_id,
            edit_url=(
                f"{_BASE_URL_POLI}/courses/{course_id}"
                f"/pages/{slug}/edit"
            ),
        )


@dataclass(frozen=True)
class AssignmentLinkResult:
    """Resultado de vincular un PDF a una actividad."""
    assignment_id:   int
    assignment_name: str
    file_id:         int
    vinculado:       bool
    motivo_fallo:    str | None = None


# ──────────────────────────────────────────────────────────────────────────────
# Repositorio principal
# ──────────────────────────────────────────────────────────────────────────────

class PageRepository:
    """
    Repositorio de operaciones sobre páginas wiki y actividades Canvas.

    Responsabilidad única (SRP): gestionar la creación y actualización
    de contenido HTML en Canvas — páginas wiki y descripciones de
    actividades. No conoce cómo se genera el HTML (eso es tarea de los
    Composers).

    Colaboradores:
        CanvasHttpClient — único medio de comunicación HTTP.
    """

    def __init__(self, http: CanvasHttpClient) -> None:
        self._http = http

    # ──────────────────────────────────────────────────────────────
    # Páginas wiki
    # ──────────────────────────────────────────────────────────────

    async def update_page(
        self,
        course_id: int,
        page_slug: str,
        html: str,
        title: str | None = None,
    ) -> PageInfo:
        """
        Actualiza el cuerpo HTML de una página wiki existente en Canvas.

        Args:
            course_id: ID del curso Canvas.
            page_slug: Identificador URL de la página
                       (ej. "front-del-curso", "inicio-presentacion").
            html:      HTML completo a establecer como cuerpo de la página.

        Returns:
            PageInfo con los metadatos de la página actualizada.

        Raises:
            CanvasNotFoundError: La página no existe en el curso.
            CanvasAuthError:     Sin permisos de edición.
        """
        logger.info(
            "Actualizando página '%s' en curso %d", page_slug, course_id
        )

        payload = {
            "wiki_page": {
                "body":          html,
                "editing_roles": "teachers",
                "published":     True,
            }
        }
        if title:
            payload["wiki_page"]["title"] = title   # ← inyectar título si se provee

        respuesta = await self._http.put(
            f"courses/{course_id}/pages/{page_slug}",
            json=payload,
        )

        info = PageInfo.desde_respuesta_canvas(respuesta, course_id)
        logger.info(
            "Página '%s' actualizada: '%s'", page_slug, info.title
        )
        return info

    async def create_page(
        self,
        course_id: int,
        title:     str,
        html:      str,
        slug:      str | None = None,
    ) -> PageInfo:
        """
        Crea una nueva página wiki en el curso.

        Usado principalmente para páginas de contenido interactivo SCORM
        que no existen en la plantilla base.

        Args:
            course_id: ID del curso Canvas.
            title:     Título visible de la página.
            html:      Contenido HTML inicial de la página.
            slug:      Slug URL personalizado (opcional).
                       Si no se provee, Canvas lo genera del título.

        Returns:
            PageInfo con los metadatos de la página recién creada.
        """
        logger.info(
            "Creando página '%s' en curso %d", title, course_id
        )

        wiki_page: dict = {
            "title":         title,
            "body":          html,
            "editing_roles": "teachers",
            "published":     True,
        }

        if slug:
            wiki_page["url"] = slug

        respuesta = await self._http.post(
            f"courses/{course_id}/pages",
            json={"wiki_page": wiki_page},
        )

        info = PageInfo.desde_respuesta_canvas(respuesta, course_id)
        logger.info(
            "Página creada: '%s' (slug: %s)", info.title, info.url
        )
        return info

    async def update_or_create_page(
        self,
        course_id: int,
        page_slug: str,
        title:     str,
        html:      str,
    ) -> PageInfo:
        """
        Actualiza la página si existe, la crea si no existe.

        Útil para páginas de contenido interactivo cuya existencia en
        la plantilla no está garantizada.

        Args:
            course_id: ID del curso Canvas.
            page_slug: Slug URL de la página.
            title:     Título para usar si se crea la página.
            html:      Contenido HTML de la página.

        Returns:
            PageInfo de la página actualizada o creada.
        """
        try:
            return await self.update_page(
            course_id, page_slug, html, title=title   # ← pasar título
        )
        except CanvasNotFoundError:
            logger.info(
                "Página '%s' no existe, creando nueva...", page_slug
            )
            return await self.create_page(
                course_id, title, html, slug=page_slug
            )

    async def list_pages(self, course_id: int) -> list[PageInfo]:
        """
        Lista todas las páginas wiki de un curso.

        Usa paginación automática para retornar la lista completa.

        Args:
            course_id: ID del curso Canvas.

        Returns:
            Lista de PageInfo con todas las páginas del curso.
        """
        logger.info("Listando páginas del curso %d", course_id)

        datos = await self._http.get_paginated(
            f"courses/{course_id}/pages",
            params={"per_page": 100},
        )

        paginas = [
            PageInfo.desde_respuesta_canvas(d, course_id)
            for d in datos
        ]

        logger.info(
            "Curso %d: %d página(s) encontrada(s)", course_id, len(paginas)
        )
        return paginas

    async def get_page(
        self, course_id: int, page_slug: str
    ) -> PageInfo:
        """
        Obtiene los metadatos de una página wiki específica.

        Args:
            course_id: ID del curso Canvas.
            page_slug: Slug URL de la página.

        Returns:
            PageInfo de la página.

        Raises:
            CanvasNotFoundError: La página no existe.
        """
        respuesta = await self._http.get(
            f"courses/{course_id}/pages/{page_slug}"
        )
        return PageInfo.desde_respuesta_canvas(
            respuesta, course_id  # type: ignore[arg-type]
        )

    # ──────────────────────────────────────────────────────────────
    # Vinculación de PDFs a actividades
    # ──────────────────────────────────────────────────────────────

    async def link_pdf_to_assignment(
        self,
        course_id:       int,
        assignment_id:   int,
        assignment_name: str,
        file_id:         int,
        filename:        str,
    ) -> AssignmentLinkResult:
        """
        Vincula un PDF a una actividad con vista previa en línea.

        Genera el HTML específico que Canvas necesita para mostrar el PDF
        con "Vista previa en línea — Expandir vista previa de forma
        predeterminada", replicando el comportamiento del script legado.

        El HTML usa las clases `instructure_file_link instructure_scribd_file`
        y el atributo `data-canvas-previewable="true"` que activan la
        vista previa integrada de Canvas.

        Args:
            course_id:       ID del curso Canvas.
            assignment_id:   ID de la actividad Canvas.
            assignment_name: Nombre de la actividad (para logging).
            file_id:         ID del archivo PDF ya subido a Canvas.
            filename:        Nombre del archivo PDF (ej. "U1_Actividad_Formativa.pdf").

        Returns:
            AssignmentLinkResult con el resultado de la operación.
        """
        logger.info(
            "Vinculando PDF file_id=%d a actividad '%s' (id=%d)",
            file_id, assignment_name, assignment_id,
        )

        html = self._generar_html_pdf_inline(course_id, file_id, filename)

        try:
            await self._http.put(
                f"courses/{course_id}/assignments/{assignment_id}",
                json={
                    "assignment": {
                        "description": html,
                    }
                },
            )

            logger.info(
                "PDF vinculado exitosamente: '%s' → actividad '%s'",
                filename, assignment_name,
            )
            return AssignmentLinkResult(
                assignment_id=assignment_id,
                assignment_name=assignment_name,
                file_id=file_id,
                vinculado=True,
            )

        except Exception as exc:
            logger.error(
                "Error vinculando '%s' a '%s': %s",
                filename, assignment_name, exc,
            )
            return AssignmentLinkResult(
                assignment_id=assignment_id,
                assignment_name=assignment_name,
                file_id=file_id,
                vinculado=False,
                motivo_fallo=str(exc),
            )


    async def link_pdf_to_forum(
        self,
        course_id:  int,
        topic_id:   int,
        topic_name: str,
        file_id:    int,
        filename:   str,
    ) -> AssignmentLinkResult:
        """
        Vincula un PDF a un foro de discusión con vista previa en línea.

        En Canvas, los foros usan el campo 'message' (no 'description')
        y el endpoint es discussion_topics en lugar de assignments.

        Args:
            course_id:  ID del curso Canvas.
            topic_id:   ID del foro de discusión.
            topic_name: Nombre del foro (para logging).
            file_id:    ID del archivo PDF ya subido a Canvas.
            filename:   Nombre del archivo PDF.

        Returns:
            AssignmentLinkResult con el resultado de la operación.
        """
        logger.info(
            "Vinculando PDF file_id=%d a foro '%s' (id=%d)",
            file_id, topic_name, topic_id,
        )

        html = self._generar_html_pdf_inline(course_id, file_id, filename, es_foro=True)

        try:
            await self._http.put(
                f"courses/{course_id}/discussion_topics/{topic_id}",
                json={"message": html},
            )
            logger.info(
                "PDF vinculado exitosamente a foro '%s'", topic_name
            )
            return AssignmentLinkResult(
                assignment_id=topic_id,
                assignment_name=topic_name,
                file_id=file_id,
                vinculado=True,
            )
        except Exception as exc:
            logger.error(
                "Error vinculando '%s' a foro '%s': %s",
                filename, topic_name, exc,
            )
            return AssignmentLinkResult(
                assignment_id=topic_id,
                assignment_name=topic_name,
                file_id=file_id,
                vinculado=False,
                motivo_fallo=str(exc),
            )
    async def link_pdfs_bulk(
        self,
        course_id:    int,
        assignments:  list[dict],
        files_map:    dict[str, int],
        modelo:       str,
        nivel:        str,
        forums:       list[dict] | None = None,
    ) -> list[AssignmentLinkResult]:
        """
        Vincula PDFs a todas las actividades y foros del curso.

        Busca primero en tareas (assignments). Si no encuentra la actividad,
        busca en foros de discusión (discussion_topics), ya que algunas
        actividades formativas se implementan como foros en Canvas.

        Args:
            course_id:   ID del curso Canvas.
            assignments: Lista de tareas del curso (de CourseRepository).
            files_map:   Mapa {ruta_relativa: file_id} de FileRepository.
            modelo:      Modelo instruccional ("Unidades" o "Nuevo sistema").
            nivel:       Nivel de formación ("Pregrado" o "Posgrado").
            forums:      Lista de foros del curso (opcional).

        Returns:
            Lista de AssignmentLinkResult por cada actividad/foro procesado.
        """
        resultados: list[AssignmentLinkResult] = []
        pdfs_disponibles = self._indexar_pdfs(files_map)

        # Índice de foros por nombre para búsqueda rápida
        foros_index: dict[str, dict] = {}
        if forums:
            for foro in forums:
                nombre = foro.get("title", "")
                if nombre:
                    foros_index[nombre] = foro

        for actividad in assignments:
            assignment_id   = actividad.get("id")
            assignment_name = actividad.get("name", "")

            if not assignment_id or not assignment_name:
                continue

            match = self._encontrar_pdf_para_actividad(
                assignment_name=assignment_name,
                modelo=modelo,
                nivel=nivel,
                pdfs_disponibles=pdfs_disponibles,
            )

            if not match:
                logger.debug(
                    "Sin PDF para actividad '%s' — omitiendo", assignment_name
                )
                continue

            ruta_rel, file_id = match
            filename = ruta_rel.split("/")[-1]

            resultado = await self.link_pdf_to_assignment(
                course_id=course_id,
                assignment_id=assignment_id,
                assignment_name=assignment_name,
                file_id=file_id,
                filename=filename,
            )
            resultados.append(resultado)

        # Buscar PDFs para foros que no se encontraron en tareas
        nombres_ya_vinculados = {r.assignment_name for r in resultados if r.vinculado}

        for nombre_foro, foro in foros_index.items():
            if nombre_foro in nombres_ya_vinculados:
                continue

            match = self._encontrar_pdf_para_actividad(
                assignment_name=nombre_foro,
                modelo=modelo,
                nivel=nivel,
                pdfs_disponibles=pdfs_disponibles,
            )

            if not match:
                continue

            ruta_rel, file_id = match
            filename = ruta_rel.split("/")[-1]

            resultado = await self.link_pdf_to_forum(
                course_id=course_id,
                topic_id=foro["id"],
                topic_name=nombre_foro,
                file_id=file_id,
                filename=filename,
            )
            resultados.append(resultado)

        exitosos = sum(1 for r in resultados if r.vinculado)
        logger.info(
            "Vinculación completada: %d/%d exitosos (tareas + foros)",
            exitosos, len(resultados),
        )
        return resultados

    # ──────────────────────────────────────────────────────────────
    # Privados — generación de HTML para Canvas
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _generar_html_pdf_inline(
        course_id: int,
        file_id:   int,
        filename:  str,
        es_foro:   bool = False,
    ) -> str:
        """
        Genera HTML con imagen de cabecera + enlace PDF con vista previa
        expandida automáticamente.

        Imagen de cabecera:
            Tareas: https://moodin.mipoli.co/imgmooact/entregas.jpg
            Foros:  https://moodin.mipoli.co/imgmooact/forocolaborativo.jpg
        """
        imagen_cabecera = (
            "https://moodin.mipoli.co/imgmooact/forocolaborativo.jpg"
            if es_foro else
            "https://moodin.mipoli.co/imgmooact/entregas.jpg"
        )

        img_html = (
            f'<div><img src="{imagen_cabecera}" '
            f'alt="" width="auto" height="auto" /></div>'
        )

        file_url = (
            f"{_BASE_URL_POLI}/courses/{course_id}"
            f"/files/{file_id}/download"
        )
        api_endpoint = (
            f"{_BASE_URL_POLI}/api/v1"
            f"/courses/{course_id}/files/{file_id}"
        )

        embed = (
            f'<a class="instructure_file_link instructure_scribd_file auto_open" '
            f'title="{filename}" '
            f'href="{file_url}" '
            f'target="_blank" rel="noopener" '
            f'data-canvas-previewable="true" '
            f'data-canvas-expanded="true" '
            f'data-api-endpoint="{api_endpoint}" '
            f'data-api-returntype="File">'
            f'{filename}</a>'
        )

        return f"{img_html}\n<p>{embed}</p>"

    # ──────────────────────────────────────────────────────────────
    # Privados — matching PDF → actividad
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _indexar_pdfs(files_map: dict[str, int]) -> dict[str, tuple[str, int]]:
        """
        Construye un índice de PDFs por nombre limpio para búsqueda rápida.

        El índice mapea el nombre del archivo (sin ruta ni extensión,
        en minúsculas) al par (ruta_relativa, file_id).

        Ejemplo:
            "2. Material fundamental/U1_Actividad_Formativa.pdf" → 555
            se indexa como:
            "u1_actividad_formativa" → ("2. Material.../U1_Actividad.pdf", 555)
        """
        indice: dict[str, tuple[str, int]] = {}

        for ruta_rel, file_id in files_map.items():
            if not ruta_rel.lower().endswith(".pdf"):
                continue
            nombre_sin_ext = ruta_rel.split("/")[-1].replace(".pdf", "")
            clave = nombre_sin_ext.lower()
            indice[clave] = (ruta_rel, file_id)

        return indice

    @staticmethod
    def _encontrar_pdf_para_actividad(
        assignment_name:  str,
        modelo:           str,
        nivel:            str,
        pdfs_disponibles: dict[str, tuple[str, int]],
    ) -> tuple[str, int] | None:
        """
        Localiza el PDF correspondiente a una actividad de Canvas.

        Estrategia de matching en dos pasos:
            1. Extrae el número de unidad del nombre de la actividad Canvas.
            2. Determina el tipo de PDF (formativa/sumativa) por palabras clave.
            3. Busca en el índice de PDFs disponibles.

        Patrones de nombre de actividad Canvas soportados:
            "Unidad 1 - Actividad formativa"  → U1_Actividad_Formativa.pdf
            "Unidad 2 - Actividad de entrega" → U2_Actividad_Sumativa.pdf
            "Unidad 3 - Actividad formativa"  → U3_Actividad_Formativa.pdf

        Args:
            assignment_name:  Nombre de la actividad en Canvas.
            modelo:           "Unidades" o "Nuevo sistema".
            nivel:            "Pregrado" o "Posgrado".
            pdfs_disponibles: Índice construido por _indexar_pdfs().

        Returns:
            Tupla (ruta_relativa, file_id) si se encontró match, None si no.
        """
        nombre_lower = assignment_name.lower()

        # Extraer número de unidad
        match_unidad = re.search(r"unidad\s+(\d)", nombre_lower)
        if not match_unidad:
            return None
        unidad = match_unidad.group(1)

        # Determinar tipo de PDF según palabras clave en el nombre de la actividad
        tipo_pdf: str | None = None

        if any(k in nombre_lower for k in ["formativa", "diagnóstica", "diagnostica"]):
            tipo_pdf = "actividad_formativa"
        elif any(k in nombre_lower for k in [
            "sumativa", "entrega", "final", "heteroevaluacion",
            "cuestionario", "examen",
        ]):
            tipo_pdf = "actividad_sumativa"
        elif "autoevaluacion" in nombre_lower:
            tipo_pdf = "actividad_formativa"

        if not tipo_pdf:
            return None

        # Buscar en el índice por clave canónica
        clave_busqueda = f"u{unidad}_{tipo_pdf}"
        if clave_busqueda in pdfs_disponibles:
            return pdfs_disponibles[clave_busqueda]

        # Fallback: buscar por prefijo (maneja sufijos como _1, _2)
        for clave, valor in pdfs_disponibles.items():
            if clave.startswith(clave_busqueda):
                return valor

        return None