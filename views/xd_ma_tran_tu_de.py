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
    
    st.info("Tính năng này giúp thầy/cô tải lên một đề thi đã soạn sẵn. AI sẽ phân tích và lập Ma trận, Đặc tả đúng chuẩn form đã cấu hình.")

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

            # --- PROMPT ÉP CHUẨN FORM MA TRẬN THEO YÊU CẦU ---
            analysis_prompt = f"""
BẠN LÀ CHUYÊN GIA KHẢO THÍ GDPT 2018.
NHIỆM VỤ: Phân tích ĐỀ KIỂM TRA ĐÃ CÓ, đếm số lượng câu, phân loại mức độ nhận thức (NB, TH, VD, VDC), tính điểm và TRẢ VỀ KẾT QUẢ ĐÚNG Y HỆT FORM BÊN DƯỚI. 
TUYỆT ĐỐI GIỮ NGUYÊN CÁC THẺ HTML NHƯ `<td colspan=.../>` VÀ CẤU TRÚC GẠCH DỌC `|`.

============================================================
THÔNG TIN ĐỀ THI
============================================================
- Môn: {mon_hoc} | Lớp: {lop}
- NỘI DUNG ĐỀ:
{exam_text}

============================================================
YÊU CẦU ĐẦU RA (BẮT BUỘC COPY ĐÚNG FORM NÀY VÀ ĐIỀN KẾT QUẢ):
============================================================

MA TRẬN ĐỀ KIỂM TRA, ĐÁNH GIÁ
CUỐI HỌC KÌ I
MÔN {mon_hoc.upper()}
- Thời điểm kiểm tra: Kiểm tra cuối kỳ (Kiến thức từ tuần 01 đến tuần 18)
- Thời gian làm bài: 90 phút.
- Hình thức kiểm tra: Kết hợp giữa trắc nghiệm và tự luận 
- Cấu trúc:
+ Mức độ đề: 40% Nhận biết; 30% Thông hiểu; 20% Vận dụng; 10% Vận dụng cao.
+ Phần trắc nghiệm: [ĐIỀN TỔNG ĐIỂM TRẮC NGHIỆM] điểm
+ Phần tự luận: [ĐIỀN TỔNG ĐIỂM TỰ LUẬN] điểm

I. MA TRẬN ĐỀ KIỂM TRA
TÊN CHỦ ĐỀ | TÊN BÀI HỌC | MỨC ĐỘ <td colspan=8/> | TỔNG SỐ CÂU <td colspan=2/> | TỔNG ĐIỂM
 |  | NHẬN BIẾT <td colspan=2/> | THÔNG HIỂU <td colspan=2/> | VẬN DỤNG <td colspan=2/> | VẬN DỤNG CAO <td colspan=2/> | <td colspan=2/> | 
 |  | TL | TN | TL | TN | TL | TN | TL | TN | TL | TN | 
[VỚI MỖI CHỦ ĐỀ TRONG ĐỀ THI, AI XUẤT RA MỘT DÒNG DỮ LIỆU ĐÚNG ĐỊNH DẠNG SAU:]
<td colspan=13/>
[Tên chủ đề] | [Tên bài học/Nội dung] | [Số câu TL] | [Số câu TN] | [Số câu TL] | [Số câu TN] | [Số câu TL] | [Số câu TN] | [Số câu TL] | [Số câu TN] | [Cộng số câu TL] | [Cộng số câu TN] | [Cộng điểm chủ đề]
[KẾT THÚC DANH SÁCH CHỦ ĐỀ, XUẤT HÀNG TỔNG:]
<td colspan=13/>
Tổng câu | | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | 
Tổng điểm | | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | 
% điểm số | | 40% <td colspan=2/> | 30% <td colspan=2/> | 20% <td colspan=2/> | 10% <td colspan=2/> | [Tính tổng % TL] | [Tính tổng % TN] | 100%

II. BẢN ĐẶC TẢ ĐỀ KIỂM TRA
TT | Chủ đề/Chương | Nội dung/Đơn vị kiến thức | Yêu cầu cần đạt | Số câu hỏi/ý hỏi ở các mức độ đánh giá <td colspan=9/> | Tổng điểm
 |  |  |  | Trắc nghiệm khách quan <td colspan=6/> | Tự luận <td colspan=3/> | 
 |  |  |  | Nhiều lựa chọn <td colspan=3/> | Đúng/Sai <td colspan=3/> | <td colspan=3/> | 
 |  |  |  | Biết | Hiểu | Vận dụng | Biết | Hiểu | Vận dụng | Biết | Hiểu | Vận dụng | 
[VỚI MỖI CHỦ ĐỀ, AI XUẤT RA DÒNG DỮ LIỆU TƯƠNG ỨNG Y HỆT ĐỊNH DẠNG SAU:]
<td colspan=14/>
[Số TT] | [Tên Chủ Đề] | [Tên Nội dung] | [Gạch đầu dòng các Yêu cầu cần đạt chi tiết của chủ đề này] | [Đếm số câu] | [Đếm số câu] | [Đếm số câu] | [Đếm số câu] | [Đếm số câu] | [Đếm số câu] | [Đếm số câu] | [Đếm số câu] | [Đếm số câu] | [Cộng điểm]
[KẾT THÚC DANH SÁCH CHỦ ĐỀ BẢN ĐẶC TẢ, XUẤT HÀNG TỔNG:]
<td colspan=14/>
Tổng số câu <td colspan=4/> | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | [Cộng] | 
Tổng số điểm <td colspan=4/> | <td colspan=3/> | <td colspan=3/> | <td colspan=3/> | 
Tỷ lệ % <td colspan=4/> | <td colspan=3/> | <td colspan=3/> | <td colspan=3/> | 
"""
            try:
                result = ai_engine.generate_text(analysis_prompt)
                if not result or not result.strip():
                    st.error("❌ AI không phản hồi.")
                    st.stop()
                    
                st.session_state["mt_content"] = result
                st.session_state["mt_filename"] = file_de.name
                st.success("✅ Phân tích hoàn tất! Dữ liệu đã được định dạng chuẩn theo mẫu.")
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
            
        st.markdown(st.session_state["mt_content"], unsafe_allow_html=True)
        
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
