import streamlit as st
import sys
from pathlib import Path

# ==========================================
# 1. CẤU HÌNH TRANG (Bắt buộc phải ở dòng đầu tiên)
# ==========================================
st.set_page_config(
    page_title="Hệ sinh thái số - THCS Nguyễn Chí Thanh",
    layout="wide"
)

# ==========================================
# 2. KIỂM TRA SECRETS TRƯỚC KHI CHẠY APP
# ==========================================
admin_password = st.secrets.get("ADMIN_PASSWORD")
if not admin_password:
    st.error("⚠️ Lỗi cấu hình hệ thống: Thiếu ADMIN_PASSWORD trong file secrets.toml.")
    st.stop()

# ==========================================
# 3. CẤU HÌNH ĐƯỜNG DẪN HỆ THỐNG
# ==========================================
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import các phân hệ (Sau khi đã nạp sys.path)
from utils.db_connector import db
from utils.ai_engine import AIEngine
from modules.quan_ly_to.danh_sach import render_danh_sach
from modules.quan_ly_to.phan_cong import render_phan_cong
from modules.quan_ly_to.bien_ban import render_bien_ban
from modules.ho_tro_giang_day.rag_ask import render_rag
from modules.ho_tro_gv.xd_khbd import render_xd_khbd

# ==========================================
# 4. KHỞI TẠO TRẠNG THÁI PHIÊN LÀM VIỆC
# ==========================================
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = None
if "is_admin_mode" not in st.session_state:
    st.session_state.is_admin_mode = False

# ==========================================
# 5. HÀM LẤY ENGINE (KHÔNG DÙNG CACHE)
# ==========================================
# Bỏ @st.cache_resource để tránh rò rỉ RAM và xung đột giữa các User
def get_ai_engine(is_admin, user_key):
    keys = {}
    
    if is_admin:
        keys["gemini"] = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("SCHOOL_ADMIN_API_KEY")
        keys["openai"] = st.secrets.get("OPENAI_API_KEY")
        keys["claude"] = st.secrets.get("CLAUDE_API_KEY")
    else:
        if user_key:
            # Tự động nhận diện nhà cung cấp qua tiền tố của API Key
            if user_key.startswith("AIza"):
                keys["gemini"] = user_key
            elif user_key.startswith("sk-ant-"):
                keys["claude"] = user_key
            elif user_key.startswith("sk-"):
                keys["openai"] = user_key
            else:
                # Fallback mặc định
                keys["gemini"] = user_key
                
    # Lọc bỏ các key bị None hoặc rỗng
    keys = {k: v for k, v in keys.items() if v}
    return AIEngine(keys=keys) if keys else None

# ==========================================
# 6. GIAO DIỆN SIDEBAR
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

# ==========================================
# 7. CỔNG BẢO MẬT (LOGIN)
# ==========================================
if not st.session_state.user_api_key and not st.session_state.is_admin_mode:
    st.warning("🔑 Vui lòng nhập API Key cá nhân HOẶC Mật khẩu Quản trị để bắt đầu.")
    with st.form("login"):
        key_input = st.text_input("Nhập API Key / Mật khẩu:", type="password")
        if st.form_submit_button("Xác nhận"):
            if not key_input.strip():
                st.error("⚠️ Vui lòng không để trống!")
            elif key_input.strip() == admin_password:
                st.session_state.is_admin_mode = True
                st.rerun()
            else:
                st.session_state.user_api_key = key_input.strip()
                st.session_state.is_admin_mode = False
                st.rerun()
    st.stop()

# ==========================================
# 8. KHỞI TẠO ENGINE & HIỂN THỊ TRẠNG THÁI
# ==========================================
ai_engine = get_ai_engine(st.session_state.is_admin_mode, st.session_state.user_api_key)

if not ai_engine:
    st.error("❌ Không thể khởi tạo Hệ thống AI. Vui lòng kiểm tra lại API Key hoặc cấu hình Secrets.")
    st.session_state.user_api_key = None
    st.session_state.is_admin_mode = False
    if st.button("🔄 Thử lại"):
        st.rerun()
    st.stop()

# Hiển thị thông báo thành công và Panel Thống kê
with st.sidebar:
    st.success("✅ AI Engine Sẵn sàng")
    with st.expander("📊 Thống kê AI", expanded=False):
        stats = ai_engine.get_stats()
        for provider, tokens in stats["tokens"].items():
            if tokens > 0:
                st.write(f"**{provider.capitalize()}**: {tokens} tokens")
        st.write(f"**Chi phí ước tính:** ${stats['estimated_cost_usd']:.5f}")
        
    if st.button("🚪 Đăng xuất / Đổi Key", use_container_width=True):
        st.session_state.user_api_key = None
        st.session_state.is_admin_mode = False
        st.rerun()

# ==========================================
# 9. CHUYỂN HƯỚNG PHÂN HỆ (ROUTING)
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
