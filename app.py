import streamlit as st
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_giang_day.xd_tro_choi import render_xd_tro_choi
from modules.ho_tro_giang_day.xd_cham_nhanh import render_xd_cham_nhanh
from modules.ho_tro_giang_day.xd_hoc_lieu import render_xd_hoc_lieu

# Giả định thầy đã có lớp AIEngine để xử lý các yêu cầu
# Nếu chưa, thầy khởi tạo lớp này theo cách cũ của thầy
class AIEngine:
    def generate_text(self, prompt):
        return "AI đang xử lý..." 

ai_engine = AIEngine()

st.set_page_config(page_title="Trợ lý Giáo viên", layout="wide")

st.title("🪴 Hệ thống Hỗ trợ Giảng dạy & Giáo viên")

phan_he = st.sidebar.radio("Chọn phân hệ:", ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy"])

if phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 👩‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs_gv = st.tabs(["XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM", "Rubric", "Chủ nhiệm", "Chấm bài Viết", "Tạo prompt", "Quizizz", "Mô phỏng thực hành"])
    # Các render_gv... tương ứng ở đây

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
