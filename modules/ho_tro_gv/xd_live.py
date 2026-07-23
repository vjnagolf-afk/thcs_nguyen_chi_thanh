# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_live(ai_engine=None):
    st.markdown("### 🔴 Lớp học Tương tác Trực tiếp (Live Class)")
    st.caption("Không gian dạy học trực tuyến kết hợp bảng trắng, bình chọn theo thời gian thực và trợ lý AI giám sát lớp học.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Yêu cầu kết nối WebRTC và WebSocket để duy trì trạng thái kết nối thời gian thực.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Tên phiên Live (Bài học):", disabled=True)
        with c2:
            st.text_input("Mã tham gia cho Học sinh:", value="ROOM-XYZ-123", disabled=True)
            
        st.button("🎥 Khởi tạo Phòng Live", type="primary", disabled=True, use_container_width=True)
