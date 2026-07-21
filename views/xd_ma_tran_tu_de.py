# -*- coding: utf-8 -*-
import streamlit as st
import json
import re
import pandas as pd
from pathlib import Path
from io import BytesIO

# ============================================================
# KIỂM TRA THƯ VIỆN DOCXTPL
# ============================================================
try:
    from docxtpl import DocxTemplate
except ImportError:
    st.error("⚠️ Thư viện docxtpl chưa được cài đặt. Vui lòng chạy lệnh: pip install docxtpl")

# ============================================================
# SERVICE 1: ĐỌC VÀ TRÍCH XUẤT VĂN BẢN (CHỐNG TRÙNG LẶP)
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
# SERVICE 2: XỬ LÝ JSON VÀ TÍNH TOÁN (ĐỒNG BỘ TEMPLATE)
# ============================================================
class MatrixCalculator:
    @staticmethod
    def parse_ai_json(result_text):
        if not result_text:
            raise ValueError("Hệ thống AI không trả về bất kỳ dữ liệu nào.")
        
        result_text = result_text.strip()
        match = re.search(r"```json\s*(.*?)\s*```", result_text, re.DOTALL | re.IGNORECASE)
        json_str = match.group(1).strip() if match else result_text
            
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
    def prepare_template_context(parsed_data, mon_hoc):
        if not isinstance(parsed_data, dict):
            raise ValueError("Dữ liệu AI phản hồi không đúng cấu trúc.")
            
        ma_tran_raw = parsed_data.get("ma_tran", [])
        dac_ta_raw = parsed_data.get("dac_ta", [])
        
        ma_tran_data = []
        for item in ma_tran_raw:
            nb = MatrixCalculator.to_number(item.get("nb", 0))
            th = MatrixCalculator.to_number(item.get("th", 0))
            vd = MatrixCalculator.to_number(item.get("vd", 0))
            vdc = MatrixCalculator.to_number(item.get("vdc", 0))
            tong_so_cau = nb + th + vd + vdc
            tong_diem = MatrixCalculator.to_number(item.get("tong_diem", 0))
            
            ma_tran_data.append({
                "chu_de": item.get("chu_de", ""),
                "noi_dung": item.get("noi_dung", ""),
                "nb": nb,
                "th": th,
                "vd": vd,
                "vdc": vdc,
                "tong_so_cau": tong_so_cau,
                "tong_diem": tong_diem
            })
            
        dac_ta_data = []
        for item in dac_ta_raw:
            dac_ta_data.append({
                "stt": item.get("stt", 1),
                "chu_de": item.get("chu_de", ""),
                "bai_hoc": item.get("bai_hoc", item.get("noi_dung", "")),
                "yccd": item.get("yccd", ""),
                "tn_nb": MatrixCalculator.to_number(item.get("tn_nb", 0)),
                "tn_hieu": MatrixCalculator.to_number(item.get("tn_hieu", 0)),
                "tn_vd": MatrixCalculator.to_number(item.get("tn_vd", 0)),
                "ds_nb": MatrixCalculator.to_number(item.get("ds_nb", 0)),
                "ds_hieu": MatrixCalculator.to_number(item.get("ds_hieu", 0)),
                "ds_vd": MatrixCalculator.to_number(item.get("ds_vd", 0)),
                "tl_biet": MatrixCalculator.to_number(item.get("tl_biet", 0)),
                "tl_hieu": MatrixCalculator.to_number(item.get("tl_hieu", 0)),
                "tl_vd": MatrixCalculator.to_number(item.get("tl_vd", 0)),
                "tong_diem": MatrixCalculator.to_number(item.get("tong_diem", 0))
            })
            
        context = {
            "MON_HOC": mon_hoc,
            "ma_tran_data": ma_tran_data,
            "dac_ta_data": dac_ta_data
        }
        return context
