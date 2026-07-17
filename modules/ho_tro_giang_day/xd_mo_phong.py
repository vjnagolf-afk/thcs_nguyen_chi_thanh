import streamlit as st

def render_xd_mo_phong(ai_engine):
    st.markdown("### 🧪 Trợ lý Thiết kế Mô phỏng & Thực hành")
    st.info("💡 Hỗ trợ lên kịch bản thí nghiệm, hướng dẫn lắp ráp mô hình STEM, hoặc sinh mã code cho các dự án vi điều khiển (IoT, Robotics).")

    if "mo_phong_result" not in st.session_state:
        st.session_state.mo_phong_result = ""

    chude = st.text_input(
        "Tên bài thực hành / Dự án:", 
        placeholder="Ví dụ: Hệ thống tiết kiệm điện năng thông minh dùng ESP8266..."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        loai_hinh = st.selectbox("Loại hình thực hành:", [
            "Lập trình Vi điều khiển (Arduino, ESP8266, micro:bit...)",
            "Mô hình STEM vật lý (vật liệu tái chế, cơ khí...)",
            "Thí nghiệm Khoa học ảo (Lý, Hóa, Sinh)",
            "Tích hợp AI & IoT"
        ])
    with col2:
        doi_tuong = st.selectbox("Đối tượng học sinh:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Khác"])

    yeu_cau_them = st.text_area(
        "Yêu cầu cụ thể (vật tư hiện có, phần mềm sử dụng...):", 
        placeholder="Ví dụ: Chỉ dùng các linh kiện cơ bản, có code mẫu cho C++ / Python, cần mô tả sơ đồ nối dây để copy vào đề tài..."
    )

    if st.button("🚀 TẠO HƯỚNG DẪN THỰC HÀNH", type="primary"):
        if chude.strip():
            with st.spinner("⏳ AI đang thiết kế kịch bản thực hành..."):
                prompt = f"""Đóng vai là một giáo viên chuyên hướng dẫn STEM và kỹ thuật cấp THCS, hãy thiết kế một bản hướng dẫn thực hành/mô phỏng chi tiết cho học sinh {doi_tuong}.
                
                - Chủ đề/Dự án: {chude}
                - Loại hình: {loai_hinh}
                - Yêu cầu bổ sung: {yeu_cau_them}
                
                Vui lòng cấu trúc bản hướng dẫn theo các phần sau:
                1. Mục tiêu bài thực hành.
                2. Danh sách thiết bị / vật tư cần chuẩn bị.
                3. Hướng dẫn thực hiện từng bước (mô tả chi tiết nguyên lý, cách lắp ráp để học sinh dễ hình dung).
                4. Mã code mẫu (nếu là dự án lập trình/IoT) có chú thích rõ ràng.
                5. Gợi ý 2-3 câu hỏi thảo luận mở rộng.
                
                Trình bày bằng định dạng Markdown đẹp mắt, dùng bảng biểu nếu cần thiết để so sánh hoặc liệt kê."""
                
                try:
                    res = ai_engine.generate_text(prompt)
                    st.session_state.mo_phong_result = res
                except Exception as e:
                    st.error(f"Lỗi khi gọi AI: {e}")
        else:
            st.warning("⚠️ Vui lòng nhập Tên bài thực hành/Dự án!")

    if st.session_state.mo_phong_result:
        st.markdown("---")
        st.markdown("### 📋 Hướng dẫn Thực hành chi tiết")
        st.markdown(st.session_state.mo_phong_result)
