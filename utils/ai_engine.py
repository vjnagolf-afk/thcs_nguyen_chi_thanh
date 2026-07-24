# -*- coding: utf-8 -*-
"""
============================================================
XUẤT BẢN WORD - BỘ ĐIỀU PHỐI TRUNG TÂM (WORD EXPORT ENGINE)
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
        # 1. LOAD TEMPLATE HOẶC TẠO MỚI (Khắc phục Lỗi 1)
        try:
            doc = Document(template_path) if template_path else Document()
        except:
            doc = Document()
        
        # 2. THỐNG NHẤT LỀ TOÀN BỘ VĂN BẢN (Khắc phục Lỗi 6: Mâu thuẫn lề)
        # Top: 1.5cm, Bottom: 1.5cm, Left: 2.0cm, Right: 1.5cm
        for section in doc.sections:
            section.top_margin = Cm(1.5)
            section.bottom_margin = Cm(1.5)
            section.left_margin = Cm(2.0)
            section.right_margin = Cm(1.5)
        
        # 3. THIẾT LẬP STYLE MẶC ĐỊNH
        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(13)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        style.paragraph_format.space_after = Pt(6)
        
        # 4. TIỀN XỬ LÝ VĂN BẢN (Khắc phục Lỗi 4: Ngừng băm nát công thức)
        # Loại bỏ hoàn toàn các lệnh replace("$", "") hay replace("\\sqrt", "√") gây gãy mã Toán
        markdown_text = markdown_text.replace("•", "+") # Chỉ đổi chấm đen thành dấu cộng
        
        lines = markdown_text.split('\n')
        
        # Tiền parser đơn giản (Bước đệm tiến tới AST Node)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Heading Renderer
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                p = doc.add_heading(text, level=min(level, 3))
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.bold = True
                    if level == 1:
                        run.font.size = Pt(16)
                    else:
                        run.font.size = Pt(14)
                continue

            # Paragraph & List Renderer
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Xử lý thụt lề cho Danh sách (List) và Bước
            if re.match(r'^[\+\-]\s+', line):
                p.paragraph_format.left_indent = Cm(1.0)
            elif re.match(r'^\d+\.\s+', line) or re.match(r'^[a-zA-Z]\)\s+', line):
                p.paragraph_format.left_indent = Cm(0.5)
            else:
                p.paragraph_format.first_line_indent = Cm(1.0)
            
            # Xử lý Text Style (Bôi đậm)
            parts = re.split(r'(\*\*.*?\*\*)', line)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    p.add_run(part)
        
        # Lưu ra byte
        f = io.BytesIO()
        doc.save(f)
        return f.getvalue()
