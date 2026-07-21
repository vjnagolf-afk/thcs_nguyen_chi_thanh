# -*- coding: utf-8 -*-
import streamlit as st
import sys
import json
import re
from pathlib import Path
from io import BytesIO

# Import thư viện xử lý Template Word
try:
    from docxtpl import DocxTemplate
except ImportError:
    st.error("⚠️ Thư viện docxtpl chưa được cài đặt. Vui lòng chạy lệnh: pip install docxtpl")

# ============================================================
# 1. BỘ CÔNG CỤ ĐỌC TÀI LIỆU
# ============================================================
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        file_name = uploaded_file.name.lower()
        file_bytes = uploaded_file.getvalue()
        if not file_bytes:
            return ""
            
        if file_name.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(file_bytes))
            pages = [page.extract_text().strip() for page in reader.pages if page.extract_text()]
            return "\n\n".join(pages).strip()
            
        elif file_name.endswith(".docx"):
            from docx import Document
            document = Document(BytesIO(file_bytes))
            contents = []
            seen_texts = set()
            for paragraph in document.paragraphs:
                text = paragraph.text.strip()
                if text and text not in seen_texts:
                    contents.append(text)
                    seen_texts.add(text)
            for table in document.tables:
                for row in table.rows:
                    row_data = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    row_text = " | ".join(filter(None, row_data))
                    if row_text.strip() and row_text not in seen_texts:
                        contents.append(row_text)
                        seen_texts.add(row_text)
            return "\n".join(contents).strip()
            
        elif file_name.endswith(".txt"):
            for encoding in ["utf-8", "utf-8-sig", "cp1258"]:
                try: return file_bytes.decode(encoding).strip()
                except: continue
    except Exception as e:
        st.error(f"❌ Lỗi đọc tài liệu: {e}")
    return ""

def normalize_outline(text):
    if not text: return ""
    clean_text = re.sub(r"\s+", " ", text).strip()
    return " ".join(clean_text.split(" ")[:6000]) # Tránh tràn Token

# ============================================================
# 2. GIAO DIỆN CHÍNH
# ============================================================
def render_xd_ma_tran_tu_de(ai_engine):
    st.markdown("### 🧩 Sinh Ma trận & Đặc tả (Kiến trúc JSON -> Template)")
    
    c1, c2 = st.columns([1, 1])
    mon_hoc = c1.selectbox("Môn", ["Khoa học Tự nhiên", "Toán học", "Ngữ văn", "Ngoại ngữ", "Khác"], key="mt_mon_hoc")
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2, key="mt_lop")

    file_de = st.file_uploader("📥 Tải lên đề kiểm tra (Hỗ trợ PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="mt_file_upload")

    if st.button("🔍 PHÂN TÍCH ĐỀ & LẬP MA TRẬN", type="primary", use_container_width=True):
        if not file_de:
            st.warning("⚠️ Vui lòng tải lên file đề kiểm tra.")
            st.stop()
            
        # Kiểm tra template có tồn tại không
        template_path = Path(__file__).resolve().parents[2] / "templates" / "ma_tran_mau.docx"
        if not template_path.exists():
            st.error(f"❌ Không tìm thấy file mẫu Word tại: {template_path}. Thầy cần tạo thư mục 'templates' và đặt file 'ma_tran_mau.docx' vào đó.")
            st.stop()

        with st.spinner("⏳ AI đang bóc tách câu hỏi và xuất dữ liệu JSON..."):
            raw_text = extract_text_from_file(file_de)
            exam_text = normalize_outline(raw_text)

            # --- PROMPT ÉP TRẢ VỀ JSON THUẦN TÚY ---
            json_prompt = f"""
BẠN LÀ HỆ THỐNG XỬ LÝ DỮ LIỆU KHẢO THÍ.
NHIỆM VỤ: Phân tích ĐỀ KIỂM TRA ĐÃ CÓ, đếm số lượng câu, phân loại mức độ nhận thức và TRẢ VỀ ĐỊNH DẠNG JSON CHUẨN (MÁY ĐỌC). TUYỆT ĐỐI KHÔNG XUẤT VĂN BẢN NÀO KHÁC NGOÀI JSON.

THÔNG TIN ĐỀ THI: Môn: {mon_hoc} | Lớp: {lop}
NỘI DUNG ĐỀ:
{exam_text}

YÊU CẦU JSON BẮT BUỘC:
Trả về 1 chuỗi JSON chứa 2 mảng chính: "ma_tran" và "dac_ta".
Định dạng mẫu (Tuân thủ tuyệt đối key):
```json
{{
  "mon_hoc": "{mon_hoc}",
  "lop": "{lop}",
  "ma_tran": [
    {{
      "chu_de": "Tên chủ đề 1",
      "noi_dung": "Nội dung bài học",
      "nb_tl": 0, "nb_tn": 8,
      "th_tl": 0, "th_tn": 4,
      "vd_tl": 0, "vd_tn": 0,
      "vdc_tl": 0, "vdc_tn": 0,
      "tong_cau_tl": 0,
      "tong_cau_tn": 12,
      "tong_diem": 4.0
    }}
  ],
  "dac_ta": [
    {{
      "stt": 1,
      "chu_de": "Tên chủ đề 1",
      "noi_dung": "Nội dung bài học",
      "yccd": "- Biết khái niệm...\\n- Hiểu cách tính...",
      "cau_tn_nb": 8, "cau_tn_th": 4, "cau_tn_vd": 0,
      "cau_tl_nb": 0, "cau_tl_th": 0, "cau_tl_vd": 0,
      "tong_diem_dt": 4.0
    }}
  ]
}}
