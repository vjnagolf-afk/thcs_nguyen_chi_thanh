# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
from pathlib import Path

# Cấu hình đường dẫn
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import các thư viện/phân hệ (giữ nguyên các import của thầy)
from utils.db_connector import db
from utils.ai_engine import AIEngine
from views.xd_khbd_view import render_xd_khbd
# ... (giữ nguyên tất cả các import khác) ...

# ========================================== #
# CẤU HÌNH TRANG
# ========================================== #
st.set_page_config(page_title="Hệ sinh thái số", layout="wide", page_icon="🏫")

# Hàm kiểm tra API Key
def validate_key(key: str) -> bool:
    k = key.strip()
    return k.startswith(("AIza", "sk-ant-", "sk-"))

def get_ai_engine_instance():
    # ... (Giữ nguyên hàm khởi tạo engine của thầy) ...
    if st.session_state.get("ai_engine_instance"): return st.session_state.ai_engine_instance
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

# ========================================== #
# KHỞI TẠO TRẠNG THÁI
# ========================================== #
if "user_api_key" not in st.session_state: st.session_state.user_api_key = None
if "is_admin_mode" not in st.session_state: st.session_state.is_admin_mode = False

# ========================================== #
# GIAO DIỆN CHÍNH
# ========================================== #
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #E63946;'>HỆ SINH THÁI SỐ</h2>", unsafe_allow_html=True)
    
    # Chỉ hiển thị menu chọn phân hệ nếu đã đăng nhập
    if st.session_state.user_api_key or st.session_state.is_admin_mode:
        phan_he = st.radio("Chọn phân hệ:", ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy", "Quản lý Tổ chuyên môn"])
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    else:
        phan_he = None

# ========================================== #
# CỔNG BẢO MẬT (Gatekeeper)
# ========================================== #
if not st.session_state.user_api_key and not st.session_state.is_admin_mode:
    st.info("🔑 Vui lòng nhập API Key / Mật khẩu hệ thống để bắt đầu.")
    with st.form("login"):
        key_input = st.text_input("Nhập API Key / Mật khẩu:", type="password")
        submit = st.form_submit_button("Xác nhận đăng nhập")
        if submit:
            admin_password = st.secrets.get("ADMIN_PASSWORD", "admin123456")
            if key_input.strip() == admin_password:
                st.session_state.is_admin_mode = True
                st.rerun()
            elif validate_key(key_input):
                st.session_state.user_api_key = key_input.strip()
                st.rerun()
            else:
                st.error("❌ API Key không đúng!")
    st.stop() # Dừng toàn bộ code bên dưới nếu chưa đăng nhập

# ========================================== #
# NỘI DUNG SAU KHI ĐĂNG NHẬP (Chỉ chạy khi đã login)
# ========================================== #
ai_engine = get_ai_engine_instance()

if phan_he == "Hỗ trợ Giáo viên":
    # ... (Các tab của Giáo viên) ...
    pass
elif phan_he == "Hỗ trợ Giảng dạy":
    # ... (Các tab của Giảng dạy) ...
    pass
elif phan_he == "Quản lý Tổ chuyên môn":
    # ... (Các tab của Tổ chuyên môn) ...
    pass
