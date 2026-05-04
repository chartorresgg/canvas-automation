"""
Pruebas unitarias para todos los Composers y PageComposerFactory.
"""

from __future__ import annotations

import pytest

from app.domain.interfaces.i_page_composer import IPageComposer
from app.infrastructure.composers.complementary_page_composer import (
    ComplementaryPageComposer,
)
from app.infrastructure.composers.front_page_composer import FrontPageComposer
from app.infrastructure.composers.iframe_composer import IframeComposer
from app.infrastructure.composers.material_fundamental_composer import (
    MaterialFundamentalComposer,
)
from app.infrastructure.composers.page_composer_factory import (
    PageComposerFactory,
    PageType,
)

COURSE_ID = 9876


# ══════════════════════════════════════════════════════════════════════════════
# Tests: IframeComposer
# ══════════════════════════════════════════════════════════════════════════════

class TestIframeComposer:

    def test_es_subclase_de_ipage_composer(self) -> None:
        assert issubclass(IframeComposer, IPageComposer)

    def test_genera_iframe(self) -> None:
        html = IframeComposer().compose(COURSE_ID, {"file_id": 555})
        assert "<iframe" in html

    def test_url_contiene_course_id_y_file_id(self) -> None:
        html = IframeComposer().compose(COURSE_ID, {"file_id": 555})
        assert str(COURSE_ID) in html
        assert "555" in html

    def test_iframe_con_ancho_completo(self) -> None:
        html = IframeComposer().compose(COURSE_ID, {"file_id": 1})
        assert "100%" in html

    def test_url_de_descarga_en_src(self) -> None:
        html = IframeComposer().compose(COURSE_ID, {"file_id": 123})
        assert "download" in html or "files/123" in html

    def test_contiene_data_api_endpoint(self) -> None:
        html = IframeComposer().compose(COURSE_ID, {"file_id": 99})
        assert "data-api-endpoint" in html

    def test_lanza_key_error_sin_file_id(self) -> None:
        with pytest.raises(KeyError):
            IframeComposer().compose(COURSE_ID, {})


# ══════════════════════════════════════════════════════════════════════════════
# Tests: MaterialFundamentalComposer
# ══════════════════════════════════════════════════════════════════════════════

class TestMaterialFundamentalComposer:

    def _ctx_basico(self, unidad: int = 1) -> dict:
        return {
            "unidad":       unidad,
            "lecturas":     [{"file_id": 101, "secuencia": 1}],
            "mat_fund_pdfs": [],
            "actividades":  [],
            "paginas_interactivas": [],
            "video_intro_url": None,
            "podcast_url":     None,
            "vimeo_url":       None,
        }

    def test_es_subclase_de_ipage_composer(self) -> None:
        assert issubclass(MaterialFundamentalComposer, IPageComposer)

    def test_contiene_banner_material_fundamental(self) -> None:
        html = MaterialFundamentalComposer().compose(COURSE_ID, self._ctx_basico())
        assert "Bannermaterialfundamental" in html

    def test_contiene_boton_lectura_con_file_id(self) -> None:
        html = MaterialFundamentalComposer().compose(COURSE_ID, self._ctx_basico())
        assert "101" in html

    def test_imagen_lectura_secuencia_1(self) -> None:
        html = MaterialFundamentalComposer().compose(COURSE_ID, self._ctx_basico())
        assert "02LF01" in html

    def test_imagen_lectura_secuencia_2(self) -> None:
        ctx = self._ctx_basico()
        ctx["lecturas"] = [
            {"file_id": 101, "secuencia": 1},
            {"file_id": 102, "secuencia": 2},
        ]
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "02LF01" in html
        assert "02LF02" in html

    def test_incluye_boton_video_intro_si_hay_url(self) -> None:
        ctx = self._ctx_basico()
        ctx["video_intro_url"] = "https://player.vimeo.com/video/123"
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "012VINT01" in html
        assert "player.vimeo.com" in html

    def test_no_incluye_video_intro_si_url_es_none(self) -> None:
        html = MaterialFundamentalComposer().compose(
            COURSE_ID, self._ctx_basico()
        )
        assert "VINT" not in html

    def test_incluye_embed_podcast_si_hay_url(self) -> None:
        ctx = self._ctx_basico()
        ctx["podcast_url"] = "https://w.soundcloud.com/player/?url=..."
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "soundcloud" in html.lower()

    def test_incluye_iframe_vimeo_si_hay_url_content(self) -> None:
        ctx = self._ctx_basico()
        ctx["vimeo_url"] = "https://player.vimeo.com/video/456"
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "456" in html

    def test_boton_actividad_formativa(self) -> None:
        ctx = self._ctx_basico(unidad=1)
        ctx["actividades"] = [{"file_id": 301, "tipo": "formativa"}]
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "04AF01" in html
        assert "301" in html

    def test_boton_actividad_sumativa_u2(self) -> None:
        ctx = self._ctx_basico(unidad=2)
        ctx["actividades"] = [{"file_id": 302, "tipo": "sumativa"}]
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "03AE01" in html

    def test_boton_actividad_sumativa_u4(self) -> None:
        ctx = self._ctx_basico(unidad=4)
        ctx["actividades"] = [{"file_id": 404, "tipo": "sumativa"}]
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "03AE02" in html

    def test_boton_contenido_interactivo(self) -> None:
        ctx = self._ctx_basico()
        ctx["paginas_interactivas"] = [
            {"page_url": "unidad-1-contenido-interactivo", "numero": 1}
        ]
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "08CI01" in html
        assert "unidad-1-contenido-interactivo" in html

    def test_boton_material_fundamental_pdf(self) -> None:
        ctx = self._ctx_basico()
        ctx["mat_fund_pdfs"] = [{"file_id": 201}]
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "013INF00" in html
        assert "201" in html

    def test_imagen_video_intro_varía_por_unidad(self) -> None:
        for unidad in [1, 2, 3, 4]:
            ctx = self._ctx_basico(unidad=unidad)
            ctx["video_intro_url"] = f"https://player.vimeo.com/video/{unidad}"
            html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
            assert f"012VINT0{unidad}" in html

    def test_unidad_sin_recursos_genera_html_valido(self) -> None:
        ctx = {
            "unidad": 3,
            "lecturas": [],
            "mat_fund_pdfs": [],
            "actividades": [],
            "paginas_interactivas": [],
            "video_intro_url": None,
            "podcast_url": None,
            "vimeo_url": None,
        }
        html = MaterialFundamentalComposer().compose(COURSE_ID, ctx)
        assert "<p>" in html
        assert "Bannermaterialfundamental" in html


