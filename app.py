import streamlit as st

# Import các module của phân hệ Giáo viên
# (Thầy đảm bảo các file này tồn tại trong folder tương ứng)
from modules.ho_tro_giao_vien.xd_khbd import render_xd_khbd
from modules.ho_tro_giao_vien.xd_de_kt import render_xd_de_kt
from modules.ho_tro_giao_vien.xd_stem import render_xd_stem
from modules.ho_tro_giao_vien.xd_rubric import render_xd_rubric
from modules.ho_tro_giao_vien.xd_chu_nhiem import render_xd_chu_nhiem
from modules.ho_tro_giao_vien.xd_cham_viet import render_xd_cham_viet
from modules.ho_tro_giao_vien.xd_tao_prompt import render_xd_tao_prompt
from modules.ho_tro_giao_vien.xd_quizizz import render_xd_quizizz
from modules.ho_tro_giao_vien.xd_mo_phong import render_xd_mo_phong

# Import các module của phân hệ Giảng dạy
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_giang_day.xd_tro_choi import render_xd_tro_choi
from modules.ho_tro_giang_day.xd_cham_nhanh import render_xd_cham_nhanh
from modules.ho_tro_giang_day.xd_hoc_lieu import render_xd_hoc_lieu

# Khởi tạo AI Engine (giả lập)
class AIEngine:
    def generate_text(self, prompt):
        return "AI đang xử lý..."

ai_engine = AIEngine()

st.set_page_config(page_title="Trợ lý Giáo viên THCS", layout="wide")
st.title("🪴 Hệ thống Hỗ trợ Giảng dạy & Giáo viên")

phan_he = st.sidebar.radio("Chọn phân hệ:", ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy"])

if phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 👩‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs_gv = st.tabs(["XD KHBD", "XD Đề KT", "STEM", "Rubric", "Chủ nhiệm", "Chấm bài Viết", "Tạo prompt", "Quizizz", "Mô phỏng"])
    
    with tabs_gv[0]: render_xd_khbd(ai_engine)
    with tabs_gv[1]: render_xd_de_kt(ai_engine)
    with tabs_gv[2]: render_xd_stem(ai_engine)
    with tabs_gv[3]: render_xd_rubric(ai_engine)
    with tabs_gv[4]: render_xd_chu_nhiem(ai_engine)
    with tabs_gv[5]: render_xd_cham_viet(ai_engine)
    with tabs_gv[6]: render_xd_tao_prompt(ai_engine)
    with tabs_gv[7]: render_xd_quizizz(ai_engine)
    with tabs_gv[8]: render_xd_mo_phong(ai_engine)

elif phan_he == "Hỗ trợ Giảng dạy":
    st.markdown("## 🪴 Phân hệ: Hỗ trợ Giảng dạy")
    tabs_gd = st.tabs(["Hỏi-Đáp (RAG)", "Trò chơi", "Chấm bài", "Học liệu"])
    
    with tabs_gd[0]: render_rag(ai_engine)
    with tabs_gd[1]: render_xd_tro_choi(ai_engine)
    with tabs_gd[2]: render_xd_cham_nhanh(ai_engine)
    with tabs_gd[3]: render_xd_hoc_lieu(ai_engine)
