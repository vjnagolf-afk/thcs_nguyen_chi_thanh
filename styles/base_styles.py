# -*- coding: utf-8 -*-

import docx
from docx.shared import Inches, Pt, RGBColor


class BaseStyleSetup:

    @staticmethod
    def setup_base_styles(
        doc: docx.Document
    ):

        # ======================================================
        # KHỔ GIẤY A4
        # ======================================================

        for section in doc.sections:

            section.page_height = Inches(11.69)
            section.page_width = Inches(8.27)

            section.top_margin = Inches(0.79)
            section.bottom_margin = Inches(0.79)

            section.left_margin = Inches(1.18)
            section.right_margin = Inches(0.79)

        # ======================================================
        # STYLE HỆ THỐNG
        # ======================================================

        styles_config = {

            "Normal": (
                13,
                False,
                False,
                0,
                6
            ),

            "Heading 1": (
                16,
                True,
                False,
                12,
                6
            ),

            "Heading 2": (
                14,
                True,
                False,
                8,
                4
            ),

            "Heading 3": (
                13,
                True,
                True,
                6,
                2
            ),

            "List Bullet": (
                13,
                False,
                False,
                0,
                3
            ),

            "List Number": (
                13,
                False,
                False,
                0,
                3
            )
        }

        for (
            name,
            (
                size,
                bold,
                italic,
                before,
                after
            )
        ) in styles_config.items():

            style = doc.styles[name]

            style.font.name = "Times New Roman"
            style.font.size = Pt(size)
            style.font.bold = bold
            style.font.italic = italic
            style.font.color.rgb = RGBColor(
                0,
                0,
                0
            )

            style.paragraph_format.space_before = Pt(before)
            style.paragraph_format.space_after = Pt(after)

            if "Heading" in name:

                style.paragraph_format.keep_with_next = True
