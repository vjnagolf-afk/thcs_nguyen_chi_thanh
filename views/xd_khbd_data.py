# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (TÍCH HỢP OCR & FIX LỖI FORMAT)
FILE: views/xd_khbd_data.py
============================================================
"""

import streamlit as st
import os
import re
import json
import logging
import pandas as pd
from docx import Document
from pathlib import Path
from io import BytesIO

logger = logging.getLogger(__name__)

NLS_GV_VAN_BAN_MAC_DINH = "Thông tư 18/2026/TT-BGDĐT"

MODE_LABELS = {
    "chinh_sua": "Chỉnh sửa và nâng cấp giáo án gốc",
    "tu_dong": "Tự động soạn từ SGK",
}

MIN_SOURCE_CHARS = 100

def init_session_state():
    defaults = {
        "khbd_mode": "tu_dong",
        "khbd_result": None,
        "khbd_nls_list": [],
        "khbd_hoat_dong_list": [],
        "khbd_processing": False,
        "khbd_nls_noi_dung": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_ket_qua():
    st.session_state["khbd_result"] = None

def reset_toan_bo_khbd():
    st.session_state["khbd_result"] = None
    st.session_state["khbd_nls_list"] = []
    st.session_state["khbd_hoat_dong_list"] = []
    st.session_state["khbd_nls_noi_dung"] = ""
    st.session_state["khbd_mode"] = "tu_dong"
    st.session_state["khbd_processing"] = False

def set_mode(mode: str):
    if mode not in MODE_LABELS:
        raise ValueError(f"Chế độ soạn không hợp lệ: {mode}")
    st.session_state.khbd_mode = mode

KHUNG_NLS_GV = {
    "1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ": {
        "1.1. Dạy học và giáo dục trong môi trường số": {"Cơ bản": "Sử dụng thiết bị cơ bản.", "Thành thạo": "Thiết kế kế hoạch bài dạy số hóa.", "Nâng cao": "Đổi mới mô hình số."}
    }
}
KHUNG_NLS_HS = {
    "1. Sử dụng thông tin và dữ liệu số": {"1.1. Tìm kiếm và chọn lọc": {"Mức 1": "Tìm kiếm cơ bản.", "Mức 2": "Đánh giá thông tin."}}
}

def get_nls_framework(loai_khung): return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS
def get_nls_domains(loai_khung): return list(get_nls_framework(loai_khung).keys())
def get_nls_components(loai_khung, linh_vuc): return list(get_nls_framework(loai_khung).get(linh_vuc, {}).keys())
def get_nls_levels(loai_khung, linh_vuc, thanh_phan): return list(get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).keys())
def get_nls_content(loai_khung, linh_vuc, thanh_phan, muc_do): return get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).get(muc_do, "")

def add_nls():
    linh_vuc = safe_text(st.session_state.get("khbd_nls_linh_vuc", ""))
    thanh_phan = safe_text(st.session_state.get("khbd_nls_thanh_phan", ""))
    muc_do = safe_text(st.session_state.get("khbd_nls_muc_do", ""))
    noi_dung = safe_text(st.session_state.get("khbd_nls_noi_dung", ""))
    if not noi_dung: return

    van_ban = NLS_GV_VAN_BAN_MAC_DINH if st.session_state.get("khbd_loai_khung_nls") == "Giáo viên (Thông tư 18)" else "Khung DigComp"
    item = {"van_ban": van_ban, "linh_vuc": linh_vuc, "thanh_phan": thanh_phan, "muc_do": muc_do, "noi_dung": noi_dung}
    if item not in st.session_state.khbd_nls_list:
        st.session_state.khbd_nls_list.append(item)

def format_nls():
    items = st.session_state.khbd_nls_list
    if not items: return "Không yêu cầu tích hợp Năng lực số chuyên biệt."
    result = []
    for index, item in enumerate(items, start=1):
        result.append(f"- Yêu cầu NLS: {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}")
    return "\n".join(result)

def safe_text(value):
    if value is None: return ""
    text = str(value).replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\r", "").replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def diagnose_source_quality(text, source_name="Tài liệu nguồn"):
    text = safe_text(text)
    chars = len(text)
    if chars < MIN_SOURCE_CHARS:
        return {"status": "empty", "message": "Hệ thống sẽ dùng AI Vision để quét PDF Scan."}
    return {"status": "valid", "message": "Dữ liệu hợp lệ."}

def extract_text_via_gemini_ocr(file_bytes, file_name="document.pdf"):
    import tempfile, os, time
    try: import google.generativeai as genai
    except ImportError: return ""

    api_key = st.session_state.get("user_api_key") or st.secrets.get("GEMINI_API_KEY")
    if not api_key: return "❌ Cần API Key."
    genai.configure(api_key=api_key)
    
    ext = os.path.splitext(file_name)[1] or ".pdf"
    tmp_path = ""
    media_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        media_file = genai.upload_file(path=tmp_path)
        while media_file.state.name == "PROCESSING":
            time.sleep(2)
            media_file = genai.get_file(media_file.name)
            
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        ocr_prompt = "Trích xuất toàn bộ chữ. CÁC CÔNG THỨC TOÁN BẮT BUỘC dùng LaTeX \sqrt{...} KHÔNG DÙNG ký tự √."
        response = model.generate_content([ocr_prompt, media_file])
        return getattr(response, "text", "")
    except Exception as e: return ""
    finally:
        if media_file: 
            try: genai.delete_file(media_file.name)
            except: pass
        if os.path.exists(tmp_path): 
            try: os.remove(tmp_path)
            except: pass

def read_pdf(uploaded_file, range_str=""):
    if uploaded_file is None: return ""
    content = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    extracted_text = ""
    try:
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        extracted_text = "\n\n".join([doc[i].get_text("text").strip() for i in range(len(doc))])
    except: pass

    if len(extracted_text) < 100:
        extracted_text = extract_text_via_gemini_ocr(content, getattr(uploaded_file, "name", "doc.pdf"))
    return safe_text(extracted_text)

def read_docx_ordered(source):
    try:
        doc = Document(BytesIO(source.getvalue())) if hasattr(source, "getvalue") else Document(source)
        return safe_text("\n".join([p.text for p in doc.paragraphs]))
    except: return ""

def read_multiple_files(files, range_str="", is_pdf_target=False):
    result = []
    for f in files or []:
        content = read_pdf(f) if f.name.endswith('.pdf') else read_docx_ordered(f)
        if len(content) > 30: result.append(content)
    return safe_text("\n".join(result))

def generate_ai(client, prompt, model_name="3.5 Flash"):
    try:
        # Nhúng thẳng lệnh hệ thống vào prompt để dập tắt lỗi Phương án A
        system_instruction = """
