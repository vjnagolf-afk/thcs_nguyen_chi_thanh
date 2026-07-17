# -*- coding: utf-8 -*-
import streamlit as st
import sys
from pathlib import Path

# Cấu hình trang
st.set_page_config(page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh", layout="wide", page_icon="🏫")

# Cấu hình đường dẫn
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import các module
from utils.db_connector import db
from utils.ai_engine import AIEngine
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
from modules.ho_tro_giao_vien.xd_khbd import render_xd_khbd
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_giang_day.xd_tro_choi import render_xd_tro_choi
from modules.ho_tro_giang_day.xd_cham_nhanh import render_xd_cham_nhanh
from modules.ho_tro_giang_day.xd_hoc_lieu import render_xd_hoc_lieu

# Khởi tạo engine (Giả sử thầy đã có hàm get_ai_engine_instance)
ai_engine = AIEngine() 

# Sidebar
with st.sidebar:
    phan_he = st.radio("Chọn phân hệ:", ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy", "Quản lý Tổ chuyên môn"])

# Routing (Phần quan trọng nhất thầy hay bị lỗi)
if phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 👩‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs_gv = st.tabs(["XD KHBD", "XD Đề KT", "STEM", "Rubric", "Chủ nhiệm", "Chấm bài", "Tạo prompt", "Quizizz", "Mô phỏng"])
    with tabs_gv[0]:
        render_xd_khbd(ai_engine)

elif phan_he == "Hỗ trợ Giảng dạy":
    st.markdown("## 🪴 Phân hệ: Hỗ trợ Giảng dạy")
    tabs_gd = st.tabs(["Hỏi-Đáp (RAG)", "Trò chơi", "Chấm bài", "Học liệu"])
    with tabs_gd[0]:
        render_rag(ai_engine)
    with tabs_gd[1]:
        render_xd_tro_choi(ai_engine)
    with tabs_gd[2]:
        render_xd_cham_nhanh(ai_engine)
    with tabs_gd[3]:
        render_xd_hoc_lieu(ai_engine)

elif phan_he == "Quản lý Tổ chuyên môn":
    st.markdown("## 📊 Phân hệ: Quản lý Tổ chuyên môn")
    tabs_to = st.tabs(["Danh sách", "Phân công", "Biên bản"])
    with tabs_to[0]:
        render_danh_sach()
    with tabs_to[1]:
        render_phan_cong(db)
    with tabs_to[2]:
        render_bien_ban(db)
