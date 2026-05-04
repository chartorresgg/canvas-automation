"""
Orquestador de despliegue de aulas virtuales Canvas LMS.

Implementa el patrón Facade: expone una única operación pública
(deploy) que coordina internamente todos los subsistemas sin que
el cliente (router FastAPI) conozca su existencia.

Capa: Aplicación
Patrón: Facade (GoF — Estructural)
Colaboradores:
    CourseRepository, FileRepository, PageRepository,
    ZipProcessor, InteractiveContentDetector, PageComposerFactory
"""

from __future__ import annotations

import asyncio
import logging
import re
import uuid
from asyncio import Queue
from collections.abc import AsyncGenerator
from pathlib import Path

from app.domain.services.file_normalizer import FileNormalizer
from app.domain.services.interactive_content_detector import (
    InteractiveContentDetector,
)
from app.domain.services.zip_processor import ZipProcessor
from app.domain.value_objects.deployment_config import CourseOption, DeploymentConfig
from app.domain.value_objects.progress_event import ProgressEvent
from app.infrastructure.canvas.course_repository import (
    CourseInfo,
    CourseRepository,
)
from app.infrastructure.canvas.file_repository import FileRepository, UploadSummary
from app.infrastructure.canvas.page_repository import PageRepository
from app.infrastructure.composers.page_composer_factory import (
    PageComposerFactory,
    PageType,
)

logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    """
    Orquestador del proceso de despliegue de aulas virtuales.

    Responsabilidad única (SRP / Facade): coordinar la secuencia
    completa de despliegue en cinco pasos, emitiendo ProgressEvents
    en cada etapa para que FastAPI los transmita como SSE al frontend.

    No realiza ninguna operación directamente. Delega en:
        - CourseRepository: crear/verificar curso en Canvas
        - ZipProcessor:     extraer y normalizar el ZIP
        - FileRepository:   subir archivos a Canvas
        - InteractiveContentDetector: detectar contenido SCORM
        - PageRepository + Composers: actualizar páginas HTML
        - PageRepository: vincular PDFs a actividades

    Uso:
        orchestrator = DeploymentOrchestrator(...)
        async for event in orchestrator.deploy(config):
            # event es un ProgressEvent
            await sse_send(event.to_sse_data())
    """

    def __init__(
        self,
        course_repo:  CourseRepository,
        file_repo:    FileRepository,
        page_repo:    PageRepository,
        detector:     InteractiveContentDetector,
        factory:      PageComposerFactory,
        tmp_dir:      Path,
    ) -> None:
        """
        Args:
            course_repo: Repositorio de cursos Canvas.
            file_repo:   Repositorio de archivos Canvas.
            page_repo:   Repositorio de páginas Canvas.
            detector:    Detector de contenido interactivo SCORM.
            factory:     Fábrica de composers de páginas.
            tmp_dir:     Directorio temporal para extracción de ZIPs.
        """
        self._course_repo = course_repo
        self._file_repo   = file_repo
        self._page_repo   = page_repo
        self._detector    = detector
        self._factory     = factory
        self._tmp_dir     = tmp_dir

    # ──────────────────────────────────────────────────────────────
    # API pública — async generator principal
    # ──────────────────────────────────────────────────────────────

    async def deploy(
        self, config: DeploymentConfig
    ) -> AsyncGenerator[ProgressEvent, None]:
        """
        Ejecuta el despliegue completo del aula virtual.

        Es un async generator: cada `yield` emite un ProgressEvent
        que FastAPI convierte en un evento SSE hacia el frontend React.

        Pasos del proceso:
            0. Inicio          → PENDING  (0%)
            1. Curso Canvas    → RUNNING  (20%)
            2. ZIP procesado   → RUNNING  (35%)
            3. Archivos subidos→ RUNNING  (35-65%, por archivo)
            4. Páginas HTML    → RUNNING  (85%)
            5. Completado      → COMPLETED(100%)

        En caso de error en cualquier paso:
            → FAILED con el paso donde ocurrió y descripción del error.

        Args:
            config: DeploymentConfig validado con Pydantic v2.

        Yields:
            ProgressEvent en cada hito significativo del proceso.
        """
        task_id     = str(uuid.uuid4())
        extract_dir = self._tmp_dir / task_id / "extracted"
        zip_proc    = ZipProcessor(
            zip_path=config.zip_path,
            extract_dir=extract_dir,
            normalizer=FileNormalizer(),
        )

        paso_actual = 0

        try:
            # ── Paso 0: Inicio ────────────────────────────────────
            yield ProgressEvent.iniciando()

            # ── Paso 1: Crear o verificar curso en Canvas ─────────
            paso_actual = 1
            logger.info("[Paso 1] Configurando curso en Canvas...")
            course_info = await self._setup_course(config)
            yield ProgressEvent.curso_listo(course_info.id)

            # ── Paso 2: Extraer y normalizar ZIP ──────────────────
            paso_actual = 2
            logger.info("[Paso 2] Procesando ZIP...")
            extraction  = zip_proc.extract()
            proc_result = zip_proc.normalize()
            yield ProgressEvent.zip_procesado(
                course_info.id,
                proc_result.total_changes,
            )

            # ── Paso 3: Subir archivos a Canvas ───────────────────
            paso_actual = 3
            logger.info(
                "[Paso 3] Subiendo %d archivos...", extraction.total_files
            )
            summary = await self._subir_archivos_con_eventos(
                course_id=course_info.id,
                content_path=zip_proc.content_path,
                # El generador interno yieldeará los eventos de progreso
                # pero no podemos yield desde aquí directamente.
                # Ver: _subir_archivos_con_eventos devuelve summary,
                # los eventos los emitimos con la queue approach.
            )

            # Emitir eventos de progreso de subida de forma agrupada
            # (los eventos individuales por archivo se emiten via SSE en el router)
            yield ProgressEvent.archivos_subidos(
                course_info.id, summary.total_exitosos
            )

            # ── Paso 4: Detectar SCORM y actualizar páginas ───────
            paso_actual = 4
            logger.info("[Paso 4] Actualizando páginas del curso...")
            interactive_map = self._detector.detect(summary.exitosos)
            await self._actualizar_paginas(
                course_info=course_info,
                files_map=summary.exitosos,
                interactive_map=interactive_map,
                config=config,
            )
            await self._vincular_pdfs(
                course_id=course_info.id,
                files_map=summary.exitosos,
                config=config,
            )
            yield ProgressEvent.paginas_actualizadas(course_info.id)

            # ── Paso 5: Completado ────────────────────────────────
            logger.info(
                "[Completado] Aula desplegada: %s", course_info.url
            )
            yield ProgressEvent.completado(course_info.id)

        except Exception as exc:
            logger.error(
                "[Error en paso %d] %s: %s",
                paso_actual, type(exc).__name__, exc,
            )
            yield ProgressEvent.fallido(
                step=paso_actual,
                message=f"Error en paso {paso_actual}: {type(exc).__name__}",
                error=str(exc),
            )

        finally:
            logger.info("Limpiando archivos temporales...")
            zip_proc.cleanup()

    # ──────────────────────────────────────────────────────────────
    # Privados — pasos del despliegue
    # ──────────────────────────────────────────────────────────────

    async def _setup_course(self, config: DeploymentConfig) -> CourseInfo:
        """
        Crea un curso nuevo o verifica un curso existente en Canvas.

        Para curso nuevo:
            1. Crea el curso vacío en Canvas.
            2. Copia la plantilla seleccionada via content migration.
            3. Espera (polling) a que la migración complete.

        Para curso existente:
            1. Consulta y valida el curso en Canvas.

        Args:
            config: DeploymentConfig con course_option y template_id/course_id.

        Returns:
            CourseInfo del curso listo para recibir contenido.
        """
        if config.course_option == CourseOption.NEW:
            logger.info(
                "Creando curso nuevo: '%s'", config.course_name
            )
            course_info = await self._course_repo.create_course(
                config.course_name  # type: ignore[arg-type]
            )

            migration = await self._course_repo.copy_template(
                src_id=config.template_id,  # type: ignore[arg-type]
                dst_id=course_info.id,
            )

            await self._course_repo.poll_migration(
                course_id=course_info.id,
                migration_id=migration.migration_id,
            )
            return course_info

        else:  # EXISTING
            logger.info(
                "Usando curso existente ID: %d", config.course_id
            )
            return await self._course_repo.get_course(
                config.course_id  # type: ignore[arg-type]
            )

    async def _subir_archivos_con_eventos(
            self,
        course_id:    int,
        content_path: Path,
    ) -> UploadSummary:
        """
        Sube todos los archivos a Canvas emitiendo progreso por queue.

        El sentinel None se envía en el bloque finally para garantizar
        que el consumer de la queue siempre termina, incluso si upload_all
        lanza una excepción.
        """
        queue: Queue[ProgressEvent | None] = Queue()
        summary_container: list[UploadSummary] = []
        error_container:   list[Exception]     = []

        def on_progress(actual: int, total: int, ruta: str) -> None:
            event = ProgressEvent.subiendo_archivo(course_id, actual, total)
            queue.put_nowait(event)

        async def _run_upload() -> None:
            try:
                summary = await self._file_repo.upload_all(
                    course_id, content_path, on_progress
                )
                summary_container.append(summary)
            except Exception as exc:
                error_container.append(exc)
            finally:
                # Sentinel siempre se envía — garantiza que el consumer termina
                queue.put_nowait(None)

        task = asyncio.create_task(_run_upload())

        while True:
            item = await queue.get()
            if item is None:
                break

        await task

        # Propagar excepción de upload_all si la hubo
        if error_container:
            raise error_container[0]

        if not summary_container:
            raise RuntimeError(
                "La tarea de subida no retornó resultado — "
                "revisa los logs de FileRepository"
            )

        return summary_container[0]

    async def _actualizar_paginas(
        self,
        course_info:     CourseInfo,
        files_map:       dict[str, int],
        interactive_map: dict[int, list[dict]],
        config:          DeploymentConfig,
    ) -> None:
        course_id = course_info.id

        # 1. Página de presentación
        file_id_presentacion = files_map.get("1. Presentación/index.html")
        if file_id_presentacion:
            composer = self._factory.create(PageType.IFRAME)
            html = composer.compose(course_id, {"file_id": file_id_presentacion})
            try:
                await self._page_repo.update_page(
                    course_id, "inicio-presentacion", html
                )
                logger.info("Página 'inicio-presentacion' actualizada")
            except Exception as exc:
                logger.warning("No se pudo actualizar presentación: %s", exc)

        # 2. Página de cierre
        file_id_cierre = files_map.get("5. Cierre/index.html")
        if file_id_cierre:
            composer = self._factory.create(PageType.IFRAME)
            html = composer.compose(course_id, {"file_id": file_id_cierre})
            try:
                await self._page_repo.update_page(
                    course_id, "cierre-retroalimentacion", html
                )
                logger.info("Página 'cierre-retroalimentacion' actualizada")
            except Exception as exc:
                logger.warning("No se pudo actualizar cierre: %s", exc)

        # 3. Página de Material de trabajo
        file_id_trabajo = files_map.get("3. Material de trabajo/index.html")
        if file_id_trabajo:
            composer = self._factory.create(PageType.IFRAME)
            html = composer.compose(course_id, {"file_id": file_id_trabajo})
            try:
                await self._page_repo.update_page(
                    course_id, "material-de-trabajo", html
                )
                logger.info("Página 'material-de-trabajo' actualizada")
            except Exception as exc:
                logger.warning("No se pudo actualizar material-de-trabajo: %s", exc)

        # 4. Páginas de Material Fundamental — slug institucional correcto
        for unidad in range(1, 5):
            ctx = self._construir_ctx_material_fundamental(
                unidad=unidad,
                files_map=files_map,
                interactive_map=interactive_map,
                course_id=course_id,
            )
            composer = self._factory.create(PageType.MATERIAL_FUNDAMENTAL)
            html = composer.compose(course_id, ctx)
            # Slug correcto: "unidad-1-material-fundamental"
            slug = f"unidad-{unidad}-material-fundamental"
            try:
                await self._page_repo.update_page(course_id, slug, html)
                logger.info("Página '%s' actualizada", slug)
            except Exception as exc:
                logger.warning("No se pudo actualizar '%s': %s", slug, exc)

        # 5. Páginas de Material Complementario — slug institucional correcto
        for unidad in range(1, 5):
            file_id_comp = self._buscar_complemento(unidad, files_map)
            if not file_id_comp:
                continue
            composer = self._factory.create(PageType.COMPLEMENTARY)
            html = composer.compose(course_id, {
                "unidad":   unidad,
                "file_id":  file_id_comp,
                "filename": f"U{unidad}_Complemento.pdf",
            })
            # Slug correcto: "unidad-1-complementario"
            slug = f"unidad-{unidad}-complementario"
            try:
                await self._page_repo.update_or_create_page(
                    course_id, slug,
                    f"Unidad {unidad} — Complementario",
                    html,
                )
                logger.info("Página '%s' actualizada", slug)
            except Exception as exc:
                logger.warning("No se pudo actualizar '%s': %s", slug, exc)

        # 6. Front del curso (solo curso nuevo)
        if config.requires_front_page_update or config.is_new_course:
            await self._actualizar_front(course_id, course_info.name, config)

    async def _actualizar_front(
        self,
        course_id:   int,
        course_name: str,
        config:      DeploymentConfig,
    ) -> None:
        """
        Actualiza la página 'front-del-curso' con datos del Excel del guion.

        En Sprint 2 usa solo el nombre del curso. En Sprint 3, cuando
        GuionExcelReader esté implementado, se leerán las URLs de Vimeo,
        SoundCloud y los párrafos de cada unidad.

        Args:
            course_id:   ID del curso Canvas.
            course_name: Nombre oficial del curso.
            config:      DeploymentConfig con excel_path opcional.
        """
        ctx: dict = {
            "course_name":  course_name,
            "video_url":    "",    # Sprint 3: GuionExcelReader
            "texto_inicio": "",    # Sprint 3: GuionExcelReader
            "texto_u1":     "",    # Sprint 3: GuionExcelReader
            "texto_u2":     "",    # Sprint 3: GuionExcelReader
            "texto_u3":     "",    # Sprint 3: GuionExcelReader
            "texto_u4":     "",    # Sprint 3: GuionExcelReader
            "texto_cierre": "",    # Sprint 3: GuionExcelReader
        }

        composer = self._factory.create(PageType.FRONT)
        html = composer.compose(course_id, ctx)

        try:
            await self._page_repo.update_page(
                course_id, "front-del-curso", html
            )
            logger.info("Página 'front-del-curso' actualizada")
        except Exception as exc:
            logger.warning("No se pudo actualizar front-del-curso: %s", exc)

    async def _vincular_pdfs(
        self,
        course_id: int,
        files_map: dict[str, int],
        config:    DeploymentConfig,
    ) -> None:
        """
        Vincula los PDFs del aula a sus actividades correspondientes en Canvas.

        Obtiene la lista de actividades del curso y delega la vinculación
        masiva a PageRepository.link_pdfs_bulk().

        El modelo instruccional se deriva del diseño instruccional del config
        (en Sprint 2 se pasa como parámetro desde la selección del analista).

        Args:
            course_id: ID del curso Canvas.
            files_map: {ruta_relativa: file_id} con los PDFs subidos.
            config:    DeploymentConfig con metadatos del despliegue.
        """
        try:
            actividades = await self._course_repo.list_assignments(course_id)

            if not actividades:
                logger.info(
                    "Curso %d sin actividades — omitiendo vinculación de PDFs",
                    course_id,
                )
                return

            resultados = await self._page_repo.link_pdfs_bulk(
                course_id=course_id,
                assignments=actividades,
                files_map=files_map,
                modelo=getattr(config, "modelo_instruccional", "Unidades"),
                nivel=getattr(config, "nivel_formacion", "Pregrado"),
            )

            exitosos = sum(1 for r in resultados if r.vinculado)
            logger.info(
                "PDFs vinculados: %d/%d actividades",
                exitosos, len(resultados),
            )

        except Exception as exc:
            logger.warning(
                "Error vinculando PDFs (no bloquea el despliegue): %s", exc
            )

    # ──────────────────────────────────────────────────────────────
    # Privados — construcción de contextos para Composers
    # ──────────────────────────────────────────────────────────────

    def _construir_ctx_material_fundamental(
        self,
        unidad:          int,
        files_map:       dict[str, int],
        interactive_map: dict[int, list[dict]],
        course_id:       int,
    ) -> dict:
        """
        Construye el contexto para MaterialFundamentalComposer de una unidad.

        Clasifica los archivos del FileMap en las categorías que el
        Composer necesita: lecturas, material_fundamental_pdfs, actividades,
        páginas interactivas y recursos multimedia (Sprint 3).

        Args:
            unidad:          Número de unidad (1-4).
            files_map:       {ruta_relativa: file_id} de todos los archivos.
            interactive_map: {unidad: [paginas_scorm]} del detector.
            course_id:       ID del curso Canvas (para construir URLs de páginas).

        Returns:
            Diccionario ctx listo para pasar a MaterialFundamentalComposer.
        """
        lecturas:      list[dict] = []
        mat_fund_pdfs: list[dict] = []
        actividades:   list[dict] = []

        prefijo = "2. Material fundamental/"

        for ruta, file_id in files_map.items():
            if not ruta.startswith(prefijo):
                continue

            nombre = ruta[len(prefijo):]
            if "/" in nombre:
                continue  # es un archivo dentro de subcarpeta SCORM

            nombre_lower = nombre.lower()

            # Filtrar por unidad
            if not nombre_lower.startswith(f"u{unidad}_"):
                continue

            # Clasificar por tipo
            if "lectura_fundamental" in nombre_lower:
                seq = self._extraer_secuencia(nombre)
                lecturas.append({"file_id": file_id, "secuencia": seq})

            elif "material_fundamental" in nombre_lower:
                mat_fund_pdfs.append({"file_id": file_id})

            elif "actividad_formativa" in nombre_lower:
                actividades.append({"file_id": file_id, "tipo": "formativa"})

            elif "actividad_sumativa" in nombre_lower:
                actividades.append({"file_id": file_id, "tipo": "sumativa"})

        # Ordenar lecturas por secuencia
        lecturas.sort(key=lambda x: x["secuencia"])

        # Construir info de páginas interactivas para esta unidad
        paginas_interactivas: list[dict] = []
        for info in interactive_map.get(unidad, []):
            numero = info["numero"]
            es_enumerado = info.get("es_enumerado", False)
            if es_enumerado or len(interactive_map.get(unidad, [])) > 1:
                slug = f"unidad-{unidad}-contenido-interactivo-{numero}"
            else:
                slug = f"unidad-{unidad}-contenido-interactivo"

            paginas_interactivas.append({
                "page_url":     slug,
                "numero":       numero,
                "es_enumerado": es_enumerado,
            })

        return {
            "unidad":               unidad,
            "lecturas":             lecturas,
            "mat_fund_pdfs":        mat_fund_pdfs,
            "actividades":          actividades,
            "paginas_interactivas": paginas_interactivas,
            # Sprint 3: GuionExcelReader llenará estas URLs
            "video_intro_url": None,
            "podcast_url":     None,
            "vimeo_url":       None,
        }

    @staticmethod
    def _buscar_complemento(
        unidad: int, files_map: dict[str, int]
    ) -> int | None:
        """
        Busca el file_id del PDF de material complementario de una unidad.

        Retorna el primer PDF encontrado en "4. Complementos/"
        cuyo nombre empieza con "U{unidad}_Complemento".

        Args:
            unidad:    Número de unidad (1-4).
            files_map: {ruta_relativa: file_id} de todos los archivos.

        Returns:
            file_id del complemento o None si no existe.
        """
        prefijo_busqueda = f"u{unidad}_complemento"

        for ruta, file_id in files_map.items():
            if not ruta.lower().startswith("4. complementos/"):
                continue
            nombre = ruta.split("/")[-1].lower().replace(".pdf", "")
            if nombre.startswith(prefijo_busqueda):
                return file_id

        return None

    @staticmethod
    def _extraer_secuencia(nombre_archivo: str) -> int:
        """
        Extrae el número de secuencia de una lectura fundamental.

        Soporta:
            "U1_Lectura_Fundamental.pdf"   → 1 (valor por defecto)
            "U1_Lectura_Fundamental_2.pdf" → 2

        Args:
            nombre_archivo: Nombre del archivo (con o sin extensión).

        Returns:
            Número de secuencia como int. Default: 1.
        """
        match = re.search(r"_(\d+)(?:\.pdf)?$", nombre_archivo, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 1