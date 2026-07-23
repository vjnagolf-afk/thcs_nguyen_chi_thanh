# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (TỐI ƯU TOÀN DIỆN VÀ RÀNG BUỘC SCOPE)
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

KHUNG_NLS_GV = {
    "1. Miền 1: Tổ chức dạy học, giáo dục trong môi trường số": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "Sử dụng thiết bị cơ bản (máy tính, máy chiếu, bảng tương tác); Dùng ứng dụng di động giáo dục đơn giản.",
            "Thành thạo": "Lựa chọn, tích hợp học liệu số vào kế hoạch hoạt động; Thiết kế hoạt động học tập tương tác.",
            "Nâng cao": "Sáng tạo mô hình giáo dục ứng dụng công nghệ mới; Hướng dẫn đồng nghiệp sử dụng thiết bị số."
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": "Hướng dẫn học sinh thao tác cơ bản, an toàn trên thiết bị số có giám sát.",
            "Thành thạo": "Quan sát, hỗ trợ kịp thời khi học sinh gặp khó khăn tương tác công nghệ.",
            "Nâng cao": "Phát triển phương pháp hỗ trợ học tập trên nền tảng công nghệ tại nhà."
        }
    },
    "2. Miền 2: Kiểm tra, đánh giá": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": "Sử dụng thiết bị số ghi lại sản phẩm hoặc khoảnh khắc học tập của học sinh.",
            "Thành thạo": "Thiết kế hoạt động đánh giá kĩ năng qua công nghệ và lưu trữ minh chứng."
        }
    },
    "6. Miền 6: Trí tuệ nhân tạo (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": "Sử dụng công cụ AI tạo sinh cơ bản hỗ trợ soạn thảo và tìm kiếm ý tưởng.",
            "Thành thạo": "Khai thác công cụ AI chuyên biệt tạo học liệu tương tác và cá nhân hóa."
        }
    }
}

