# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_phan_tich(ai_engine=None):
    st.markdown("### 📈 Phân tích Dữ liệu Điểm số & Học tập")
    st.caption("AI đóng vai trò như một chuyên gia phân tích dữ liệu (Data Analyst) để tìm ra xu hướng điểm, phổ điểm và dự báo học lực của học sinh.")

    col_data, col_prompt = st.columns([1, 1])

    with col_data:
        st.markdown("**Dữ liệu điểm số (CSV, Text):**")
        bang_diem = st.text_area(
            "Dán bảng điểm (Tên, Điểm Toán, Điểm Văn...) hoặc dữ liệu thô:", 
            height=200, 
            placeholder="Nguyen Van A, 8.5, 7.0\nTran Thi B, 9.0, 8.5\nLe Van C, 5.0, 6.5"
        )
        
    with col_prompt:
        st.markdown("**Yêu cầu Phân tích:**")
        muc_tieu = st.radio(
            "AI cần tập trung vào:",
            ["Thống kê phổ điểm chung (Trung bình, Giỏi, Yếu)", "Tìm ra học sinh cần lưu ý đặc biệt (Khen thưởng / Phụ đạo)", "Nhận xét tổng quan chất lượng lớp học"]
        )
        btn_phan_tich = st.button("📊 Chạy Phân Tích", type="primary", use_container_width=True)

    if btn_phan_tich:
        if not bang_diem.strip():
            st.warning("⚠️ Vui lòng dán dữ liệu bảng điểm.")
        else:
            with st.spinner("AI đang tính toán và phân tích các chỉ số..."):
                prompt = f"""
                Bạn là một chuyên gia Thống kê và Quản lý chất lượng giáo dục.
                Dựa trên bộ dữ liệu điểm số thô dưới đây, hãy thực hiện phân tích: {muc_tieu}.
                
                DỮ LIỆU ĐIỂM SỐ:
                {bang_diem}
                
                YÊU CẦU:
                - Phân tích khách quan, sử dụng số liệu để chứng minh.
                - Trình bày gọn gàng, có điểm nhấn (bold) các kết luận quan trọng.
                - Nếu phát hiện điểm bất thường (outliers), hãy nêu rõ.
                """
                
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.success("✅ Phân tích hoàn tất!")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI.")