# ══════════════════════════════════════════════════════════════════════════════
# Tests: ComplementaryPageComposer
# ══════════════════════════════════════════════════════════════════════════════

class TestComplementaryPageComposer:

    def test_es_subclase_de_ipage_composer(self) -> None:
        assert issubclass(ComplementaryPageComposer, IPageComposer)

    def test_contiene_banner_material_complementario(self) -> None:
        html = ComplementaryPageComposer().compose(COURSE_ID, {
            "unidad": 1, "file_id": 111, "filename": "U1_Complemento.pdf"
        })
        assert "Bannermaterialcomplementario" in html

    def test_contiene_file_id_en_url(self) -> None:
        html = ComplementaryPageComposer().compose(COURSE_ID, {
            "unidad": 2, "file_id": 222, "filename": "U2_Complemento.pdf"
        })
        assert "222" in html

    def test_imagen_varía_por_unidad(self) -> None:
        for unidad in [1, 2, 3, 4]:
            html = ComplementaryPageComposer().compose(COURSE_ID, {
                "unidad": unidad,
                "file_id": 100 + unidad,
                "filename": f"U{unidad}_Complemento.pdf",
            })
            assert f"00LC0{unidad}" in html

    def test_contiene_tomodal_class(self) -> None:
        html = ComplementaryPageComposer().compose(COURSE_ID, {
            "unidad": 1, "file_id": 111, "filename": "test.pdf"
        })
        assert "toModal" in html

    def test_contiene_course_id_en_url(self) -> None:
        html = ComplementaryPageComposer().compose(COURSE_ID, {
            "unidad": 1, "file_id": 111, "filename": "test.pdf"
        })
        assert str(COURSE_ID) in html

    def test_lanza_key_error_sin_file_id(self) -> None:
        with pytest.raises(KeyError):
            ComplementaryPageComposer().compose(COURSE_ID, {"unidad": 1})


# ══════════════════════════════════════════════════════════════════════════════
# Tests: FrontPageComposer
# ══════════════════════════════════════════════════════════════════════════════

