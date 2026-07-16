import streamlit as st
from docxtpl import DocxTemplate
import io
import json
import PyPDF2
import os
from loguru import logger

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    if "khbd_docx" not in st.session_state:
        st.session_state.khbd_docx = None
    if "khbd_filename" not in st.session_state:
        st.session_state.khbd_filename = ""

    # Giao diện
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học Tự nhiên", "Tiếng Anh", "Tin học", "Công nghệ"])
    with col2:
        lop = st.selectbox("Lớp", [str(i) for i in range(6, 13)], index=3)
    with col3:
        hinh_thuc = st.selectbox("Chọn hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    with col4:
        thoi_luong = st.number_input("Số tiết", min_value=1, value=1)

    ten_bai = st.text_input("Tên bài dạy / Chủ đề")
    loai_ai = st.selectbox("🤖 Phiên bản AI", ["Flash (Nhanh, Mặc định)", "Pro (Thông minh, Suy luận sâu)"])
    
    model_chon = None
    if ai_engine:
        model_chon = ai_engine.MODELS["flash"] if "Flash" in loai_ai else ai_engine.MODELS["pro"]

    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=False)
    yeu_cau_them = st.text_area("Yêu cầu bổ sung")

    # Nút bấm
    tao_btn = st.button("🚀 Soạn KHBD", type="primary")

    if st.session_state.khbd_docx:
        st.download_button("📥 Tải file Word", data=st.session_state.khbd_docx, file_name=st.session_state.khbd_filename)

    if tao_btn:
        if not ten_bai:
            st.warning("Vui lòng nhập tên bài dạy!")
        elif not ai_engine or not model_chon:
            st.error("🔐 AI chưa kết nối!")
        else:
            with st.spinner("🤖 AI đang biên soạn..."):
                try:
                    # 1. Xử lý file
                    noi_dung_tham_khao = ""
                    if bam_sat and file_tai_len:
                        if file_tai_len.name.endswith('.pdf'):
                            reader = PyPDF2.PdfReader(file_tai_len)
                            for page in reader.pages:
                                text = page.extract_text()
                                if text: noi_dung_tham_khao += text + "\n"
                                if len(noi_dung_tham_khao) > 3000: break
                        noi_dung_tham_khao = f"\n[TÀI LIỆU]: {noi_dung_tham_khao}"

                    # 2. Prompt
                    prompt = f"Soạn KHBD cho bài: '{ten_bai}', lớp {lop}, {thoi_luong} tiết. Hình thức: {hinh_thuc}. {yeu_cau_them}. {noi_dung_tham_khao}. TRẢ VỀ JSON CHUẨN."

                    # 3. Gọi AI
                    response = ai_engine.generate_text(prompt, model_name=model_chon)
                    clean_json = response.replace("```json", "").replace("```", "").strip()
                    data_dict = json.loads(clean_json)

                    # 4. Render Word
                    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates", "KHBD_Mau.docx")
                    doc = DocxTemplate(template_path)
                    doc.render(data_dict)
                    
                    bio = io.BytesIO()
                    doc.save(bio)
                    st.session_state.khbd_docx = bio.getvalue()
                    st.session_state.khbd_filename = f"KHBD_{ten_bai.replace(' ', '_')}.docx"
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                    logger.exception("Lỗi sinh KHBD")
