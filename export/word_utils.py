# -*- coding: utf-8 -*-

import os
import re
import datetime
import logging

from typing import Optional


logger = logging.getLogger(
    "WordUtils"
)


class WordUtils:

    @staticmethod
    def get_current_date_str() -> str:

        now = datetime.datetime.now()

        return (
            f"ngày {now.day:02d} "
            f"tháng {now.month:02d} "
            f"năm {now.year}"
        )

    @staticmethod
    def safe_delete_file(
        file_path: str
    ):

        try:

            if os.path.exists(
                file_path
            ):

                os.remove(
                    file_path
                )

        except Exception as error:

            logger.warning(
                "Không thể xóa file %s: %s",
                file_path,
                error
            )

    @staticmethod
    def sanitize_filename(
        filename: str
    ) -> str:

        if not filename:

            return "document"

        invalid_chars = (
            r'[<>:"/\\|?*]'
        )

        filename = re.sub(
            invalid_chars,
            "_",
            filename
        )

        filename = filename.strip(
            " ."
        )

        return filename[:100] or "document"

    @staticmethod
    def format_money(
        amount: float
    ) -> str:

        return (
            "{:,.0f}".format(
                amount
            ).replace(
                ",",
                "."
            )
        )

    @staticmethod
    def is_valid_url(
        url: str
    ) -> bool:

        if not url:

            return False

        regex = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9]"
            r"(?:[A-Z0-9-]{0,61}"
            r"[A-Z0-9])?\.)+"
            r"[A-Z]{2,63}\.?|"
            r"localhost|"
            r"\d{1,3}(?:\."
            r"\d{1,3}){3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE
        )

        return (
            re.match(
                regex,
                url
            )
            is not None
        )
