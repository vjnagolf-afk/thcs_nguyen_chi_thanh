# -*- coding: utf-8 -*-

from typing import List, Dict, Any

from docx.shared import Pt, RGBColor

from styles.xml_helpers import XmlHelpers


class TextRenderer:

    @classmethod
    def render_inline_tokens(
        cls,
        paragraph,
        tokens: List[Dict[str, Any]],
        math_renderer
    ):

        if not tokens:
            return

        for token in tokens:

            token_type = token.get(
                "type"
            )

            content = token.get(
                "content",
                ""
            )

            if token_type == "text":

                cls._add_text(
                    paragraph,
                    content
                )

            elif token_type == "bold":

                run = cls._add_text(
                    paragraph,
                    content
                )

                run.bold = True

            elif token_type == "italic":

                run = cls._add_text(
                    paragraph,
                    content
                )

                run.italic = True

            elif token_type == "underline":

                run = cls._add_text(
                    paragraph,
                    content
                )

                run.underline = True

            elif token_type == "strike":

                run = cls._add_text(
                    paragraph,
                    content
                )

                run.font.strike = True

            elif token_type == "highlight":

                run = cls._add_text(
                    paragraph,
                    content
                )

                run.font.highlight_color = 7

            elif token_type == "inline_code":

                run = cls._add_text(
                    paragraph,
                    content,
                    "Courier New"
                )

                run.font.size = Pt(10.5)

            elif token_type == "link":

                run = cls._add_text(
                    paragraph,
                    content
                )

                run.underline = True

                run.font.color.rgb = RGBColor(
                    0,
                    102,
                    204
                )

            elif token_type == "inline_math":

                math_renderer.render_inline_math(
                    paragraph,
                    content
                )

    @staticmethod
    def _add_text(
        paragraph,
        text: str,
        font_name: str = "Times New Roman"
    ):

        run = paragraph.add_run(
            text
        )

        XmlHelpers.set_font_safely(
            run,
            font_name
        )

        return run
