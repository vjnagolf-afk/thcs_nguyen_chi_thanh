# -*- coding: utf-8 -*-
"""
============================================================
ĐIỀU HƯỚNG TRUNG TÂM DỰ ÁN: NGUYỄN CHÍ THANH
FILE: app.py
============================================================
"""

import streamlit as st
import os
import sys

# Thêm thư mục gốc vào hệ thống path để đảm bảo import tuyệt đối chính xác
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import các tầng tiện ích, cơ sở dữ liệu và AI Engine
try:
    from utils.db_connector import init_db
    from utils.ai_engine import AIEngine
except ImportError:
    # Fallback an toàn nếu chưa khởi tạo đầy đủ
    init_db = None
    AIEngine = None

# Import các phân hệ giao diện chính
try:
    from modules.quan_ly_to.danh_sach import render_danh_sach
    from modules.quan_ly_to.phan_cong import render_phan_cong
    from modules.quan_ly_to.bien_ban import render_bien_ban
    from modules.quan_ly_to.xd_ke_hoach import render_ke_hoach
    from modules.quan_ly_to.xd_kiem_tra_khbd import render_kiem_tra_khbd
    from modules.quan_ly_to.xd_cham_sang_kien import render_cham_sang_kien
    from modules.quan_ly_to.xd_viet_sang_kien import render_viet_sang_kien
    from modules.quan_ly_to.xd_sach_kn_so import render_sach_kn_so
    from modules.quan_ly_to.xd_thi_dua import render_thi_dua
    from modules.quan_ly_to.xd_tkb import render_tkb
    from modules.quan_ly_to.xd_tom_tat_gmail import render_tom_tat_gmail
except ImportError as e:
    st.error(f"❌ Lỗi import phân hệ Quản lý tổ chuyên môn: {e}")

try:
    from views.ung_dung_khac import render_ung_dung_khac
    from views.xd_de_kt_view import render_xd_de_kt
    from views.xd_khbd_view import render_xd_khbd
    from views.xd_ma_tran_tu_de import render_xd_ma_tran_tu_de
except ImportError as e:
    st.error(f"❌ Lỗi import các View phân hệ bổ trợ: {e}")

# ============================================================
# CẤU HÌNH TRANG STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Hệ thống Quản lý & Hỗ trợ Chuyên môn - Nguyễn Chí Thanh",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# KHỞI TẠO BỘ NHỚ TRẠNG THÁI & AI ENGINE
# ============================================================
def init_global_state():
    if "db" not in st.session_state:
        try:
            st.session_state.db = init_db() if init_db else None
        except Exception:
            st.session_state.db = None

    if "ai_engine" not in st.session_state:
        try:
            st.session_state.ai_engine = AIEngine() if AIEngine else None
        except Exception:
            st.session_state.ai_engine = None

    if "danh_sach_gv" not in st.session_state:
        st.session_state.danh_sach_gv = []

init_global_state()

# ============================================================
# THANH ĐIỀU HƯỚNG CHÍNH (SIDEBAR)
# ============================================================
st.sidebar.markdown("## 🏫 TRƯỜNG THCS NGUYỄN CHÍ THANH")
st.sidebar.caption("Hệ thống Trợ lý AI Quản lý & Chuyên môn Tổ KHTN")
st.sidebar.divider()

menu_category = st.sidebar.radio(
    "📂 Chọn phân hệ:",
    [
        "👥 Quản lý Tổ chuyên môn",
        "📘 Xây dựng & Thẩm định KHBD",
        "📝 Đề kiểm tra & Ma trận",
        "🧩 Ma trận ngược từ Đề",
        "🛠️ Ứng dụng khác"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Cấu hình API & Hệ thống")
user_api_key_input = st.sidebar.text_input("Nhập Gemini API Key cá nhân:", type="password", key="user_api_key")
if user_api_key_input:
    st.sidebar.success("✅ Đã ghi nhận API Key cá nhân!")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Hệ thống vận hành chuẩn:** Bám sát công văn 5512, Thông tư 18 và chuẩn khảo thí giáo dục phổ thông mới.")

# ============================================================
# ĐIỀU HƯỚNG NỘI DUNG (ROUTING)
# ============================================================
db_instance = st.session_state.get("db")
ai_instance = st.session_state.get("ai_engine")

if menu_category == "👥 Quản lý Tổ chuyên môn":
    st.markdown("## 👥 Phân hệ: Quản lý Tổ chuyên môn")
    sub_tab = st.tabs([
        "Danh sách GV", 
        "Phân công", 
        "Thời khóa biểu", 
        "Biên bản họp", 
        "Kế hoạch chuyên đề", 
        "Kiểm tra KHBD", 
        "Chấm sáng kiến", 
        "Viết sáng kiến", 
        "Tóm tắt Email", 
        "Tủ sách số", 
        "Thi đua"
    ])
    
    with sub_tab[0]:
        try: render_danh_sach()
        except NameError: st.warning("Module Danh sách chưa sẵn sàng.")
    with sub_tab[1]:
        try: render_phan_cong(db_instance)
        except NameError: st.warning("Module Phân công chưa sẵn sàng.")
    with sub_tab[2]:
        try: render_tkb(db_instance)
        except NameError: st.warning("Module Thời khóa biểu chưa sẵn sàng.")
    with sub_tab[3]:
        try: render_bien_ban(ai_instance)
        except NameError: st.warning("Module Biên bản chưa sẵn sàng.")
    with sub_tab[4]:
        try: render_ke_hoach()
        except NameError: st.warning("Module Kế hoạch chuyên đề chưa sẵn sàng.")
    with sub_tab[5]:
        try: render_kiem_tra_khbd(ai_instance)
        except NameError: st.warning("Module Kiểm tra KHBD chưa sẵn sàng.")
    with sub_tab[6]:
        try: render_cham_sang_kien(ai_instance)
        except NameError: st.warning("Module Chấm sáng kiến chưa sẵn sàng.")
    with sub_tab[7]:
        try: render_viet_sang_kien(ai_instance)
        except NameError: st.warning("Module Viết sáng kiến chưa sẵn sàng.")
    with sub_tab[8]:
        try: render_tom_tat_gmail(ai_instance)
        except NameError: st.warning("Module Tóm tắt Gmail chưa sẵn sàng.")
    with sub_tab[9]:
        try: render_sach_kn_so()
        except NameError: st.warning("Module Tủ sách số chưa sẵn sàng.")
    with sub_tab[10]:
        try: render_thi_dua()
        except NameError: st.warning("Module Thi đua chưa sẵn sàng.")

elif menu_category == "📘 Xây dựng & Thẩm định KHBD":
    try:
        render_xd_khbd(ai_instance)
    except Exception as e:
        st.error(f"Lỗi hiển thị phân hệ KHBD: {e}")

elif menu_category == "📝 Đề kiểm tra & Ma trận":
    try:
        render_xd_de_kt(ai_instance)
    except Exception as e:
        st.error(f"Lỗi hiển thị phân hệ Đề kiểm tra: {e}")

elif menu_category == "🧩 Ma trận ngược từ Đề":
    try:
        render_xd_ma_tran_tu_de(ai_instance)
    except Exception as e:
        st.error(f"Lỗi hiển thị phân hệ Ma trận ngược: {e}")

elif menu_category == "🛠️ Ứng dụng khác":
    try:
        render_ung_dung_khac()
    except Exception as e:
        st.error(f"Lỗi hiển thị phân hệ Ứng dụng khác: {e}")
