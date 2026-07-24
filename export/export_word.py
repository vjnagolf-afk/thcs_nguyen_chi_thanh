# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/export_word.py
Nhiệm vụ: Bộ điều phối trung tâm kết xuất Markdown / AI Generated Content 
thành file Word (.docx) chuẩn 5512.
Có Auto-Fix Regex bọc $ tự động cho công thức LaTeX bị đi lạc.
============================================================
"""

import io
import re
import json
import logging
from typing import List, Dict, Any, Optional

import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

logger = logging.getLogger(__name__)

# ============================================================
# KIỂM TRA VÀ NẠP CÁC MODULE TRONG HỆ THỐNG EXPORT
# ============================================================
try:
    from .markdown_tokenizer import MarkdownTokenizer
except ImportError as e1:
    try:
        from export.markdown_tokenizer import MarkdownTokenizer
    except ImportError as e2:
        MarkdownTokenizer = None

try:
    from .word_math import insert_math_to_paragraph
except ImportError as e1:
    try:
        from export.word_math import insert_math_to_paragraph
    except ImportError as e2:
        insert_math_to_paragraph = None

try:
    from .word_tables import process_and_draw_markdown_table
except ImportError as e1:
    try:
        from export.word_tables import process_and_draw_markdown_table
    except ImportError as e2:
        process_and_draw_markdown_table = None

try:
    from .word_images import insert_image_to_paragraph, insert_image_to_docx
except ImportError as e1:
    try:
        from export.word_images import insert_image_to_paragraph, insert_image_to_docx
    except ImportError as e2:
        insert_image_to_paragraph = None
        insert_image_to_docx = None

# ============================================================
# AUTO-FIX CÔNG THỨC BỊ THIẾU DẤU $
# ============================================================
def _fix_missing_math_dollars(text: str) -> str:
    """Tự động bọc dấu $ cho các ký hiệu LaTeX đi lạc trong văn bản."""
    if not text:
        return ""
    
    # 1. Bọc các hàm phân số \frac, căn \sqrt, góc \widehat
    text = re.sub(r'(?<!\$)(?<!\\)(\\frac\s*\{[^{}]*\}\s*\{[^{}]*\})(?!\$)', r'$\1$', text)
    text = re.sub(r'(?<!\$)(?<!\\)(\\sqrt\s*(?:\[[^\]]*\])?\s*\{[^{}]*\})(?!\$)', r'$\1$', text)
    text = re.sub(r'(?<!\$)(?<!\\)(\\widehat\s*\{[^{}]*\})(?!\$)', r'$\1$', text)
    
    # 2. Bọc các công thức dạng n_{21}, x_1, 10^8, 0^\circ
    text = re.sub(r'(?<!\$)\b([a-zA-Z]_\{[^{}]+\}|[a-zA-Z]_\d+)(?!\$)', r'$\1$', text)
    text = re.sub(r'(?<!\$)\b(\d+\^\circ|\d+\^\{[^{}]+\}|\d+\^\d+)(?!\$)', r'$\1$', text)
    
    return text

def _parse_inline_fallback(text: str) -> List[Dict[str, Any]]:
    tokens = []
    pattern = re.compile(r'(\$\$(.*?)\$\$)|(\$([^$]+?)\$)|(\*\*([^*]+?)\*\*)|(\*([^*]+?)\*)')
    last_idx = 0
    for match in pattern.finditer(text):
        if match.start() > last_idx:
            tokens.append({"type": "text", "content": text[last_idx:match.start()]})
        if match.group(1):
            tokens.append({"type": "math_block", "content": match.group(2)})
        elif match.group(3):
            tokens.append({"type": "inline_math", "content": match.group(4)})
        elif match.group(5):
            tokens.append({"type": "bold", "content": match.group(6)})
        elif match.group(7):
            tokens.append({"type": "italic", "content": match.group(8)})
        last_idx = match.end()
    if last_idx < len(text):
        tokens.append({"type": "text", "content": text[last_idx:]})
    return tokens

def _fallback_parse_markdown(markdown_text: str) -> List[Dict[str, Any]]:
    ast_nodes = []
    lines = (markdown_text or "").splitlines()
    table_buffer = []
    in_code = False
    code_lang = ""
    code_buffer = []

    def flush_table():
        if table_buffer:
            ast_nodes.append({"type": "table_raw_lines", "lines": list(table_buffer)})
            table_buffer.clear()

    for line in lines:
        s_line = line.strip()

        if s_line.startswith("```"):
            if in_code:
                in_code = False
                ast_nodes.append({"type": "code", "language": code_lang, "text": "\n".join(code_buffer)})
                code_buffer.clear()
            else:
                flush_table()
                in_code = True
                code_lang = s_line.lstrip("`").strip()
            continue

        if in_code:
            code_buffer.append(line)
            continue

        if s_line.startswith("|"):
            table_buffer.append(s_line)
            continue
        else:
            flush_table()

        if not s_line:
            continue

        if s_line.startswith("$$") and s_line.endswith("$$") and len(s_line) > 4:
            ast_nodes.append({"type": "block_math", "content": s_line[2:-2].strip()})
            continue
        elif s_line == "$$":
            continue

        if s_line.startswith("#"):
            match = re.match(r'^(#{1,6})\s+(.*)', s_line)
            if match:
                level = len(match.group(1))
                text = match.group(2)
                ast_nodes.append({"type": "heading", "level": level, "text": text, "tokens": _parse_inline_fallback(text)})
                continue

        if re.match(r'^\s*([-*_])\1{2,}\s*$', s_line):
            ast_nodes.append({"type": "hr"})
            continue

        if s_line.startswith("- [ ]") or s_line.startswith("- [x]") or s_line.startswith("- [X]"):
            checked = "[x]" in s_line or "[X]" in s_line
            text = s_line[5:].strip()
            ast_nodes.append({"type": "checkbox", "checked": checked, "level": 1, "tokens": _parse_inline_fallback(text)})
            continue

        if s_line.startswith("- ") or s_line.startswith("* "):
            text = s_line[2:].strip()
            ast_nodes.append({"type": "list_item", "style": "bullet", "level": 1, "tokens": _parse_inline_fallback(text)})
            continue

        num_match = re.match(r'^\d+\.\s+(.*)', s_line)
        if num_match:
            text = num_match.group(1)
            ast_nodes.append({"type": "list_item", "style": "number", "level": 1, "tokens": _parse_inline_fallback(text)})
            continue

        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)', s_line)
        if img_match:
            ast_nodes.append({"type": "image", "alt": img_match.group(1), "url": img_match.group(2)})
            continue

        ast_nodes.append({"type": "paragraph", "text": s_line, "tokens": _parse_inline_fallback(s_line)})

    flush_table()
    return ast_nodes

# ============================================================
# EXPORT ENGINE
# ============================================================
class WordExportEngine:

    @staticmethod
    def _set_font(run, font_name="Times New Roman"):
        try:
            rPr = run._element.get_or_add_rPr()
            rFonts = rPr.find(qn("w:rFonts"))
            if rFonts is None:
                rFonts = OxmlElement("w:rFonts")
                rPr.append(rFonts)
            rFonts.set(qn('w:ascii'), font_name)
            rFonts.set(qn('w:hAnsi'), font_name)
            rFonts.set(qn('w:cs'), font_name)
        except Exception:
            pass

    @classmethod
    def _render_inline_tokens(cls, p, tokens: List[Dict[str, Any]], export_errors: List[Dict[str, Any]]):
        if not tokens:
            return

        for idx, token in enumerate(tokens):
            try:
                ttype = token.get("type", "text")
                content = token.get("content") or token.get("text") or ""

                if ttype in ["text", "bold", "italic", "underline", "strike", "highlight", "inline_code", "code"]:
                    run = p.add_run(content)
                    cls._set_font(run, "Courier New" if ttype in ["inline_code", "code"] else "Times New Roman")
                    run.font.size = Pt(11) if ttype in ["inline_code", "code"] else Pt(13)

                    if ttype == "bold": run.bold = True
                    elif ttype == "italic": run.italic = True
                    elif ttype == "underline": run.underline = True
                    elif ttype == "strike": run.font.strike = True
                    elif ttype == "highlight": run.font.color.rgb = RGBColor(199, 37, 78)

                elif ttype in ["inline_math", "math_inline", "math", "math_block", "block_math"]:
                    if insert_math_to_paragraph:
                        is_block = ttype in ["math_block", "block_math"]
                        insert_math_to_paragraph(p, content, is_block=is_block)
                    else:
                        run = p.add_run(f" {content} ")
                        cls._set_font(run, "Cambria Math")
                        run.italic = True

                elif ttype == "image":
                    img_src = token if ("base64" in token or "path" in token or "caption" in token) else (token.get("url") or token.get("path") or content)
                    if insert_image_to_paragraph:
                        insert_image_to_paragraph(p, img_src)
                    else:
                        p.add_run(f"[Hình ảnh: {img_src}]").italic = True

                elif ttype == "link":
                    url = token.get("url", "")
                    run = p.add_run(f"{content} ({url})" if url else content)
                    run.font.color.rgb = RGBColor(0, 102, 204)
                    run.underline = True

                else:
                    run = p.add_run(str(content))
                    cls._set_font(run, "Times New Roman")
                    run.font.size = Pt(13)

            except Exception as e:
                export_errors.append({"type": "inline_token", "index": idx, "token": token, "error": str(e)})
                try:
                    p.add_run(str(token.get("content") or token.get("text") or ""))
                except Exception:
                    pass

    @classmethod
    def _render_khbd_header(cls, doc: Document, metadata: dict):
        try:
            table = doc.add_table(rows=1, cols=2)
            tblPr = table._element.xpath('w:tblPr')
            if tblPr:
                tblBorders = OxmlElement('w:tblBorders')
                for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
                    border = OxmlElement(f'w:{border_name}')
                    border.set(qn('w:val'), 'none')
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
            mon = str(metadata.get('mon', '.......')).upper()
            lop = str(metadata.get('lop', '.......'))
            r1 = p1.add_run(f"HỌ VÀ TÊN GIÁO VIÊN: ..........................\nMÔN: {mon}\nLỚP: {lop}")
            r1.bold = True
            cls._set_font(r1)
            doc.add_paragraph()

            p_title = doc.add_paragraph()
            p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title = str(metadata.get('title', '.........................')).upper()
            rt = p_title.add_run(f"TÊN BÀI DẠY: {title}")
            rt.bold = True
            rt.font.size = Pt(16)
            cls._set_font(rt)

            p_time = doc.add_paragraph()
            p_time.alignment = WD_ALIGN_PARAGRAPH.CENTER
            so_tiet = str(metadata.get('so_tiet', '...'))
            r_time = p_time.add_run(f"Môn học/Hoạt động giáo dục: {mon}; Thời gian thực hiện: {so_tiet} tiết")
            r_time.font.italic = True
            cls._set_font(r_time)
            doc.add_paragraph()
        except Exception:
            pass

    @classmethod
    def convert_markdown_to_docx_bytes(cls, markdown_text: str, metadata: dict = None) -> bytes:
        export_errors = []
        doc = Document()
        
        try:
            for s in doc.sections:
                s.page_height, s.page_width = Inches(11.69), Inches(8.27) 
                s.top_margin = Inches(0.59)    
                s.bottom_margin = Inches(0.59) 
                s.right_margin = Inches(0.59)  
                s.left_margin = Inches(0.79)   

            ns = doc.styles['Normal']
            ns.font.name, ns.font.size = 'Times New Roman', Pt(13)
            ns.paragraph_format.space_after = Pt(4)
            ns.paragraph_format.line_spacing = 1.15
        except Exception as e:
            export_errors.append({"type": "setup_styles", "error": str(e)})

        if metadata and isinstance(metadata, dict) and metadata.get("is_khbd"):
            cls._render_khbd_header(doc, metadata)

        # Kích hoạt Auto-Fix cho công thức
        markdown_text = _fix_missing_math_dollars(markdown_text or "")

        ast_nodes = []
        if MarkdownTokenizer and hasattr(MarkdownTokenizer, 'parse'):
            try:
                ast_nodes = MarkdownTokenizer.parse(markdown_text)
            except Exception as tok_err:
                export_errors.append({"type": "tokenizer_error", "error": str(tok_err)})
                ast_nodes = _fallback_parse_markdown(markdown_text)
        else:
            ast_nodes = _fallback_parse_markdown(markdown_text)

        for node_idx, node in enumerate(ast_nodes):
            try:
                ntype = node.get("type", "paragraph")

                if ntype == "paragraph":
                    p = doc.add_paragraph()
                    p.paragraph_format.space_after = Pt(4)
                    raw_text = str(node.get("text", "")).strip()
                    
                    if raw_text.startswith("[IMAGE:") and raw_text.endswith("]"):
                        img_id = raw_text[7:-1].strip()
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        if insert_image_to_paragraph:
                            insert_image_to_paragraph(p, img_id)
                        else:
                            p.add_run(f"[Hình ảnh: {img_id}]").italic = True
                        continue

                    tokens = node.get("tokens", [])
                    if tokens:
                        cls._render_inline_tokens(p, tokens, export_errors)
                    elif raw_text:
                        r = p.add_run(raw_text)
                        cls._set_font(r, "Times New Roman")
                        r.font.size = Pt(13)

                elif ntype == "heading":
                    level = min(max(node.get("level", 1), 1), 6)
                    p = doc.add_paragraph()
                    p.paragraph_format.space_before = Pt(10)
                    p.paragraph_format.space_after = Pt(4)
                    p.paragraph_format.keep_with_next = True
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT

                    tokens = node.get("tokens", [])
                    if tokens:
                        cls._render_inline_tokens(p, tokens, export_errors)
                    else:
                        r = p.add_run(str(node.get("text") or ""))
                        cls._set_font(r, "Times New Roman")

                    for r in p.runs:
                        r.bold = True
                        cls._set_font(r, "Times New Roman")
                        r.font.size = Pt(16 if level == 1 else (14 if level == 2 else 13))

                elif ntype in ["block_math", "math_block"]:
                    math_content = node.get("content") or node.get("text") or ""
                    p = doc.add_paragraph()
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after = Pt(6)

                    if insert_math_to_paragraph:
                        insert_math_to_paragraph(p, math_content, is_block=True)
                    else:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        r = p.add_run(math_content)
                        cls._set_font(r, "Cambria Math")
                        r.italic = True

                elif ntype in ["list_item", "bullet_list", "numbered_list"]:
                    is_num = (node.get("style") == "number" or ntype == "numbered_list")
                    style_name = 'List Number' if is_num else 'List Bullet'
                    level = node.get("level", 1)

                    p = doc.add_paragraph(style=style_name)
                    p.paragraph_format.left_indent = Inches(0.25 * level + 0.25)
                    p.paragraph_format.first_line_indent = Inches(-0.25)
                    p.paragraph_format.space_after = Pt(3)

                    tokens = node.get("tokens", [])
                    if tokens:
                        cls._render_inline_tokens(p, tokens, export_errors)
                    else:
                        r = p.add_run(str(node.get("text") or ""))
                        cls._set_font(r, "Times New Roman")

                elif ntype == "checkbox":
                    level = node.get("level", 1)
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent = Inches(0.25 * level)
                    p.paragraph_format.space_after = Pt(3)

                    checked_symbol = "☑ " if node.get("checked") else "☐ "
                    r_check = p.add_run(checked_symbol)
                    r_check.bold = True
                    cls._set_font(r_check, "MS Gothic")

                    tokens = node.get("tokens", [])
                    if tokens:
                        cls._render_inline_tokens(p, tokens, export_errors)
                    else:
                        r = p.add_run(str(node.get("text") or ""))
                        cls._set_font(r, "Times New Roman")

                elif ntype == "image":
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after = Pt(6)

                    img_source = node if ("base64" in node or "path" in node or "caption" in node) else (node.get("url") or node.get("path") or node.get("alt") or "")
                    if insert_image_to_paragraph:
                        insert_image_to_paragraph(p, img_source)
                    else:
                        p.add_run(f"[Hình ảnh: {img_source}]").italic = True

                elif ntype in ["table", "table_raw_lines"]:
                    lines = node.get("lines", [])
                    if process_and_draw_markdown_table and lines:
                        process_and_draw_markdown_table(doc, lines)
                    else:
                        for line in lines:
                            p = doc.add_paragraph()
                            p.add_run(str(line))

                elif ntype in ["code", "code_block"]:
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent = Inches(0.4)
                    p.paragraph_format.space_before = Pt(4)
                    p.paragraph_format.space_after = Pt(4)
                    try:
                        pPr = p._element.get_or_add_pPr()
                        shd = OxmlElement('w:shd')
                        shd.set(qn('w:val'), 'clear')
                        shd.set(qn('w:color'), 'auto')
                        shd.set(qn('w:fill'), 'F5F5F5')
                        pPr.append(shd)
                    except Exception:
                        pass
                    code_text = node.get("text", "")
                    r = p.add_run(code_text)
                    cls._set_font(r, "Courier New")
                    r.font.size = Pt(10.5)

                elif ntype in ["hr", "horizontal_rule"]:
                    p = doc.add_paragraph()
                    pPr = p._element.get_or_add_pPr()
                    pb = OxmlElement("w:pBdr")
                    bottom = OxmlElement("w:bottom")
                    bottom.set(qn("w:val"), "single")
                    bottom.set(qn("w:sz"), "8")
                    bottom.set(qn("w:color"), "CCCCCC")
                    pb.append(bottom)
                    pPr.append(pb)

                elif ntype == "page_break":
                    doc.add_page_break()

            except Exception as node_err:
                export_errors.append({"type": "ast_node", "node_index": node_idx, "node": node, "error": str(node_err)})
                try:
                    p_err = doc.add_paragraph()
                    p_err.add_run(f"[Lỗi kết xuất nội dung: {node.get('type')}]").italic = True
                except Exception:
                    pass

        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream.getvalue()

    @classmethod
    def export_to_word(cls, data_cache: Dict[str, Any]) -> bytes:
        if not isinstance(data_cache, dict):
            return cls.convert_markdown_to_docx_bytes(str(data_cache))
        markdown_content = data_cache.get("ai_generated_content", "")
        return cls.convert_markdown_to_docx_bytes(markdown_content, metadata=data_cache)


def export_word(markdown_text_or_cache) -> bytes:
    try:
        if isinstance(markdown_text_or_cache, dict):
            return WordExportEngine.export_to_word(markdown_text_or_cache)
        elif isinstance(markdown_text_or_cache, str):
            return WordExportEngine.convert_markdown_to_docx_bytes(markdown_text_or_cache, metadata=None)
        else:
            return WordExportEngine.convert_markdown_to_docx_bytes(str(markdown_text_or_cache), metadata=None)
    except Exception as fatal_err:
        fallback_doc = Document()
        fallback_doc.add_paragraph("KẾ HOẠCH BÀI DẠY (BẢN PHỤC HỒI)")
        fallback_doc.add_paragraph(f"Lỗi: {fatal_err}")
        if isinstance(markdown_text_or_cache, dict):
            fallback_doc.add_paragraph(str(markdown_text_or_cache.get("ai_generated_content", "")))
        else:
            fallback_doc.add_paragraph(str(markdown_text_or_cache))
        bio = io.BytesIO()
        fallback_doc.save(bio)
        bio.seek(0)
        return bio.getvalue()
