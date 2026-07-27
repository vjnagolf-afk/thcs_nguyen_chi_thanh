# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_math.py
Nhiệm vụ: Trình biên dịch AST (Abstract Syntax Tree) mạnh mẽ
chuyển đổi LaTeX thành Office MathML (OMML) Native của Word.
Hỗ trợ lồng ghép phức tạp Toán, Lý, Hóa (Phân số, Căn, Mũ, Chỉ số).
============================================================
"""

import re
import logging
from docx.oxml import parse_xml
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

logger = logging.getLogger(__name__)

# ============================================================
# 1. HÀM ESCAPE XML AN TOÀN TUYỆT ĐỐI
# ============================================================
def escape_xml(text: str) -> str:
    """Bảo vệ an toàn mọi ký tự nhạy cảm khi nhúng vào XML."""
    if not text: 
        return ""
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text

# ============================================================
# 2. TỪ ĐIỂN KÝ HIỆU KHOA HỌC (KHTN)
# ============================================================
SYMBOLS = {
    # Greek letters
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε',
    'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'iota': 'ι', 'kappa': 'κ',
    'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ', 'omicron': 'ο',
    'pi': 'π', 'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ',
    'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω',
    'Alpha': 'Α', 'Beta': 'Β', 'Gamma': 'Γ', 'Delta': 'Δ', 'Epsilon': 'Ε',
    'Zeta': 'Ζ', 'Eta': 'Η', 'Theta': 'Θ', 'Iota': 'Ι', 'Kappa': 'Κ',
    'Lambda': 'Λ', 'Mu': 'Μ', 'Nu': 'Ν', 'Xi': 'Ξ', 'Omicron': 'Ο',
    'Pi': 'Π', 'Rho': 'Ρ', 'Sigma': 'Σ', 'Tau': 'Τ', 'Upsilon': 'Υ',
    'Phi': 'Φ', 'Chi': 'Χ', 'Psi': 'Ψ', 'Omega': 'Ω',
    
    # Toán học & Lượng giác
    'leq': '≤', 'le': '≤', 'geq': '≥', 'ge': '≥', 'neq': '≠', 'ne': '≠',
    'approx': '≈', 'equiv': '≡', 'pm': '±', 'mp': '∓', 'times': '×',
    'cdot': '·', 'div': '÷', 'infty': '∞', 'partial': '∂', 'circ': '°',
    'sum': '∑', 'prod': '∏', 'int': '∫', 'perp': '⊥', 'angle': '∠',
    'triangle': '△', 'rightarrow': '→', 'Rightarrow': '⇒',
    'leftrightarrow': '↔', 'Leftrightarrow': '⇔',
    'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'cot': 'cot',
    'arcsin': 'arcsin', 'arccos': 'arccos', 'arctan': 'arctan',
    'log': 'log', 'ln': 'ln', 'lim': 'lim', 'max': 'max', 'min': 'min',
    
    # Khoảng trắng
    'quad': '    ', 'qquad': '        ', ',': ' ', ';': ' ', ':': ' ', ' ': ' '
}

# ============================================================
# 3. TRÌNH PHÂN TÍCH CÚ PHÁP LATEX (RECURSIVE AST PARSER)
# ============================================================
class LatexParser:
    def __init__(self, s: str):
        self.s = s
        self.pos = 0
        self.n = len(s)

    def peek(self) -> str:
        return self.s[self.pos] if self.pos < self.n else ''

    def get(self) -> str:
        c = self.peek()
        self.pos += 1
        return c

    def parse(self) -> list:
        nodes = []
        while self.pos < self.n:
            c = self.peek()
            
            # Xử lý lệnh LaTeX bắt đầu bằng \
            if c == '\\':
                self.get()
                cmd_match = re.match(r'[a-zA-Z]+|.', self.s[self.pos:])
                if cmd_match:
                    cmd = cmd_match.group(0)
                    self.pos += len(cmd)
                    
                    if cmd == 'frac':
                        num = self.parse_group()
                        den = self.parse_group()
                        nodes.append(('frac', num, den))
                    elif cmd == 'sqrt':
                        if self.peek() == '[':
                            self.get()
                            deg = self.parse_until(']')
                            expr = self.parse_group()
                            nodes.append(('root', deg, expr))
                        else:
                            expr = self.parse_group()
                            nodes.append(('sqrt', expr))
                    elif cmd == 'text':
                        content = self.parse_group()
                        nodes.append(('normal_text', content))
                    elif cmd in ['mathrm', 'mathbf', 'operatorname', 'widehat']:
                        content = self.parse_group()
                        nodes.append(('group', content))
                    elif cmd in SYMBOLS:
                        nodes.append(('text', SYMBOLS[cmd]))
                    elif cmd in ['left', 'right']:
                        delim = self.get()
                        if delim == '\\':
                            m = re.match(r'[a-zA-Z]+|.', self.s[self.pos:])
                            if m:
                                self.pos += len(m.group(0))
                                delim = m.group(0)
                        nodes.append(('text', delim))
                    else:
                        nodes.append(('text', '\\' + cmd))
                else:
                    nodes.append(('text', '\\'))
                    
            # Xử lý khối ngoặc {...}
            elif c == '{':
                nodes.append(('group', self.parse_group_content()))
                
            elif c == '}':
                break # Đảm bảo an toàn không kẹt vòng lặp
                
            # Xử lý số mũ (Superscript)
            elif c == '^':
                self.get()
                expr = self.parse_group()
                if nodes:
                    prev = nodes.pop()
                    # Bóc tách kỹ tự đứng liền kề trước đó (Ví dụ F trong F^2, hoặc e trong Fe^{3+})
                    if prev[0] == 'text' and len(prev[1]) > 1:
                        nodes.append(('text', prev[1][:-1]))
                        nodes.append(('sup', ('text', prev[1][-1]), expr))
                    elif prev[0] == 'sub':
                        nodes.append(('subsup', prev[1], prev[2], expr))
                    else:
                        nodes.append(('sup', prev, expr))
                else:
                    nodes.append(('sup', ('text', ''), expr)) # Trường hợp ^14C (Không có base)
                    
            # Xử lý chỉ số dưới (Subscript)
            elif c == '_':
                self.get()
                expr = self.parse_group()
                if nodes:
                    prev = nodes.pop()
                    if prev[0] == 'text' and len(prev[1]) > 1:
                        nodes.append(('text', prev[1][:-1]))
                        nodes.append(('sub', ('text', prev[1][-1]), expr))
                    elif prev[0] == 'sup':
                        nodes.append(('subsup', prev[1], expr, prev[2]))
                    else:
                        nodes.append(('sub', prev, expr))
                else:
                    nodes.append(('sub', ('text', ''), expr))
                    
            else:
                nodes.append(('text', self.get()))
                
        return self.combine_text_nodes(nodes)

    def parse_group(self) -> list:
        """Lấy một phần tử (có thể là ký tự đơn hoặc khối {...}) làm tham số."""
        while self.peek() in ' \t\n\r':
            self.get()
            
        if not self.peek(): return []
        
        if self.peek() == '{':
            return self.parse_group_content()
        elif self.peek() == '\\':
            self.get()
            cmd_match = re.match(r'[a-zA-Z]+|.', self.s[self.pos:])
            if cmd_match:
                cmd = cmd_match.group(0)
                self.pos += len(cmd)
                if cmd == 'frac': return [('frac', self.parse_group(), self.parse_group())]
                elif cmd == 'sqrt':
                    if self.peek() == '[':
                        self.get()
                        deg = self.parse_until(']')
                        return [('root', deg, self.parse_group())]
                    return [('sqrt', self.parse_group())]
                elif cmd == 'text': return [('normal_text', self.parse_group())]
                elif cmd in SYMBOLS: return [('text', SYMBOLS[cmd])]
                else: return [('text', '\\' + cmd)]
            else:
                return [('text', '\\')]
        else:
            return [('text', self.get())]

    def parse_group_content(self) -> list:
        """Phân tích nội dung nằm trong ngoặc nhọn {...}"""
        self.get() # Bỏ qua '{'
        start_pos = self.pos
        depth = 1
        while self.pos < self.n:
            c = self.get()
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    inner = self.s[start_pos:self.pos-1]
                    return LatexParser(inner).parse()
        inner = self.s[start_pos:self.pos]
        return LatexParser(inner).parse()

    def parse_until(self, end_char: str) -> list:
        start = self.pos
        while self.pos < self.n and self.peek() != end_char:
            self.get()
        inner = self.s[start:self.pos]
        if self.peek() == end_char:
            self.get()
        return LatexParser(inner).parse()

    def combine_text_nodes(self, nodes: list) -> list:
        """Gộp các ký tự rời rạc thành chuỗi liền mạch để tối ưu XML."""
        res = []
        cur_text = ""
        for n in nodes:
            if n[0] == 'text':
                cur_text += n[1]
            else:
                if cur_text:
                    res.append(('text', cur_text))
                    cur_text = ""
                res.append(n)
        if cur_text:
            res.append(('text', cur_text))
        return res


# ============================================================
# 4. KẾT XUẤT CÂY AST THÀNH MÃ XML OMML CỦA WORD
# ============================================================
def render_omml(nodes: list) -> str:
    if not nodes: return ""
    xml = ""
    for n in nodes:
        t = n[0]
        if t == 'text':
            # xml:space="preserve" giữ nguyên dấu cách trong Vật lý (vd: F = m a)
            xml += f'<m:r><m:t xml:space="preserve">{escape_xml(n[1])}</m:t></m:r>'
        elif t == 'normal_text':
            # Ép thẻ <m:nor/> để text (như đơn vị m/s) không bị in nghiêng
            inner_xml = render_omml(n[1])
            inner_xml = inner_xml.replace('<m:r>', '<m:r><m:rPr><m:nor/></m:rPr>')
            xml += inner_xml
        elif t == 'group':
            xml += render_omml(n[1])
        elif t == 'frac':
            num = render_omml(n[1]) or "<m:r><m:t></m:t></m:r>"
            den = render_omml(n[2]) or "<m:r><m:t></m:t></m:r>"
            xml += f"<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>"
        elif t == 'sqrt':
            expr = render_omml(n[1]) or "<m:r><m:t></m:t></m:r>"
            xml += f"<m:rad><m:deg/><m:e>{expr}</m:e></m:rad>"
        elif t == 'root':
            deg = render_omml(n[1]) or "<m:r><m:t></m:t></m:r>"
            expr = render_omml(n[2]) or "<m:r><m:t></m:t></m:r>"
            xml += f"<m:rad><m:deg>{deg}</m:deg><m:e>{expr}</m:e></m:rad>"
        elif t == 'sup':
            base = render_omml([n[1]]) or "<m:r><m:t></m:t></m:r>"
            exp = render_omml(n[2]) or "<m:r><m:t></m:t></m:r>"
            xml += f"<m:sSup><m:e>{base}</m:e><m:sup>{exp}</m:sup></m:sSup>"
        elif t == 'sub':
            base = render_omml([n[1]]) or "<m:r><m:t></m:t></m:r>"
            sub = render_omml(n[2]) or "<m:r><m:t></m:t></m:r>"
            xml += f"<m:sSub><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>"
        elif t == 'subsup':
            base = render_omml([n[1]]) or "<m:r><m:t></m:t></m:r>"
            sub = render_omml(n[2]) or "<m:r><m:t></m:t></m:r>"
            exp = render_omml(n[3]) or "<m:r><m:t></m:t></m:r>"
            xml += f"<m:sSubSup><m:e>{base}</m:e><m:sub>{sub}</m:sub><m:sup>{exp}</m:sup></m:sSubSup>"
    return xml

def latex_to_omml_xml(latex_str: str) -> str:
    """Hàm lõi dịch chuỗi LaTeX thành Office MathML."""
    if not latex_str or not latex_str.strip():
        return '<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:r><m:t></m:t></m:r></m:oMath>'
    
    # Lột bỏ vỏ $ hoặc \( \) của AI
    s = latex_str.strip()
    if s.startswith('$$') and s.endswith('$$'): s = s[2:-2]
    elif s.startswith('$') and s.endswith('$'): s = s[1:-1]
    elif s.startswith('\\[') and s.endswith('\\]'): s = s[2:-2]
    elif s.startswith('\\(') and s.endswith('\\)'): s = s[2:-2]
        
    try:
        parser = LatexParser(s)
        nodes = parser.parse()
        omml_body = render_omml(nodes)
        
        if not omml_body:
            omml_body = '<m:r><m:t></m:t></m:r>'
            
        return f'<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">{omml_body}</m:oMath>'
        
    except Exception as e:
        logger.error(f"Lỗi biên dịch Toán học: {e} với chuỗi: {latex_str}")
        # Cứu hộ khẩn cấp bằng văn bản Cambria Math nếu AST gãy
        safe_text = escape_xml(s)
        return f'<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:r><m:t xml:space="preserve">{safe_text}</m:t></m:r></m:oMath>'


# ============================================================
# 5. GIAO TIẾP VỚI ENGINE XUẤT WORD
# ============================================================
def insert_math_to_paragraph(paragraph, latex_content: str, is_block: bool = False):
    """
    API Công khai: Gắn công thức OMML vào Paragraph của thư viện python-docx.
    An toàn 100%, có fallback.
    """
    if not latex_content or not latex_content.strip():
        return
        
    try:
        if is_block:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        omml_xml_string = latex_to_omml_xml(latex_content)
        omml_element = parse_xml(omml_xml_string)
        paragraph._p.append(omml_element)
        
    except Exception as e:
        logger.error(f"Lỗi chèn OMML vào Paragraph: {e}")
        # Fallback in nghiêng font Cambria Math
        run = paragraph.add_run(f" {latex_content} ")
        run.font.name = 'Cambria Math'
        run.italic = True
