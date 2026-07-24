# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_tables.py
Nhiệm vụ: Phân tích bảng Markdown, khởi tạo bảng Word, xử lý
nội dung từng ô (văn bản, công thức OMML, hình ảnh, Markdown) 
một cách thông minh. Tuyệt đối không dùng cell.text gây mất định dạng.
============================================================
"""

import re
import logging
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

logger = logging.getLogger(__name__)

# Tích hợp an toàn với các API nội bộ
try:
    from .word_math import insert_math_to_paragraph
except ImportError:
    insert_math_to_paragraph = None

try:
    from .word_images import insert_image_to_paragraph
except ImportError:
    insert_image_to_paragraph = None

def _parse_and_fill_cell(cell, cell_text: str, is_header: bool = False):
    """
    Phân tích nội dung ô và điền dữ liệu tuần tự (Văn bản, Toán, Ảnh, Format).
    """
    if not cell.paragraphs:
        p = cell.add_paragraph()
    else:
        p = cell.paragraphs[0]
        
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_header else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.space_before = Pt(3)

    cell_text = cell_text.replace('<br>', '\n').replace('<br/>', '\n')

    # Trực tiếp xử lý nếu toàn bộ ô là chuỗi JSON Metadata hình ảnh
    if cell_text.strip().startswith('{') and cell_text.strip().endswith('}') and '"id"' in cell_text:
        if insert_image_to_paragraph:
            insert_image_to_paragraph(p, cell_text.strip(), max_width=Inches(2.0))
        else:
            r = p.add_run("[Hình ảnh]")
            r.font.name = 'Times New Roman'
        return

    # Regex quét hỗn hợp: Ảnh, Công thức Toán, Bold, Italic
    pattern = re.compile(
        r'(!\[.*?\]\((.*?)\))|'       # Group 1, 2: Ảnh ![alt](url)
        r'(\$\$(.*?)\$\$)|'           # Group 3, 4: Toán block $$...$$
        r'(\$([^$]+)\$)|'             # Group 5, 6: Toán inline $...$
        r'(\\\((.*?)\\\))|'           # Group 7, 8: Toán inline \(...\)
        r'(\*\*([^*]+)\*\*)|'         # Group 9, 10: Bold **...**
        r'(__([^_]+)__)|'             # Group 11, 12: Bold __...__
        r'(\*([^*]+)\*)|'             # Group 13, 14: Italic *...*
        r'(_([^_]+)_)'                # Group 15, 16: Italic _..._
    )
    
    last_idx = 0
    for match in pattern.finditer(cell_text):
        # 1. Ghi phần văn bản thường đứng trước match
        text_before = cell_text[last_idx:match.start()]
        if text_before:
            r = p.add_run(text_before.replace('\\|', '|'))
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            if is_header: r.bold = True
            
        # 2. Xử lý các thành phần đặc biệt
        if match.group(1): # Hình ảnh Markdown
            img_url = match.group(2)
            if insert_image_to_paragraph:
                # Giới hạn kích thước ảnh trong bảng để tránh vỡ cột
                insert_image_to_paragraph(p, img_url, max_width=Inches(1.8))
            else:
                r = p.add_run(f"[Ảnh: {img_url}]")
                r.font.name = 'Times New Roman'
                
        elif match.group(3) or match.group(5) or match.group(7): # Công thức Toán học (OMML)
            math_content = match.group(4) or match.group(6) or match.group(8)
            if insert_math_to_paragraph:
                # Ép công thức trong bảng thành dạng inline để không phá dòng
                insert_math_to_paragraph(p, math_content, is_block=False)
            else:
                r = p.add_run(math_content)
                r.font.name = 'Cambria Math'
                r.italic = True
                
        elif match.group(9) or match.group(11): # In đậm
            text_bold = match.group(10) or match.group(12)
            r = p.add_run(text_bold.replace('\\|', '|'))
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            r.bold = True
            
        elif match.group(13) or match.group(15): # In nghiêng
            text_italic = match.group(14) or match.group(16)
            r = p.add_run(text_italic.replace('\\|', '|'))
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            r.italic = True
            if is_header: r.bold = True
            
        last_idx = match.end()
        
    # 3. Ghi phần văn bản còn sót lại ở cuối
    if last_idx < len(cell_text):
        text_after = cell_text[last_idx:]
        r = p.add_run(text_after.replace('\\|', '|'))
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        if is_header: r.bold = True

def process_and_draw_markdown_table(doc: Document, table_lines: list):
    """
    API Public: Chuyển đổi danh sách dòng Markdown table thành bảng Word chuẩn.
    Bảo toàn cấu trúc, viền bảng và định dạng chi tiết từng ô.
    """
    if not table_lines or len(table_lines) < 2:
        return
        
    try:
        # 1. Phân tích an toàn hàng/cột (Không làm vỡ các công thức có chứa '|' như $|x|$)
        parsed_rows = []
        for line in table_lines:
            line = line.strip()
            if not line:
                continue
            
            # Xóa ống | bao ngoài viền
            if line.startswith('|'): line = line[1:]
            if line.endswith('|'): line = line[:-1]
            
            # Cắt cột an toàn, bỏ qua các dấu \| bị escape
            cells = re.split(r'(?<!\\)\|', line)
            cells = [c.strip() for c in cells]
            parsed_rows.append(cells)
            
        # 2. Lọc bỏ dòng phân cách (vd: |---|---|)
        filtered_rows = []
        for row in parsed_rows:
            if row and all(re.match(r'^[\-\:]+$', c.replace(' ', '')) for c in row if c):
                continue
            filtered_rows.append(row)
            
        if not filtered_rows:
            return
            
        # 3. Chuẩn hóa ma trận bảng (Đảm bảo số cột đồng đều)
        num_rows = len(filtered_rows)
        num_cols = max(len(r) for r in filtered_rows)
        
        for r in filtered_rows:
            while len(r) < num_cols:
                r.append("")
                
        # 4. Khởi tạo Bảng Word
        table = doc.add_table(rows=num_rows, cols=num_cols)
        table.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Vẽ viền bảng đen chuẩn xác
        tblPr = table._element.xpath('w:tblPr')
        if tblPr:
            tblBorders = OxmlElement('w:tblBorders')
            for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'single')
                border.set(qn('w:sz'), '4') 
                border.set(qn('w:space'), '0')
                border.set(qn('w:color'), '000000') 
                tblBorders.append(border)
            tblPr[0].append(tblBorders)

        # 5. Phân tích và render nội dung từng ô thông minh
        for r_idx, row_data in enumerate(filtered_rows):
            row_cells = table.rows[r_idx].cells
            is_header = (r_idx == 0)
            
            for c_idx, cell_value in enumerate(row_data):
                cell = row_cells[c_idx]
                
                # Nền xám nhạt cho tiêu đề
                if is_header:
                    tcPr = cell._element.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'), 'clear')
                    shd.set(qn('w:color'), 'auto')
                    shd.set(qn('w:fill'), 'F2F2F2')
                    tcPr.append(shd)
                
                # Gọi bộ xử lý nội dung đa thành phần
                _parse_and_fill_cell(cell, cell_value, is_header=is_header)

        # Cách 1 khoảng paragraph dưới bảng để không bị dính văn bản
        doc.add_paragraph()
        
    except Exception as e:
        logger.error(f"Lỗi vẽ bảng Markdown: {e}")
        # Fallback an toàn: Trả văn bản thô lại vào Word nếu có lỗi ngoại lệ
        for line in table_lines:
            doc.add_paragraph(line)
