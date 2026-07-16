# =========================================================================
# MODULE: export/export_word.py
# Nhiệm vụ: Lớp điều phối trung tâm (Facade Pattern) chuẩn hành chính
# CHUẨN KIẾN TRÚC: Gọi tuyệt đối từ gốc dự án nhìn xuống, không file phụ, không importlib
# =========================================================================
import io
import logging
from typing import Dict, Any
import docx

# Cấu hình logging tiêu chuẩn hệ thống
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WordExportEngine")

class WordExportEngine:
    """
    Điểm truy cập duy nhất (Entry point) cho toàn bộ hệ thống xuất file Word.
    Tuyệt đối không chứa logic xử lý chuỗi hay vẽ bảng trực tiếp tại đây.
    """

    @classmethod
    def export_to_word(cls, data_cache: Dict[str, Any]) -> bytes:
        """
        Tiếp nhận dữ liệu thô từ Streamlit, phân rã qua AST và phân phối render file Word.
        """
        try:
            logger.info("Khởi động tiến trình kết xuất tài liệu Word...")
            doc = docx.Document()

            # =========================================================================
            # NHẬP KHẨU TRỄ (LAZY IMPORTS) CHUẨN KIẾN TRÚC TUYỆT ĐỐI GỐC DỰ ÁN
            # Giải quyết dứt điểm lỗi Circular Import và lỗi nạp Package trên Cloud
            # =========================================================================
            from export.word_markdown import MarkdownTokenizer
            from export.word_math import MathRenderer
            from export.word_styles import StyleManager
            from export.word_tables import TableRenderer
            from export.word_images import ImageRenderer  # Đã sửa: Nạp đầy đủ để chống lỗi NameError

            # 1. KHỞI TẠO ĐỊNH DẠNG CHUẨN (A4, Margins, Base Fonts)
            StyleManager.setup_base_styles(doc)

            # Lấy dữ liệu cốt lõi thô từ AI gửi qua data_cache
            ai_text = data_cache.get("ai_generated_content", "")
            is_khbd = data_cache.get("is_khbd", False)

            # 2. XỬ LÝ CÁC THÀNH PHẦN TĨNH PHÂN HỆ ĐẶC THÙ (Nghiệp vụ sư phạm)
            if is_khbd:
                logger.info("Render cấu trúc tĩnh: Kế hoạch bài dạy (KHBD)")
                TableRenderer.build_khbd_header(doc, data_cache)
            else:
                logger.info("Render cấu trúc tĩnh: Ma trận và Đặc tả")
                TableRenderer.build_matrix_table(doc, data_cache, StyleManager, MathRenderer)
                doc.add_paragraph()
                TableRenderer.build_specification_table(doc, data_cache, StyleManager, MathRenderer)
                doc.add_paragraph()

            # 3. PHÂN TÍCH CÚ PHÁP MẠNH (AST GENERATION)
            logger.info("Đang phân tích cú pháp Markdown và LaTeX (Tokenizer)...")
            ast_nodes = MarkdownTokenizer.parse(ai_text)

            # 4. KẾT XUẤT ĐỘNG TOÀN DIỆN (AST RENDERING)
            logger.info(f"Bắt đầu render {len(ast_nodes)} AST Nodes...")
            for node in ast_nodes:
                node_type = node.get("type")
                
                if node_type == "paragraph":
                    StyleManager.render_paragraph(doc, node, MathRenderer)
                    
                elif node_type == "heading":
                    StyleManager.render_heading(doc, node, MathRenderer)
                    
                elif node_type == "list_item":
                    StyleManager.render_list_item(doc, node, MathRenderer)
                    
                elif node_type == "checkbox":
                    StyleManager.render_checkbox(doc, node, MathRenderer)
                    
                elif node_type == "callout":
                    StyleManager.render_callout(doc, node, TableRenderer, MathRenderer)
                    
                elif node_type == "code":  # Đã đồng bộ: Đổi từ 'code_block' sang 'code' khớp 1:1 với Tokenizer
                    StyleManager.render_code_block(doc, node)
                    
                elif node_type == "table":
                    TableRenderer.render_ast_table(doc, node, StyleManager, MathRenderer)
                    
                elif node_type == "image":
                    ImageRenderer.render_image(doc, node)
                    
                elif node_type == "hr":  # Bổ sung: Tự động vẽ đường kẻ vách ngăn paragraph border nâng cao
                    StyleManager.render_hr(doc)
                    
                elif node_type == "page_break":
                    doc.add_page_break()
                    
                elif node_type in ["inline_math", "display_math"]:  # Đồng bộ các khối phương trình lớn
                    MathRenderer.render_display_math(doc, node.get("content", ""))
                    
                else:
                    logger.warning(f"Bỏ qua Node không xác định: {node_type}")

            # 5. LƯU TRỮ VÀ XUẤT LUỒNG BYTES NHỊ PHÂN
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            logger.info("Tiến trình kết xuất văn bản Word hoàn tất thành công.")
            return bio.getvalue()

        except Exception as e:
            logger.error(f"Lỗi nghiêm trọng sập hệ thống Render: {str(e)}", exc_info=True)
            return cls._generate_failsafe_document(str(e))

    @staticmethod
    def _generate_failsafe_document(error_msg: str) -> bytes:
        """
        Bảo hiểm cuối cùng: Tạo file Word báo cáo lỗi OpenXML chi tiết thay vì làm treo sập ứng dụng web.
        """
        from docx.shared import RGBColor  # Đã sửa: Nạp trực tiếp tại runtime để chống NameError
        
        err_doc = docx.Document()
        err_doc.add_heading("⚠️ SỰ CỐ KẾT XUẤT TÀI LIỆU", level=1)
        err_doc.add_paragraph("Hệ thống phát hiện lỗi trong cấu trúc dữ liệu hoặc công thức định dạng:")
        
        p = err_doc.add_paragraph()
        run = p.add_run(f"Chi tiết mã lỗi: {error_msg}")
        run.bold = True
        run.font.size = docx.shared.Pt(11)
        run.font.color.rgb = RGBColor(255, 0, 0) # Ép màu đỏ cảnh báo hành chính
        
        bio = io.BytesIO()
        err_doc.save(bio)
        bio.seek(0)
        return bio.getvalue()
