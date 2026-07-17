# -*- coding: utf-8 -*-
import streamlit as st
import sys
from pathlib import Path

# ========================================== #
# 1. CẤU HÌNH TRANG (Bắt buộc ở dòng đầu tiên)
# ========================================== #
st.set_page_config(
    page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh",
    layout="wide",
    page_icon="🏫"
)

# ========================================== #
# 2. CẤU HÌNH ĐƯỜNG DẪN HỆ THỐNG
# ========================================== #
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ========================================== #
# 3. IMPORT CÁC PHÂN HỆ
# ========================================== #
try:
    from utils.db_connector import db
    from utils.ai_engine import AIEngine
    
    # --- Quản lý tổ ---
    from modules.quan_ly_to.danh_sach import render_danh_sach
    from modules.quan_ly_to.phan_cong import render_phan_cong
    from modules.quan_ly_to.bien_ban import render_bien_ban
    
    # --- Hỗ trợ giáo viên ---
    from views.xd_khbd_view import render_xd_khbd
    # Import các module của phân hệ Giáo viên
    from modules.ho_tro_gv.xd_khbd import render_xd_khbd
    from views.xd_de_kt_view import render_xd_de_kt
    from modules.ho_tro_gv.xd_stem import render_xd_stem
    from modules.ho_tro_gv.xd_rubric import render_xd_rubric
    from modules.ho_tro_gv.xd_chu_nhiem import render_xd_chu_nhiem
    from modules.ho_tro_gv.xd_cham_viet import render_xd_cham_viet
    from modules.ho_tro_gv.xd_tao_prompt import render_xd_tao_prompt
    from modules.ho_tro_gv.xd_quizizz import render_xd_quizizz
    from modules.ho_tro_gv.xd_mo_phong import render_xd_mo_phong
    from modules.ho_tro_gv.xd_live import render_xd_live
    
    # --- Hỗ trợ giảng dạy ---
    from modules.ho_tro_giang_day.rag_ask import render_rag
    from modules.ho_tro_giang_day.xd_tro_choi import render_xd_tro_choi
    from modules.ho_tro_giang_day.xd_cham_nhanh import render_xd_cham_nhanh
    from modules.ho_tro_giang_day.xd_hoc_lieu import render_xd_hoc_lieu
    from modules.ho_tro_giang_day.xd_mo_phong import render_xd_mo_phong
    from modules.ho_tro_giang_day.xd_phan_tich import render_xd_phan_tich
    from modules.ho_tro_giang_day.xd_ngan_hang_de import render_xd_ngan_hang_de
    from modules.ho_tro_giang_day.xd_sinh_video import render_xd_sinh_video
    from modules.ho_tro_giang_day.xd_tuong_tac import render_xd_tuong_tac
    from modules.ho_tro_giang_day.xd_ca_nhan_hoa import render_xd_ca_nhan_hoa
except ImportError as e:
    st.error(f"❌ Thiếu file hệ thống hoặc lỗi cấu trúc thư mục: {e}")
    st.stop()

# ========================================== #
# 4. KHỞI TẠO TRẠNG THÁI PHIÊN LÀM VIỆC
# ========================================== #
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = None
if "is_admin_mode" not in st.session_state:
    st.session_state.is_admin_mode = False

# ========================================== #
# 5. HÀM KIỂM TRA ĐỊNH DẠNG API KEY
# ========================================== #
def validate_key(key: str) -> bool:
    k = key.strip()
    return (
        k.startswith("AIza")       
        or k.startswith("sk-ant-") 
        or k.startswith("sk-")     
    )

# ========================================== #
# 6. HÀM LẤY ENGINE TỐI ƯU
# ========================================== #
def get_ai_engine_instance():
    if st.session_state.get("ai_engine_instance"):
        return st.session_state.ai_engine_instance

    keys = {}
    if st.session_state.is_admin_mode:
        keys["gemini"] = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("SCHOOL_ADMIN_API_KEY")
        keys["openai"] = st.secrets.get("OPENAI_API_KEY")
        keys["claude"] = st.secrets.get("CLAUDE_API_KEY")
    else:
        k = st.session_state.user_api_key
        if k:
            if k.startswith("AIza"): keys["gemini"] = k
            elif k.startswith("sk-ant-"): keys["claude"] = k
            elif k.startswith("sk-"): keys["openai"] = k
            else: keys["gemini"] = k

    keys = {k: v for k, v in keys.items() if v}
    
    if keys:
        st.session_state.ai_engine_instance = AIEngine(keys=keys)
    else:
        st.session_state.ai_engine_instance = None
        
    return st.session_state.ai_engine_instance

