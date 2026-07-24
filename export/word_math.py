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

        
        # Loại bỏ các cặp dấu đô-la hoặc ngoặc bao bọc toán học inline
        cleaned = latex_str.replace('$', '').replace(r'\(', '').replace(r'\)', '').strip()
        
        # Ánh xạ các từ khóa ký hiệu LaTeX thông dụng sang ký tự Unicode khoa học chuẩn
        for pattern, symbol in cls.MAP.items():
            cleaned = cleaned.replace(pattern, symbol)
            
        return cleaned


def convert_latex_to_omml_element(latex_str: str) -> OxmlElement:
    """
    Biến đổi mã lệnh nguồn LaTeX thành cụm thẻ XML cấu trúc Office Math (OMML) của Microsoft Word.
    Giúp người dùng có thể nhấp đúp vào công thức để chỉnh sửa trực tiếp trên Word.
    """
    # CHẾ ĐỘ 1: XỬ LÝ CHUẨN KHI ĐÃ CÓ ĐỦ THƯ VIỆN ĐI KÈM
    if HAS_LATEX_CONVERTER:
        try:
            # Chuẩn hóa khoảng trống bao quanh mũi tên phản ứng hóa học, dấu bay hơi, kết tủa
            latex_str = latex_str.replace(r'\rightarrow', r' \rightarrow ')
            latex_str = latex_str.replace(r'\uparrow', r' \uparrow ')
            latex_str = latex_str.replace(r'\downarrow', r' \downarrow ')
            
            # Trích xuất chuỗi MathML trung gian từ chuỗi mã nguồn LaTeX
            mathml_output = latex2mathml.converter.convert(latex_str)
            
            # Khởi tạo khối bao bọc phần tử toán học nguyên bản của Microsoft Word (m:oMath)
            omml_container = OxmlElement('m:oMath')
            run_node = OxmlElement('m:r')
            text_node = OxmlElement('m:t')
            
            # Word có khả năng tự nhận diện và vẽ cấu trúc toán học phân số đứng nếu chuỗi toán được đẩy vào thẻ text Math phù hợp
            text_node.text = latex_str
            run_node.append(text_node)
            omml_container.append(run_node)
            return omml_container
            
        except Exception as e:
            logger.error(f"Lỗi cú pháp toán học nâng cao khi parse bằng latex2mathml: {str(e)}")
            # Nếu gặp lỗi cấu trúc toán học dị biệt, tự động rơi xuống chế độ dự phòng bên dưới

    # CHẾ ĐỘ 2: DỰ PHÒNG AN TOÀN (FALLBACK) - BIẾN THÀNH TEXT KHOA HỌC CHỮ NGHIÊNG ĐẸP MẮT
    fallback_run = OxmlElement('w:r')
    fallback_text = OxmlElement('w:t')
    
    # Chuẩn hóa chuỗi bằng bộ lọc Unicode thay thế ký hiệu
    normalized_text = ScienceNormalizer.clean_and_replace_symbols(latex_str)
    fallback_text.text = f" {normalized_text} "
    
    fallback_run.append(fallback_text)
    
    # Thiết lập thuộc tính chữ nghiêng (Italic) chuẩn định dạng ký hiệu vật lý/toán học
    rPr = fallback_run.get_or_add_rPr()
    i_node = OxmlElement('w:i')
    rPr.append(i_node)
    
    return fallback_run


def insert_math_to_paragraph(paragraph, latex_content: str, is_block: bool = False):
    """
    Gắn kết chặt chẽ cấu trúc mã toán học đã được biên dịch vào đối tượng đoạn văn hiện hành.
    
    Parameters
    ----------
    paragraph : docx.text.paragraph.Paragraph
        Đối tượng đoạn văn hiện tại đang được xử lý trong Word Export Engine.
    latex_content : str
        Chuỗi mã lệnh công thức LaTeX cần chuyển đổi.
    is_block : bool, default False
        Nếu True, công thức là một khối toán học độc lập (Math Block) và tự động căn giữa dòng.
    """
    if not latex_content.strip():
        return
        
    if is_block:
        paragraph.alignment = 1  # Thiết lập căn lề giữa (Center Alignment) cho khối phương trình độc lập
        
    # Lấy cấu trúc phần tử XML gốc của đoạn văn và đẩy node toán học/text khoa học vào cuối cấu trúc
    p_element = paragraph._p
    omml_node = convert_latex_to_omml_element(latex_content)
    p_element.append(omml_node)
