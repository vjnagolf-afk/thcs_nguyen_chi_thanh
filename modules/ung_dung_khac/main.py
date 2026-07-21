# -*- coding: utf-8 -*-
import streamlit as st

# Import từng thẻ chức năng từ các file con trong thư mục
from .the_01_tao_prompt import render_the_01

def render_ung_dung_khac(ai_engine=None):
    st.markdown("## 🛠️ Phân hệ: Ứng dụng khác")
    st.divider()

    # Danh sách tên 10 thẻ chức năng
    tab_titles = [
        "🎮 Tạo prompt trò chơi", 
        "Thẻ 2", "Thẻ 3", "Thẻ 4", "Thẻ 5", 
        "Thẻ 6", "Thẻ 7", "Thẻ 8", "Thẻ 9", "Thẻ 10"
    ]
    
    tabs = st.tabs(tab_titles)

    # Thẻ số 1: Gọi hàm từ file the_01_tao_prompt.py
    with tabs[0]:
        render_the_01(ai_engine)

    # Các thẻ từ 2 đến 10 (tạm thời để khung chờ)
    for idx in range(1, 10):
        with tabs[idx]:
            st.markdown(f"### 📌 Không gian làm việc: Thẻ chức năng số {idx + 1}")
            st.write(f"Thầy đang thao tác trên giao diện của **Thẻ {idx + 1}** trong phân hệ Ứng dụng khác.")
            with st.container(border=True):
                st.info(f"Khu vực tính năng cho Thẻ {idx + 1} sẽ được phát triển tại file `the_{idx+1:02d}_...py`.")
