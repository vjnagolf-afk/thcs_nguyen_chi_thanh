# -*- coding: utf-8 -*-
"""
============================================================
WORD STYLES & DOCUMENT LAYOUT ENGINE
FILE: export/word_styles.py
============================================================

Nhiệm vụ:
- Thiết lập khổ giấy và lề tài liệu.
- Chuẩn hóa font chữ.
- Chuẩn hóa paragraph.
- Cung cấp XML helpers dùng chung.
- Cung cấp renderer cho heading, list, checkbox, code block, callout.

Nguyên tắc:
- Không tự ý tạo cấu hình lề khác nhau ở các module khác.
- Không phá vỡ bố cục của template nếu template đã có cấu hình.
- Nội dung văn bản thông thường căn đều 2 bên.
- Tiêu đề, công thức, bảng, hình ảnh và các block đặc biệt có căn chỉnh riêng.
"""

from __future__ import annotations

from typing import Any, Optional

import docx

from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_LINE_SPACING,
)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


# ============================================================
# CẤU HÌNH TRUNG TÂM
# ============================================================

class WordLayoutConfig:
    """
    Cấu hình định dạng Word dùng chung cho toàn bộ hệ thống.
    """

    # --------------------------------------------------------
    # KHỔ GIẤY
    # --------------------------------------------------------

    PAGE_WIDTH_CM = 21.0
    PAGE_HEIGHT_CM = 29.7

    # --------------------------------------------------------
    # LỀ TRANG
    #
    # Theo yêu cầu:
    # Top:    1.0 - 1.5 cm
    # Bottom: 1.0 - 1.5 cm
    # Left:   1.5 - 2.0 cm
    # Right:  1.0 - 1.5 cm
    #
    # Cấu hình mặc định:
    # Top:    1.5 cm
    # Bottom: 1.5 cm
    # Left:   2.0 cm
    # Right:  1.5 cm
    # --------------------------------------------------------

    TOP_MARGIN_CM = 1.5
    BOTTOM_MARGIN_CM = 1.5
    LEFT_MARGIN_CM = 2.0
    RIGHT_MARGIN_CM = 1.5

    # --------------------------------------------------------
    # FONT
    # --------------------------------------------------------

    DEFAULT_FONT = "Times New Roman"
    MONOSPACE_FONT = "Courier New"

    DEFAULT_FONT_SIZE = 13
    SMALL_FONT_SIZE = 10.5
    FORMULA_FONT_SIZE = 13

    # --------------------------------------------------------
    # ĐOẠN VĂN
    # --------------------------------------------------------

    LINE_SPACING = 1.15

    SPACE_BEFORE = 0
    SPACE_AFTER = 6

    FIRST_LINE_INDENT_CM = 1.0

    # --------------------------------------------------------
    # VÙNG NỘI DUNG
    # --------------------------------------------------------

    CONTENT_WIDTH_CM = (
        PAGE_WIDTH_CM
        - LEFT_MARGIN_CM
        - RIGHT_MARGIN_CM
    )

    CONTENT_WIDTH_INCHES = (
        CONTENT_WIDTH_CM / 2.54
    )


# ============================================================
# BASE STYLE SETUP
# ============================================================

