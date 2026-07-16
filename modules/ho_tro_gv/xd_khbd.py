import streamlit as st
import sys
from pathlib import Path
from loguru import logger
from pypdf import PdfReader
sys.path.append(str(Path(__file__).resolve().parents[2]))
from export.export_word import WordExportEngine

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    col1, col2, col3, col4 = st.columns(4)
    mon_hoc = col1.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học Tự nhiên", "Vật lý", "Hóa học", "Sinh học", "Tin học", "Công nghệ"])
    lop = col2.selectbox("Lớp", [f"Lớp {i}" for i in range(6, 13)])
    hinh_thuc = col3.selectbox("Chọn hình thức", ["KHBD thu gọn", "Chuẩn 5512", "KHBD Stem"])
    so_tiet = col4.number_input("Số tiết", min_value=1, max_value=10, value=2)
    
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=True)
    yeu_cau = st.text_area("Yêu cầu bổ sung (VD: Năng lực số, tích hợp AI...)")
    file_tai_len = st.file_uploader("Tài liệu tham khảo", type=["pdf", "txt"])
    
    c1, c2 = st.columns(2)
    if c1.button("🚀 KHỞI TẠO", type="primary"):
        with st.spinner("⏳ AI đang soạn thảo..."):
            file_context = ""
            if file_tai_len and bam_sat:
                reader = PdfReader(file_tai_len)
                file_context = "\n".join([p.extract_text() for p in reader.pages[:10]])
            
            prompt = f"""Soạn KHBD bài '{ten_bai}', môn {mon_hoc}, lớp {lop}, {so_tiet} tiết, hình thức {hinh_thuc}.
            YÊU CẦU BẮT BUỘC: 
            1. Lồng ghép mục tiêu Năng lực số và giáo dục AI.
            2. Trình bày chuyên nghiệp, bắt đầu từ I. MỤC TIÊU (Không có lời chào).
            3. Sử dụng cú pháp LaTeX $...$ cho công thức toán.
            4. {yeu_cau}
            Dữ liệu tham khảo: {file_context[:4000]}"""
            
            st.session_state['khbd_content'] = ai_engine.generate_text(prompt)
            st.session_state['khbd_meta'] = {"ten": ten_bai, "mon": mon_hoc, "lop": lop}
            st.rerun()

    if c2.button("🗑️ XÓA DỮ LIỆU"):
        st.session_state.pop('khbd_content', None)
        st.rerun()

    if st.session_state.get('khbd_content'):
        st.markdown(st.session_state['khbd_content'])
        if st.button("📥 Tải file Word"):
            word_bytes = WordExportEngine.export_to_word({
                "title": st.session_state['khbd_meta']['ten'],
                "ai_generated_content": st.session_state['khbd_content'],
                "is_khbd": True
            })
            st.download_button("Tải ngay", word_bytes, "KHBD.docx")
