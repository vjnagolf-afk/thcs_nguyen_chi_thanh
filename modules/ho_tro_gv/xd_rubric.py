# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_rubric(ai_engine=None):
    st.markdown("### 📊 Trợ lý Xây dựng Rubric Đánh Giá")
    st.caption("Thiết kế ma trận tiêu chí đánh giá (Rubric) chi tiết cho các bài thuyết trình, dự án học tập, hoặc bài luận theo hướng phát triển phẩm chất, năng lực.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: AI sinh ra các bảng tiêu chí định lượng (Mức 1, 2, 3, 4) kèm mô tả hành vi rõ ràng để giáo viên chấm điểm khách quan.")
        
        loai_nhiem_vu = st.selectbox("Loại nhiệm vụ đánh giá:", ["Dự án học tập (Project)", "Bài thuyết trình", "Bài viết luận/Nghị luận", "Hoạt động thực hành/Thí nghiệm"], disabled=True)
        yeu_cau_can_dat = st.text_area("Yêu cầu cần đạt (Mục tiêu):", disabled=True, height=100)
        
        st.button("✨ Xây dựng Rubric", type="primary", disabled=True, use_container_width=True)
