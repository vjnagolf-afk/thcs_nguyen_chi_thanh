# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_tao_hoc_lieu(ai_engine=None):
    st.markdown("### 📚 Trợ lý Thiết kế Học liệu Đa phương tiện")
    st.caption("Tự động sinh nội dung cho Flashcard, Handout, tóm tắt lý thuyết, hoặc kịch bản Slide thuyết trình.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Rút gọn kiến thức dài thành các dạng học liệu dễ tiêu hóa cho học sinh.")
        
        loai_hoc_lieu = st.selectbox("Định dạng đầu ra:", ["Bộ thẻ ghi nhớ (Flashcard Q&A)", "Kịch bản Slide (PowerPoint)", "Phiếu học tập (Handout)", "Sơ đồ tư duy (Text)"], disabled=True)
        noi_dung_goc = st.text_area("Dán nội dung kiến thức gốc vào đây:", disabled=True, height=150)
        
        st.button("🪄 Tạo Học Liệu", type="primary", disabled=True, use_container_width=True)
