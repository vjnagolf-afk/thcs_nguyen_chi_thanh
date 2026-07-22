# -*- coding: utf-8 -*-
"""
Module: export/word_utils.py

Nhiệm vụ:
- Các hàm tiện ích dùng chung cho hệ thống xuất Word.
- Không chứa logic nghiệp vụ.
- Không phụ thuộc Streamlit.
"""

from __future__ import annotations

import datetime
import logging
import os
import re
from pathlib import Path
from typing import Optional, Union


logger = logging.getLogger("WordUtils")


class WordUtils:
    """Các tiện ích dùng chung cho hệ thống xuất DOCX."""

    @staticmethod
    def get_current_date_str() -> str:
        """
        Trả về ngày hiện tại theo chuẩn văn bản hành chính Việt Nam.

        Ví dụ:
        ngày 22 tháng 07 năm 2026
        """

        now = datetime.datetime.now()

        return (
            f"ngày {now.day:02d} "
            f"tháng {now.month:02d} "
            f"năm {now.year}"
        )

    @staticmethod
    def safe_delete_file(
        file_path: Union[str, Path]
    ) -> bool:
        """
        Xóa file an toàn.

        Returns:
            True  : Xóa thành công hoặc file không tồn tại.
            False : Xóa thất bại.
        """

        if not file_path:
            return True

        path = Path(file_path)

        try:

            if not path.exists():
                return True

            if not path.is_file():
                logger.warning(
                    "Không thể xóa vì không phải file: %s",
                    path
                )

                return False

            path.unlink()

            logger.info(
                "Đã xóa file tạm: %s",
                path
            )

            return True

        except Exception as exc:

            logger.warning(
                "Không thể xóa file %s: %s",
                path,
                exc
            )

            return False

    @staticmethod
    def sanitize_filename(
        filename: str,
        default_name: str = "document"
    ) -> str:
        """
        Làm sạch tên file an toàn cho Windows/Linux.

        Không làm thay đổi phần mở rộng.
        """

        if not filename:

            filename = default_name

        filename = str(filename).strip()

        # Loại bỏ ký tự điều khiển
        filename = re.sub(
            r"[\x00-\x1f\x7f]",
            "",
            filename
        )

        # Ký tự không hợp lệ trên Windows/Linux
        filename = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            filename
        )

        # Gom nhiều khoảng trắng
        filename = re.sub(
            r"\s+",
            " ",
            filename
        ).strip()

        # Không để tên kết thúc bằng dấu chấm/khoảng trắng
        filename = filename.rstrip(". ")

        # Tên file không hợp lệ trên Windows
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }

        stem = Path(filename).stem
        suffix = Path(filename).suffix

        if stem.upper() in reserved_names:

            stem = f"{stem}_file"

        filename = f"{stem}{suffix}"

        if not filename:

            filename = default_name

        return filename[:100]

    @staticmethod
    def format_money(
        amount: Optional[float]
    ) -> str:
        """Định dạng tiền Việt Nam."""

        if amount is None:

            return "0"

        try:

            value = float(amount)

        except (TypeError, ValueError):

            return "0"

        return (
            f"{value:,.0f}"
            .replace(",", ".")
        )

    @staticmethod
    def is_valid_url(
        url: str
    ) -> bool:
        """Kiểm tra URL HTTP/HTTPS."""

        if not url:

            return False

        url = str(url).strip()

        regex = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9]"
            r"(?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
            r"[A-Z]{2,63}\.?|"
            r"localhost|"
            r"\d{1,3}(?:\.\d{1,3}){3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE
        )

        return bool(
            regex.match(url)
        )
