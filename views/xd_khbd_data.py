# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY 
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

# Cấu trúc giả định mẫu cho TT18 và DigComp (Có thể mở rộng thêm)
KHUNG_NLS_GV = {
    "1. Tổ chức dạy học trong môi trường số": {
        "1.1. Khai thác thiết bị và học liệu số": {
            "Mức Cơ bản": "Sử dụng được các thiết bị số cơ bản và khai thác học liệu số có sẵn.",
            "Mức Thành thạo": "Lựa chọn và tích hợp hiệu quả học liệu số vào quá trình dạy học.",
            "Mức Nâng cao": "Đánh giá, sáng tạo và chia sẻ học liệu số mang tính sư phạm cao."
        },
        "1.2. Tổ chức hoạt động học tập": {
            "Mức Cơ bản": "Sử dụng công cụ số để giao bài tập đơn giản.",
            "Mức Thành thạo": "Sử dụng nền tảng số để theo dõi, tương tác và hỗ trợ học sinh."
        }
    },
    "2. Đánh giá kết quả học tập": {
        "2.1. Đánh giá trực tuyến": {
            "Mức Cơ bản": "Sử dụng phần mềm tạo bài trắc nghiệm nhanh.",
            "Mức Thành thạo": "Phân tích dữ liệu từ nền tảng để điều chỉnh phương pháp."
        }
    }
}

KHUNG_NLS_HS = {
    "1. Sử dụng thông tin và dữ liệu số": {
        "1.1. Tìm kiếm và chọn lọc": {
            "Mức 1": "Biết sử dụng công cụ tìm kiếm cơ bản.",
            "Mức 2": "Biết đánh giá độ tin cậy của thông tin."
        }
    },
    "2. Giao tiếp và hợp tác trực tuyến": {
        "2.1. Tương tác qua môi trường số": {
            "Mức 1": "Biết sử dụng email, chat để trao đổi học tập.",
            "Mức 2": "Biết sử dụng nền tảng làm việc nhóm (Padlet, Azota...)."
        }
    }
}

def get_nls_framework(loai_khung):
    return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS

def get_nls_domains(loai_khung):
    return list(get_nls_framework(loai_khung).keys())

def get_nls_components(loai_khung, linh_vuc):
    return list(get_nls_framework(loai_khung).get(linh_vuc, {}).keys())

def get_nls_levels(loai_khung, linh_vuc, thanh_phan):
    return list(get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).keys())

def get_nls_content(loai_khung, linh_vuc, thanh_phan, muc_do):
    try:
        return get_nls_framework(loai_khung)[linh_vuc][thanh_phan][muc_do]
    except Exception:
        return ""

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
        result.append(f"{index}. Mục tiêu NLS: {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}")
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
    words = len(re.findall(r"\S+", text))
    if chars == 0:
        return {"status": "empty", "message": f"Không đọc được nội dung chữ từ {source_name}. Nếu là PDF scan dạng ảnh, hãy dùng tính năng OCR để lấy text trước.", "chars": chars, "words": words}
    if chars < MIN_SOURCE_CHARS:
        return {"status": "insufficient", "message": f"{source_name} quá ngắn, không đủ cơ sở để sinh giáo án dài.", "chars": chars, "words": words}
    return {"status": "valid", "message": f"{source_name} đủ dữ liệu.", "chars": chars, "words": words}

def read_pdf(uploaded_file, range_str=""):
    if uploaded_file is None: return ""
    try:
        if hasattr(uploaded_file, "getvalue"):
            content = uploaded_file.getvalue()
        else:
            if hasattr(uploaded_file, "seek"): uploaded_file.seek(0)
            content = uploaded_file.read()
        if not content: return ""

        range_str = safe_text(range_str)
        selected_start, selected_end = None, None
        if range_str:
            try:
                if "-" in range_str:
                    parts = range_str.split("-", 1)
                    selected_start, selected_end = int(parts[0].strip()), int(parts[1].strip())
                else:
                    selected_start = selected_end = int(range_str)
            except Exception:
                pass

        try:
            import fitz
            doc = fitz.open(stream=content, filetype="pdf")
            total_pages = len(doc)
            if total_pages > 0:
                s_page = 1 if selected_start is None else max(1, selected_start)
                e_page = total_pages if selected_end is None else min(total_pages, selected_end)
                if s_page > e_page: s_page, e_page = 1, total_pages
                
                pages = [doc[i - 1].get_text("text").strip() for i in range(s_page, e_page + 1) if doc[i - 1].get_text("text")]
                result = "\n\n".join(pages)
                if len(result) >= 50: return safe_text(result)
        except Exception:
            pass

        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(content))
            total_pages = len(reader.pages)
            if total_pages > 0:
                s_page = 1 if selected_start is None else max(1, selected_start)
                e_page = total_pages if selected_end is None else min(total_pages, selected_end)
                if s_page > e_page: s_page, e_page = 1, total_pages
                
                pages = [reader.pages[i - 1].extract_text().strip() for i in range(s_page, e_page + 1) if reader.pages[i - 1].extract_text()]
                return safe_text("\n\n".join(pages))
        except Exception as e:
            return f"[LỖI ĐỌC PDF: {e}]"
    except Exception as e:
        return f"[LỖI ĐỌC PDF: {e}]"

