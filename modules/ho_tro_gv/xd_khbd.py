import streamlit as st
from loguru import logger
from pypdf import PdfReader

# CHUẨN KIẾN TRÚC: Import tuyệt đối tự nhiên từ gốc dự án nhìn xuống sau khi đã xóa __init__.py gốc
from export.export_word import WordExportEngine

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # Khởi tạo bộ nhớ tạm để tránh mất dữ liệu khi UI reload (st.rerun)
    if 'khbd_content' not in st.session_state:
        st.session_state['khbd_content'] = None
    if 'khbd_meta' not in st.session_state:
        st.session_state['khbd_meta'] = {}
    if 'khbd_word_bytes' not in st.session_state:
        st.session_state['khbd_word_bytes'] = None

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
    lop = col2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
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
        else:
            with st.spinner("⏳ AI đang quét tài liệu và thiết kế giáo án..."):
                file_context = ""
                if file_tai_len and bam_sat:
                    try:
                        if file_tai_len.name.endswith('.pdf'):
                            reader = PdfReader(file_tai_len)
                            file_context = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                        elif file_tai_len.name.endswith('.txt'):
                            file_context = file_tai_len.read().decode("utf-8")
                    except Exception as e:
                        st.warning(f"Không thể đọc tài liệu: {e}")

                # Prompt thiết kế giáo án định hình cấu trúc đầu ra chuẩn
                prompt = f"""
                Bạn là một chuyên gia giáo dục. Hãy soạn KHBD cho bài học: '{ten_bai_hoc}'.
                Thông tin: Môn {mon_hoc}, lớp {lop}, {so_tiet} tiết, hình thức {hinh_thuc}.

                YÊU CẦU PHÂN TÍCH:
                1. Tìm kiếm và trích xuất nội dung liên quan trực tiếp đến bài '{ten_bai_hoc}' trong tài liệu tham khảo được cung cấp bên dưới.
                2. Lồng ghép nội dung Năng lực số và giáo dục AI vào các hoạt động.
                3. {yeu_cau}

                YÊU CẦU TRÌNH BÀY:
                1. Bắt đầu ngay từ "I. MỤC TIÊU". Không có lời chào.
                2. Sử dụng LaTeX ($...$) cho mọi công thức toán học/hóa học.
                3. Không sử dụng dấu ">" đầu dòng.

                Dữ liệu tài liệu tham khảo:
                {file_context[:8000]}
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['khbd_content'] = content
                    st.session_state['khbd_meta'] = {"ten": ten_bai_hoc, "mon": mon_hoc, "lop": lop}
                    st.session_state['khbd_word_bytes'] = None  # Reset file Word cũ khi tạo bài mới
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    if c2.button("🗑️ XÓA DỮ LIỆU", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # 3. HIỂN THỊ KẾT QUẢ VÀ LOGIC GỐC 2 BƯỚC XUẤT FILE WORD
    if st.session_state.get('khbd_content'):
        st.markdown("---")
        st.markdown(st.session_state['khbd_content'])
        
        # Logic nút bấm xuất file chuẩn nguyên bản của thầy
        if st.button("📥 Xuất file Word", use_container_width=True):
            with st.spinner("⏳ Hệ thống đang đóng gói văn bản OpenXML..."):
                try:
                    # Chạy hàm đóng gói chính thức từ Engine dùng chung của dự án
                    word_bytes = WordExportEngine.export_to_word({
                        "ai_generated_content": st.session_state['khbd_content'],
                        "is_khbd": True
                    })
                    
                    st.session_state['khbd_word_bytes'] = word_bytes
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi kết xuất văn bản Word: {e}")
                    logger.exception("Lỗi xuất Word")
        
        # Nếu đã có dữ liệu đóng gói trong phiên -> Hiển thị nút tải file về máy
        if st.session_state.get('khbd_word_bytes'):
            file_name_clean = st.session_state['khbd_meta'].get('ten', 'Giao_An').replace(' ', '_')
            st.download_button(
                label="Tải file về máy",
                data=st.session_state['khbd_word_bytes'],
                file_name=f"KHBD_{file_name_clean}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
