# -*- coding: utf-8 -*-
import streamlit as st

from .the_01_tao_prompt import render_the_01
from .the_02_embed_hub import render_the_02
from .the_03_xu_ly_video import render_the_03  # <-- Import Thẻ 3

def render_ung_dung_khac(ai_engine=None):
    st.markdown("## 🛠️ Phân hệ: Ứng dụng khác")
    st.divider()

    # Cập nhật tên các thẻ chức năng
    tab_titles = [
        "🎮 Tạo prompt trò chơi", 
        "🌐 Nhúng YouTube & Canva", 
        "🎬 Xử lý Video & YouTube", # <-- Tên Thẻ 3
        "Thẻ 4", "Thẻ 5", 
        "Thẻ 6", "Thẻ 7", "Thẻ 8", "Thẻ 9", "Thẻ 10"
    ]
    
    tabs = st.tabs(tab_titles)

    # Thẻ số 1
    with tabs[0]:
        render_the_01(ai_engine)

    # Thẻ số 2
    with tabs[1]:
        render_the_02(ai_engine)

    # Thẻ số 3: Gọi hàm xử lý video
    with tabs[2]:
        render_the_03(ai_engine)

    # Các thẻ từ 4 đến 10 (Khung chờ)
    for idx in range(3, 10):
        with tabs[idx]:
            st.markdown(f"### 📌 Không gian làm việc: Thẻ chức năng số {idx + 1}")
            st.write(f"Thầy đang thao tác trên giao diện của **Thẻ {idx + 1}** trong phân hệ Ứng dụng khác.")
            with st.container(border=True):
                st.info(f"Khu vực tính năng cho Thẻ {idx + 1} sẽ được phát triển tiếp theo.")
