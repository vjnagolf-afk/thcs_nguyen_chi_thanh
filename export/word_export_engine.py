# -*- coding: utf-8 -*-
import io
from docx import Document
from .template_loader import TemplateLoader
from .word_styles import setup_document_styles
from .markdown_tokenizer import MarkdownTokenizer
from .word_math import insert_math_to_paragraph
from .word_tables import process_and_draw_markdown_table
from .word_images import insert_image_to_docx
from .word_utils import clean_xml_forbidden_chars

def export_markdown_to_word(markdown_content: str, template_file_path: str = None, meta_variables: dict = None) -> io.BytesIO:
    """
    Hàm đầu não thực thi phân tích toàn diện mã Markdown và kết xuất thành File Word dạng Stream nhị phân.
    """
    # 1. Khởi chạy nạp Template và bơm biến dữ liệu (Giải quyết triệt để Lỗi 1)
    doc = TemplateLoader.load(template_file_path)
    if meta_variables:
        doc = TemplateLoader.inject_variables(doc, meta_variables)
        
    # 2. Đồng bộ hóa kích thước lề trang và kiểu chữ (Giải quyết triệt để Lỗi 2 & Lỗi 6)
    setup_document_styles(doc)
    
    # 3. Phân tách văn bản theo từng dòng bằng Máy trạng thái (State Machine)
    lines = markdown_content.split('\n')
    table_lines_buffer = []
    is_table_active = False
    
    for line in lines:
        stripped_line = line.strip()
        
        # Nhận diện trạng thái vùng dữ liệu thuộc bảng biểu (Giải quyết triệt để Lỗi 3)
        if stripped_line.startswith('|'):
            is_table_active = True
            table_lines_buffer.append(line)
            continue
        else:
            if is_table_active:
                process_and_draw_markdown_table(doc, table_lines_buffer)
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
            except Exception:
                pass
            continue
            
        # Xử lý các văn bản thường đan xen công thức toán độc lập (Giải quyết triệt để Lỗi 4)
        inline_tokens = MarkdownTokenizer.tokenize_inline(line)
        refined_tokens = MarkdownTokenizer.parse_rich_styles(inline_tokens)
        
        if not refined_tokens:
            continue
            
        p = doc.add_paragraph()
        for token in refined_tokens:
            t_type = token['type']
            t_content = token['content']
            
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
                
    # Bản vẽ cuối cùng nếu kết thúc chuỗi mà bộ đệm bảng vẫn chứa dữ liệu
    if is_table_active and table_lines_buffer:
        process_and_draw_markdown_table(doc, table_lines_buffer)
        
    # Nén tệp dữ liệu vào bộ nhớ đệm luồng byte phục vụ cấp phát tải về lập tức
    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream
