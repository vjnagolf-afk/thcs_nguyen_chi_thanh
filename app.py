# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
from pathlib import Path

# ========================================== #
# 1. CẤU HÌNH ĐƯỜNG DẪN & IMPORT (Đưa lên đầu)
# ========================================== #
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import các thư viện nội bộ
from utils.db_connector import db
from utils.ai_engine import AIEngine

# Import Phân hệ Giáo viên
from views.xd_khbd_view import render_xd_khbd
from views.xd_de_kt_view import render_xd_de_kt
from modules.ho_tro_gv.xd_stem import render_xd_stem
from modules.ho_tro_gv.xd_rubric import render_xd_rubric
from modules.ho_tro_gv.xd_chu_nhiem import render_xd_chu_nhiem
from modules.ho_tro_gv.xd_cham_viet import render_xd_cham_viet
from modules.ho_tro_gv.xd_tao_prompt import render_xd_tao_prompt
from modules.ho_tro_gv.xd_quizizz import render_xd_quizizz
from modules.ho_tro_gv.xd_mo_phong import render_xd_mo_phong
from modules.ho_tro_gv.xd_live import render_xd_live

# Import Phân hệ Giảng dạy
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_giang_day.xd_tro_choi import render_xd_tro_choi
from modules.ho_tro_giang_day.xd_cham_nhanh import render_xd_cham_nhanh
from modules.ho_tro_giang_day.xd_hoc_lieu import render_xd_hoc_lieu
from modules.ho_tro_giang_day.xd_mo_phong import render_xd_mo_phong
from modules.ho_tro_giang_day.xd_phan_tich import render_xd_phan_tich
from modules.ho_tro_giang_day.xd_ngan_hang_de import render_xd_ngan_hang_de
from modules.ho_tro_giang_day.xd_sinh_video import render_xd_sinh_video
from modules.ho_tro_giang_day.xd_tuong_tac import render_xd_tuong_tac
from modules.ho_tro_giang_day.xd_ca_nhan_hoa import render_xd_ca_nhan_hoa

# Import Phân hệ Tổ chuyên môn
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban

# ========================================== #
# 2. CẤU HÌNH TRANG
# ========================================== #
st.set_page_config(
    page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh",
    layout="wide",
    page_icon="🏫"
)

# ========================================== #
# 3. HÀM KHỞI TẠO ENGINE
# ========================================== #
if "user_api_key" not in st.session_state: st.session_state.user_api_key = None
if "is_admin_mode" not in st.session_state: st.session_state.is_admin_mode = False

def get_ai_engine_instance():
    if st.session_state.get("ai_engine_instance"): return st.session_state.ai_engine_instance
    keys = {}
    if st.session_state.is_admin_mode:
        keys["gemini"] = st.secrets.get("GEMINI_API_KEY")
        keys["openai"] = st.secrets.get("OPENAI_API_KEY")
        keys["claude"] = st.secrets.get("CLAUDE_API_KEY")
    else:
        k = st.session_state.user_api_key
        if k: keys["gemini" if k.startswith("AIza") else "openai"] = k

    keys = {k: v for k, v in keys.items() if v}
    st.session_state.ai_engine_instance = AIEngine(keys=keys) if keys else None
    return st.session_state.ai_engine_instance

# ========================================== #
# 4. GIAO DIỆN & ROUTING (Logic liên tục)
# ========================================== #
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #E63946;'>HỆ SINH THÁI SỐ</h2>", unsafe_allow_html=True)
    phan_he = st.radio("Chọn phân hệ:", ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy", "Quản lý Tổ chuyên môn"], label_visibility="collapsed")
    
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# Kiểm tra Login
if not st.session_state.user_api_key and not st.session_state.is_admin_mode:
    st.info("🔑 Vui lòng nhập API Key để bắt đầu.")
    st.stop()

# Khởi tạo engine sau khi login
ai_engine = get_ai_engine_instance()

# Routing không bị ngắt quãng
if phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 👩‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs_gv = st.tabs(["XD KHBD", "XD Đề KT", "STEM", "Rubric", "Chủ nhiệm", "Kỹ năng viết", "Prompt", "Quizizz", "Mô phỏng","Live"])
    with tabs_gv[0]: render_xd_khbd(ai_engine)
    with tabs_gv[1]: render_xd_de_kt(ai_engine)
    with tabs_gv[2]: render_xd_stem(ai_engine)
    with tabs_gv[3]: render_xd_rubric(ai_engine)
    with tabs_gv[4]: render_xd_chu_nhiem(ai_engine)
    with tabs_gv[5]: render_xd_cham_viet(ai_engine)
    with tabs_gv[6]: render_xd_tao_prompt(ai_engine)
    with tabs_gv[7]: render_xd_quizizz(ai_engine)
    with tabs_gv[8]: render_xd_mo_phong(ai_engine)
    with tabs_gv[9]: render_xd_live(ai_engine)

elif phan_he == "Hỗ trợ Giảng dạy":
    st.markdown("## 🪴 Phân hệ: Hỗ trợ Giảng dạy")
    tabs_gd = st.tabs(["RAG", "Trò chơi", "Chấm bài", "Học liệu", "Mô phỏng", "Phân tích", "Ngân hàng đề", "Video", "Tương tác", "Cá nhân"])
    with tabs_gd[0]: render_rag(ai_engine)
    with tabs_gd[1]: render_xd_tro_choi(ai_engine)
    with tabs_gd[2]: render_xd_cham_nhanh(ai_engine)
    with tabs_gd[3]: render_xd_hoc_lieu(ai_engine)
    with tabs_gd[4]: render_xd_mo_phong(ai_engine)
    with tabs_gd[5]: render_xd_phan_tich(ai_engine)
    with tabs_gd[6]: render_xd_ngan_hang_de(ai_engine)
    with tabs_gd[7]: render_xd_sinh_video(ai_engine)
    with tabs_gd[8]: render_xd_tuong_tac(ai_engine)
    with tabs_gd[9]: render_xd_ca_nhan_hoa(ai_engine)

elif phan_he == "Quản lý Tổ chuyên môn":
    st.markdown("## 📊 Phân hệ: Quản lý Tổ chuyên môn")
    tabs_to = st.tabs(["Danh sách", "Phân công", "Biên bản", "Kế hoạch", "Thi đua", "Kiểm tra KHBD"])
    with tabs_to[0]: render_danh_sach()
    with tabs_to[1]: render_phan_cong(db)
    with tabs_to[2]: render_bien_ban(db)
