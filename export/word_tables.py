# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import List

from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from .word_styles import (
    WordLayout,
    XmlHelpers
)


class MarkdownTableParser:

    @staticmethod
    def parse(lines: List[str]):

        rows = []

        for line in lines:

            line = line.strip()

            if not line.startswith("|"):
                continue

            cells = [
                cell.strip()
                for cell in line.strip("|").split("|")
            ]

            # Bỏ dòng phân cách Markdown
            if all(
                set(cell.replace(":", "").strip()) <= {"-"}
                for cell in cells
            ):
                continue

            rows.append(cells)

        return rows


class WordTableRenderer:

    @classmethod
    def render(
        cls,
        doc,
        rows,
        text_renderer=None,
        math_renderer=None
    ):

        if not rows:

            return None

        column_count = max(
            len(row)
            for row in rows
        )

        table = doc.add_table(
            rows=len(rows),
            cols=column_count
        )

        table.alignment = (
            WD_TABLE_ALIGNMENT.CENTER
        )

        table.autofit = True

        # Lặp qua từng ô
        for row_index, row_data in enumerate(rows):

            row = table.rows[row_index]

            for col_index in range(column_count):

                cell = row.cells[col_index]

                text = (
                    row_data[col_index]
                    if col_index < len(row_data)
                    else ""
                )

                paragraph = cell.paragraphs[0]

                paragraph.alignment = (
                    WD_ALIGN_PARAGRAPH.JUSTIFY
                )

                paragraph.paragraph_format.space_after = Pt(0)

                if text_renderer:

                    text_renderer.render_inline_tokens(
                        paragraph,
                        text_renderer.tokenize_inline(text),
                        math_renderer
                    )

                else:

                    run = paragraph.add_run(text)

                    XmlHelpers.set_font_safely(
                        run,
                        WordLayout.FONT_NAME
                    )

                    run.font.size = WordLayout.FONT_SIZE

                # Header
                if row_index == 0:

                    for run in paragraph.runs:

                        run.bold = True

        # Độ rộng tương đối
        if column_count == 2:

            widths = [
                Cm(8.0),
                Cm(8.0)
            ]

        else:

            width = 16.0 / column_count

            widths = [
                Cm(width)
                for _ in range(column_count)
            ]

        for row in table.rows:

            for index, cell in enumerate(row.cells):

                if index < len(widths):

                    cell.width = widths[index]

        doc.add_paragraph()

        return table
