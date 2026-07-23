# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_chu_nhiem(ai_engine=None):
    st.markdown("### 👨‍👩‍👧‍👦 Trợ lý Công tác Chủ nhiệm")
    st.caption("AI hỗ trợ phân tích tâm lý học sinh, đề xuất kịch bản họp phụ huynh và xử lý các tình huống sư phạm khó.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Tư vấn tâm lý học đường, viết báo cáo hạnh kiểm, lên kịch bản sinh hoạt lớp.")
        
        chu_de = st.selectbox(
            "Chọn nhóm tình huống cần hỗ trợ:",
            ["Xử lý vi phạm kỷ luật", "Tư vấn tâm lý học đường", "Kịch bản họp Phụ huynh", "Xây dựng phong trào lớp"],
            disabled=True
        )
        st.text_area("Mô tả chi tiết tình huống hiện tại:", disabled=True, height=100)
        st.button("🧠 AI Đề xuất hướng giải quyết", type="primary", disabled=True, use_container_width=True)
