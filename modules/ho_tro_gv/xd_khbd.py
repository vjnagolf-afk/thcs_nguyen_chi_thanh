import streamlit as st
from docxtpl import DocxTemplate
from jinja2 import Environment, Undefined
from pathlib import Path
from loguru import logger
import io
import json
from pypdf import PdfReader

def extract_json(text):
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1: raise ValueError("AI không trả về JSON")
    return text[start:end + 1]

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # 1. Giao diện Input
    col1, col2 = st.columns(2)
    ten_bai = col1.text_input("Tên bài dạy")
    mon_hoc = col2.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học Tự nhiên", "Tiếng Anh"])
    
    col3, col4 = st.columns(2)
    lop = col3.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
    hinh_thuc = col4.selectbox("Hình thức", ["Chuẩn 5512", "KHBD thu gọn"])
    
    model_choice = st.selectbox("🤖 Phiên bản AI", ["Flash (Nhanh)", "Pro (Sâu)"])
    model_chon = ai_engine.MODELS["flash"] if "Flash" in model_choice else ai_engine.MODELS["pro"]
    
    file_tai_len = st.file_uploader("Tài liệu tham khảo", type=["pdf", "txt"])

    # 2. Xử lý Logic
    if st.button("🚀 Soạn KHBD"):
        if not ten_bai: st.warning("Vui lòng nhập tên bài!")
        else:
            with st.spinner("⏳ AI đang soạn thảo..."):
                file_context = ""
                if file_tai_len:
                    reader = PdfReader(file_tai_len)
                    for page in reader.pages:
                        file_context += (page.extract_text() or "")
                
                # Prompt chuẩn hóa cấu trúc
                prompt = f"""Soạn bài {ten_bai}, môn {mon_hoc}, lớp {lop}, hình thức {hinh_thuc}.
                Dựa trên tài liệu: {file_context[:3000]}.
                Trả về JSON với các key: TEN_BAI, MON_HOC, LOP, HINH_THUC, MUC_TIEU, THIET_BI, HOAT_DONG_DAY_HOC, DANH_GIA."""
                
                try:
                    response = ai_engine.generate_text(prompt, model_name=model_chon)
                    st.session_state['khbd_data'] = json.loads(extract_json(response))
                    st.success("Soạn xong!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    # 3. Xuất Word chuyên nghiệp
    if 'khbd_data' in st.session_state:
        data = st.session_state['khbd_data']
        st.json(data)
        
        if st.button("📄 Tạo file Word"):
            BASE_DIR = Path(__file__).resolve().parents[2]
            template_path = BASE_DIR / "templates" / "KHBD_Mau.docx"
            
            try:
                doc = DocxTemplate(str(template_path))
                doc.render(data, jinja_env=Environment(undefined=Undefined))
                
                bio = io.BytesIO()
                doc.save(bio)
                st.session_state['khbd_file'] = bio.getvalue()
            except Exception as e:
                st.error(f"Lỗi render: {e}")

    if 'khbd_file' in st.session_state:
        st.download_button(
            "📥 Tải file KHBD",
            data=st.session_state['khbd_file'],
            file_name=f"KHBD_{st.session_state['khbd_data']['TEN_BAI']}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
