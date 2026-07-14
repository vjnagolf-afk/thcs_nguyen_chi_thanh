import streamlit as st
from utils.db_connector import db
from utils.ai_engine import AIEngine

# Import các phân hệ
from modules.quan_ly_to import danh_sach, phan_cong, bien_ban, ke_hoach, thi_dua
from modules.ho_tro_giang_day import rag_ask # ... và các file khác
from modules.ho_tro_gv import xd_khbd # ... và các file khác

st.set_page_config(page_title="Hệ sinh thái số", layout="wide")

# --- 1. GATEKEEPER & AUTH ---
# Giả định đã tích hợp Auth, ở đây em check email để phân quyền Admin
user_email = "vjnagolf@gmail.com" # Thay bằng logic lấy user thực tế

with st.sidebar:
    st.title("⚙️ HỆ THỐNG")
    
    # Menu chọn phân hệ chính
    phan_he = st.radio("CHỌN PHÂN HỆ", [
        "Quản lý Tổ chuyên môn", 
        "Hỗ trợ Giảng dạy", 
        "Hỗ trợ Giáo viên"
    ])
    
    st.markdown("---")
    
    # Điều hướng chi tiết dựa trên phân hệ chọn
    if phan_he == "Quản lý Tổ chuyên môn":
        sub_menu = st.selectbox("Chức năng:", ["Danh sách thành viên", "Phân công", "Biên bản", "Kế hoạch", "Thi đua"])
    elif phan_he == "Hỗ trợ Giảng dạy":
        sub_menu = st.selectbox("Chức năng:", ["Hỏi-Đáp (RAG)", "Chấm bài", "Mô phỏng", "Ngân hàng đề", "Camera chấm bài"])
    else:
        sub_menu = st.selectbox("Chức năng:", ["XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM", "Rubric", "Quản lý điểm"])

    # Admin Gate
    if user_email == "vjnagolf@gmail.com":
        if st.checkbox("🛡️ Quản trị (Admin)"):
            from modules.admin.user_management import render_user_management
            render_user_management()

# --- 2. ĐIỀU HƯỚNG LOGIC ---
if phan_he == "Quản lý Tổ chuyên môn":
    if sub_menu == "Danh sách thành viên": danh_sach.render()
    elif sub_menu == "Phân công": phan_cong.render(db)
    elif sub_menu == "Biên bản": bien_ban.render(db)
    # ... các case khác
