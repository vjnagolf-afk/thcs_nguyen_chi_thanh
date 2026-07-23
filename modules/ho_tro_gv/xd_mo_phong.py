# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_mo_phong(ai_engine=None):
    st.markdown("### 🧪 Trợ lý Sinh Mã Mô Phỏng Thí Nghiệm (HTML/JS)")
    st.caption("AI viết mã HTML/JavaScript/CSS để xây dựng các thí nghiệm ảo cơ bản. Giáo viên có thể copy mã này dán vào thẻ 'Nhúng Canva/HTML' để học sinh chơi.")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            mon_hoc = st.selectbox("Môn học:", ["Vật lí", "Hóa học", "Sinh học", "Toán học"])
        with col2:
            kieu_tuong_tac = st.selectbox("Loại tương tác:", ["Kéo thanh trượt đổi thông số", "Bấm nút hiện kết quả", "Kéo thả vật thể"])
            
        hien_tuong = st.text_area("Mô tả thí nghiệm cần mô phỏng:", height=100, placeholder="VD: Thí nghiệm ném vật chéo góc. Học sinh kéo thanh trượt chỉnh góc ném, quả bóng bay thành đường parabol...")
        
        btn_sinh_ma = st.button("⚙️ Viết mã Mô phỏng", type="primary", use_container_width=True)

    if btn_sinh_ma:
        if not hien_tuong.strip():
            st.warning("⚠️ Vui lòng mô tả hiện tượng vật lý/hóa học.")
        else:
            with st.spinner("Lập trình viên AI đang viết code HTML/JS cho mô phỏng này..."):
                prompt = f"""
                Bạn là một Kỹ sư lập trình Web (Frontend) và Chuyên gia giáo dục STEM.
                Nhiệm vụ: Viết một file HTML đơn lẻ (Single HTML file bao gồm thẻ <style> và <script> bên trong) để mô phỏng một thí nghiệm giáo dục.
                
                - Môn học: {mon_hoc}
                - Yêu cầu thí nghiệm: {hien_tuong}
                - Yêu cầu tương tác UI: {kieu_tuong_tac}
                
                YÊU CẦU CODE BẮT BUỘC:
                1. Giao diện trực quan, rõ ràng, có vùng hiển thị kết quả/đồ thị/hoạt hình đơn giản (dùng Canvas hoặc div CSS).
                2. Áp dụng đúng công thức khoa học của môn {mon_hoc}.
                3. Đặt toàn bộ code vào trong môt khối block ```html ... ``` duy nhất.
                """
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.success("✅ Đã lập trình xong! Hãy copy đoạn mã dưới đây dán vào notepad, lưu đuôi .html để chạy.")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
