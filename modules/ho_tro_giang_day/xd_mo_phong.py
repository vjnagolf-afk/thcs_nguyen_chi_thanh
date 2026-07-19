import streamlit as st
import streamlit.components.v1 as components

def render_xd_mo_phong(ai_engine):
    st.markdown("### 🧪 Mô phỏng & Thí nghiệm ảo")
    
    # 1. Menu lựa chọn nguồn tài nguyên
    nguon = st.selectbox(
        "Chọn nền tảng mô phỏng:",
        ["PhET Interactive Simulations", "MozaWeb - Thư viện 3D"]
    )
    
    # 2. Xử lý logic nhúng (Embed)
    if nguon == "PhET Interactive Simulations":
        st.info("💡 PhET cung cấp các mô phỏng tương tác miễn phí cho môn Vật lý, Hóa học, Sinh học, Toán học.")
        # Link PhET cho phép nhúng (embed)
        phong_phet = "https://phet.colorado.edu/vi/"
        components.iframe(phong_phet, height=700, scrolling=True)
        
    elif nguon == "MozaWeb - Thư viện 3D":
        st.info("💡 MozaWeb mang đến các mô hình 3D trực quan cho bài giảng.")
        # Lưu ý: MozaWeb có thể chặn nhúng tùy vào cấu hình bảo mật của trang web
        phong_moza = "https://mozaweb.vn/vi/lexikon.php?cmd=getlist&let=3D&sid=BIO"
        components.iframe(phong_moza, height=700, scrolling=True)
        
    # 3. Ghi chú cho giáo viên
    with st.expander("📝 Hướng dẫn sử dụng"):
        st.write("""
        - **PhET**: Chọn chủ đề, sau đó click vào nút Play trên mô phỏng để chạy.
        - **MozaWeb**: Bạn cần đăng nhập tài khoản MozaWeb nếu hệ thống yêu cầu quyền truy cập vào các nội dung 3D cao cấp.
        - Nếu trang web không hiện, hãy thử mở trực tiếp bằng nút liên kết dưới đây.
        """)
        st.link_button("Mở PhET trong tab mới", "https://phet.colorado.edu/vi/")
        st.link_button("Mở MozaWeb trong tab mới", "https://mozaweb.vn/vi/")
