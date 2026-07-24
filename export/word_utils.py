# -*- coding: utf-8 -*-
import re
from docx.shared import Cm, Pt, RGBColor

# THỐNG NHẤT HỆ THỐNG LỀ TOÀN CỤC CHÍNH XÁC THEO ĐỀ XUẤT (Lỗi 6)
MARGIN_TOP = Cm(1.5)
MARGIN_BOTTOM = Cm(1.5)
MARGIN_LEFT = Cm(2.0)
MARGIN_RIGHT = Cm(1.5)

FONT_NAME = "Times New Roman"
CODE_FONT_NAME = "Courier New"

def clean_xml_forbidden_chars(text: str) -> str:
    """Loại bỏ ký tự điều khiển ASCII thấp tránh làm hỏng cấu trúc tệp Word."""
    if not isinstance(text, str):
        return str(text)
    illegal_chars = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
    return illegal_chars.sub('', text)
