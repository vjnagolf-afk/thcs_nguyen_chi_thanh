# -*- coding: utf-8 -*-
import streamlit as st
import sys
import json
import re
from pathlib import Path
from io import BytesIO

# Kiểm tra thư viện template
try:
    from docxtpl import DocxTemplate
except ImportError:
    st.error("⚠️ Thư viện docxtpl chưa được cài đặt. Vui lòng chạy lệnh: pip install docxtpl")

# ============================================================
# SERVICE 1: ĐỌC VÀ TRÍCH XUẤT VĂN BẢN (ExamTextExtractor)
# ============================================================
class ExamTextExtractor:
    @staticmethod
    def extract(uploaded_file):
        if not uploaded_file:
            return ""
        try:
            file_name = uploaded_file.name.lower()
            file_bytes = uploaded_file.getvalue()
            
            if file_name.endswith(".pdf"):
                from pypdf import PdfReader
                reader = PdfReader(BytesIO(file_bytes))
                pages_text = []
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        pages_text.append(extracted.strip())
                return "\n".join(pages_text)
                
            elif file_name.endswith(".docx"):
                from docx import Document
                doc = Document(BytesIO(file_bytes))
                contents = set()
                result = []
                
                for p in doc.paragraphs:
                    text = p.text.strip()
                    if text and text not in contents:
                        result.append(text)
                        contents.add(text)
                        
                for table in doc.tables:
                    for row in table.rows:
                        row_data = []
                        for cell in row.cells:
                            row_data.append(cell.text.strip().replace("\n", " "))
                        row_text = " | ".join(filter(None, row_data))
                        if row_text.strip() and row_text not in contents:
                            result.append(row_text)
                            contents.add(row_text)
                return "\n".join(result)
                
            elif file_name.endswith(".txt"):
                for enc in ["utf-8", "utf-8-sig", "cp1258"]:
                    try:
                        return file_bytes.decode(enc).strip()
                    except Exception:
                        continue
        except Exception as e:
            st.error(f"❌ Lỗi đọc file: {e}")
        return ""

    @staticmethod
    def normalize(text):
        if not text:
            return ""
        clean_text = re.sub(r"\s+", " ", text).strip()
        words = clean_text.split(" ")
        return " ".join(words[:6000])

