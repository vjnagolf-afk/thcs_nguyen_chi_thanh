import streamlit as st

def render_xd_mo_phong(ai_engine):
    st.markdown("### 🧪 Phòng thí nghiệm ảo")
    st.caption("Nền tảng thực hành mô phỏng tương tác giúp học sinh trực quan hóa kiến thức.")
    
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <b>Quy trình thực nghiệm:</b><br>
        ⚙️ Thay đổi thông số ➔ 👁️ Quan sát kết quả ➔ 🤔 Dự đoán ➔ 🧪 Thực nghiệm ➔ 📝 Kết luận
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        mon_hoc = st.selectbox("Chọn môn học:", ["Vật lý", "Hóa học", "Sinh học", "Toán học", "Khác"])
    
    with col2:
        if mon_hoc == "Vật lý":
            chu_de = st.selectbox("Chủ đề mô phỏng:", ["Đo vận tốc", "Định luật Ôm", "Mạch điện", "Lực", "Công", "Năng lượng", "Âm học", "Quang học"])
        else:
            chu_de = st.text_input("Nhập chủ đề cần mô phỏng:", placeholder=f"Ví dụ: Cấu tạo tế bào, Phản ứng Oxi hóa...")

    if st.button("🚀 Khởi tạo bài thực hành", type="primary"):
        if chu_de.strip():
            with st.spinner("AI đang thiết lập kịch bản phòng thí nghiệm..."):
                prompt = f"""
                Tôi đang dạy môn {mon_hoc}, chủ đề "{chu_de}". Hãy thiết kế một kịch bản "Phòng thí nghiệm ảo" cho học sinh THCS dựa theo đúng 5 bước sau:
                1. Thay đổi thông số (Gợi ý học sinh có thể điều chỉnh các biến số nào)
                2. Quan sát kết quả (Học sinh sẽ thấy hiện tượng gì xảy ra)
                3. Dự đoán (Câu hỏi định hướng để học sinh suy đoán quy luật)
                4. Thực nghiệm (Các bước kiểm chứng)
                5. Kết luận (Kiến thức cốt lõi rút ra)
                """
                try:
                    kich_ban = ai_engine.generate_text(prompt)
                    st.success(f"Đã tải kịch bản mô phỏng cho chủ đề: {chu_de}")
                    st.info(kich_ban)
                except Exception as e:
                    st.error(f"Lỗi khởi tạo: {e}")
        else:
            st.warning("Vui lòng nhập chủ đề trước khi khởi tạo!")
