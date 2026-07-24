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
        # 1. LOAD TEMPLATE (Nếu có) HOẶC TẠO MỚI
        try:
            doc = Document(template_path) if template_path else Document()
        except:
            doc = Document()
        
        # 2. THỐNG NHẤT LỀ VĂN BẢN (Top=1.5, Bot=1.5, Left=2.0, Right=1.5)
        for section in doc.sections:
            section.top_margin = Cm(1.5)
            section.bottom_margin = Cm(1.5)
            section.left_margin = Cm(2.0)
            section.right_margin = Cm(1.5)
        
        # 3. THIẾT LẬP STYLE CƠ BẢN
        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(13)
        
        # 4. TOKENIZER (Bóc tách Markdown & Toán học)
        lines = markdown_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # --- Heading Renderer ---
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                p = doc.add_heading(text, level=min(level, 3))
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.bold = True
                    run.font.color.rgb = None # Trả về màu mặc định
                    run.font.size = Pt(16) if level == 1 else Pt(14)
                continue

            # --- Paragraph & List Renderer ---
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Xử lý Căn lề thụt đầu dòng (List)
            if re.match(r'^[\+\-]\s+', line):
                p.paragraph_format.left_indent = Cm(1.0)
            elif re.match(r'^\d+\.\s+', line) or re.match(r'^[a-zA-Z]\)\s+', line):
                p.paragraph_format.left_indent = Cm(0.5)
            else:
                p.paragraph_format.first_line_indent = Cm(1.0)
            
            # --- Inline Tokenizer (Tách Text thường, In đậm, và LaTeX Math) ---
            # Biểu thức Regex này sẽ cắt dòng thành danh sách các chuỗi: 
            # 1: Công thức block $$, 2: Công thức inline $, 3: In đậm **
            tokens = re.split(r'(\$\$.*?\$\$|\$.*?\$|\*\*.*?\*\*)', line)
            
            for token in tokens:
                if not token:
                    continue
                
                # A. Math Renderer (Toán học LaTeX)
                if token.startswith('$$') and token.endswith('$$'):
                    math_expr = token[2:-2]
                    # Tại đây: Gắn Hook gọi sang word_math.py (chuyển đổi oMath)
                    # Hiện tại in nguyên gốc để giữ an toàn cấu trúc
                    run = p.add_run(math_expr)
                    run.italic = True 
                    
                elif token.startswith('$') and token.endswith('$'):
                    math_expr = token[1:-1]
                    # Tại đây: Gắn Hook gọi sang word_math.py
                    run = p.add_run(math_expr)
                    run.italic = True
                    
                # B. Bold Renderer
                elif token.startswith('**') and token.endswith('**'):
                    run = p.add_run(token[2:-2])
                    run.bold = True
                    
                # C. Normal Text
                else:
                    run = p.add_run(token)

        # 5. LƯU THÀNH BYTES
        f = io.BytesIO()
        doc.save(f)
        return f.getvalue()