class BaseStyleSetup:
    """
    Thiết lập toàn bộ style nền cho tài liệu Word.

    Lưu ý:
    - Nếu tài liệu được tạo từ template, cấu hình của template
      được ưu tiên khi cần thiết.
    - Hàm này chỉ chuẩn hóa các style nền và không tạo nội dung.
    """

    @staticmethod
    def setup_page_layout(
        doc: docx.Document,
        preserve_template_layout: bool = False,
    ) -> None:
        """
        Thiết lập khổ giấy và lề trang.

        preserve_template_layout=True:
            Không ghi đè cấu hình lề hiện có của template.

        preserve_template_layout=False:
            Áp dụng cấu hình chuẩn của hệ thống.
        """

        for section in doc.sections:

            # Khổ giấy A4
            section.page_width = Cm(
                WordLayoutConfig.PAGE_WIDTH_CM
            )

            section.page_height = Cm(
                WordLayoutConfig.PAGE_HEIGHT_CM
            )

            if preserve_template_layout:
                continue

            section.top_margin = Cm(
                WordLayoutConfig.TOP_MARGIN_CM
            )

            section.bottom_margin = Cm(
                WordLayoutConfig.BOTTOM_MARGIN_CM
            )

            section.left_margin = Cm(
                WordLayoutConfig.LEFT_MARGIN_CM
            )

            section.right_margin = Cm(
                WordLayoutConfig.RIGHT_MARGIN_CM
            )

    @staticmethod
    def _configure_style(
        style,
        font_name: str,
        font_size: float,
        bold: bool = False,
        italic: bool = False,
        alignment: Optional[int] = None,
        space_before: float = 0,
        space_after: float = 0,
        first_line_indent_cm: Optional[float] = None,
        line_spacing: float = 1.15,
        keep_with_next: bool = False,
    ) -> None:

        # ----------------------------------------------------
        # FONT
        # ----------------------------------------------------

        style.font.name = font_name
        style.font.size = Pt(font_size)
        style.font.bold = bold
        style.font.italic = italic
        style.font.color.rgb = RGBColor(
            0,
            0,
            0
        )

        # ----------------------------------------------------
        # PARAGRAPH
        # ----------------------------------------------------

        paragraph_format = style.paragraph_format

        if alignment is not None:
            paragraph_format.alignment = alignment

        paragraph_format.space_before = Pt(
            space_before
        )

        paragraph_format.space_after = Pt(
            space_after
        )

        paragraph_format.line_spacing = (
            line_spacing
        )

        paragraph_format.line_spacing_rule = (
            WD_LINE_SPACING.MULTIPLE
        )

        paragraph_format.keep_with_next = (
            keep_with_next
        )

        if first_line_indent_cm is not None:
            paragraph_format.first_line_indent = Cm(
                first_line_indent_cm
            )

        # ----------------------------------------------------
        # FONT XML
        # ----------------------------------------------------

        BaseStyleSetup._set_style_font_xml(
            style,
            font_name
        )

    @staticmethod
    def _set_style_font_xml(
        style,
        font_name: str,
    ) -> None:

        style_element = style._element

        rPr = style_element.find(
            qn("w:rPr")
        )

        if rPr is None:

            rPr = OxmlElement(
                "w:rPr"
            )

            style_element.append(
                rPr
            )

        rFonts = rPr.find(
            qn("w:rFonts")
        )

        if rFonts is None:

            rFonts = OxmlElement(
                "w:rFonts"
            )

            rPr.append(
                rFonts
            )

        for attr in (
            "ascii",
            "hAnsi",
            "eastAsia",
            "cs",
        ):

            rFonts.set(
                qn(f"w:{attr}"),
                font_name
            )

    @classmethod
    def setup_base_styles(
        cls,
        doc: docx.Document,
        preserve_template_layout: bool = False,
    ) -> None:
        """
        Thiết lập toàn bộ style nền.

        Đây là entry point chính của module.
        """

        cls.setup_page_layout(
            doc,
            preserve_template_layout
        )

        # ----------------------------------------------------
        # NORMAL
        # ----------------------------------------------------

        cls._configure_style(
            doc.styles["Normal"],
            font_name=WordLayoutConfig.DEFAULT_FONT,
            font_size=WordLayoutConfig.DEFAULT_FONT_SIZE,
            alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
            space_before=0,
            space_after=WordLayoutConfig.SPACE_AFTER,
            first_line_indent_cm=(
                WordLayoutConfig.FIRST_LINE_INDENT_CM
            ),
            line_spacing=WordLayoutConfig.LINE_SPACING,
        )

        # ----------------------------------------------------
        # HEADING 1
        # ----------------------------------------------------

        cls._configure_style(
            doc.styles["Heading 1"],
            font_name=WordLayoutConfig.DEFAULT_FONT,
            font_size=16,
            bold=True,
            alignment=WD_ALIGN_PARAGRAPH.CENTER,
            space_before=12,
            space_after=6,
            line_spacing=1.0,
            keep_with_next=True,
        )

        # ----------------------------------------------------
        # HEADING 2
        # ----------------------------------------------------

        cls._configure_style(
            doc.styles["Heading 2"],
            font_name=WordLayoutConfig.DEFAULT_FONT,
            font_size=14,
            bold=True,
            alignment=WD_ALIGN_PARAGRAPH.LEFT,
            space_before=8,
            space_after=4,
            line_spacing=1.0,
            keep_with_next=True,
        )

        # ----------------------------------------------------
        # HEADING 3
        # ----------------------------------------------------

        cls._configure_style(
            doc.styles["Heading 3"],
            font_name=WordLayoutConfig.DEFAULT_FONT,
            font_size=13,
            bold=True,
            italic=True,
            alignment=WD_ALIGN_PARAGRAPH.LEFT,
            space_before=6,
            space_after=2,
            line_spacing=1.0,
            keep_with_next=True,
        )

        # ----------------------------------------------------
        # LIST BULLET
        # ----------------------------------------------------

        cls._configure_style(
            doc.styles["List Bullet"],
            font_name=WordLayoutConfig.DEFAULT_FONT,
            font_size=13,
            alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
            space_before=0,
            space_after=3,
            line_spacing=WordLayoutConfig.LINE_SPACING,
        )

        # ----------------------------------------------------
        # LIST NUMBER
        # ----------------------------------------------------

        cls._configure_style(
            doc.styles["List Number"],
            font_name=WordLayoutConfig.DEFAULT_FONT,
            font_size=13,
            alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
            space_before=0,
            space_after=3,
            line_spacing=WordLayoutConfig.LINE_SPACING,
        )

    @classmethod
    def setup_document(
        cls,
        doc: docx.Document,
        preserve_template_layout: bool = False,
    ) -> docx.Document:
        """
        Hàm tiện ích để thiết lập toàn bộ document.
        """

        cls.setup_base_styles(
            doc,
            preserve_template_layout
        )

        return doc


