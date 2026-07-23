# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_live_v1(ai_engine=None):
    st.markdown("### 🔴 Lớp học Live (Phiên bản V1)")
    st.caption("Bản dự phòng giao diện lớp học trực tuyến phiên bản 1.0.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Phiên bản cổ điển của hệ thống phòng học Live. Tạm thời được giữ lại làm bản dự phòng (Fallback) khi nâng cấp hệ thống.")
        st.button("Vào phòng Live V1", type="primary", disabled=True)
