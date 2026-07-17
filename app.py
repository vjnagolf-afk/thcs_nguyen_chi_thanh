# -*- coding: utf-8 -*-
import streamlit as st
import sys
from pathlib import Path

# ========================================== #
# 1. CẤU HÌNH TRANG
# ========================================== #
st.set_page_config(page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh", layout="wide", page_icon="🏫")

# Cấu hình đường dẫn hệ thống
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ========================================== #
# 2. IMPORT CÁC MODULE
# ========================================== #
try:
    from utils.db_connector import db
    from utils.ai_engine import AIEngine
    # Phân hệ Quản lý tổ
    from modules.quan_ly_to.danh_sach import render_danh_sach
    from modules.quan_ly_to.phan_cong import render_phan_cong
    from modules.quan_ly_to.bien_ban import render_bien_ban
    # Phân hệ Giáo viên
    from modules.ho_tro_giao_vien.xd_khbd import render_xd_khbd
    # Phân hệ Giảng dạy (ĐÃ TÍCH HỢP 4 MODULE MỚI)
    from modules.ho_tro_giang_day.rag_ask import render_rag
    from modules.ho_tro_giang_day.xd_tro_choi import render_xd_tro_choi
    from modules.ho_tro_giang_day.xd_cham_nhanh import render_xd_cham_nhanh
    from modules.ho_tro_giang_day.xd_hoc_lieu import render_xd_hoc_lieu
except ImportError as e:
    st.error(f"❌ Thiếu file hệ thống hoặc lỗi cấu trúc thư mục: {e}")
    st.stop()

# ========================================== #
# 3. CÁC HÀM XỬ LÝ ENGINE (GIỮ NGUYÊN)
# ========================================== #
# (Các hàm validate_key và get_ai_engine_instance giữ nguyên như code thầy đã gửi)
def get_ai_engine_instance():
    if st.session_state.get("ai_engine_instance"):
        return st.session_state.ai_engine_instance
    # ... logic khởi tạo ai_engine ...
    return None

# ========================================== #
# 4. ROUTING PHÂN HỆ GIẢNG DẠY (PHẦN THẦY CẦN)
# ========================================== #
# ... (Phần Sidebar và Login giữ nguyên) ...

elif phan_he == "Hỗ trợ Giảng dạy":
    st.markdown("## 🪴 Phân hệ: Hỗ trợ Giảng dạy")
    tabs_gd = st.tabs(["Hỏi-Đáp (RAG)", "Trò chơi", "Chấm bài", "Học liệu", "Mô phỏng", "Phân tích", "Ngân hàng đề", "Sinh Video", "Tương tác", "Cá nhân hóa"])
    
    with tabs_gd[0]:
        render_rag(ai_engine)
    with tabs_gd[1]:
        render_xd_tro_choi(ai_engine)
    with tabs_gd[2]:
        render_xd_cham_nhanh(ai_engine)
    with tabs_gd[3]:
        render_xd_hoc_lieu(ai_engine)
    with tabs_gd[4]:
        st.info("💡 Tính năng Mô phỏng đang được phát triển.")

# ... (Phần Quản lý Tổ chuyên môn giữ nguyên) ...
