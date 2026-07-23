# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_chuyen_doi(ai_engine=None):
    st.markdown("### 🔄 Trợ lý Chuyển đổi Định dạng & Xử lý Tài liệu")
    st.caption("Công cụ siêu tốc giúp giáo viên chuyển đổi qua lại giữa PDF, Word, Excel, nhận diện văn bản (OCR) từ ảnh.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Trích xuất bảng biểu từ PDF sang Excel, lấy chữ từ ảnh chụp sách giáo khoa.")
        
        loai_chuyen_doi = st.radio(
            "Chọn thao tác:",
            ["PDF sang Word", "Ảnh sang Văn bản (OCR)", "Tách bảng từ PDF sang Excel"],
            horizontal=True,
            disabled=True
        )
        st.file_uploader("Tải tài liệu gốc lên đây:", disabled=True)
        st.button("⚙️ Thực thi Chuyển đổi", type="primary", disabled=True, use_container_width=True)
