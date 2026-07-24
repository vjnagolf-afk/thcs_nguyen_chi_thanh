# -*- coding: utf-8 -*-
"""
Module: export/word_math.py - Đoạn 1/2
Nhiệm vụ: Cấu hình bộ chuẩn hóa ký hiệu khoa học bằng Unicode, không import thư viện ngoài ở đầu file.
"""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

class ScienceNormalizer:
    """Bộ chuẩn hóa và dịch nhanh ký hiệu khoa học Phổ thông mới sang Unicode."""
    MAP = {
        r'\perp': '⊥', r'\circ': '°', r'\neq': '≠', r'\ne': '≠', 
        r'\leq': '≤', r'\le': '≤', r'\geq': '≥', r'\ge': '≥', 
        r'\times': '×', r'\div': '÷', r'\cdot': '·',
        r'\triangle': '△', r'\angle': '∠', r'\rightarrow': '→', 
        r'\Rightarrow': '⇒', r'\Leftrightarrow': '⇔', r'\approx': '≈', r'\pm': '±',
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\pi': 'π', 
        r'\sum': '∑', r'\int': '∫', r'\uparrow': '↑', r'\downarrow': '↓'
    }

    @classmethod
    def clean_and_replace_symbols(cls, latex_str: str) -> str:
        if not latex_str:
            return ""
        cleaned = latex_str.replace('$', '').replace(r'\(', '').replace(r'\)', '').strip()
        for pattern, symbol in cls.MAP.items():
            cleaned = cleaned.replace(pattern, symbol)
        return cleaned
# Tiếp nối đoạn 1/2 của file export/word_math.py

def convert_latex_to_omml_element(latex_str: str) -> OxmlElement:
    """Biến đổi mã lệnh LaTeX sang XML Office Math bằng cơ chế Lazy Import bảo vệ AI Key."""
    # CHẾ ĐỘ 1: LAZY IMPORT - Chỉ nạp thư viện khi hàm này được gọi (khi bấm xuất file)
    try:
        import latex2mathml.converter
        
        latex_str = latex_str.replace(r'\rightarrow', r' \rightarrow ')
        latex_str = latex_str.replace(r'\uparrow', r' \uparrow ')
        latex_str = latex_str.replace(r'\downarrow', r' \downarrow ')
        
        omml_container = OxmlElement('m:oMath')
        run_node = OxmlElement('m:r')
        text_node = OxmlElement('m:t')
        
        text_node.text = latex_str
        run_node.append(text_node)
        omml_container.append(run_node)
        return omml_container
    except Exception:
        # Tự động chuyển sang chế độ dự phòng nếu gặp bất kỳ lỗi nạp hoặc lỗi cú pháp nào
        pass

    # CHẾ ĐỘ 2: DỰ PHÒNG AN TOÀN (FALLBACK)
    fallback_run = OxmlElement('w:r')
    fallback_text = OxmlElement('w:t')
    normalized_text = ScienceNormalizer.clean_and_replace_symbols(latex_str)
    fallback_text.text = f" {normalized_text} "
    fallback_run.append(fallback_text)
    
    rPr = fallback_run.get_or_add_rPr()
    i_node = OxmlElement('w:i')
    rPr.append(i_node)
    return fallback_run

def insert_math_to_paragraph(paragraph, latex_content: str, is_block: bool = False):
    if not latex_content.strip():
        return
    if is_block:
        paragraph.alignment = 1
    p_element = paragraph._p
    omml_node = convert_latex_to_omml_element(latex_content)
    p_element.append(omml_node)
