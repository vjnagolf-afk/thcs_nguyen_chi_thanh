# -*- coding: utf-8 -*-
from docx.shared import Pt, RGBColor
from .word_utils import MARGIN_TOP, MARGIN_BOTTOM, MARGIN_LEFT, MARGIN_RIGHT, FONT_NAME

def setup_document_styles(doc):
    """Định cấu hình kích thước lề trang và phân cấp font chữ chuẩn tài liệu Việt Nam."""
    # Áp dụng lề trang nhất quán (Sửa lỗi 2 & Lỗi 6)
    for section in doc.sections:
        section.top_margin = MARGIN_TOP
        section.bottom_margin = MARGIN_BOTTOM
        section.left_margin = MARGIN_LEFT
        section.right_margin = MARGIN_RIGHT

    # Định dạng thuộc tính Normal Style
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = FONT_NAME
    font.size = Pt(13)
    font.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(6)

    # Khởi tạo hoặc cập nhật định dạng các Heading
    headings_cfg = {
        'Heading 1': Pt(16),
        'Heading 2': Pt(14),
        'Heading 3': Pt(13)
    }
    for name, size in headings_cfg.items():
        if name in doc.styles:
            h_style = doc.styles[name]
            h_font = h_style.font
            h_font.name = FONT_NAME
            h_font.bold = True
            h_font.color.rgb = RGBColor(0, 0, 0)
            h_font.size = size
            h_style.paragraph_format.space_before = Pt(12)
            h_style.paragraph_format.space_after = Pt(4)
            h_style.paragraph_format.keep_with_next = True
