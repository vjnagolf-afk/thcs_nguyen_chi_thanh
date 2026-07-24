# -*- coding: utf-8 -*-
"""
Module: export/export_word.py
Nhiệm vụ: 
- Cung cấp Public API tương thích ngược với hệ thống cũ.
- Thực thi bóc tách văn bản khoa học đan xen công thức (Toán, Lý, Hóa).
- Đồng bộ toàn vẹn lề trang cố định theo đúng yêu cầu thiết kế.
"""

import io
from typing import Dict, Any, Optional
from .word_export_engine import export_markdown_to_word
from .word_utils import clean_xml_forbidden_chars

class WordExportEngine:
    """
    Class Wrapper tương thích ngược với cấu trúc Engine cũ của bạn.
    Điều phối luồng gọi trực tiếp vào lõi xử lý trung tâm mới.
    """
    
    @classmethod
    def convert_markdown_to_docx_bytes(cls, markdown_text: str, metadata: Optional[dict] = None) -> bytes:
        """
        Chuyển đổi chuỗi văn bản Markdown chứa biểu thức khoa học phức tạp sang mảng bytes dữ liệu.
        """
        meta_vars = {}
        if metadata:
            # Áp dụng map các biến nhãn dán từ metadata sang template (Lỗi 1)
            meta_vars = {
                "title": metadata.get("title", "........................."),
                "mon": metadata.get("mon", "......."),
                "lop": metadata.get("lop", "......."),
                "so_tiet": metadata.get("so_tiet", "...")
            }
            
            # Nếu có cờ cấu hình KHBD (Kế hoạch bài dạy) từ hệ thống cũ, ta tự động chèn 
            # một khối cấu trúc Header tiêu chuẩn 5512 vào phần đầu văn bản Markdown
            if metadata.get("is_khbd"):
                khbd_header_markdown = (
                    f"| TRƯỜNG: .................................... | HỌ VÀ TÊN GIÁO VIÊN: .......................... |\n"
                    f"| TỔ: ........................................ | MÔN: {meta_vars['mon'].upper()} - LỚP: {meta_vars['lop']} |\n\n"
                    f"# TÊN BÀI DẠY: {meta_vars['title'].upper()}\n"
                    f"*Môn học/Hoạt động giáo dục: {meta_vars['mon']}; Thời gian thực hiện: {meta_vars['so_tiet']} tiết*\n\n"
                    f"---\n\n"
                )
                markdown_text = khbd_header_markdown + markdown_text

        # Gọi trực tiếp bộ điều phối Word Export Engine trung tâm để xuất stream dữ liệu (Sửa lỗi 6)
        bytes_io_stream = export_markdown_to_word(
            markdown_content=markdown_text,
            template_file_path=None,  # Có thể truyền đường dẫn file template .docx cục bộ vào đây
            meta_variables=meta_vars
        )
        
        return bytes_io_stream.getvalue()

    @classmethod
    def export_to_word(cls, data_cache: Dict[str, Any]) -> bytes:
        """
        API tiếp nhận cache dữ liệu thô từ hệ thống AI và trích xuất tệp Word nhị phân.
        """
        markdown_content = data_cache.get("ai_generated_content", "")
        return cls.convert_markdown_to_docx_bytes(markdown_content, metadata=data_cache)


# ============================================================
# PUBLIC API (Cổng giao tiếp dùng cho các View / Streamlit UI)
# ============================================================
def export_word(markdown_text: str) -> bytes:
    """
    Hàm API công khai kết nối trực tiếp đến giao diện hiển thị chính của người dùng.
    
    Parameters
    ----------
    markdown_text : str
        Nội dung chuỗi Markdown kết hợp LaTeX do AI hoặc người dùng biên soạn.
        
    Returns
    -------
    bytes
        Dữ liệu tệp Word (.docx) ở dạng chuỗi byte nhị phân sẵn sàng để download.
    """
    return WordExportEngine.convert_markdown_to_docx_bytes(markdown_text)