# ========================================== #
# 7. GIAO DIỆN SIDEBAR
# ========================================== #
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #E63946;'>HỆ SINH THÁI SỐ<br>HỖ TRỢ GIÁO VIÊN</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h4 style='text-align: center; color: #1D3557;'>CHỌN PHÂN HỆ</h4>", unsafe_allow_html=True)
    
    phan_he = st.radio(
        "Chọn phân hệ:",
        ["Hỗ trợ Giáo viên", "Hỗ trợ Giảng dạy", "Quản lý Tổ chuyên môn"],
        label_visibility="collapsed"
    )
    
    st.write("")
    st.write("")
    st.write("")
    
    st.markdown(
        """
        <div style='color: #007AFF; font-style: italic; line-height: 1.4; border-left: 3px solid #007AFF; padding-left: 10px;'>
            <p style='margin: 0;'><b>Tác giả:</b> Lê Hồng Dưỡng</p>
            <p style='margin: 0;'><b>Đơn vị:</b> Trường THCS Nguyễn Chí Thanh</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    if st.session_state.user_api_key or st.session_state.is_admin_mode:
        if st.button("🚪 Đăng xuất / Đổi Key", use_container_width=True, type="secondary"):
            st.session_state.user_api_key = None
            st.session_state.is_admin_mode = False
            if "ai_engine_instance" in st.session_state:
                del st.session_state.ai_engine_instance
            st.rerun()

# ========================================== #
# 8. CỔNG BẢO MẬT (LOGIN FORM)
# ========================================== #
if not st.session_state.user_api_key and not st.session_state.is_admin_mode:
    st.info("🔑 Vui lòng nhập API Key cá nhân hoặc Mật khẩu Quản trị để bắt đầu.")
    
    with st.form("login"):
        key_input = st.text_input(
            "Nhập API Key / Mật khẩu hệ thống:", 
            type="password", 
            help="Nhập Key Gemini (AIza) / OpenAI (sk-) / Claude (sk-ant-) hoặc mật khẩu Admin."
        )
        submit = st.form_submit_button("Xác nhận đăng nhập", use_container_width=True)
        
        if submit:
            clean_input = key_input.strip()
            admin_password = st.secrets.get("ADMIN_PASSWORD", "admin123456")
            
            if not clean_input:
                st.error("⚠️ Vui lòng không để trống trường thông tin!")
            elif clean_input == admin_password:
                st.session_state.is_admin_mode = True
                st.success("🎉 Đăng nhập quyền Quản trị hệ thống thành công!")
                st.rerun()
            elif validate_key(clean_input):
                st.session_state.user_api_key = clean_input
                st.session_state.is_admin_mode = False
                st.success("🚀 Khởi tạo với API Key cá nhân thành công!")
                st.rerun()
            else:
                st.error("❌ API Key không đúng định dạng. Vui lòng kiểm tra lại!")
    st.stop()

# ========================================== #
# 9. KHỞI TẠO ENGINE
# ========================================== #
ai_engine = get_ai_engine_instance()

if not ai_engine:
    st.error("❌ Không thể cấu hình Động cơ AI. Vui lòng kiểm tra lại Key.")
    if st.button("Quay lại màn hình đăng nhập"):
        st.session_state.user_api_key = None
        st.session_state.is_admin_mode = False
        st.rerun()
    st.stop()

# ========================================== #
# 10. CHUYỂN HƯỚNG PHÂN HỆ (ROUTING CHUẨN)
# ========================================== #
if phan_he == "Hỗ trợ Giáo viên":
    st.markdown("## 👩‍🏫 Phân hệ: Hỗ trợ Giáo viên")
    
    # Khai báo đúng số lượng và tên các tab
    tabs_gv = st.tabs(["XD KHBD", "XD Đề KT", "Thiết kế bài dạy STEM", "Rubric", "Chủ nhiệm", "Đánh giá kĩ năng viết", "Tạo prompt", "Quizizz", "Mô phỏng thực hành","Live"])
    
    # Gắn liên kết từng hàm vào đúng tab
    with tabs_gv[0]:
        render_xd_khbd(ai_engine)
    with tabs_gv[1]:
        render_xd_de_kt(ai_engine)
    with tabs_gv[2]:
        render_xd_stem(ai_engine)
    with tabs_gv[3]:
        render_xd_rubric(ai_engine)
    with tabs_gv[4]:
        render_xd_chu_nhiem(ai_engine)
    with tabs_gv[5]:
        render_xd_cham_viet(ai_engine) # Gắn chức năng chấm bài viết vào tab Quản lý điểm
    with tabs_gv[6]:
        render_xd_tao_prompt(ai_engine)
    with tabs_gv[7]:
        render_xd_quizizz(ai_engine)
    with tabs_gv[8]:
        render_xd_mo_phong(ai_engine)
    with tabs_gv[9]: 
        render_xd_live(ai_engine)
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
    with tabs_gd[4]: 
        render_xd_mo_phong(ai_engine)
    with tabs_gd[5]: 
        render_xd_phan_tich(ai_engine)
    with tabs_gd[6]: 
        render_xd_ngan_hang_de(ai_engine)
    with tabs_gd[7]: 
        render_xd_sinh_video(ai_engine)
    with tabs_gd[8]: 
        render_xd_tuong_tac(ai_engine)
    with tabs_gd[9]: 
        render_xd_ca_nhan_hoa(ai_engine)

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
        st.info("💡 Tính năng Kế hoạch đang được phát triển.")
    with tabs_to[4]:
        st.info("💡 Tính năng Thi đua đang được phát triển.")
    with tabs_to[5]:
        st.info("💡 Tính năng Kiểm tra KHBD đang được phát triển.")
