import streamlit as st
from utils.db_connector import db
from utils.ai_engine import AIEngine

# Import các phân hệ (Thầy đảm bảo các hàm này đã được định nghĩa trong file tương ứng)
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
# Sẽ bổ sung các hàm tương ứng sau
from modules.ho_tro_giang_day.rag_ask import render_rag

# Khởi tạo
ai_engine = AIEngine(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(page_title="Hệ sinh thái số", layout="wide")

with st.sidebar:
    # --- HEADER: HỆ SINH THÁI SỐ ---
    st.markdown("""
        <p style='font-size: 26px; color: red; font-weight: bold; text-align: center;'>
            HỆ SINH THÁI SỐ<br>HỖ TRỢ GIÁO VIÊN
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- CHỌN PHÂN HỆ ---
    st.markdown("""
        <p style='font-size: 26px; color: red; font-weight: bold; text-align: center;'>
            CHỌN PHÂN HỆ
        </p>
    """, unsafe_allow_html=True)
    
    # Radio buttons
    phan_he = st.radio("", [
        "Hỗ trợ Giáo viên",
        "Hỗ trợ Giảng dạy",
        "Quản lý Tổ chuyên môn"
    ])
    
    st.markdown("---")
    
    # Admin Gate
    if st.checkbox("🛡️ Quản trị (Admin)"):
        from modules.admin.user_management import render_user_management
        render_user_management()

    # --- FOOTER: TÁC GIẢ ---
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; font-style: italic; color: #555;'>
            Tác giả: Lê Hồng Dưỡng<br>
            THCS Nguyễn Chí Thanh
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.checkbox("🛡️ Quản trị (Admin)"):
        from modules.admin.user_management import render_user_management
        render_user_management()

# --- MAIN BODY: DÙNG TABS ---
# 1. PHÂN HỆ: QUẢN LÝ TỔ CHUYÊN MÔN
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

# 2. PHÂN HỆ: HỖ TRỢ GIẢNG DẠY
elif phan_he == "Hỗ trợ Giảng dạy":
    st.markdown("## 🪴 Hỗ trợ Giảng dạy")
    tabs = st.tabs([
        "Hỏi-Đáp (RAG)", "Trò chơi", "Chấm bài", "Học liệu", "Mô phỏng", 
        "Phân tích", "Ngân hàng đề", "Sinh Video", "Tương tác", "Cá nhân hóa"
    ])
    
    with tabs[0]: render_rag(ai_engine)
    with tabs[1]: st.info("Đang phát triển: Trò chơi")
    with tabs[2]: st.info("Đang phát triển: Chấm bài")
    # ... (Tiếp tục cho các tab khác)

# 3. PHÂN HỆ: HỖ TRỢ GIÁO VIÊN
elif phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 🧑‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs = st.tabs([
        "XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM", "Rubric", 
        "Chủ nhiệm", "Quản lý điểm", "Tạo prompt", "Quizizz", "Mô phỏng thực hành"
    ])
    
    with tabs[0]: st.info("Đang phát triển: Xây dựng KHBD")
    # ... (Các tab khác)
