import streamlit as st
from utils.db_connector import db
from modules.management.bien_ban import render_bien_ban

# Cấu hình trang
st.set_page_config(page_title="Hệ sinh thái số", layout="wide")

# Sidebar cấu hình
with st.sidebar:
    st.title("⚙️ Cấu hình")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        st.session_state['gemini_api_key'] = api_key
        st.success("Đã nạp API Key!")

# Điều hướng chính
menu = st.sidebar.radio("CHỌN PHÂN HỆ", ["Quản lý Tổ chuyên môn", "Hỗ trợ Giảng dạy"])

if menu == "Quản lý Tổ chuyên môn":
    # Gọi trực tiếp module từ thư mục modules/management
    render_bien_ban(db) # Truyền 'db' vào thay vì 'supabase'