class TestFrontPageComposer:

    def _ctx_completo(self) -> dict:
        return {
            "course_name":  "Fundamentos de Ingeniería",
            "video_url":    "https://player.vimeo.com/video/999",
            "texto_inicio": "Texto de bienvenida al curso.",
            "texto_u1":     "Introducción a la unidad 1.",
            "texto_u2":     "Introducción a la unidad 2.",
            "texto_u3":     "Introducción a la unidad 3.",
            "texto_u4":     "Introducción a la unidad 4.",
            "texto_cierre": "Cierre del módulo.",
        }

    def test_es_subclase_de_ipage_composer(self) -> None:
        assert issubclass(FrontPageComposer, IPageComposer)

    def test_reemplaza_nombre_del_curso(self) -> None:
        html = FrontPageComposer().compose(COURSE_ID, self._ctx_completo())
        assert "Fundamentos de Ingeniería" in html
        assert "INSERTAR NOMBRE DEL CURSO" not in html

    def test_reemplaza_url_del_video(self) -> None:
        html = FrontPageComposer().compose(COURSE_ID, self._ctx_completo())
        assert "https://player.vimeo.com/video/999" in html
        assert "INSERTAR URL DEL VÍDEO" not in html

    def test_reemplaza_id_del_curso_en_urls(self) -> None:
        html = FrontPageComposer().compose(COURSE_ID, self._ctx_completo())
        assert f"courses/{COURSE_ID}" in html

    def test_reemplaza_texto_inicio(self) -> None:
        html = FrontPageComposer().compose(COURSE_ID, self._ctx_completo())
        assert "Texto de bienvenida al curso." in html

    def test_reemplaza_textos_de_unidades(self) -> None:
        html = FrontPageComposer().compose(COURSE_ID, self._ctx_completo())
        for n in [1, 2, 3, 4]:
            assert f"Introducción a la unidad {n}." in html

    def test_reemplaza_texto_cierre(self) -> None:
        html = FrontPageComposer().compose(COURSE_ID, self._ctx_completo())
        assert "Cierre del módulo." in html

    def test_ctx_vacio_retorna_template_con_placeholders(self) -> None:
        html = FrontPageComposer().compose(COURSE_ID, {})
        assert "INSERTAR NOMBRE DEL CURSO" in html

    def test_ctx_parcial_solo_reemplaza_campos_presentes(self) -> None:
        ctx = {"course_name": "Solo el nombre"}
        html = FrontPageComposer().compose(COURSE_ID, ctx)
        assert "Solo el nombre" in html
        assert "INSERTAR URL DEL VÍDEO" in html  # no se reemplazó

    def test_html_contiene_estructura_de_modulos(self) -> None:
        html = FrontPageComposer().compose(COURSE_ID, self._ctx_completo())
        assert "modulo-title-2" in html
        assert "modulo-desc" in html

    def test_reemplazar_modulo_funciona_correctamente(self) -> None:
        html_original = (
            '<p class="modulo-title-2">UNIDAD 1</p>'
            '<p>extra</p>'
            '<div class="modulo-desc">texto viejo</div>'
        )
        resultado = FrontPageComposer._reemplazar_modulo(
            html_original, "UNIDAD 1", "texto nuevo"
        )
        assert "texto nuevo" in resultado
        assert "texto viejo" not in resultado


# ══════════════════════════════════════════════════════════════════════════════
# Tests: PageComposerFactory
# ══════════════════════════════════════════════════════════════════════════════

class TestPageComposerFactory:

    def test_crea_iframe_composer(self) -> None:
        factory = PageComposerFactory()
        composer = factory.create(PageType.IFRAME)
        assert isinstance(composer, IframeComposer)

    def test_crea_material_fundamental_composer(self) -> None:
        factory = PageComposerFactory()
        composer = factory.create(PageType.MATERIAL_FUNDAMENTAL)
        assert isinstance(composer, MaterialFundamentalComposer)

    def test_crea_complementary_composer(self) -> None:
        factory = PageComposerFactory()
        composer = factory.create(PageType.COMPLEMENTARY)
        assert isinstance(composer, ComplementaryPageComposer)

    def test_crea_front_page_composer(self) -> None:
        factory = PageComposerFactory()
        composer = factory.create(PageType.FRONT)
        assert isinstance(composer, FrontPageComposer)

    def test_cada_create_retorna_instancia_nueva(self) -> None:
        factory = PageComposerFactory()
        c1 = factory.create(PageType.IFRAME)
        c2 = factory.create(PageType.IFRAME)
        assert c1 is not c2

    def test_todos_los_composers_son_ipage_composer(self) -> None:
        factory = PageComposerFactory()
        for tipo in factory.tipos_registrados():
            composer = factory.create(tipo)
            assert isinstance(composer, IPageComposer)

    def test_lanza_error_para_tipo_desconocido(self) -> None:
        factory = PageComposerFactory()
        with pytest.raises(ValueError, match="no registrado"):
            factory.create("tipo_que_no_existe")

    def test_register_nuevo_tipo(self) -> None:
        class MockComposer(IPageComposer):
            def compose(self, course_id: int, ctx: dict) -> str:
                return "<p>mock</p>"

        factory = PageComposerFactory()
        factory.register("mock", MockComposer)

        composer = factory.create("mock")
        assert isinstance(composer, MockComposer)

    def test_register_lanza_error_si_no_es_ipage_composer(self) -> None:
        factory = PageComposerFactory()
        with pytest.raises(TypeError):
            factory.register("invalido", str)  # type: ignore[arg-type]

    def test_tipos_registrados_incluye_los_4_defaults(self) -> None:
        factory = PageComposerFactory()
        tipos = factory.tipos_registrados()
        assert PageType.IFRAME in tipos
        assert PageType.MATERIAL_FUNDAMENTAL in tipos
        assert PageType.COMPLEMENTARY in tipos
        assert PageType.FRONT in tipos

    def test_tipos_registrados_retorna_lista(self) -> None:
        factory = PageComposerFactory()
        assert isinstance(factory.tipos_registrados(), list)