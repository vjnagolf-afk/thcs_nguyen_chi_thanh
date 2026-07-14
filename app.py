import streamlit as st
from utils.db_connector import db
from modules.management.danh_sach import render_danh_sach
from modules.management.phan_cong import render_phan_cong
from modules.management.bien_ban import render_bien_ban

st.set_page_config(page_title="Hệ sinh thái số", layout="wide")

# Sidebar
with st.sidebar:
    st.title("⚙️ Hệ thống")
    if 'gemini_api_key' not in st.session_state:
        st.session_state['gemini_api_key'] = st.text_input("Gemini API Key", type="password")

menu = st.sidebar.radio("CHỌN PHÂN HỆ", ["Danh sách", "Phân công", "Biên bản"])

if menu == "Danh sách":
    render_danh_sach()
elif menu == "Phân công":
    render_phan_cong(db)
elif menu == "Biên bản":
    render_bien_ban(db)
