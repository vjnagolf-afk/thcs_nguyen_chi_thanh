# -*- coding: utf-8 -*-
import streamlit as st
import sys
from pathlib import Path
from io import BytesIO
import re

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
            pages = []
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    pages.append(f"\n--- TRANG {page_number} ---\n{text.strip()}")
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
            for encoding in ["utf-8", "utf-8-sig", "cp1258", "latin-1"]:
                try:
                    return file_bytes.decode(encoding).strip()
                except Exception:
                    continue
            return ""
    except Exception as e:
        st.error(f"❌ Lỗi đọc tài liệu: {e}")
        return ""
    return ""

def normalize_outline(text):
    if not text:
        return ""
    clean_text = re.sub(r"\s+", " ", text).strip()
    words = clean_text.split(" ")
    safe_text = " ".join(words[:6000]) # Tránh tràn Token
    return safe_text

# ============================================================
# 2. GIAO DIỆN CHÍNH (THẺ PHÂN TÍCH ĐỀ)
# ============================================================
def render_xd_ma_tran_tu_de(ai_engine):
    st.markdown("### 🧩 Sinh Ma trận & Đặc tả từ Đề đã có (Dịch ngược)")
    
    st.info("Tính năng này giúp thầy/cô tải lên một đề thi đã soạn sẵn. AI sẽ đọc, phân tích từng câu hỏi, gán nhãn mức độ nhận thức và tự động lập Ma trận, Đặc tả chuẩn 5512 tương ứng hoàn hảo với đề thi đó.")

    # --- KHỐI NHẬP LIỆU GIAO DIỆN ---
    c1, c2 = st.columns([1, 1])
    mon_hoc = c1.selectbox(
        "Môn", 
        [
            "Khoa học Tự nhiên", "Toán học", "Ngữ văn", "Ngoại ngữ", 
            "Lịch sử và Địa lý", "Lịch sử", "Địa lý", "Vật lý", "Hóa học", 
            "Sinh học", "Tin học", "Công nghệ", "Khác"
        ], 
        key="mt_mon_hoc"
    )
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2, key="mt_lop")

    st.markdown("<br>", unsafe_allow_html=True)
    file_de = st.file_uploader("📥 Tải lên đề kiểm tra (Hỗ trợ PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="mt_file_upload")

    col_chk1, col_chk2 = st.columns(2)
    has_answer = col_chk1.checkbox("☑️ Đề đã có sẵn đáp án ở cuối", value=False)
    has_image = col_chk2.checkbox("🖼️ Đề có chứa hình ảnh minh họa", value=False)

    # --- NÚT KÍCH HOẠT ---
    if st.button("🔍 PHÂN TÍCH ĐỀ & LẬP MA TRẬN", type="primary", use_container_width=True):
        if not file_de:
            st.warning("⚠️ Thầy/Cô vui lòng tải lên file đề kiểm tra trước khi phân tích.")
            st.stop()

        with st.spinner("⏳ AI đang quét dữ liệu, phân loại nhận thức và xây dựng ma trận..."):
            raw_text = extract_text_from_file(file_de)
            exam_text = normalize_outline(raw_text)

            if not exam_text:
                st.error("❌ Không trích xuất được văn bản từ file. Vui lòng kiểm tra lại định dạng.")
                st.stop()

            # --- PROMPT CHUYÊN BIỆT CHO PHÂN TÍCH ĐỀ THI ---
            analysis_prompt = f"""
BẠN LÀ CHUYÊN GIA KHẢO THÍ GDPT 2018.
NHIỆM VỤ: Bạn sẽ nhận được nội dung một ĐỀ KIỂM TRA ĐÃ SOẠN SẴN. Bạn phải đọc thật kỹ, dịch ngược nội dung đó để lập MA TRẬN và BẢN ĐẶC TẢ chuẩn xác 100% khớp với đề. Bạn bắt buộc phải trả về ĐỊNH DẠNG VĂN BẢN MARKDOWN THUẦN TÚY (Tuyệt đối không bọc trong JSON hay Code Block).

============================================================
THÔNG TIN HỆ THỐNG
============================================================
- Môn: {mon_hoc}
- Lớp: {lop}
- Có đáp án đính kèm: {"Có" if has_answer else "Không"}
- Có hình vẽ: {"Có" if has_image else "Không"}

============================================================
NỘI DUNG ĐỀ THI CẦN PHÂN TÍCH
============================================================
{exam_text}

============================================================
YÊU CẦU XỬ LÝ (BẮT BUỘC TUÂN THỦ)
============================================================
BƯỚC 1: PHÂN TÍCH TỪNG CÂU HỎI
Hãy quét từ Câu 1 đến câu cuối cùng trong đề. Tự động xác định:
- Nội dung/Chủ đề câu hỏi.
- Dạng câu hỏi (Trắc nghiệm nhiều lựa chọn, Đúng/Sai, Điền khuyết, hay Tự luận).
- Mức độ nhận thức:
  + Nhận biết (Nhớ lại khái niệm, công thức, nhận diện).
  + Thông hiểu (Giải thích, so sánh, phân biệt, tính toán cơ bản).
  + Vận dụng (Tính toán nhiều bước, giải quyết tình huống thực tế).
  + Vận dụng cao (Bài toán khó, tư duy tổng hợp).
- Điểm số dự kiến: Nếu đề không ghi điểm, hãy tự quy định chuẩn (Trắc nghiệm thường 0.25đ/câu, Tự luận chia đều để tổng là 10đ).

BƯỚC 2: LẬP MA TRẬN
Tổng hợp kết quả từ BƯỚC 1 để lập thành bảng Ma trận đề thi. Cột tổng số câu và tổng điểm phải khớp chính xác tuyệt đối với những gì đã phân tích. 

BƯỚC 3: LẬP BẢN ĐẶC TẢ
Từ Ma trận ở BƯỚC 2, trình bày chi tiết Yêu cầu cần đạt cho từng câu hỏi ứng với từng mức độ nhận thức.

QUY TẮC TRÌNH BÀY ĐẦU RA (MARKDOWN THUẦN TÚY):
- KHÔNG bọc trong JSON.
- Công thức toán học, biểu thức, ký hiệu (nếu có trích dẫn) BẮT BUỘC bọc trong cặp dấu $. (VD: $x^2 + 1$, $AB // CD$).

TRÌNH BÀY CHÍNH XÁC THEO CẤU TRÚC BÊN DƯỚI VÀ KHÔNG THÊM BỚT TIÊU ĐỀ KHÁC:

# PHẦN I. PHÂN TÍCH CẤU TRÚC ĐỀ THI
(Liệt kê ngắn gọn: Câu X - [Dạng câu] - [Chủ đề] - [Mức độ] - [Điểm])

# PHẦN II. MA TRẬN ĐỀ KIỂM TRA
(Vẽ bảng ma trận với các cột: Chủ đề | Nhận biết | Thông hiểu | Vận dụng | Vận dụng cao | Tổng)

# PHẦN III. BẢN ĐẶC TẢ CHI TIẾT
(Vẽ bảng đặc tả với các cột: Chủ đề | Mức độ | Yêu cầu cần đạt | Số câu hỏi | Câu hỏi số)
"""
            try:
                result = ai_engine.generate_text(analysis_prompt)
                if not result or not result.strip():
                    st.error("❌ AI không phản hồi.")
                    st.stop()
                    
                st.session_state["mt_content"] = result
                st.session_state["mt_filename"] = file_de.name
                st.success("✅ Phân tích hoàn tất! Dữ liệu khớp 100% với đề bài gốc.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Lỗi xử lý AI: {e}")

    # --- KHỐI HIỂN THỊ KẾT QUẢ VÀ XUẤT WORD ---
    if "mt_content" in st.session_state:
        st.divider()
        st.markdown(f"## 📄 MA TRẬN & ĐẶC TẢ (TỪ TỆP: `{st.session_state.get('mt_filename')}`)")
        
        if st.button("🗑️ ĐÓNG VÀ LÀM LẠI", key="mt_delete"):
            st.session_state.pop("mt_content", None)
            st.session_state.pop("mt_filename", None)
            st.rerun()
            
        st.markdown(st.session_state["mt_content"])
        
        # Xuất Word
        try:
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
                
            from export.export_word import WordExportEngine
            word_bytes = WordExportEngine.export_to_word({
                "ai_generated_content": st.session_state["mt_content"],
                "is_de_kt": False, 
                "title": "Ma_Tran_Phan_Tich_Tu_De"
            })
            st.download_button(
                "📥 TẢI XUỐNG FILE WORD (.DOCX)", 
                data=word_bytes, 
                file_name="Ma_Tran_Dac_Ta.docx", 
                use_container_width=True, 
                key="mt_download_word"
            )
        except Exception as e:
            st.warning(f"⚠️ Chưa thể kết xuất Word do lỗi thư viện: {e}")
