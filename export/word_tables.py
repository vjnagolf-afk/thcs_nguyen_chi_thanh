# -*- coding: utf-8 -*-
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .word_utils import clean_xml_forbidden_chars
from .markdown_tokenizer import MarkdownTokenizer
from .word_math import insert_math_to_paragraph

def build_cell_border_xml(table):
    """Cấu hình khung lưới viền (Grid Borders) mỏng nhẹ màu xám sang trọng chuẩn quốc tế."""
    tblPr = table._tbl.tblPr
    borders_node = OxmlElement('w:tblBorders')
    for position in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{position}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '4')  # Độ dày mảnh tinh tế ~0.5pt
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), 'A0A0A0')  # Màu xám dịu mắt
        borders_node.append(b)
    tblPr.append(borders_node)

def process_and_draw_markdown_table(doc, raw_markdown_lines: list):
    """Trích xuất mảng dữ liệu từ các dòng text Markdown và vẽ bảng biểu vào tệp Word."""
    cleaned_rows = []
    
    for line in raw_markdown_lines:
        current_line = line.strip().strip('|')
        if not current_line or current_line.startswith('---') or current_line.startswith(':::'):
            continue  # Loại bỏ dòng ngăn cách gạch ngang của chuẩn Markdown Table
        
        row_cells = [cell.strip() for cell in current_line.split('|')]
        cleaned_rows.append(row_cells)
        
    if not cleaned_rows:
        return
        
    total_rows = len(cleaned_rows)
    total_cols = max(len(r) for r in cleaned_rows)
    
    word_table = doc.add_table(rows=total_rows, cols=total_cols)
    word_table.autofit = True
    build_cell_border_xml(word_table)
    
    for r_idx, cells_data in enumerate(cleaned_rows):
        row_obj = word_table.rows[r_idx]
        for c_idx, text_val in enumerate(cells_data):
            if c_idx >= total_cols:
                break
            cell_obj = row_obj.cells[c_idx]
            p_obj = cell_obj.paragraphs[0]
            p_obj.paragraph_format.space_after = Pt(2)
            
            # Tô nền xám nhạt cho dòng tiêu đề đầu tiên (Header Row)
            if r_idx == 0:
                bg_shd = OxmlElement('w:shd')
                bg_shd.set(qn('w:val'), 'clear')
                bg_shd.set(qn('w:fill'), 'F0F4F8')  # Màu xanh xám nhạt chuyên nghiệp
                cell_obj._tc.get_or_add_tcPr().append(bg_shd)
                p_obj.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Xử lý text chứa công thức hoặc chữ thường lồng trong ô bằng Tokenizer
            inline_toks = MarkdownTokenizer.tokenize_inline(text_val)
            styled_toks = MarkdownTokenizer.parse_rich_styles(inline_toks)
            
            for tok in styled_toks:
                if tok['type'] == 'text':
                    r = p_obj.add_run(clean_xml_forbidden_chars(tok['content']))
                    if r_idx == 0: r.bold = True
                elif tok['type'] == 'bold':
                    r = p_obj.add_run(clean_xml_forbidden_chars(tok['content']))
                    r.bold = True
                elif tok['type'] == 'italic':
                    r = p_obj.add_run(clean_xml_forbidden_chars(tok['content']))
                    r.italic = True
                elif tok['type'] in ['math_inline', 'math_block']:
                    insert_math_to_paragraph(p_obj, tok['content'], is_block=False)
