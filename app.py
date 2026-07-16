import streamlit as st
from utils.db_connector import db
from utils.ai_engine import AIEngine

# ==========================================
# IMPORT CÁC PHÂN HỆ
# ==========================================
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_gv.xd_khbd import render_xd_khbd

# ==========================================
# CẤU HÌNH TRANG (PHẢI Ở TRÊN CÙNG)
# ==========================================
st.set_page_config(page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh", layout="wide")

# ==========================================
# QUẢN LÝ BỘ NHỚ TẠM (SESSION STATE)
# ==========================================
def get_current_user_api_key():
    return st.session_state.get("user_api_key", None)

if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = None

# ==========================================
# GIAO DIỆN SIDEBAR (LUÔN HIỂN THỊ)
# ==========================================
with st.sidebar:
    st.markdown("""
        <style>
            div.stRadio > div[role="radiogroup"] { padding-left: 1cm; }
            div.stRadio > div[role="radiogroup"] label p { font-size: 16px !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 26px; color: red; font-weight: bold; text-align: center;'>HỆ SINH THÁI SỐ<br>HỖ TRỢ GIÁO VIÊN</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<p style='font-size: 20px; color: blue; font-weight: bold; text-align: center;'>CHỌN PHÂN HỆ</p>", unsafe_allow_html=True)
    
    phan_he = st.radio(
        "Label ẩn", 
        ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy", "Quản lý Tổ chuyên môn"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    
    if st.checkbox("🛡️ Quản trị (Admin)"):
        try:
            from modules.admin.user_management import render_user_management
            render_user_management()
        except ImportError:
            st.warning("Đang chờ file: `modules/admin/user_management.py`")

    st.markdown("---")
    st.markdown("<div style='text-align: center; font-style: italic; color: #555;'>Tác giả: Lê Hồng Dưỡng<br>THCS Nguyễn Chí Thanh</div>", unsafe_allow_html=True)

# ==========================================
# CỔNG BẢO MẬT: KIỂM TRA API KEY Ở MAIN BODY
# ==========================================
user_api_key = get_current_user_api_key()
ai_engine = None

if not user_api_key:
    # Nếu chưa có Key, hiển thị form ở giữa màn hình chính
    st.markdown("## 🔐 Cổng kết nối AI")
    st.info("👋 Để đảm bảo tính bảo mật và tài nguyên độc lập, vui lòng nhập API Key Gemini của cá nhân thầy/cô để sử dụng các tính năng.")
    
    with st.form("form_nhap_key"):
        key_input = st.text_input("🔑 Nhập Google Gemini API Key:", type="password")
        submit_key = st.form_submit_button("🚀 Xác nhận & Vào hệ thống")
        
        if submit_key:
            if key_input.strip() == "":
                st.error("Vui lòng không để trống API Key!")
            else:
                st.session_state.user_api_key = key_input.strip()
                st.rerun() # Tải lại trang để cấp quyền vào hệ thống
    
    # Dừng vẽ phần bên dưới, nhưng Sidebar ở trên đã được vẽ xong
    st.stop() 

else:
    # Nếu đã có Key, khởi tạo AI Engine và hiển thị nút Đăng xuất
    try:
        ai_engine = AIEngine(api_key=user_api_key)
        
        # Thêm nút Hủy Key ở góc phải để người dùng có thể thoát hoặc đổi Key khác
        col_blank, col_logout = st.columns([8, 1])
        with col_logout:
            if st.button("🚪 Hủy Key AI"):
                st.session_state.user_api_key = None
                st.rerun()
                
    except Exception as e:
        st.error("Lỗi kết nối AI. API Key có thể không hợp lệ!")
        if st.button("🔄 Nhập lại Key"):
            st.session_state.user_api_key = None
            st.rerun()
        st.stop()

# ==========================================
# MAIN BODY: CHẠY CÁC PHÂN HỆ (KHI ĐÃ CÓ KEY)
# ==========================================
if phan_he == "Quản lý Tổ chuyên môn":
    st.markdown("## 📊 Phân hệ: Quản lý Tổ chuyên môn")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👥 Danh sách thành viên", "📋 Phân công", "📝 Biên bản", "📁 Kế hoạch", "🏆 Thi đua", "🔍 Kiểm tra KHBD"
    ])
    with tab1: render_danh_sach()
    with tab2: render_phan_cong(db)
    with tab3: render_bien_ban(db)
    with tab4: st.info("Sẽ gọi hàm từ: `modules/quan_ly_to/ke_hoach.py`")
    with tab5: st.info("Sẽ gọi hàm từ: `modules/quan_ly_to/thi_dua.py`")
    with tab6: st.info("Sẽ gọi hàm từ: `modules/quan_ly_to/kiem_tra_khbd.py`")

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

elif phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 🧑‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs = st.tabs([
        "XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM", "Rubric", 
        "Chủ nhiệm", "Quản lý điểm", "Tạo prompt", "Quizizz", "Mô phỏng thực hành"
    ])
    with tabs[0]: 
        if ai_engine: render_xd_khbd(ai_engine)
    with tabs[1]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_gv/xd_de_kt.py`")
    with tabs[2]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_gv/bai_day_stem.py`")
    with tabs[3]: st.info("Sẽ gọi hàm từ: `modules/ho_tro_gv/rubric.py`")