def read_docx_ordered(source):
    try:
        if isinstance(source, (str, Path)): doc = Document(source)
        elif hasattr(source, "getvalue"): doc = Document(BytesIO(source.getvalue()))
        elif hasattr(source, "read"):
            if hasattr(source, "seek"): source.seek(0)
            doc = Document(BytesIO(source.read()))
        else: doc = Document(source)

        result = []
        from docx.text.paragraph import Paragraph
        from docx.table import Table

        for element in doc.element.body:
            if element.tag.endswith("}p"):
                text = safe_text(Paragraph(element, doc).text)
                if text: result.append(text)
            elif element.tag.endswith("}tbl"):
                table = Table(element, doc)
                result.append("\n[BẢNG DỮ LIỆU]")
                for row in table.rows:
                    cells = [safe_text(cell.text).replace("\n", " ") for cell in row.cells if safe_text(cell.text)]
                    if cells: result.append(" | ".join(cells))
        return safe_text("\n".join(result))
    except Exception as e:
        return f"[LỖI ĐỌC DOCX: {e}]"

def read_uploaded_file(uploaded_file, range_str="", is_pdf_target=False):
    if not uploaded_file: return ""
    ext = Path(getattr(uploaded_file, "name", "").lower()).suffix
    if ext == ".pdf": return read_pdf(uploaded_file, range_str if is_pdf_target else "")
    if ext == ".docx": return read_docx_ordered(uploaded_file)
    return ""

def read_multiple_files(files, range_str="", is_pdf_target=False):
    result = []
    for f in files or []:
        content = read_uploaded_file(f, range_str, is_pdf_target)
        if len(content.strip()) > 30:
            result.append(f"\n--- TÀI LIỆU: {getattr(f, 'name', 'Tài liệu')} ---\n{content}")
    return safe_text("\n".join(result))

def generate_ai(client, prompt, model_name="3.5 Flash"):
    if client is None: raise RuntimeError("Chưa truyền đối tượng Client AI.")
    try:
        # Gọi qua Wrapper chuẩn
        if hasattr(client, "generate_text"):
            return client.generate_text(prompt, model_name=model_name, max_tokens=8192)
        
        # Fallback nếu truyền thẳng genai object
        model_mapping = {
            "3.1 Flash-Lite": "gemini-2.5-flash-lite",
            "3.5 Flash": "gemini-2.5-flash",
            "3.1 Pro": "gemini-2.5-pro",
            "Tư duy mở rộng": "gemini-2.5-pro"
        }
        api_model = model_mapping.get(model_name, "gemini-2.5-flash")
        response = client.models.generate_content(model=api_model, contents=prompt)
        return getattr(response, "text", "").strip()
    except Exception as e:
        logger.error("Lỗi gọi AI: %s", e)
        raise RuntimeError(f"Lỗi kết nối AI: {e}")