# ============================================================
# XML HELPERS
# ============================================================

class XmlHelpers:
    """
    Các thao tác XML an toàn cho WordprocessingML.
    """

    # --------------------------------------------------------
    # FONT RUN
    # --------------------------------------------------------

    @staticmethod
    def set_font_safely(
        run,
        font_name: str = WordLayoutConfig.DEFAULT_FONT,
    ) -> None:

        run.font.name = font_name

        rPr = run._element.get_or_add_rPr()

        rFonts = rPr.find(
            qn("w:rFonts")
        )

        if rFonts is None:

            rFonts = OxmlElement(
                "w:rFonts"
            )

            rPr.append(
                rFonts
            )

        for attr in (
            "ascii",
            "hAnsi",
            "eastAsia",
            "cs",
        ):

            rFonts.set(
                qn(f"w:{attr}"),
                font_name
            )

    # --------------------------------------------------------
    # PARAGRAPH SHADING
    # --------------------------------------------------------

    @staticmethod
    def apply_paragraph_shading(
        paragraph,
        color_hex: str = "F5F5F5",
    ) -> None:

        pPr = paragraph._element.get_or_add_pPr()

        shd = pPr.find(
            qn("w:shd")
        )

        if shd is None:

            shd = OxmlElement(
                "w:shd"
            )

            pPr.append(
                shd
            )

        shd.set(
            qn("w:val"),
            "clear"
        )

        shd.set(
            qn("w:color"),
            "auto"
        )

        shd.set(
            qn("w:fill"),
            color_hex
        )

    # --------------------------------------------------------
    # PARAGRAPH BORDER
    # --------------------------------------------------------

    @staticmethod
    def apply_bottom_border(
        paragraph,
        color_hex: str = "CCCCCC",
        size: int = 8,
    ) -> None:

        pPr = paragraph._element.get_or_add_pPr()

        pBdr = pPr.find(
            qn("w:pBdr")
        )

        if pBdr is None:

            pBdr = OxmlElement(
                "w:pBdr"
            )

            pPr.append(
                pBdr
            )

        bottom = pBdr.find(
            qn("w:bottom")
        )

        if bottom is None:

            bottom = OxmlElement(
                "w:bottom"
            )

            pBdr.append(
                bottom
            )

        bottom.set(
            qn("w:val"),
            "single"
        )

        bottom.set(
            qn("w:sz"),
            str(size)
        )

        bottom.set(
            qn("w:space"),
            "4"
        )

        bottom.set(
            qn("w:color"),
            color_hex
        )

    # --------------------------------------------------------
    # CELL SHADING
    # --------------------------------------------------------

    @staticmethod
    def apply_cell_shading(
        cell,
        color_hex: str,
    ) -> None:

        tcPr = cell._tc.get_or_add_tcPr()

        shd = tcPr.find(
            qn("w:shd")
        )

        if shd is None:

            shd = OxmlElement(
                "w:shd"
            )

            tcPr.append(
                shd
            )

        shd.set(
            qn("w:val"),
            "clear"
        )

        shd.set(
            qn("w:color"),
            "auto"
        )

        shd.set(
            qn("w:fill"),
            color_hex
        )

    # --------------------------------------------------------
    # CELL MARGINS
    # --------------------------------------------------------

    @staticmethod
    def set_cell_margins(
        cell,
        top: int = 80,
        start: int = 100,
        bottom: int = 80,
        end: int = 100,
    ) -> None:
        """
        Đơn vị: twentieths of a point (twips).
        """

        tc = cell._tc

        tcPr = tc.get_or_add_tcPr()

        tcMar = tcPr.find(
            qn("w:tcMar")
        )

        if tcMar is None:

            tcMar = OxmlElement(
                "w:tcMar"
            )

            tcPr.append(
                tcMar
            )

        margins = {
            "top": top,
            "start": start,
            "bottom": bottom,
            "end": end,
        }

        for margin_name, value in margins.items():

            node = tcMar.find(
                qn(f"w:{margin_name}")
            )

            if node is None:

                node = OxmlElement(
                    f"w:{margin_name}"
                )

                tcMar.append(
                    node
                )

            node.set(
                qn("w:w"),
                str(value)
            )

            node.set(
                qn("w:type"),
                "dxa"
            )

    # --------------------------------------------------------
    # CELL BORDERS
    # --------------------------------------------------------

    @staticmethod
    def set_cell_borders(
        cell,
        *,
        top: Optional[dict] = None,
        bottom: Optional[dict] = None,
        start: Optional[dict] = None,
        end: Optional[dict] = None,
        insideH: Optional[dict] = None,
        insideV: Optional[dict] = None,
    ) -> None:

        tcPr = cell._tc.get_or_add_tcPr()

        tcBorders = tcPr.find(
            qn("w:tcBorders")
        )

        if tcBorders is None:

            tcBorders = OxmlElement(
                "w:tcBorders"
            )

            tcPr.append(
                tcBorders
            )

        border_config = {
            "top": top,
            "bottom": bottom,
            "start": start,
            "end": end,
            "insideH": insideH,
            "insideV": insideV,
        }

        for side, config in border_config.items():

            if config is None:
                continue

            border = tcBorders.find(
                qn(f"w:{side}")
            )

            if border is None:

                border = OxmlElement(
                    f"w:{side}"
                )

                tcBorders.append(
                    border
                )

            for key, value in config.items():

                border.set(
                    qn(f"w:{key}"),
                    str(value)
                )

    # --------------------------------------------------------
    # TABLE WIDTH
    # --------------------------------------------------------

    @staticmethod
    def set_table_width(
        table,
        width_twips: int,
    ) -> None:

        tblPr = table._tbl.tblPr

        tblW = tblPr.find(
            qn("w:tblW")
        )

        if tblW is None:

            tblW = OxmlElement(
                "w:tblW"
            )

            tblPr.append(
                tblW
            )

        tblW.set(
            qn("w:w"),
            str(width_twips)
        )

        tblW.set(
            qn("w:type"),
            "dxa"
        )

    # --------------------------------------------------------
    # TABLE LAYOUT
    # --------------------------------------------------------

    @staticmethod
    def set_table_fixed_layout(
        table,
    ) -> None:

        tblPr = table._tbl.tblPr

        tblLayout = tblPr.find(
            qn("w:tblLayout")
        )

        if tblLayout is None:

            tblLayout = OxmlElement(
                "w:tblLayout"
            )

            tblPr.append(
                tblLayout
            )

        tblLayout.set(
            qn("w:type"),
            "fixed"
        )

    # --------------------------------------------------------
    # REPEAT TABLE HEADER
    # --------------------------------------------------------

    @staticmethod
    def repeat_table_header(
        row,
    ) -> None:

        trPr = row._tr.get_or_add_trPr()

        tblHeader = trPr.find(
            qn("w:tblHeader")
        )

        if tblHeader is None:

            tblHeader = OxmlElement(
                "w:tblHeader"
            )

            trPr.append(
                tblHeader
            )

        tblHeader.set(
            qn("w:val"),
            "true"
        )

    # --------------------------------------------------------
    # KEEP PARAGRAPH TOGETHER
    # --------------------------------------------------------

    @staticmethod
    def keep_paragraph_together(
        paragraph,
        value: bool = True,
    ) -> None:

        pPr = paragraph._element.get_or_add_pPr()

        keepLines = pPr.find(
            qn("w:keepLines")
        )

        if keepLines is None:

            keepLines = OxmlElement(
                "w:keepLines"
            )

            pPr.append(
                keepLines
            )

        if value:

            keepLines.set(
                qn("w:val"),
                "true"
            )

        else:

            keepLines.set(
                qn("w:val"),
                "false"
            )


