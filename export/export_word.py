# -*- coding: utf-8 -*-
"""
Module: export/export_word.py - Phần 1
Nhiệm vụ: Khai báo thư viện và bộ cấu hình phân tách từ khóa Inline.
"""

import io
import re
from typing import List, Dict, Any, Optional
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Import các công cụ xử lý công thức và bảng biểu đã tối ưu từ package mới
try:
    from .word_math import insert_math_to_paragraph
    from .word_tables import process_and_draw_markdown_table
except ImportError:
    from export.word_math import insert_math_to_paragraph
    from export.word_tables import process_and_draw_markdown_table

# ==========================================
# 1. BỘ PHÂN TÍCH MARKDOWN (TOKENIZER)
# ==========================================
class MarkdownTokenizer:
    _HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)')
    _IMAGE_RE = re.compile(r'^!\[(.*?)\]\((.*?)\)')
    _BULLET_RE = re.compile(r'^(\s*)([\*\-])\s+(.*)')
    _NUMBER_RE = re.compile(r'^(\s*)(\d+\.)\s+(.*)')
    _CHECKBOX_RE = re.compile(r'^(\s*)([\*\-])\s+\[([ xX])\]\s+(.*)')
    _HR_RE = re.compile(r'^\s*([-*_])\1{2,}\s*$')
    _CODE_BLOCK_START_RE = re.compile(r'^```(\w*)')
    _MATH_RE = re.compile(r'(\$.+?\$|\\\([\s\S]+?\\\))')
    _LINK_RE = re.compile(r'\[(.*?)\](.*?)')
    _INLINE_CODE_RE = re.compile(r'`([^`]+)`')
    _BOLD_RE = re.compile(r'(\*\*\*|___\b)(.*?)\1|(\*\*|__\b)(.*?)\3')
    _ITALIC_RE = re.compile(r'(\*|_\b)(.*?)\1')
    _UNDERLINE_RE = re.compile(r'<u>(.*?)</u>', re.IGNORECASE)
    _STRIKE_RE = re.compile(r'~~(.*?)~~')
    _HIGHLIGHT_RE = re.compile(r'==(.*?)==')

    @classmethod
    def parse(cls, markdown_text: str) -> List[Dict[str, Any]]:
        forbidden = ("Chào bạn", "Với vai trò", "Tôi là", "Lưu ý về")
        ast_nodes, table_buf, code_buf = [], [], []
        code_lang, in_code = "", False

        def flush_table():
            if table_buf:
                ast_nodes.append({"type": "table_raw_lines", "lines": list(table_buf)})
                table_buf.clear()

        for raw_line in markdown_text.splitlines():
            raw_line = re.sub(r'^\s*>\s*', '', raw_line)
            if any(raw_line.lstrip().startswith(p) for p in forbidden): 
                continue
            
            if in_code:
                if raw_line.strip() == "```":
                    in_code = False
                    ast_nodes.append({"type": "code", "language": code_lang, "text": "\n".join(code_buf)})
                    code_buf.clear()
                else: 
                    code_buf.append(raw_line)
                continue

            s_line = raw_line.strip()
            if match := cls._CODE_BLOCK_START_RE.match(s_line):
                flush_table()
                in_code = True
                code_lang = match.group(1).lower() or "text"
                continue

            if not s_line: 
                flush_table()
                continue

            if s_line.startswith('|'): 
                table_buf.append(s_line)
                continue

            flush_table()

            if cls._HR_RE.match(s_line): 
                ast_nodes.append({"type": "hr"})
            elif match := cls._HEADING_RE.match(s_line): 
                ast_nodes.append({"type": "heading", "level": len(match.group(1)), "tokens": cls._parse_inline_content(match.group(2))})
            elif match := cls._IMAGE_RE.match(s_line): 
                ast_nodes.append({"type": "image", "alt": match.group(1), "url": match.group(2)})
            elif match := cls._CHECKBOX_RE.match(raw_line): 
                ast_nodes.append({"type": "checkbox", "checked": match.group(3).lower()=='x', "level": (len(match.group(1))//2)+1, "tokens": cls._parse_inline_content(match.group(4))})
            elif match := cls._BULLET_RE.match(raw_line): 
                ast_nodes.append({"type": "list_item", "style": "bullet", "level": (len(match.group(1))//2)+1, "tokens": cls._parse_inline_content(match.group(3))})
            elif match := cls._NUMBER_RE.match(raw_line): 
                ast_nodes.append({"type": "list_item", "style": "number", "level": (len(match.group(1))//2)+1, "tokens": cls._parse_inline_content(match.group(3))})
            else: 
                ast_nodes.append({"type": "paragraph", "tokens": cls._parse_inline_content(s_line)})

        flush_table()
        return ast_nodes

    @classmethod
    def _parse_inline_content(cls, text: str) -> List[Dict[str, Any]]:
        tokens = []
        if not text: 
            return tokens
        parts = cls._MATH_RE.split(text)
        for part in parts:
            if not part: 
                continue
            if (part.startswith('$') and part.endswith('$')) or (part.startswith(r'\(') and part.endswith(r'\)')):
                tokens.append({"type": "inline_math", "content": part.strip('$').replace(r'\(', '').replace(r'\)', '').strip()})
            else: 
                tokens.extend(cls._parse_rich_text_styles(part))
        return tokens

    @classmethod
    def _parse_rich_text_styles(cls, text: str) -> List[Dict[str, Any]]:
        if match := cls._LINK_RE.search(text): return cls._build_node(text, match, "link", match.group(1))
        if match := cls._INLINE_CODE_RE.search(text): return cls._build_node(text, match, "inline_code", match.group(1))
        if match := cls._HIGHLIGHT_RE.search(text): return cls._build_node(text, match, "highlight", match.group(1))
        if match := cls._UNDERLINE_RE.search(text): return cls._build_node(text, match, "underline", match.group(1))
        if match := cls._BOLD_RE.search(text): return cls._build_node(text, match, "bold", match.group(2) or match.group(4))
        if match := cls._STRIKE_RE.search(text): return cls._build_node(text, match, "strike", match.group(1))
        if match := cls._ITALIC_RE.search(text): return cls._build_node(text, match, "italic", match.group(2))
        return [{"type": "text", "content": text}]

    @classmethod
    def _build_node(cls, text: str, match: re.Match, t_type: str, inner: str) -> List[Dict[str, Any]]:
        s, e = match.span()
        tokens = []
        if s > 0: 
            tokens.extend(cls._parse_rich_text_styles(text[:s]))
        for t in cls._parse_rich_text_styles(inner):
            tokens.append({"type": t_type, "content": t.get("content") or t.get("text", "")} if t["type"] == "text" else t)
        if e < len(text): 
            tokens.extend(cls._parse_rich_text_styles(text[e:]))
        return tokens
# -*- coding: utf-8 -*-
"""
Module: export/export_word.py - Phần 2
Nhiệm vụ: Cấu hình phong cách và định dạng Header tài liệu.
"""

# ==========================================
# 2. KẾT XUẤT TÀI LIỆU WORD (ENGINE)
# ==========================================
class WordExportEngine:
    
    @staticmethod
    def _set_font(run, font_name="Times New Roman"):
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:cs'), font_name)

    @staticmethod
    def _set_shading(p_or_cell, color_hex):
        if hasattr(p_or_cell, 'paragraphs'):
            element = p_or_cell._element.get_or_add_tcPr()
        else:
            element = p_or_cell._element.get_or_add_pPr()
        shd = element.find(qn("w:shd"))
        if shd is None:
            shd = OxmlElement("w:shd")
            element.append(shd)
        shd.set(qn("w:fill"), color_hex)

    @classmethod
    def _render_inline(cls, p, tokens: List[Dict[str, Any]]):
        if not tokens: 
            return
        for t in tokens:
            tt = t.get("type")
            c = t.get("content", "")
            if tt in ["text", "bold", "italic", "underline", "strike", "highlight", "subscript", "superscript", "inline_code"]:
                run = p.add_run(c)
                cls._set_font(run, "Courier New" if tt == "inline_code" else "Times New Roman")
                if tt == "bold": run.bold = True
                elif tt == "italic": run.italic = True
                elif tt == "underline": run.underline = True
                elif tt == "strike": run.font.strike = True
                elif tt == "inline_code": 
                    run.font.size = Pt(11)
                    run.font.color.rgb = RGBColor(199, 37, 78)
            elif tt == "inline_math":
                insert_math_to_paragraph(p, c, is_block=False)

    @classmethod
    def _render_khbd_header(cls, doc, metadata: dict):
        table = doc.add_table(rows=1, cols=2)
        tblPr = table._element.xpath('w:tblPr')
        if tblPr:
            tblBorders = OxmlElement('w:tblBorders')
            for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'none')
                border.set(qn('w:sz'), '0')
                border.set(qn('w:space'), '0')
                border.set(qn('w:color'), 'auto')
                tblBorders.append(border)
            tblPr[0].append(tblBorders)
            
        c0 = table.cell(0, 0)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run("TRƯỜNG: ....................................\nTỔ: ........................................")
        r0.bold = True
        cls._set_font(r0)
        
        c1 = table.cell(0, 1)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(f"HỌ VÀ TÊN GIÁO VIÊN: ..........................\nMÔN: {metadata.get('mon', '.......').upper()}\nLỚP: {metadata.get('lop', '.......')}")
        r1.bold = True
        cls._set_font(r1)
        doc.add_paragraph()

        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rt = p_title.add_run(f"TÊN BÀI DẠY: {metadata.get('title', '.........................').upper()}")
        rt.bold = True
        rt.font.size = Pt(16)
        cls._set_font(rt)

        p_time = doc.add_paragraph()
        p_time.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_time = p_time.add_run(f"Môn học/Hoạt động giáo dục: {metadata.get('mon', '.......')}; Thời gian thực hiện: {metadata.get('so_tiet', '...')} tiết")
        r_time.font.italic = True
        cls._set_font(r_time)
        doc.add_paragraph()
# -*- coding: utf-8 -*-
"""
Module: export/export_word.py - Phần 3 (Bản sửa lỗi thụt lề)
Nhiệm vụ: Thiết lập cấu trúc lề trang, lắp ghép cây AST văn bản và xuất bản API.
"""

    @classmethod
    def convert_markdown_to_docx_bytes(cls, markdown_text: str, metadata: dict = None) -> bytes:
        ast_nodes = MarkdownTokenizer.parse(markdown_text)
        doc = docx.Document()
        
        # Thống nhất hệ thống lề chuẩn chính xác theo yêu cầu đề xuất (Top/Bottom/Right=1.5cm, Left=2.0cm)
        for s in doc.sections:
            s.page_height, s.page_width = Inches(11.69), Inches(8.27)
            s.top_margin = Inches(0.59)     # 1.5 cm
            s.bottom_margin = Inches(0.59)  # 1.5 cm
            s.right_margin = Inches(0.59)   # 1.5 cm
            s.left_margin = Inches(0.79)    # 2.0 cm
            
        ns = doc.styles['Normal']
        ns.font.name, ns.font.size = 'Times New Roman', Pt(13)
        ns.paragraph_format.space_after = Pt(6)
        
        if metadata and metadata.get("is_khbd"):
            cls._render_khbd_header(doc, metadata)
            
        for node in ast_nodes:
            nt = node.get("type")
            if nt == "paragraph":
                p = doc.add_paragraph()
                cls._render_inline(p, node.get("tokens", []))
            elif nt == "heading":
                lv = min(max(node.get("level", 1), 1), 3)
                p = doc.add_paragraph()
                p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(10), Pt(4)
                p.paragraph_format.keep_with_next = True
                if lv == 1: 
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cls._render_inline(p, node.get("tokens", []))
                for r in p.runs: 
                    r.bold = True
                    r.font.size = Pt(17 - lv)
                    cls._set_font(r)
            elif nt == "list_item":
                st = 'List Number' if node.get("style") == "number" else 'List Bullet'
                p = doc.add_paragraph(style=st)
                p.paragraph_format.left_indent = Inches(0.25 * node.get("level", 1) + 0.25)
                p.paragraph_format.first_line_indent = Inches(-0.25)
                cls._render_inline(p, node.get("tokens", []))
            elif nt == "checkbox":
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25 * node.get("level", 1))
                r = p.add_run("☑ " if node.get("checked") else "☐ ")
                cls._set_font(r, "MS Gothic")
                r.bold = True
                cls._render_inline(p, node.get("tokens", []))
            elif nt == "code":
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                cls._set_shading(p, "F5F5F5")
                r = p.add_run(node.get("text", ""))
                r.font.size = Pt(10.5)
                cls._set_font(r, "Courier New")
            elif nt == "hr":
                p = doc.add_paragraph()
                pPr = p._element.get_or_add_pPr()
                pb = OxmlElement("w:pBdr")
                bottom = OxmlElement("w:bottom")
                bottom.set(qn("w:val"), "single")
                bottom.set(qn("w:sz"), "8")
                bottom.set(qn("w:color"), "CCCCCC")
                pb.append(bottom)
                pPr.append(pb)
            elif nt == "page_break":
                doc.add_page_break()
            elif nt == "table_raw_lines":
                process_and_draw_markdown_table(doc, node.get("lines", []))
                
        bio = io.BytesIO()
        doc.save(bio)
        return bio.getvalue()

    @classmethod
    def export_to_word(cls, data_cache: Dict[str, Any]) -> bytes:
        markdown_content = data_cache.get("ai_generated_content", "")
        return cls.convert_markdown_to_docx_bytes(markdown_content, metadata=data_cache)

# ==========================================
# 3. PUBLIC API CŨ (Đưa hẳn ra ngoài rìa class)
# ==========================================
def export_word(markdown_text: str) -> bytes:
    return WordExportEngine.convert_markdown_to_docx_bytes(markdown_text)