def validate_khbd_result(text):
    text = safe_text(text).upper()
    if len(text) < 500: return False, "Nội dung giáo án quá ngắn, vui lòng thử mô hình khác hoặc kiểm tra lại file SGK."
    valid_count = sum(1 for kw in ["MỤC TIÊU", "THIẾT BỊ", "TIẾN TRÌNH", "HOẠT ĐỘNG"] if kw in text)
    if valid_count < 3: return False, "Thiếu các mục cấu trúc bắt buộc của Phụ lục 4 (Mục tiêu, Tiến trình...)."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, nls_str, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, mode, so_tiet):
    source = safe_text(noi_dung_chinh)[:15000] # Mở rộng context window
    
    # Kiểm tra chất lượng dữ liệu đầu vào
    if mode == "tu_dong":
        quality = diagnose_source_quality(source, "Tài liệu SGK")
        if quality["status"] != "valid":
            raise ValueError(quality['message'])

    ga_block = f"--- GIÁO ÁN CŨ ĐỂ CHỈNH SỬA ---\n{safe_text(noi_dung_ga)[:10000]}\n" if mode == "chinh_sua" else ""
    
    hoa_nhap_block = f"BẮT BUỘC: Đề xuất phương pháp/công cụ hỗ trợ riêng cho học sinh khuyết tật: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else "Không yêu cầu giáo dục hòa nhập đặc biệt."
    ai_block = "BẮT BUỘC: Có hoạt động ứng dụng Trí tuệ Nhân tạo (AI) trong việc dạy/học của GV hoặc HS." if tich_hop_ai else "Không bắt buộc dùng AI."

    if mode == "chinh_sua":
        nhiem_vu = f"""
        NHIỆM VỤ CỦA BẠN: CHỈNH SỬA VÀ NÂNG CẤP KẾ HOẠCH BÀI DẠY (GIÁO ÁN) GỐC.
        1. Giữ nguyên ưu điểm của giáo án cũ, sửa các lỗi về kiến thức/sư phạm (nếu có).
        2. Bổ sung làm phong phú các Hoạt động Khởi động, Khám phá, Luyện tập, Vận dụng sao cho không bị nhàm chán.
        3. Tích hợp hữu cơ các yêu cầu chuyên biệt sau vào tiến trình:
           - Năng lực số: {nls_str}
           - {ai_block}
           - {hoa_nhap_block}
        4. Trình bày chuẩn hóa lại toàn bộ theo cấu trúc Phụ lục 4 Công văn 5512/BGDĐT.
        """
    else:
        nhiem_vu = f"""
        NHIỆM VỤ CỦA BẠN: SOẠN MỚI HOÀN TOÀN KẾ HOẠCH BÀI DẠY (GIÁO ÁN) DỰA TRÊN SGK.
        1. Đọc thật kỹ NGUỒN KIẾN THỨC CỐT LÕI (SGK) để rút ra khái niệm, công thức, bảng biểu, bài tập. Tuyệt đối KHÔNG BỊA ĐẶT kiến thức ngoài SGK.
        2. Bài học này kéo dài {so_tiet} tiết. BẮT BUỘC phải phân bổ thời lượng, nội dung và ghi rõ (Ví dụ: ### TIẾT 1: Hoạt động 1, 2. ### TIẾT 2: Hoạt động 3, 4).
        3. Chi tiết hóa từng Hoạt động gồm 4 bước: a) Mục tiêu; b) Nội dung; c) Sản phẩm; d) Tổ chức thực hiện (Rõ GV làm gì, HS làm gì). Không viết chung chung cụt ngủn.
        4. Tích hợp sâu sắc các yêu cầu sau vào thiết kế:
           - Năng lực số: {nls_str}
           - {ai_block}
           - {hoa_nhap_block}
        5. Cấu trúc tuân thủ nghiêm ngặt Phụ lục 4 Công văn 5512/BGDĐT.
        """

    return (
        f"BẠN LÀ CHUYÊN GIA SƯ PHẠM VÀ PHƯƠNG PHÁP DẠY HỌC THẾ KỶ 21.\n\n"
        f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\n"
        f"--- NHIỆM VỤ CỐT LÕI ---\n{nhiem_vu}\n\n"
        f"--- NGUỒN KIẾN THỨC CỐT LÕI (SGK) ---\n{source}\n\n"
        f"{ga_block}\n"
        f"--- RÀNG BUỘC KỸ THUẬT XUẤT BẢN ---\n"
        f"1. Xuất file bằng định dạng Markdown siêu chuẩn.\n"
        f"2. Công thức Toán học, Vật lí, Hóa học BẮT BUỘC dùng cú pháp LaTeX: dùng dấu $ cho inline (ví dụ: $x^2 + y^2 = r^2$) và $$ cho công thức đứng độc lập (block).\n"
        f"3. Dùng Markdown Table (dấu |) để vẽ các bảng biểu so sánh, phiếu học tập nếu SGK có đề cập.\n"
        f"4. Bắt đầu ngay kết quả bằng # TÊN BÀI HỌC (Không cần dạ vâng hay giải thích).\n"
    )
