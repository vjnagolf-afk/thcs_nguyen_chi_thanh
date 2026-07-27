# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_styles.py

NHIỆM VỤ:
- Thiết lập khổ giấy và lề trang theo template / quy định.
- Thiết lập hệ thống Style Word thống nhất.
- Thiết lập font Times New Roman an toàn cho tiếng Việt.
- Hỗ trợ căn chỉnh đoạn văn.
- Hỗ trợ shading, border, cell border.
- Hỗ trợ bảng, callout, code block, heading, list.
- Không chứa logic AI.
- Không chứa logic phân tích Markdown.
- Không xử lý trực tiếp công thức.
  Công thức phải được chuyển qua export.word_math.

NGUYÊN TẮC:
1. Nếu có template, ưu tiên giữ cấu trúc template.
2. Không ép toàn bộ tài liệu về lề 3 cm trái / 2 cm phải.
3. Lề mặc định:
       Top    = 1.2 cm
       Bottom = 1.2 cm
       Left   = 2.0 cm
       Right  = 1.5 cm
4. Nội dung văn bản thường căn đều hai bên.
5. Heading không căn đều.
6. Công thức, hình ảnh, bảng có quy tắc riêng.
7. Không tạo các class trùng lặp giữa word_styles.py
   và word_tables.py.

============================================================
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import docx

from docx.enum.section import WD_SECTION
from docx.enum.table import (
    WD_CELL_VERTICAL_ALIGNMENT,
    WD_TABLE_ALIGNMENT,
)
from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_LINE_SPACING,
)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import (
    Cm,
    Inches,
    Pt,
    RGBColor,
)


logger = logging.getLogger("WordStyles")


# ============================================================
# CẤU HÌNH TRANG
# ============================================================

class PageConfig:
    """
    Cấu hình trang A4.

    Có thể điều chỉnh tập trung tại đây.
    """

    PAGE_WIDTH_CM = 21.0
    PAGE_HEIGHT_CM = 29.7

    # Theo yêu cầu:
    # Top    : 1.0 – 1.5 cm
    # Bottom : 1.0 – 1.5 cm
    # Left   : 1.5 – 2.0 cm
    # Right  : 1.0 – 1.5 cm

    TOP_CM = 1.2
    BOTTOM_CM = 1.2
    LEFT_CM = 2.0
    RIGHT_CM = 1.5

    HEADER_CM = 0.5
    FOOTER_CM = 0.5

    GUTTER_CM = 0.0


# ============================================================
# CẤU HÌNH STYLE
# ============================================================

class StyleConfig:
    """
    Cấu hình font và khoảng cách.
    """

    FONT_NAME = "Times New Roman"

    NORMAL_SIZE = 13
    HEADING_1_SIZE = 16
    HEADING_2_SIZE = 14
    HEADING_3_SIZE = 13

    CODE_SIZE = 10.5

    # Line spacing:
    # 1.0 = single
    # 1.15 = Word-like
    # 1.5 = giãn dòng 1.5
    NORMAL_LINE_SPACING = 1.15

    NORMAL_SPACE_BEFORE_PT = 0
    NORMAL_SPACE_AFTER_PT = 6

    HEADING_1_BEFORE_PT = 12
    HEADING_1_AFTER_PT = 6

    HEADING_2_BEFORE_PT = 8
    HEADING_2_AFTER_PT = 4

    HEADING_3_BEFORE_PT = 6
    HEADING_3_AFTER_PT = 3

    LIST_SPACE_AFTER_PT = 3


# ============================================================
# XML HELPERS
# ============================================================

