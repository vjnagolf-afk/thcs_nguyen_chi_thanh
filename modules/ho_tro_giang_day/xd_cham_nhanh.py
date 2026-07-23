# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_cham_nhanh(ai_engine=None):
    st.markdown("### ⚡ Chấm nhanh tự luận / Đoạn văn")
    st.caption("Giáo viên dán nhanh đoạn văn của học sinh và đáp án chuẩn, AI sẽ đưa ra nhận xét, chỉ lỗi sai và cho điểm ngay lập tức.")

    col_hs, col_gv = st.columns(2)
    
    with col_hs:
        bai_lam = st.text_area("Dán bài làm của Học sinh:", height=250, placeholder="HS viết: Hiện tượng quang hợp xảy ra khi cây hấp thụ khí O2...")
    with col_gv:
        dap_an = st.text_area("Đáp án chuẩn / Thang điểm:", height=250, placeholder="Đáp án đúng: Cây hấp thụ CO2 và nhả O2. Điểm tối đa: 10 điểm.")
        
    if st.button("💯 Chấm bài ngay", type="primary", use_container_width=True):
        if not bai_lam or not dap_an:
            st.warning("Vui lòng điền đủ bài làm và đáp án.")
        else:
            with st.spinner("AI đang chấm điểm và viết lời nhận xét..."):
                prompt = f"""
                Bạn là Giáo viên chấm thi nghiêm khắc nhưng tận tâm.
                Hãy chấm bài làm sau của học sinh dựa trên đáp án chuẩn do giáo viên cung cấp.
                
                ĐÁP ÁN CHUẨN/THANG ĐIỂM:
                {dap_an}
                
                BÀI LÀM CỦA HỌC SINH:
                {bai_lam}
                
                YÊU CẦU ĐẦU RA:
                1. Điểm số (Ước lượng).
                2. Liệt kê các ý học sinh đã làm đúng.
                3. Chỉ ra lỗi sai (sai kiến thức, sai diễn đạt, hoặc thiếu ý).
                4. Lời nhận xét khích lệ để ghi vào sổ.
                """
                if ai_engine:
                    res = ai_engine.generate_text(prompt)
                    st.markdown("---")
                    st.markdown("### 🏆 Kết quả chấm bài")
                    st.markdown(res)
                else:
                    st.error("Chưa kết nối AI.")
