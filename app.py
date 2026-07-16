import streamlit as st
from utils.ai_engine import AIEngine

# ==========================================
# HÀM BẢO MẬT: LẤY API KEY CỦA NGƯỜI DÙNG HIỆN TẠI
# ==========================================
def get_current_user_api_key():
    """
    Hàm này chỉ trả về API Key của người dùng đang đăng nhập.
    Tạm thời lấy từ Session State. Tuyệt đối không gọi st.secrets của Admin.
    """
    return st.session_state.get("user_api_key", None)

# ==========================================
# KIỂM SOÁT LUỒNG VÀ KHỞI TẠO AI
# ==========================================
user_api_key = get_current_user_api_key()

if user_api_key:
    # 🟢 Nếu đã có Key của cá nhân -> Khởi tạo AIEngine riêng cho người đó
    try:
        ai_engine = AIEngine(api_key=user_api_key)
    except Exception as e:
        ai_engine = None
        st.error("Lỗi khởi tạo AI. Vui lòng kiểm tra lại API Key của thầy/cô.")
else:
    # 🔴 Nếu chưa có Key -> Yêu cầu nhập để đi tiếp
    ai_engine = None
    st.info("👋 Chào mừng đến với Hệ sinh thái. Vui lòng nhập API Key Gemini của thầy/cô để bắt đầu.")
    
    with st.form("form_nhap_key"):
        key_input = st.text_input("🔑 Nhập Google Gemini API Key cá nhân:", type="password")
        submit_key = st.form_submit_button("Xác nhận")
        
        if submit_key and key_input:
            st.session_state.user_api_key = key_input
            st.rerun() # Tải lại trang để áp dụng Key mới
    
    st.stop() # Chặn hoàn toàn không cho dùng tính năng bên dưới nếu chưa có Key

# ==========================================
# TRUYỀN ENGINE VÀO CÁC PHÂN HỆ
# ==========================================
# VD: with tabs[0]: render_xd_khbd(ai_engine)
