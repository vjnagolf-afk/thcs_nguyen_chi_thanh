# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/export_word.py
Nhiệm vụ: Bộ điều phối trung tâm kết xuất Markdown / AI Generated Content 
vào Template Word (.docx) chuẩn 5512.
============================================================
"""

import io
import re
import logging
from typing import List, Dict, Any

import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

logger = logging.getLogger(__name__)

# ============================================================
# NẠP CÁC MODULE CON TRONG HỆ THỐNG EXPORT
# ============================================================
try: from .template_loader import get_word_document
except ImportError:
    def get_word_document(): return Document()

try: from .word_styles import set_run_font, align_paragraph
except ImportError:
    def set_run_font(run, *args, **kwargs): pass
    def align_paragraph(p, align): p.alignment = align

try: from .markdown_tokenizer import MarkdownTokenizer
except ImportError: MarkdownTokenizer = None

try: from .word_math import insert_math_to_paragraph
except ImportError: insert_math_to_paragraph = None

try: from .word_tables import process_and_draw_markdown_table
except ImportError: process_and_draw_markdown_table = None

try: from .word_images import insert_image_to_paragraph
except ImportError: insert_image_to_paragraph = None


# ============================================================
# BỘ SANITIZER & AUTO-FIX LATEX
# ============================================================
def _sanitize_and_fix_math(text: str) -> str:
    if not text: return ""
    # Khử đột biến ký tự (Biến | thành \)
    text = re.sub(r'\|(sqrt|frac|approx|times|sin|cos|tan|cot|lim|log|ln|alpha|beta|gamma|Delta|pi|text)\b', r'\\\1', text)

    protected = []
    def protect_math(match):
        protected.append(match.group(0))
        return f"@@MATH_PROTECTED_{len(protected) - 1}@@"

    text = re.sub(r"\$\$[\s\S]*?\$\$", protect_math, text)
    text = re.sub(r"\$(?!\$)[^$\n]+?\$(?!\$)", protect_math, text)

    formula_pattern = re.compile(
        r"""
        (?<![\w$])
        (
            (?:[a-zA-Z][a-zA-Z0-9_]*|\d+)\^\{?[^{}\n]+\}?
            \s*(?:=|<|>|\le|\ge|\approx|\neq)\s*
            [^.,;:\n]+?(?=[.,;:]?(?:\s|$))
            |
            [A-Za-z](?:_\{[^{}\n]+\}|_\d+|\d+)
            \s*=\s*(?:\\frac\s*\{[^{}\n]+\}\s*\{[^{}\n]+\})
            |
            \\sqrt\s*(?:\[[^\]]*\])?\s*\{[^{}\n]+\}
            \s*(?:=|\approx)\s*
            [^.,;:\n]+?(?=[.,;:]?(?:\s|$))
        )
        (?![\w$])
        """, re.VERBOSE
    )

    def wrap_formula(match):
        formula = match.group(1).strip()
        formula = re.sub(r"\b([A-Za-z])(\d{1,3})\b", r"\1_{\2}", formula)
        return f"${formula}$"

    text = formula_pattern.sub(wrap_formula, text)
    text = re.sub(r"(?<![$\w])([a-zA-Z]\^\{?[^{}\n\s]+\}?)(?![$])", r"$\1$", text)
    text = re.sub(r"(?<![$\\])(\\frac\s*\{[^{}\n]*\}\s*\{[^{}\n]*\})(?![$])", r"$\1$", text)
    text = re.sub(r"(?<![$\\])(\\sqrt(?:\[[^\]]*\])?\s*\{[^{}\n]*\})(?![$])", r"$\1$", text)

    for idx, original in enumerate(protected):
        text = text.replace(f"@@MATH_PROTECTED_{idx}@@", original)

    return text


def _parse_inline_with_math_and_images(text: str) -> List[Dict[str, Any]]:
    tokens = []
    pattern = re.compile(
        r'(\$\$(.*?)\$\$)|'
        r'(\$([^$]+?)\$)|'
        r'(\[IMAGE\s*(?:-\s*ID:\s*)?([^\]]+)\])|'
        r'(\[TABLE\s*(?:-\s*ID:\s*)?([^\]]+)\])|'
        r'(\*\*([^*]+?)\*\*)|'
        r'(\*([^*]+?)\*)'
    )
    last_idx = 0
    for match in pattern.finditer(text):
        if match.start() > last_idx:
            tokens.append({"type": "text", "content": text[last_idx:match.start()]})
        
        if match.group(1): tokens.append({"type": "block_math", "content": match.group(2)})
        elif match.group(3): tokens.append({"type": "inline_math", "content": match.group(4)})
        elif match.group(5): tokens.append({"type": "image", "content": match.group(6).strip()})
        elif match.group(7): tokens.append({"type": "text", "content": f"[BẢNG/SỐ LIỆU ĐÍNH KÈM: {match.group(8).strip()}]"})
        elif match.group(9): tokens.append({"type": "bold", "content": match.group(10)})
        elif match.group(11): tokens.append({"type": "italic", "content": match.group(12)})
        last_idx = match.end()
        
    if last_idx < len(text):
        tokens.append({"type": "text", "content": text[last_idx:]})
    return tokens


def _fallback_parse_markdown(markdown_text: str) -> List[Dict[str, Any]]:
    ast_nodes, lines = [], (markdown_text or "").splitlines()
    table_buffer, in_code, code_lang, code_buffer = [], False, "", []

    def flush_table():
        if table_buffer:
            ast_nodes.append({"type": "table_raw_lines", "lines": list(table_buffer)})
            table_buffer.clear()

    for line in lines:
        s_line = line.strip()
        if s_line.startswith("```"):
            if in_code:
                in_code, ast_nodes.append({"type": "code", "language": code_lang, "text": "\n".join(code_buffer)}), code_buffer.clear()
            else: flush_table(), in_code, code_lang = True, s_line.lstrip("`").strip()
            continue
        if in_code: code_buffer.append(line); continue
        if s_line.startswith("|"): table_buffer.append(s_line); continue
        else: flush_table()
        if not s_line: continue
        
        if s_line.startswith("$$") and s_line.endswith("$$") and len(s_line) > 4:
            ast_nodes.append({"type": "block_math", "content": s_line[2:-2].strip()}); continue
        if s_line.startswith("#"):
            match = re.match(r'^(#{1,6})\s+(.*)', s_line)
            if match: ast_nodes.append({"type": "heading", "level": len(match.group(1)), "text": match.group(2), "tokens": _parse_inline_with_math_and_images(match.group(2))}); continue
        if s_line.startswith("- ") or s_line.startswith("* "):
            ast_nodes.append({"type": "list_item", "style": "bullet", "level": 1, "tokens": _parse_inline_with_math_and_images(s_line[2:].strip())}); continue
        num_match = re.match(r'^\d+\.\s+(.*)', s_line)
        if num_match:
            ast_nodes.append({"type": "list_item", "style": "number", "level": 1, "tokens": _parse_inline_with_math_and_images(num_match.group(1))}); continue
            
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)', s_line)
        if img_match: ast_nodes.append({"type": "image", "content": img_match.group(2)}); continue
        ast_nodes.append({"type": "paragraph", "text": s_line, "tokens": _parse_inline_with_math_and_images(s_line)})

    flush_table()
    return ast_nodes


# ============================================================
# LỚP ĐIỀU PHỐI KẾT XUẤT CHÍNH
# ============================================================
class WordExportEngine:

    @classmethod
    def _render_inline_tokens(cls, p, tokens: List[Dict[str, Any]], export_errors: List[Dict[str, Any]], data_cache: dict = None):
        if not tokens: return
        for idx, token in enumerate(tokens):
            try:
                ttype = token.get("type", "text")
                content = token.get("content") or token.get("text") or ""

                if ttype in ["text", "bold", "italic", "underline", "strike", "highlight", "inline_code", "code"]:
                    if ttype in ["inline_code", "code"]:
                        run = p.add_run(content)
                        set_run_font(run, "Courier New", 11)
                    else:
                        sub_tokens = _parse_inline_with_math_and_images(_sanitize_and_fix_math(content))
                        if len(sub_tokens) > 1 or (sub_tokens and sub_tokens[0].get("type") != "text"):
                            cls._render_inline_tokens(p, sub_tokens, export_errors, data_cache)
                        else:
                            run = p.add_run(content)
                            set_run_font(run, "Times New Roman", 13, bold=(ttype=="bold"), italic=(ttype=="italic"))
                            if ttype == "underline": run.underline = True
                            elif ttype == "strike": run.font.strike = True
                            elif ttype == "highlight": run.font.color.rgb = RGBColor(199, 37, 78)
                    continue

                if ttype in ["inline_math", "math_inline", "math", "math_block", "block_math"]:
                    if insert_math_to_paragraph: insert_math_to_paragraph(p, content, is_block=(ttype in ["math_block", "block_math"]))
                    else:
                        run = p.add_run(f" {content} ")
                        set_run_font(run, "Cambria Math", 13, italic=True)

                elif ttype == "image":
                    img_id = content
                    img_src = None
                    if data_cache and "pages" in data_cache:
                        for page in data_cache["pages"]:
                            for img in page.get("images", []):
                                if img.get("id") == img_id:
                                    img_src = {"base64": img.get("base64"), "caption": img_id}
                                    break
                            if img_src: break
                    if insert_image_to_paragraph: insert_image_to_paragraph(p, img_src if img_src else img_id)
                    else: p.add_run(f"[Hình ảnh: {img_id}]").italic = True

                else:
                    run = p.add_run(str(content))
                    set_run_font(run, "Times New Roman", 13)

            except Exception as e:
                export_errors.append({"type": "inline_token", "index": idx, "token": token, "error": str(e)})

    @classmethod
    def convert_markdown_to_docx_bytes(cls, markdown_text: str, metadata: dict = None) -> bytes:
        export_errors = []
        
        # 1. Khởi tạo Document (Tải từ Template nếu có thể)
        doc = get_word_document()

        # Áp dụng bộ lọc khử đột biến và bọc toán học
        markdown_text = _sanitize_and_fix_math(markdown_text or "")

        ast_nodes = []
        if MarkdownTokenizer and hasattr(MarkdownTokenizer, 'parse'):
            try: ast_nodes = MarkdownTokenizer.parse(markdown_text)
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
                    tokens = node.get("tokens", [])
                    if tokens: cls._render_inline_tokens(p, tokens, export_errors, metadata)
                    elif raw_text:
                        inline_tokens = _parse_inline_with_math_and_images(_sanitize_and_fix_math(raw_text))
                        cls._render_inline_tokens(p, inline_tokens, export_errors, metadata)

                elif ntype == "heading":
                    level = min(max(node.get("level", 1), 1), 6)
                    p = doc.add_paragraph()
                    p.paragraph_format.space_before = Pt(10)
                    p.paragraph_format.space_after = Pt(4)
                    p.paragraph_format.keep_with_next = True
                    align_paragraph(p, WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT)

                    tokens = node.get("tokens", [])
                    if tokens: cls._render_inline_tokens(p, tokens, export_errors, metadata)
                    else:
                        inline_tokens = _parse_inline_with_math_and_images(_sanitize_and_fix_math(str(node.get("text") or "")))
                        cls._render_inline_tokens(p, inline_tokens, export_errors, metadata)

                    for r in p.runs: set_run_font(r, "Times New Roman", 16 if level == 1 else (14 if level == 2 else 13), bold=True)

                elif ntype in ["block_math", "math_block"]:
                    math_content = node.get("content") or node.get("text") or ""
                    p = doc.add_paragraph()
                    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(6), Pt(6)
                    if insert_math_to_paragraph: insert_math_to_paragraph(p, math_content, is_block=True)
                    else:
                        align_paragraph(p, WD_ALIGN_PARAGRAPH.CENTER)
                        r = p.add_run(math_content)
                        set_run_font(r, "Cambria Math", 13, italic=True)

                elif ntype in ["list_item", "bullet_list", "numbered_list"]:
                    style_name = 'List Number' if (node.get("style") == "number" or ntype == "numbered_list") else 'List Bullet'
                    level = node.get("level", 1)
                    p = doc.add_paragraph(style=style_name)
                    p.paragraph_format.left_indent = Inches(0.25 * level + 0.25)
                    p.paragraph_format.first_line_indent = Inches(-0.25)
                    p.paragraph_format.space_after = Pt(3)

                    tokens = node.get("tokens", [])
                    if tokens: cls._render_inline_tokens(p, tokens, export_errors, metadata)
                    else:
                        inline_tokens = _parse_inline_with_math_and_images(_sanitize_and_fix_math(str(node.get("text") or "")))
                        cls._render_inline_tokens(p, inline_tokens, export_errors, metadata)

                elif ntype == "image":
                    p = doc.add_paragraph()
                    align_paragraph(p, WD_ALIGN_PARAGRAPH.CENTER)
                    img_id = node.get("content") or node.get("url") or node.get("path")
                    img_src = None
                    if metadata and "pages" in metadata:
                        for page in metadata["pages"]:
                            for img in page.get("images", []):
                                if img.get("id") == img_id:
                                    img_src = {"base64": img.get("base64"), "caption": img_id}
                                    break
                            if img_src: break
                    if insert_image_to_paragraph: insert_image_to_paragraph(p, img_src if img_src else img_id)
                    else: p.add_run(f"[Hình ảnh: {img_id}]").italic = True

                elif ntype in ["table", "table_raw_lines"]:
                    lines = node.get("lines", [])
                    if process_and_draw_markdown_table and lines:
                        process_and_draw_markdown_table(doc, lines, metadata)
                    else:
                        for line in lines: doc.add_paragraph().add_run(str(line))

            except Exception as node_err:
                export_errors.append({"type": "ast_node", "node_index": node_idx, "node": node, "error": str(node_err)})

        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream.getvalue()

    @classmethod
    def export_to_word(cls, data_cache: Dict[str, Any]) -> bytes:
        if not isinstance(data_cache, dict): return cls.convert_markdown_to_docx_bytes(str(data_cache))
        return cls.convert_markdown_to_docx_bytes(data_cache.get("ai_generated_content", ""), metadata=data_cache)


def export_word(markdown_text_or_cache) -> bytes:
    try:
        if isinstance(markdown_text_or_cache, dict): return WordExportEngine.export_to_word(markdown_text_or_cache)
        return WordExportEngine.convert_markdown_to_docx_bytes(str(markdown_text_or_cache), metadata=None)
    except Exception as fatal_err:
        fallback_doc = Document()
        fallback_doc.add_paragraph("LỖI KẾT XUẤT GIÁO ÁN").bold = True
        fallback_doc.add_paragraph(f"Chi tiết lỗi: {fatal_err}")
        bio = io.BytesIO()
        fallback_doc.save(bio)
        bio.seek(0)
        return bio.getvalue()
