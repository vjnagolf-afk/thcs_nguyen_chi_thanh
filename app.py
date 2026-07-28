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

# ============================================================
# IMPORT UTILS & AI ENGINE
# ============================================================
try:
    from utils.db_connector import init_db
    from utils.ai_engine import AIEngine
except ImportError:
    init_db = None
    AIEngine = None

# ============================================================
# IMPORT PHÂN HỆ 1: QUẢN LÝ TỔ CHUYÊN MÔN
# ============================================================
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

# ============================================================
# IMPORT PHÂN HỆ 2: HỖ TRỢ GIÁO VIÊN
# ============================================================
# Tách độc lập cơ chế import các file làm từ trước để bảo toàn hệ thống

# 1. Module KHBD
try:
    from views.xd_khbd_view import render_xd_khbd
except ImportError:
    try: from views.xd_khbd_view import render_xd_khbd_view as render_xd_khbd
    except ImportError: render_xd_khbd = None

# 2. Module Đề kiểm tra
try:
    from views.xd_de_kt_view import render_xd_de_kt
except ImportError:
    try: from views.xd_de_kt_view import render_xd_de_kt_view as render_xd_de_kt
    except ImportError: 
        try: from views.xd_de_kt_view import render_de_kt as render_xd_de_kt
        except ImportError: render_xd_de_kt = None

# 3. Module Ma trận
try:
    from views.xd_ma_tran_tu_de import render_xd_ma_tran_tu_de
except ImportError:
    try: from views.xd_ma_tran_tu_de import render_xd_ma_tran_tu_de_view as render_xd_ma_tran_tu_de
    except ImportError: render_xd_ma_tran_tu_de = None

# Các module Hỗ trợ Giáo viên mới
try:
    from modules.ho_tro_gv.xd_cham_viet import render_xd_cham_viet
    from modules.ho_tro_gv.xd_chu_nhiem import render_xd_chu_nhiem
    from modules.ho_tro_gv.xd_chuyen_doi import render_xd_chuyen_doi
    from modules.ho_tro_gv.xd_live import render_xd_live
    from modules.ho_tro_gv.xd_mo_phong import render_xd_mo_phong
    from modules.ho_tro_gv.xd_quizizz import render_xd_quizizz
    from modules.ho_tro_gv.xd_rubric import render_xd_rubric
    from modules.ho_tro_gv.xd_stem import render_xd_stem
    from modules.ho_tro_gv.xd_tao_hoc_lieu import render_xd_tao_hoc_lieu
    from modules.ho_tro_gv.xd_tao_prompt import render_xd_tao_prompt
except ImportError as e:
    st.error(f"❌ Lỗi import các tính năng Hỗ trợ Giáo viên: {e}")

# ============================================================
# IMPORT PHÂN HỆ 3: HỖ TRỢ GIẢNG DẠY
# ============================================================
try:
    from modules.ho_tro_giang_day.rag_ask import render_rag_ask
    from modules.ho_tro_giang_day.xd_ca_nhan_hoa import render_xd_ca_nhan_hoa
    from modules.ho_tro_giang_day.xd_camera import render_xd_camera
    from modules.ho_tro_giang_day.xd_cham_nhanh import render_xd_cham_nhanh
    from modules.ho_tro_giang_day.xd_hoc_lieu import render_xd_hoc_lieu
    from modules.ho_tro_giang_day.xd_kiem_tra_nhanh import render_xd_kiem_tra_nhanh
    from modules.ho_tro_giang_day.xd_ngan_hang_de import render_xd_ngan_hang_de
    from modules.ho_tro_giang_day.xd_phan_tich import render_xd_phan_tich
    from modules.ho_tro_giang_day.xd_phan_tich_bh import render_xd_phan_tich_bh
    from modules.ho_tro_giang_day.xd_sinh_video import render_xd_sinh_video
    from modules.ho_tro_giang_day.xd_tro_choi import render_xd_tro_choi
    from modules.ho_tro_giang_day.mo_phong.page import render_xd_mo_phong
except ImportError as e:
    st.error(f"❌ Lỗi import phân hệ Hỗ trợ Giảng dạy: {e}")

# ============================================================
# IMPORT PHÂN HỆ 4: ỨNG DỤNG KHÁC
# ============================================================
try:
    from views.ung_dung_khac import render_ung_dung_khac
