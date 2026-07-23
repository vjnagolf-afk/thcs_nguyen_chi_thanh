# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_tao_prompt(ai_engine=None):
    st.markdown("### 🧠 Thư viện & Công cụ Sinh Prompt Sư phạm")
    st.caption("Tạo ra các câu lệnh (Prompt) chuẩn mực để giao tiếp hiệu quả với ChatGPT, Claude, Gemini trong các tình huống sư phạm cụ thể.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Kho lưu trữ các câu lệnh tối ưu giúp giáo viên khai thác AI một cách chuyên nghiệp nhất, tránh việc AI trả lời chung chung.")
        
        muc_dich = st.selectbox("Mục đích sử dụng AI:", ["Soạn giáo án", "Ra đề thi", "Tư vấn tâm lý", "Dịch thuật văn bản", "Lập trình"], disabled=True)
        chi_tiet = st.text_input("Chi tiết yêu cầu (VD: Ra 10 câu trắc nghiệm Sinh học lớp 9):", disabled=True)
        
        st.button("⚙️ Sinh Prompt Tối ưu", type="primary", disabled=True, use_container_width=True)
