# -*- coding: utf-8 -*-
"""
============================================================
ĐIỀU HƯỚNG TRUNG TÂM DỰ ÁN: NGUYỄN CHÍ THANH (BẢN TỐI GIẢN AN TOÀN)
FILE: app.py
============================================================
"""

import streamlit as st
import os
import sys

# ============================================================
# CẤU HÌNH TRANG STREAMLIT (PHẢI ĐẶT Ở DÒNG ĐẦU TIÊN CỦA STREAMLIT)
# ============================================================
st.set_page_config(
    page_title="Hệ thống Quản lý & Hỗ trợ Chuyên môn - Nguyễn Chí Thanh",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Thêm thư mục gốc vào hệ thống path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# ============================================================
# THANH ĐIỀU HƯỚNG CHÍNH (SIDEBAR)
# ============================================================
st.sidebar.markdown("## 🏫 TRƯỜNG THCS NGUYỄN CHÍ THANH")
st.sidebar.caption("Hệ thống Trợ lý AI Quản lý & Chuyên môn (Chế độ An toàn)")
st.sidebar.divider()

menu_category = st.sidebar.radio(
    "📂 BẢNG ĐIỀU KHIỂN CHÍNH:",
    [
        "🏠 Trang chủ & Trạng thái Hệ thống",
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
# Hiển thị thông tin bản quyền tác giả
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
# GIAO DIỆN CHÍNH (ĐÃ VÔ HIỆU HÓA CÁC MODULE ĐỂ TEST HỆ THỐNG)
# ============================================================
if menu_category == "🏠 Trang chủ & Trạng thái Hệ thống":
    st.markdown("# 🏫 Chào mừng đến với Hệ thống Quản lý & Chuyên môn")
    st.markdown("### Trường THCS Nguyễn Chí Thanh - Tác giả: Lê Hồng Dưỡng")
    st.info("💡 **Trạng thái hệ thống:** Ứng dụng đang chạy ở **Chế độ An toàn tối giản** để xác nhận máy chủ hoạt động ổn định 100%. Các phân hệ chuyên sâu sẽ được kích hoạt lần lượt từng bước theo ý muốn của thầy.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ **Môi trường Streamlit:** Đã khởi động thành công mỹ mãn.")
        st.success("✅ **Thư viện hệ thống:** Đã được dọn sạch các gói xung đột.")
    with col2:
        st.info("ℹ️ Thầy có thể nhập API Key ở menu bên trái để sẵn sàng cho các bước kiểm tra tiếp theo.")

elif menu_category == "👨‍🏫 Phân hệ Hỗ trợ Giáo viên":
    st.markdown("## 👨‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    st.warning("⚠️ Phân hệ này đang tạm vô hiệu hóa để kiểm tra nền tảng. Sẽ được kết nối lại ngay khi app chạy mượt.")

elif menu_category == "🎓 Phân hệ Hỗ trợ Giảng dạy":
    st.markdown("## 🎓 Phân hệ: Hỗ trợ Giảng dạy")
    st.warning("⚠️ Phân hệ này đang tạm vô hiệu hóa để kiểm tra nền tảng.")

elif menu_category == "🛠️ Phân hệ Ứng dụng khác":
    st.markdown("## 🛠️ Phân hệ: Ứng dụng khác")
    st.warning("⚠️ Phân hệ này đang tạm vô hiệu hóa để kiểm tra nền tảng.")

elif menu_category == "👥 Phân hệ Quản lý Tổ chuyên môn":
    st.markdown("## 👥 Phân hệ: Quản lý Tổ chuyên môn")
    st.warning("⚠️ Phân hệ này đang tạm vô hiệu hóa để kiểm tra nền tảng.")
