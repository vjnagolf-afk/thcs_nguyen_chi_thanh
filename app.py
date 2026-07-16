import streamlit as st
from utils.db_connector import db
from utils.ai_engine import AIEngine

# Import các phân hệ
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_gv.xd_khbd import render_xd_khbd

# Cấu hình trang (Luôn đặt ở đầu)
st.set_page_config(page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh", layout="wide")

# Khởi tạo trạng thái cho API Key
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = None

# Hàm lấy Engine dựa trên ngữ cảnh (Cá nhân hay Admin)
def get_ai_engine():
    # Kiểm tra nếu là tác vụ Admin
    if st.session_state.get("is_admin_mode", False):
        admin_key = st.secrets.get("SCHOOL_ADMIN_API_KEY")
        return AIEngine(api_key=admin_key) if admin_key else None
    
    # Mặc định dùng Key cá nhân
    key = st.session_state.get("user_api_key")
    return AIEngine(api_key=key) if key else None

# ==========================================
# GIAO DIỆN SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: red;'>HỆ SINH THÁI SỐ</h2>", unsafe_allow_html=True)
    phan_he = st.radio("Chọn phân hệ:", ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy", "Quản lý Tổ chuyên môn"])
    
    st.markdown("---")
    if st.button("🚪 Đăng xuất/Đổi Key", use_container_width=True):
        st.session_state.user_api_key = None
        st.rerun()

# ==========================================
# CỔNG BẢO MẬT (LOGIN)
# ==========================================
if not st.session_state.user_api_key:
    st.warning("🔐 Vui lòng nhập API Key cá nhân để bắt đầu.")
    with st.form("login"):
        key = st.text_input("Nhập API Key:", type="password")
        if st.form_submit_button("Xác nhận"):
            st.session_state.user_api_key = key
            st.rerun()
    st.stop() # Dừng việc render các nội dung bên dưới nếu chưa có Key

# ==========================================
# KHỞI TẠO ENGINE & CHUYỂN HƯỚNG PHÂN HỆ
# ==========================================
ai_engine = get_ai_engine()

if phan_he == "Hỗ trợ Giáo viên":
    render_xd_khbd(ai_engine)
elif phan_he == "Hỗ trợ Giảng dạy":
    render_rag(ai_engine)
elif phan_he == "Quản lý Tổ chuyên môn":
    tab1, tab2, tab3 = st.tabs(["Danh sách", "Phân công", "Biên bản"])
    with tab1: 
        render_danh_sach()
    with tab2: 
        render_phan_cong(db)
    with tab3: 
        render_bien_ban(db)
