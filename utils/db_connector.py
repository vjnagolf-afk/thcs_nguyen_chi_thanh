# -*- coding: utf-8 -*-
"""
============================================================
KẾT NỐI CƠ SỞ DỮ LIỆU: QUẢN LÝ KẾT NỐI SUPABASE (Tối ưu Cache)
FILE: utils/db_connector.py
============================================================
"""

import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_database_connection() -> Client:
    """Khởi tạo kết nối Supabase chuẩn và lưu vào bộ nhớ đệm (Cache)"""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError as e:
        st.error(f"❌ Lỗi: Thiếu cấu hình {e} trong file secrets.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Supabase: {e}")
        st.stop()

# Xuất biến db chuẩn để các file khác (app.py) import vào sử dụng
db = get_database_connection()
