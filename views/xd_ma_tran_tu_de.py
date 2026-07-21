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
# 2. BỘ CÔNG CỤ XỬ LÝ LOGIC (JSON & TÍNH TOÁN)
# ============================================================
def extract_json_from_ai(result_text):
    """Bóc tách chuỗi JSON thuần túy từ câu trả lời của AI."""
    json_match = re.search(r'```json\n(.*?)\n```', result_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = result_text.strip()
    return json.loads(json_str)

def calculate_matrix_totals(parsed_data):
    """Tính toán lại tổng điểm và tổng số câu để đảm bảo chính xác tuyệt đối."""
    t_nb_tl = t_nb_tn = t_th_tl = t_th_tn = t_vd_tl = t_vd_tn = t_vdc_tl = t_vdc_tn = 0
    t_cau_tl = t_cau_tn = t_diem = 0.0
    
    for item in parsed_data.get("ma_tran", []):
        t_nb_tl += item.get("nb_tl", 0); t_nb_tn += item.get("nb_tn", 0)
        t_th_tl += item.get("th_tl", 0); t_th_tn += item.get("th_tn", 0)
        t_vd_tl += item.get("vd_tl", 0); t_vd_tn += item.get("vd_tn", 0)
        t_vdc_tl += item.get("vdc_tl", 0); t_vdc_tn += item.get("vdc_tn", 0)
        t_cau_tl += item.get("tong_cau_tl", 0); t_cau_tn += item.get("tong_cau_tn", 0)
        t_diem += item.get("tong_diem", 0.0)

    total_cau = t_cau_tl + t_cau_tn
    parsed_data["tong"] = {
        "nb_tl": t_nb_tl, "nb_tn": t_nb_tn, "th_tl": t_th_tl, "th_tn": t_th_tn,
        "vd_tl": t_vd_tl, "vd_tn": t_vd_tn, "vdc_tl": t_vdc_tl, "vdc_tn": t_vdc_tn,
        "cau_tl": t_cau_tl, "cau_tn": t_cau_tn, "diem": t_diem,
        "phan_tram_tl": (t_cau_tl / total_cau * 100) if total_cau > 0 else 0,
        "phan_tram_tn": (t_cau_tn / total_cau * 100) if total_cau > 0 else 0
    }
    return parsed_data
# ============================================================
# 3. BỘ CÔNG CỤ KẾT XUẤT WORD
# ============================================================
def generate_word_from_template(template_path, context_data):
    """Đổ dữ liệu Dictionary vào file Word Template và trả về định dạng Bytes."""
    doc = DocxTemplate(str(template_path))
    doc.render(context_data)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()
# ============================================================
# 4. GIAO DIỆN HIỂN THỊ CHÍNH
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
            
        template_path = Path(__file__).resolve().parents[2] / "templates" / "ma_tran_mau.docx"
        if not template_path.exists():
            st.error(f"❌ Không tìm thấy file mẫu Word tại: {template_path}.")
            st.stop()

        with st.spinner("⏳ AI đang bóc tách câu hỏi và xuất dữ liệu JSON..."):
            raw_text = extract_text_from_file(file_de)
            exam_text = normalize_outline(raw_text)

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
      "chu_de": "Tên chủ đề 1", "noi_dung": "Nội dung bài học",
      "nb_tl": 0, "nb_tn": 8, "th_tl": 0, "th_tn": 4,
      "vd_tl": 0, "vd_tn": 0, "vdc_tl": 0, "vdc_tn": 0,
      "tong_cau_tl": 0, "tong_cau_tn": 12, "tong_diem": 4.0
    }}
  ],
  "dac_ta": [
    {{
      "stt": 1, "chu_de": "Tên chủ đề 1", "noi_dung": "Nội dung bài học",
      "yccd": "- Biết khái niệm...\\n- Hiểu cách tính...",
      "cau_tn_nb": 8, "cau_tn_th": 4, "cau_tn_vd": 0,
      "cau_tl_nb": 0, "cau_tl_th": 0, "cau_tl_vd": 0,
      "tong_diem_dt": 4.0
    }}
  ]
}}
"""
try:
# 1. Gọi AI
result = ai_engine.generate_text(json_prompt)
# 2. Xử lý Dữ liệu
            parsed_data = extract_json_from_ai(result)
            final_data = calculate_matrix_totals(parsed_data)
            
            # 3. Đổ vào Word
            word_bytes = generate_word_from_template(template_path, final_data)
            
            # 4. Lưu trạng thái
            st.session_state["mt_word_bytes"] = word_bytes
            st.session_state["mt_filename"] = file_de.name
            
            st.success("✅ AI phân tích JSON và chèn vào file Word mẫu thành công tuyệt đối!")
            st.rerun()

        except json.JSONDecodeError:
            st.error("❌ AI không trả về đúng chuẩn JSON. Vui lòng thử lại.")
        except Exception as e:
            st.error(f"❌ Lỗi hệ thống: {e}")

# --- KHỐI HIỂN THỊ KẾT QUẢ TẢI XUỐNG ---
if "mt_word_bytes" in st.session_state:
    st.divider()
    st.success("🎉 Dữ liệu đã được liên kết với file Word mẫu của trường. Bảng biểu và Gộp ô được giữ nguyên 100%.")
    
    c_btn1, c_btn2 = st.columns(2)
    c_btn1.download_button(
        "📥 TẢI XUỐNG MA TRẬN ĐẶC TẢ (.DOCX)", 
        data=st.session_state["mt_word_bytes"], 
        file_name=f"MaTran_DacTa_{st.session_state.get('mt_filename', 'HoanChinh')}.docx", 
        use_container_width=True, 
        type="primary"
    )
    if c_btn2.button("🗑️ XÓA VÀ LÀM LẠI", use_container_width=True):
        st.session_state.pop("mt_word_bytes", None)
        st.session_state.pop("mt_filename", None)
        st.rerun()
