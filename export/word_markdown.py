import re
from typing import List, Dict, Any

class MarkdownTokenizer:
    # 1. Các Regex xử lý mức Khối (Block Level)
    _HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)')
    _IMAGE_RE = re.compile(r'^!\[(.*?)\]\((.*?)\)')
    _BULLET_RE = re.compile(r'^(\s*)([\*\-])\s+(.*)')
    _NUMBER_RE = re.compile(r'^(\s*)(\d+\.)\s+(.*)')
    _HR_RE = re.compile(r'^\s*([-*_])\1{2,}\s*$')  # Nhận diện ---, ***, ___ (tối thiểu 3 ký tự giống nhau)
    _CODE_BLOCK_START_RE = re.compile(r'^```(\w*)')
    _BLOCKQUOTE_PREFIX_RE = re.compile(r'^\s*>\s*')

    # 2. Các Regex xử lý mức Nội dòng (Inline Level)
    # Khắc phục lỗi Toán học chứa các ký tự đặc biệt như \(\frac, \sqrt, ^, _     _MATH_RE =\) re.compile(r'(\$(?:\\[\s\S]|[^\$])+\$|\\\([\s\S]+?\\\))')
    
    # Định dạng văn bản phong phú (Đảm bảo độ ưu tiên bóc tách từ phức tạp đến đơn giản)
    _BOLD_RE = re.compile(r'(\*\*\*|___\b)(.*?)\1|(\*\*|__\b)(.*?)\3')
    _ITALIC_RE = re.compile(r'(\*|_\b)(.*?)\1')
    _UNDERLINE_RE = re.compile(r'<u>(.*?)</u>', re.IGNORECASE)
    _STRIKE_RE = re.compile(r'~~(.*?)~~')

    @classmethod
    def parse(cls, markdown_text: str) -> List[Dict[str, Any]]:
        forbidden_prefixes = ("Chào bạn", "Với vai trò", "Tôi là", "Lưu ý về")
        
        lines = [
            line for line in markdown_text.splitlines() 
            if not line.lstrip().startswith(forbidden_prefixes)
        ]

        ast_nodes = []
        table_buffer = []
        code_buffer = []
        code_language = ""
        in_code_block = False

        def flush_table():
            if table_buffer:
                ast_nodes.append(cls._parse_table(table_buffer))
                table_buffer.clear()

        for raw_line in lines:
            # 1. Kiểm tra trạng thái đang trong Khối mã (Code Block)
            if in_code_block:
                if raw_line.strip() == "```":
                    in_code_block = False
                    ast_nodes.append({
                        "type": "code",
                        "language": code_language,
                        "text": "\n".join(code_buffer)
                    })
                    code_buffer.clear()
                    code_language = ""
                else:
                    code_buffer.append(raw_line)
                continue

            # Xóa dấu trích dẫn > từ File 1
            line = cls._BLOCKQUOTE_PREFIX_RE.sub('', raw_line)
            stripped_line = line.strip()

            # 2. Phát hiện bắt đầu Khối mã mới
            if match := cls._CODE_BLOCK_START_RE.match(stripped_line):
                flush_table()
                in_code_block = True
                code_language = match.group(1).lower() or "text"
                continue

            # Nếu dòng trống, giải phóng hàng đợi bảng
            if not stripped_line:
                flush_table()
                continue

            # 3. Gom nhóm dữ liệu Bảng
            if stripped_line.startswith('|'):
                table_buffer.append(stripped_line)
                continue

            flush_table()

            # 4. Nhận diện các định dạng khối chuyên biệt
            if cls._HR_RE.match(stripped_line):
                ast_nodes.append({"type": "hr"})
                
            elif match := cls._HEADING_RE.match(stripped_line):
                ast_nodes.append({
                    "type": "heading",
                    "level": len(match.group(1)),
                    "tokens": cls._parse_inline_content(match.group(2))
                })
                
            elif match := cls._IMAGE_RE.match(stripped_line):
                ast_nodes.append({
                    "type": "image",
                    "alt": match.group(1),
                    "url": match.group(2)
                })
                
            elif match := cls._BULLET_RE.match(line):
                indent = len(match.group(1))
                level = (indent // 2) + 1  # Quy đổi 2 khoảng trắng thành 1 cấp độ lồng
                ast_nodes.append({
                    "type": "list_item",
                    "style": "bullet",
                    "level": level,
                    "tokens": cls._parse_inline_content(match.group(3))
                })
                
            elif match := cls._NUMBER_RE.match(line):
                indent = len(match.group(1))
                level = (indent // 2) + 1
                ast_nodes.append({
                    "type": "list_item",
                    "style": "number",
                    "level": level,
                    "tokens": cls._parse_inline_content(match.group(3))
                })
                
            else:
                ast_nodes.append({
                    "type": "paragraph",
                    "tokens": cls._parse_inline_content(stripped_line)
                })

        flush_table()
        return ast_nodes

    @staticmethod
    def _parse_table(lines: List[str]) -> Dict[str, Any]:
        rows = []
        headers = []
        for line in lines:
            cells = [c.strip() for c in line.split('|')]
            if cells and not cells[0]: cells.pop(0)
            if cells and not cells[-1]: cells.pop()
            if not cells: continue

            if any(re.match(r'^\s*:-?-?:*\s*$', c) or '---' in c for c in cells):
                continue

            processed_cells = [{"content": MarkdownTokenizer._parse_inline_content(c)} for c in cells]
            if not headers:
                headers = processed_cells
            else:
                rows.append(processed_cells)

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
            "cols": len(headers) if headers else 0
        }

    @classmethod
    def _parse_inline_content(cls, text: str) -> List[Dict[str, Any]]:
        """Phân tích văn bản nội dòng, tách biệt Toán học và các Định dạng Rich Text"""
        tokens = []
        if not text:
            return tokens

        # Bước 1: Trích xuất toán học (LaTeX) ra trước để bảo vệ các ký tự toán học khỏi bộ lọc chữ
        parts = cls._MATH_RE.split(text)
        for part in parts:
            if not part:
                continue

            if (part.startswith('$') and part.endswith('$')) or \
               (part.startswith(r'\(') and part.endswith(r'\)')):
                clean_math = part.strip('$').replace(r'\(', '').replace(r'\)', '').strip()
                tokens.append({"type": "inline_math", "content": clean_math})
            else:
                # Bước 2: Chuyển phần text thường sang bộ lọc định dạng chữ (Bold, Italic,...)
                tokens.extend(cls._parse_rich_text_styles(part))
                
        return tokens

    @classmethod
    def _parse_rich_text_styles(cls, text: str) -> List[Dict[str, str]]:
        """Phân tích văn bản đệ quy để bóc tách các thẻ Bold, Italic, Underline, Strike"""
        # 1. Xử lý Gạch chân <u>
        if match := cls._UNDERLINE_RE.search(text):
            return cls._build_rich_tokens(text, match, "underline")
            
        # 2. Xử lý Chữ đậm ** hoặc __
        if match := cls._BOLD_RE.search(text):
            # Lấy group text không rỗng từ các cặp nhóm điều kiện của Regex
            content = match.group(2) if match.group(2) is not None else match.group(4)
            return cls._build_rich_tokens(text, match, "bold", content)

        # 3. Xử lý Gạch ngang ~~
        if match := cls._STRIKE_RE.search(text):
            return cls._build_rich_tokens(text, match, "strike")

        # 4. Xử lý Chữ nghiêng * hoặc _
        if match := cls._ITALIC_RE.search(text):
            return cls._build_rich_tokens(text, match, "italic")

        # Văn bản thuần túy không chứa thẻ định dạng
        return [{"type": "text", "content": text}]

    @classmethod
    def _build_rich_tokens(cls, text: str, match: re.Match, token_type: str, custom_content: str = None) -> List[Dict[str, str]]:
        """Hàm trợ giúp phân tách chuỗi đệ quy xung quanh vị trí Match được tìm thấy"""
        start_idx, end_idx = match.span()
        inner_content = custom_content if custom_content is not None else match.group(1)

        tokens = []
        # Phân tích phần văn bản phía trước thẻ định dạng
        if start_idx > 0:
            tokens.extend(cls._parse_rich_text_styles(text[:start_idx]))

        # Đưa node định dạng hiện tại vào (chạy đệ quy tiếp bên trong phòng trường hợp định dạng lồng nhau như ***đậm nghiêng***)
        inner_tokens = cls._parse_rich_text_styles(inner_content)
        for token in inner_tokens:
            if token["type"] == "text":
                tokens.append({"type": token_type, "text": token["content"]})
            else:
                # Nếu lồng nhau, giữ nguyên node con nhưng cập nhật hoặc bọc thêm thuộc tính tùy kiến trúc render của bạn
                tokens.append(token)

        # Phân tích phần văn bản phía sau thẻ định dạng
        if end_idx < len(text):
            tokens.extend(cls._parse_rich_text_styles(text[end_idx:]))

        return tokens
