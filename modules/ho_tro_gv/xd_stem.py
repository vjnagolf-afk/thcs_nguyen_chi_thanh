# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_stem(ai_engine=None):
    st.markdown("### 🚀 Thiết kế Kế hoạch Bài học STEM / STEAM")
    st.caption("AI hỗ trợ lên ý tưởng, thiết kế tiến trình 5 bước (Tiêu chí - Tưởng tượng - Chế tạo - Thử nghiệm - Cải tiến) cho các chủ đề giáo dục STEM.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Cung cấp bài toán thực tiễn, AI sẽ đề xuất vật liệu, quy trình kỹ thuật và câu hỏi định hướng cho học sinh.")
        
        van_de_thuc_tien = st.text_input("Vấn đề thực tiễn cần giải quyết (VD: Làm sao để lọc nước đục thành nước trong?):", disabled=True)
        c2, c3 = st.columns(2)
        with c2:
            st.text_input("Môn học chủ đạo:", disabled=True)
        with c3:
            st.text_input("Vật liệu dự kiến:", disabled=True)
            
        st.button("🛠️ Thiết kế Tiến trình STEM", type="primary", disabled=True, use_container_width=True)
