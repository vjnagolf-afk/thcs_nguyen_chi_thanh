import re
from typing import List, Dict, Any

class MarkdownTokenizer:
    # Biên dịch trước các Regex để tối ưu hóa hiệu năng
    _HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)')
    _IMAGE_RE = re.compile(r'^!\[(.*?)\]\((.*?)\)')
    _BULLET_RE = re.compile(r'^([\*\-])\s+(.*)')
    _NUMBER_RE = re.compile(r'^(\d+\.)\s+(.*)')
    _MATH_RE = re.compile(r'(\$.*?\$|\\\([^()]*\\\))')

    @classmethod
    def parse(cls, markdown_text: str) -> List[Dict[str, Any]]:
        # 1. BỘ LỌC RÁC TOÀN CỤC (Làm sạch trước khi xử lý)
        forbidden_prefixes = ("Chào bạn", "Với vai trò", "Tôi là", "Lưu ý về")
        lines = [
            line for line in markdown_text.splitlines() 
            if not line.lstrip().startswith(forbidden_prefixes)
        ]
        
        ast_nodes = []
        table_buffer = []

        # Hàm helper để xuất bảng khi kết thúc khối dữ liệu
        def flush_table():
            if table_buffer:
                ast_nodes.append(cls._parse_table(table_buffer))
                table_buffer.clear()

        # 2. XỬ LÝ DÒNG VÀ GOM NHÓM BẢNG
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                flush_table()
                continue

            # Kiểm tra dòng bắt đầu bằng | để nhận diện hàng của bảng
            if line.startswith('|'):
                table_buffer.append(line)
                continue
            
            # Nếu dòng không phải bảng mà đang có buffer -> xuất bảng ngay
            flush_table()

            # 3. CÁC ĐỊNH DẠNG KHÁC (Heading, List, Image)
            if match := cls._HEADING_RE.match(line):
                ast_nodes.append({
                    "type": "heading", 
                    "level": len(match.group(1)), 
                    "tokens": cls._parse_inline_content(match.group(2))
                })
            elif match := cls._IMAGE_RE.match(line):
                ast_nodes.append({
                    "type": "image", 
                    "alt": match.group(1), 
                    "url": match.group(2)
                })
            elif match := cls._BULLET_RE.match(line):
                ast_nodes.append({
                    "type": "list_item", 
                    "style": "bullet", 
                    "tokens": cls._parse_inline_content(match.group(2))
                })
            elif match := cls._NUMBER_RE.match(line):
                ast_nodes.append({
                    "type": "list_item", 
                    "style": "number", 
                    "tokens": cls._parse_inline_content(match.group(2))
                })
            else:
                ast_nodes.append({
                    "type": "paragraph", 
                    "tokens": cls._parse_inline_content(line)
                })

        # Kết thúc vòng lặp, kiểm tra nếu còn sót bảng
        flush_table()
        return ast_nodes

    @staticmethod
    def _parse_table(lines: List[str]) -> Dict[str, Any]:
        """Chuyển đổi các dòng thành cấu trúc bảng chuẩn, hỗ trợ toán học trong bảng"""
        rows = []
        headers = []
        
        for line in lines:
            # Tách cột, loại bỏ ký tự | thừa
            cells = [c.strip() for c in line.split('|') if c.strip() or '---' in c]
            if not cells: continue
            
            # Bỏ qua dòng phân cách Markdown (---)
            if any('---' in c for c in cells):
                continue
            
            # Gọi _parse_inline_content cho mỗi ô để toán (LaTeX) được xử lý đúng
            processed_cells = [{"content": MarkdownTokenizer._parse_inline_content(c)} for c in cells]
            
            if not headers:
                headers = processed_cells
            else:
                rows.append(processed_cells)
                
        return {
            "type": "table", 
            "headers": headers, 
            "rows": rows, 
            "cols": len(headers)
        }

    @classmethod
    def _parse_inline_content(cls, text: str) -> List[Dict[str, str]]:
        tokens = []
        if not text: return tokens
        
        # Tách text và math bằng Regex pre-compiled
        parts = cls._MATH_RE.split(text)

        for part in parts:
            if not part: continue
            
            # Kiểm tra toán học
            if (part.startswith('$') and part.endswith('$')) or \
               (part.startswith(r'\(') and part.endswith(r'\)')):
                
                clean_math = part.strip('$').replace(r'\(', '').replace(r'\)', '')
                tokens.append({"type": "inline_math", "content": clean_math})
            else:
                tokens.append({"type": "text", "content": part})
        return tokens
