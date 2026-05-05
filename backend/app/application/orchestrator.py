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
from app.domain.services.guion_excel_reader import GuionData, GuionExcelReader
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

    async def _crear_paginas_interactivas(
        self,
        course_id:       int,
        interactive_map: dict[int, list[dict]],
    ) -> dict[int, list[dict]]:
        """
        Crea en Canvas las páginas wiki para cada paquete SCORM detectado.

        Slug y título institucional:
            Un solo contenido:  slug = "unidad-1-material-interactivo"
                                title = "Unidad 1 - Material interactivo"
            Múltiples:          slug = "unidad-1-material-interactivo-2"
                                title = "Unidad 1 - Material interactivo 2"
        """
        paginas_creadas: dict[int, list[dict]] = {}

        for unidad, contenidos in interactive_map.items():
            paginas_creadas[unidad] = []
            multiples = len(contenidos) > 1

            for info in contenidos:
                numero       = info["numero"]
                file_id      = info["file_id"]
                es_enumerado = info.get("es_enumerado", False)

                if multiples or es_enumerado:
                    slug  = f"unidad-{unidad}-material-interactivo-{numero}"
                    title = f"Unidad {unidad} - Material interactivo {numero}"
                else:
                    slug  = f"unidad-{unidad}-material-interactivo"
                    title = f"Unidad {unidad} - Material interactivo"

                composer = self._factory.create(PageType.IFRAME)
                html = composer.compose(course_id, {"file_id": file_id})

                try:
                    await self._page_repo.update_or_create_page(
                        course_id, slug, title, html
                    )
                    logger.info(
                        "Página interactiva creada/actualizada: '%s'", slug
                    )
                except Exception as exc:
                    logger.warning(
                        "No se pudo crear página interactiva '%s': %s", slug, exc
                    )

                paginas_creadas[unidad].append({
                    "numero":       numero,
                    "file_id":      file_id,
                    "page_url":     slug,
                    "es_enumerado": es_enumerado,
                })

        return paginas_creadas
    
    @staticmethod
    def _buscar_archivos_material_trabajo(
        files_map: dict[str, int]
    ) -> list[dict]:
        """
        Busca archivos PDF de Material de trabajo por unidad.

        Detecta archivos en "3. Material de trabajo/" cuyo nombre
        empieza por U{n} y extrae el número de unidad.

        Returns:
            Lista de {file_id, unidad} ordenada por unidad.
        """
        import re as _re

        archivos: list[dict] = []
        prefijo = "3. Material de trabajo/"

        for ruta, file_id in files_map.items():
            if not ruta.lower().startswith(prefijo.lower()):
                continue
            nombre = ruta[len(prefijo):]
            if "/" in nombre:
                continue  # ignorar subcarpetas

            match = _re.match(r"u(\d)", nombre, _re.IGNORECASE)
            if match:
                archivos.append({
                    "file_id": file_id,
                    "unidad":  int(match.group(1)),
                })

        return sorted(archivos, key=lambda x: x["unidad"])

    async def _actualizar_paginas(
        self,
        course_info:     CourseInfo,
        files_map:       dict[str, int],
        interactive_map: dict[int, list[dict]],
        config:          DeploymentConfig,
    ) -> None:
        course_id = course_info.id

        # Leer Guion Excel una sola vez — alimenta Material Fundamental y Front
        guion_data: GuionData | None = None
        if config.excel_path and config.excel_path.exists():
            try:
                guion_data = GuionExcelReader(config.excel_path).read()
                logger.info(
                    "Guion Excel leído: video_inicial=%s, unidades=%s",
                    bool(guion_data.video_inicial_url),
                    list(guion_data.unidades.keys()),
                )
            except Exception as exc:
                logger.warning(
                    "No se pudo leer Guion Excel — páginas sin multimedia: %s", exc
                )

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
        # Paso 3 — Material de trabajo (PDFs individuales o index.html)
        archivos_trabajo = self._buscar_archivos_material_trabajo(files_map)
        if archivos_trabajo:
            composer = self._factory.create(PageType.MATERIAL_TRABAJO)
            html = composer.compose(course_id, {"archivos": archivos_trabajo})
            try:
                await self._page_repo.update_page(
                    course_id, "material-de-trabajo", html
                )
                logger.info("Página 'material-de-trabajo' actualizada con botones")
            except Exception as exc:
                logger.warning("No se pudo actualizar material-de-trabajo: %s", exc)
        elif files_map.get("3. Material de trabajo/index.html"):
            # Fallback: index.html como iframe
            file_id_trabajo = files_map["3. Material de trabajo/index.html"]
            composer = self._factory.create(PageType.IFRAME)
            html = composer.compose(course_id, {"file_id": file_id_trabajo})
            try:
                await self._page_repo.update_page(
                    course_id, "material-de-trabajo", html
                )
                logger.info("Página 'material-de-trabajo' actualizada como iframe")
            except Exception as exc:
                logger.warning("No se pudo actualizar material-de-trabajo: %s", exc)

        # Paso 3.5 — Crear páginas interactivas ANTES de Material Fundamental
        paginas_interactivas_creadas = await self._crear_paginas_interactivas(
            course_id, interactive_map
        )

        # 4. Páginas de Material Fundamental — con datos del Guion Excel
        for unidad in range(1, 5):
            ctx = self._construir_ctx_material_fundamental(
                unidad=unidad,
                files_map=files_map,
                interactive_map=paginas_interactivas_creadas,
                course_id=course_id,
                guion_data=guion_data,
            )
            composer = self._factory.create(PageType.MATERIAL_FUNDAMENTAL)
            html = composer.compose(course_id, ctx)
            slug = f"unidad-{unidad}-material-fundamental"
            try:
                await self._page_repo.update_page(course_id, slug, html)
                logger.info("Página '%s' actualizada", slug)
            except Exception as exc:
                logger.warning("No se pudo actualizar '%s': %s", slug, exc)

        # 5. Páginas de Material Complementario
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

        # 6. Front del curso
        if config.requires_front_page_update or config.is_new_course:
            await self._actualizar_front(
                course_id, course_info.name, config, guion_data
            )

    async def _actualizar_front(
        self,
        course_id:   int,
        course_name: str,
        config:      DeploymentConfig,
        guion_data:  GuionData | None = None,
    ) -> None:
        """
        Actualiza 'front-del-curso'. Recibe guion_data ya parseado
        para evitar leer el Excel dos veces.
        """
        ctx: dict = {"course_name": course_name}

        if guion_data:
            ctx["video_url"]    = guion_data.video_inicial_url or ""
            ctx["texto_inicio"] = guion_data.texto_inicio
            ctx["texto_u1"]     = guion_data.unidad(1).parrafo_intro
            ctx["texto_u2"]     = guion_data.unidad(2).parrafo_intro
            ctx["texto_u3"]     = guion_data.unidad(3).parrafo_intro
            ctx["texto_u4"]     = guion_data.unidad(4).parrafo_intro
            ctx["texto_cierre"] = guion_data.texto_cierre
        elif config.excel_path and config.excel_path.exists():
            # Fallback: leer el Excel si no vino del paso anterior
            try:
                lector    = GuionExcelReader(config.excel_path)
                guion     = lector.read()
                ctx["video_url"]    = guion.video_inicial_url or ""
                ctx["texto_inicio"] = guion.texto_inicio
                ctx["texto_u1"]     = guion.unidad(1).parrafo_intro
                ctx["texto_u2"]     = guion.unidad(2).parrafo_intro
                ctx["texto_u3"]     = guion.unidad(3).parrafo_intro
                ctx["texto_u4"]     = guion.unidad(4).parrafo_intro
                ctx["texto_cierre"] = guion.texto_cierre
            except Exception as exc:
                logger.warning(
                    "No se pudo leer Guion Excel para front: %s", exc
                )

        composer = self._factory.create(PageType.FRONT)
        html = composer.compose(course_id, ctx)

        try:
            await self._page_repo.update_page(course_id, "front-del-curso", html)
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
        Vincula PDFs a actividades (tareas y foros) del curso.
        """
        try:
            actividades, foros = await asyncio.gather(
                self._course_repo.list_assignments(course_id),
                self._course_repo.list_discussion_topics(course_id),
            )

            if not actividades and not foros:
                logger.info(
                    "Curso %d sin actividades ni foros — omitiendo vinculación",
                    course_id,
                )
                return

            resultados = await self._page_repo.link_pdfs_bulk(
                course_id=course_id,
                assignments=actividades,
                files_map=files_map,
                modelo=getattr(config, "modelo_instruccional", "Unidades"),
                nivel=getattr(config, "nivel_formacion", "Pregrado"),
                forums=foros,
            )

            exitosos = sum(1 for r in resultados if r.vinculado)
            logger.info(
                "PDFs vinculados: %d/%d (tareas + foros)",
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
        guion_data:      GuionData | None = None,
    ) -> dict:
        """
        Construye el contexto para MaterialFundamentalComposer.
        Si guion_data está disponible, inyecta URLs de video, podcast y Vimeo.
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
                continue
            nombre_lower = nombre.lower()
            if not nombre_lower.startswith(f"u{unidad}_"):
                continue

            if "lectura_fundamental" in nombre_lower:
                seq = self._extraer_secuencia(nombre)
                lecturas.append({"file_id": file_id, "secuencia": seq})
            elif "material_fundamental" in nombre_lower:
                mat_fund_pdfs.append({"file_id": file_id})
            elif "actividad_formativa" in nombre_lower:
                actividades.append({"file_id": file_id, "tipo": "formativa"})
            elif "actividad_sumativa" in nombre_lower:
                actividades.append({"file_id": file_id, "tipo": "sumativa"})

        lecturas.sort(key=lambda x: x["secuencia"])

        paginas_interactivas: list[dict] = []
        for info in interactive_map.get(unidad, []):
            # interactive_map ya viene con page_url calculado
            # desde _crear_paginas_interactivas — usarlo directamente
            paginas_interactivas.append({
                "page_url":     info["page_url"],
                "numero":       info["numero"],
                "es_enumerado": info.get("es_enumerado", False),
            })

        # URLs multimedia del Guion Excel (si está disponible)
        video_intro_url: str | None = None
        podcast_url:     str | None = None
        vimeo_url:       str | None = None

        if guion_data:
            unidad_guion = guion_data.unidad(unidad)
            video_intro_url = unidad_guion.video_intro_url
            podcast_url     = unidad_guion.podcast_url
            vimeo_url       = unidad_guion.vimeo_mat_fund_url

        return {
            "unidad":               unidad,
            "lecturas":             lecturas,
            "mat_fund_pdfs":        mat_fund_pdfs,
            "actividades":          actividades,
            "paginas_interactivas": paginas_interactivas,
            "video_intro_url":      video_intro_url,
            "podcast_url":          podcast_url,
            "vimeo_url":            vimeo_url,
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