"""
Module: export/word_utils.py
Nhiệm vụ: Chứa các hàm tiện ích hỗ trợ (Helper functions).
Giúp các module khác tinh gọn hơn, không cần lặp lại logic xử lý dữ liệu.
"""

import os
import datetime
import logging
from typing import Optional

logger = logging.getLogger("WordUtils")

class WordUtils:
    @staticmethod
    def get_current_date_str() -> str:
        """Trả về ngày tháng năm theo chuẩn văn bản hành chính Việt Nam (VD: 13 tháng 07 năm 2026)"""
        now = datetime.datetime.now()
        return f"ngày {now.day:02d} tháng {now.month:02d} năm {now.year}"

    @staticmethod
    def safe_delete_file(file_path: str):
        """Xóa tệp tạm an toàn, tránh lỗi FileNotFoundError."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Đã xóa tệp tạm: {file_path}")
        except Exception as e:
            logger.warning(f"Không thể xóa tệp tạm {file_path}: {e}")

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Dọn dẹp tên file để tránh các ký tự đặc biệt gây lỗi hệ thống Windows/Linux.
        Thay thế các ký tự cấm bằng dấu gạch dưới.
        """
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        return sanitized[:100]  # Giới hạn độ dài tên file

    @staticmethod
    def format_money(amount: float) -> str:
        """Định dạng số tiền hiển thị chuyên nghiệp (nếu cần dùng trong báo cáo tài chính)"""
        return "{:,.0f}".format(amount).replace(",", ".")

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Kiểm tra đường dẫn URL có đúng định dạng không."""
        regex = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None
