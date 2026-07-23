# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_quizizz(ai_engine=None):
    st.markdown("### ⚡ Trợ lý Tạo tệp Import Quizizz / Kahoot / Blooket")
    st.caption("Chuyển đổi văn bản, đề cương ôn tập hoặc ảnh chụp thành định dạng Excel/CSV chuẩn để tải thẳng lên các nền tảng trò chơi học tập.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Tiết kiệm hàng giờ nhập liệu thủ công bằng cách để AI đọc đề bài và tự động điền vào template Excel mẫu của Quizizz/Kahoot.")
        
        st.file_uploader("Tải lên file đề bài (Word/PDF/Ảnh):", disabled=True)
        st.selectbox("Nền tảng đích:", ["Quizizz (Excel)", "Kahoot (Excel)", "Blooket (CSV)"], disabled=True)
        
        st.button("🚀 Chuyển đổi siêu tốc", type="primary", disabled=True, use_container_width=True)