[QUY TẮC ĐỊNH DẠNG BẮT BUỘC - KHÔNG ĐƯỢC VI PHẠM]:
1. CẤM VIẾT LỜI CHÀO, LỜI MỞ ĐẦU HOẶC KẾT LUẬN. Kế hoạch phải bắt đầu bằng đúng chữ "# TÊN BÀI HỌC:".
2. CẤM DÙNG KÝ TỰ CĂN UNICODE `√`. Mọi công thức Toán học PHẢI dùng mã LaTeX `\sqrt{A}` đặt trong dấu `$`. (Ví dụ ĐÚNG: $\sqrt{x-3}$).
3. XUỐNG DÒNG RÕ RÀNG: Giữa các đoạn văn, đề mục phải có khoảng trắng bằng cách ấn Enter 2 lần (\n\n).
4. CẤM DÙNG DẤU CHẤM ĐEN (BULLET) trước các đề mục nhỏ như: a) Mục tiêu, b) Nội dung, c) Sản phẩm, d) Tổ chức thực hiện.
5. BẮT BUỘC chèn đủ Tiêu đề, Môn học, Khối lớp, Số tiết ở ngay đầu giáo án.
        """
        full_prompt = system_instruction + "\n\n" + prompt
        
        api_model = "gemini-2.5-pro" if "Pro" in model_name else "gemini-2.5-flash"
        if hasattr(client, "generate_text"):
            # Gọi phương thức generate_text đã bỏ system_instruction kwarg
            text_out = client.generate_text(full_prompt, model_name=model_name)
        else:
            response = client.models.generate_content(model=api_model, contents=full_prompt)
            text_out = getattr(response, "text", "").strip()
            
        # Tiền xử lý: Cắt bỏ rác nếu AI vẫn cố tình chào hỏi
        if "# TÊN BÀI HỌC:" in text_out:
            text_out = text_out[text_out.find("# TÊN BÀI HỌC:"):]
            
        return text_out
    except Exception as e:
        logger.error("Lỗi gọi AI: %s", e)
        raise RuntimeError(f"Lỗi kết nối AI: {e}")

def validate_khbd_result(text):
    if len(text) < 500: return False, "Nội dung quá ngắn."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, nls_str, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, mode, so_tiet):
    source = safe_text(noi_dung_chinh)[:20000] 
    ga_block = f"--- GIÁO ÁN CŨ ĐỂ CHỈNH SỬA ---\n{safe_text(noi_dung_ga)[:10000]}\n" if mode == "chinh_sua" else ""
    
    hoa_nhap_block = f"- Dạy học hòa nhập: Đề xuất công cụ/phương pháp hỗ trợ riêng cho HS: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else ""
    ai_block = "- Tích hợp AI: Thiết kế hoạt động ứng dụng AI cho GV/HS." if tich_hop_ai else ""

    nhiem_vu = f"""
NHIỆM VỤ CỦA BẠN: {'CHỈNH SỬA GIÁO ÁN GỐC' if mode == 'chinh_sua' else 'SOẠN MỚI GIÁO ÁN TỪ SGK'}.
1. Đọc kỹ NGUỒN KIẾN THỨC CỐT LÕI (SGK) để rút ra khái niệm, công thức.
2. Bài học kéo dài {so_tiet} tiết. Phân bổ rõ: ### TIẾT 1, ### TIẾT 2...
3. Chi tiết hóa từng Hoạt động gồm đúng 4 bước KHÔNG DÙNG BULLET POINT:
   a) Mục tiêu: ...
   b) Nội dung: ...
   c) Sản phẩm: ... (Ghi rõ lời giải/đáp án của các phương trình/công thức có trong nội dung)
   d) Tổ chức thực hiện: ...
4. TẠO HẲN MỘT MỤC RIÊNG "III. TÍCH HỢP CHUYÊN SÂU" Ở ĐẦU BÀI VÀ TRÌNH BÀY:
   {nls_str}
   {ai_block}
   {hoa_nhap_block}
"""
    return f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\n{nhiem_vu}\n\n--- NGUỒN KIẾN THỨC ---\n{source}\n\n{ga_block}"
