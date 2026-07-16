import io
import re
from typing import List, Dict, Any

import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

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
    _BLOCKQUOTE_RE = re.compile(r'^\s*>\s*(.*)')
    
    _MATH_RE = re.compile(r'(\$(?:\\[\s\S]|[^\$])+\$|\\\([\s\S]+?\\\))')
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
        ast_nodes, table_buf, code_buf, bq_buf = [], [], [], []
        code_lang, in_code, in_bq = "", False, False

        def flush_table():
            if table_buf:
                ast_nodes.append(cls._parse_table(table_buf))
                table_buf.clear()

        def flush_bq():
            if bq_buf:
                inner = cls.parse("\n".join(bq_buf))
                ast_nodes.append({"type": "callout", "style": "quote", "children": inner})
                bq_buf.clear()

        for raw_line in markdown_text.splitlines():
            if any(raw_line.lstrip().startswith(p) for p in forbidden): continue
            
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
                flush_table(); flush_bq(); in_code = True; code_lang = match.group(1).lower() or "text"; continue
            
            if match := cls._BLOCKQUOTE_RE.match(raw_line):
                flush_table(); in_bq = True; bq_buf.append(match.group(1)); continue
            elif in_bq and not match and s_line:
                bq_buf.append(raw_line); continue
            elif in_bq and not s_line:
                in_bq = False; flush_bq(); continue

            if not s_line: flush_table(); continue
            if s_line.startswith('|'): table_buf.append(s_line); continue
            flush_table()

            if cls._HR_RE.match(s_line): ast_nodes.append({"type": "hr"})
            elif match := cls._HEADING_RE.match(s_line): ast_nodes.append({"type": "heading", "level": len(match.group(1)), "tokens": cls._parse_inline_content(match.group(2))})
            elif match := cls._IMAGE_RE.match(s_line): ast_nodes.append({"type": "image", "alt": match.group(1), "url": match.group(2)})
            elif match := cls._CHECKBOX_RE.match(raw_line): ast_nodes.append({"type": "checkbox", "checked": match.group(3).lower()=='x', "level": (len(match.group(1))//2)+1, "tokens": cls._parse_inline_content(match.group(4))})
            elif match := cls._BULLET_RE.match(raw_line): ast_nodes.append({"type": "list_item", "style": "bullet", "level": (len(match.group(1))//2)+1, "tokens": cls._parse_inline_content(match.group(3))})
            elif match := cls._NUMBER_RE.match(raw_line): ast_nodes.append({"type": "list_item", "style": "number", "level": (len(match.group(1))//2)+1, "tokens": cls._parse_inline_content(match.group(3))})
            else: ast_nodes.append({"type": "paragraph", "tokens": cls._parse_inline_content(s_line)})

        flush_table(); flush_bq()
        return ast_nodes

    @classmethod
    def _parse_table(cls, lines: List[str]) -> Dict[str, Any]:
        rows, headers = [], []
        for line in lines:
            cells = [c.strip() for c in line.split('|') if c.strip() or '---' in c]
            if cells and not cells[0]: cells.pop(0)
            if cells and not cells[-1]: cells.pop()
            if not cells or any('---' in c for c in cells): continue
            p_cells = [{"content": cls._parse_inline_content(c)} for c in cells]
            if not headers: headers = p_cells
            else: rows.append(p_cells)
        return {"type": "table", "headers": headers, "rows": rows, "cols": len(headers) if headers else 0}

    @classmethod
    def _parse_inline_content(cls, text: str) -> List[Dict[str, Any]]:
        tokens = []
        if not text: return tokens
        parts = cls._MATH_RE.split(text)
        for part in parts:
            if not part: continue
            if (part.startswith('$') and part.endswith('$')) or (part.startswith(r'\(') and part.endswith(r'\)')):
                tokens.append({"type": "inline_math", "content": part.strip('$').replace(r'\(', '').replace(r'\)', '').strip()})
            else: tokens.extend(cls._parse_rich_text_styles(part))
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
        if s > 0: tokens.extend(cls._parse_rich_text_styles(text[:s]))
        for t in cls._parse_rich_text_styles(inner):
            tokens.append({"type": t_type, "content": t.get("content") or t.get("text", "")} if t["type"] == "text" else t)
        if e < len(text): tokens.extend(cls._parse_rich_text_styles(text[e:]))
        return tokens

# ==========================================
# 2. CHUẨN HÓA CÔNG THỨC TOÁN/HÓA HỌC
# ==========================================
class ScienceNormalizer:
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    SUP = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
    MAP = {
        r'\perp': '⊥', r'\circ': '°', r'\ne': '≠', r'\le': '≤', r'\ge': '≥', r'\times': '×', r'\div': '÷',
        r'\triangle': '△', r'\angle': '∠', r'\rightarrow': '→', r'\Rightarrow': '⇒', r'\approx': '≈',
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\pi': 'π', r'\sum': '∑', r'\int': '∫'
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        if not text: return ""
        text = text.replace('$', '').replace(r'\(', '').replace(r'\)', '').strip()
        # Xử lý phân số
        while r'\frac{' in text:
            text = re.sub(r'\\frac\{([\s\S]+?)\}\{([\s\S]+?)\}', r'((\1)/(\2))', text)
        text = re.sub(r'\\sqrt\{([\s\S]+?)\}', r'√(\1)', text)
        text = re.sub(r'([A-Z][a-z]?|\))(\d+)', lambda m: m.group(1) + m.group(2).translate(cls.SUB), text)
        text = re.sub(r'([A-Za-z₀₁₂₃₄₅₆₇₈₉\)]+)\^(\d*[+\-])', lambda m: m.group(1) + m.group(2).translate(cls.SUP), text)
        for k, v in cls.MAP.items(): text = text.replace(k, v)
        return re.sub(r'\\text\{([\s\S]+?)\}', r'\1', text)

# ==========================================
# 3. KẾT XUẤT TÀI LIỆU WORD (ENGINE)
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
        element = p_or_cell._element.get_or_add_pPr() if hasattr(p_or_cell, 'paragraphs') else p_or_cell._element.get_or_add_tcPr()
        shd = element.find(qn("w:shd"))
        if shd is None: 
            shd = OxmlElement("w:shd")
            element.append(shd)
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), color_hex)

    @classmethod
    def _render_inline(cls, p, tokens: List[Dict[str, Any]]):
        if not tokens: return
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
                elif tt == "subscript": run.font.subscript = True
                elif tt == "superscript": run.font.superscript = True
                elif tt == "highlight": run.font.highlight_color = 4
                elif tt == "inline_code": 
                    run.font.size = Pt(11)
                    run.font.color.rgb = RGBColor(199, 37, 78)
            elif tt == "inline_math":
                run = p.add_run(ScienceNormalizer.normalize(c))
                run.font.italic = True
                cls._set_font(run, "Times New Roman")

    @classmethod
    def convert_markdown_to_docx_bytes(cls, markdown_text: str) -> bytes:
        ast_nodes = MarkdownTokenizer.parse(markdown_text)
        doc = docx.Document()
        
        # Cấu hình chuẩn A4 Giáo dục
        for s in doc.sections:
            s.page_height, s.page_width = Inches(11.69), Inches(8.27)
            s.top_margin, s.bottom_margin, s.right_margin = Inches(0.79), Inches(0.79), Inches(0.79)
            s.left_margin = Inches(1.18)

        ns = doc.styles['Normal']
        ns.font.name, ns.font.size = 'Times New Roman', Pt(13)
        ns.paragraph_format.space_after = Pt(6)

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
                if lv == 1: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
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
                cls._set_font(r, "MS Gothic"); r.bold = True
                cls._render_inline(p, node.get("tokens", []))
            elif nt == "code":
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                cls._set_shading(p, "F5F5F5")
                r = p.add_run(node.get("text", ""))
                r.font.size = Pt(10.5); cls._set_font(r, "Courier New")
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
            elif nt == "table":
                rows, headers, cols = node.get("rows", []), node.get("headers", []), node.get("cols", 1)
                table = doc.add_table(rows=len(rows) + (1 if headers else 0), cols=cols)
                table.style = 'Table Grid'
                table.alignment = 1
                r_idx = 0
                if headers:
                    h_row = table.rows[0]
                    h_row._element.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
                    for c_idx, cell_n in enumerate(headers):
                        cell = h_row.cells[c_idx]
                        cls._set_shading(cell, "EAEAEA")
                        p = cell.paragraphs[0]
                        cls._render_inline(p, cell_n.get("content", []))
                        for r in p.runs: r.bold = True
                    r_idx = 1
                for loop_idx, r_data in enumerate(rows):
                    row = table.rows[r_idx]
                    row._element.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
                    bg = "F9F9F9" if loop_idx % 2 == 1 else "FFFFFF"
                    for c_idx, cell_n in enumerate(r_data):
                        cell = row.cells[c_idx]
                        cls._set_shading(cell, bg)
                        cls._render_inline(cell.paragraphs[0], cell_n.get("content", []))
                    r_idx += 1
                for row in table.rows:
                    for cell in row.cells: cell.width = Inches(6.3 / cols)

        bio = io.BytesIO()
        doc.save(bio)
        return bio.getvalue()

    # ==========================================
    # HÀM ADAPTER ĐỂ TƯƠNG THÍCH VỚI GIAO DIỆN
    # ==========================================
    @classmethod
    def export_to_word(cls, data_cache: Dict[str, Any]) -> bytes:
        """
        Hàm này giúp module xd_khbd.py gọi xuất file an toàn 
        mà không cần sửa lại code phần Frontend.
        """
        markdown_content = data_cache.get("ai_generated_content", "")
        return cls.convert_markdown_to_docx_bytes(markdown_content)
