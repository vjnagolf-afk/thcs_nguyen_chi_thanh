import streamlit as st
import sys
from pathlib import Path
from loguru import logger
from pypdf import PdfReader

# Xóa bỏ dòng import gây lỗi ở đầu file này:
# from export.word_export_engine import WordExportEngine  <-- ĐÃ XÓA DÒNG NÀY ĐỂ TRÁNH LỖI CRASH 

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # Khởi tạo bộ nhớ tạm để tránh mất dữ liệu khi UI reload (st.rerun)
    if 'khbd_content' not in st.session_state:
        st.session_state['khbd_content'] = None
    if 'khbd_meta' not in st.session_state:
        st.session_state['khbd_meta'] = {}

    # 1. CẤU HÌNH GIAO DIỆN
    ds_mon = [
        "Ngữ văn", "Toán", "Ngoại ngữ", "Giáo dục công dân", "Lịch sử và Địa lý", 
        "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", "Công nghệ", 
        "Tin học", "Giáo dục thể chất", "Nghệ thuật", "Giáo dục địa phương", 
        "Hoạt động trải nghiệm, hướng nghiệp"
    ]

    # Hàng 1: Thông tin cơ bản
    col1, col2, col3, col4 = st.columns(4)
    mon_hoc = col1.selectbox("Môn học", ds_mon)
    lop = col2.selectbox("Lớp", [f"Lớp {i}" for i in range(6, 13)])
    hinh_thuc = col3.selectbox("Chọn hình thức", ["KHBD thu gọn", "Chuẩn 5512", "KHBD Stem"])
    so_tiet = col4.number_input("Số tiết", min_value=1, max_value=20, value=2)

    # Hàng 2: Tên bài và Tài liệu (QUAN TRỌNG)
    ten_bai_hoc = st.text_input(
        "Tên chủ đề / Tên bài học (AI sẽ tìm kiếm từ khóa này trong tài liệu)",
        value=st.session_state['khbd_meta'].get('ten', '')
    )
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=True)
    yeu_cau = st.text_area("Yêu cầu bổ sung cho AI (Ví dụ: Lồng ghép Năng lực số, tích hợp AI...)")
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])

    # 2. XỬ LÝ LOGIC TIẾN TRÌNH SOẠN BÀI
    c1, c2 = st.columns(2)
    
    if c1.button("🚀 KHỞI TẠO TIẾN TRÌNH", type="primary", use_container_width=True):
        if not ten_bai_hoc.strip():
            st.error("⚠️ Vui lòng nhập 'Tên chủ đề / Tên bài học' để AI thực hiện tìm kiếm!")
        elif not ai_engine:
            st.error("🔐 Hệ thống AI chưa được kết nối API Key!")
        else:
            with st.spinner("⏳ AI đang quét tài liệu và thiết kế giáo án chuyên sâu..."):
                file_context = ""
                if file_tai_len and bam_sat:
                    try:
                        if file_tai_len.name.endswith('.pdf'):
                            reader = PdfReader(file_tai_len)
                            file_context = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                        elif file_tai_len.name.endswith('.txt'):
                            file_context = file_tai_len.read().decode("utf-8")
                    except Exception as e:
                        st.warning(f"Không thể đọc tài liệu tham khảo: {e}")

                prompt = f"""
                Bạn là Chuyên gia Giáo dục cấp THCS và THPT. Hãy soạn một Kế hoạch bài dạy (KHBD) chi tiết cho bài học: '{ten_bai_hoc}'.
                Thông tin cấu trúc: Môn {mon_hoc}, {lop}, thời lượng {so_tiet} tiết, theo hình thức {hinh_thuc}.

                YÊU CẦU PHÂN TÍCH NỘI DUNG:
                1. Tìm kiếm và trích xuất nội dung liên quan trực tiếp đến bài '{ten_bai_hoc}' từ tài liệu tham khảo được cung cấp.
                2. Chủ động lồng ghép nội dung Năng lực số và ứng dụng giáo dục AI vào các hoạt động học tập.
                3. Yêu cầu bổ sung: {yeu_cau if yeu_cau.strip() else "Theo chuẩn khung đổi mới phương pháp dạy học."}

                YÊU CẦU ĐỊNH DẠNG (BẮT BUỘC):
                1. Bắt đầu ngay lập tức từ tiêu đề "I. MỤC TIÊU". Tuyệt đối không viết lời chào, lời dẫn thô hay giải thích bên ngoài.
                2. Sử dụng cú pháp LaTeX kẹp giữa cặp dấu $...$ cho toàn bộ các biểu thức, phương trình, công thức Toán học / Hóa học.
                3. Không sử dụng ký tự trích dẫn ">" ở đầu dòng.
                4. Sử dụng cấu trúc bảng Markdown dạng | Tiêu đề 1 | Tiêu đề 2 | cho các bảng ma trận hoạt động (nếu có).

                Dữ liệu tài liệu tham khảo đính kèm:
                {file_context[:12000]}
                """

                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['khbd_content'] = content
                    st.session_state['khbd_meta'] = {"ten": ten_bai_hoc, "mon": mon_hoc, "lop": lop}
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi phản hồi từ hệ thống AI: {e}")
                    logger.exception("Lỗi sinh KHBD")

    if c2.button("🗑️ XÓA DỮ LIỆU", use_container_width=True):
        st.session_state['khbd_content'] = None
        st.session_state['khbd_meta'] = {}
        st.rerun()

    # 3. HIỂN THỊ KẾT QUẢ VÀ TẢI FILE WORD NATIVE (.DOCX)
    if st.session_state['khbd_content']:
        st.markdown("---")
        
        col_title, col_download = st.columns()
        with col_title:
            st.markdown("#### 🎯 Bản phác thảo Kế hoạch bài dạy từ AI:")
        
        with col_download:
            try:
                # DI CHUYỂN IMPORT VÀO ĐÂY: Hàm sẽ tìm đúng thư mục export nhờ sys.path của app.py
                from export.word_export_engine import WordExportEngine
                
                # Biên dịch trực tiếp chuỗi Markdown sang luồng Bytes Word Native
                word_bytes = WordExportEngine.convert_markdown_to_docx_bytes(st.session_state['khbd_content'])
                
                file_name_clean = st.session_state['khbd_meta'].get('ten', 'Giao_An').replace(' ', '_')
                st.download_button(
                    label="📥 Tải file Word (.docx)",
                    data=word_bytes,
                    file_name=f"KHBD_{file_name_clean}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Lỗi đóng gói file Word: {e}")
                logger.exception("Lỗi xuất Word")

        st.markdown(st.session_state['khbd_content'])
