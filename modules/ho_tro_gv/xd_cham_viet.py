# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_cham_viet(ai_engine=None):
    st.markdown("### 📝 Trợ lý Chấm & Chữa bài Tự luận/Viết")
    st.caption("AI hỗ trợ đọc ảnh bài làm của học sinh, nhận diện chữ viết tay và chấm điểm dựa trên Rubric hoặc đáp án chuẩn.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Cho phép tải lên file ảnh bài làm (JPG/PNG), AI sẽ đọc (OCR), chỉ ra lỗi sai và đưa ra nhận xét chi tiết.")
        
        # Form khung nhập liệu chờ phát triển
        col1, col2 = st.columns([1, 2])
        with col1:
            st.file_uploader("Tải lên ảnh bài làm của học sinh:", type=["png", "jpg", "jpeg"], disabled=True)
        with col2:
            st.text_area("Nhập đáp án chuẩn hoặc tiêu chí chấm (Rubric):", disabled=True, height=100)
            
        st.button("🚀 Bắt đầu chấm bài", type="primary", disabled=True, use_container_width=True)
