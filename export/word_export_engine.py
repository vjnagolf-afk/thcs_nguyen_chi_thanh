# -*- coding: utf-8 -*-
"""
============================================================
XUẤT BẢN WORD - ĐỊNH DẠNG CHUẨN HÀNH CHÍNH
FILE: export/word_export_engine.py
============================================================
"""

import io
import re
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

class WordExportEngine:
    @staticmethod
    def convert_markdown_to_docx_bytes(markdown_text, template_path=None):
        doc = Document()
        
        # ==========================================
        # 1. CẤU HÌNH LỀ CHUẨN HÀNH CHÍNH
        # Top/Bottom: 1.2 cm, Left: 2.0 cm, Right: 1.5 cm
        # ==========================================
        for section in doc.sections:
            section.top_margin = Cm(1.2)
            section.bottom_margin = Cm(1.2)
            section.left_margin = Cm(2.0)
            section.right_margin = Cm(1.5)
        
        # 2. Cấu hình Style Mặc định: Font Times New Roman 13, Căn đều 2 bên
        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(13)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        style.paragraph_format.space_after = Pt(6)
        
        # 3. Tiền xử lý văn bản: Chống gãy công thức Toán
        markdown_text = markdown_text.replace("·", "") # Xóa chấm đen rác
        markdown_text = markdown_text.replace("$", "") # Xóa ký hiệu rác LaTeX
        markdown_text = markdown_text.replace("\\sqrt", "√") 
        markdown_text = markdown_text.replace("\\Rightarrow", "⇒")
        markdown_text = markdown_text.replace("\\Leftrightarrow", "⇔")
        markdown_text = markdown_text.replace("\\ge", "≥")
        markdown_text = markdown_text.replace("\\le", "≤")
        
        lines = markdown_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Xử lý Tiêu đề (Heading)
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                p = doc.add_heading(text, level=min(level, 3))
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    if level == 1:
                        run.font.size = Pt(16)
                    else:
                        run.font.size = Pt(14)
                continue

            # Xử lý Đoạn văn thường
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY # Căn đều 2 bên
            
            # Xử lý thụt lề đầu dòng
            if re.match(r'^[\-\*]\s+', line):
                p.paragraph_format.left_indent = Cm(1.0)
                text = re.sub(r'^[\-\*]\s+', '- ', line)
            elif re.match(r'^\d+\.\s+', line):
                p.paragraph_format.left_indent = Cm(0.5)
                text = line
            elif re.match(r'^[a-zA-Z]\)\s+', line):
                p.paragraph_format.left_indent = Cm(0.5)
                text = line
            else:
                p.paragraph_format.first_line_indent = Cm(1.0)
                text = line
            
            # 4. Thuật toán phân tách chữ Đậm và số Mũ (Superscript)
            parts = re.split(r'(\*\*.*?\*\*)', text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    # Bóc tách và đẩy x^2 thành số mũ trên Word
                    sub_parts = re.split(r'([A-Za-z0-9\(\)]+\^\d+)', part)
                    for sp in sub_parts:
                        if '^' in sp:
                            try:
                                base, sup = sp.split('^', 1)
                                p.add_run(base)
                                run_sup = p.add_run(sup)
                                run_sup.font.superscript = True
                            except:
                                p.add_run(sp)
                        else:
                            p.add_run(sp)
        
        # Lưu ra luồng byte
        f = io.BytesIO()
        doc.save(f)
        return f.getvalue()
