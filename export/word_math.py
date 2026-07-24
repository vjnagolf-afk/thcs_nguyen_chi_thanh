# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_math.py
Nhiệm vụ: Xử lý và chuẩn hóa công thức toán học, số mũ, chỉ số hóa học,
phân số và căn bậc hai sang định dạng hiển thị chuẩn trên Microsoft Word 
(Sử dụng Font Cambria Math, hỗ trợ native Superscript & Subscript).
============================================================
"""

import re
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def parse_math_to_styled_runs(s: str):
    """Phân tách chuỗi toán học thành các thành phần (Normal, Superscript, Subscript) để Word hiển thị đúng số mũ và chỉ số."""
    runs = []
    i = 0
    n = len(s)
    current_text = ""
    current_style = "normal"  # 'normal', 'super', 'sub'
    
    while i < n:
        char = s[i]
        if char == '^' or char == '_':
            if current_text:
                runs.append((current_text, current_style))
                current_text = ""
            
            target_style = "super" if char == '^' else "sub"
            i += 1
            if i < n:
                if s[i] == '{':
                    i += 1
                    brace_content = ""
                    depth = 1
                    while i < n:
                        if s[i] == '{':
                            depth += 1
                            brace_content += s[i]
                        elif s[i] == '}':
                            depth -= 1
                            if depth == 0:
                                i += 1
                                break
                            else:
                                brace_content += s[i]
                        else:
                            brace_content += s[i]
                        i += 1
                    runs.append((brace_content, target_style))
                else:
                    sub_char = s[i]
                    runs.append((sub_char, target_style))
                    i += 1
        else:
            current_text += char
            i += 1
            
    if current_text:
        runs.append((current_text, current_style))
        
    return runs

def latex_to_word_math_string(latex_str: str) -> str:
    """Chuẩn hóa các ký hiệu LaTeX nâng cao (phân số, căn bậc hai, ký hiệu khoa học) sang định dạng Unicode trực quan."""
    if not latex_str:
        return ""
    
    s = latex_str.strip()
    s = s.replace('$', '').replace(r'\(', '').replace(r'\)', '').strip()
    
    # 1. Xử lý phân số \frac{a}{b} -> (a)/(b)
    while '\\frac' in s:
        match = re.search(r'\\frac\s*\{([^}]*)\}\s*\{([^}]*)\}', s)
        if match:
            num, den = match.groups()
            s = s.replace(match.group(0), f"({num})/({den})")
        else:
            break
            
    # 2. Xử lý căn bậc hai \sqrt{x} -> √ ( x ) (thêm khoảng trắng đệm để không bị cắt cụt dấu căn trên Word)
    while '\\sqrt' in s:
        match = re.search(r'\\sqrt\s*\{([^}]*)\}', s)
        if match:
            content = match.group(1)
            s = s.replace(match.group(0), f"√ ( {content} )")
        else:
            break
            
    # 3. Thay thế các ký hiệu toán học, logic và chữ Hy Lạp phổ biến
    replacements = {
        r'\\cdot'    : '·',
        r'\\times'   : '×',
        r'\\div'     : '÷',
        r'\\pm'      : '±',
        r'\\mp'      : '∓',
        r'\\leq'     : '≤',
        r'\\le'      : '≤',
        r'\\geq'     : '≥',
        r'\\ge'      : '≥',
        r'\\neq'     : '≠',
        r'\\approx'  : '≈',
        r'\\equiv'   : '≡',
        r'\\infty'   : '∞',
        r'\\sum'     : '∑',
        r'\\prod'    : '∏',
        r'\\int'     : '∫',
        r'\\partial' : '∂',
        r'\\Delta'   : 'Δ',
        r'\\alpha'   : 'α',
        r'\\beta'    : 'β',
        r'\\gamma'   : 'γ',
        r'\\pi'      : 'π',
        r'\\theta'   : 'θ',
        r'\\omega'   : 'ω',
        r'\\deg'     : '°',
        r'\\perp'    : '⊥',
        r'\\triangle': '△',
        r'\\angle'   : '∠',
        r'\\rightarrow': '→',
        r'\\Rightarrow': '⇒',
        r'\\quad'    : '    ',
        r'\\,'       : ' ',
    }
    
    for k, v in replacements.items():
        s = s.replace(k, v)
        
    s = s.replace(r'\left(', '(').replace(r'\right)', ')')
    s = s.replace(r'\left[', '[').replace(r'\right]', ']')
    
    return s

def insert_math_to_paragraph(paragraph, latex_content: str, is_block: bool = False):
    """
    Chèn công thức toán học vào đoạn văn Word, hỗ trợ hiển thị chính xác số mũ, 
    chỉ số dưới (hóa học), phân số và căn thức với font Cambria Math.
    """
    if not latex_content or not latex_content.strip():
        return
        
    try:
        processed_str = latex_to_word_math_string(latex_content)
        styled_runs = parse_math_to_styled_runs(processed_str)
        
        if is_block:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        for text, style in styled_runs:
            if not text:
                continue
            run = paragraph.add_run(text)
            run.font.name = 'Cambria Math'
            run.font.size = Pt(13)
            run.italic = True
            
            if style == 'super':
                run.font.superscript = True
            elif style == 'sub':
                run.font.subscript = True
                
    except Exception:
        # Fallback an toàn tuyệt đối
        run = paragraph.add_run(f" {latex_content} ")
        run.font.name = 'Cambria Math'
        run.italic = True
