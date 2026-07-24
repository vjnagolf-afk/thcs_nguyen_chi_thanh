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
        
        # 1. Cấu hình Style Mặc định: Font Times New Roman 13, Căn đều 2 bên (Justify)
        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(13)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        style.paragraph_format.space_after = Pt(6)
        
        # 2. Tiền xử lý văn bản: Xóa các khoảng trắng thừa
        markdown_text = markdown_text.replace("·", "") # Xóa các chấm đen sinh lỗi
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
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY # Bắt buộc căn đều 2 bên
            
            # Xử lý thụt lề (Chỉ thụt 1.0 - 1.2cm theo chuẩn)
            if re.match(r'^[\-\*]\s+', line):
                p.paragraph_format.left_indent = Cm(1.2) # Thụt lề toàn đoạn cho danh sách
                text = re.sub(r'^[\-\*]\s+', '- ', line)
            elif re.match(r'^\d+\.\s+', line):
                p.paragraph_format.left_indent = Cm(1.2)
                text = line
            else:
                p.paragraph_format.first_line_indent = Cm(1.2) # Thụt lề dòng đầu tiên 1.2cm
                text = line
            
            # Xử lý Bôi đậm (**text**)
            parts = re.split(r'(\*\*.*?\*\*)', text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    p.add_run(part)
        
        # Lưu ra luồng byte
        f = io.BytesIO()
        doc.save(f)
        return f.getvalue()
