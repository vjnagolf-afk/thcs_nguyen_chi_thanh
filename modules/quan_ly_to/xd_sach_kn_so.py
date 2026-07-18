import streamlit as st

def render_sach_kn_so():
    st.markdown("### 📘 Tủ sách Kỹ năng số cho Giáo viên")
    st.caption("Kho tài liệu, cẩm nang hướng dẫn ứng dụng công nghệ thông tin và AI vào công tác giảng dạy.")
    
    # Chia giao diện thành 3 cột để trưng bày sách
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🤖 Cẩm nang AI")
        st.info("""
        - Hướng dẫn cơ bản sử dụng ChatGPT
        - Kỹ năng viết Prompt sư phạm
        - Ứng dụng Gemini trong soạn giảng KHBD
        """)
        st.button("📖 Đọc tài liệu", key="doc_ai", type="primary", use_container_width=True)
        
    with col2:
        st.markdown("#### 🖥️ Công cụ Tương tác")
        st.success("""
        - Hướng dẫn tạo Quizizz / Kahoot
        - Tổ chức lớp học với Padlet
        - Sử dụng phòng thí nghiệm ảo (PhET)
        """)
        st.button("📖 Đọc tài liệu", key="doc_tt", type="primary", use_container_width=True)
        
    with col3:
        st.markdown("#### 📊 Quản trị Lớp học")
        st.warning("""
        - Quản lý điểm số nâng cao với Excel
        - Xây dựng hồ sơ số, Google Classroom
        - Bảo mật thông tin học sinh
        """)
        st.button("📖 Đọc tài liệu", key="doc_ql", type="primary", use_container_width=True)
        
    st.markdown("---")
    st.markdown("#### 🔍 Tìm kiếm tài liệu khác")
    tim_kiem = st.text_input("Nhập từ khóa tài liệu bạn muốn tìm (VD: Canva, PowerPoint...):")
    if tim_kiem:
        st.write(f"Đang tìm kiếm tài liệu liên quan đến: **{tim_kiem}**... (Tính năng kết nối kho lưu trữ đang hoàn thiện)")
