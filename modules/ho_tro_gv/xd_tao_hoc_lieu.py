# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_tao_hoc_lieu(ai_engine=None):
    st.markdown("### 📚 Trợ lý Thiết kế Học liệu Đa phương tiện")
    st.caption("Tự động sinh nội dung cho Flashcard, Handout, tóm tắt lý thuyết, hoặc kịch bản Slide thuyết trình.")
    
    with st.container(border=True):
        loai_hoc_lieu = st.selectbox("Định dạng đầu ra:", [
            "Bộ thẻ ghi nhớ (Flashcard Q&A)", 
            "Kịch bản Slide (PowerPoint)", 
            "Phiếu học tập (Handout) điền khuyết", 
            "Sơ đồ tư duy (Định dạng Markdown)"
        ])
        noi_dung_goc = st.text_area("Dán nội dung kiến thức gốc vào đây:", height=200, placeholder="Dán nội dung lý thuyết dài từ SGK hoặc đề cương...")
        
        btn_hoc_lieu = st.button("🪄 Tạo Học Liệu", type="primary", use_container_width=True)

    if btn_hoc_lieu:
        if not noi_dung_goc.strip():
            st.warning("⚠️ Vui lòng cung cấp kiến thức gốc.")
        else:
            with st.spinner(f"AI đang chuyển đổi kiến thức thành dạng {loai_hoc_lieu}..."):
                prompt = f"""
                Nhiệm vụ của bạn là chuyển đổi khối kiến thức khô khan thành học liệu trực quan, hấp dẫn cho học sinh THCS.
                
                LOẠI HỌC LIỆU YÊU CẦU: {loai_hoc_lieu}.
                
                NỘI DUNG GỐC:
                {noi_dung_goc}
                
                HƯỚNG DẪN CHI TIẾT TÙY THEO ĐỊNH DẠNG:
                - Nếu là Flashcard: Trình bày dạng bảng (Cột 1: Mặt trước / Khái niệm, Cột 2: Mặt sau / Giải thích).
                - Nếu là Kịch bản Slide: Chia rõ Slide 1, Slide 2... Cung cấp nội dung văn bản (bullets) và gợi ý hình ảnh minh họa cần chèn.
                - Nếu là Phiếu học tập điền khuyết: Viết lại đoạn văn nhưng thay các từ khóa quan trọng bằng dấu [____], và cung cấp bảng đáp án ở cuối.
                - Nếu là Sơ đồ tư duy: Trình bày dạng danh sách phân cấp thụt lề rõ ràng (Sử dụng #, -, *).
                """
                if ai_engine:
                    try:
                        res = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown(f"#### 🎨 Kết quả thiết kế: {loai_hoc_lieu}")
                        st.markdown(res)
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
