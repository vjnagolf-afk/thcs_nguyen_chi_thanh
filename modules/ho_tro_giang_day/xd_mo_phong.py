import streamlit as st
import streamlit.components.v1 as components

def render_xd_mo_phong(ai_engine):
    st.markdown("### 🧪 Mô phỏng & Thí nghiệm ảo")
    
    # 1. Menu lựa chọn chế độ
    lua_chon = st.radio(
        "Chọn hình thức:", 
        ["🤖 Trợ lý AI thiết kế mô phỏng", "🌐 Nhúng phòng thí nghiệm ảo (PhET/MozaWeb)"], 
        horizontal=True
    )
    
    # 2. Logic giữ lại tính năng cũ (Dùng AI tạo mô phỏng)
    if lua_chon == "🤖 Trợ lý AI thiết kế mô phỏng":
        st.info("AI sẽ hỗ trợ thầy xây dựng kịch bản hoặc code mô phỏng.")
        # [PHẦN NÀY THẦY GIỮ NGUYÊN CODE CŨ CỦA THẦY Ở ĐÂY]
        # Ví dụ: prompt = st.text_area("Yêu cầu mô phỏng...")
        # if st.button("Tạo mô phỏng"): ...
        
    # 3. Logic bổ sung tính năng nhúng
    else:
        nguon = st.selectbox("Chọn nền tảng:", ["PhET Interactive Simulations", "MozaWeb - Thư viện 3D"])
        
        if nguon == "PhET Interactive Simulations":
            components.iframe("https://phet.colorado.edu/vi/", height=700, scrolling=True)
        else:
            st.warning("MozaWeb có thể chặn nhúng. Nếu không hiển thị, hãy dùng nút mở dưới đây:")
            components.iframe("https://mozaweb.vn/vi/lexikon.php?cmd=getlist&let=3D&sid=BIO", height=700, scrolling=True)
            st.link_button("Mở MozaWeb trong tab mới", "https://mozaweb.vn/vi/")
