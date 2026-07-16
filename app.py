import streamlit as st
import sys
from pathlib import Path

# ==========================================
# 1. CẤU HÌNH TRANG (Bắt buộc phải ở dòng đầu tiên và chỉ gọi 1 lần)
# ==========================================
st.set_page_config(
    page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh",
    layout="wide"
)

# ==========================================
# 2. CẤU HÌNH ĐƯỜNG DẪN HỆ THỐNG
# ==========================================
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import các phân hệ
from utils.db_connector import db
from utils.ai_engine import AIEngine
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_gv.xd_khbd import render_xd_khbd

# ==========================================
# 3. KHỞI TẠO TRẠNG THÁI PHIÊN LÀM VIỆC
# ==========================================
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = None
if "is_admin_mode" not in st.session_state:
    st.session_state.is_admin_mode = False

# ==========================================
# 4. HÀM LẤY ENGINE TỐI ƯU (CACHE CHỐNG LAG & MULTI-KEY)
# ==========================================
@st.cache_resource
def get_ai_engine(is_admin, user_key):
    keys = {}
    
    if is_admin:
        # Chế độ Admin: Lấy toàn bộ bộ Key từ secrets.toml
        keys["gemini"] = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("SCHOOL_ADMIN_API_KEY")
        keys["openai"] = st.secrets.get("OPENAI_API_KEY")
        keys["claude"] = st.secrets.get("CLAUDE_API_KEY")
    else:
        # Chế độ User: Giáo viên tự nhập Key của mình
        keys["gemini"] = user_key
        
    # Lọc bỏ các key bị None hoặc rỗng
    keys = {k: v for k, v in keys.items() if v}
    
    return AIEngine(keys=keys) if keys else None

# ==========================================
# 5. GIAO DIỆN SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: red;'>HỆ SINH THÁI SỐ<br>HỖ TRỢ GIÁO VIÊN</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h4 style='text-align: center; color: blue;'>CHỌN PHÂN HỆ</h4>", unsafe_allow_html=True)
    
    phan_he = st.radio(
        "Chọn phân hệ:", 
        ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy", "Quản lý Tổ chuyên môn"], 
        label_visibility="collapsed"
    )
    
    st.markdown("<br>" * 10, unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style='color: #007AFF; font-style: italic; line-height: 1.2;'>
            <p style='margin: 0 0 2px 0;'>Tác giả: Lê Hồng Dưỡng</p>
            <p style='margin: 0 0 10px 0;'>Đơn vị: Trường THCS Nguyễn Chí Thanh</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Chỉ hiện nút Đăng xuất khi đã đăng nhập
    if st.session_state.user_api_key or st.session_state.is_admin_mode:
        if st.button("🚪 Đăng xuất / Đổi Key", use_container_width=True):
            st.session_state.user_api_key = None
            st.session_state.is_admin_mode = False
            st.rerun()

# ==========================================
# 6. CỔNG BẢO MẬT (LOGIN)
# ==========================================
if not st.session_state.user_api_key and not st.session_state.is_admin_mode:
    st.warning("🔑 Vui lòng nhập API Key cá nhân HOẶC Mật khẩu Quản trị để bắt đầu.")
    with st.form("login"):
        key_input = st.text_input("Nhập API Key / Mật khẩu:", type="password")
        if st.form_submit_button("Xác nhận"):
            if not key_input.strip():
                st.error("⚠️ Vui lòng không để trống!")
            # Kiểm tra xem có phải mật khẩu Admin không
            elif key_input.strip() == st.secrets.get("ADMIN_PASSWORD", "admin123456"):
                st.session_state.is_admin_mode = True
                st.rerun()
            else:
                st.session_state.user_api_key = key_input.strip()
                st.session_state.is_admin_mode = False
                st.rerun()
    st.stop()

# ==========================================
# 7. KHỞI TẠO ENGINE & KIỂM TRA TOÀN VẸN
# ==========================================
ai_engine = get_ai_engine(st.session_state.is_admin_mode, st.session_state.user_api_key)

if not ai_engine:
    st.error("❌ Không thể khởi tạo Hệ thống AI. Vui lòng kiểm tra lại API Key hoặc cấu hình Secrets.")
    st.stop()

# ==========================================
# 8. CHUYỂN HƯỚNG PHÂN HỆ (ROUTING)
# ==========================================
if phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 👩‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    tabs_gv = st.tabs(["XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM", "Rubric", "Chủ nhiệm", "Quản lý điểm", "Tạo prompt", "Quizizz", "Mô phỏng thực hành"])
    with tabs_gv[0]:
        render_xd_khbd(ai_engine)
    with tabs_gv[1]:
        st.info("Tính năng Xây dựng Đề kiểm tra đang được phát triển.")

elif phan_he == "Hỗ trợ Giảng dạy":
    st.markdown("## 🪴 Hỗ trợ Giảng dạy")
    tabs_gd = st.tabs(["Hỏi-Đáp (RAG)", "Trò chơi", "Chấm bài", "Học liệu", "Mô phỏng", "Phân tích", "Ngân hàng đề", "Sinh Video", "Tương tác", "Cá nhân hóa"])
    with tabs_gd[0]:
        render_rag(ai_engine)
    with tabs_gd[1]:
        st.info("Tính năng Trò chơi đang được phát triển.")

elif phan_he == "Quản lý Tổ chuyên môn":
    st.markdown("## 📊 Phân hệ: Quản lý Tổ chuyên môn")
    tabs_to = st.tabs(["Danh sách thành viên", "Phân công", "Biên bản", "Kế hoạch", "Thi đua", "Kiểm tra KHBD"])
    with tabs_to[0]:
        render_danh_sach()
    with tabs_to[1]:
        render_phan_cong(db)
    with tabs_to[2]:
        render_bien_ban(db)
    with tabs_to[3]:
        st.info("Tính năng Kế hoạch đang được phát triển.")
