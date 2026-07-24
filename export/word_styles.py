# -*- coding: utf-8 -*-

from __future__ import annotations

import docx

from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class WordLayout:

    TOP = Cm(1.5)
    BOTTOM = Cm(1.5)
    LEFT = Cm(2.0)
    RIGHT = Cm(1.5)

    FONT_NAME = "Times New Roman"
    FONT_SIZE = Pt(13)

    @classmethod
    def apply(cls, doc: docx.Document):

        for section in doc.sections:

            section.top_margin = cls.TOP
            section.bottom_margin = cls.BOTTOM
            section.left_margin = cls.LEFT
            section.right_margin = cls.RIGHT

            # Không chừa gáy
            section.gutter = Cm(0)

            # Khổ A4
            section.page_width = Cm(21.0)
            section.page_height = Cm(29.7)

        cls.configure_styles(doc)

    @classmethod
    def configure_styles(cls, doc):

        style_names = [
            "Normal",
            "Body Text",
            "List Paragraph",
            "List Bullet",
            "List Number",
        ]

        for name in style_names:

            try:

                style = doc.styles[name]

                style.font.name = cls.FONT_NAME
                style.font.size = cls.FONT_SIZE

                style.paragraph_format.alignment = (
                    WD_ALIGN_PARAGRAPH.JUSTIFY
                )

                style.paragraph_format.space_after = Pt(0)
                style.paragraph_format.space_before = Pt(0)

                style.paragraph_format.line_spacing = 1.15

            except KeyError:

                continue

        for level in range(1, 4):

            try:

                style = doc.styles[f"Heading {level}"]

                style.font.name = cls.FONT_NAME

                style.paragraph_format.keep_with_next = True

            except KeyError:

                pass


class XmlHelpers:

    @staticmethod
    def set_font_safely(
        run,
        font_name: str = "Times New Roman"
    ):

        run.font.name = font_name

        rPr = run._element.get_or_add_rPr()

        rFonts = rPr.find(qn("w:rFonts"))

        if rFonts is None:

            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)

        for attr in (
            "ascii",
            "hAnsi",
            "eastAsia",
            "cs"
        ):

            rFonts.set(
                qn(f"w:{attr}"),
                font_name
            )

    @staticmethod
    def apply_paragraph_shading(
        paragraph,
        color_hex: str = "F5F5F5"
    ):

        pPr = paragraph._element.get_or_add_pPr()

        shd = pPr.find(qn("w:shd"))

        if shd is None:

            shd = OxmlElement("w:shd")
            pPr.append(shd)

        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), color_hex)

    @staticmethod
    def apply_bottom_border(
        paragraph,
        color_hex: str = "CCCCCC",
        size: int = 8
    ):

        pPr = paragraph._element.get_or_add_pPr()

        pBdr = pPr.find(qn("w:pBdr"))

        if pBdr is None:

            pBdr = OxmlElement("w:pBdr")
            pPr.append(pBdr)

        old = pBdr.find(qn("w:bottom"))

        if old is not None:

            pBdr.remove(old)

        bottom = OxmlElement("w:bottom")

        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), str(size))
        bottom.set(qn("w:space"), "4")
        bottom.set(qn("w:color"), color_hex)

        pBdr.append(bottom)


class ParagraphFormatter:

    @staticmethod
    def justify(paragraph):

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.JUSTIFY
        )

    @staticmethod
    def center(paragraph):

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

    @staticmethod
    def no_first_line_indent(paragraph):

        paragraph.paragraph_format.first_line_indent = Cm(0)

    @staticmethod
    def first_line_indent(paragraph):

        paragraph.paragraph_format.first_line_indent = Cm(1.0)
