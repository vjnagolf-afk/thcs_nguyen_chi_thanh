import streamlit as st
from utils.db_connector import db
from utils.ai_engine import AIEngine

# Import các phân hệ
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
from modules.ho_tro_giang_day.rag_ask import render_rag

# Cấu hình trang
st.set_page_config(page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh", layout="wide")

# Khởi tạo AI Engine
try:
    ai_engine = AIEngine(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    ai_engine = None
    st.error("Lỗi cấu hình AI Engine: Vui lòng kiểm tra GEMINI_API_KEY trong Secrets.")

# --- 1. SIDEBAR: ĐIỀU HƯỚNG ---
with st.sidebar:
    # Header styling
    st.markdown("""
        <p style='font-size: 26px; color: red; font-weight: bold; text-align: center;'>
            HỆ SINH THÁI SỐ<br>HỖ TRỢ GIÁO VIÊN
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chọn phân hệ
    st.markdown("""
        <p style='font-size: 26px; color: red; font-weight: bold; text-align: center;'>
            CHỌN PHÂN HỆ
        </p>
    """, unsafe_allow_html=True)
    
    phan_he = st.radio("", [
        "Hỗ trợ Giáo viên",
        "Hỗ trợ Giảng dạy",
        "Quản lý Tổ chuyên môn"
    ])
    
    st.markdown("---")
    
    # Admin Gate
    if st.checkbox("🛡️ Quản trị (Admin)"):
        try:
            from modules.admin.user_management import render_user_management
            render_user_management()
        except:
            st.warning("Phân hệ Admin đang được cập nhật.")

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; font-style: italic; color: #555;'>
            Tác giả: Lê Hồng Dưỡng<br>
            THCS Nguyễn Chí Thanh
        </div>
    """, unsafe_allow_html=True)

# --- 2. MAIN BODY: HIỂN THỊ NỘI DUNG ---

# Phân hệ: Quản lý Tổ chuyên môn
if phan_he == "Quản lý Tổ chuyên môn":
    st.markdown("## 📊 Phân hệ: Quản lý Tổ chuyên môn")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Danh sách thành viên", "📋 Phân công", "📝 Biên bản", "📁 Kế hoạch", "🏆 Thi đua"
    ])
    
    with tab1: render_danh_sach()
    with tab2: render_phan_cong(db)
    with tab3: render_bien_ban(db)
    with tab4: st.info("Đang phát triển: Kế hoạch")
    with tab5: st.info("Đang phát triển: Thi đua")

# Phân hệ: Hỗ trợ Giảng dạy
elif phan_he == "Hỗ trợ Giảng dạy":
    st.markdown("## 🪴 Hỗ trợ Giảng dạy")
    tabs = st.tabs([
        "Hỏi-Đáp (RAG)", "Trò chơi", "Chấm bài", "Học liệu", "Mô phỏng", 
        "Phân tích", "Ngân hàng đề", "Sinh Video", "Tương tác", "Cá nhân hóa"
    ])
    
    with tabs[0]: 
        if ai_engine: render_rag(ai_engine)
    with tabs[1]: st.info("Đang phát triển: Trò chơi")
    with tabs[2]: st.info("Đang phát triển: Chấm bài")
    with tabs[3]: st.info("Đang phát triển: Học liệu")
    with tabs[4]: st.info("Đang phát triển: Mô phỏng")
    # ... các tab khác tương tự

# Phân hệ: Hỗ trợ Giáo viên
elif phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 🧑‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs = st.tabs([
        "XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM", "Rubric", 
        "Chủ nhiệm", "Quản lý điểm", "Tạo prompt", "Quizizz", "Mô phỏng thực hành"
    ])
    
    with tabs[0]: st.info("Đang phát triển: Xây dựng KHBD")
    with tabs[1]: st.info("Đang phát triển: Xây dựng Đề KT")
    # ... các tab khác tương tự
