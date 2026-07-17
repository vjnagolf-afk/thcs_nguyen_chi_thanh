import streamlit as st
import sys
from pathlib import Path

def render_xd_cham_nhanh(ai_engine):
    st.markdown("### ⚡ Chấm bài nhanh & Phản hồi tức thì")
    
    col1, col2 = st.columns([2, 1])
    dap_an_dung = col1.text_area("Nhập đáp án đúng hoặc tiêu chí chấm:", placeholder="VD: 1A, 2B, 3C... hoặc các ý chính cần có trong bài tự luận ngắn.")
    diem_toi_da = col2.number_input("Điểm tối đa:", min_value=1, max_value=100, value=10)
    
    bai_lam_hs = st.text_area("Dán bài làm của học sinh:", height=150)
    
    if st.button("🚀 CHẤM NHANH", type="primary", use_container_width=True):
        if not dap_an_dung or not bai_lam_hs:
            st.error("Vui lòng nhập đầy đủ đáp án và bài làm!")
        else:
            with st.spinner("⏳ AI đang chấm điểm..."):
                prompt = f"""
                Bạn là trợ lý giáo viên. Hãy chấm bài tập này dựa trên tiêu chí sau:
                - Đáp án/Tiêu chí: {dap_an_dung}
                - Điểm tối đa: {diem_toi_da}
                - Bài làm học sinh: {bai_lam_hs}

                Yêu cầu:
                1. Cho điểm chính xác (theo thang {diem_toi_da}).
                2. Nhận xét ngắn gọn 1-2 câu về ưu điểm và hạn chế.
                3. Trình bày dạng bảng để giáo viên dễ ghi vào sổ.
                """
                try:
                    res = ai_engine.generate_text(prompt)
                    st.markdown("---")
                    st.markdown(res)
                except Exception as e:
                    st.error(f"Lỗi chấm bài: {e}")
