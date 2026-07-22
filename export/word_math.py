# -*- coding: utf-8 -*-

import re
from typing import Tuple

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls


class ScienceNormalizer:

    SUB = str.maketrans(
        "0123456789",
        "₀₁₂₃₄₅₆₇₈₉"
    )

    SUP = str.maketrans(
        "0123456789+-",
        "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"
    )

    TRANSLATION_MAP = {

        r"\perp": "⊥",
        r"\circ": "°",
        r"\ne": "≠",
        r"\le": "≤",
        r"\ge": "≥",

        r"\times": "×",
        r"\div": "÷",
        r"\pm": "±",

        r"\in": "∈",
        r"\notin": "∉",

        r"\infty": "∞",

        r"\triangle": "△",
        r"\angle": "∠",

        r"\rightarrow": "→",
        r"\Rightarrow": "⇒",
        r"\Leftrightarrow": "⇔",

        r"\approx": "≈",
        r"\cong": "≅",
        r"\sim": "~",
        r"\propto": "∝",

        r"\forall": "∀",
        r"\exists": "∃",

        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\lambda": "λ",
        r"\mu": "μ",
        r"\omega": "ω",
        r"\pi": "π",
        r"\theta": "θ",
        r"\sigma": "σ",

        r"\sum": "∑",
        r"\int": "∫",

        r"\text{cm}": "cm",
        r"\text{mm}": "mm",
        r"\text{dm}": "dm",
        r"\text{m}": "m",
        r"\text{kg}": "kg"
    }

    @classmethod
    def _parse_nested_braces(
        cls,
        text: str,
        start_pos: int
    ) -> Tuple[str, int]:

        stack = []
        content = []

        for index in range(
            start_pos,
            len(text)
        ):

            char = text[index]

            if char == "{":

                stack.append("{")

                if len(stack) > 1:
                    content.append(char)

            elif char == "}":

                if stack:

                    stack.pop()

                    if not stack:

                        return (
                            "".join(content),
                            index
                        )

                    content.append(char)

            else:

                content.append(char)

        return (
            "".join(content),
            len(text)
        )

    @classmethod
    def convert_frac_recursive(
        cls,
        text: str
    ) -> str:

        while r"\frac{" in text:

            start = text.find(
                r"\frac{"
            )

            numerator, end_num = cls._parse_nested_braces(
                text,
                start + 5
            )

            if (
                end_num + 1 < len(text)
                and text[end_num + 1] == "{"
            ):

                denominator, end_den = cls._parse_nested_braces(
                    text,
                    end_num + 1
                )

                numerator = cls.convert_frac_recursive(
                    numerator
                )

                denominator = cls.convert_frac_recursive(
                    denominator
                )

                old = text[
                    start:end_den + 1
                ]

                new = (
                    f"(({numerator})/"
                    f"({denominator}))"
                )

                text = text.replace(
                    old,
                    new,
                    1
                )

            else:

                break

        return text

    @classmethod
    def normalize_chemistry(
        cls,
        text: str
    ) -> str:

        # CuSO4.5H2O → CuSO₄•5H₂O
        text = re.sub(
            r"([A-Za-z0-9\]\)])"
            r"\s*\.\s*"
            r"(\d*[A-Z][a-z]?)",
            r"\1•\2",
            text
        )

        # Ca(OH)2 → Ca(OH)₂
        text = re.sub(
            r"([A-Z][a-z]?|\))(\d+)",
            lambda m:
                m.group(1)
                + m.group(2).translate(cls.SUB),
            text
        )

        # Fe^3+ → Fe³⁺
        text = re.sub(
            r"([A-Za-z₀₁₂₃₄₅₆₇₈₉\)]+)"
            r"\^(\d*[+\-])",
            lambda m:
                m.group(1)
                + m.group(2).translate(cls.SUP),
            text
        )

        return text

    @classmethod
    def normalize(
        cls,
        text: str
    ) -> str:

        if not text:
            return ""

        text = (
            text
            .replace("$", "")
            .replace(r"\(", "")
            .replace(r"\)", "")
            .strip()
        )

        text = cls.convert_frac_recursive(
            text
        )

        text = re.sub(
            r"\\sqrt\{([\s\S]+?)\}",
            r"√(\1)",
            text
        )

        text = re.sub(
            r"\\widehat\{([A-Za-z]+)\}",
            lambda m:
                f"∠{m.group(1)}"
                if len(m.group(1)) > 1
                else f"{m.group(1)}̂",
            text
        )

        text = cls.normalize_chemistry(
            text
        )

        for latex, symbol in cls.TRANSLATION_MAP.items():

            text = text.replace(
                latex,
                symbol
            )

        text = re.sub(
            r"\\text\{([\s\S]+?)\}",
            r"\1",
            text
        )

        text = re.sub(
            r"\\mathrm\{([\s\S]+?)\}",
            r"\1",
            text
        )

        return text


class MathRenderer:

    @staticmethod
    def _set_font_safely(
        run,
        font_name: str = "Times New Roman"
    ):

        run.font.name = font_name

        rPr = run._element.get_or_add_rPr()

        rFonts = rPr.find(
            qn("w:rFonts")
        )

        if rFonts is None:

            rFonts = OxmlElement(
                "w:rFonts"
            )

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

    @classmethod
    def render_inline_math(
        cls,
        paragraph,
        latex_str: str
    ):

        clean_text = ScienceNormalizer.normalize(
            latex_str
        )

        run = paragraph.add_run(
            clean_text
        )

        cls._set_font_safely(
            run,
            "Times New Roman"
        )

        run.font.italic = True

    @classmethod
    def render_display_math(
        cls,
        doc,
        latex_str: str
    ):

        p = doc.add_paragraph()

        p.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        clean_text = ScienceNormalizer.normalize(
            latex_str
        )

        run = p.add_run(
            clean_text
        )

        cls._set_font_safely(
            run,
            "Times New Roman"
        )

        run.font.size = Pt(13)
        run.font.italic = True

        return p
