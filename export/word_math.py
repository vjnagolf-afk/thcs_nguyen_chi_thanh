import re
from docx.oxml import parse_xml
from docx.shared import RGBColor

class ScienceNormalizer:
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    SUP = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
    
    # Từ điển dịch ký tự LaTeX sang Unicode chuyên nghiệp
    TRANSLATION_MAP = {
        r'\perp': '⊥',
        r'\circ': '°',
        r'\widehat{A}': 'Â',
        r'\widehat{C}': 'Ĉ',
        r'\text{cm}': 'cm',
        r'\ne': '≠'
    }
    
    @classmethod
    def normalize(cls, text: str) -> str:
        # 1. Xử lý hóa học (Chỉ số trên/dưới)
        text = re.sub(r'([A-Za-z]+\d*)\^(\d*[+\-])', lambda m: m.group(1).translate(cls.SUB) + m.group(2).translate(cls.SUP), text)
        text = re.sub(r'([A-Z][a-z]?|\))(\d+)', lambda m: m.group(1) + m.group(2).translate(cls.SUB), text)
        
        # 2. Xử lý các ký tự toán học từ từ điển (Đã đưa vào trong hàm)
        for latex, unicode_char in cls.TRANSLATION_MAP.items():
            text = text.replace(latex, unicode_char)
            
        return text

class MathRenderer:
    @classmethod
    def render_inline_math(cls, paragraph, latex_str: str):
        # Dịch nhanh trước khi chèn
        clean_text = latex_str.replace(r'\frac{', '(').replace('}{', ')/(').replace('}', ')')
        run = paragraph.add_run(ScienceNormalizer.normalize(clean_text))
        run.font.name = 'Times New Roman'

    @classmethod
    def render_display_math(cls, doc, node):
        p = doc.add_paragraph()
        p.alignment = 1
        latex_content = node.get("content", "")
        # Chèn nội dung đã chuẩn hóa
        run = p.add_run(ScienceNormalizer.normalize(latex_content))
        run.font.name = 'Times New Roman'
        run.font.italic = True
