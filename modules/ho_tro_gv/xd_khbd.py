import streamlit as st
from docxtpl import DocxTemplate, Jinja2
import io
import json
import PyPDF2
import os
from loguru import logger

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # Session State
    if "khbd_docx" not in st.session_state: st.session_state.khbd_docx = None
    if "khbd_filename" not in st.session_state: st.session_state.khbd_filename = ""

    # Giao diện Input
    col1, col2, col3, col4 = st.columns(4)
    mon_hoc = col1.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học Tự nhiên", "Tiếng Anh", "Tin học", "Công nghệ"])
    lop = col2.selectbox("Lớp", [str(i) for i in range(6, 13)], index=3)
    hinh_thuc = col3.selectbox("Hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    thoi_luong = col4.number_input("Số tiết", min_value=1, value=1)
    
    ten_bai = st.text_input("Tên bài dạy / Chủ đề")
    loai_ai = st.selectbox("🤖 Phiên bản AI", ["Flash (Nhanh)", "Pro (Sâu)"])
    model_chon = ai_engine.MODELS["flash"] if "Flash" in loai_ai else ai_engine.MODELS["pro"]
    
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    bam_sat = st.checkbox("Bám sát nội dung file", value=False)
    yeu_cau_them = st.text_area("Yêu cầu bổ sung")

    # Nút điều khiển
    tao_btn = st.button("🚀 Soạn KHBD", type="primary")

    if st.session_state.khbd_docx:
        st.download_button("📥 Tải file Word", data=st.session_state.khbd_docx, file_name=st.session_state.khbd_filename)

    if tao_btn:
        if not ten_bai: st.warning("Vui lòng nhập tên bài!")
        else:
            with st.spinner("🤖 AI đang biên soạn..."):
                try:
                    # 1. Đọc file
                    noi_dung = ""
                    if bam_sat and file_tai_len:
                        if file_tai_len.name.endswith('.pdf'):
                            reader = PyPDF2.PdfReader(file_tai_len)
                            for page in reader.pages:
                                txt = page.extract_text()
                                if txt: noi_dung += txt + "\n"
                                if len(noi_dung) > 3000: break
                        noi_dung = f"\n[TÀI LIỆU]: {noi_dung}"

                    # 2. Gọi AI
                    prompt = f"Soạn KHBD bài '{ten_bai}', lớp {lop}, {thoi_luong} tiết. {yeu_cau_them}. {noi_dung}. Trả về JSON chuẩn."
                    response = ai_engine.generate_text(prompt, model_name=model_chon)
                    clean_json = response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)

                    # 3. Hiển thị Preview
                    st.success("AI đã soạn xong!")
                    with st.expander("👁️ Xem trước dữ liệu"):
                        st.json(data)

                    # 4. Render Word với Jinja2 (An toàn hơn)
                    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates", "KHBD_Mau.docx")
                    doc = DocxTemplate(template_path)
                    
                    # Cấu hình Jinja để không xóa biến nếu thiếu Key
                    jinja_env = Jinja2(undefined='keep') 
                    doc.render(data, jinja_env=jinja_env)
                    
                    bio = io.BytesIO()
                    doc.save(bio)
                    st.session_state.khbd_docx = bio.getvalue()
                    st.session_state.khbd_filename = f"KHBD_{ten_bai.replace(' ', '_')}.docx"
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                    logger.exception("Lỗi render Word")
