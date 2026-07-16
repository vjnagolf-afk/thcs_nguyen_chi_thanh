import streamlit as st
from utils.db_connector import db
from utils.ai_engine import AIEngine

# ==========================================
# IMPORT CÁC PHÂN HỆ (Bám sát cây thư mục)
# ==========================================

# 1. Quản lý Tổ chuyên môn (Thư mục: modules/quan_ly_to/)
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban

# 2. Hỗ trợ Giảng dạy (Thư mục: modules/ho_tro_giang_day/)
from modules.ho_tro_giang_day.rag_ask import render_rag

# 3. Hỗ trợ Giáo viên (Thư mục: modules/ho_tro_gv/)
from modules.ho_tro_gv.xd_khbd import render_xd_khbd

# ==========================================
# CẤU HÌNH TRANG & KHỞI TẠO AI
# ==========================================
st.set_page_config(page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh", layout="wide")

try:
    ai_engine = AIEngine(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    ai_engine = None
    st.error("Lỗi cấu hình AI: Vui lòng kiểm tra GEMINI_API_KEY trong mục Secrets trên Streamlit Cloud.")

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================

# --- 1. SIDEBAR: ĐIỀU HƯỚNG ---
with st.sidebar:
    # 🌟 THÊM CSS TÙY CHỈNH CHO RADIO BUTTON
    st.markdown("""
        <style>
            /* Đẩy container của radio buttons thụt vào 1cm (xa lề trái) */
            div.stRadio > div[role="radiogroup"] {
                padding-left: 1cm; 
            }
            /* Chỉnh cỡ chữ 16px cho các tùy chọn bên trong */
            div.stRadio > div[role="radiogroup"] label p {
                font-size: 16px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <p style='font-size: 26px; color: red; font-weight: bold; text-align: center;'>
            HỆ SINH THÁI SỐ<br>HỖ TRỢ GIÁO VIÊN
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chọn phân hệ (Chữ màu xanh dương, cỡ chữ 20)
    st.markdown("""
        <p style='font-size: 20px; color: blue; font-weight: bold; text-align: center;'>
            CHỌN PHÂN HỆ
        </p>
    """, unsafe_allow_html=True)
    
    phan_he = st.radio(
        "Label ẩn", # Tên ẩn không hiển thị
        [
            "Hỗ trợ Giáo viên",
            "Hỗ trợ Giảng dạy",
            "Quản lý Tổ chuyên môn"
        ],
        label_visibility="collapsed" # Lệnh giấu chữ đi
    )
    
    st.markdown("---")
    
    # Quản trị (Admin)
    if st.checkbox("🛡️ Quản trị (Admin)"):
        try:
            from modules.admin.user_management import render_user_management
            render_user_management()
        except ImportError:
            st.warning("Đang chờ file: `modules/admin/user_management.py`")

    # Footer Tác giả
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; font-style: italic; color: #555;'>
            Tác giả: Lê Hồng Dưỡng<br>
            THCS Nguyễn Chí Thanh
        </div>
    """, unsafe_allow_html=True)

# --- 2. MAIN BODY: HIỂN THỊ TABS ---

# PHÂN HỆ 1: QUẢN LÝ TỔ CHUYÊN MÔN
if phan_he == "Quản lý Tổ chuyên môn":
    st.markdown("## 📊 Phân hệ: Quản lý Tổ chuyên môn")
    
    # Thêm tab6 vào danh sách
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👥 Danh sách thành viên", 
        "📋 Phân công", 
        "📝 Biên bản", 
        "📁 Kế hoạch", 
        "🏆 Thi đua", 
        "🔍 Kiểm tra KHBD"
    ])
    
    with tab1: render_danh_sach()
    with tab2: render_phan_cong(db)
    with tab3: render_bien_ban(db)
    with tab4: st.info("Sẽ gọi hàm từ: `modules/quan_ly_to/ke_hoach.py`")
    with tab5: st.info("Sẽ gọi hàm từ: `modules/quan_ly_to/thi_dua.py`")
    with tab6: st.info("Sẽ gọi hàm từ: `modules/quan_ly_to/kiem_tra_khbd.py`")

# PHÂN HỆ 2: HỖ TRỢ GIẢNG DẠY
elif phan_he == "Hỗ trợ Giảng dạy":
    st.markdown("## 🪴 Hỗ trợ Giảng dạy")
    tabs = st.tabs([
        "Hỏi-Đáp (RAG)", "Trò chơi", "Chấm bài", "Học liệu", "Mô phỏng", 
        "Phân tích", "Ngân hàng đề", "Sinh Video", "Tương tác", "Cá nhân hóa"
    ])
    
    with tabs[0]: 
        if ai_engine: render_rag(ai_engine)
    with tabs[1]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_giang_day/tro_choi.py`")
    with tabs[2]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_giang_day/cham_bai.py`")
    with tabs[3]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_giang_day/hoc_lieu.py`")
    with tabs[4]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_giang_day/mo_phong.py`")
    # Các tab còn lại tương tự...

# PHÂN HỆ 3: HỖ TRỢ GIÁO VIÊN
elif phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 🧑‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs = st.tabs([
        "XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM", "Rubric", 
        "Chủ nhiệm", "Quản lý điểm", "Tạo prompt", "Quizizz", "Mô phỏng thực hành"
    ])
    
    # Đã cập nhật lệnh gọi hàm render_xd_khbd tại đây!
    with tabs[0]: render_xd_khbd(ai_engine)
    with tabs[1]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_gv/xd_de_kt.py`")
    with tabs[2]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_gv/bai_day_stem.py`")
    with tabs[3]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_gv/rubric.py`")
    # Các tab còn lại tương tự...
