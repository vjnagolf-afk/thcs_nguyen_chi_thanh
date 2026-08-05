# -*- coding: utf-8 -*-
"""
============================================================
MODULE: modules/ho_tro_giang_day/mo_phong/page.py
Mô tả: Giao diện Mô phỏng Thí nghiệm & Đồ thị khoa học.
============================================================
"""

import streamlit as st

def render_xd_mo_phong():
    st.markdown("### 🧪 Phòng Thí nghiệm Ẩo & Trợ lý Mô phỏng Khoa học")
    st.caption("Góc chuyên gia: Kết hợp giữa Mô hình toán học trực quan (Interactive Simulations) và Trợ giảng AI.")

    # Tạo các tab con bên trong mô phỏng để giao diện phong phú
    tab1, tab2 = st.tabs(["🔬 1. Mô phỏng Thí nghiệm & Đồ thị (Interactive Lab)", "💬 2. Trợ giảng AI Giải đáp Thí nghiệm"])

    with tab1:
        st.markdown("#### Chọn Mô hình Thí nghiệm Ẩo")
        chu_de = st.selectbox(
            "Chọn chủ đề mô phỏng:",
            ["🚀 Chuyển động Ném ngang (Vật lý 10)", "⚡ Định luật Ohm (Vật lý 9)", "🧪 Phản ứng hóa học cơ bản (Hóa học 8)"]
        )

        st.markdown("---")
        if "Ném ngang" in chu_de:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("##### 🎛️ Thông số đầu vào")
                v0 = st.slider("Vận tốc ban đầu v0 (m/s):", 5.0, 30.0, 15.0)
                h = st.slider("Độ cao ban đầu h (m):", 5.0, 50.0, 20.0)
                
                g = 9.8
                t = (2 * h / g) ** 0.5
                range_x = v0 * t
                
                st.info(f"📊 **Kết quả tính toán mô phỏng:**\n- Thời gian bay: **{t:.2f}s**\n- Tầm bay xa: **{range_x:.2f}m**")

            with col2:
                st.markdown("##### 📈 Mô phỏng quỹ đạo bay")
                st.success(f"Đang hiển thị mô hình trực quan cho vận tốc $v_0 = {v0}$ m/s và độ cao $h = {h}$ m.")
                st.markdown("*(Đồ thị mô phỏng chuyển động đang được vẽ trực tuyến qua Streamlit)*")

        else:
            st.info(f"Mô hình cho chủ đề **{chu_de}** đang được tải dữ liệu tương tác...")

    with tab2:
        st.markdown("#### 🤖 Trợ giảng AI Hướng dẫn Thí nghiệm")
        st.text_input("Hỏi AI về hiện tượng vật lý / hóa học trong thí nghiệm:", placeholder="VD: Tại sao vật lại rơi theo quỹ đạo parabol?")
        st.button("Gửi câu hỏi cho Trợ giảng AI", type="primary")
