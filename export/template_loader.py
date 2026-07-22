# -*- coding: utf-8 -*-
"""
template_loader.py
Đọc và nạp mẫu Word KHBD.
"""

import os
from pathlib import Path
from typing import Optional

import docx


class TemplateLoader:

    DEFAULT_TEMPLATE = "templates/KHBD_Mau.docx"

    @classmethod
    def get_template_path(
        cls,
        custom_template=None,
        default_path: str = None
    ) -> Optional[str]:

        if custom_template is not None:

            # UploadedFile của Streamlit
            if hasattr(custom_template, "name"):
                temp_dir = Path("temp_templates")
                temp_dir.mkdir(exist_ok=True)

                output_path = temp_dir / custom_template.name

                with open(output_path, "wb") as f:
                    f.write(custom_template.getbuffer())

                return str(output_path)

            # Đường dẫn file
            if isinstance(custom_template, str):
                if os.path.exists(custom_template):
                    return custom_template

        path = default_path or cls.DEFAULT_TEMPLATE

        if os.path.exists(path):
            return path

        return None

    @classmethod
    def load_template(
        cls,
        custom_template=None,
        default_path: str = None
    ):

        template_path = cls.get_template_path(
            custom_template=custom_template,
            default_path=default_path
        )

        if not template_path:
            return None

        try:
            return docx.Document(template_path)
        except Exception:
            return None
