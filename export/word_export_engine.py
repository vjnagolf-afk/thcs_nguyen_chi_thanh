# -*- coding: utf-8 -*-
"""
============================================================
BỘ ĐIỀU PHỐI ĐẦU NÃO KẾT XUẤT WORD (ĐÃ GIA CỐ BẪY LỖI AN TOÀN)
============================================================
"""

import io
import logging
from docx import Document
from .template_loader import TemplateLoader
from .word_styles import setup_document_styles
from .markdown_tokenizer import MarkdownTokenizer
from .word_math import insert_math_to_paragraph
from .word_tables import process_and_draw_markdown_table
from .word_images import insert_image_to_docx
from .word_utils import clean_xml_forbidden_chars

logger = logging.getLogger(__name__)

def export_markdown_to_word(markdown_content: str, template_file_path: str = None, meta_variables: dict = None) -> io.BytesIO:
    """
    Hàm đầu não thực thi phân tích toàn diện mã Markdown và kết xuất thành File Word dạng Stream nhị phân.
    Đã được tích hợp cơ chế bảo vệ ngoại lệ để chống khóa nút tải vĩnh viễn.
    """
    try:
        # 1. Khởi chạy nạp Template và bơm biến dữ liệu (Giải quyết triệt để Lỗi 1)
        try:
            doc = TemplateLoader.load(template_file_path)
            if meta_variables and doc:
                doc = TemplateLoader.inject_variables(doc, meta_variables)
        except Exception as e:
            logger.error(f"Lỗi nạp Template: {e}")
            doc = Document() # Fallback an toàn nếu template lỗi
            
        # 2. Đồng bộ hóa kích thước lề trang và kiểu chữ (Giải quyết triệt để Lỗi 2 & Lỗi 6)
        try:
            setup_document_styles(doc)
        except Exception as e:
            logger.error(f"Lỗi thiết lập Style: {e}")
        
        # 3. Phân tách văn bản theo từng dòng bằng Máy trạng thái (State Machine)
        lines = (markdown_content or "").split('\n')
        table_lines_buffer = []
        is_table_active = False
        
        for line in lines:
            try:
                stripped_line = line.strip()
                
                # Nhận diện trạng thái vùng dữ liệu thuộc bảng biểu (Giải quyết triệt để Lỗi 3)
                if stripped_line.startswith('|'):
                    is_table_active = True
                    table_lines_buffer.append(line)
                    continue
                else:
                    if is_table_active:
                        try:
                            process_and_draw_markdown_table(doc, table_lines_buffer)
                        except Exception as tbl_err:
                            logger.error(f"Lỗi vẽ bảng biểu Markdown: {tbl_err}")
                        table_lines_buffer = []
                        is_table_active = False
                        
                if not stripped_line:
                    continue
                    
                # Điều phối xử lý các cấp Heading đầu mục bài học
                if stripped_line.startswith('# '):
                    doc.add_heading(clean_xml_forbidden_chars(stripped_line[2:]), level=1)
                    continue
                elif stripped_line.startswith('## '):
                    doc.add_heading(clean_xml_forbidden_chars(stripped_line[3:]), level=2)
                    continue
                elif stripped_line.startswith('### '):
                    doc.add_heading(clean_xml_forbidden_chars(stripped_line[4:]), level=3)
                    continue
                    
                # Điều phối nạp tệp hình ảnh từ thẻ Markdown tiêu chuẩn (Giải quyết triệt để Lỗi 5)
                if stripped_line.startswith('![') and ']' in stripped_line and '(' in stripped_line:
                    try:
                        start_p = stripped_line.find('(')
                        end_p = stripped_line.find(')', start_p)
                        extracted_url = stripped_line[start_p + 1:end_p]
                        insert_image_to_docx(doc, extracted_url)
                    except Exception as img_err:
                        logger.error(f"Lỗi chèn hình ảnh: {img_err}")
                    continue
                    
                # Xử lý các văn bản thường đan xen công thức toán độc lập (Giải quyết triệt để Lỗi 4)
                inline_tokens = MarkdownTokenizer.tokenize_inline(line)
                refined_tokens = MarkdownTokenizer.parse_rich_styles(inline_tokens)
                
                if not refined_tokens:
                    continue
                    
                p = doc.add_paragraph()
                for token in refined_tokens:
                    try:
                        t_type = token.get('type', 'text')
                        t_content = token.get('content', '')
                        
                        if t_type == 'text':
                            p.add_run(clean_xml_forbidden_chars(t_content))
                        elif t_type == 'bold':
                            r = p.add_run(clean_xml_forbidden_chars(t_content))
                            r.bold = True
                        elif t_type == 'italic':
                            r = p.add_run(clean_xml_forbidden_chars(t_content))
                            r.italic = True
                        elif t_type == 'math_inline':
                            insert_math_to_paragraph(p, t_content, is_block=False)
                        elif t_type == 'math_block':
                            # Chuyển dịch khối toán học độc lập vào vị trí trung tâm dòng mới
                            insert_math_to_paragraph(p, t_content, is_block=True)
                    except Exception as token_err:
                        logger.error(f"Lỗi xử lý Token: {token_err}")
                        p.add_run(clean_xml_forbidden_chars(str(token.get('content', ''))))
            except Exception as line_err:
                logger.error(f"Lỗi xử lý dòng văn bản: {line_err}")
                continue
                
        # Bản vẽ cuối cùng nếu kết thúc chuỗi mà bộ đệm bảng vẫn chứa dữ liệu
        if is_table_active and table_lines_buffer:
            try:
                process_and_draw_markdown_table(doc, table_lines_buffer)
            except Exception as tbl_err:
                logger.error(f"Lỗi vẽ bảng cuối: {tbl_err}")
                
        # Nén tệp dữ liệu vào bộ nhớ đệm luồng byte phục vụ cấp phát tải về lập tức
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream
        
    except Exception as fatal_err:
        logger.error(f"Lỗi nghiêm trọng trong tiến trình kết xuất Word: {fatal_err}")
        # Trả về tệp an toàn chứa thông báo lỗi để Streamlit không bị kẹt trạng thái nút bấm
        fallback_doc = Document()
        fallback_doc.add_paragraph(f"Đã xảy ra lỗi kết xuất file Word: {str(fatal_err)}")
        output_stream = io.BytesIO()
        fallback_doc.save(output_stream)
        output_stream.seek(0)
        return output_stream
