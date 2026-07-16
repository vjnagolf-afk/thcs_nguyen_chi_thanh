import streamlit as st
from docxtpl import DocxTemplate
from jinja2 import Environment, Undefined
from pypdf import PdfReader
from pathlib import Path
from loguru import logger
import io
import json

# Hàm tách JSON an toàn
def extract_json(text):
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("AI không trả về cấu trúc JSON hợp lệ")
    return text[start:end + 1]

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    if "khbd_docx" not in st.session_state: st.session_state.khbd_docx = None
    if "khbd_filename" not in st.session_state: st.session_state.khbd_filename = ""

    # UI Inputs
    col1, col2, col3, col4 = st.columns(4)
    mon_hoc = col1.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học Tự nhiên", "Tiếng Anh", "Tin học", "Công nghệ"])
    lop = col2.selectbox("Lớp", [str(i) for i in range(6, 13)], index=3)
    hinh_thuc = col3.selectbox("Hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    thoi_luong = col4.number_input("Số tiết", min_value=1, value=1)
    
    ten_bai = st.text_input("Tên bài dạy / Chủ đề")
    model_chon = ai_engine.MODELS["flash"] if "Flash" in st.selectbox("🤖 Phiên bản AI", ["Flash (Nhanh)", "Pro (Sâu)"]) else ai_engine.MODELS["pro"]
    
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    bam_sat = st.checkbox("Bám sát nội dung file", value=False)
    yeu_cau_them = st.text_area("Yêu cầu bổ sung")

    tao_btn = st.button("🚀 Soạn KHBD", type="primary")

    if st.session_state.khbd_docx:
        st.download_button("📥 Tải file Word", data=st.session_state.khbd_docx, file_name=st.session_state.khbd_filename)

    if tao_btn:
        if not ten_bai: st.warning("Vui lòng nhập tên bài!")
        else:
            with st.spinner("🤖 AI đang biên soạn..."):
                try:
                    # 1. Đọc tài liệu
                    noi_dung = ""
                    if bam_sat and file_tai_len:
                        if file_tai_len.name.endswith('.pdf'):
                            reader = PdfReader(file_tai_len)
                            for page in reader.pages:
                                txt = page.extract_text()
                                if txt: noi_dung += txt + "\n"
                                if len(noi_dung) > 3000: break
                        elif file_tai_len.name.endswith('.txt'):
                            noi_dung = file_tai_len.getvalue().decode("utf-8")[:3000]
                        noi_dung = f"\n[TÀI LIỆU]: {noi_dung}"

                    # 2. Gọi AI
                    prompt = f"Soạn KHBD bài '{ten_bai}', lớp {lop}, {thoi_luong} tiết. {yeu_cau_them}. {noi_dung}. Trả về JSON chuẩn."
                    response = ai_engine.generate_text(prompt, model_name=model_chon)
                    
                    # 3. Trích xuất và parse JSON an toàn
                    clean_json = extract_json(response)
                    data = json.loads(clean_json)

                    with st.expander("👁️ Xem trước dữ liệu"):
                        st.json(data)

                    # 4. Định vị Template (Pathlib)
                    BASE_DIR = Path(__file__).resolve().parents[2]
                    template_path = BASE_DIR / "templates" / "KHBD_Mau.docx"
                    
                    if not template_path.exists():
                        st.error(f"❌ Không tìm thấy file mẫu:\n{template_path}")
                        return

                    # 5. Render Word
                    doc = DocxTemplate(str(template_path))
                    jinja_env = Environment(undefined=Undefined)
                    doc.render(data, jinja_env=jinja_env)
                    
                    bio = io.BytesIO()
                    doc.save(bio)
                    st.session_state.khbd_docx = bio.getvalue()
                    st.session_state.khbd_filename = f"KHBD_{ten_bai.replace(' ', '_')}.docx"
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                    logger.exception("Lỗi hệ thống")
