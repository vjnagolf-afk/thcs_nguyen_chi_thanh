# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (ÉP XUỐNG DÒNG, BẢO TOÀN TOÁN)
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

# (Giữ nguyên KHUNG_NLS_GV và KHUNG_NLS_HS như bản trước...)
KHUNG_NLS_HS = {
    "1. Sử dụng thông tin và dữ liệu số": {
        "1.1. Tìm kiếm và chọn lọc": {"Mức 1": "Biết sử dụng công cụ tìm kiếm cơ bản.", "Mức 2": "Biết đánh giá độ tin cậy của thông tin."}
    },
    "2. Giao tiếp và hợp tác trực tuyến": {
        "2.1. Tương tác qua môi trường số": {"Mức 1": "Biết sử dụng email, chat để trao đổi học tập.", "Mức 2": "Biết sử dụng nền tảng làm việc nhóm (Padlet, Azota...)."}
    }
}
def get_nls_framework(loai_khung): return KHUNG_NLS_HS # Giữ logic của thầy
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
    item = {"linh_vuc": linh_vuc, "thanh_phan": thanh_phan, "muc_do": muc_do, "noi_dung": noi_dung}
    if item not in st.session_state.khbd_nls_list:
        st.session_state.khbd_nls_list.append(item)

def format_nls():
    items = st.session_state.khbd_nls_list
    if not items: return "Không yêu cầu."
    return "\n".join([f"- {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}" for item in items])

def safe_text(value):
    if value is None: return ""
    text = str(value).replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\r", "").replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    return text.strip()

def read_pdf(uploaded_file, range_str=""):
    if uploaded_file is None: return ""
    content = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    extracted_text = ""
    try:
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        extracted_text = "\n\n".join([doc[i].get_text("text").strip() for i in range(len(doc))])
    except: pass
    return safe_text(extracted_text)

def read_docx_ordered(source):
    try:
        doc = Document(BytesIO(source.getvalue())) if hasattr(source, "getvalue") else Document(source)
        return safe_text("\n".join([p.text for p in doc.paragraphs]))
    except: return ""

def read_multiple_files(files, range_str="", is_pdf_target=False):
    result = []
    for f in files or []:
        file_name = getattr(f, 'name', '').lower()
        if file_name.endswith('.pdf'): content = read_pdf(f)
        else: content = read_docx_ordered(f)
        if len(content) > 30: result.append(content)
    return safe_text("\n".join(result))

def generate_ai(client, prompt, model_name="3.5 Flash"):
    if client is None: raise RuntimeError("Chưa truyền đối tượng Client AI.")
        
    try:
        system_instruction = """
[KỶ LUẬT ĐỊNH DẠNG VÀ CẤU TRÚC 5512 BẮT BUỘC - LÀM SAI SẼ BỊ PHẠT]:
1. CẤM VIẾT LỜI CHÀO/KẾT LUẬN. Bắt đầu bằng "# TÊN BÀI HỌC:".
2. BẮT BUỘC ÉP XUỐNG DÒNG: Các mục a, b, c, d tuyệt đối không được viết liền nhau trên 1 dòng. Sau mỗi dấu hai chấm (:) hoặc hết một ý, phải XUỐNG DÒNG.
Mẫu trình bày ĐÚNG:
a) Mục tiêu: ...
b) Nội dung: ...
c) Sản phẩm: ...
d) Tổ chức thực hiện: 
3. TRONG MỤC TỔ CHỨC THỰC HIỆN: CẤM SỬ DỤNG DẤU CHẤM ĐEN (•). Chỉ được phép sử dụng dấu cộng (+) để bắt đầu:
+ Bước 1: GV giao nhiệm vụ...
+ Bước 2: HS thực hiện...
+ Bước 3: Báo cáo thảo luận...
+ Bước 4: Kết luận nhận định...
4. CÔNG THỨC TOÁN HỌC: Giữ nguyên định dạng, tuyệt đối không được viết gãy (Ví dụ: phải viết đầy đủ là √(x+2) thay vì √).
        """
        full_prompt = system_instruction + "\n\n" + prompt
        
        if hasattr(client, "generate_text"):
            text_out = client.generate_text(full_prompt, model_name=model_name)
        elif hasattr(client, "models") and hasattr(client.models, "generate_content"):
            api_model = "gemini-2.5-pro" if "Pro" in model_name else "gemini-2.5-flash"
            response = client.models.generate_content(model=api_model, contents=full_prompt)
            text_out = getattr(response, "text", "").strip()
        else:
            raise RuntimeError("Đối tượng AI Engine không đúng chuẩn.")
            
        if "# TÊN BÀI HỌC:" in text_out:
            text_out = text_out[text_out.find("# TÊN BÀI HỌC:"):]
            
        # Xóa nốt dấu chấm đen nếu AI vẫn cứng đầu
        text_out = text_out.replace("•", "+")
        return text_out
    except Exception as e:
        logger.error(f"Lỗi gọi AI: {str(e)}")
        raise RuntimeError(f"Lỗi kết nối AI: {str(e)}")

def validate_khbd_result(text):
    if len(text) < 500: return False, "Nội dung quá ngắn."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, nls_str, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, mode, so_tiet):
    source = safe_text(noi_dung_chinh)[:20000] 
    ga_block = f"--- GIÁO ÁN CŨ ĐỂ CHỈNH SỬA ---\n{safe_text(noi_dung_ga)[:10000]}\n" if mode == "chinh_sua" else ""
    
    hoa_nhap_block = f"- Dạy học hòa nhập: HS: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else ""
    ai_block = "- Tích hợp AI: Đề xuất hoạt động." if tich_hop_ai else ""

    nhiem_vu = f"""
NHIỆM VỤ: SOẠN KẾ HOẠCH BÀI DẠY (GIÁO ÁN) SIÊU CHI TIẾT TỪ NGUỒN CUNG CẤP.
- Bài học có {so_tiet} tiết. Phân bổ rải đều.
- Trích xuất ĐẦY ĐỦ đề bài, công thức, ví dụ từ SGK. KHÔNG TÓM TẮT CHUNG CHUNG.
- DÀN Ý BẮT BUỘC:

# TÊN BÀI HỌC: ...
I. MỤC TIÊU (1. Kiến thức, 2. Năng lực, 3. Phẩm chất)
II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
III. TÍCH HỢP CHUYÊN SÂU
{nls_str}
{ai_block}
{hoa_nhap_block}
IV. TIẾN TRÌNH DẠY HỌC
### TIẾT 1
**Hoạt động 1: Khởi động (X phút)**
a) Mục tiêu: ...
b) Nội dung: ... (Ghi chi tiết câu hỏi)
c) Sản phẩm: ... (Ghi chi tiết đáp án)
d) Tổ chức thực hiện: 
+ Bước 1: GV giao nhiệm vụ...
+ Bước 2: HS thực hiện...
+ Bước 3: Báo cáo thảo luận...
+ Bước 4: Kết luận nhận định...

(Làm tương tự cho Hoạt động Hình thành kiến thức, Luyện tập, Vận dụng cho toàn bộ các tiết).
"""
    return f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\n{nhiem_vu}\n\n--- NGUỒN KIẾN THỨC ---\n{source}\n\n{ga_block}"
