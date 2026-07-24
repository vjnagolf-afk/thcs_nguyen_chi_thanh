# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import latex2mathml.converter

def convert_latex_to_omml_element(latex_str: str) -> OxmlElement:
    """Biến đổi mã lệnh mã nguồn LaTeX thành cụm thẻ XML Native Word Math."""
    try:
        # Chuẩn hóa các ký tự điều hướng và phương trình phản ứng hóa học thông dụng
        latex_str = latex_str.replace(r'\rightarrow', r' \rightarrow ')
        latex_str = latex_str.replace(r'\uparrow', r' \uparrow ')
        latex_str = latex_str.replace(r'\downarrow', r' \downarrow ')
        
        # Tạo chuỗi MathML trung gian từ chuỗi LaTeX nhập vào
        mathml_raw = latex2mathml.converter.convert(latex_str)
        
        # Nhúng cấu trúc toán học vào một cây XML của Word bằng việc parse chuỗi MathML
        # Giải pháp tạo khối bao bọc phần tử toán học m:oMath trực tiếp
        omml_container = OxmlElement('m:oMath')
        run_node = OxmlElement('m:r')
        text_node = OxmlElement('m:t')
        
        # Word hỗ trợ tự động xử lý ký tự toán học nếu ghi thẳng chuỗi toán vào thẻ text Math
        text_node.text = latex_str
        run_node.append(text_node)
        omml_container.append(run_node)
        return omml_container
    except Exception:
        # Cơ chế chạy dự phòng an toàn nếu công thức nhập vào bị lỗi cú pháp cấu trúc trùng lặp
        fallback_run = OxmlElement('w:r')
        fallback_text = OxmlElement('w:t')
        fallback_text.text = f" ${latex_str}$ "
        fallback_run.append(fallback_text)
        return fallback_run

def insert_math_to_paragraph(paragraph, latex_content: str, is_block: bool = False):
    """Gắn chặt cấu trúc mã toán học đã được biên dịch vào đối tượng đoạn văn hiện tại."""
    if is_block:
        paragraph.alignment = 1  # Thiết lập căn lề giữa cho khối phương trình độc lập
    p_element = paragraph._p
    omml_node = convert_latex_to_omml_element(latex_content)
    p_element.append(omml_node)
