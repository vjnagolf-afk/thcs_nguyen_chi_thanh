# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_mo_phong(ai_engine=None):
    st.markdown("### 🧪 Trợ lý Sinh Mã Mô Phỏng Thí Nghiệm")
    st.caption("AI hỗ trợ viết mã HTML/JavaScript/CSS hoặc tạo kịch bản để xây dựng các thí nghiệm ảo, mô phỏng hiện tượng Vật lí, Hóa học, Sinh học.")
    
    with st.container(border=True):
        st.info("💡 Tính năng Đang phát triển: Giáo viên nhập mô tả hiện tượng, AI sẽ xuất ra đoạn mã HTML nhúng để học sinh có thể kéo thả, tương tác trực tiếp trên trình duyệt.")
        
        mon_hoc = st.selectbox("Chọn môn học:", ["Vật lí", "Hóa học", "Sinh học", "Toán học"], disabled=True)
        hien_tuong = st.text_area("Mô tả hiện tượng cần mô phỏng (VD: Con lắc lò xo, Mạch điện RLC, Chu trình quang hợp):", disabled=True, height=100)
        
        st.button("⚙️ Sinh mã mô phỏng tương tác", type="primary", disabled=True, use_container_width=True)
