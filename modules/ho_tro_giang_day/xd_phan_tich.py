import streamlit as st

def render_xd_phan_tich(ai_engine):
    st.markdown("### 📈 Trợ lý Phân tích Kết quả Học tập")
    st.info("💡 Hỗ trợ giáo viên phân tích phổ điểm, đánh giá năng lực học sinh (qua điểm số hoặc nhận xét) và tự động đề xuất giải pháp phụ đạo/bồi dưỡng.")

    # Khởi tạo session để giữ kết quả
    if "phan_tich_result" not in st.session_state:
        st.session_state.phan_tich_result = ""

    col1, col2 = st.columns([1, 2])
    
    with col1:
        loai_du_lieu = st.selectbox(
            "Loại dữ liệu phân tích:", 
            ["Bảng điểm (Số)", "Nhận xét/Đánh giá (Chữ)", "Kết quả khảo sát"]
        )
        
        muc_tieu = st.multiselect(
            "Trọng tâm phân tích:",
            ["Phân loại học lực", "Tìm ra lỗ hổng kiến thức", "Đề xuất kế hoạch phụ đạo", "Đề xuất bài tập nâng cao"],
            default=["Phân loại học lực", "Đề xuất kế hoạch phụ đạo"]
        )

    with col2:
        du_lieu = st.text_area(
            "Nhập dữ liệu (Copy/Paste từ Excel hoặc Word):", 
            height=200, 
            placeholder="Ví dụ 1 (Nhận xét):\nNguyễn Văn A: 5 (Sai nhiều phần hình học)\nTrần Thị B: 9 (Làm tốt, tư duy nhanh)\nLê Văn C: 4 (Tính toán chậm, ẩu)...\n\nVí dụ 2 (Chỉ có điểm): 5, 6, 8, 9, 4, 3, 10, 8, 7..."
        )

    st.markdown("---")

    if st.button("📊 TIẾN HÀNH PHÂN TÍCH", type="primary"):
        if du_lieu.strip():
            with st.spinner("⏳ AI đang xử lý số liệu và lập báo cáo..."):
                prompt = f"""Đóng vai là một chuyên gia phân tích dữ liệu giáo dục và phương pháp giảng dạy cấp THCS. Hãy phân tích tập dữ liệu sau của học sinh.
                
                - Loại dữ liệu: {loai_du_lieu}
                - Dữ liệu đầu vào:
                {du_lieu}
                
                - Trọng tâm cần phân tích: {', '.join(muc_tieu)}
                
                YÊU CẦU ĐẦU RA BÁO CÁO (Trình bày bằng Markdown chuyên nghiệp):
                1. Đánh giá tổng quan: Tình hình chung của lớp/nhóm học sinh này như thế nào?
                2. Phân tích chi tiết: Đi sâu vào các trọng tâm mà giáo viên yêu cầu ở trên. Nếu có thể, hãy gom nhóm học sinh (nhóm giỏi, khá, cần cố gắng).
                3. Giải pháp sư phạm: Đưa ra 3-4 lời khuyên thiết thực, các dạng bài tập nên giao thêm, hoặc cách điều chỉnh kịch bản giảng dạy cho phù hợp với thực trạng vừa phân tích.
                (Lưu ý: Dùng bảng biểu markdown nếu nó giúp báo cáo dễ nhìn hơn).
                """
                
                try:
                    res = ai_engine.generate_text(prompt)
                    st.session_state.phan_tich_result = res
                except Exception as e:
                    st.error(f"Lỗi khi gọi AI: {e}")
        else:
            st.warning("⚠️ Vui lòng dán dữ liệu điểm số hoặc nhận xét vào ô trống để AI có thể phân tích!")

    if st.session_state.phan_tich_result:
        st.markdown("### 📑 Báo cáo Phân tích Năng lực Học sinh")
        st.markdown(st.session_state.phan_tich_result)
