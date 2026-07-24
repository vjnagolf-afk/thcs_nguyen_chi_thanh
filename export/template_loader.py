# -*- coding: utf-8 -*-
import os
from docx import Document
from .word_utils import clean_xml_forbidden_chars

class TemplateLoader:
    """Bộ nạp và trích xuất dữ liệu biến số động trên tệp biểu mẫu (.docx)."""
    
    @classmethod
    def load(cls, template_path: str = None) -> Document:
        """Đọc tệp tin mẫu từ đường dẫn lưu trữ, nếu trống sẽ tạo văn bản sạch."""
        if template_path and os.path.exists(template_path) and template_path.lower().endswith('.docx'):
            return Document(template_path)
        return Document()

    @classmethod
    def inject_variables(cls, doc: Document, context_vars: dict):
        """Thay thế hàng loạt các biến nhãn dán dạng {{tên_biến}} xuất hiện trong văn bản."""
        if not context_vars:
            return doc
            
        def replace_text_in_paragraph(p):
            for run in p.runs:
                for key, val in context_vars.items():
                    placeholder = f"{{{{{key}}}}}"
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, clean_xml_forbidden_chars(str(val)))

        # Quét và thay đổi trên hệ thống Paragraph chính
        for paragraph in doc.paragraphs:
            replace_text_in_paragraph(paragraph)
            
        # Quét dọn nội dung bên trong các bảng hiện hữu trên Template
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_text_in_paragraph(paragraph)
                        
        # Quét dọn thông tin trên tiêu đề trang (Header/Footer)
        for section in doc.sections:
            for paragraph in section.header.paragraphs:
                replace_text_in_paragraph(paragraph)
            for paragraph in section.footer.paragraphs:
                replace_text_in_paragraph(paragraph)
                
        return doc
