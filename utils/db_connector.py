# -*- coding: utf-8 -*-
"""
============================================================
KẾT NỐI CƠ SỞ DỮ LIỆU: QUẢN LÝ KẾT NỐI SUPABASE
FILE: utils/db_connector.py
============================================================
"""

import os
import streamlit as st

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None

class DatabaseConnector:
    """
    Lớp bọc (Wrapper) quản lý kết nối cơ sở dữ liệu Supabase.
    Cung cấp thuộc tính `client` để các module khác (như xd_tkb.py) gọi trực tiếp.
    """
    def __init__(self, client):
        self.client = client

def init_db():
    """
    Hàm khởi tạo kết nối đến Supabase.
    Ưu tiên lấy thông tin cấu hình từ Streamlit Secrets, 
    nếu không có sẽ tìm trong biến môi trường hệ thống.
    """
    if create_client is None:
        # Nếu chưa cài đặt thư viện supabase
        return None
        
    try:
        url = None
        key = None
        
        # 1. Tìm trong st.secrets
        if hasattr(st, "secrets"):
            if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
                url = st.secrets["SUPABASE_URL"]
                key = st.secrets["SUPABASE_KEY"]
                
        # 2. Tìm trong biến môi trường hệ thống nếu secrets không có
        if not url or not key:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")

        # 3. Khởi tạo client nếu có đủ credentials
        if url and key:
            supabase_client = create_client(url, key)
            return DatabaseConnector(supabase_client)
            
        return None
        
    except Exception as e:
        # Bắt lỗi tĩnh lặng (silent fail) để không làm hỏng giao diện
        # Có thể thêm logging nếu cần thiết
        return None
