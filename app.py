import streamlit as st
import sys
from pathlib import Path

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN HỆ THỐNG (SỬA LỖI MODULE)
# Đảm bảo Streamlit Cloud nhận diện đúng thư mục gốc và thư mục export
# ==========================================
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Tiếp tục import các thư viện và phân hệ (Giữ nguyên 100% cấu trúc của bạn)
from utils.db_connector import db
from utils.ai_engine import AIEngine

# Import các phân hệ hiện có
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_gv.xd_khbd import render_xd_khbd

# Cấu hình trang (Luôn đặt ở đầu)
st.set_page_config(page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh", layout="wide")

# Khởi tạo trạng thái phiên làm việc
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = None
if "is_admin_mode" not in st.session_state:
    st.session_state.is_admin_mode = False

# Hàm lấy Engine dựa trên quyền Admin hoặc User
def get_ai_engine():
    if st.session_state.is_admin_mode:
        admin_key = st.secrets.get("SCHOOL_ADMIN_API_KEY")
        return AIEngine(api_key=admin_key) if admin_key else None
    else:
        key = st.session_state.get("user_api_key")
        return AIEngine(api_key=key) if key else None

# ==========================================
# GIAO DIỆN SIDEBAR
# ==========================================
with st.sidebar:
    # Tiêu đề Sidebar như ảnh gốc
    st.markdown("<h2 style='text-align: center; color: red;'>HỆ SINH THÁI SỐ<br>HỖ TRỢ GIÁO VIÊN</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h4 style='text-align: center; color: blue;'>CHỌN PHÂN HỆ</h4>", unsafe_allow_html=True)
    phan_he = st.radio(
        "Chọn phân hệ:", 
        ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy", "Quản lý Tổ chuyên môn"], 
        label_visibility="collapsed" # Ẩn label mặc định để dùng dòng CHỌN PHÂN HỆ ở trên
    )
    
    # Nút Admin và Đăng xuất ở cuối Sidebar
    st.markdown("<br>" * 10, unsafe_allow_html=True) # Đẩy phần dưới xuống thấp
    st.session_state.is_admin_mode = st.checkbox("🛡️ Quản trị (Admin)", value=st.session_state.is_admin_mode)
    if st.button("🚪 Đăng xuất/Đổi Key", use_container_width=True):
        st.session_state.user_api_key = None
        st.rerun()

# ==========================================
# CỔNG BẢO MẬT (LOGIN)
# ==========================================
if not st.session_state.user_api_key and not st.session_state.is_admin_mode:
    st.warning("🔑 Vui lòng nhập API Key cá nhân để bắt đầu.")
    with st.form("login"):
        key = st.text_input("Nhập API Key:", type="password")
        if st.form_submit_button("Xác nhận"):
            st.session_state.user_api_key = key
            st.rerun()
    st.stop()

# ==========================================
# KHỞI TẠO ENGINE & CHUYỂN HƯỚNG PHÂN HỆ
# ==========================================
ai_engine = get_ai_engine()

# PHÂN HỆ 1: HỖ TRỢ GIÁO VIÊN
if phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 👩‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs_gv = st.tabs(["XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM", "Rubric", "Chủ nhiệm", "Quản lý điểm", "Tạo prompt", "Quizizz", "Mô phỏng thực hành"])
    with tabs_gv[0]:
        render_xd_khbd(ai_engine)
    with tabs_gv[1]:
        st.info("Tính năng Xây dựng Đề kiểm tra đang được phát triển.")
    # Các tab còn lại chờ bổ sung code

# PHÂN HỆ 2: HỖ TRỢ GIẢNG DẠY
elif phan_he == "Hỗ trợ Giảng dạy":
    st.markdown("## 🪴 Hỗ trợ Giảng dạy")
    tabs_gd = st.tabs(["Hỏi-Đáp (RAG)", "Trò chơi", "Chấm bài", "Học liệu", "Mô phỏng", "Phân tích", "Ngân hàng đề", "Sinh Video", "Tương tác", "Cá nhân hóa"])
    with tabs_gd[0]:
        render_rag(ai_engine)
    with tabs_gd[1]:
        st.info("Tính năng Trò chơi đang được phát triển.")
    # Các tab còn lại chờ bổ sung code

# PHÂN HỆ 3: QUẢN LÝ TỔ CHUYÊN MÔN
elif phan_he == "Quản lý Tổ chuyên môn":
    st.markdown("## 📊 Phân hệ: Quản lý Tổ chuyên môn")
    tabs_to = st.tabs(["Danh sách thành viên", "Phân công", "Biên bản", "Kế hoạch", "Thi đua", "Kiểm tra KHBD"])
    with tabs_to[0]:
        render_danh_sach()
    with tabs_to[1]:
        render_phan_cong(db)
    with tabs_to[2]:
        render_bien_ban(db)
    with tabs_to[3]:
        st.info("Tính năng Kế hoạch đang được phát triển.")
    # Các tab còn lại chờ bổ sung code
