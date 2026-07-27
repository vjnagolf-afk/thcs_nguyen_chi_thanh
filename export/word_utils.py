# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_styles.py
Nhiệm vụ: Quản lý tập trung toàn bộ định dạng văn bản (Typography), 
lề trang, font chữ và căn chỉnh (Alignment) cho file Word xuất ra.
Đảm bảo tuân thủ tuyệt đối quy định trình bày văn bản.
============================================================
"""

from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def apply_standard_margins(section):
    """
    Thiết lập lề trang theo quy định chuẩn:
    - Trên: 1.5 cm
    - Dưới: 1.5 cm
    - Trái: 2.0 cm
    - Phải: 1.5 cm
    """
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(1.5)

def set_run_font(run, font_name="Times New Roman", size_pt=13, bold=False, italic=False, color_rgb=None):
    """
    Thiết lập font chữ chuẩn Unicode cho một đoạn text (Run) trong Word.
    Giải quyết triệt để lỗi nhảy font khi có ký tự lạ.
    """
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if color_rgb:
        run.font.color.rgb = color_rgb
        
    # Ép font Unicode native ở cấp độ XML (Chống Word tự đổi sang font Calibri/Arial)
    try:
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:cs'), font_name)
    except Exception:
        pass

def setup_document_styles(doc):
    """
    Khởi tạo và chuẩn hóa các style mặc định của Document.
    Đảm bảo nội dung thông thường luôn được CĂN ĐỀU HAI BÊN (Justify).
    """
    try:
        # Style Normal (Đoạn văn thông thường)
        style_normal = doc.styles['Normal']
        style_normal.font.name = 'Times New Roman'
        style_normal.font.size = Pt(13)
        style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY # Bắt buộc căn đều
        style_normal.paragraph_format.space_after = Pt(6)
        style_normal.paragraph_format.line_spacing = 1.15
        
        # Có thể mở rộng định dạng cho các Heading ở đây nếu template chưa có sẵn
    except Exception:
        pass

def align_paragraph(paragraph, alignment_type):
    """
    Tiện ích hỗ trợ ép căn lề riêng biệt (Trái, Giữa, Phải, Đều) cho từng paragraph.
    Dùng cho Tiêu đề, Hình ảnh, Bảng biểu (những thành phần không áp dụng Justify).
    """
    paragraph.alignment = alignment_type
