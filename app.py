# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os

# 1. CẤU HÌNH ĐƯỜNG DẪN
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 2. IMPORT THƯ VIỆN & CẤU HÌNH TRANG
from utils.db_connector import db
from utils.ai_engine import AIEngine
from utils.ai_engine_2 import AIEngine2

st.set_page_config(page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh", layout="wide", page_icon="🏫")

# 3. IMPORT CÁC MODULE PHÂN HỆ
# Phân hệ Hỗ trợ Giáo viên
from views.xd_khbd_view import render_xd_khbd
from views.xd_de_kt_view import render_xd_de_kt
from modules.ho_tro_gv.xd_stem import render_xd_stem
from modules.ho_tro_gv.xd_rubric import render_xd_rubric
from modules.ho_tro_gv.xd_chu_nhiem import render_xd_chu_nhiem
from modules.ho_tro_gv.xd_cham_viet import render_xd_cham_viet
from modules.ho_tro_gv.xd_tao_prompt import render_xd_tao_prompt
from modules.ho_tro_gv.xd_quizizz import render_xd_quizizz
from modules.ho_tro_gv.xd_live import render_xd_live
from modules.ho_tro_gv.xd_chuyen_doi import render_xd_chuyen_doi
from modules.ho_tro_gv.xd_tao_hoc_lieu import render_tao_hoc_lieu

try:
    from modules.ho_tro_gv.xd_chuyen_doi import render_xd_chuyen_doi
except ImportError:
    render_xd_chuyen_doi = None
    st.sidebar.error("❌ Lỗi: Không tìm thấy file xd_chuyen_doi.py")
# Phân hệ Hỗ trợ Giảng dạy
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_giang_day.xd_tro_choi import render_xd_tro_choi
from modules.ho_tro_giang_day.xd_cham_nhanh import render_xd_cham_nhanh
from modules.ho_tro_giang_day.xd_hoc_lieu import render_xd_tuong_tac
from modules.ho_tro_giang_day.xd_mo_phong import render_xd_mo_phong
from modules.ho_tro_giang_day.mo_phong.page import render_mo_phong
from modules.ho_tro_giang_day.xd_phan_tich import render_xd_phan_tich
from modules.ho_tro_giang_day.xd_ngan_hang_de import render_xd_ngan_hang_de
from modules.ho_tro_giang_day.xd_sinh_video import render_xd_sinh_video
from modules.ho_tro_giang_day.xd_camera import render_camera_module
from modules.ho_tro_giang_day.xd_ca_nhan_hoa import render_xd_ca_nhan_hoa
from modules.ho_tro_giang_day.xd_phan_tich_bh import render_phan_tich_bh
from modules.ho_tro_giang_day.xd_kiem_tra_nhanh import render_kiem_tra_nhanh
# Phân hệ Quản lý Tổ chuyên môn
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
from modules.quan_ly_to.xd_ke_hoach import render_ke_hoach
from modules.quan_ly_to.xd_thi_dua import render_thi_dua
from modules.quan_ly_to.xd_kiem_tra_khbd import render_kiem_tra_khbd
from modules.quan_ly_to.xd_sach_kn_so import render_sach_kn_so
from modules.quan_ly_to.xd_tom_tat_gmail import render_tom_tat_gmail
from modules.quan_ly_to.xd_viet_sang_kien import render_viet_sang_kien
from modules.quan_ly_to.xd_cham_sang_kien import render_cham_sang_kien

# 4. HÀM CẤU HÌNH ENGINE
def get_ai_engine_instance():
    if "ai_engine_instance" not in st.session_state:
        keys = {}
        if st.session_state.is_admin_mode:
            keys["gemini"] = st.secrets.get("GEMINI_API_KEY")
            keys["openai"] = st.secrets.get("OPENAI_API_KEY")
        else:
            k = st.session_state.user_api_key
            if k: keys["gemini" if k.startswith("AIza") else "openai"] = k
        keys = {k: v for k, v in keys.items() if v}
        st.session_state.ai_engine_instance = AIEngine(keys=keys) if keys else None
    return st.session_state.ai_engine_instance

def get_ai_engine_2_instance():
    if "ai_engine_2_instance" not in st.session_state:
        key = st.secrets.get("OPENROUTER_API_KEY")
        st.session_state.ai_engine_2_instance = AIEngine2(api_key=key) if key else None
    return st.session_state.ai_engine_2_instance

# 5. KHỞI TẠO STATE
if "user_api_key" not in st.session_state: st.session_state.user_api_key = None
if "is_admin_mode" not in st.session_state: st.session_state.is_admin_mode = False

# 6. GIAO DIỆN CHÍNH
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #E63946;'>HỆ SINH THÁI SỐ</h2>", unsafe_allow_html=True)
    if st.session_state.user_api_key or st.session_state.is_admin_mode:
        phan_he = st.radio("Chọn phân hệ:", ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy", "Quản lý Tổ chuyên môn"])
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    else: phan_he = None

if not phan_he:
    st.info("🔑 Vui lòng đăng nhập để bắt đầu.")
    # ... [Giữ nguyên logic form đăng nhập cũ của thầy]
    st.stop()

# 7. RENDER
try:
    ai_engine = get_ai_engine_instance()
    ai_engine_2 = get_ai_engine_2_instance()

# ========================================================
    # PHÂN HỆ 1: HỖ TRỢ GIÁO VIÊN
    # ========================================================
    if phan_he == "Hỗ trợ Giáo viên":
        st.markdown("## 👩‍🏫 Phân hệ: Hỗ trợ Giáo viên")
        tabs = st.tabs(["XD KHBD", "XD ĐỀ KT", "STEM", "RUBRIC", "CHỦ NHIỆM", "KT KĨ NĂNG VIẾT", "PROMPT", "QUIZIZZ", "MÔ PHỎNG TN", "LIVE", "T.LIỆU SANG KHBD", "TẠO HỌC LIỆU"])
        
        with tabs[0]: render_xd_khbd(ai_engine)
        with tabs[1]: render_xd_de_kt(ai_engine)
        with tabs[2]: render_xd_stem(ai_engine)
        with tabs[3]: render_xd_rubric(ai_engine)
        with tabs[4]: render_xd_chu_nhiem(ai_engine)
        with tabs[5]: render_xd_cham_viet(ai_engine)
        with tabs[6]: render_xd_tao_prompt(ai_engine)
        with tabs[7]: render_xd_quizizz(ai_engine)
        with tabs[8]: render_mo_phong(ai_engine)
        with tabs[9]: render_xd_live(ai_engine)
        with tabs[10]: render_chuyen_doi(ai_engine)
        with tabs[11]: render_tao_hoc_lieu(ai_engine)

    # ========================================================
    # PHÂN HỆ 2: HỖ TRỢ GIẢNG DẠY
    # ========================================================
    elif phan_he == "Hỗ trợ Giảng dạy":
        st.markdown("## 🪴 Phân hệ: Hỗ trợ Giảng dạy")
        tabs = st.tabs(["Hỏi đáp", "Trò chơi", "Chấm bài", "Tóm tắt tài liệu", "Mô phỏng LT TN ảo", "Phân tích KQ học tập", "Tạo đề nhanh", "Tạo Video", "Camera chấm bài", "Cá nhân hóa", "Phân tích bài học", "Tương tác trên lớp"])
        
        with tabs[0]: render_rag(ai_engine)
        with tabs[1]: render_xd_tro_choi(ai_engine)
        with tabs[2]: render_xd_cham_nhanh(ai_engine)
        with tabs[3]: render_xd_tuong_tac(ai_engine)
        with tabs[4]: render_xd_mo_phong(ai_engine)
        with tabs[5]: render_xd_phan_tich(ai_engine)
        with tabs[6]: render_xd_ngan_hang_de(ai_engine)
        with tabs[7]: render_xd_sinh_video(ai_engine)
        with tabs[8]: render_camera_module() # Không cần tham số
        with tabs[9]: render_xd_ca_nhan_hoa(ai_engine)
        with tabs[10]: render_phan_tich_bh(ai_engine)
        with tabs[11]: render_kiem_tra_nhanh(ai_engine)

    # ========================================================
    # PHÂN HỆ 3: QUẢN LÝ TỔ CHUYÊN MÔN
    # ========================================================
    elif phan_he == "Quản lý Tổ chuyên môn":
        st.markdown("## 📊 Phân hệ: Quản lý Tổ chuyên môn")
        tabs = st.tabs(["Danh sách", "Phân công", "Biên bản", "Chuyên đề", "Thi đua", "Kiểm tra KHBD", "Kỹ năng số", "Tóm tắt Gmail", "Viết sáng kiến", "Chấm sáng kiến"])
        
        with tabs[0]: render_danh_sach()
        with tabs[1]: render_phan_cong(db)
        with tabs[2]: render_bien_ban(db)
        with tabs[3]: render_ke_hoach()
        with tabs[4]: render_thi_dua()
        with tabs[5]: render_kiem_tra_khbd(ai_engine)
        with tabs[6]: render_sach_kn_so()
        with tabs[7]: render_tom_tat_gmail(ai_engine)
        with tabs[8]: render_viet_sang_kien(ai_engine_2)
        with tabs[9]: render_cham_sang_kien(ai_engine_2)

except Exception as e:
    st.error("🚨 Lỗi hệ thống!")
    st.exception(e)
