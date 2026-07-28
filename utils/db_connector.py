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
    def __init__(self, client):
        self.client = client

def init_db():
    if create_client is None:
        st.error("⚠️ Lỗi: Chưa cài đặt thư viện supabase. Thầy hãy mở Terminal gõ: pip install supabase")
        return None
        
    try:
        url = None
        key = None
        
        # 1. Tìm trong st.secrets
        if hasattr(st, "secrets"):
            if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
                url = st.secrets["SUPABASE_URL"]
                key = st.secrets["SUPABASE_KEY"]
            else:
                st.error("⚠️ Lỗi: Có file secrets.toml nhưng bên trong không có dòng SUPABASE_URL hoặc SUPABASE_KEY.")
        else:
            st.error("⚠️ Lỗi: Hệ thống không tìm thấy file .streamlit/secrets.toml")

        # 2. Khởi tạo client
        if url and key:
            supabase_client = create_client(url, key)
            return DatabaseConnector(supabase_client)
            
        return None
        
    except Exception as e:
        st.error(f"⚠️ Chi tiết lỗi từ máy chủ Supabase: {e}")
        return None
