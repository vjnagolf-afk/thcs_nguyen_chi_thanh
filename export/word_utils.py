# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_utils.py
============================================================
Nhiệm vụ:
- Các hàm tiện ích dùng chung cho hệ thống xuất Word.
- Xử lý ngày tháng.
- Xóa file tạm.
- Làm sạch tên file.
- Định dạng tiền.
- Kiểm tra URL.
- Chuẩn hóa dữ liệu đầu vào.

Không chứa logic tạo DOCX.
============================================================
"""

from __future__ import annotations

import datetime
import logging
import os
import re
from pathlib import Path
from typing import Any, Optional, Union


logger = logging.getLogger("WordUtils")


class WordUtils:
    """
    Bộ tiện ích dùng chung cho hệ thống export Word.
    """

    # ========================================================
    # NGÀY THÁNG
    # ========================================================

    @staticmethod
    def get_current_date_str(
        include_prefix: bool = True,
        zero_pad: bool = True,
    ) -> str:
        """
        Trả về ngày hiện tại theo chuẩn văn bản Việt Nam.

        Ví dụ:
        - ngày 22 tháng 07 năm 2026
        - 22 tháng 07 năm 2026
        """

        now = datetime.datetime.now()

        if zero_pad:
            day = f"{now.day:02d}"
            month = f"{now.month:02d}"
        else:
            day = str(now.day)
            month = str(now.month)

        result = f"{day} tháng {month} năm {now.year}"

        if include_prefix:
            return f"ngày {result}"

        return result

    # ========================================================
    # FILE
    # ========================================================

    @staticmethod
    def safe_delete_file(
        file_path: Optional[Union[str, Path]]
    ) -> bool:
        """
        Xóa file an toàn.

        Returns:
            True  -> đã xóa hoặc file không tồn tại
            False -> xóa thất bại
        """

        if not file_path:
            return True

        try:
            path = Path(file_path)

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
                file_path,
                exc
            )

            return False

    @staticmethod
    def ensure_directory(
        directory: Union[str, Path]
    ) -> Path:
        """
        Tạo thư mục nếu chưa tồn tại.
        """

        path = Path(directory)

        path.mkdir(
            parents=True,
            exist_ok=True
        )

        return path

    # ========================================================
    # TÊN FILE
    # ========================================================

    @staticmethod
    def sanitize_filename(
        filename: Any,
        max_length: int = 100,
        default_name: str = "document"
    ) -> str:
        """
        Làm sạch tên file để tương thích Windows/Linux.

        Loại bỏ:
        < > : " / \\ | ? *

        Đồng thời:
        - loại bỏ ký tự điều khiển
        - loại bỏ khoảng trắng đầu/cuối
        - không để tên file rỗng
        """

        if filename is None:
            filename = ""

        filename = str(filename).strip()

        if not filename:
            filename = default_name

        # Ký tự không hợp lệ trên Windows/Linux
        filename = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            filename
        )

        # Ký tự điều khiển
        filename = re.sub(
            r"[\x00-\x1f\x7f]",
            "_",
            filename
        )

        # Gom nhiều khoảng trắng
        filename = re.sub(
            r"\s+",
            " ",
            filename
        ).strip()

        # Không để kết thúc bằng dấu chấm hoặc khoảng trắng
        filename = filename.rstrip(". ")

        if not filename:
            filename = default_name

        return filename[:max_length]

    @staticmethod
    def build_filename(
        prefix: str,
        name: Optional[str] = None,
        extension: str = ".docx"
    ) -> str:
        """
        Tạo tên file chuẩn.

        Ví dụ:
            build_filename(
                "KHBD",
                "Bài 1: Chuyển động",
                ".docx"
            )

        Kết quả:
            KHBD_Bài 1_ Chuyển động.docx
        """

        parts = []

        if prefix:
            parts.append(
                WordUtils.sanitize_filename(prefix)
            )

        if name:
            parts.append(
                WordUtils.sanitize_filename(name)
            )

        filename = "_".join(parts)

        extension = extension or ""

        if extension and not extension.startswith("."):
            extension = f".{extension}"

        return f"{filename}{extension}"

    # ========================================================
    # CHUẨN HÓA CHUỖI
    # ========================================================

    @staticmethod
    def safe_text(
        value: Any,
        default: str = ""
    ) -> str:
        """
        Chuyển dữ liệu về chuỗi an toàn.
        """

        if value is None:
            return default

        try:
            text = str(value)
        except Exception:
            return default

        return (
            text
            .replace("\x00", "")
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .strip()
        )

    @staticmethod
    def normalize_whitespace(
        text: Any
    ) -> str:
        """
        Chuẩn hóa khoảng trắng nhưng vẫn giữ xuống dòng.
        """

        text = WordUtils.safe_text(text)

        lines = []

        for line in text.splitlines():
            line = re.sub(
                r"[ \t]+",
                " ",
                line
            ).strip()

            lines.append(line)

        return "\n".join(lines)

    # ========================================================
    # SỐ TIỀN
    # ========================================================

    @staticmethod
    def format_money(
        amount: Any,
        suffix: str = ""
    ) -> str:
        """
        Định dạng tiền theo kiểu Việt Nam.

        Ví dụ:
            1500000 → 1.500.000
        """

        try:
            value = float(amount)
        except (TypeError, ValueError):
            return "0"

        result = f"{value:,.0f}".replace(
            ",",
            "."
        )

        return f"{result}{suffix}"

    # ========================================================
    # URL
    # ========================================================

    @staticmethod
    def is_valid_url(
        url: Any
    ) -> bool:
        """
        Kiểm tra URL HTTP/HTTPS.
        """

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

        return regex.match(url) is not None

    # ========================================================
    # EXTENSION
    # ========================================================

    @staticmethod
    def get_extension(
        filename: Any
    ) -> str:
        """
        Lấy phần mở rộng file, viết thường.

        Ví dụ:
            file.DOCX → .docx
        """

        if not filename:
            return ""

        return Path(
            str(filename)
        ).suffix.lower()

    @staticmethod
    def remove_extension(
        filename: Any
    ) -> str:
        """
        Bỏ phần mở rộng file.
        """

        if not filename:
            return ""

        return Path(
            str(filename)
        ).stem

    # ========================================================
    # CHUYỂN ĐỔI BOOLEAN
    # ========================================================

    @staticmethod
    def to_bool(
        value: Any,
        default: bool = False
    ) -> bool:
        """
        Chuyển dữ liệu về bool an toàn.
        """

        if isinstance(value, bool):
            return value

        if value is None:
            return default

        if isinstance(value, (int, float)):
            return bool(value)

        text = str(value).strip().lower()

        if text in {
            "true",
            "1",
            "yes",
            "y",
            "co",
            "có",
            "on"
        }:
            return True

        if text in {
            "false",
            "0",
            "no",
            "n",
            "khong",
            "không",
            "off"
        }:
            return False

        return default
