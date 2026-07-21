# -*- coding: utf-8 -*-
import streamlit as st

from .the_01_tao_prompt import render_the_01
from .the_02_embed_hub import render_the_02  # <-- Import Thẻ 2

def render_ung_dung_khac(ai_engine=None):
    st.markdown("## 🛠️ Phân hệ: Ứng dụng khác")
    st.divider()

    # Đặt tên trực quan cho các thẻ
    tab_titles = [
        "🎮 Tạo prompt trò chơi", 
        "🌐 Nhúng YouTube & Canva", # <-- Đổi tên Thẻ 2
        "Thẻ 3", "Thẻ 4", "Thẻ 5", 
        "Thẻ 6", "Thẻ 7", "Thẻ 8", "Thẻ 9", "Thẻ 10"
    ]
    
    tabs = st.tabs(tab_titles)

    # Thẻ số 1: Tạo prompt trò chơi
    with tabs[0]:
        render_the_01(ai_engine)

    # Thẻ số 2: Nhúng YouTube & Canva
    with tabs[1]:
        render_the_02(ai_engine)

    # Các thẻ từ 3 đến 10 (Khung chờ phát triển)
    for idx in range(2, 10):
        with tabs[idx]:
            st.markdown(f"### 📌 Không gian làm việc: Thẻ chức năng số {idx + 1}")
            st.write(f"Thầy đang thao tác trên giao diện của **Thẻ {idx + 1}** trong phân hệ Ứng dụng khác.")
            with st.container(border=True):
                st.info(f"Khu vực tính năng cho Thẻ {idx + 1} sẽ được phát triển tiếp theo.")
