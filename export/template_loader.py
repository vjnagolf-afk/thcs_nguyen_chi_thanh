# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import logging

from typing import Dict, Any, Optional

import docx


logger = logging.getLogger(
    "TemplateLoader"
)


class TemplateLoader:

    @staticmethod
    def validate_template(
        template_path: Optional[str]
    ) -> bool:

        return bool(
            template_path
            and os.path.isfile(template_path)
            and template_path.lower().endswith(".docx")
        )

    @classmethod
    def load(
        cls,
        template_path: Optional[str] = None
    ) -> docx.Document:

        if cls.validate_template(template_path):

            return docx.Document(
                template_path
            )

        logger.warning(
            "Không có template hợp lệ. "
            "Tạo tài liệu Word mới."
        )

        return docx.Document()

    @staticmethod
    def replace_variables(
        doc,
        variables: Dict[str, Any]
    ):

        if not variables:

            return doc

        def replace_paragraph(paragraph):

            if not paragraph.runs:

                return

            full_text = "".join(
                run.text or ""
                for run in paragraph.runs
            )

            new_text = full_text

            for key, value in variables.items():

                value = "" if value is None else str(value)

                patterns = [
                    "{{ " + str(key) + " }}",
                    "{{" + str(key) + "}}",
                    "{{" + str(key) + " }}",
                    "{{ " + str(key) + "}}",
                ]

                for pattern in patterns:

                    new_text = new_text.replace(
                        pattern,
                        value
                    )

            if new_text == full_text:

                return

            # Giữ format của run đầu tiên
            paragraph.runs[0].text = new_text

            for run in paragraph.runs[1:]:

                run.text = ""

        for paragraph in doc.paragraphs:

            replace_paragraph(paragraph)

        for table in doc.tables:

            for row in table.rows:

                for cell in row.cells:

                    for paragraph in cell.paragraphs:

                        replace_paragraph(paragraph)

        for section in doc.sections:

            for paragraph in section.header.paragraphs:

                replace_paragraph(paragraph)

            for paragraph in section.footer.paragraphs:

                replace_paragraph(paragraph)

        return doc

    @staticmethod
    def save(
        doc,
        output_path: str
    ):

        os.makedirs(
            os.path.dirname(output_path)
            or ".",
            exist_ok=True
        )

        doc.save(output_path)

        return output_path
