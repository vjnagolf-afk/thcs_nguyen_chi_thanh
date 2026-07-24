# -*- coding: utf-8 -*-
import re
from typing import List, Dict, Any

class MarkdownTokenizer:
    """Bộ bóc tách chuỗi Markdown sang cây cú pháp sơ cấp (AST Tokens) không làm gãy công thức."""
    
    @classmethod
    def tokenize_inline(cls, text: str) -> List[Dict[str, Any]]:
        """Phân rã chính xác văn bản thường xen kẽ các đoạn toán học inline."""
        tokens = []
        i, n = 0, len(text)
        
        while i < n:
            # Ưu tiên nhận diện Math Block độc lập nằm bên trong dòng dữ liệu
            if text[i:i+2] == '$$':
                end_idx = text.find('$$', i + 2)
                if end_idx != -1:
                    tokens.append({'type': 'math_block', 'content': text[i+2:end_idx].strip()})
                    i = end_idx + 2
                    continue
                else:
                    tokens.append({'type': 'text', 'content': text[i:]})
                    break
            # Nhận diện Math Inline nằm lồng ghép
            elif text[i] == '$':
                end_idx = text.find('$', i + 1)
                if end_idx != -1:
                    tokens.append({'type': 'math_inline', 'content': text[i+1:end_idx].strip()})
                    i = end_idx + 1
                    continue
                else:
                    tokens.append({'type': 'text', 'content': text[i:]})
                    break
            else:
                next_dollar = text.find('$', i)
                if next_dollar == -1:
                    tokens.append({'type': 'text', 'content': text[i:]})
                    break
                else:
                    tokens.append({'type': 'text', 'content': text[i:next_dollar]})
                    i = next_dollar
        return tokens

    @classmethod
    def parse_rich_styles(cls, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Bổ sung gắn thẻ định dạng in đậm, in nghiêng cho phần text thường."""
        refined_tokens = []
        bold_re = re.compile(r'(\*\*|__)(.*?)\1')
        italic_re = re.compile(r'(\*|_)(.*?)\1')
        
        for tok in tokens:
            if tok['type'] != 'text':
                refined_tokens.append(tok)
                continue
                
            txt = tok['content']
            # Phân tách in đậm (Bold) sơ bộ
            parts = bold_re.split(txt)
            is_bold = False
            for part in parts:
                if not part and not is_bold:
                    is_bold = not is_bold
                    continue
                if is_bold:
                    refined_tokens.append({'type': 'bold', 'content': part})
                    is_bold = False
                else:
                    # Tiếp tục bóc tách in nghiêng (Italic) từ cụm text thường còn lại
                    sub_parts = italic_re.split(part)
                    is_italic = False
                    for sub_p in sub_parts:
                        if not sub_p and not is_italic:
                            is_italic = not is_italic
                            continue
                        if is_italic:
                            refined_tokens.append({'type': 'italic', 'content': sub_p})
                            is_italic = False
                        else:
                            if sub_p:
                                refined_tokens.append({'type': 'text', 'content': sub_p})
                    is_bold = True
        return refined_tokens
