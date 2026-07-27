# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_math.py
============================================================

Mục tiêu:
- Chuẩn hóa công thức Toán học.
- Chuẩn hóa công thức Vật lý.
- Chuẩn hóa công thức Hóa học.
- Không làm mất nội dung LaTeX khi xuất Word.
- Xử lý phân số, căn, số mũ, chỉ số dưới, ký hiệu Hy Lạp,
  vectơ, góc, đạo hàm, tích phân, đơn vị đo...
- Hỗ trợ công thức inline và công thức display.

Lưu ý kiến trúc:
- Module này KHÔNG dùng MathML/OMML vì python-docx không hỗ trợ
  trực tiếp việc tạo công thức Word native một cách ổn định.
- Công thức được chuyển thành Unicode + superscript/subscript
  để Word hiển thị ổn định, không bị mất nội dung.
- Không được xóa toàn bộ ký hiệu '$' trước khi tokenizer xử lý.
============================================================
"""

from __future__ import annotations

import re
from typing import Tuple, Optional

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# ============================================================
# 1. NORMALIZER
# ============================================================

class ScienceNormalizer:
    """
    Bộ chuẩn hóa công thức khoa học.

    Phạm vi:
    - Toán học
    - Vật lý
    - Hóa học
    """

    SUB_TRANSLATION = str.maketrans(
        "0123456789+-=()",
        "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎"
    )

    SUP_TRANSLATION = str.maketrans(
        "0123456789+-=()",
        "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
    )

    # ========================================================
    # KÝ HIỆU LATEX → UNICODE
    # ========================================================

    TRANSLATION_MAP = {

        # Toán tử
        r"\times": "×",
        r"\cdot": "·",
        r"\div": "÷",
        r"\pm": "±",
        r"\mp": "∓",

        # Quan hệ
        r"\neq": "≠",
        r"\ne": "≠",
        r"\leq": "≤",
        r"\le": "≤",
        r"\geq": "≥",
        r"\ge": "≥",
        r"\approx": "≈",
        r"\equiv": "≡",
        r"\sim": "∼",
        r"\cong": "≅",
        r"\propto": "∝",

        # Hình học
        r"\perp": "⊥",
        r"\parallel": "∥",
        r"\angle": "∠",
        r"\triangle": "△",
        r"\circ": "°",

        # Mũi tên
        r"\rightarrow": "→",
        r"\to": "→",
        r"\leftarrow": "←",
        r"\Rightarrow": "⇒",
        r"\Leftarrow": "⇐",
        r"\Leftrightarrow": "⇔",
        r"\leftrightarrow": "↔",
        r"\uparrow": "↑",
        r"\downarrow": "↓",

        # Tập hợp
        r"\in": "∈",
        r"\notin": "∉",
        r"\subset": "⊂",
        r"\subseteq": "⊆",
        r"\supset": "⊃",
        r"\supseteq": "⊇",
        r"\cup": "∪",
        r"\cap": "∩",
        r"\emptyset": "∅",

        # Logic
        r"\forall": "∀",
        r"\exists": "∃",
        r"\land": "∧",
        r"\lor": "∨",
        r"\neg": "¬",

        # Số học / giải tích
        r"\infty": "∞",
        r"\partial": "∂",
        r"\nabla": "∇",
        r"\sum": "∑",
        r"\prod": "∏",
        r"\int": "∫",

        # Hy Lạp
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\delta": "δ",
        r"\epsilon": "ε",
        r"\varepsilon": "ϵ",
        r"\zeta": "ζ",
        r"\eta": "η",
        r"\theta": "θ",
        r"\vartheta": "ϑ",
        r"\iota": "ι",
        r"\kappa": "κ",
        r"\lambda": "λ",
        r"\mu": "μ",
        r"\nu": "ν",
        r"\xi": "ξ",
        r"\pi": "π",
        r"\varpi": "ϖ",
        r"\rho": "ρ",
        r"\sigma": "σ",
        r"\tau": "τ",
        r"\upsilon": "υ",
        r"\phi": "φ",
        r"\varphi": "ϕ",
        r"\chi": "χ",
        r"\psi": "ψ",
        r"\omega": "ω",

        # Hy Lạp viết hoa
        r"\Gamma": "Γ",
        r"\Delta": "Δ",
        r"\Theta": "Θ",
        r"\Lambda": "Λ",
        r"\Xi": "Ξ",
        r"\Pi": "Π",
        r"\Sigma": "Σ",
        r"\Phi": "Φ",
        r"\Psi": "Ψ",
        r"\Omega": "Ω",

        # Đơn vị thường gặp
        r"\degree": "°",
        r"\ohm": "Ω",

        # Khoảng trắng LaTeX
        r"\,": " ",
        r"\;": " ",
        r"\:": " ",
        r"\!": "",
    }

    # ========================================================
    # PARSE BRACE
    # ========================================================

    @classmethod
    def _parse_braced_content(
        cls,
        text: str,
        opening_index: int
    ) -> Tuple[str, int]:

        if (
            opening_index >= len(text)
            or text[opening_index] != "{"
        ):
            return "", opening_index

        depth = 0
        content = []

        for index in range(
            opening_index,
            len(text)
        ):

            char = text[index]

            if char == "{":

                depth += 1

                if depth > 1:
                    content.append(char)

            elif char == "}":

                depth -= 1

                if depth == 0:

                    return (
                        "".join(content),
                        index
                    )

                content.append(char)

            else:

                content.append(char)

        return (
            "".join(content),
            len(text) - 1
        )

    # ========================================================
    # REMOVE LATEX DELIMITERS
    # ========================================================

    @classmethod
    def strip_math_delimiters(
        cls,
        text: str
    ) -> str:

        if not text:
            return ""

        text = text.strip()

        # $$ ... $$
        if (
            text.startswith("$$")
            and text.endswith("$$")
        ):
            text = text[2:-2]

        # \( ... \)
        elif (
            text.startswith(r"\(")
            and text.endswith(r"\)")
        ):
            text = text[2:-2]

        # \[ ... \]
        elif (
            text.startswith(r"\[")
            and text.endswith(r"\]")
        ):
            text = text[2:-2]

        # $ ... $
        elif (
            text.startswith("$")
            and text.endswith("$")
        ):
            text = text[1:-1]

        return text.strip()

    # ========================================================
    # FRAC
    # ========================================================

    @classmethod
    def convert_frac_recursive(
        cls,
        text: str
    ) -> str:

        if not text:
            return ""

        while r"\frac{" in text:

            start = text.find(
                r"\frac{"
            )

            numerator_start = start + len(
                r"\frac"
            )

            numerator, numerator_end = (
                cls._parse_braced_content(
                    text,
                    numerator_start
                )
            )

            denominator_start = numerator_end + 1

            if (
                denominator_start >= len(text)
                or text[denominator_start] != "{"
            ):
                break

            denominator, denominator_end = (
                cls._parse_braced_content(
                    text,
                    denominator_start
                )
            )

            numerator = cls.convert_frac_recursive(
                numerator
            )

            denominator = cls.convert_frac_recursive(
                denominator
            )

            replacement = (
                f"({numerator})"
                f"⁄"
                f"({denominator})"
            )

            text = (
                text[:start]
                + replacement
                + text[denominator_end + 1:]
            )

        return text

    # ========================================================
    # SQRT
    # ========================================================

    @classmethod
    def convert_sqrt(
        cls,
        text: str
    ) -> str:

        pattern = re.compile(
            r"\\sqrt(?:\[(.*?)\])?\{([^{}]*)\}"
        )

        def replace(match):

            index = match.group(1)
            content = match.group(2)

            if index:

                return (
                    f"√[{index}]"
                    f"({content})"
                )

            return f"√({content})"

        previous = None

        while previous != text:

            previous = text

            text = pattern.sub(
                replace,
                text
            )

        return text

    # ========================================================
    # TEXT COMMANDS
    # ========================================================

    @classmethod
    def convert_text_commands(
        cls,
        text: str
    ) -> str:

        # \text{abc} → abc
        text = re.sub(
            r"\\text\{([^{}]*)\}",
            r"\1",
            text
        )

        # \mathrm{abc} → abc
        text = re.sub(
            r"\\mathrm\{([^{}]*)\}",
            r"\1",
            text
        )

        # \mathbf{abc} → abc
        text = re.sub(
            r"\\mathbf\{([^{}]*)\}",
            r"\1",
            text
        )

        # \operatorname{sin} → sin
        text = re.sub(
            r"\\operatorname\{([^{}]*)\}",
            r"\1",
            text
        )

        return text

    # ========================================================
    # SUPERSCRIPT
    # ========================================================

    @classmethod
    def convert_superscript(
        cls,
        text: str
    ) -> str:

        # x^{2} → x²
        text = re.sub(
            r"\^\{([^{}]+)\}",
            lambda m: cls._to_superscript(
                m.group(1)
            ),
            text
        )

        # x^2 → x²
        text = re.sub(
            r"\^([0-9+\-=()]+)",
            lambda m: cls._to_superscript(
                m.group(1)
            ),
            text
        )

        # H^+ → H⁺
        text = re.sub(
            r"([A-Za-zΑ-Ωα-ω\)])\^([+\-])",
            lambda m:
            m.group(1)
            + cls._to_superscript(
                m.group(2)
            ),
            text
        )

        return text

    # ========================================================
    # SUBSCRIPT
    # ========================================================

    @classmethod
    def convert_subscript(
        cls,
        text: str
    ) -> str:

        # H_{2}O → H₂O
        text = re.sub(
            r"_\{([^{}]+)\}",
            lambda m: cls._to_subscript(
                m.group(1)
            ),
            text
        )

        # H_2O → H₂O
        text = re.sub(
            r"_([0-9]+)",
            lambda m: cls._to_subscript(
                m.group(1)
            ),
            text
        )

        return text

    # ========================================================
    # UNICODE SUP / SUB
    # ========================================================

    @classmethod
    def _to_superscript(
        cls,
        value: str
    ) -> str:

        return value.translate(
            cls.SUP_TRANSLATION
        )

    @classmethod
    def _to_subscript(
        cls,
        value: str
    ) -> str:

        return value.translate(
            cls.SUB_TRANSLATION
        )

    # ========================================================
    # CHEMISTRY
    # ========================================================

    @classmethod
    def normalize_chemistry(
        cls,
        text: str
    ) -> str:

        if not text:
            return ""

        # CuSO4.5H2O → CuSO₄·5H₂O
        text = re.sub(
            r"([A-Za-z0-9\]\)])"
            r"\s*\.\s*"
            r"(\d*[A-Z][a-z]?)",
            r"\1·\2",
            text
        )

        # Fe^3+ → Fe³⁺
        text = re.sub(
            r"([A-Za-z0-9\)\]])"
            r"\^"
            r"([0-9]*[+\-])",
            lambda m:
            m.group(1)
            + cls._to_superscript(
                m.group(2)
            ),
            text
        )

        # Ca(OH)2 → Ca(OH)₂
        text = re.sub(
            r"(\)|[A-Z][a-z]?)(\d+)",
            lambda m:
            m.group(1)
            + cls._to_subscript(
                m.group(2)
            ),
            text
        )

        # H2SO4 → H₂SO₄
        text = re.sub(
            r"([A-Z][a-z]?)(\d+)",
            lambda m:
            m.group(1)
            + cls._to_subscript(
                m.group(2)
            ),
            text
        )

        return text

    # ========================================================
    # VECTOR / GEOMETRY
    # ========================================================

    @classmethod
    def normalize_geometry(
        cls,
        text: str
    ) -> str:

        # \vec{AB} → \u0305AB
        text = re.sub(
            r"\\vec\{([A-Za-z]+)\}",
            r"\1⃗",
            text
        )

        # \overline{AB} → AB
        text = re.sub(
            r"\\overline\{([^{}]+)\}",
            r"\1",
            text
        )

        # \widehat{ABC} → ∠ABC
        text = re.sub(
            r"\\widehat\{([A-Za-z]+)\}",
            lambda m:
            "∠" + m.group(1),
            text
        )

        return text

    # ========================================================
    # MASTER NORMALIZE
    # ========================================================

    @classmethod
    def normalize(
        cls,
        text: str
    ) -> str:

        if text is None:
            return ""

        text = str(text)

        if not text.strip():
            return ""

        # Không được xóa tùy tiện các ký tự '$'
        text = cls.strip_math_delimiters(
            text
        )

        # Chuẩn hóa khoảng trắng
        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        # Xử lý lệnh phức tạp trước
        text = cls.convert_frac_recursive(
            text
        )

        text = cls.convert_sqrt(
            text
        )

        text = cls.convert_geometry(
            text
        )

        text = cls.convert_text_commands(
            text
        )

        text = cls.convert_superscript(
            text
        )

        text = cls.convert_subscript(
            text
        )

        text = cls.normalize_chemistry(
            text
        )

        # Thay thế các ký hiệu đơn
        for latex, symbol in sorted(
            cls.TRANSLATION_MAP.items(),
            key=lambda item: len(item[0]),
            reverse=True
        ):

            text = text.replace(
                latex,
                symbol
            )

        # Xóa các cặp ngoặc LaTeX còn sót lại
        text = re.sub(
            r"\\left",
            "",
            text
        )

        text = re.sub(
            r"\\right",
            "",
            text
        )

        # Xóa escape backslash trước ký tự thông thường
        text = re.sub(
            r"\\([{}[\]()])",
            r"\1",
            text
        )

        # Dọn ngoặc thừa ở đầu/cuối
        text = text.strip()

        return text

    # Alias tương thích
    convert = normalize

    # Alias sửa lỗi tương thích với bản cũ
    @classmethod
    def convert_geometry(
        cls,
        text: str
    ) -> str:

        return cls.normalize_geometry(
            text
        )


# ============================================================
# 2. MATH RENDERER
# ============================================================

class MathRenderer:
    """
    Bộ kết xuất công thức vào Word.

    Công thức inline:
        p = document.add_paragraph()
        MathRenderer.render_inline_math(
            p,
            r"F = ma"
        )

    Công thức display:
        MathRenderer.render_display_math(
            doc,
            r"E = mc^2"
        )
    """

    DEFAULT_FONT = "Cambria Math"

    # ========================================================
    # FONT
    # ========================================================

    @staticmethod
    def _set_font_safely(
        run,
        font_name: str = DEFAULT_FONT
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

            rPr.append(
                rFonts
            )

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

    # ========================================================
    # INLINE
    # ========================================================

    @classmethod
    def render_inline_math(
        cls,
        paragraph,
        latex_str: str
    ):

        clean_text = ScienceNormalizer.normalize(
            latex_str
        )

        if not clean_text:
            return None

        run = paragraph.add_run(
            clean_text
        )

        cls._set_font_safely(
            run,
            cls.DEFAULT_FONT
        )

        run.font.size = Pt(13)

        # Công thức inline thường dùng dạng nghiêng
        # nhưng không ép nghiêng các ký hiệu đã chuyển Unicode.
        run.font.italic = True

        return run

    # ========================================================
    # DISPLAY
    # ========================================================

    @classmethod
    def render_display_math(
        cls,
        doc,
        latex_str: str
    ):

        paragraph = doc.add_paragraph()

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        paragraph.paragraph_format.space_before = Pt(4)
        paragraph.paragraph_format.space_after = Pt(6)

        clean_text = ScienceNormalizer.normalize(
            latex_str
        )

        if not clean_text:
            return paragraph

        run = paragraph.add_run(
            clean_text
        )

        cls._set_font_safely(
            run,
            cls.DEFAULT_FONT
        )

        run.font.size = Pt(14)
        run.font.italic = True

        return paragraph

    # ========================================================
    # RENDER WITH OPTIONAL DISPLAY
    # ========================================================

    @classmethod
    def render(
        cls,
        doc,
        latex_str: str,
        display: bool = False,
        paragraph=None
    ):

        if display:

            return cls.render_display_math(
                doc,
                latex_str
            )

        if paragraph is None:

            paragraph = doc.add_paragraph()

        return cls.render_inline_math(
            paragraph,
            latex_str
        )


# ============================================================
# 3. API TƯƠNG THÍCH NGƯỢC
# ============================================================

def normalize_science_formula(
    formula: str
) -> str:

    return ScienceNormalizer.normalize(
        formula
    )


def render_inline_math(
    paragraph,
    formula: str
):

    return MathRenderer.render_inline_math(
        paragraph,
        formula
    )


def render_display_math(
    doc,
    formula: str
):

    return MathRenderer.render_display_math(
        doc,
        formula
    )
