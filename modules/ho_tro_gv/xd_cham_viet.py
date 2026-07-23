# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_cham_viet(ai_engine=None):
    st.markdown("### 📝 Trợ lý Chấm & Chữa bài Tự luận/Viết")
    st.caption("AI hỗ trợ đọc bài làm của học sinh (đoạn văn, bài văn) và chấm điểm chi tiết dựa trên Rubric hoặc đáp án chuẩn.")
    
    with st.container(border=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            bai_lam = st.text_area("Nhập hoặc dán bài làm của học sinh:", height=300, placeholder="Học sinh viết: Trong tác phẩm Lão Hạc, Nam Cao đã thể hiện...")
        with col2:
            rubric = st.text_area("Nhập đáp án chuẩn hoặc tiêu chí chấm (Rubric):", height=300, placeholder="Tiêu chí: 1. Đúng hình thức đoạn văn (2đ). 2. Nêu được giá trị nhân đạo (5đ). 3. Không sai chính tả (3đ)...")
            
        btn_cham = st.button("🚀 Bắt đầu chấm bài chi tiết", type="primary", use_container_width=True)

    if btn_cham:
        if not bai_lam.strip() or not rubric.strip():
            st.warning("⚠️ Vui lòng nhập đầy đủ Bài làm của học sinh và Tiêu chí chấm/Đáp án.")
        else:
            with st.spinner("AI đang đọc, phân tích câu từ và đối chiếu với Rubric..."):
                prompt = f"""
                Bạn là một giáo viên bộ môn dày dặn kinh nghiệm, vô cùng tỉ mỉ nhưng cũng rất tâm lý.
                Hãy chấm bài làm của học sinh dựa CHÍNH XÁC vào Rubric/Đáp án chuẩn do giáo viên cung cấp.

                TIÊU CHÍ CHẤM / ĐÁP ÁN:
                {rubric}

                BÀI LÀM CỦA HỌC SINH:
                {bai_lam}

                YÊU CẦU ĐẦU RA BẮT BUỘC:
                1. Đánh giá theo từng tiêu chí (Chỉ ra học sinh đạt hay không đạt, thiếu ý nào).
                2. Sửa lỗi diễn đạt, chính tả, ngữ pháp trực tiếp (nếu có).
                3. Cho điểm số dự kiến / Thang điểm tổng.
                4. Viết 1-2 câu nhận xét khích lệ để giáo viên ghi vào sổ/vở của học sinh.
                """
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown("#### 💯 Bảng điểm & Nhận xét của AI")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
