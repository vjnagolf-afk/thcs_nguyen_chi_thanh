# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_rubric(ai_engine=None):
    st.markdown("### 📊 Trợ lý Xây dựng Rubric Đánh Giá")
    st.caption("Thiết kế ma trận tiêu chí đánh giá (Rubric) chi tiết cho các bài thuyết trình, dự án học tập, hoặc bài luận theo hướng phát triển năng lực.")
    
    with st.container(border=True):
        loai_nhiem_vu = st.selectbox("Loại nhiệm vụ đánh giá:", ["Dự án học tập (Project)", "Bài thuyết trình", "Bài viết luận/Nghị luận", "Hoạt động thực hành/Thí nghiệm", "Làm việc nhóm"])
        yeu_cau_can_dat = st.text_area("Mục tiêu bài học / Yêu cầu cần đạt:", height=100, placeholder="VD: HS thiết kế được mô hình tế bào thực vật bằng vật liệu tái chế, thuyết trình rõ ràng chức năng các bào quan.")
        
        c1, c2 = st.columns(2)
        with c1:
            thang_diem = st.selectbox("Thang đánh giá:", ["4 mức (Chưa đạt, Đạt, Khá, Tốt)", "3 mức (Cần cố gắng, Đạt, Tốt)", "Thang điểm 10 chi tiết"])
        with c2:
            kieu_trinh_bay = st.selectbox("Góc nhìn đánh giá:", ["Giáo viên chấm điểm", "Học sinh tự đánh giá (Self-assessment)", "Đánh giá đồng đẳng (Peer-assessment)"])
        
        btn_rubric = st.button("✨ Xây dựng Rubric", type="primary", use_container_width=True)

    if btn_rubric:
        if not yeu_cau_can_dat.strip():
            st.warning("⚠️ Vui lòng nhập Yêu cầu cần đạt.")
        else:
            with st.spinner("AI đang thiết kế ma trận tiêu chí đánh giá..."):
                prompt = f"""
                Bạn là Chuyên gia đo lường và đánh giá giáo dục.
                Hãy xây dựng một bảng Rubric chi tiết để đánh giá nhiệm vụ: {loai_nhiem_vu}.
                Yêu cầu cần đạt của nhiệm vụ: {yeu_cau_can_dat}.
                
                THÔNG SỐ:
                - Thang đánh giá: {thang_diem}
                - Đối tượng sử dụng rubric: {kieu_trinh_bay} (Hãy điều chỉnh ngôn từ cho phù hợp: VD GV chấm thì dùng từ chuyên môn, HS tự chấm thì dùng đại từ "Tôi làm được...").
                
                YÊU CẦU ĐẦU RA:
                Kẻ một bảng Markdown. Cột dọc đầu tiên là "Các tiêu chí đánh giá" (ít nhất 4 tiêu chí cốt lõi). Các cột ngang tiếp theo là các mức độ đánh giá.
                Trong mỗi ô, mô tả CHUẨN XÁC, CỤ THỂ hành vi học sinh biểu hiện ra, có thể đo lường được.
                """
                if ai_engine:
                    try:
                        res = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown("#### 📑 Bảng Tiêu chí Đánh giá (Rubric)")
                        st.markdown(res)
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
