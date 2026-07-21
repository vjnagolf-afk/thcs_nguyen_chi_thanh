# -*- coding: utf-8 -*-
import streamlit as st
import json
import re
import pandas as pd
from pathlib import Path
from io import BytesIO

# ============================================================
# KIỂM TRA THƯ VIỆN
# ============================================================
try:
    from docxtpl import DocxTemplate
except ImportError:
    st.error("⚠️ Thư viện docxtpl chưa được cài đặt. Vui lòng chạy lệnh: pip install docxtpl")

# ============================================================
# SERVICE 1: ĐỌC VÀ TRÍCH XUẤT VĂN BẢN (TỐI ƯU CHỐNG TRÙNG)
# ============================================================
class ExamTextExtractor:
    @staticmethod
    def extract(uploaded_file):
        if not uploaded_file:
            return ""
        try:
            file_name = uploaded_file.name.lower()
            file_bytes = uploaded_file.getvalue()
            
            # XỬ LÝ FILE PDF
            if file_name.endswith(".pdf"):
                from pypdf import PdfReader
                reader = PdfReader(BytesIO(file_bytes))
                pages_text = []
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        pages_text.append(extracted.strip())
                return "\n".join(pages_text)
                
            # XỬ LÝ FILE DOCX (Loại bỏ trùng lặp phần tử bảng)
            elif file_name.endswith(".docx"):
                from docx import Document
                doc = Document(BytesIO(file_bytes))
                result = []
                
                table_texts = set()
                for table in doc.tables:
                    for row in table.rows:
                        row_data = []
                        for cell in row.cells:
                            cell_text = cell.text.strip()
                            if cell_text:
                                for p in cell.paragraphs:
                                    p_txt = p.text.strip()
                                    if p_txt:
                                        table_texts.add(p_txt)
                            cell_text_clean = cell_text.replace("\n", " ")
                            row_data.append(cell_text_clean)
                        
                        row_text = " | ".join(filter(None, row_data))
                        if row_text:
                            result.append(row_text)
                
                for paragraph in doc.paragraphs:
                    text = paragraph.text.strip()
                    if text and (text not in table_texts) and (text not in result):
                        result.append(text)
                
                return "\n".join(result)
            
            # XỬ LÝ FILE TXT
            elif file_name.endswith(".txt"):
                for encoding in ["utf-8", "utf-8-sig", "cp1258"]:
                    try:
                        return file_bytes.decode(encoding).strip()
                    except Exception:
                        continue
                raise ValueError("Không thể giải mã file TXT.")
                
        except Exception as e:
            raise RuntimeError(f"Lỗi đọc định dạng file {file_name}: {str(e)}")
        return ""

    @staticmethod
    def normalize(text):
        if not text:
            return ""
        clean_text = re.sub(r"\s+", " ", text).strip()
        words = clean_text.split(" ")
        return " ".join(words[:12000])
