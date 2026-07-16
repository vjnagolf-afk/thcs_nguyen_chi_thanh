import re
from typing import List, Tuple
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import qn, nsdecls

class ScienceNormalizer:
    # Bảng ánh xạ chỉ số dưới (Subscript) và chỉ số trên (Superscript) bằng Unicode
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    SUP = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
    
    # 4. TRANSLATION_MAP mở rộng đầy đủ ký hiệu giáo dục THCS
    TRANSLATION_MAP = {
        r'\perp': '⊥', r'\circ': '°', r'\ne': '≠', r'\le': '≤', r'\ge': '≥',
        r'\times': '×', r'\div': '÷', r'\pm': '±', r'\in': '∈', r'\notin': '∉',
        r'\subset': '⊂', r'\infty': '∞', r'\triangle': '△', r'\angle': '∠',
        r'\rightarrow': '→', r'\Rightarrow': '⇒', r'\Leftrightarrow': '⇔',
        r'\approx': '≈', r'\cong': '≅', r'\sim': '~', r'\propto': '∝',
        r'\forall': '∀', r'\exists': '∃',
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\lambda': 'λ',
        r'\mu': 'μ', r'\omega': 'ω', r'\pi': 'π', r'\theta': 'θ', r'\sigma': 'σ',
        r'\text{cm}': 'cm', r'\text{m}': 'm', r'\text{dm}': 'dm', r'\text{mm}': 'mm', r'\text{kg}': 'kg'
    }

    @classmethod
    def _parse_nested_braces(cls, text: str, start_pos: int) -> Tuple[str, int]:
        """3. Thuật toán Stack bóc tách chính xác các cặp dấu ngoặc {} lồng nhau"""
        stack = []
        content = []
        for i in range(start_pos, len(text)):
            char = text[i]
            if char == '{':
                stack.append('{')
                if len(stack) > 1:
                    content.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:
                        return "".join(content), i
                    else:
                        content.append(char)
            else:
                content.append(char)
        return "".join(content), len(text)

    @classmethod
    def convert_frac_recursive(cls, text: str) -> str:
        """Chuyển đổi đệ quy cấu trúc \frac{tử}{mẫu} lồng nhau thành chuỗi Unicode phẳng"""
        while r'\frac{' in text:
            idx = text.find(r'\frac{')
            # Tìm tử số
            tu_so, end_tu_idx = cls._parse_nested_braces(text, idx + 5)
            # Tìm mẫu số bắt đầu ngay sau dấu ngoặc nhọn của tử số
            if end_tu_idx + 1 < len(text) and text[end_tu_idx + 1] == '{':
                mau_so, end_mau_idx = cls._parse_nested_braces(text, end_tu_idx + 1)
                
                # Đệ quy xử lý nếu bên trong tử hoặc mẫu chứa phân số khác
                tu_so_clean = cls.convert_frac_recursive(tu_so)
                mau_so_clean = cls.convert_frac_recursive(mau_so)
                
                # Thay thế cụm phân số hiện tại bằng chuỗi phẳng dạng ((tử)/(mẫu))
                old_frac = text[idx:end_mau_idx + 1]
                new_frac = f"(({tu_so_clean})/({mau_so_clean}))"
                text = text.replace(old_frac, new_frac, 1)
            else:
                break
        return text

    @classmethod
    def normalize_chemistry(cls, text: str) -> str:
        """5. Xử lý nâng cao các cấu trúc Hóa học phức tạp (Ca(OH)2, CuSO4.5H2O, Fe3+)"""
        # Thay thế dấu chấm liên kết tinh thể ngậm nước bằng dấu chấm tâm Unicode tròn đẹp (•)
        text = re.sub(r'([A-Za-z0-9\]\)])\s*\.\s*(\d*[A-Z][a-z]?)', r'\1•\2', text)
        
        # Biến đổi các số đứng sau ký tự hóa học hoặc dấu đóng ngoặc đơn thành Chỉ số dưới (Subscript)
        # Bắt giữ cả trường hợp như CuSO₄, Ca(OH)₂
        text = re.sub(r'([A-Z][a-z]?|\))(\d+)', lambda m: m.group(1) + m.group(2).translate(cls.SUB), text)
        
        # Biến đổi số đứng sau các nguyên tố trong nhóm chỉ số dưới đã hạ (đảm bảo quét sạch)
        text = re.sub(r'([₀₁₂₃₄₅₆₇₈₉])(\d+)', lambda m: m.group(1) + m.group(2).translate(cls.SUB), text)

        # Biến đổi số mũ Điện tích / Ion thành Chỉ số trên (Superscript) ví dụ: Fe^3+ -> Fe³⁺
        text = re.sub(r'([A-Za-z₀₁₂₃₄₅₆₇₈₉\)]+)\^(\d*[+\-])', lambda m: m.group(1) + m.group(2).translate(cls.SUP), text)
        return text

    @classmethod
    def normalize(cls, text: str) -> str:
        """Hàm điều phối làm sạch tổng thể văn bản trước khi đưa vào Inline Run"""
        if not text:
            return ""

        text = text.replace('$', '').replace(r'\(', '').replace(r'\)', '').strip()

        # Áp dụng bộ giải mã phân số lồng nhau
        text = cls.convert_frac_recursive(text)

        # Áp dụng bộ giải mã căn thức cơ bản
        text = re.sub(r'\\sqrt\{([\s\S]+?)\}', r'√(\1)', text)
        
        # Áp dụng bộ lọc cấu trúc hình học góc
        text = re.sub(r'\\widehat\{([A-Za-z]+)\}', lambda m: f"∠{m.group(1)}" if len(m.group(1)) > 1 else f"{m.group(1)}̂", text)

        # Áp dụng bộ lọc dọn dẹp cấu trúc hóa học nâng cao
        text = cls.normalize_chemistry(text)

        # Dịch chuyển các ký tự từ điển hệ thống
        for latex, unicode_char in cls.TRANSLATION_MAP.items():
            text = text.replace(latex, unicode_char)

        # Xóa các định dạng text bọc thừa của LaTeX
        text = re.sub(r'\\text\{([\s\S]+?)\}', r'\1', text)
        text = re.sub(r'\\mathrm\{([\s\S]+?)\}', r'\1', text)

        return text