# ============================================================
# BLOCK RENDERER
# ============================================================

class BlockRenderer:

    @classmethod
    def render_heading(
        cls,
        doc,
        node: dict,
        text_renderer: Any,
        math_renderer: Any,
    ):

        level = int(
            node.get(
                "level",
                1
            )
        )

        level = min(
            max(
                level,
                1
            ),
            3
        )

        paragraph = doc.add_paragraph(
            style=f"Heading {level}"
        )

        if level == 1:

            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

        else:

            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.LEFT
            )

        paragraph.paragraph_format.keep_with_next = True

        text_renderer.render_inline_tokens(
            paragraph,
            node.get(
                "tokens",
                []
            ),
            math_renderer
        )

        for run in paragraph.runs:

            XmlHelpers.set_font_safely(
                run,
                WordLayoutConfig.DEFAULT_FONT
            )

        return paragraph

    @classmethod
    def render_list_item(
        cls,
        doc,
        node: dict,
        text_renderer: Any,
        math_renderer: Any,
    ):

        style_name = (
            "List Number"
            if node.get("style") == "number"
            else "List Bullet"
        )

        paragraph = doc.add_paragraph(
            style=style_name
        )

        level = max(
            int(
                node.get(
                    "level",
                    1
                )
            ),
            1
        )

        # Thụt lề có kiểm soát
        left_indent_cm = (
            0.63
            + (level - 1) * 0.63
        )

        paragraph.paragraph_format.left_indent = Cm(
            left_indent_cm
        )

        paragraph.paragraph_format.first_line_indent = Cm(
            -0.63
        )

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.JUSTIFY
        )

        text_renderer.render_inline_tokens(
            paragraph,
            node.get(
                "tokens",
                []
            ),
            math_renderer
        )

        return paragraph

    @classmethod
    def render_checkbox(
        cls,
        doc,
        node: dict,
        text_renderer: Any,
        math_renderer: Any,
    ):

        paragraph = doc.add_paragraph()

        level = max(
            int(
                node.get(
                    "level",
                    1
                )
            ),
            1
        )

        paragraph.paragraph_format.left_indent = Cm(
            0.63 * level
        )

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.JUSTIFY
        )

        box_char = (
            "☑ "
            if node.get(
                "checked",
                False
            )
            else "☐ "
        )

        run_box = paragraph.add_run(
            box_char
        )

        XmlHelpers.set_font_safely(
            run_box,
            "Segoe UI Symbol"
        )

        run_box.bold = True

        text_renderer.render_inline_tokens(
            paragraph,
            node.get(
                "tokens",
                []
            ),
            math_renderer
        )

        return paragraph


