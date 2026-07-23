# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (CHUẨN HÓA KHÔNG DÙNG PYPDF2)
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

NLS_GV_VAN_BAN_MAC_DINH = "18/2026/TT-BGDĐT"

MODE_LABELS = {
    "chinh_sua": "Chỉnh sửa và nâng cấp giáo án gốc",
    "tao_moi": "Soạn mới hoàn toàn từ tài liệu SGK",
    "tu_dong": "Soạn mới hoàn toàn từ tài liệu SGK",
}

MIN_SOURCE_CHARS = 300
MIN_SOURCE_WORDS = 50

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
    "1. Miền 1: Tổ chức dạy học trong môi trường số": {
        "1.1. Dạy học trong môi trường số": {
            "Cơ bản": "Sử dụng thiết bị cơ bản; Dùng ứng dụng giáo dục đơn giản.",
            "Thành thạo": "Tích hợp học liệu số vào kế hoạch; Thiết kế hoạt động tương tác."
        }
    },
    "6. Miền 6: Trí tuệ nhân tạo (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": "Sử dụng công cụ AI tạo sinh cơ bản hỗ trợ tìm kiếm ý tưởng.",
            "Thành thạo": "Khai thác công cụ AI chuyên biệt tạo học liệu tương tác."
        }
    }
}
KHUNG_NLS_HS = {
    "1. Thông tin và dữ liệu số": {
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu": {
            "Mức 1": "Tìm kiếm dữ liệu đơn giản.",
            "Mức 2": "Sử dụng kĩ thuật tìm kiếm nâng cao."
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

    van_ban = NLS_GV_VAN_BAN_MAC_DINH if st.session_state.get("khbd_loai_khung_nls") == "Giáo viên (Thông tư 18)" else "DigComp"
    item = {"van_ban": van_ban, "linh_vuc": linh_vuc, "thanh_phan": thanh_phan, "muc_do": muc_do, "noi_dung": noi_dung}
    if item not in st.session_state.khbd_nls_list:
        st.session_state.khbd_nls_list.append(item)

def format_nls():
    items = st.session_state.khbd_nls_list
    if not items: return "Không tích hợp năng lực số cụ thể."
    result = []
    for index, item in enumerate(items, start=1):
        result.append(f"{index}. [{item['van_ban']}] {item['linh_vuc']} - Thành phần: {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}")
    return "\n".join(result)

def add_activity():
    value = safe_text(st.session_state.get("khbd_new_activity", ""))
    if value and value not in st.session_state.khbd_hoat_dong_list:
        st.session_state.khbd_hoat_dong_list.append(value)
    st.session_state.khbd_new_activity = ""

def safe_text(value):
    if value is None: return ""
    text = str(value).replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\r", "").replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def normalize_source_text(text):
    return safe_text(text)

def diagnose_source_quality(text, source_name="Tài liệu nguồn"):
    text = safe_text(text)
    chars = len(text)
    words = len(re.findall(r"\S+", text))
    if chars == 0:
        return {"status": "empty", "message": f"Không thể đọc chữ từ {source_name}.", "chars": chars, "words": words}
    if chars < MIN_SOURCE_CHARS:
        return {"status": "insufficient", "message": f"{source_name} không đủ dữ liệu (Cần tối thiểu {MIN_SOURCE_CHARS} ký tự).", "chars": chars, "words": words}
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

        # 1. PyMuPDF (fitz)
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
                if len(result) >= 50: return normalize_source_text(result)
        except Exception as e:
            logger.warning("PyMuPDF lỗi: %s", e)

        # 2. pypdf (Thay thế hoàn toàn PyPDF2)
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(content))
            total_pages = len(reader.pages)
            if total_pages > 0:
                s_page = 1 if selected_start is None else max(1, selected_start)
                e_page = total_pages if selected_end is None else min(total_pages, selected_end)
                if s_page > e_page: s_page, e_page = 1, total_pages
                
                pages = [reader.pages[i - 1].extract_text().strip() for i in range(s_page, e_page + 1) if reader.pages[i - 1].extract_text()]
                return normalize_source_text("\n\n".join(pages))
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
                result.append("[BẢNG DỮ LIỆU]")
                for row in table.rows:
                    cells = [safe_text(cell.text).replace("\n", " ") for cell in row.cells if safe_text(cell.text)]
                    if cells: result.append(" | ".join(cells))
        return normalize_source_text("\n".join(result))
    except Exception as e:
        return f"[LỖI ĐỌC DOCX: {e}]"

def read_excel_structured(uploaded_file):
    try:
        file_source = BytesIO(uploaded_file.getvalue()) if hasattr(uploaded_file, "getvalue") else uploaded_file
        if hasattr(file_source, "seek"): file_source.seek(0)
        
        result = []
        sheets = pd.read_excel(file_source, sheet_name=None)
        for name, df in sheets.items():
            result.append(f"\n[SHEET: {name}]")
            records = df.dropna(how='all').fillna("").to_dict(orient="records")
            for idx, rec in enumerate(records, start=1):
                clean_rec = {safe_text(k): safe_text(v) for k, v in rec.items() if safe_text(v)}
                if clean_rec: result.append(f"Dòng {idx}: {json.dumps(clean_rec, ensure_ascii=False)}")
        return normalize_source_text("\n".join(result))
    except Exception as e:
        return f"[LỖI ĐỌC EXCEL: {e}]"

def read_uploaded_file(uploaded_file, range_str="", is_pdf_target=False):
    if not uploaded_file: return ""
    ext = Path(getattr(uploaded_file, "name", "").lower()).suffix
    if ext == ".pdf": return read_pdf(uploaded_file, range_str if is_pdf_target else "")
    if ext == ".docx": return read_docx_ordered(uploaded_file)
    if ext in [".xlsx", ".xls"]: return read_excel_structured(uploaded_file)
    return ""

def read_multiple_files(files, range_str="", is_pdf_target=False):
    result = []
    for f in files or []:
        content = read_uploaded_file(f, range_str, is_pdf_target)
        if len(content.strip()) > 30:
            result.append(f"\n--- TÀI LIỆU NGUỒN: {getattr(f, 'name', 'Tài liệu')} ---\n{content}")
    return normalize_source_text("\n".join(result))

def read_template_local(path="templates/KHBD_Mau.docx"):
    if not os.path.exists(path): return ""
    try: return read_docx_ordered(path)
    except: return ""

def load_task_config():
    path = "prompts/task_config_khbd.txt"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return f.read().strip()
        except: pass
    return "BẠN LÀ CHUYÊN GIA SƯ PHẠM CHUẨN PHỤ LỤC 4 CÔNG VĂN 5512."

def generate_ai(client, prompt, model_name="3.5 Flash"):
    if client is None: raise RuntimeError("Chưa truyền đối tượng Client AI.")
    try:
        # Cập nhật để hỗ trợ việc sử dụng AIEngine wrapper thống nhất
        if hasattr(client, "generate_text"):
            return client.generate_text(prompt, model_name=model_name)
        
        # Hỗ trợ tương thích ngược nếu truyền thẳng thư viện
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
        raise RuntimeError(f"Máy chủ AI phản hồi lỗi: {e}")

def validate_khbd_result(text):
    text = safe_text(text).upper()
    if len(text) < 500: return False, "Nội dung giáo án quá ngắn."
    valid_count = sum(1 for kw in ["MỤC TIÊU", "THIẾT BỊ", "TIẾN TRÌNH", "HOẠT ĐỘNG"] if kw in text)
    if valid_count < 3: return False, "Thiếu mục cấu trúc sư phạm."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, noi_dung_ppct, noi_dung_ai, noi_dung_mau, nls, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, hoat_dong, mode):
    if mode not in MODE_LABELS: raise ValueError("Chế độ không hợp lệ.")
    source = safe_text(noi_dung_chinh)[:8000]
    
    quality = diagnose_source_quality(source, "Tài liệu nguồn")
    if quality["status"] != "valid" and mode in ["tu_dong", "tao_moi"]:
        raise ValueError(f"❌ Không trích xuất được văn bản.\nChi tiết: {quality['message']}")

    ga_block = f"\n[GIÁO ÁN GỐC THAM KHẢO]\n{safe_text(noi_dung_ga)[:3000]}\n" if noi_dung_ga else ""
    hoa_nhap_block = f"Hỗ trợ riêng cho học sinh: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else "Đại trà."

    return (
        f"{load_task_config()}\n\n"
        f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\n"
        f"--- NGUỒN KIẾN THỨC CỐT LÕI ---\n{source}\n\n"
        f"--- CHỈ ĐẠO BỔ SUNG ---\nPPCT: {safe_text(noi_dung_ppct)}\n{ga_block}\n"
        f"Năng lực số: {nls}\nAI: {'Có' if tich_hop_ai else 'Không'}\nHòa nhập: {hoa_nhap_block}\nThêm HĐ: {safe_text(hoat_dong)}\n\n"
        f"--- RÀNG BUỘC KỸ THUẬT ---\n"
        f"1. Tuyệt đối không bịa đặt kiến thức ngoài Nguồn cốt lõi.\n"
        f"2. Nếu bài >1 tiết, phải phân tách rõ ràng: ### TIẾT 1, ### TIẾT 2...\n"
        f"3. Dùng Markdown chuẩn, bắt đầu ngay bằng # TÊN BÀI HỌC.\n"
    )
