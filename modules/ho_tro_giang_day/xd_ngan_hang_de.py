import streamlit as st
import io
from docx import Document

def render_xd_ngan_hang_de(ai_engine):
    st.markdown("### 🗂️ Trợ lý Sinh & Quản lý Ngân hàng Đề")
    st.info("💡 Hỗ trợ tạo tự động câu hỏi trắc nghiệm, tự luận theo ma trận năng lực từ văn bản hoặc chủ đề cho trước.")

    if "ngan_hang_de_result" not in st.session_state:
        st.session_state.ngan_hang_de_result = ""

    col1, col2, col3 = st.columns(3)
    with col1:
        mon_hoc = st.selectbox("Môn học:", ["Toán", "Ngữ Văn", "Tiếng Anh", "KHTN (Lý, Hóa, Sinh)", "Lịch sử & Địa lý", "Tin học", "Công nghệ", "GDCD", "Khác"])
    with col2:
        khoi_lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
    with col3:
        hinh_thuc = st.selectbox("Hình thức câu hỏi:", ["Trắc nghiệm (4 lựa chọn)", "Tự luận", "Trắc nghiệm Đúng/Sai", "Kết hợp (Trắc nghiệm + Tự luận)"])

    chu_de = st.text_area(
        "Chủ đề hoặc Nội dung bài học (Paste văn bản bài học hoặc gõ từ khóa):",
        height=150,
        placeholder="Ví dụ: Định lý Vi-et, Hoặc dán toàn bộ nội dung bài học vào đây..."
    )

    st.markdown("**Cấu trúc Ma trận đề (Số lượng câu hỏi):**")
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        so_luong_nb = st.number_input("Mức Nhận biết:", min_value=0, max_value=50, value=4)
    with col5:
        so_luong_th = st.number_input("Mức Thông hiểu:", min_value=0, max_value=50, value=3)
    with col6:
        so_luong_vd = st.number_input("Mức Vận dụng:", min_value=0, max_value=20, value=2)
    with col7:
        so_luong_vdc = st.number_input("Mức VD cao:", min_value=0, max_value=20, value=1)

    st.markdown("---")

    if st.button("🚀 SINH NGÂN HÀNG CÂU HỎI", type="primary"):
        tong_so_cau = so_luong_nb + so_luong_th + so_luong_vd + so_luong_vdc
        if not chu_de.strip():
            st.warning("⚠️ Vui lòng nhập Chủ đề hoặc dán Nội dung bài học!")
        elif tong_so_cau == 0:
            st.warning("⚠️ Vui lòng chọn ít nhất 1 câu hỏi ở các mức độ!")
        else:
            with st.spinner(f"⏳ AI đang soạn {tong_so_cau} câu hỏi theo ma trận..."):
                prompt = f"""Đóng vai là một giáo viên {mon_hoc} giỏi cấp THCS, hãy soạn một bộ câu hỏi {hinh_thuc} cho học sinh {khoi_lop} dựa trên nội dung/chủ đề sau:
                
                NỘI DUNG/CHỦ ĐỀ:
                {chu_de}
                
                YÊU CẦU MA TRẬN ĐỀ:
                - Mức độ Nhận biết: {so_luong_nb} câu
                - Mức độ Thông hiểu: {so_luong_th} câu
                - Mức độ Vận dụng: {so_luong_vd} câu
                - Mức độ Vận dụng cao: {so_luong_vdc} câu
                
                YÊU CẦU ĐẦU RA:
                1. Trình bày rõ ràng phần CÂU HỎI.
                2. Nếu là câu hỏi trắc nghiệm, các đáp án A, B, C, D phải có độ nhiễu tốt.
                3. BẮT BUỘC cung cấp ĐÁP ÁN CHI TIẾT và GIẢI THÍCH ở phần cuối cùng của tài liệu.
                """
                try:
                    res = ai_engine.generate_text(prompt)
                    st.session_state.ngan_hang_de_result = res
                except Exception as e:
                    st.error(f"Lỗi khi gọi AI: {e}")

    # Hiển thị kết quả và tạo nút Tải Word
    if st.session_state.ngan_hang_de_result:
        st.markdown("### 📝 Bộ câu hỏi & Đáp án")
        st.markdown(st.session_state.ngan_hang_de_result)
        
        # --- ĐOẠN CODE TẠO FILE WORD ĐỂ TẢI XUỐNG ---
        st.markdown("---")
        doc = Document()
        doc.add_heading(f'Ngân hàng đề - Môn {mon_hoc} - {khoi_lop}', 0)
        
        # Ghi nội dung kết quả vào file Word
        doc.add_paragraph(st.session_state.ngan_hang_de_result)
        
        # Lưu file vào bộ nhớ đệm (BytesIO) để tải xuống
        bio = io.BytesIO()
        doc.save(bio)
        
        st.download_button(
            label="💾 Tải xuống file Word (.docx)",
            data=bio.getvalue(),
            file_name=f"Ngan_Hang_De_{mon_hoc}_{khoi_lop}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary"
        )