# ============================================================
# SERVICE 2: XỬ LÝ JSON VÀ TÍNH TOÁN MA TRẬN
# ============================================================
class MatrixCalculator:
    @staticmethod
    def parse_ai_json(result_text):
        if not result_text:
            raise ValueError("Hệ thống AI không trả về bất kỳ dữ liệu nào.")
        
        result_text = result_text.strip()
        match = re.search(r"```json\s*(.*?)\s*```", result_text, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1).strip()
        else:
            json_str = result_text
            
        if not json_str.startswith("{"):
            start = json_str.find("{")
            end = json_str.rfind("}")
            if start != -1 and end != -1:
                json_str = json_str[start:end + 1]
                
        return json.loads(json_str)

    @staticmethod
    def to_number(value):
        try:
            if value is None:
                return 0
            if isinstance(value, str):
                value = value.replace(",", ".")
                return float(value) if "." in value else int(value)
            return value
        except Exception:
            return 0

    @staticmethod
    def calculate_totals(parsed_data):
        if not isinstance(parsed_data, dict):
            raise ValueError("Dữ liệu AI phản hồi không đúng cấu trúc.")
        if "ma_tran" not in parsed_data or "dac_ta" not in parsed_data:
            raise ValueError("Dữ liệu thiếu trường 'ma_tran' hoặc 'dac_ta'.")
            
        total = {
            "nb_tl": 0, "nb_tn": 0, "th_tl": 0, "th_tn": 0,
            "vd_tl": 0, "vd_tn": 0, "vdc_tl": 0, "vdc_tn": 0,
            "cau_tl": 0, "cau_tn": 0, "diem_tl": 0.0, "diem_tn": 0.0, "diem": 0.0
        }
        
        for item in parsed_data["ma_tran"]:
            tong_cau_tl = (MatrixCalculator.to_number(item.get("nb_tl", 0)) +
                           MatrixCalculator.to_number(item.get("th_tl", 0)) +
                           MatrixCalculator.to_number(item.get("vd_tl", 0)) +
                           MatrixCalculator.to_number(item.get("vdc_tl", 0)))
                           
            tong_cau_tn = (MatrixCalculator.to_number(item.get("nb_tn", 0)) +
                           MatrixCalculator.to_number(item.get("th_tn", 0)) +
                           MatrixCalculator.to_number(item.get("vd_tn", 0)) +
                           MatrixCalculator.to_number(item.get("vdc_tn", 0)))
            
            item["tong_cau_tl"] = tong_cau_tl
            item["tong_cau_tn"] = tong_cau_tn
            
            diem_tl = MatrixCalculator.to_number(item.get("tong_diem_tl", 0))
            diem_tn = MatrixCalculator.to_number(item.get("tong_diem_tn", 0))
            item["tong_diem_tl"] = diem_tl
            item["tong_diem_tn"] = diem_tn
            item["tong_diem"] = diem_tl + diem_tn
            
            for key in ["nb_tl", "nb_tn", "th_tl", "th_tn", "vd_tl", "vd_tn", "vdc_tl", "vdc_tn"]:
                total[key] += MatrixCalculator.to_number(item.get(key, 0))
                
            total["cau_tl"] += tong_cau_tl
            total["cau_tn"] += tong_cau_tn
            total["diem_tl"] += diem_tl
            total["diem_tn"] += diem_tn
            
        total["diem"] = total["diem_tl"] + total["diem_tn"]
        
        if total["diem"] > 0:
            total["phan_tram_tl"] = round(total["diem_tl"] / total["diem"] * 100, 1)
            total["phan_tram_tn"] = round(total["diem_tn"] / total["diem"] * 100, 1)
        else:
            total["phan_tram_tl"] = 0
            total["phan_tram_tn"] = 0
            
        parsed_data["tong"] = total
        return parsed_data

# ============================================================
# SERVICE 3: ĐỘNG CƠ GHI DỮ LIỆU VÀO WORD (DÙNG DOCXTPL AN TOÀN)
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
# 4. VIEW CHÍNH VÀ ĐIỀU HƯỚNG GIAO DIỆN (PHẦN 4a)
# ============================================================
def render_xd_ma_tran_tu_de(ai_engine):
    st.markdown("### 🧩 Sinh Ma trận & Đặc tả Đề kiểm tra")
    
    c1, c2 = st.columns(2)
    mon_hoc = c1.selectbox("Môn học", ["Khoa học Tự nhiên", "Toán học", "Ngữ văn", "Ngoại ngữ", "Khác"], key="mt_mon")
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2, key="mt_lop")
    
    file_de = st.file_uploader("Tải lên tệp đề kiểm tra hiện tại", type=["pdf", "docx", "txt"], key="mt_file")
    
    if st.button("PHÂN TÍCH ĐỀ & LẬP MA TRẬN", type="primary", use_container_width=True):
        if not file_de:
            st.warning("Vui lòng đính kèm và tải lên file đề kiểm tra trước khi thực hiện phân tích.")
            return
            
        template_path = Path(__file__).resolve().parents[1] / "templates" / "ma_tran_dac_ta_mau.docx"
        if not template_path.exists():
            st.error(f"Hệ thống thiếu file cấu trúc mẫu tại đường dẫn: {template_path}")
            return
            
        try:
            with st.spinner("Hệ thống AI đang đọc dữ liệu tệp và phân tích cấu trúc đề..."):
                raw_text = ExamTextExtractor.extract(file_de)
                exam_text = ExamTextExtractor.normalize(raw_text)
                
                if not exam_text:
                    st.error("Không thể đọc được dữ liệu chữ từ tệp tin này.")
                    return
                
                json_schema = """
{
  "mon_hoc": "[Điền Môn]",
  "lop": "[Điền Lớp]",
  "ma_tran": [
    {
      "chu_de": "Tên chủ đề",
      "noi_dung": "Đơn vị kiến thức",
      "nb_tl": 0, "nb_tn": 8, "th_tl": 0, "th_tn": 4,
      "vd_tl": 0, "vd_tn": 0, "vdc_tl": 0, "vdc_tn": 0,
      "tong_cau_tl": 0, "tong_cau_tn": 12,
      "tong_diem_tl": 0.0, "tong_diem_tn": 3.0, "tong_diem": 3.0
    }
  ],
  "dac_ta": [
    {
      "stt": 1,
      "chu_de": "Tên chủ đề",
      "noi_dung": "Đơn vị kiến thức",
      "yccd": "- YCCĐ 1.\\n- YCCĐ 2.",
      "cau_tn_nb": 8, "cau_tn_th": 4, "cau_tn_vd": 0, "cau_tn_vdc": 0,
      "cau_tl_nb": 0, "cau_tl_th": 0, "cau_tl_vd": 0, "cau_tl_vdc": 0,
      "ds_cau_hoi": "Câu 1, 2, 3 (NB); Câu 4, 5 (TH)",
      "tong_diem_dt": 3.0
    }
  ]
}
"""
                prompt = f"""
BẠN LÀ HỆ THỐNG XỬ LÝ DỮ LIỆU KHẢO THÍ.
NHIỆM VỤ: Đọc đề kiểm tra, tách từng câu, xác định mức độ nhận thức (NB, TH, VD, VDC), tính điểm và trả về JSON chuẩn. TUYỆT ĐỐI KHÔNG XUẤT VĂN BẢN NÀO KHÁC NGOÀI JSON.

THÔNG TIN: Môn {mon_hoc} | Lớp {lop}
NỘI DUNG ĐỀ THI:
{exam_text}

QUY TẮC LOGIC ĐIỂM SỐ (BẮT BUỘC):
1. Tính điểm thật chính xác (Trắc nghiệm thường 0.25đ/câu).
2. tong_diem = tong_diem_tl + tong_diem_tn.
3. Hãy đảm bảo tính toán khớp 100% số liệu giữa mảng 'ma_tran' và mảng 'dac_ta'.

CẤU TRÚC JSON YÊU CẦU:
```json
{json_schema}
"""
---

