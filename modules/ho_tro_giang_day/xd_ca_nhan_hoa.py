# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_ca_nhan_hoa(ai_engine=None):
    st.markdown("### 🎯 Trợ lý Thiết kế Lộ trình Cá nhân hóa")
    st.caption("AI phân tích điểm mạnh, điểm yếu của từng học sinh để tự động thiết kế lộ trình phụ đạo hoặc bồi dưỡng chuyên sâu.")

    with st.form("form_ca_nhan_hoa"):
        col1, col2 = st.columns(2)
        with col1:
            ten_hs = st.text_input("Tên học sinh / Nhóm học sinh:", placeholder="VD: Nhóm HS Yếu môn Lý 8")
            muc_tieu = st.text_input("Mục tiêu cần đạt:", placeholder="VD: Lấy lại gốc bài Định luật Ôm, đạt 6.5 điểm")
        with col2:
            thoi_gian = st.selectbox("Thời lượng lộ trình:", ["1 tuần", "2 tuần", "4 tuần (1 tháng)", "8 tuần (Giữa kỳ)"], index=2)
            kieu_lo_trinh = st.selectbox("Dạng lộ trình:", ["Phụ đạo lấy gốc", "Bồi dưỡng HSG", "Rèn luyện kỹ năng tự học"])
            
        diem_yeu = st.text_area("Mô tả kỹ năng còn yếu hoặc đặc điểm của HS:", placeholder="VD: Hay sai dấu khi giải phương trình, mất tập trung, không thuộc công thức...")
        
        submitted = st.form_submit_button("🚀 AI Lập lộ trình học tập", type="primary", use_container_width=True)

    if submitted:
        if not diem_yeu.strip():
            st.warning("⚠️ Vui lòng mô tả điểm yếu/thực trạng của học sinh.")
        else:
            with st.spinner("AI đang lên kế hoạch từng bước..."):
                prompt = f"""
                Bạn là một chuyên gia Sư phạm và Cố vấn học tập.
                Hãy lập một lộ trình học tập cá nhân hóa cực kỳ chi tiết cho học sinh/nhóm sau:
                - Đối tượng: {ten_hs}
                - Mục tiêu: {muc_tieu}
                - Thời gian: {thoi_gian}
                - Phân loại: {kieu_lo_trinh}
                - Thực trạng / Điểm yếu hiện tại: {diem_yeu}
                
                YÊU CẦU:
                - Lộ trình chia theo từng Tuần (hoặc từng ngày nếu ngắn).
                - Tại mỗi giai đoạn, chỉ rõ: Nội dung cần học, Bài tập thực hành, và Tiêu chí đánh giá hoàn thành.
                - Đưa ra 3 lời khuyên tâm lý học đường dành cho giáo viên khi kèm cặp nhóm này.
                """
                if ai_engine:
                    result = ai_engine.generate_text(prompt)
                    st.success("✅ Đã hoàn thành lộ trình!")
                    st.markdown("---")
                    st.markdown(result)
                else:
                    st.error("❌ Không có kết nối AI Engine.")