# ============================================================
# SERVICE 3: ĐỘNG CƠ KẾT XUẤT WORD BẰNG DOCXTPL
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
# 4. VIEW CHÍNH VÀ ĐIỀU HƯỚNG GIAO DIỆN
# ============================================================
def render_xd_ma_tran_tu_de(ai_engine):
    st.markdown("### 🧩 Sinh Ma trận & Đặc tả Đề kiểm tra (Chuẩn Template Word)")
    
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
            with st.spinner("Hệ thống AI đang đọc dữ liệu tệp và phân tích cấu trúc chi tiết..."):
                raw_text = ExamTextExtractor.extract(file_de)
                exam_text = ExamTextExtractor.normalize(raw_text)
                
                if not exam_text:
                    st.error("Không thể đọc được dữ liệu chữ từ tệp tin này.")
                    return
                
                json_schema = """
{
  "ma_tran": [
    {
      "chu_de": "Tên chủ đề",
      "noi_dung": "Tên bài học",
      "nb": 2,
      "th": 1,
      "vd": 1,
      "vdc": 0,
      "tong_diem": 1.5
    }
  ],
  "dac_ta": [
    {
      "stt": 1,
      "chu_de": "Tên chủ đề",
      "bai_hoc": "Tên bài học",
      "yccd": "- Nêu được định nghĩa...\\n- Giải thích được hiện tượng...",
      "tn_nb": 2,
      "tn_hieu": 1,
      "tn_vd": 0,
      "ds_nb": 0,
      "ds_hieu": 0,
      "ds_vd": 0,
      "tl_biet": 0,
      "tl_hieu": 0,
      "tl_vd": 1,
      "tong_diem": 1.5
    }
  ]
}
"""
                prompt = f"""
BẠN LÀ CHUYÊN GIA KHẢO THÍ VÀ BIÊN SOẠN CHƯƠNG TRÌNH GDPT 2018.
NHIỆM VỤ: Phân tích sâu sắc ĐỀ THI Môn {mon_hoc} - {lop} được cung cấp dưới đây. Bóc tách chi tiết từng câu hỏi để xây dựng Ma trận và Bản đặc tả có chuyên môn cao, tường minh, không viết cụt lủn.

NỘI DUNG ĐỀ THI:
{exam_text}

YÊU CẦU ĐẶC TẢ ('dac_ta'):
- Cột 'yccd': Viết chi tiết hành động theo mức độ (Nhận biết: nêu/phát biểu; Thông hiểu: giải thích/so sánh; Vận dụng: tính toán/giải quyết bài toán thực tế). Gạch đầu dòng rõ ràng gắn với nội dung câu hỏi trong đề.

CẤU TRÚC JSON YÊU CẦU ĐẦU RA (CHỈ TRẢ VỀ JSON THUẦN TÚY):
```json
{json_schema}
try:
    result = ai_engine.generate_text(prompt)
    parsed_json = MatrixCalculator.parse_ai_json(result)
    template_context = MatrixCalculator.prepare_template_context(parsed_json, mon_hoc)
    word_bytes = DocxTemplateEngine.render_to_bytes(template_path, template_context)
    
    st.session_state["processed_matrix_data"] = template_context
    st.session_state["download_word_bytes"] = word_bytes
    st.session_state["mt_mon_hoc_file"] = mon_hoc
    st.session_state["mt_lop_file"] = lop
    st.success("🎉 Phân tích đề bài và thiết lập file Word mẫu thành công!")
    
except json.JSONDecodeError:
    st.error("❌ AI trả về dữ liệu không đúng chuẩn định dạng JSON. Vui lòng bấm thử lại.")
except Exception as err:
    st.error(f"❌ Quá trình phân tích thất bại: {str(err)}")

if "processed_matrix_data" in st.session_state:
    st.divider()
    st.markdown("#### 👁️ Xem trước dữ liệu cấu trúc")
    
    data = st.session_state["processed_matrix_data"]
    if data.get("ma_tran_data"):
        st.markdown("**1. Bảng Ma Trận**")
        st.dataframe(pd.DataFrame(data["ma_tran_data"]), use_container_width=True)
        
    if data.get("dac_ta_data"):
        st.markdown("**2. Bản Đặc Tả**")
        st.dataframe(pd.DataFrame(data["dac_ta_data"]), use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    safe_mon = st.session_state.get('mt_mon_hoc_file', 'Mon')
    safe_lop = st.session_state.get('mt_lop_file', 'Lop')
    
    st.download_button(
        label="📥 TẢI XUỐNG FILE WORD MA TRẬN & ĐẶC TẢ (.DOCX)",
        data=st.session_state["download_word_bytes"],
        file_name=f"Ma_tran_Dac_ta_{safe_mon}_{safe_lop}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
        type="primary"
    )
