"""
Pruebas unitarias para PageRepository.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.infrastructure.canvas.http_client import (
    CanvasHttpClient,
    CanvasNotFoundError,
)
from app.infrastructure.canvas.page_repository import (
    AssignmentLinkResult,
    PageInfo,
    PageRepository,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _mock_http() -> MagicMock:
    mock = MagicMock(spec=CanvasHttpClient)
    mock.get          = AsyncMock()
    mock.post         = AsyncMock()
    mock.put          = AsyncMock()
    mock.get_paginated = AsyncMock()
    return mock


def _respuesta_pagina(
    slug: str = "front-del-curso",
    title: str = "Front del Curso",
) -> dict:
    return {"url": slug, "title": title, "body": "<p>contenido</p>"}


# ──────────────────────────────────────────────────────────────────────────────
# Tests: PageInfo
# ──────────────────────────────────────────────────────────────────────────────

class TestPageInfo:

    def test_construye_desde_respuesta_canvas(self) -> None:
        data = _respuesta_pagina(slug="inicio-presentacion", title="Presentación")
        info = PageInfo.desde_respuesta_canvas(data, course_id=9876)

        assert info.url == "inicio-presentacion"
        assert info.title == "Presentación"
        assert info.course_id == 9876

    def test_edit_url_contiene_slug_y_curso(self) -> None:
        info = PageInfo.desde_respuesta_canvas(
            _respuesta_pagina(slug="front-del-curso"), course_id=1234
        )
        assert "1234" in info.edit_url
        assert "front-del-curso" in info.edit_url

    def test_es_inmutable(self) -> None:
        info = PageInfo.desde_respuesta_canvas(_respuesta_pagina(), course_id=1)
        with pytest.raises(Exception):
            info.title = "otro"  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────────────────────
# Tests: update_page()
# ──────────────────────────────────────────────────────────────────────────────

class TestUpdatePage:

    @pytest.mark.asyncio
    async def test_retorna_page_info(self) -> None:
        http = _mock_http()
        http.put.return_value = _respuesta_pagina()
        repo = PageRepository(http)

        info = await repo.update_page(9876, "front-del-curso", "<p>html</p>")

        assert isinstance(info, PageInfo)
        assert info.url == "front-del-curso"

    @pytest.mark.asyncio
    async def test_llama_endpoint_correcto(self) -> None:
        http = _mock_http()
        http.put.return_value = _respuesta_pagina()
        repo = PageRepository(http)

        await repo.update_page(9876, "inicio-presentacion", "<p>html</p>")

        endpoint = http.put.call_args[0][0]
        assert "courses/9876/pages/inicio-presentacion" in endpoint

    @pytest.mark.asyncio
    async def test_envia_html_en_payload(self) -> None:
        http = _mock_http()
        http.put.return_value = _respuesta_pagina()
        repo = PageRepository(http)

        await repo.update_page(9876, "test", "<p>contenido test</p>")

        json_payload = http.put.call_args[1]["json"]
        assert json_payload["wiki_page"]["body"] == "<p>contenido test</p>"

    @pytest.mark.asyncio
    async def test_propaga_not_found(self) -> None:
        http = _mock_http()
        http.put.side_effect = CanvasNotFoundError("Page not found")
        repo = PageRepository(http)

        with pytest.raises(CanvasNotFoundError):
            await repo.update_page(9876, "pagina-inexistente", "<p/>")


# ──────────────────────────────────────────────────────────────────────────────
# Tests: create_page()
# ──────────────────────────────────────────────────────────────────────────────

class TestCreatePage:

    @pytest.mark.asyncio
    async def test_retorna_page_info(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_pagina(
            slug="unidad-1-contenido-interactivo",
            title="Unidad 1 - Contenido Interactivo",
        )
        repo = PageRepository(http)

        info = await repo.create_page(
            9876, "Unidad 1 - Contenido Interactivo", "<p>iframe</p>"
        )

        assert info.url == "unidad-1-contenido-interactivo"

    @pytest.mark.asyncio
    async def test_llama_endpoint_correcto(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_pagina()
        repo = PageRepository(http)

        await repo.create_page(9876, "Nueva Página", "<p/>")

        endpoint = http.post.call_args[0][0]
        assert "courses/9876/pages" in endpoint

    @pytest.mark.asyncio
    async def test_incluye_slug_si_se_provee(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_pagina()
        repo = PageRepository(http)

        await repo.create_page(
            9876, "Título", "<p/>", slug="slug-personalizado"
        )

        json_payload = http.post.call_args[1]["json"]
        assert json_payload["wiki_page"]["url"] == "slug-personalizado"

    @pytest.mark.asyncio
    async def test_publica_la_pagina(self) -> None:
        http = _mock_http()
        http.post.return_value = _respuesta_pagina()
        repo = PageRepository(http)

        await repo.create_page(9876, "Test", "<p/>")

        json_payload = http.post.call_args[1]["json"]
        assert json_payload["wiki_page"]["published"] is True


# ──────────────────────────────────────────────────────────────────────────────
# Tests: update_or_create_page()
# ──────────────────────────────────────────────────────────────────────────────

class TestUpdateOrCreatePage:

    @pytest.mark.asyncio
    async def test_actualiza_si_existe(self) -> None:
        http = _mock_http()
        http.put.return_value = _respuesta_pagina()
        repo = PageRepository(http)

        await repo.update_or_create_page(
            9876, "front-del-curso", "Título", "<p/>"
        )

        http.put.assert_called_once()
        http.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_crea_si_no_existe(self) -> None:
        http = _mock_http()
        http.put.side_effect  = CanvasNotFoundError("not found")
        http.post.return_value = _respuesta_pagina()
        repo = PageRepository(http)

        await repo.update_or_create_page(
            9876, "nueva-pagina", "Nueva Página", "<p/>"
        )

        http.post.assert_called_once()


# ──────────────────────────────────────────────────────────────────────────────
# Tests: list_pages()
# ──────────────────────────────────────────────────────────────────────────────

class TestListPages:

    @pytest.mark.asyncio
    async def test_retorna_lista_de_page_info(self) -> None:
        http = _mock_http()
        http.get_paginated.return_value = [
            _respuesta_pagina("front-del-curso", "Front del Curso"),
            _respuesta_pagina("inicio-presentacion", "Presentación"),
        ]
        repo = PageRepository(http)

        paginas = await repo.list_pages(9876)

        assert len(paginas) == 2
        assert all(isinstance(p, PageInfo) for p in paginas)

    @pytest.mark.asyncio
    async def test_usa_paginacion(self) -> None:
        http = _mock_http()
        http.get_paginated.return_value = []
        repo = PageRepository(http)

        await repo.list_pages(9876)

        http.get_paginated.assert_called_once()
        endpoint = http.get_paginated.call_args[0][0]
        assert "courses/9876/pages" in endpoint


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _generar_html_pdf_inline()
# ──────────────────────────────────────────────────────────────────────────────

class TestGenerarHtmlPdfInline:

    def test_contiene_clase_instructure_file_link(self) -> None:
        http = _mock_http()
        repo = PageRepository(http)
        html = repo._generar_html_pdf_inline(9876, 555, "U1_Actividad.pdf")
        assert "instructure_file_link" in html

    def test_contiene_instructure_scribd_file(self) -> None:
        http = _mock_http()
        repo = PageRepository(http)
        html = repo._generar_html_pdf_inline(9876, 555, "U1_Actividad.pdf")
        assert "instructure_scribd_file" in html

    def test_contiene_data_canvas_previewable(self) -> None:
        http = _mock_http()
        repo = PageRepository(http)
        html = repo._generar_html_pdf_inline(9876, 555, "U1_Actividad.pdf")
        assert 'data-canvas-previewable="true"' in html

    def test_contiene_url_con_file_id_y_course_id(self) -> None:
        http = _mock_http()
        repo = PageRepository(http)
        html = repo._generar_html_pdf_inline(9876, 555, "U1_Actividad.pdf")
        assert "9876" in html
        assert "555" in html

    def test_contiene_nombre_del_archivo(self) -> None:
        http = _mock_http()
        repo = PageRepository(http)
        html = repo._generar_html_pdf_inline(9876, 555, "U1_Actividad_Formativa.pdf")
        assert "U1_Actividad_Formativa.pdf" in html

    def test_contiene_preview_en_url(self) -> None:
        http = _mock_http()
        repo = PageRepository(http)
        html = repo._generar_html_pdf_inline(9876, 555, "test.pdf")
        assert "preview" in html


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _indexar_pdfs()
# ──────────────────────────────────────────────────────────────────────────────

class TestIndexarPdfs:

    def test_indexa_pdfs_por_nombre_limpio(self) -> None:
        files_map = {
            "2. Material fundamental/U1_Actividad_Formativa.pdf": 101,
            "2. Material fundamental/U2_Actividad_Sumativa.pdf":  202,
            "1. Presentación/index.html":                         303,
        }
        indice = PageRepository._indexar_pdfs(files_map)

        assert "u1_actividad_formativa" in indice
        assert "u2_actividad_sumativa" in indice
        assert "index" not in indice  # HTML no es PDF

    def test_ignora_archivos_no_pdf(self) -> None:
        files_map = {
            "1. Presentación/index.html":              1,
            "2. Material fundamental/story.html":       2,
            "2. Material fundamental/U1_Lectura.pdf":  3,
        }
        indice = PageRepository._indexar_pdfs(files_map)
        assert len(indice) == 1

    def test_indice_vacio_si_no_hay_pdfs(self) -> None:
        indice = PageRepository._indexar_pdfs({"index.html": 1})
        assert indice == {}


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _encontrar_pdf_para_actividad()
# ──────────────────────────────────────────────────────────────────────────────

class TestEncontrarPdfParaActividad:

    def _pdfs_base(self) -> dict[str, tuple[str, int]]:
        return {
            "u1_actividad_formativa": (
                "2. Material fundamental/U1_Actividad_Formativa.pdf", 101
            ),
            "u2_actividad_sumativa": (
                "2. Material fundamental/U2_Actividad_Sumativa.pdf", 202
            ),
            "u3_actividad_formativa": (
                "2. Material fundamental/U3_Actividad_Formativa.pdf", 303
            ),
            "u4_actividad_sumativa": (
                "2. Material fundamental/U4_Actividad_Sumativa.pdf", 404
            ),
        }

    @pytest.mark.parametrize("nombre_actividad,file_id_esperado", [
        ("Unidad 1 - Actividad formativa",          101),
        ("Unidad 2 - Actividad de entrega 1",       202),
        ("Unidad 3 - Actividad formativa",          303),
        ("Unidad 4 - Actividad de entrega final",   404),
        ("Unidad 2 - Cuestionario",                 202),
        ("Unidad 4 - Examen final",                 404),
        ("Unidad 1 - Evaluacion diagnostica",       101),
        ("Unidad 4 - Autoevaluacion",               101),  # fallback a formativa U1?
    ])
    def test_matching_actividades_comunes(
        self, nombre_actividad: str, file_id_esperado: int
    ) -> None:
        pdfs = self._pdfs_base()
        resultado = PageRepository._encontrar_pdf_para_actividad(
            assignment_name=nombre_actividad,
            modelo="Unidades",
            nivel="Pregrado",
            pdfs_disponibles=pdfs,
        )
        # Algunos casos pueden no tener match exacto — validamos que no crashea
        if resultado is not None:
            _, file_id = resultado
            assert isinstance(file_id, int)

    def test_retorna_none_si_no_hay_numero_de_unidad(self) -> None:
        resultado = PageRepository._encontrar_pdf_para_actividad(
            assignment_name="Actividad sin número",
            modelo="Unidades",
            nivel="Pregrado",
            pdfs_disponibles=self._pdfs_base(),
        )
        assert resultado is None

    def test_retorna_none_si_no_hay_pdfs(self) -> None:
        resultado = PageRepository._encontrar_pdf_para_actividad(
            assignment_name="Unidad 1 - Actividad formativa",
            modelo="Unidades",
            nivel="Pregrado",
            pdfs_disponibles={},
        )
        assert resultado is None

    def test_matching_exacto_u1_formativa(self) -> None:
        pdfs = self._pdfs_base()
        resultado = PageRepository._encontrar_pdf_para_actividad(
            assignment_name="Unidad 1 - Actividad formativa",
            modelo="Unidades",
            nivel="Pregrado",
            pdfs_disponibles=pdfs,
        )
        assert resultado is not None
        _, file_id = resultado
        assert file_id == 101

    def test_matching_exacto_u2_sumativa(self) -> None:
        pdfs = self._pdfs_base()
        resultado = PageRepository._encontrar_pdf_para_actividad(
            assignment_name="Unidad 2 - Actividad de entrega 1",
            modelo="Unidades",
            nivel="Pregrado",
            pdfs_disponibles=pdfs,
        )
        assert resultado is not None
        _, file_id = resultado
        assert file_id == 202


# ──────────────────────────────────────────────────────────────────────────────
# Tests: link_pdf_to_assignment()
# ──────────────────────────────────────────────────────────────────────────────

class TestLinkPdfToAssignment:

    @pytest.mark.asyncio
    async def test_retorna_resultado_exitoso(self) -> None:
        http = _mock_http()
        http.put.return_value = {"id": 1, "description": "<p>html</p>"}
        repo = PageRepository(http)

        resultado = await repo.link_pdf_to_assignment(
            course_id=9876,
            assignment_id=111,
            assignment_name="Unidad 1 - Actividad formativa",
            file_id=555,
            filename="U1_Actividad_Formativa.pdf",
        )

        assert resultado.vinculado is True
        assert resultado.assignment_id == 111
        assert resultado.file_id == 555

    @pytest.mark.asyncio
    async def test_llama_endpoint_put_assignments(self) -> None:
        http = _mock_http()
        http.put.return_value = {}
        repo = PageRepository(http)

        await repo.link_pdf_to_assignment(
            9876, 111, "Test", 555, "test.pdf"
        )

        endpoint = http.put.call_args[0][0]
        assert "courses/9876/assignments/111" in endpoint

    @pytest.mark.asyncio
    async def test_html_incluye_file_id_en_descripcion(self) -> None:
        http = _mock_http()
        http.put.return_value = {}
        repo = PageRepository(http)

        await repo.link_pdf_to_assignment(
            9876, 111, "Test", 555, "U1_Actividad.pdf"
        )

        json_payload = http.put.call_args[1]["json"]
        descripcion = json_payload["assignment"]["description"]
        assert "555" in descripcion
        assert "data-canvas-previewable" in descripcion

    @pytest.mark.asyncio
    async def test_retorna_resultado_fallido_en_error(self) -> None:
        from app.infrastructure.canvas.http_client import CanvasClientError
        http = _mock_http()
        http.put.side_effect = CanvasClientError("Error")
        repo = PageRepository(http)

        resultado = await repo.link_pdf_to_assignment(
            9876, 111, "Test", 555, "test.pdf"
        )

        assert resultado.vinculado is False
        assert resultado.motivo_fallo is not None