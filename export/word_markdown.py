import re
class MarkdownTokenizer:
    _HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)')

    @classmethod
    def parse(cls, markdown_text: str) -> list:
        ast_nodes = []
        for raw_line in markdown_text.splitlines():
            # XỬ LÝ: Xóa ký tự > và khoảng trắng ở đầu dòng
            line = re.sub(r'^\s*>\s*', '', raw_line).strip()
            if not line: continue
            
            if match := cls._HEADING_RE.match(line):
                ast_nodes.append({"type": "heading", "level": len(match.group(1)), "tokens": [{"type":"text", "content": match.group(2)}]})
            else:
                ast_nodes.append({"type": "paragraph", "tokens": [{"type":"text", "content": line}]})
        return ast_nodes
