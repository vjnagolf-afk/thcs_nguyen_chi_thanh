# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_math.py
Nhiệm vụ: Chuẩn hóa và chuyển đổi mã lệnh LaTeX sang ký tự Unicode 
trực quan, hiển thị sắc nét bằng font Cambria Math trong Word.
============================================================
"""

import re
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

class ScienceNormalizer:
    """Bộ chuẩn hóa và dịch ký hiệu khoa học Phổ thông sang Unicode trực quan."""
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
        
        # Làm sạch các thẻ bọc LaTeX cơ bản
        cleaned = latex_str.replace('$', '').replace(r'\(', '').replace(r'\)', '').strip()
        
        # 1. Xử lý phân số \frac{a}{b} -> (a)/(b)
        cleaned = re.sub(r'\\frac\s*\{([^}]*)\}\s*\{([^}]*)\}', r'(\1)/(\2)', cleaned)
        
        # 2. Xử lý căn bậc hai \sqrt{x} -> √(x)
        cleaned = re.sub(r'\\sqrt\s*\{([^}]*)\}', r'√(\1)', cleaned)
        
        # 3. Thay thế các ký hiệu toán học và chữ Hy Lạp
        for pattern, symbol in cls.MAP.items():
            cleaned = cleaned.replace(pattern, symbol)
            
        # 4. Xử lý các dấu ngoặc và dọn dẹp ngoặc nhọn dư thừa
        cleaned = cleaned.replace(r'\left(', '(').replace(r'\right)', ')')
        cleaned = cleaned.replace(r'\left[', '[').replace(r'\right]', ']')
        cleaned = re.sub(r'\{([^}]*)\}', r'\1', cleaned)
        
        return cleaned

def insert_math_to_paragraph(paragraph, latex_content: str, is_block: bool = False):
    """
    Chèn công thức toán học vào đoạn văn Word dưới dạng văn bản Unicode 
    với định dạng font Cambria Math và kiểu chữ nghiêng chuẩn toán học.
    """
    if not latex_content or not latex_content.strip():
        return
        
    try:
        normalized_text = ScienceNormalizer.clean_and_replace_symbols(latex_content)
        
        if is_block:
            paragraph.alignment = 1  # Căn giữa dòng cho khối công thức
            run = paragraph.add_run(f"   {normalized_text}   ")
        else:
            run = paragraph.add_run(f" {normalized_text} ")
            
        # Thiết lập định dạng chuẩn cho công thức toán học trên Word
        run.font.name = 'Cambria Math'
        run.font.size = Pt(13)
        run.italic = True
        
    except Exception:
        # Fallback an toàn tuyệt đối nếu xảy ra lỗi định dạng
        run = paragraph.add_run(f" {latex_content} ")
        run.italic = True
