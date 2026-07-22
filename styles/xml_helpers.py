# -*- coding: utf-8 -*-

from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class XmlHelpers:

    @staticmethod
    def set_font_safely(
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

        for font_attr in (
            "ascii",
            "hAnsi",
            "eastAsia",
            "cs"
        ):

            rFonts.set(
                qn(f"w:{font_attr}"),
                font_name
            )

    @staticmethod
    def apply_paragraph_shading(
        paragraph,
        color_hex: str = "F5F5F5"
    ):

        pPr = paragraph._element.get_or_add_pPr()

        shd = pPr.find(
            qn("w:shd")
        )

        if shd is None:

            shd = OxmlElement(
                "w:shd"
            )

            pPr.append(shd)

        shd.set(
            qn("w:val"),
            "clear"
        )

        shd.set(
            qn("w:color"),
            "auto"
        )

        shd.set(
            qn("w:fill"),
            color_hex
        )

    @staticmethod
    def apply_bottom_border(
        paragraph,
        color_hex: str = "CCCCCC",
        size: int = 8
    ):

        pPr = paragraph._element.get_or_add_pPr()

        pBdr = pPr.find(
            qn("w:pBdr")
        )

        if pBdr is None:

            pBdr = OxmlElement(
                "w:pBdr"
            )

            pPr.append(pBdr)

        old_bottom = pBdr.find(
            qn("w:bottom")
        )

        if old_bottom is not None:

            pBdr.remove(old_bottom)

        bottom = OxmlElement(
            "w:bottom"
        )

        bottom.set(
            qn("w:val"),
            "single"
        )

        bottom.set(
            qn("w:sz"),
            str(size)
        )

        bottom.set(
            qn("w:space"),
            "4"
        )

        bottom.set(
            qn("w:color"),
            color_hex
        )

        pBdr.append(bottom)

    @staticmethod
    def set_cell_shading(
        cell,
        color_hex: str
    ):

        tcPr = cell._element.get_or_add_tcPr()

        shd = tcPr.find(
            qn("w:shd")
        )

        if shd is None:

            shd = OxmlElement(
                "w:shd"
            )

            tcPr.append(shd)

        shd.set(
            qn("w:val"),
            "clear"
        )

        shd.set(
            qn("w:fill"),
            color_hex
        )

    @staticmethod
    def set_cell_border(
        cell,
        **kwargs
    ):

        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()

        tcBorders = tcPr.first_child_found_in(
            "w:tcBorders"
        )

        if tcBorders is None:

            tcBorders = OxmlElement(
                "w:tcBorders"
            )

            tcPr.append(tcBorders)

        for edge in (
            "top",
            "left",
            "bottom",
            "right",
            "insideH",
            "insideV"
        ):

            if edge not in kwargs:
                continue

            edge_data = kwargs.get(edge)

            tag = "w:{}".format(edge)

            element = tcBorders.find(
                qn(tag)
            )

            if element is None:

                element = OxmlElement(tag)
                tcBorders.append(element)

            for key in [
                "val",
                "sz",
                "space",
                "color"
            ]:

                if key in edge_data:

                    element.set(
                        qn(f"w:{key}"),
                        str(edge_data[key])
                    )
