# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_math.py
Nhiệm vụ: Chuyển đổi mã LaTeX thành Office MathML (OMML) native.
Sử dụng Trình biên dịch Cú pháp (Parser) an toàn tuyệt đối.
Hỗ trợ đầy đủ Lượng giác, Phân số, Mũ, Căn.
============================================================
"""

import re
from docx.oxml import parse_xml
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

def escape_xml(text: str) -> str:
    if not text: 
        return ""
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text

# Đã bổ sung các hàm Toán Lượng Giác & Logarit
SYMBOLS = {
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
    'leq': '≤', 'le': '≤', 'geq': '≥', 'ge': '≥', 'neq': '≠', 'ne': '≠',
    'approx': '≈', 'equiv': '≡', 'pm': '±', 'mp': '∓', 'times': '×',
    'cdot': '·', 'div': '÷', 'infty': '∞', 'partial': '∂', 'circ': '°',
    'sum': '∑', 'prod': '∏', 'int': '∫', 'perp': '⊥', 'angle': '∠',
    'triangle': '△', 'rightarrow': '→', 'Rightarrow': '⇒',
    'leftrightarrow': '↔', 'Leftrightarrow': '⇔',
    'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'cot': 'cot',
    'arcsin': 'arcsin', 'arccos': 'arccos', 'arctan': 'arctan',
    'log': 'log', 'ln': 'ln', 'lim': 'lim',
    'max': 'max', 'min': 'min',
    'quad': '    ', 'qquad': '        ', ',': ' ', ';': ' ', ':': ' '
}

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
                    elif cmd in SYMBOLS:
                        nodes.append(('text', SYMBOLS[cmd]))
                    elif cmd in ['text', 'mathrm', 'mathbf', 'operatorname']:
                        content = self.parse_group()
                        nodes.append(('group', content))
                    elif cmd in ['left', 'right']:
                        delim = self.get()
                        if delim == '\\':
                            match = re.match(r'[a-zA-Z]+|.', self.s[self.pos:])
                            if match:
                                self.pos += len(match.group(0))
                                delim = match.group(0)
                        if delim in ['{', '}']: 
                            delim = delim
                        nodes.append(('text', delim))
                    else:
                        nodes.append(('text', '\\' + cmd))
                else:
                    nodes.append(('text', '\\'))
                    
            elif c == '{':
                nodes.append(('group', self.parse_group_content()))
                
            elif c == '}':
                break
                
            elif c == '^':
                self.get()
                expr = self.parse_group()
                if nodes:
                    prev = nodes.pop()
                    if prev[0] == 'text' and len(prev[1]) > 1:
                        nodes.append(('text', prev[1][:-1]))
                        nodes.append(('sup', ('text', prev[1][-1]), expr))
                    elif prev[0] == 'sub':
                        nodes.append(('subsup', prev[1], prev[2], expr))
                    else:
                        nodes.append(('sup', prev, expr))
                else:
                    nodes.append(('sup', ('text', ''), expr))
                    
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
        while self.peek() in ' \t\n\r':
            self.get()
            
        if not self.peek():
            return []
        
        if self.peek() == '{':
            return self.parse_group_content()
        elif self.peek() == '\\':
            self.get()
            cmd_match = re.match(r'[a-zA-Z]+|.', self.s[self.pos:])
            if cmd_match:
                cmd = cmd_match.group(0)
                self.pos += len(cmd)
                if cmd == 'frac':
                    num = self.parse_group()
                    den = self.parse_group()
                    return [('frac', num, den)]
                elif cmd == 'sqrt':
                    if self.peek() == '[':
                        self.get()
                        deg = self.parse_until(']')
                        expr = self.parse_group()
                        return [('root', deg, expr)]
                    else:
                        expr = self.parse_group()
                        return [('sqrt', expr)]
                elif cmd in SYMBOLS:
                    return [('text', SYMBOLS[cmd])]
                else:
                    return [('text', '\\' + cmd)]
            else:
                return [('text', '\\')]
        else:
            return [('text', self.get())]

    def parse_group_content(self) -> list:
        self.get()
        start_pos = self.pos
        depth = 1
        while self.pos < self.n:
            c = self.get()
            if c == '{':
                depth += 1
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

def render_omml(nodes: list) -> str:
    if not nodes:
        return ""
    xml = ""
    for n in nodes:
        t = n[0]
        if t == 'text':
            xml += f'<m:r><m:t xml:space="preserve">{escape_xml(n[1])}</m:t></m:r>'
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
    if not latex_str or not latex_str.strip():
        return '<m:oMath xmlns:m="[http://schemas.openxmlformats.org/officeDocument/2006/math](http://schemas.openxmlformats.org/officeDocument/2006/math)"><m:r><m:t></m:t></m:r></m:oMath>'
    
    s = latex_str.strip()
    if s.startswith('$') and s.endswith('$'):
        s = s[1:-1]
    elif s.startswith('\\(') and s.endswith('\\)'):
        s = s[2:-2]
        
    try:
        parser = LatexParser(s)
        nodes = parser.parse()
        omml_body = render_omml(nodes)
        
        if not omml_body:
            omml_body = '<m:r><m:t></m:t></m:r>'
            
        return f'<m:oMath xmlns:m="[http://schemas.openxmlformats.org/officeDocument/2006/math](http://schemas.openxmlformats.org/officeDocument/2006/math)">{omml_body}</m:oMath>'
        
    except Exception:
        safe_text = escape_xml(s)
        return f'<m:oMath xmlns:m="[http://schemas.openxmlformats.org/officeDocument/2006/math](http://schemas.openxmlformats.org/officeDocument/2006/math)"><m:r><m:t xml:space="preserve">{safe_text}</m:t></m:r></m:oMath>'


def insert_math_to_paragraph(paragraph, latex_content: str, is_block: bool = False):
    if not latex_content or not latex_content.strip():
        return
        
    try:
        if is_block:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        omml_xml_string = latex_to_omml_xml(latex_content)
        omml_element = parse_xml(omml_xml_string)
        paragraph._p.append(omml_element)
        
    except Exception:
        run = paragraph.add_run(f" {latex_content} ")
        run.font.name = 'Cambria Math'
        run.italic = True