class XmlHelpers:
    """
    Các thao tác XML dùng chung cho Word.
    """

    # --------------------------------------------------------
    # FONT
    # --------------------------------------------------------

    @staticmethod
    def set_font_safely(
        run,
        font_name: str = StyleConfig.FONT_NAME,
    ) -> None:
        """
        Thiết lập font đầy đủ cho Latin, East Asia và Complex Script.

        Đây là cách an toàn hơn chỉ dùng:
            run.font.name = "Times New Roman"

        vì Word có thể vẫn sử dụng font khác cho tiếng Việt
        hoặc ký tự Unicode.
        """

        if run is None:
            return

        try:
            run.font.name = font_name

            r_pr = run._element.get_or_add_rPr()

            r_fonts = r_pr.find(
                qn("w:rFonts")
            )

            if r_fonts is None:
                r_fonts = OxmlElement("w:rFonts")
                r_pr.append(r_fonts)

            for attribute in (
                "ascii",
                "hAnsi",
                "eastAsia",
                "cs",
            ):
                r_fonts.set(
                    qn(f"w:{attribute}"),
                    font_name,
                )

        except Exception as exc:
            logger.warning(
                "Không thể thiết lập font: %s",
                exc,
            )

    # --------------------------------------------------------
    # PARAGRAPH KEEP
    # --------------------------------------------------------

    @staticmethod
    def set_keep_with_next(
        paragraph,
        value: bool = True,
    ) -> None:

        p_pr = paragraph._p.get_or_add_pPr()

        element = p_pr.find(
            qn("w:keepNext")
        )

        if value:

            if element is None:
                element = OxmlElement("w:keepNext")
                p_pr.append(element)

        elif element is not None:

            p_pr.remove(element)

    @staticmethod
    def set_keep_together(
        paragraph,
        value: bool = True,
    ) -> None:

        p_pr = paragraph._p.get_or_add_pPr()

        element = p_pr.find(
            qn("w:keepLines")
        )

        if value:

            if element is None:
                element = OxmlElement("w:keepLines")
                p_pr.append(element)

        elif element is not None:

            p_pr.remove(element)

    # --------------------------------------------------------
    # SHADING
    # --------------------------------------------------------

    @staticmethod
    def apply_paragraph_shading(
        paragraph,
        color_hex: str = "F5F5F5",
    ) -> None:
        """
        Tô nền toàn bộ paragraph.
        """

        if paragraph is None:
            return

        p_pr = paragraph._p.get_or_add_pPr()

        shd = p_pr.find(
            qn("w:shd")
        )

        if shd is None:

            shd = OxmlElement("w:shd")
            p_pr.append(shd)

        shd.set(
            qn("w:val"),
            "clear",
        )

        shd.set(
            qn("w:color"),
            "auto",
        )

        shd.set(
            qn("w:fill"),
            color_hex.replace("#", "").upper(),
        )

    @staticmethod
    def apply_cell_shading(
        cell,
        color_hex: str = "FFFFFF",
    ) -> None:

        if cell is None:
            return

        tc_pr = cell._tc.get_or_add_tcPr()

        shd = tc_pr.find(
            qn("w:shd")
        )

        if shd is None:

            shd = OxmlElement("w:shd")
            tc_pr.append(shd)

        shd.set(
            qn("w:val"),
            "clear",
        )

        shd.set(
            qn("w:color"),
            "auto",
        )

        shd.set(
            qn("w:fill"),
            color_hex.replace("#", "").upper(),
        )

    # --------------------------------------------------------
    # PARAGRAPH BORDER
    # --------------------------------------------------------

    @staticmethod
    def apply_bottom_border(
        paragraph,
        color_hex: str = "CCCCCC",
        size: int = 8,
        space: int = 4,
    ) -> None:

        p_pr = paragraph._p.get_or_add_pPr()

        p_bdr = p_pr.find(
            qn("w:pBdr")
        )

        if p_bdr is None:

            p_bdr = OxmlElement("w:pBdr")
            p_pr.append(p_bdr)

        old_bottom = p_bdr.find(
            qn("w:bottom")
        )

        if old_bottom is not None:
            p_bdr.remove(old_bottom)

        bottom = OxmlElement("w:bottom")

        bottom.set(
            qn("w:val"),
            "single",
        )

        bottom.set(
            qn("w:sz"),
            str(size),
        )

        bottom.set(
            qn("w:space"),
            str(space),
        )

        bottom.set(
            qn("w:color"),
            color_hex.replace("#", "").upper(),
        )

        p_bdr.append(bottom)

    # --------------------------------------------------------
    # CELL BORDER
    # --------------------------------------------------------

    @staticmethod
    def set_cell_borders(
        cell,
        *,
        top: Optional[dict] = None,
        bottom: Optional[dict] = None,
        left: Optional[dict] = None,
        right: Optional[dict] = None,
        inside_h: Optional[dict] = None,
        inside_v: Optional[dict] = None,
    ) -> None:
        """
        Thiết lập viền ô Word.

        Ví dụ:

            XmlHelpers.set_cell_borders(
                cell,
                top={
                    "val": "single",
                    "sz": "8",
                    "color": "000000",
                },
            )
        """

        if cell is None:
            return

        tc_pr = cell._tc.get_or_add_tcPr()

        tc_borders = tc_pr.find(
            qn("w:tcBorders")
        )

        if tc_borders is None:

            tc_borders = OxmlElement("w:tcBorders")
            tc_pr.append(tc_borders)

        border_map = {
            "top": top,
            "bottom": bottom,
            "left": left,
            "right": right,
            "insideH": inside_h,
            "insideV": inside_v,
        }

        for side, config in border_map.items():

            if config is None:
                continue

            tag = qn(
                f"w:{side}"
            )

            element = tc_borders.find(tag)

            if element is None:

                element = OxmlElement(
                    f"w:{side}"
                )

                tc_borders.append(element)

            for key, value in config.items():

                element.set(
                    qn(f"w:{key}"),
                    str(value),
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
        Đơn vị Word: twentieths of a point (twips-like XML unit).

        Giúp nội dung bảng không bị dính sát biên.
        """

        if cell is None:
            return

        tc_pr = cell._tc.get_or_add_tcPr()

        tc_mar = tc_pr.find(
            qn("w:tcMar")
        )

        if tc_mar is None:

            tc_mar = OxmlElement("w:tcMar")
            tc_pr.append(tc_mar)

        margins = {
            "top": top,
            "start": start,
            "bottom": bottom,
            "end": end,
        }

        for side, value in margins.items():

            element = tc_mar.find(
                qn(f"w:{side}")
            )

            if element is None:

                element = OxmlElement(
                    f"w:{side}"
                )

                tc_mar.append(element)

            element.set(
                qn("w:w"),
                str(value),
            )

            element.set(
                qn("w:type"),
                "dxa",
            )

    # --------------------------------------------------------
    # TABLE WIDTH
    # --------------------------------------------------------

    @staticmethod
    def set_table_width(
        table,
        width_inches: float,
    ) -> None:

        if table is None:
            return

        tbl_pr = table._tbl.tblPr

        tbl_w = tbl_pr.find(
            qn("w:tblW")
        )

        if tbl_w is None:

            tbl_w = OxmlElement("w:tblW")
            tbl_pr.append(tbl_w)

        # 1 inch = 1440 twentieths of a point
        width = int(
            width_inches * 1440
        )

        tbl_w.set(
            qn("w:w"),
            str(width),
        )

        tbl_w.set(
            qn("w:type"),
            "dxa",
        )

    # --------------------------------------------------------
    # TABLE LAYOUT
    # --------------------------------------------------------

    @staticmethod
    def set_table_fixed_layout(
        table,
    ) -> None:

        if table is None:
            return

        tbl_pr = table._tbl.tblPr

        tbl_layout = tbl_pr.find(
            qn("w:tblLayout")
        )

        if tbl_layout is None:

            tbl_layout = OxmlElement(
                "w:tblLayout"
            )

            tbl_pr.append(tbl_layout)

        tbl_layout.set(
            qn("w:type"),
            "fixed",
        )

    # --------------------------------------------------------
    # ROW CANNOT SPLIT
    # --------------------------------------------------------

    @staticmethod
    def prevent_row_split(
        row,
    ) -> None:

        if row is None:
            return

        tr_pr = row._tr.get_or_add_trPr()

        cant_split = tr_pr.find(
            qn("w:cantSplit")
        )

        if cant_split is None:

            cant_split = OxmlElement(
                "w:cantSplit"
            )

            tr_pr.append(cant_split)

    # --------------------------------------------------------
    # REPEAT HEADER ROW
    # --------------------------------------------------------

    @staticmethod
    def set_repeat_table_header(
        row,
    ) -> None:

        if row is None:
            return

        tr_pr = row._tr.get_or_add_trPr()

        tbl_header = tr_pr.find(
            qn("w:tblHeader")
        )

        if tbl_header is None:

            tbl_header = OxmlElement(
                "w:tblHeader"
            )

            tr_pr.append(tbl_header)

    # --------------------------------------------------------
    # VERTICAL ALIGNMENT
    # --------------------------------------------------------

    @staticmethod
    def set_cell_vertical_alignment(
        cell,
        alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER,
    ) -> None:

        if cell is None:
            return

        cell.vertical_alignment = alignment


# ============================================================
# BASE STYLE SETUP
# ============================================================

class BaseStyleSetup:
    """
    Thiết lập nền tảng cho toàn bộ tài liệu Word.
    """

    @staticmethod
    def setup_page(
        doc: docx.Document,
    ) -> None:
        """
        Thiết lập A4 và lề trang.

        Nếu template đã có section riêng, hàm vẫn chỉ điều chỉnh
        các thuộc tính trang cần thiết, không tạo section mới.
        """

        for section in doc.sections:

            section.page_width = Cm(
                PageConfig.PAGE_WIDTH_CM
            )

            section.page_height = Cm(
                PageConfig.PAGE_HEIGHT_CM
            )

            section.top_margin = Cm(
                PageConfig.TOP_CM
            )

            section.bottom_margin = Cm(
                PageConfig.BOTTOM_CM
            )

            section.left_margin = Cm(
                PageConfig.LEFT_CM
            )

            section.right_margin = Cm(
                PageConfig.RIGHT_CM
            )

            section.header_distance = Cm(
                PageConfig.HEADER_CM
            )

            section.footer_distance = Cm(
                PageConfig.FOOTER_CM
            )

            section.gutter = Cm(
                PageConfig.GUTTER_CM
            )

    @staticmethod
    def setup_base_styles(
        doc: docx.Document,
    ) -> None:
        """
        Thiết lập toàn bộ style nền tảng.
        """

        if doc is None:
            return

        BaseStyleSetup.setup_page(
            doc
        )

        styles_config = {

            "Normal": {
                "size": StyleConfig.NORMAL_SIZE,
                "bold": False,
                "italic": False,
                "before": StyleConfig.NORMAL_SPACE_BEFORE_PT,
                "after": StyleConfig.NORMAL_SPACE_AFTER_PT,
                "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
                "line_spacing": StyleConfig.NORMAL_LINE_SPACING,
            },

            "Body Text": {
                "size": StyleConfig.NORMAL_SIZE,
                "bold": False,
                "italic": False,
                "before": 0,
                "after": 6,
                "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
                "line_spacing": StyleConfig.NORMAL_LINE_SPACING,
            },

            "Heading 1": {
                "size": StyleConfig.HEADING_1_SIZE,
                "bold": True,
                "italic": False,
                "before": StyleConfig.HEADING_1_BEFORE_PT,
                "after": StyleConfig.HEADING_1_AFTER_PT,
                "alignment": WD_ALIGN_PARAGRAPH.CENTER,
                "line_spacing": 1.0,
            },

            "Heading 2": {
                "size": StyleConfig.HEADING_2_SIZE,
                "bold": True,
                "italic": False,
                "before": StyleConfig.HEADING_2_BEFORE_PT,
                "after": StyleConfig.HEADING_2_AFTER_PT,
                "alignment": WD_ALIGN_PARAGRAPH.LEFT,
                "line_spacing": 1.0,
            },

            "Heading 3": {
                "size": StyleConfig.HEADING_3_SIZE,
                "bold": True,
                "italic": False,
                "before": StyleConfig.HEADING_3_BEFORE_PT,
                "after": StyleConfig.HEADING_3_AFTER_PT,
                "alignment": WD_ALIGN_PARAGRAPH.LEFT,
                "line_spacing": 1.0,
            },

            "List Bullet": {
                "size": StyleConfig.NORMAL_SIZE,
                "bold": False,
                "italic": False,
                "before": 0,
                "after": StyleConfig.LIST_SPACE_AFTER_PT,
                "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
                "line_spacing": StyleConfig.NORMAL_LINE_SPACING,
            },

            "List Number": {
                "size": StyleConfig.NORMAL_SIZE,
                "bold": False,
                "italic": False,
                "before": 0,
                "after": StyleConfig.LIST_SPACE_AFTER_PT,
                "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
                "line_spacing": StyleConfig.NORMAL_LINE_SPACING,
            },

        }

        for style_name, config in styles_config.items():

            try:

                style = doc.styles[
                    style_name
                ]

            except KeyError:

                logger.warning(
                    "Không tìm thấy style: %s",
                    style_name,
                )

                continue

            style.font.name = (
                StyleConfig.FONT_NAME
            )

            style.font.size = Pt(
                config["size"]
            )

            style.font.bold = (
                config["bold"]
            )

            style.font.italic = (
                config["italic"]
            )

            style.font.color.rgb = RGBColor(
                0,
                0,
                0,
            )

            style.paragraph_format.space_before = Pt(
                config["before"]
            )

            style.paragraph_format.space_after = Pt(
                config["after"]
            )

            style.paragraph_format.line_spacing = (
                config["line_spacing"]
            )

            style.paragraph_format.alignment = (
                config["alignment"]
            )

            style.paragraph_format.widow_control = True

            if style_name.startswith(
                "Heading"
            ):

                style.paragraph_format.keep_with_next = True

    @staticmethod
    def setup_document(
        doc: docx.Document,
    ) -> docx.Document:
        """
        API chính.

        Dùng:

            BaseStyleSetup.setup_document(doc)

        """

        BaseStyleSetup.setup_base_styles(
            doc
        )

        return doc


# ============================================================
# BLOCK RENDERER
# ============================================================

class BlockRenderer:
    """
    Render các block Markdown / AST.
    """

    @classmethod
    def render_heading(
        cls,
        doc,
        node: dict,
        text_renderer: Any,
        math_renderer: Any,
    ):
        """
        Render heading.

        Công thức trong heading vẫn phải được chuyển qua
        math_renderer.
        """

        level = node.get(
            "level",
            1,
        )

        try:
            level = int(level)

        except (
            TypeError,
            ValueError,
        ):
            level = 1

        level = max(
            1,
            min(
                level,
                3,
            ),
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

        XmlHelpers.set_keep_with_next(
            paragraph,
            True,
        )

        XmlHelpers.set_keep_together(
            paragraph,
            True,
        )

        if text_renderer is not None:

            text_renderer.render_inline_tokens(
                paragraph,
                node.get(
                    "tokens",
                    [],
                ),
                math_renderer,
            )

        for run in paragraph.runs:

            XmlHelpers.set_font_safely(
                run,
                StyleConfig.FONT_NAME,
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

        level = node.get(
            "level",
            1,
        )

        try:
            level = max(
                1,
                int(level),
            )

        except (
            TypeError,
            ValueError,
        ):
            level = 1

        # Không thụt quá sâu.
        # Mỗi cấp tăng 0.5 cm.
        left_cm = 0.5 + (
            (level - 1) * 0.5
        )

        paragraph.paragraph_format.left_indent = Cm(
            left_cm
        )

        paragraph.paragraph_format.first_line_indent = Cm(
            -0.5
        )

        paragraph.paragraph_format.alignment = (
            WD_ALIGN_PARAGRAPH.JUSTIFY
        )

        if text_renderer is not None:

            text_renderer.render_inline_tokens(
                paragraph,
                node.get(
                    "tokens",
                    [],
                ),
                math_renderer,
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

        level = node.get(
            "level",
            1,
        )

        try:
            level = max(
                1,
                int(level),
            )

        except (
            TypeError,
            ValueError,
        ):
            level = 1

        paragraph.paragraph_format.left_indent = Cm(
            0.5 * level
        )

        paragraph.paragraph_format.alignment = (
            WD_ALIGN_PARAGRAPH.JUSTIFY
        )

        checked = bool(
            node.get(
                "checked",
                False,
            )
        )

        box_char = (
            "☑ "
            if checked
            else "☐ "
        )

        run_box = paragraph.add_run(
            box_char
        )

        # Segoe UI Symbol có độ tương thích tốt hơn MS Gothic
        # với các hệ thống Windows hiện đại.
        XmlHelpers.set_font_safely(
            run_box,
            "Segoe UI Symbol",
        )

        run_box.bold = True

        if text_renderer is not None:

            text_renderer.render_inline_tokens(
                paragraph,
                node.get(
                    "tokens",
                    [],
                ),
                math_renderer,
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

        paragraph.paragraph_format.left_indent = Cm(
            0.5
        )

        paragraph.paragraph_format.right_indent = Cm(
            0.5
        )

        paragraph.paragraph_format.space_before = Pt(
            4
        )

        paragraph.paragraph_format.space_after = Pt(
            4
        )

        paragraph.paragraph_format.alignment = (
            WD_ALIGN_PARAGRAPH.LEFT
        )

        XmlHelpers.apply_paragraph_shading(
            paragraph,
            "F5F5F5",
        )

        run = paragraph.add_run(
            node.get(
                "text",
                "",
            )
        )

        run.font.size = Pt(
            StyleConfig.CODE_SIZE
        )

        XmlHelpers.set_font_safely(
            run,
            "Courier New",
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
            "quote",
        )

        if style == "warning":

            bg_color = "FFF5F5"
            border_color = "C00000"

        elif style == "tip":

            bg_color = "F0F7FF"
            border_color = "0070C0"

        else:

            bg_color = "F9F9F9"
            border_color = "808080"

        table = doc.add_table(
            rows=1,
            cols=1,
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
            0,
        )

        XmlHelpers.apply_cell_shading(
            cell,
            bg_color,
        )

        XmlHelpers.set_cell_margins(
            cell,
            top=100,
            start=140,
            bottom=100,
            end=140,
        )

        XmlHelpers.set_cell_borders(
            cell,

            left={
                "val": "single",
                "sz": "20",
                "space": "0",
                "color": border_color,
            },

            top={
                "val": "nil",
            },

            bottom={
                "val": "nil",
            },

            right={
                "val": "nil",
            },
        )

        cell.vertical_alignment = (
            WD_CELL_VERTICAL_ALIGNMENT.CENTER
        )

        children = node.get(
            "children",
            [],
        )

        # Xóa paragraph rỗng mặc định nếu cần
        paragraph = cell.paragraphs[0]

        for index, child in enumerate(
            children
        ):

            if index > 0:

                paragraph = cell.add_paragraph()

            paragraph.paragraph_format.space_after = Pt(
                4
            )

            paragraph.paragraph_format.alignment = (
                WD_ALIGN_PARAGRAPH.JUSTIFY
            )

            if (
                child.get("type")
                == "paragraph"
            ):

                if text_renderer is not None:

                    text_renderer.render_inline_tokens(
                        paragraph,
                        child.get(
                            "tokens",
                            [],
                        ),
                        math_renderer,
                    )

        return table


# ============================================================
# EXPORT API
# ============================================================

__all__ = [
    "PageConfig",
    "StyleConfig",
    "XmlHelpers",
    "BaseStyleSetup",
    "BlockRenderer",
    "ContainerRenderer",
]
