import streamlit as st
from utils.db_connector import db
from utils.ai_engine import AIEngine

# Import các phân hệ
# Sửa lại phần import trong app.py
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
from modules.ho_tro_giang_day.rag_ask import render_rag

# Khởi tạo AI Engine
ai_engine = AIEngine(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(page_title="Hệ sinh thái số", layout="wide")

# --- 1. SIDEBAR: ĐIỀU HƯỚNG ---
with st.sidebar:
    st.title("⚙️ HỆ THỐNG")
    
    # Menu chọn phân hệ chính
    phan_he = st.radio("CHỌN PHÂN HỆ", [
        "Quản lý Tổ chuyên môn", 
        "Hỗ trợ Giảng dạy", 
        "Hỗ trợ Giáo viên"
    ])
    
    st.markdown("---")
    
    # Khai báo sub_menu mặc định
    sub_menu = None
    
    # Logic chọn sub_menu dựa trên phan_he
    if phan_he == "Quản lý Tổ chuyên môn":
        sub_menu = st.selectbox("Chức năng:", ["Danh sách thành viên", "Phân công", "Biên bản"])
    elif phan_he == "Hỗ trợ Giảng dạy":
        sub_menu = st.selectbox("Chức năng:", ["Hỏi-Đáp (RAG)", "Chấm bài", "Mô phỏng"])
    elif phan_he == "Hỗ trợ Giáo viên":
        sub_menu = st.selectbox("Chức năng:", ["XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM"])

    # Admin Gate
    st.markdown("---")
    if st.checkbox("🛡️ Quản trị (Admin)"):
        from modules.admin.user_management import render_user_management
        render_user_management()

# --- 2. MAIN BODY: HIỂN THỊ NỘI DUNG ---
if phan_he == "Quản lý Tổ chuyên môn":
    if sub_menu == "Danh sách thành viên": 
        render_danh_sach()
    elif sub_menu == "Phân công": 
        render_phan_cong(db)
    elif sub_menu == "Biên bản": 
        render_bien_ban(db)

elif phan_he == "Hỗ trợ Giảng dạy":
    if sub_menu == "Hỏi-Đáp (RAG)":
        render_rag(ai_engine) 
    else:
        st.info(f"Đang phát triển chức năng: {sub_menu}")

elif phan_he == "Hỗ trợ Giáo viên":
    st.info(f"Đang phát triển phân hệ: {sub_menu}")
