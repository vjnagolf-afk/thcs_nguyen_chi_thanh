import streamlit as st

def render_xd_ca_nhan_hoa(ai_engine):
    st.markdown("### 🎯 Trợ lý Cá nhân hóa Lộ trình Học tập")
    st.info("💡 Hỗ trợ giáo viên xây dựng lộ trình học tập, tài liệu và phương pháp giảng dạy được "may đo" riêng cho từng học sinh hoặc từng nhóm học sinh cụ thể.")

    if "ca_nhan_hoa_result" not in st.session_state:
        st.session_state.ca_nhan_hoa_result = ""

    col1, col2, col3 = st.columns(3)
    with col1:
        mon_hoc = st.selectbox("Môn học / Lĩnh vực:", ["Toán", "Ngữ Văn", "Tiếng Anh", "KHTN", "Lịch sử & Địa lý", "Tin học", "STEM/Dự án", "Khác"])
    with col2:
        doi_tuong = st.selectbox("Nhóm đối tượng:", ["Học sinh Yếu/Kém (Cần phụ đạo)", "Học sinh Trung bình (Cần bứt phá)", "Học sinh Khá/Giỏi (Cần bồi dưỡng)", "Học sinh có khó khăn đặc biệt (Tâm lý, ADHD...)"])
    with col3:
        thoi_gian = st.selectbox("Thời lượng lộ trình:", ["1 Tuần", "2 Tuần", "1 Tháng", "1 Học kỳ"])

    st.markdown("**Hồ sơ học sinh (Đầu vào):**")
    diem_manh_yeu = st.text_area(
        "Mô tả năng lực hiện tại (Điểm mạnh, điểm yếu, sở thích học tập):",
        height=100,
        placeholder="Ví dụ: Học sinh tiếp thu hình học tốt nhưng tính toán đại số rất hay sai vặt. Thích học qua hình ảnh và trò chơi..."
    )
    
    muc_tieu = st.text_input(
        "Mục tiêu cần đạt được:",
        placeholder="Ví dụ: Nắm vững bảng tuần hoàn hóa học, Đạt điểm 8 kỳ thi giữa kỳ..."
    )

    st.markdown("---")

    if st.button("🚀 TẠO LỘ TRÌNH CÁ NHÂN HÓA", type="primary"):
        if diem_manh_yeu.strip() and muc_tieu.strip():
            with st.spinner("⏳ AI đang phân tích hồ sơ và thiết kế lộ trình riêng..."):
                prompt = f"""Đóng vai là một chuyên gia tâm lý học đường và giáo viên {mon_hoc} kỳ cựu cấp THCS. Hãy xây dựng một lộ trình học tập cá nhân hóa cho đối tượng: {doi_tuong}.
                
                THÔNG TIN HỌC SINH:
                - Mô tả năng lực/sở thích: {diem_manh_yeu}
                - Mục tiêu cần đạt: {muc_tieu}
                - Thời gian thực hiện: {thoi_gian}
                
                YÊU CẦU ĐẦU RA (Trình bày bằng Markdown chuyên nghiệp, có icon minh họa):
                1. Phân tích tâm lý & phương pháp: Phân tích ngắn gọn nguyên nhân cốt lõi của tình trạng hiện tại và đề xuất phương pháp tiếp cận phù hợp nhất (Ví dụ: Học qua thị giác, chia nhỏ nhiệm vụ...).
                2. Lộ trình chi tiết ({thoi_gian}): Phân bổ nội dung học tập theo từng giai đoạn (từng ngày/tuần tùy thời lượng).
                3. Đề xuất tài liệu/Bài tập: Gợi ý 2-3 dạng bài tập/hoạt động cụ thể phù hợp với sở thích và năng lực của học sinh này.
                4. Cách giáo viên & Phụ huynh đồng hành: Lời khuyên về cách khích lệ, kiểm tra đánh giá mà không gây áp lực.
                """
                
                try:
                    res = ai_engine.generate_text(prompt)
                    st.session_state.ca_nhan_hoa_result = res
                except Exception as e:
                    st.error(f"Lỗi khi gọi AI: {e}")
        else:
            st.warning("⚠️ Vui lòng nhập Mô tả năng lực và Mục tiêu cần đạt!")

    # Hiển thị kết quả
    if st.session_state.ca_nhan_hoa_result:
        st.markdown("### 📋 Kế hoạch & Lộ trình chi tiết")
        st.markdown(st.session_state.ca_nhan_hoa_result)
