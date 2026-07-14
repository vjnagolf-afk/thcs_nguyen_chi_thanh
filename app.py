import streamlit as st
from utils.db_connector import db
from modules.management.danh_sach import render_danh_sach
from modules.management.phan_cong import render_phan_cong
from modules.management.bien_ban import render_bien_ban

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="Hệ sinh thái số", layout="wide")

# 2. LẤY THÔNG TIN NGƯỜI DÙNG (Cần có bước đăng nhập của Supabase)
# Trong Streamlit, ta dùng st.experimental_user để lấy thông tin email từ phiên đăng nhập
user = st.experimental_user 

# 3. SIDEBAR CHỨC NĂNG
with st.sidebar:
    st.title("⚙️ Hệ thống")
    
    # Kiểm tra trạng thái đăng nhập
    if not user.is_logged_in:
        st.warning("Vui lòng đăng nhập để sử dụng hệ thống.")
        st.stop()
    
    # Lấy email từ user object
    user_email = user.email
    st.write(f"👤 Chào thầy/cô: **{user_email}**")

    # MENU ĐIỀU HƯỚNG
    menu = st.radio("CHỌN PHÂN HỆ", ["Danh sách", "Phân công", "Biên bản"])

    # PHÂN QUYỀN ADMIN (Cửa ải)
    if user_email == "vjnagolf@gmail.com": 
        if st.checkbox("🛡️ Quản trị (Admin)"):
            from modules.admin.user_management import render_user_management
            render_user_management()

# 4. ĐIỀU HƯỚNG CHÍNH
if menu == "Danh sách":
    render_danh_sach()
elif menu == "Phân công":
    render_phan_cong(db)
elif menu == "Biên bản":
    render_bien_ban(db)