KHUNG_NLS_HS = {
    "1. Thông tin và dữ liệu số": {
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu": {
            "Mức 1": "Xác định nhu cầu thông tin, tìm kiếm dữ liệu đơn giản trong môi trường số.",
            "Mức 2": "Sử dụng kĩ thuật tìm kiếm nâng cao để lấy dữ liệu và thông tin chính xác."
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

def safe_text(value):
    if value is None: return ""
    if not isinstance(value, str):
        value = str(value)
    text = value.replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\r", "")
    text = text.replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def normalize_source_text(text):
    text = safe_text(text)
    if not text: return ""
    return text.strip()

def count_words(text):
    if not text: return 0
    return len(re.findall(r"\S+", text))

def diagnose_source_quality(text, source_name="Tài liệu nguồn"):
    text = safe_text(text)
    chars = len(text)
    words = count_words(text)
    if chars == 0:
        return {"status": "empty", "message": f"Không thể đọc bất kỳ chữ nào từ {source_name}. Hãy chắc chắn tệp không rỗng hoặc copy văn bản ra file Word.", "chars": chars, "words": words}
    if "[LỖI ĐỌC" in text.upper():
        return {"status": "error", "message": f"{source_name} có lỗi khi đọc.", "chars": chars, "words": words}
    if chars < MIN_SOURCE_CHARS or words < MIN_SOURCE_WORDS:
        return {"status": "insufficient", "message": f"{source_name} không đủ dữ liệu. (Cần tối thiểu {MIN_SOURCE_CHARS} ký tự)", "chars": chars, "words": words}
    return {"status": "valid", "message": f"{source_name} đủ dữ liệu.", "chars": chars, "words": words}

def read_pdf(uploaded_file, range_str=""):
    """
    Đọc PDF bằng PyMuPDF trước, pypdf dự phòng.
    Luôn đọc bytes từ đầu để tránh lỗi con trỏ file.
    """
    if uploaded_file is None:
        return ""

    try:
        # =====================================================
        # ĐỌC BYTES AN TOÀN
        # =====================================================
        if hasattr(uploaded_file, "getvalue"):
            content = uploaded_file.getvalue()
        else:
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            content = uploaded_file.read()

        if not content:
            return ""

        # =====================================================
        # XỬ LÝ PHẠM VI TRANG
        # =====================================================
        range_str = safe_text(range_str)
        selected_start = None
        selected_end = None

        if range_str:
            try:
                if "-" in range_str:
                    parts = range_str.split("-", 1)
                    selected_start = int(parts[0].strip())
                    selected_end = int(parts[1].strip())
                else:
                    selected_start = int(range_str)
                    selected_end = selected_start
            except Exception:
                selected_start = None
                selected_end = None

        # =====================================================
        # ƯU TIÊN 1: PYMUPDF
        # =====================================================
        try:
            import fitz

            doc = fitz.open(stream=content, filetype="pdf")
            total_pages = len(doc)

            if total_pages == 0:
                return ""

            start_page = 1 if selected_start is None else max(1, selected_start)
            end_page = total_pages if selected_end is None else min(total_pages, selected_end)

            if start_page > end_page:
                start_page, end_page = 1, total_pages

            pages = []

            for page_number in range(start_page, end_page + 1):
                page = doc[page_number - 1]
                text = page.get_text("text") or ""

                if text.strip():
                    pages.append(
                        f"[PDF - Trang {page_number}]\n{text.strip()}"
                    )

            result = "\n\n".join(pages)

            if len(result.strip()) >= 50:
                logger.info(
                    "Đọc PDF bằng PyMuPDF thành công: %s ký tự",
                    len(result)
                )
                return normalize_source_text(result)

        except Exception as e:
            logger.warning("PyMuPDF không đọc được PDF: %s", e)

        # =====================================================
        # ƯU TIÊN 2: PYPDF
        # =====================================================
        try:
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(content))
            total_pages = len(reader.pages)

            if total_pages == 0:
                return ""

            start_page = 1 if selected_start is None else max(1, selected_start)
            end_page = total_pages if selected_end is None else min(total_pages, selected_end)

            if start_page > end_page:
                start_page, end_page = 1, total_pages

            pages = []

            for page_number in range(start_page, end_page + 1):
                text = reader.pages[page_number - 1].extract_text() or ""

                if text.strip():
                    pages.append(
                        f"[PDF - Trang {page_number}]\n{text.strip()}"
                    )

            result = "\n\n".join(pages)

            logger.info(
                "Đọc PDF bằng pypdf thành công: %s ký tự",
                len(result)
            )

            return normalize_source_text(result)

        except Exception as e:
            logger.error("pypdf cũng không đọc được PDF: %s", e)
            return f"[LỖI ĐỌC PDF: {e}]"

    except Exception as e:
        logger.error("Lỗi tổng quát khi đọc PDF: %s", e)
        return f"[LỖI ĐỌC PDF: {e}]"

def read_docx_ordered(source):
    """
    Đọc DOCX theo đúng thứ tự đoạn văn và bảng.
    Đảm bảo luôn đọc file từ đầu.
    """
    try:
        # =====================================================
        # MỞ DOCUMENT
        # =====================================================
        if isinstance(source, (str, Path)):
            doc = Document(source)

        elif hasattr(source, "getvalue"):
            content = source.getvalue()

            if not content:
                return ""

            doc = Document(BytesIO(content))

        elif hasattr(source, "read"):
            if hasattr(source, "seek"):
                source.seek(0)

            content = source.read()

            if isinstance(content, str):
                content = content.encode("utf-8")

            if not content:
                return ""

            doc = Document(BytesIO(content))

        else:
            doc = Document(source)

        # =====================================================
        # ĐỌC THEO THỨ TỰ DOCUMENT XML
        # =====================================================
        result = []

        from docx.text.paragraph import Paragraph
        from docx.table import Table

        for element in doc.element.body:

            # -------------------------
            # ĐOẠN VĂN
            # -------------------------
            if element.tag.endswith("}p"):

                paragraph = Paragraph(element, doc)
                text = safe_text(paragraph.text)

                if text:
                    result.append(text)

            # -------------------------
            # BẢNG
            # -------------------------
            elif element.tag.endswith("}tbl"):

                table = Table(element, doc)

                result.append("[BẢNG DỮ LIỆU]")

                for row in table.rows:

                    cells = []

                    for cell in row.cells:
                        cell_text = safe_text(cell.text)
                        cell_text = cell_text.replace("\n", " ")

                        if cell_text:
                            cells.append(cell_text)

                    if cells:
                        result.append(" | ".join(cells))

        final_text = "\n".join(result)
        final_text = normalize_source_text(final_text)

        logger.info(
            "Đọc DOCX thành công: %s ký tự",
            len(final_text)
        )

        return final_text

    except Exception as e:
        logger.error("Lỗi đọc DOCX: %s", e)
        return f"[LỖI ĐỌC DOCX: {e}]"

def read_excel_structured(uploaded_file):
    """
    Đọc Excel có cấu trúc.
    Đảm bảo luôn đọc file từ đầu.
    """
    result = []
    try:
        # =====================================================
        # ĐỌC BYTES AN TOÀN
        # =====================================================
        if hasattr(uploaded_file, "getvalue"):
            content = uploaded_file.getvalue()
            if not content: return ""
            file_source = BytesIO(content)
        else:
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            file_source = uploaded_file
            
        sheets = pd.read_excel(file_source, sheet_name=None)
        for sheet_name, dataframe in sheets.items():
            result.append(f"\n[PHÂN PHỐI CHƯƠNG TRÌNH - SHEET: {sheet_name}]")
            dataframe = dataframe.dropna(how='all').fillna("")
            records = dataframe.to_dict(orient="records")
            for idx, rec in enumerate(records, start=1):
                clean_rec = {safe_text(k): safe_text(v) for k, v in rec.items() if safe_text(v)}
                if clean_rec:
                    result.append(f"Dòng {idx}: " + json.dumps(clean_rec, ensure_ascii=False))
                    
        final_text = normalize_source_text("\n".join(result))
        logger.info("Đọc EXCEL thành công: %s ký tự", len(final_text))
        return final_text
    except Exception as e:
        logger.error("Lỗi đọc EXCEL: %s", e)
        return f"[LỖI ĐỌC EXCEL: {e}]"

def read_uploaded_file(
    uploaded_file,
    range_str="",
    is_pdf_target=False
):
    """
    Bộ định tuyến đọc file nguồn.
    """
    if uploaded_file is None:
        return ""

    try:
        filename = getattr(
            uploaded_file,
            "name",
            ""
        )

        extension = Path(
            filename.lower()
        ).suffix

        if extension == ".pdf":
            return read_pdf(
                uploaded_file,
                range_str if is_pdf_target else ""
            )

        elif extension == ".docx":
            return read_docx_ordered(
                uploaded_file
            )

        elif extension in [".xlsx", ".xls"]:
            return read_excel_structured(
                uploaded_file
            )

        else:
            return ""

    except Exception as e:
        logger.error(
            "Lỗi định tuyến file %s: %s",
            filename,
            e
        )

        return f"[LỖI ĐỌC FILE: {e}]"

def read_multiple_files(files, range_str="", is_pdf_target=False):
    result = []
    for uploaded_file in files or []:
        fname = getattr(uploaded_file, "name", "Tài liệu")
        content = read_uploaded_file(uploaded_file, range_str, is_pdf_target)
        if len(content.strip()) > 30:
            result.append(f"\n--- TÀI LIỆU NGUỒN: {fname} ---")
            result.append(content)
    return normalize_source_text("\n".join(result))

def read_template_local(path="templates/KHBD_Mau.docx"):
    if not os.path.exists(path): return ""
    try:
        return read_docx_ordered(path)
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

def load_task_config():
    config_path = "prompts/task_config_khbd.txt"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "BẠN LÀ CHUYÊN GIA SƯ PHẠM CHUẨN PHỤ LỤC 4 CÔNG VĂN 5512."

def normalize_ai_result(result):
    if result is None: return ""
    if isinstance(result, str): return result.strip()
    if isinstance(result, dict):
        try:
            if "choices" in result and result["choices"]:
                content = result["choices"][0].get("message", {}).get("content")
                if content: return str(content).strip()
        except Exception:
            pass
        for key in ["text", "content", "response", "output", "answer"]:
            if key in result and isinstance(result[key], str):
                return result[key].strip()
    return str(result).strip()

def generate_ai(ai_engine, prompt):
    if ai_engine is None: raise RuntimeError("Chưa truyền AI Engine.")
    if hasattr(ai_engine, "generate_text"):
        return normalize_ai_result(ai_engine.generate_text(prompt))
    if hasattr(ai_engine, "generate"):
        return normalize_ai_result(ai_engine.generate(prompt))
    raise RuntimeError("AI Engine không phản hồi hoặc không có phương thức sinh văn bản hợp lệ.")

def validate_khbd_result(text):
    text = safe_text(text)
    if len(text) < 500:
        return False, "Nội dung giáo án quá ngắn."
    
    upper = text.upper()
    valid_count = sum(1 for kw in ["MỤC TIÊU", "THIẾT BỊ", "TIẾN TRÌNH", "HOẠT ĐỘNG"] if kw in upper)
    if valid_count < 3:
         return False, "Giáo án trả về thiếu các từ khóa sư phạm căn bản (Mục tiêu, Thiết bị, Tiến trình)."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, noi_dung_ppct, noi_dung_ai, noi_dung_mau, nls, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, hoat_dong, mode):
    if mode not in MODE_LABELS:
        raise ValueError(f"Chế độ soạn không hợp lệ: {mode}")

    task_config = load_task_config()
    source = safe_text(noi_dung_chinh)
    
    quality = diagnose_source_quality(source, "SGK")
    if quality["status"] != "valid" and mode == "tu_dong":
        raise ValueError(
            f"❌ Không đọc được nội dung văn bản từ tài liệu nguồn.\n\n"
            f"Chi tiết: {quality['message']}\n"
            f"Số ký tự: {quality['chars']}\n"
            f"Số từ: {quality['words']}"
        )

    ga_block = f"\n[GIÁO ÁN GỐC (THAM KHẢO CẤU TRÚC)]\n{safe_text(noi_dung_ga)}\n" if noi_dung_ga else ""
    ai_block = f"\n[HƯỚNG DẪN AI BỔ SUNG]\n{safe_text(noi_dung_ai)}\n" if noi_dung_ai else ""
    hoa_nhap_block = f"Bắt buộc thiết kế các hoạt động hỗ trợ riêng cho đối tượng: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else "Môi trường học tập đại trà."

    return (
        f"{task_config}\n\n"
        f"================================================================\n"
        f"THÔNG TIN BÀI HỌC VÀ THỜI LƯỢNG\n"
        f"================================================================\n"
        f"{thong_tin}\n\n"
        f"================================================================\n"
        f"NGUỒN KIẾN THỨC CHÍNH (SGK BẮT BUỘC SỬ DỤNG)\n"
        f"================================================================\n"
        f"{source}\n\n"
        f"================================================================\n"
        f"TÀI LIỆU CHỈ ĐẠO & THAM KHẢO\n"
        f"================================================================\n"
        f"[PHÂN PHỐI CHƯƠNG TRÌNH]\n"
        f"{safe_text(noi_dung_ppct)}\n"
        f"{ga_block}{ai_block}\n"
        f"================================================================\n"
        f"YÊU CẦU ĐẶC THÙ & TÍCH HỢP\n"
        f"================================================================\n"
        f"- Năng lực số: {nls}\n"
        f"- Tích hợp AI: {'Có sử dụng công cụ AI hỗ trợ.' if tich_hop_ai else 'Không yêu cầu.'}\n"
        f"- Giáo dục hòa nhập: {hoa_nhap_block}\n"
        f"- Hoạt động bổ sung giáo viên yêu cầu: {safe_text(hoat_dong)}\n\n"
        f"================================================================\n"
        f"RÀNG BUỘC NGHIÊM NGẶT (KNOWLEDGE SCOPE & FORMAT)\n"
        f"================================================================\n"
        f"1. CHỐNG SUY DIỄN: Mọi định nghĩa, ví dụ, câu hỏi phải được lấy TRỰC TIẾP từ NGUỒN KIẾN THỨC CHÍNH. Nghiêm cấm bịa đặt kiến thức ngoài SGK.\n"
        f"2. ĐỐI CHIẾU SỐ TIẾT: \n"
        f"   - Nếu bài học có 2 tiết trở lên, BẮT BUỘC phân tách rõ ràng tiến trình theo: ### TIẾT 1, ### TIẾT 2...\n"
        f"   - Mỗi tiết phải có đủ các hoạt động thực chất, không viết gộp chung.\n"
        f"3. KHUÔN MẪU (SCHEMA TƯƠNG THÍCH WORD):\n"
        f"{safe_text(noi_dung_mau)}\n\n"
        f"Hãy tạo giáo án chuẩn Markdown, bắt đầu ngay bằng # TÊN BÀI HỌC."
    )
