# -*- coding: utf-8 -*-

import io

import docx

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from export.markdown_tokenizer import (
    MarkdownTokenizer
)

from export.word_math import (
    MathRenderer
)

from export.word_images import (
    ImageRenderer
)

from styles.base_styles import (
    BaseStyleSetup
)

from styles.xml_helpers import (
    XmlHelpers
)

from renderers.text_renderer import (
    TextRenderer
)

from renderers.block_renderer import (
    BlockRenderer
)

from renderers.container_renderer import (
    ContainerRenderer
)


class WordExportEngine:

    @classmethod
    def convert_markdown_to_docx_bytes(
        cls,
        markdown_text: str
    ) -> bytes:

        ast_nodes = MarkdownTokenizer.parse(
            markdown_text
        )

        doc = docx.Document()

        BaseStyleSetup.setup_base_styles(
            doc
        )

        for node in ast_nodes:

            node_type = node.get(
                "type"
            )

            # Paragraph
            if node_type == "paragraph":

                paragraph = doc.add_paragraph()

                TextRenderer.render_inline_tokens(
                    paragraph,
                    node.get(
                        "tokens",
                        []
                    ),
                    MathRenderer
                )

            # Heading
            elif node_type == "heading":

                BlockRenderer.render_heading(
                    doc,
                    node,
                    TextRenderer,
                    MathRenderer
                )

            # List
            elif node_type == "list_item":

                BlockRenderer.render_list_item(
                    doc,
                    node,
                    TextRenderer,
                    MathRenderer
                )

            # Checkbox
            elif node_type == "checkbox":

                BlockRenderer.render_checkbox(
                    doc,
                    node,
                    TextRenderer,
                    MathRenderer
                )

            # Code
            elif node_type == "code":

                ContainerRenderer.render_code_block(
                    doc,
                    node
                )

            # Callout
            elif node_type == "callout":

                ContainerRenderer.render_callout(
                    doc,
                    node,
                    TextRenderer,
                    MathRenderer
                )

            # Image
            elif node_type == "image":

                ImageRenderer.render_image(
                    doc,
                    node
                )

            # Horizontal Rule
            elif node_type == "hr":

                paragraph = doc.add_paragraph()

                XmlHelpers.apply_bottom_border(
                    paragraph
                )

            # Page Break
            elif node_type == "page_break":

                doc.add_page_break()

            # Table
            elif node_type == "table":

                cls._render_table(
                    doc,
                    node
                )

        output = io.BytesIO()

        doc.save(
            output
        )

        return output.getvalue()

    @classmethod
    def _render_table(
        cls,
        doc,
        node
    ):

        headers = node.get(
            "headers",
            []
        )

        rows = node.get(
            "rows",
            []
        )

        cols = max(
            node.get(
                "cols",
                1
            ),
            1
        )

        total_rows = (
            len(rows)
            + (
                1
                if headers
                else 0
            )
        )

        table = doc.add_table(
            rows=total_rows,
            cols=cols
        )

        table.style = (
            "Table Grid"
        )

        table.autofit = True

        row_index = 0

        # Header
        if headers:

            header_row = table.rows[
                row_index
            ]

            trPr = (
                header_row
                ._element
                .get_or_add_trPr()
            )

            tbl_header = OxmlElement(
                "w:tblHeader"
            )

            tbl_header.set(
                qn(
                    "w:val"
                ),
                "true"
            )

            trPr.append(
                tbl_header
            )

            for col_index, cell_data in enumerate(
                headers
            ):

                if col_index >= cols:

                    break

                cell = (
                    header_row
                    .cells[col_index]
                )

                XmlHelpers.set_cell_shading(
                    cell,
                    "EAEAEA"
                )

                paragraph = (
                    cell
                    .paragraphs[0]
                )

                TextRenderer.render_inline_tokens(
                    paragraph,
                    cell_data.get(
                        "content",
                        []
                    ),
                    MathRenderer
                )

                for run in paragraph.runs:

                    run.bold = True

            row_index += 1

        # Body
        for data_index, row_data in enumerate(
            rows
        ):

            if row_index >= len(
                table.rows
            ):

                break

            row = table.rows[
                row_index
            ]

            trPr = (
                row
                ._element
                .get_or_add_trPr()
            )

            cant_split = OxmlElement(
                "w:cantSplit"
            )

            trPr.append(
                cant_split
            )

            if data_index % 2:

                bg_color = "F9F9F9"

            else:

                bg_color = "FFFFFF"

            for col_index, cell_data in enumerate(
                row_data
            ):

                if col_index >= cols:

                    break

                cell = (
                    row
                    .cells[col_index]
                )

                XmlHelpers.set_cell_shading(
                    cell,
                    bg_color
                )

                TextRenderer.render_inline_tokens(
                    cell.paragraphs[0],
                    cell_data.get(
                        "content",
                        []
                    ),
                    MathRenderer
                )

            row_index += 1