### ĐOẠN 4b: Gọi AI, Tính toán và Giao diện kết quả
*(Thầy copy đoạn này dán nối tiếp ngay phía dưới Đoạn 4a - chú ý lề của chữ `# Sử dụng...` đang lùi vào vừa đúng khối `with st.spinner`)*

```python
                # ============================================================
                # 4. VIEW CHÍNH VÀ ĐIỀU HƯỚNG GIAO DIỆN (PHẦN 4b - Nối tiếp)
                # ============================================================
                # Sử dụng hàm generate_text chuẩn
                result = ai_engine.generate_text(prompt)
                
                parsed_data = MatrixCalculator.parse_ai_json(result)
                final_data = MatrixCalculator.calculate_totals(parsed_data)
                
                # Dùng DocxTemplateEngine thay vì WordMatrixEngine can thiệp thủ công
                word_bytes = DocxTemplateEngine.render_to_bytes(template_path, final_data)
                
                st.session_state["processed_matrix_data"] = final_data
                st.session_state["download_word_bytes"] = word_bytes
                st.session_state["mt_mon_hoc_file"] = mon_hoc
                st.session_state["mt_lop_file"] = lop
                st.success("🎉 Phân tích đề bài và tự động thiết lập ma trận thành công!")

        except json.JSONDecodeError:
            st.error("❌ AI trả về dữ liệu không đúng chuẩn JSON. Vui lòng thử lại.")
        except Exception as err:
            st.error(f"❌ Quá trình phân tích thất bại: {str(err)}")
            
    # --- HIỂN THỊ XEM TRƯỚC VÀ NÚT TẢI XUỐNG ---
    if "processed_matrix_data" in st.session_state:
        st.divider()
        st.markdown("#### Đã phân tích - Xem trước bảng dữ liệu ma trận sơ bộ")
        
        data = st.session_state["processed_matrix_data"]
        
        if "ma_tran" in data and data["ma_tran"]:
            st.markdown("**1. MA TRẬN**")
            df_mt = pd.DataFrame(data["ma_tran"])
            st.dataframe(df_mt, use_container_width=True)
            
        if "dac_ta" in data and data["dac_ta"]:
            st.markdown("**2. BẢN ĐẶC TẢ**")
            df_dt = pd.DataFrame(data["dac_ta"])
            st.dataframe(df_dt, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        safe_mon = st.session_state.get('mt_mon_hoc_file', 'Mon')
        safe_lop = st.session_state.get('mt_lop_file', 'Lop')
        
        c_btn1, c_btn2 = st.columns(2)
        c_btn1.download_button(
            label="📥 TẢI XUỐNG FILE WORD MA TRẬN & ĐẶC TẢ (.DOCX)",
            data=st.session_state["download_word_bytes"],
            file_name=f"Ma_tran_Dac_ta_{safe_mon}_{safe_lop}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            type="primary"
        )
        if c_btn2.button("🗑️ ĐÓNG & LÀM LẠI", use_container_width=True):
            st.session_state.pop("processed_matrix_data", None)
            st.session_state.pop("download_word_bytes", None)
            st.rerun()
