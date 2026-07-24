# -*- coding: utf-8 -*-

from __future__ import annotations

import io
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from .template_loader import TemplateLoader
from .word_styles import (
    WordLayout,
    XmlHelpers
)
from .word_math import (
    ScienceNormalizer,
    MathRenderer
)
from .word_images import ImageRenderer
from .word_tables import (
    MarkdownTableParser,
    WordTableRenderer
)


class InlineTextRenderer:

    @staticmethod
    def tokenize_inline(text):

        pattern = re.compile(
            r"(\*\*.*?\*\*|"
            r"\*.*?\*|"
            r"`.*?`|"
            r"\$.*?\$|"
            r"\\\(.*?\\\))"
        )

        return pattern.split(text)

    @classmethod
    def render_inline_tokens(
        cls,
        paragraph,
        tokens,
        math_renderer
    ):

        for token in tokens:

            if not token:

                continue

            # Bold
            if (
                token.startswith("**")
                and token.endswith("**")
            ):

                run = paragraph.add_run(
                    token[2:-2]
                )

                run.bold = True

                XmlHelpers.set_font_safely(
                    run
                )

                continue

            # Italic
            if (
                token.startswith("*")
                and token.endswith("*")
            ):

                run = paragraph.add_run(
                    token[1:-1]
                )

                run.italic = True

                XmlHelpers.set_font_safely(
                    run
                )

                continue

            # Inline code
            if (
                token.startswith("`")
                and token.endswith("`")
            ):

                run = paragraph.add_run(
                    token[1:-1]
                )

                XmlHelpers.set_font_safely(
                    run,
                    "Courier New"
                )

                continue

            # Math
            if (
                token.startswith("$")
                and token.endswith("$")
            ):

                MathRenderer.render_inline_math(
                    paragraph,
                    token[1:-1]
                )

                continue

            if (
                token.startswith(r"\(")
                and token.endswith(r"\)")
            ):

                MathRenderer.render_inline_math(
                    paragraph,
                    token[2:-2]
                )

                continue

            # Text
            run = paragraph.add_run(
                token
            )

            XmlHelpers.set_font_safely(
                run
            )


