# -*- coding: utf-8 -*-
"""
============================================================
MODULE: views/ung_dung_khac.py
Nhiệm vụ: Giao diện tổng quản lý các tab của Phân hệ Ứng dụng khác.
============================================================
"""

import streamlit as st

# Import các thẻ chức năng
from modules.ung_dung_khac.the_01_tao_prompt import render_the_01
from modules.ung_dung_khac.the_02_embed_hub import render_the_02
from modules.ung_dung_khac.the_03_xu_ly_video import render_the_03
from modules.ung_dung_khac.the_04_quan_sat import render_the_04
from modules.ung_dung_khac.the_05_gvg import render_the_05

def render_ung_dung_khac(ai_engine=None):
    st.markdown("## 🛠️ Phân hệ: Ứng dụng khác")
def render_ung_dung_khac(ai_engine=None):
    st.markdown("## 🛠️ Phân hệ: Ứng dụng khác")
   
    # Khai báo danh sách các Tab
    tab_titles = [
        "🎮 Tạo prompt trò chơi", 
        "🌐 Nhúng YouTube & Canva", 
        "🎬 Xử lý Video & YouTube", 
        "👁️‍🗨️ Quan sát & Lắng nghe"
        "🏆 Xây dựng Biện pháp GVG"
    ]
    
    # Tạo các Tab trên giao diện
    tabs = st.tabs(tab_titles)
    
    # Bật công tắc cho từng Tab
    with tabs[0]:
        try:
            render_the_01(ai_engine)
        except Exception as e:
            st.error(f"Lỗi hiển thị Thẻ 1: {e}")
            
    with tabs[1]:
        try:
            render_the_02(ai_engine)
        except Exception as e:
            st.error(f"Lỗi hiển thị Thẻ 2: {e}")
            
    with tabs[2]:
        try:
            render_the_03(ai_engine)
        except Exception as e:
            st.error(f"Lỗi hiển thị Thẻ 3: {e}")
            
    with tabs[3]:
        try:
            render_the_04(ai_engine)
        except Exception as e:
            st.error(f"Lỗi hiển thị Thẻ 4: {e}")