# ============================================================
# SERVICE 2: BỘ XỬ LÝ LOGIC MA TRẬN (MatrixCalculator)
# ============================================================
class MatrixCalculator:
    @staticmethod
    def parse_ai_json(result_text):
        json_match = re.search(r'```json\n(.*?)\n```', result_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = result_text.strip()
        return json.loads(json_str)

    @staticmethod
    def calculate_totals(parsed_data):
        total = {
            "nb_tl": 0, "nb_tn": 0, "th_tl": 0, "th_tn": 0,
            "vd_tl": 0, "vd_tn": 0, "vdc_tl": 0, "vdc_tn": 0,
            "cau_tl": 0, "cau_tn": 0, "diem_tl": 0.0, "diem_tn": 0.0
        }

        for item in parsed_data.get("ma_tran", []):
            for key in ["nb_tl", "nb_tn", "th_tl", "th_tn", "vd_tl", "vd_tn", "vdc_tl", "vdc_tn"]:
                total[key] += item.get(key, 0)
            
            total["cau_tl"] += item.get("tong_cau_tl", 0)
            total["cau_tn"] += item.get("tong_cau_tn", 0)
            total["diem_tl"] += item.get("tong_diem_tl", 0.0)
            total["diem_tn"] += item.get("tong_diem_tn", 0.0)

        total["diem"] = total["diem_tl"] + total["diem_tn"]

        if total["diem"] > 0:
            total["phan_tram_tl"] = round((total["diem_tl"] / total["diem"]) * 100, 1)
            total["phan_tram_tn"] = round((total["diem_tn"] / total["diem"]) * 100, 1)
        else:
            total["phan_tram_tl"] = 0
            total["phan_tram_tn"] = 0

        parsed_data["tong"] = total
        return parsed_data

# ============================================================
# SERVICE 3: ĐỘNG CƠ XUẤT WORD (DocxTemplateEngine)
# ============================================================
class DocxTemplateEngine:
    @staticmethod
    def render_to_bytes(template_path, context_data):
        doc = DocxTemplate(str(template_path))
        doc.render(context_data)
        bio = BytesIO()
        doc.save(bio)
        return bio.getvalue()

# ============================================================
# 4. VIEW: GIAO DIỆN CHÍNH (render_xd_ma_tran_tu_de)
# ============================================================
def render_xd_ma_tran_tu_de(ai_engine):
    st.markdown("### 🧩 Sinh Ma trận & Đặc tả (Kiến trúc Chuẩn)")
    
    # 1. Thu thập cấu hình
    c1, c2 = st.columns([1, 1])
    mon_hoc = c1.selectbox("Môn", ["Khoa học Tự nhiên", "Toán học", "Ngữ văn", "Ngoại ngữ", "Khác"], key="mt_mon")
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2, key="mt_lop")
    file_de = st.file_uploader("📥 Tải lên đề kiểm tra", type=["pdf", "docx", "txt"], key="mt_file")

    # 2. Xử lý luồng chính
    if st.button("🔍 PHÂN TÍCH ĐỀ & LẬP MA TRẬN", type="primary", use_container_width=True):
        if not file_de:
            st.warning("⚠️ Vui lòng tải lên file đề kiểm tra.")
            st.stop()
            
        # Thư mục templates nằm ngang hàng với thư mục chứa file app.py
        template_path = Path(__file__).resolve().parents[1] / "templates" / "ma_tran_dac_ta_mau.docx"
        if not template_path.exists():
            st.error(f"❌ Không tìm thấy file mẫu tại: {template_path}. Vui lòng tạo thư mục 'templates' và bỏ file mẫu vào.")
            st.stop()

        with st.spinner("⏳ AI đang phân tích từng câu hỏi và gán nhãn nhận thức..."):
            raw_text = ExamTextExtractor.extract(file_de)
            exam_text = ExamTextExtractor.normalize(raw_text)

            # TÁCH ĐỘC LẬP SCHEMA JSON (Theo đề xuất siêu an toàn của thầy)
            json_schema = """
{
  "mon_hoc": "[Điền Môn]",
  "lop": "[Điền Lớp]",
  "ma_tran": [
    {
      "chu_de": "Tên chủ đề",
      "noi_dung": "Đơn vị kiến thức",
      "nb_tl": 0,
      "nb_tn": 8,
      "th_tl": 0,
      "th_tn": 4,
      "vd_tl": 0,
      "vd_tn": 0,
      "vdc_tl": 0,
      "vdc_tn": 0,
      "tong_cau_tl": 0,
      "tong_cau_tn": 12,
      "tong_diem_tl": 0.0,
      "tong_diem_tn": 3.0,
      "tong_diem": 3.0
    }
  ],
  "dac_ta": [
    {
      "stt": 1,
      "chu_de": "Tên chủ đề",
      "noi_dung": "Đơn vị kiến thức",
      "yccd": "- YCCĐ 1.\\n- YCCĐ 2.",
      "cau_tn_nb": 8,
      "cau_tn_th": 4,
      "cau_tn_vd": 0,
      "cau_tn_vdc": 0,
      "cau_tl_nb": 0,
      "cau_tl_th": 0,
      "cau_tl_vd": 0,
      "cau_tl_vdc": 0,
      "ds_cau_hoi": "Câu 1, 2, 3 (NB); Câu 4, 5 (TH)",
      "tong_diem_dt": 3.0
    }
  ]
}
"""

            # NHÚNG SCHEMA VÀO PROMPT
            prompt = f"""
BẠN LÀ HỆ THỐNG XỬ LÝ DỮ LIỆU KHẢO THÍ.
NHIỆM VỤ: Đọc đề kiểm tra, tách từng câu, xác định mức độ nhận thức (NB, TH, VD, VDC), tính điểm và trả về JSON chuẩn. TUYỆT ĐỐI KHÔNG XUẤT VĂN BẢN NÀO KHÁC NGOÀI JSON.

THÔNG TIN: Môn {mon_hoc} | Lớp {lop}
NỘI DUNG ĐỀ THI:
{exam_text}

CẤU TRÚC JSON YÊU CẦU:
```json
{json_schema}