class WordExportEngine:

    @classmethod
    def convert_markdown_to_docx_bytes(
        cls,
        markdown_text,
        template_path=None
    ):

        if not markdown_text:

            markdown_text = ""

        # QUAN TRỌNG:
        # Dùng template làm nền
        doc = TemplateLoader.load(
            template_path
        )

        # Chỉ áp dụng layout chuẩn khi cần.
        # Không phá style gốc của template.
        cls._apply_page_layout(
            doc
        )

        lines = markdown_text.splitlines()

        index = 0

        while index < len(lines):

            raw_line = lines[index]

            line = raw_line.strip()

            # Bỏ dòng rỗng dư thừa
            if not line:

                index += 1

                continue

            # Markdown table
            if cls._is_table_start(
                lines,
                index
            ):

                table_lines = []

                while (
                    index < len(lines)
                    and lines[index].strip().startswith("|")
                ):

                    table_lines.append(
                        lines[index]
                    )

                    index += 1

                rows = MarkdownTableParser.parse(
                    table_lines
                )

                WordTableRenderer.render(
                    doc,
                    rows,
                    InlineTextRenderer,
                    MathRenderer
                )

                continue

            # Heading
            heading_match = re.match(
                r"^(#{1,6})\s+(.*)$",
                line
            )

            if heading_match:

                level = min(
                    len(heading_match.group(1)),
                    3
                )

                text = heading_match.group(2)

                p = doc.add_paragraph(
                    style=f"Heading {level}"
                )

                if level == 1:

                    p.alignment = (
                        WD_ALIGN_PARAGRAPH.CENTER
                    )

                else:

                    p.alignment = (
                        WD_ALIGN_PARAGRAPH.LEFT
                    )

                InlineTextRenderer.render_inline_tokens(
                    p,
                    InlineTextRenderer.tokenize_inline(
                        text
                    ),
                    MathRenderer
                )

                index += 1

                continue

            # Horizontal rule
            if re.match(
                r"^([-*_])\s*\1\s*\1+",
                line
            ):

                p = doc.add_paragraph()

                XmlHelpers.apply_bottom_border(
                    p
                )

                index += 1

                continue

            # Image
            image_match = re.match(
                r"^!\[([^\]]*)\]\(([^)]+)\)$",
                line
            )

            if image_match:

                alt = image_match.group(1)

                url = image_match.group(2)

                ImageRenderer.render_image(
                    doc,
                    {
                        "alt": alt,
                        "url": url
                    }
                )

                index += 1

                continue

            # Mermaid
            if line == "```mermaid":

                index += 1

                mermaid_lines = []

                while (
                    index < len(lines)
                    and lines[index].strip() != "```"
                ):

                    mermaid_lines.append(
                        lines[index]
                    )

                    index += 1

                ImageRenderer.render_mermaid(
                    doc,
                    "\n".join(mermaid_lines)
                )

                index += 1

                continue

            # Code block
            if line.startswith("```"):

                index += 1

                code_lines = []

                while (
                    index < len(lines)
                    and lines[index].strip() != "```"
                ):

                    code_lines.append(
                        lines[index]
                    )

                    index += 1

                p = doc.add_paragraph()

                XmlHelpers.apply_paragraph_shading(
                    p
                )

                run = p.add_run(
                    "\n".join(code_lines)
                )

                XmlHelpers.set_font_safely(
                    run,
                    "Courier New"
                )

                run.font.size = Pt(10)

                index += 1

                continue

            # Bullet
            bullet_match = re.match(
                r"^[-*+]\s+(.*)$",
                line
            )

            if bullet_match:

                p = doc.add_paragraph(
                    style="List Bullet"
                )

                p.alignment = (
                    WD_ALIGN_PARAGRAPH.JUSTIFY
                )

                InlineTextRenderer.render_inline_tokens(
                    p,
                    InlineTextRenderer.tokenize_inline(
                        bullet_match.group(1)
                    ),
                    MathRenderer
                )

                index += 1

                continue

            # Number list
            number_match = re.match(
                r"^\d+[.)]\s+(.*)$",
                line
            )

            if number_match:

                p = doc.add_paragraph(
                    style="List Number"
                )

                p.alignment = (
                    WD_ALIGN_PARAGRAPH.JUSTIFY
                )

                InlineTextRenderer.render_inline_tokens(
                    p,
                    InlineTextRenderer.tokenize_inline(
                        number_match.group(1)
                    ),
                    MathRenderer
                )

                index += 1

                continue

            # Paragraph
            p = doc.add_paragraph()

            p.alignment = (
                WD_ALIGN_PARAGRAPH.JUSTIFY
            )

            # Không thụt đầu dòng tùy tiện.
            # Template quyết định định dạng chính.
            p.paragraph_format.first_line_indent = Cm(0)

            InlineTextRenderer.render_inline_tokens(
                p,
                InlineTextRenderer.tokenize_inline(
                    line
                ),
                MathRenderer
            )

            index += 1

        output = io.BytesIO()

        doc.save(output)

        output.seek(0)

        return output.getvalue()

    @staticmethod
    def _is_table_start(
        lines,
        index
    ):

        if index + 1 >= len(lines):

            return False

        first = lines[index].strip()

        second = lines[index + 1].strip()

        return (
            first.startswith("|")
            and second.startswith("|")
            and "-" in second
        )

    @staticmethod
    def _apply_page_layout(doc):

        for section in doc.sections:

            section.top_margin = Cm(1.5)
            section.bottom_margin = Cm(1.5)
            section.left_margin = Cm(2.0)
            section.right_margin = Cm(1.5)

            section.gutter = Cm(0)
