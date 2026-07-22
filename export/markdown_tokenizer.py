# -*- coding: utf-8 -*-
"""
Module: export/markdown_tokenizer.py
Nhiệm vụ:
- Phân tích Markdown thành AST đơn giản.
- Hỗ trợ heading, paragraph, list, checkbox, table,
  code block, blockquote, image, math và rich text.
"""

import re
from typing import List, Dict, Any


class MarkdownTokenizer:

    _HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)')
    _IMAGE_RE = re.compile(r'^!\[(.*?)\]\((.*?)\)')
    _BULLET_RE = re.compile(r'^(\s*)([\*\-])\s+(.*)')
    _NUMBER_RE = re.compile(r'^(\s*)(\d+\.)\s+(.*)')
    _CHECKBOX_RE = re.compile(
        r'^(\s*)([\*\-])\s+\[([ xX])\]\s+(.*)'
    )
    _HR_RE = re.compile(r'^\s*([-*_])\1{2,}\s*$')
    _CODE_BLOCK_START_RE = re.compile(r'^```(\w*)')
    _BLOCKQUOTE_RE = re.compile(r'^\s*>\s*(.*)')

    _MATH_RE = re.compile(
        r'(\$(?:\\[\s\S]|[^\$])+\$|\\\([\s\S]+?\\\))'
    )

    _LINK_RE = re.compile(
        r'\[([^\]]+)\]\(([^)]+)\)'
    )

    _INLINE_CODE_RE = re.compile(
        r'`([^`]+)`'
    )

    _BOLD_RE = re.compile(
        r'(\*\*\*|___)(.*?)\1|(\*\*|__)(.*?)\3'
    )

    _ITALIC_RE = re.compile(
        r'(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)'
    )

    _UNDERLINE_RE = re.compile(
        r'<u>(.*?)</u>',
        re.IGNORECASE
    )

    _STRIKE_RE = re.compile(
        r'~~(.*?)~~'
    )

    _HIGHLIGHT_RE = re.compile(
        r'==(.*?)=='
    )

    @classmethod
    def parse(cls, markdown_text: str) -> List[Dict[str, Any]]:

        if not markdown_text:
            return []

        forbidden_prefixes = (
            "Chào bạn",
            "Với vai trò",
            "Tôi là",
            "Lưu ý về"
        )

        ast_nodes = []

        table_buf = []
        code_buf = []
        blockquote_buf = []

        in_code = False
        in_blockquote = False
        code_lang = ""

        def flush_table():
            if table_buf:
                ast_nodes.append(
                    cls._parse_table(table_buf)
                )
                table_buf.clear()

        def flush_blockquote():
            nonlocal in_blockquote

            if blockquote_buf:
                children = cls.parse(
                    "\n".join(blockquote_buf)
                )

                ast_nodes.append({
                    "type": "callout",
                    "style": "quote",
                    "children": children
                })

                blockquote_buf.clear()

            in_blockquote = False

        for raw_line in markdown_text.splitlines():

            if any(
                raw_line.lstrip().startswith(prefix)
                for prefix in forbidden_prefixes
            ):
                continue

            # ==================================================
            # CODE BLOCK
            # ==================================================
            if in_code:

                if raw_line.strip() == "```":

                    in_code = False

                    ast_nodes.append({
                        "type": "code",
                        "language": code_lang,
                        "text": "\n".join(code_buf)
                    })

                    code_buf.clear()

                else:
                    code_buf.append(raw_line)

                continue

            stripped = raw_line.strip()

            # ==================================================
            # BẮT ĐẦU CODE BLOCK
            # ==================================================
            code_match = cls._CODE_BLOCK_START_RE.match(stripped)

            if code_match:

                flush_table()
                flush_blockquote()

                in_code = True
                code_lang = (
                    code_match.group(1).lower()
                    or "text"
                )

                continue

            # ==================================================
            # BLOCKQUOTE
            # ==================================================
            quote_match = cls._BLOCKQUOTE_RE.match(raw_line)

            if quote_match:

                flush_table()

                in_blockquote = True
                blockquote_buf.append(
                    quote_match.group(1)
                )

                continue

            if in_blockquote:

                if stripped:
                    blockquote_buf.append(raw_line)
                    continue

                flush_blockquote()

            # ==================================================
            # DÒNG TRỐNG
            # ==================================================
            if not stripped:

                flush_table()
                continue

            # ==================================================
            # TABLE
            # ==================================================
            if stripped.startswith("|"):

                table_buf.append(stripped)
                continue

            flush_table()

            # ==================================================
            # HORIZONTAL RULE
            # ==================================================
            if cls._HR_RE.match(stripped):

                ast_nodes.append({
                    "type": "hr"
                })

            # ==================================================
            # HEADING
            # ==================================================
            elif match := cls._HEADING_RE.match(stripped):

                ast_nodes.append({
                    "type": "heading",
                    "level": len(match.group(1)),
                    "tokens": cls._parse_inline_content(
                        match.group(2)
                    )
                })

            # ==================================================
            # IMAGE
            # ==================================================
            elif match := cls._IMAGE_RE.match(stripped):

                ast_nodes.append({
                    "type": "image",
                    "alt": match.group(1),
                    "url": match.group(2)
                })

            # ==================================================
            # CHECKBOX
            # ==================================================
            elif match := cls._CHECKBOX_RE.match(raw_line):

                ast_nodes.append({
                    "type": "checkbox",
                    "checked": (
                        match.group(3).lower() == "x"
                    ),
                    "level": (
                        len(match.group(1)) // 2
                    ) + 1,
                    "tokens": cls._parse_inline_content(
                        match.group(4)
                    )
                })

            # ==================================================
            # BULLET
            # ==================================================
            elif match := cls._BULLET_RE.match(raw_line):

                ast_nodes.append({
                    "type": "list_item",
                    "style": "bullet",
                    "level": (
                        len(match.group(1)) // 2
                    ) + 1,
                    "tokens": cls._parse_inline_content(
                        match.group(3)
                    )
                })

            # ==================================================
            # NUMBER
            # ==================================================
            elif match := cls._NUMBER_RE.match(raw_line):

                ast_nodes.append({
                    "type": "list_item",
                    "style": "number",
                    "level": (
                        len(match.group(1)) // 2
                    ) + 1,
                    "tokens": cls._parse_inline_content(
                        match.group(3)
                    )
                })

            # ==================================================
            # PARAGRAPH
            # ==================================================
            else:

                ast_nodes.append({
                    "type": "paragraph",
                    "tokens": cls._parse_inline_content(
                        stripped
                    )
                })

        flush_table()
        flush_blockquote()

        return ast_nodes

    # ==========================================================
    # TABLE
    # ==========================================================

    @classmethod
    def _parse_table(
        cls,
        lines: List[str]
    ) -> Dict[str, Any]:

        rows = []
        headers = []

        for line in lines:

            cells = [
                cell.strip()
                for cell in line.split("|")
            ]

            if cells and not cells[0]:
                cells.pop(0)

            if cells and not cells[-1]:
                cells.pop()

            if not cells:
                continue

            # Bỏ dòng phân cách Markdown:
            # |---|---|
            if all(
                re.fullmatch(
                    r':?-{3,}:?',
                    cell.replace(" ", "")
                )
                for cell in cells
            ):
                continue

            parsed_cells = [
                {
                    "content": cls._parse_inline_content(
                        cell
                    )
                }
                for cell in cells
            ]

            if not headers:
                headers = parsed_cells
            else:
                rows.append(parsed_cells)

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
            "cols": len(headers)
        }

    # ==========================================================
    # INLINE CONTENT
    # ==========================================================

    @classmethod
    def _parse_inline_content(
        cls,
        text: str
    ) -> List[Dict[str, Any]]:

        if not text:
            return []

        tokens = []

        parts = cls._MATH_RE.split(text)

        for part in parts:

            if not part:
                continue

            if (
                part.startswith("$")
                and part.endswith("$")
            ):

                tokens.append({
                    "type": "inline_math",
                    "content": part[1:-1].strip()
                })

            elif (
                part.startswith(r"\(")
                and part.endswith(r"\)")
            ):

                tokens.append({
                    "type": "inline_math",
                    "content": part[2:-2].strip()
                })

            else:

                tokens.extend(
                    cls._parse_rich_text_styles(part)
                )

        return tokens

    # ==========================================================
    # RICH TEXT
    # ==========================================================

    @classmethod
    def _parse_rich_text_styles(
        cls,
        text: str
    ) -> List[Dict[str, Any]]:

        if not text:
            return []

        # Link
        match = cls._LINK_RE.search(text)

        if match:

            return cls._build_node(
                text,
                match,
                "link",
                match.group(1),
                url=match.group(2)
            )

        # Inline code
        match = cls._INLINE_CODE_RE.search(text)

        if match:

            return cls._build_node(
                text,
                match,
                "inline_code",
                match.group(1)
            )

        # Highlight
        match = cls._HIGHLIGHT_RE.search(text)

        if match:

            return cls._build_node(
                text,
                match,
                "highlight",
                match.group(1)
            )

        # Underline
        match = cls._UNDERLINE_RE.search(text)

        if match:

            return cls._build_node(
                text,
                match,
                "underline",
                match.group(1)
            )

        # Bold
        match = cls._BOLD_RE.search(text)

        if match:

            inner = (
                match.group(2)
                or match.group(4)
            )

            return cls._build_node(
                text,
                match,
                "bold",
                inner
            )

        # Strike
        match = cls._STRIKE_RE.search(text)

        if match:

            return cls._build_node(
                text,
                match,
                "strike",
                match.group(1)
            )

        # Italic
        match = cls._ITALIC_RE.search(text)

        if match:

            inner = (
                match.group(1)
                or match.group(2)
            )

            return cls._build_node(
                text,
                match,
                "italic",
                inner
            )

        return [
            {
                "type": "text",
                "content": text
            }
        ]

    @classmethod
    def _build_node(
        cls,
        text: str,
        match: re.Match,
        token_type: str,
        inner: str,
        **extra
    ) -> List[Dict[str, Any]]:

        start, end = match.span()

        tokens = []

        if start > 0:

            tokens.extend(
                cls._parse_rich_text_styles(
                    text[:start]
                )
            )

        node = {
            "type": token_type,
            "content": inner
        }

        node.update(extra)

        tokens.append(node)

        if end < len(text):

            tokens.extend(
                cls._parse_rich_text_styles(
                    text[end:]
                )
            )

        return tokens
