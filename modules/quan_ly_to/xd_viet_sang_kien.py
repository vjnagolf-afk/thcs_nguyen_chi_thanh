import streamlit as st

def render_viet_sang_kien(ai_engine):
    st.markdown("### ✍️ Trợ lý Viết Sáng kiến Kinh nghiệm")
    
    # 1. Tải tài liệu hướng dẫn & Dữ liệu thực tế
    with st.expander("📥 Tải tài liệu nền tảng"):
        huong_dan = st.file_uploader("Tải công văn/quy định cấu trúc:", type=["pdf", "docx"])
        du_lieu = st.file_uploader("Tải minh chứng/số liệu thực tế:", type=["xlsx", "docx", "pdf"])
    
    # 2. Nhập bối cảnh (Prompt Engineering)
    col1, col2 = st.columns(2)
    with col1:
        nam_hoc = st.text_input("Năm học:")
        doi_tuong = st.text_input("Đối tượng/Lớp:")
    with col2:
        mon_hoc = st.text_input("Môn học:")
        chu_de = st.text_input("Tên đề tài:")

    # 3. Lệnh cho AI
    if st.button("🚀 Phác thảo dàn ý & Viết nội dung"):
        # Logic: AI đọc file huong_dan và du_lieu để tạo nội dung
        # Yêu cầu AI đóng vai chuyên gia giáo dục, viết theo bố cục: 
        # Đặt vấn đề -> Nội dung nghiên cứu -> Hiệu quả sáng kiến
        st.info("AI đang xử lý, vui lòng kiểm tra lại tính nguyên gốc sau khi nhận kết quả.")