class MathRenderer:
    @staticmethod
    def _set_font_safely(run, font_name: str = "Times New Roman"):
        """6. Giải quyết triệt để lỗi Word tự động nhảy Font về Cambria trên môi trường Windows"""
        run.font.name = font_name
        rPr = run._element.get_or_add_rPr()
        
        # Tạo thẻ rFonts để ép cứng cấu trúc XML nội tại của Microsoft Word
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:eastAsia'), font_name)
        rFonts.set(qn('w:cs'), font_name)
        rPr.append(rFonts)

    @classmethod
    def render_inline_math(cls, paragraph, latex_str: str):
        """Chèn công thức toán nội dòng dạng Unicode phẳng, định dạng chữ nghiêng"""
        clean_text = ScienceNormalizer.normalize(latex_str)
        run = paragraph.add_run(clean_text)
        
        # Khóa cứng Font và bật thuộc tính in nghiêng sư phạm cho biến số
        cls._set_font_safely(run, "Times New Roman")
        run.font.italic = True

    @classmethod
    def _latex_to_omml(cls, latex_str: str) -> str:
        """Biến đổi mã LaTeX thô sang thẻ XML cấu trúc OMML chính thống của Microsoft Office"""
        # Làm sạch chuỗi bao quanh dấu khối toán học
        latex_clean = latex_str.replace('$$', '').replace(r'\[', '').replace(r'\]', '').strip()
        
        # Chuẩn hóa cấu trúc phân số thuần để Microsoft Word đọc hiểu thẻ phân chia \frac
        latex_clean = re.sub(r'\\frac\{([\s\S]+?)\}\{([\s\S]+?)\}', r'{\1 \\over \2}', latex_clean)

        # Khai báo không gian tên XML của Microsoft Office Math (m:oMath)
        xslt_omml = (
            f'<w:p {nsdecls("w")}>'
            f'<m:oMathPara {nsdecls("m")}>'
            f'<m:oMath><m:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/></w:rPr>'
            f'<m:t>{latex_clean}</m:t></m:r></m:oMath>'
            f'</m:oMathPara></w:p>'
        )
        return xslt_omml

    @classmethod
    def render_display_math(cls, doc, latex_str: str):
        """7. Khởi tạo Khối Phương trình Toán học độc lập chuẩn native bằng cấu trúc XML OMML"""
        try:
            # Tạo chuỗi XML cấu trúc toán học chính thống
            omml_xml_string = cls._latex_to_omml(latex_str)
            omml_element = parse_xml(omml_xml_string)
            
            # Gắn đoạn XML Toán học trực tiếp vào cấu trúc cây tài liệu của file Word
            doc._body._element.append(omml_element)
            
            # Lấy paragraph vừa tạo cuối cùng để căn lề giữa trang
            last_p = doc.paragraphs[-1]
            last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        except Exception:
            # Cơ chế Dự phòng (Fallback): Nếu biên dịch XML lỗi, quay lại chèn text phẳng căn giữa an toàn
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            clean_text = ScienceNormalizer.normalize(latex_str)
            run = p.add_run(clean_text)
            
            cls._set_font_safely(run, "Times New Roman")
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.italic = True
