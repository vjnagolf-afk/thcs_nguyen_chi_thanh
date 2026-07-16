"""
Module: export/export_word.py
Nhiệm vụ: Lớp điều phối trung tâm (Facade Pattern).
Cơ chế: Đọc Abstract Syntax Tree (AST) từ Tokenizer và phân phối tới các Renderer.
Bảo mật: Bẫy lỗi toàn cục (Global Exception Handling), không để sập ứng dụng.
"""

import io
import logging
from typing import Dict, Any
import docx

# Cấu hình logging tiêu chuẩn
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WordExportEngine")

class WordExportEngine:
    """
    Điểm truy cập duy nhất (Entry point) cho toàn bộ hệ thống xuất file Word.
    Tuyệt đối không chứa logic xử lý chuỗi hay vẽ bảng tại đây.
    """

    @classmethod
    def export_to_word(cls, data_cache: Dict[str, Any]) -> bytes:
        """
        Tiếp nhận dữ liệu thô, phân tích thành AST và render ra file Word.
        
        Args:
            data_cache (Dict[str, Any]): Dữ liệu lưu trữ (exam_cache) từ Streamlit.
            
        Returns:
            bytes: Luồng byte của file .docx sẵn sàng để tải xuống.
        """
        try:
            logger.info("Khởi động tiến trình kết xuất tài liệu Word...")
            doc = docx.Document()

            # Nhập khẩu trễ (Lazy Imports) để tránh Circular Import và cô lập lỗi
            from .word_styles import StyleManager
            from .word_markdown import MarkdownTokenizer
            from .word_tables import TableRenderer
            from .word_images import ImageRenderer
            from .word_math import MathRenderer

            # 1. KHỞI TẠO ĐỊNH DẠNG CHUẨN (A4, Margins, Base Fonts)
            StyleManager.setup_base_styles(doc)

            # Lấy dữ liệu cốt lõi
            ai_text = data_cache.get("ai_generated_content", "")
            is_khbd = data_cache.get("is_khbd", False)

            # 2. XỬ LÝ CÁC THÀNH PHẦN TĨNH (Phân hệ đặc thù)
            if is_khbd:
                logger.info("Render cấu trúc tĩnh: Kế hoạch bài dạy (KHBD)")
                TableRenderer.build_khbd_header(doc, data_cache)
            else:
                logger.info("Render cấu trúc tĩnh: Ma trận và Đặc tả")
                TableRenderer.build_matrix_table(doc, data_cache)
                doc.add_paragraph()
                TableRenderer.build_specification_table(doc, data_cache)
                doc.add_paragraph()

            # 3. PHÂN TÍCH CÚ PHÁP (AST GENERATION)
            # Tokenizer trả về một mảng các Node: [{"type": "heading", "level": 1, "tokens": [...]}, ...]
            logger.info("Đang phân tích cú pháp Markdown và LaTeX (Tokenizer)...")
            ast_nodes = MarkdownTokenizer.parse(ai_text)

            # 4. KẾT XUẤT ĐỘNG (AST RENDERING)
            logger.info(f"Bắt đầu render {len(ast_nodes)} AST Nodes...")
            for node in ast_nodes:
                node_type = node.get("type")

                if node_type == "heading":
                    StyleManager.render_heading(doc, node, MathRenderer)
                
                elif node_type == "paragraph":
                    StyleManager.render_paragraph(doc, node, MathRenderer)
                
                elif node_type == "list_item":
                    StyleManager.render_list_item(doc, node, MathRenderer)
                
                elif node_type == "table":
                    TableRenderer.render_ast_table(doc, node, StyleManager, MathRenderer)
                
                elif node_type == "image":
                    ImageRenderer.render_image(doc, node)
                
                elif node_type == "math_block":
                    MathRenderer.render_display_math(doc, node)
                
                elif node_type == "code_block":
                    StyleManager.render_code_block(doc, node)
                
                else:
                    logger.warning(f"Bỏ qua Node không xác định: {node_type}")

            # 5. LƯU TRỮ VÀ XUẤT BYTES
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            logger.info("Tiến trình kết xuất hoàn tất thành công.")
            
            return bio.getvalue()

        except Exception as e:
            logger.error(f"Lỗi nghiêm trọng sập hệ thống Render: {str(e)}", exc_info=True)
            return cls._generate_failsafe_document(str(e))

    @staticmethod
    def _generate_failsafe_document(error_msg: str) -> bytes:
        """
        Bảo hiểm cuối cùng: Đảm bảo Streamlit luôn nhận được một file hợp lệ,
        chứa log lỗi chi tiết để kỹ thuật viên dễ dàng debug thay vì crash app.
        """
        err_doc = docx.Document()
        err_doc.add_heading("⚠️ SỰ CỐ KẾT XUẤT TÀI LIỆU", level=1)
        err_doc.add_paragraph("Hệ thống phát hiện lỗi trong cấu trúc dữ liệu hoặc công thức LaTeX:")
        
        p = err_doc.add_paragraph()
        run = p.add_run(error_msg)
        run.font.color.rgb = docx.shared.RGBColor(255, 0, 0)
        
        bio = io.BytesIO()
        err_doc.save(bio)
        bio.seek(0)
        return bio.getvalue()