except ImportError as e:
    st.error(f"❌ Lỗi import phân hệ Ứng dụng khác: {e}")

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
st.sidebar.caption("Hệ thống Trợ lý AI Quản lý & Chuyên môn")
st.sidebar.divider()

menu_category = st.sidebar.radio(
    "📂 BẢNG ĐIỀU KHIỂN CHÍNH:",
    [
        "👨‍🏫 Phân hệ Hỗ trợ Giáo viên",
        "🎓 Phân hệ Hỗ trợ Giảng dạy",
        "🛠️ Phân hệ Ứng dụng khác",
        "👥 Phân hệ Quản lý Tổ chuyên môn"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Cấu hình API & Hệ thống")
user_api_key_input = st.sidebar.text_input("Nhập Gemini API Key cá nhân:", type="password", key="user_api_key")
if user_api_key_input:
    st.sidebar.success("✅ Đã ghi nhận API Key cá nhân!")

st.sidebar.markdown("---")
# Hiển thị thông tin bản quyền chữ nhỏ, nghiêng, màu xanh dương
st.sidebar.markdown(
    """
    <div style='font-size: 0.85em; font-style: italic; color: #0056b3; text-align: left; line-height: 1.5;'>
        Tác giả: Lê Hồng Dưỡng.<br>
        Trường THCS Nguyễn Chí Thanh.
    </div>
    """, 
    unsafe_allow_html=True
)

# ============================================================
# ĐIỀU HƯỚNG NỘI DUNG (ROUTING)
# ============================================================
db_instance = st.session_state.get("db")
ai_instance = st.session_state.get("ai_engine")

# --- VƯỢT RÀO CHẶN GIAO DIỆN KHI CHƯA NHẬP KEY ---
if ai_instance is None:
    class DummyAIEngine:
        def generate_text(self, prompt, model_name=""):
            raise RuntimeError("Vui lòng nhập API Key hợp lệ ở menu bên trái để sử dụng tính năng này.")
    ai_instance = DummyAIEngine()
# --------------------------------------------------

# ------------------------------------------------------------
# 1. PHÂN HỆ HỖ TRỢ GIÁO VIÊN
# ------------------------------------------------------------
if menu_category == "👨‍🏫 Phân hệ Hỗ trợ Giáo viên":
    st.markdown("## 👨‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    
    tab_titles_gv = [
        "1. KHBD", "2. Đề kiểm tra", "3. Ma trận từ đề", 
        "4. Chấm viết", "5. Chủ nhiệm", "6. Chuyển đổi", 
        "7. Live", "8. Mô phỏng", "9. Quizizz", 
        "10. Rubric", "11. STEM", "12. Tạo học liệu/Prompt"
    ]
    tabs_gv = st.tabs(tab_titles_gv)
    
    with tabs_gv[0]:
        if render_xd_khbd: render_xd_khbd(ai_instance)
        else: st.warning("🚧 Hệ thống tạm cách ly Module KHBD do lỗi sai tên hàm bên trong file views/xd_khbd_view.py.")
            
    with tabs_gv[1]:
        if render_xd_de_kt: render_xd_de_kt(ai_instance)
        else: st.warning("🚧 Hệ thống tạm cách ly Module Đề kiểm tra do lỗi sai tên hàm bên trong file views/xd_de_kt_view.py.")
            
    with tabs_gv[2]:
        if render_xd_ma_tran_tu_de: render_xd_ma_tran_tu_de(ai_instance)
        else: st.warning("🚧 Hệ thống tạm cách ly Module Ma trận do lỗi sai tên hàm bên trong file views/xd_ma_tran_tu_de.py.")
            
    with tabs_gv[3]:
        try: render_xd_cham_viet(ai_instance)
        except NameError: st.warning("Module Chấm viết chưa sẵn sàng.")
    with tabs_gv[4]:
        try: render_xd_chu_nhiem(ai_instance)
        except NameError: st.warning("Module Chủ nhiệm chưa sẵn sàng.")
    with tabs_gv[5]:
        try: render_xd_chuyen_doi(ai_instance)
        except NameError: st.warning("Module Chuyển đổi chưa sẵn sàng.")
    with tabs_gv[6]:
        try: render_xd_live(ai_instance)
        except NameError: st.warning("Module Live chưa sẵn sàng.")
    with tabs_gv[7]:
        try: render_xd_mo_phong(ai_instance)
        except NameError: st.warning("Module Mô phỏng chưa sẵn sàng.")
    with tabs_gv[8]:
        try: render_xd_quizizz(ai_instance)
        except NameError: st.warning("Module Quizizz chưa sẵn sàng.")
    with tabs_gv[9]:
        try: render_xd_rubric(ai_instance)
        except NameError: st.warning("Module Rubric chưa sẵn sàng.")
    with tabs_gv[10]:
        try: render_xd_stem(ai_instance)
        except NameError: st.warning("Module STEM chưa sẵn sàng.")
    with tabs_gv[11]:
        try:
            render_xd_tao_hoc_lieu(ai_instance)
            st.divider()
            render_xd_tao_prompt(ai_instance)
        except NameError: st.warning("Module Tạo học liệu/Prompt chưa sẵn sàng.")

# ------------------------------------------------------------
# 2. PHÂN HỆ HỖ TRỢ GIẢNG DẠY
# ------------------------------------------------------------
elif menu_category == "🎓 Phân hệ Hỗ trợ Giảng dạy":
    st.markdown("## 🎓 Phân hệ: Hỗ trợ Giảng dạy")
    
    tab_titles_gd = [
        "1. RAG Ask", "2. Cá nhân hóa", "3. Camera", 
        "4. Chấm nhanh", "5. Học liệu", "6. Kiểm tra nhanh", 
        "7. Ngân hàng đề", "8. Phân tích", "9. Phân tích BH", 
        "10. Sinh video", "11. Trò chơi", "12. Mô phỏng (Đang phát triển)"
    ]
    tabs_gd = st.tabs(tab_titles_gd)
    
    with tabs_gd[0]:
        try: render_rag_ask(ai_instance)
        except NameError: st.warning("Module RAG Ask chưa sẵn sàng.")
    with tabs_gd[1]:
        try: render_xd_ca_nhan_hoa(ai_instance)
        except NameError: st.warning("Module Cá nhân hóa chưa sẵn sàng.")
    with tabs_gd[2]:
        try: render_xd_camera(ai_instance)
        except NameError: st.warning("Module Camera chưa sẵn sàng.")
    with tabs_gd[3]:
        try: render_xd_cham_nhanh(ai_instance)
        except NameError: st.warning("Module Chấm nhanh chưa sẵn sàng.")
    with tabs_gd[4]:
        try: render_xd_hoc_lieu(ai_instance)
        except NameError: st.warning("Module Học liệu chưa sẵn sàng.")
    with tabs_gd[5]:
        try: render_xd_kiem_tra_nhanh(ai_instance)
        except NameError: st.warning("Module Kiểm tra nhanh chưa sẵn sàng.")
    with tabs_gd[6]:
        try: render_xd_ngan_hang_de(ai_instance)
        except NameError: st.warning("Module Ngân hàng đề chưa sẵn sàng.")
    with tabs_gd[7]:
        try: render_xd_phan_tich(ai_instance)
        except NameError: st.warning("Module Phân tích chưa sẵn sàng.")
    with tabs_gd[8]:
        try: render_xd_phan_tich_bh(ai_instance)
        except NameError: st.warning("Module Phân tích Bài học chưa sẵn sàng.")
    with tabs_gd[9]:
        try: render_xd_sinh_video(ai_instance)
        except NameError: st.warning("Module Sinh video chưa sẵn sàng.")
    with tabs_gd[10]:
        try: render_xd_tro_choi(ai_instance)
        except NameError: st.warning("Module Trò chơi chưa sẵn sàng.")
    with tabs_gd[11]:
        st.info("Khu vực tính năng Mô phỏng thuộc phân hệ Hỗ trợ giảng dạy đang được phát triển...")
    elif selected_menu == "Mô phỏng": # Hoặc tên menu tương ứng của thầy
        render_xd_mo_phong(ai_engine)
# ------------------------------------------------------------
# 3. PHÂN HỆ ỨNG DỤNG KHÁC
# ------------------------------------------------------------
elif menu_category == "🛠️ Phân hệ Ứng dụng khác":
    try:
        render_ung_dung_khac(ai_instance)
    except Exception as e:
        st.error(f"Lỗi hiển thị phân hệ Ứng dụng khác: {e}")

# ------------------------------------------------------------
# 4. PHÂN HỆ QUẢN LÝ TỔ CHUYÊN MÔN
# ------------------------------------------------------------
elif menu_category == "👥 Phân hệ Quản lý Tổ chuyên môn":
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
