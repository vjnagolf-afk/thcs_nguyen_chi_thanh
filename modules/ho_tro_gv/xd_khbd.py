import streamlit as st
import sys
from pathlib import Path
from loguru import logger
from pypdf import PdfReader
sys.path.append(str(Path(__file__).resolve().parents[2]))
from export.export_word import WordExportEngine

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # Danh sách môn học chuẩn
    ds_mon = [
        "Ngữ văn", "Toán", "Ngoại ngữ", "Giáo dục công dân", "Lịch sử và Địa lý", 
        "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", "Công nghệ", 
        "Tin học", "Giáo dục thể chất", "Nghệ thuật", "Giáo dục địa phương", 
        "Hoạt động trải nghiệm, hướng nghiệp"
    ]

    col1, col2, col3, col4 = st.columns(4)
    mon_hoc = col1.selectbox("Môn học", ds_mon)
    lop = col2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    hinh_thuc = col3.selectbox("Chọn hình thức", ["KHBD thu gọn", "Chuẩn 5512", "KHBD Stem"])
    so_tiet = col4.number_input("Số tiết", min_value=1, max_value=20, value=2)
    
    # Các ô bổ sung
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=True)
    yeu_cau = st.text_area("Yêu cầu bổ sung cho AI (Ví dụ: Lồng ghép Năng lực số, tích hợp AI...)")
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    
    c1, c2 = st.columns(2)
    if c1.button("🚀 KHỞI TẠO", type="primary"):
        with st.spinner("⏳ AI đang thiết kế giáo án..."):
            file_context = ""
            if file_tai_len and bam_sat:
                if file_tai_len.name.endswith('.pdf'):
                    reader = PdfReader(file_tai_len)
                    file_context = "\n".join([p.extract_text() for p in reader.pages[:10]])
            
            prompt = f"""Soạn KHBD môn {mon_hoc}, lớp {lop}, {so_tiet} tiết, hình thức {hinh_thuc}.
            YÊU CẦU BẮT BUỘC: 
            1. Lồng ghép nội dung Năng lực số và giáo dục AI.
            2. Trình bày từ mục "I. MỤC TIÊU" (Không có lời chào).
            3. Sử dụng LaTeX cho công thức toán.
            4. {yeu_cau}
            Dữ liệu tham khảo: {file_context[:4000]}"""
            
            st.session_state['khbd_content'] = ai_engine.generate_text(prompt)
            st.session_state['khbd_meta'] = {"ten": "KHBD", "mon": mon_hoc, "lop": lop}
            st.rerun()

    if c2.button("🗑️ XÓA DỮ LIỆU"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.get('khbd_content'):
        st.markdown(st.session_state['khbd_content'])
        if st.button("📥 Xuất file Word"):
            word_bytes = WordExportEngine.export_to_word({
                "ai_generated_content": st.session_state['khbd_content'],
                "is_khbd": True
            })
            st.download_button("Tải file về máy", word_bytes, "KHBD.docx")
