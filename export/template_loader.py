# -*- coding: utf-8 -*-

"""
Module: export/template_loader.py

Nhiệm vụ:
- Tải Word template.
- Kiểm tra template.
- Tạo bản sao làm việc.
- Thay thế biến {{ variable }}.
- Hỗ trợ paragraph, table, header, footer.
"""

import os
import shutil
import logging

from typing import (
    Dict,
    Any,
    Optional
)

import docx


logger = logging.getLogger(
    "TemplateLoader"
)


class TemplateLoader:

    DEFAULT_TEMPLATE_NAME = (
        "default_template.docx"
    )

    @classmethod
    def validate_template(
        cls,
        template_path: str
    ) -> bool:

        if not template_path:

            return False

        if not os.path.exists(
            template_path
        ):

            return False

        if not template_path.lower().endswith(
            ".docx"
        ):

            return False

        return True

    @classmethod
    def load(
        cls,
        template_path: Optional[str] = None
    ) -> docx.Document:

        if template_path:

            if not cls.validate_template(
                template_path
            ):

                raise FileNotFoundError(
                    "Template Word không hợp lệ: "
                    f"{template_path}"
                )

            return docx.Document(
                template_path
            )

        logger.info(
            "Không có template. "
            "Khởi tạo tài liệu Word mới."
        )

        return docx.Document()

    @classmethod
    def copy_template(
        cls,
        template_path: str,
        output_path: str
    ) -> str:

        if not cls.validate_template(
            template_path
        ):

            raise FileNotFoundError(
                "Không tìm thấy template Word."
            )

        output_dir = os.path.dirname(
            output_path
        )

        if output_dir:

            os.makedirs(
                output_dir,
                exist_ok=True
            )

        shutil.copy2(
            template_path,
            output_path
        )

        return output_path

    @classmethod
    def replace_variables(
        cls,
        doc: docx.Document,
        variables: Dict[str, Any]
    ):

        if not variables:

            return doc

        # Paragraph
        for paragraph in doc.paragraphs:

            cls._replace_in_paragraph(
                paragraph,
                variables
            )

        # Tables
        for table in doc.tables:

            for row in table.rows:

                for cell in row.cells:

                    for paragraph in cell.paragraphs:

                        cls._replace_in_paragraph(
                            paragraph,
                            variables
                        )

        # Headers / Footers
        for section in doc.sections:

            for paragraph in section.header.paragraphs:

                cls._replace_in_paragraph(
                    paragraph,
                    variables
                )

            for paragraph in section.footer.paragraphs:

                cls._replace_in_paragraph(
                    paragraph,
                    variables
                )

        return doc

    @staticmethod
    def _replace_in_paragraph(
        paragraph,
        variables: Dict[str, Any]
    ):

        if not paragraph.runs:

            return

        full_text = "".join(
            run.text or ""
            for run in paragraph.runs
        )

        if not full_text:

            return

        new_text = full_text

        for key, value in variables.items():

            placeholder = (
                "{{ "
                + str(key)
                + " }}"
            )

            placeholder_no_space = (
                "{{"
                + str(key)
                + "}}"
            )

            new_text = new_text.replace(
                placeholder,
                str(value)
            )

            new_text = new_text.replace(
                placeholder_no_space,
                str(value)
            )

        if new_text == full_text:

            return

        paragraph.runs[0].text = new_text

        for run in paragraph.runs[1:]:

            run.text = ""

    @classmethod
    def save(
        cls,
        doc: docx.Document,
        output_path: str
    ) -> str:

        output_dir = os.path.dirname(
            output_path
        )

        if output_dir:

            os.makedirs(
                output_dir,
                exist_ok=True
            )

        doc.save(
            output_path
        )

        return output_path