# ============================================================
# CONTAINER RENDERER
# ============================================================

class ContainerRenderer:

    @classmethod
    def render_code_block(
        cls,
        doc,
        node: dict,
    ):

        paragraph = doc.add_paragraph()

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.LEFT
        )

        paragraph.paragraph_format.left_indent = Cm(
            0.5
        )

        paragraph.paragraph_format.space_before = Pt(
            4
        )

        paragraph.paragraph_format.space_after = Pt(
            4
        )

        paragraph.paragraph_format.line_spacing = 1.0

        XmlHelpers.apply_paragraph_shading(
            paragraph,
            "F5F5F5"
        )

        run = paragraph.add_run(
            node.get(
                "text",
                ""
            )
        )

        run.font.size = Pt(
            WordLayoutConfig.SMALL_FONT_SIZE
        )

        XmlHelpers.set_font_safely(
            run,
            WordLayoutConfig.MONOSPACE_FONT
        )

        return paragraph

    @classmethod
    def render_callout(
        cls,
        doc,
        node: dict,
        text_renderer: Any,
        math_renderer: Any,
    ):

        style = node.get(
            "style",
            "quote"
        )

        color_config = {

            "warning": {
                "background": "FFF5F5",
                "border": "FF3B30",
            },

            "tip": {
                "background": "F0F7FF",
                "border": "007AFF",
            },

            "quote": {
                "background": "F9F9F9",
                "border": "8E8E93",
            },

        }

        config = color_config.get(
            style,
            color_config["quote"]
        )

        table = doc.add_table(
            rows=1,
            cols=1
        )

        table.alignment = (
            WD_TABLE_ALIGNMENT.CENTER
        )

        table.autofit = False

        XmlHelpers.set_table_fixed_layout(
            table
        )

        cell = table.cell(
            0,
            0
        )

        cell.vertical_alignment = (
            WD_CELL_VERTICAL_ALIGNMENT.CENTER
        )

        XmlHelpers.apply_cell_shading(
            cell,
            config["background"]
        )

        XmlHelpers.set_cell_margins(
            cell,
            top=100,
            start=160,
            bottom=100,
            end=160,
        )

        XmlHelpers.set_cell_borders(
            cell,

            top={
                "val": "nil"
            },

            bottom={
                "val": "nil"
            },

            start={
                "val": "single",
                "sz": "24",
                "space": "0",
                "color": config["border"],
            },

            end={
                "val": "nil"
            },
        )

        children = node.get(
            "children",
            []
        )

        # Xóa paragraph rỗng mặc định nếu có thể
        first_paragraph = cell.paragraphs[0]

        if not children:

            first_paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.JUSTIFY
            )

            return table

        for index, child in enumerate(children):

            if index == 0:

                paragraph = first_paragraph

            else:

                paragraph = cell.add_paragraph()

            paragraph.paragraph_format.space_after = Pt(
                4
            )

            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.JUSTIFY
            )

            if child.get("type") == "paragraph":

                text_renderer.render_inline_tokens(
                    paragraph,
                    child.get(
                        "tokens",
                        []
                    ),
                    math_renderer
                )

        return table


# ============================================================
# HÀM TIỆN ÍCH CẤP MODULE
# ============================================================

def setup_document_styles(
    doc: docx.Document,
    preserve_template_layout: bool = False,
) -> docx.Document:
    """
    API đơn giản để các module khác sử dụng.
    """

    return BaseStyleSetup.setup_document(
        doc,
        preserve_template_layout
    )


__all__ = [
    "WordLayoutConfig",
    "BaseStyleSetup",
    "XmlHelpers",
    "BlockRenderer",
    "ContainerRenderer",
    "setup_document_styles",
]
