# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY
KIẾN TRÚC: SOURCE PIPELINE → KNOWLEDGE SCOPE → LESSON PLAN
FILE: views/xd_khbd_data.py
============================================================
"""

import streamlit as st
import os
import re
import json
import math
import pandas as pd
import PyPDF2

from docx import Document
from pathlib import Path
from io import BytesIO


# ============================================================
# 1. HẰNG SỐ
# ============================================================

NLS_GV_VAN_BAN_MAC_DINH = "18/2026/TT-BGDĐT"

MODE_LABELS = {
    "chinh_sua": "Chỉnh sửa và nâng cấp giáo án gốc",
    "tao_moi": "Soạn mới hoàn toàn từ tài liệu SGK",
    "tu_dong": "Soạn mới hoàn toàn từ tài liệu SGK"
}

# Ngưỡng tối thiểu để tránh gửi nguồn rỗng cho AI
MIN_SOURCE_CHARS = 1000
MIN_SOURCE_WORDS = 150

# Ngưỡng cảnh báo
WARNING_SOURCE_CHARS = 3000
WARNING_SOURCE_WORDS = 500


# ============================================================
# 2. KHUNG NĂNG LỰC SỐ
# ============================================================

KHUNG_NLS_GV = {
    "1. Miền 1: Tổ chức dạy học, giáo dục trong môi trường số": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": (
                "Sử dụng thiết bị cơ bản (máy tính, máy chiếu, bảng tương tác); "
                "Dùng ứng dụng di động giáo dục đơn giản."
            ),
            "Thành thạo": (
                "Lựa chọn, tích hợp học liệu số vào kế hoạch hoạt động; "
                "Thiết kế hoạt động học tập tương tác."
            ),
            "Nâng cao": (
                "Sáng tạo mô hình giáo dục ứng dụng công nghệ mới; "
                "Hướng dẫn đồng nghiệp sử dụng thiết bị số."
            )
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": (
                "Hướng dẫn học sinh thao tác cơ bản, an toàn trên thiết bị số "
                "có giám sát."
            ),
            "Thành thạo": (
                "Quan sát, hỗ trợ kịp thời khi học sinh gặp khó khăn "
                "tương tác công nghệ."
            ),
            "Nâng cao": (
                "Phát triển phương pháp hỗ trợ học tập trên nền tảng công nghệ "
                "tại nhà."
            )
        }
    },

    "2. Miền 2: Kiểm tra, đánh giá": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": (
                "Sử dụng thiết bị số ghi lại sản phẩm/khoảnh khắc học tập "
                "của học sinh."
            ),
            "Thành thạo": (
                "Thiết kế hoạt động đánh giá kĩ năng qua công nghệ "
                "và lưu trữ minh chứng."
            )
        }
    },

    "6. Miền 6: Trí tuệ nhân tạo (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": (
                "Sử dụng công cụ AI tạo sinh cơ bản hỗ trợ soạn thảo, "
                "tìm kiếm ý tưởng."
            ),
            "Thành thạo": (
                "Khai thác công cụ AI chuyên biệt tạo học liệu tương tác, "
                "cá nhân hóa."
            )
        }
    }
}


KHUNG_NLS_HS = {
    "1. Thông tin và dữ liệu số": {
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu": {
            "Mức 1": (
                "Xác định nhu cầu thông tin, tìm kiếm dữ liệu đơn giản "
                "trong môi trường số."
            ),
            "Mức 2": (
                "Sử dụng kĩ thuật tìm kiếm nâng cao để lấy dữ liệu, "
                "thông tin chính xác."
            )
        }
    }
}


# ============================================================
# 3. API NĂNG LỰC SỐ
# ============================================================

def get_nls_framework(loai_khung):
    return (
        KHUNG_NLS_GV
        if loai_khung == "Giáo viên (Thông tư 18)"
        else KHUNG_NLS_HS
    )


def get_nls_domains(loai_khung):
    return list(get_nls_framework(loai_khung).keys())


def get_nls_components(loai_khung, linh_vuc):
    framework = get_nls_framework(loai_khung)
    return list(framework.get(linh_vuc, {}).keys())


def get_nls_levels(loai_khung, linh_vuc, thanh_phan):
    framework = get_nls_framework(loai_khung)
    return list(
        framework
        .get(linh_vuc, {})
        .get(thanh_phan, {})
        .keys()
    )


def get_nls_content(
    loai_khung,
    linh_vuc,
    thanh_phan,
    muc_do
):
    framework = get_nls_framework(loai_khung)

    return (
        framework
        .get(linh_vuc, {})
        .get(thanh_phan, {})
        .get(muc_do, "")
    )


# ============================================================
# 4. SESSION STATE
# ============================================================

def init_session_state():

    defaults = {
        "khbd_mode": "tu_dong",
        "khbd_result": None,
        "khbd_nls_list": [],
        "khbd_hoat_dong_list": [],
        "khbd_processing": False,
        "khbd_nls_noi_dung": "",
        "khbd_source_quality": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_ket_qua():
    st.session_state["khbd_result"] = None
    st.session_state["khbd_source_quality"] = None


def reset_toan_bo_khbd():

    keys_to_reset = {
        "khbd_result": None,
        "khbd_nls_list": [],
        "khbd_hoat_dong_list": [],
        "khbd_nls_noi_dung": "",
        "khbd_mode": "tu_dong",
        "khbd_processing": False,
        "khbd_source_quality": None,
    }

    for key, value in keys_to_reset.items():
        st.session_state[key] = value


def set_mode(mode: str):

    if mode not in MODE_LABELS:
        raise ValueError(
            f"Chế độ soạn không hợp lệ: {mode}"
        )

    st.session_state.khbd_mode = mode


# ============================================================
# 5. LÀM SẠCH VĂN BẢN
# ============================================================

def safe_text(value):

    if value is None:
        return ""

    if isinstance(value, float):
        if math.isnan(value):
            return ""

    if not isinstance(value, str):
        value = str(value)

    text = value.replace("\x00", "")

    text = re.sub(
        r"[\r\t]+",
        " ",
        text
    )

    text = re.sub(
        r"[ ]{2,}",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def count_words(text):

    text = safe_text(text)

    if not text:
        return 0

    return len(
        re.findall(
            r"\S+",
            text,
            flags=re.UNICODE
        )
    )


# ============================================================
# 6. ĐỌC PDF
# ============================================================

def _parse_page_range(range_str, total_pages):

    start = 1
    end = total_pages

    if not range_str:
        return start, end

    match = re.match(
        r"^\s*(\d+)\s*-\s*(\d+)\s*$",
        str(range_str)
    )

    if match:

        start = max(
            1,
            int(match.group(1))
        )

        end = min(
            total_pages,
            int(match.group(2))
        )

    return start, end


def _extract_pdf_text_pypdf2(
    uploaded_file,
    range_str=""
):

    result = []

    try:

        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

        reader = PyPDF2.PdfReader(
            uploaded_file
        )

        total_pages = len(reader.pages)

        start, end = _parse_page_range(
            range_str,
            total_pages
        )

        for index in range(
            start,
            end + 1
        ):

            page = reader.pages[index - 1]

            text = page.extract_text() or ""

            text = safe_text(text)

            if text:

                result.append(
                    f"\n[PDF - Trang {index}]\n{text}"
                )

        return "\n".join(result)

    except Exception:

        return ""


def _ocr_pdf(
    uploaded_file,
    range_str=""
):

    """
    OCR fallback.

    Cần cài:

    pip install pdf2image pytesseract

    Đồng thời máy chủ cần có Tesseract OCR.
    """

    try:

        from pdf2image import convert_from_bytes
        import pytesseract

    except ImportError:

        return ""

    try:

        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

        pdf_bytes = uploaded_file.read()

        if not pdf_bytes:
            return ""

        reader = PyPDF2.PdfReader(
            BytesIO(pdf_bytes)
        )

        total_pages = len(reader.pages)

        start, end = _parse_page_range(
            range_str,
            total_pages
        )

        images = convert_from_bytes(
            pdf_bytes,
            dpi=200,
            first_page=start,
            last_page=end
        )

        result = []

        for offset, image in enumerate(images):

            page_number = start + offset

            try:

                text = pytesseract.image_to_string(
                    image,
                    lang="vie+eng"
                )

            except Exception:

                text = pytesseract.image_to_string(
                    image
                )

            text = safe_text(text)

            if text:

                result.append(
                    f"\n[OCR - PDF - Trang {page_number}]\n{text}"
                )

        return "\n".join(result)

    except Exception:

        return ""


def read_pdf(
    uploaded_file,
    range_str=""
):

    """
    Pipeline đọc PDF:

    1. PyPDF2
    2. Nếu text quá ngắn → OCR fallback
    3. Trả về nguồn có chất lượng tốt hơn
    """

    text_result = _extract_pdf_text_pypdf2(
        uploaded_file,
        range_str
    )

    if len(text_result) >= MIN_SOURCE_CHARS:

        return text_result

    ocr_result = _ocr_pdf(
        uploaded_file,
        range_str
    )

    if len(ocr_result) > len(text_result):

        return ocr_result

    return text_result


# ============================================================
# 7. ĐỌC DOCX
# ============================================================

def read_docx_ordered(source):

    result = []

    try:

        if isinstance(source, (str, Path)):

            doc = Document(source)

        elif hasattr(source, "read"):

            if hasattr(source, "seek"):
                source.seek(0)

            content = source.read()

            if isinstance(content, str):
                content = content.encode(
                    "utf-8"
                )

            doc = Document(
                BytesIO(content)
            )

        else:

            doc = Document(source)

        for element in doc.element.body:

            tag = element.tag

            if tag.endswith("}p") or tag.endswith("p"):

                from docx.text.paragraph import Paragraph

                paragraph = Paragraph(
                    element,
                    doc
                )

                text = safe_text(
                    paragraph.text
                )

                if text:
                    result.append(text)

            elif tag.endswith("}tbl") or tag.endswith("tbl"):

                from docx.table import Table

                table = Table(
                    element,
                    doc
                )

                result.append(
                    "\n[BẢNG DỮ LIỆU]"
                )

                for row in table.rows:

                    cells = []

                    for cell in row.cells:

                        cell_text = safe_text(
                            cell.text
                        ).replace(
                            "\n",
                            " "
                        )

                        cells.append(
                            cell_text
                        )

                    row_text = " | ".join(
                        cells
                    )

                    if row_text.strip():

                        result.append(
                            row_text
                        )

        return "\n".join(result)

    except Exception as e:

        return (
            "[LỖI ĐỌC DOCX: "
            + str(e)
            + "]"
        )


# ============================================================
# 8. ĐỌC EXCEL
# ============================================================

def read_excel_structured(uploaded_file):

    result = []

    try:

        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

        sheets = pd.read_excel(
            uploaded_file,
            sheet_name=None
        )

        for sheet_name, dataframe in sheets.items():

            result.append(
                f"\n[PHÂN PHỐI CHƯƠNG TRÌNH - SHEET: "
                f"{sheet_name}]"
            )

            dataframe = dataframe.fillna("")

            records = dataframe.to_dict(
                orient="records"
            )

            for index, record in enumerate(
                records,
                start=1
            ):

                clean_record = {}

                for key, value in record.items():

                    value = safe_text(value)

                    if value:

                        clean_record[
                            str(key).strip()
                        ] = value

                if clean_record:

                    result.append(
                        f"Dòng {index}: "
                        + json.dumps(
                            clean_record,
                            ensure_ascii=False
                        )
                    )

        return "\n".join(result)

    except Exception as e:

        return (
            "[LỖI ĐỌC EXCEL: "
            + str(e)
            + "]"
        )


# ============================================================
# 9. ĐỌC FILE CHUNG
# ============================================================

def read_uploaded_file(
    uploaded_file,
    range_str="",
    is_pdf_target=False
):

    if uploaded_file is None:

        return ""

    filename = getattr(
        uploaded_file,
        "name",
        "file"
    )

    extension = Path(
        filename.lower()
    ).suffix

    try:

        if extension == ".pdf":

            return read_pdf(
                uploaded_file,
                range_str
                if is_pdf_target
                else ""
            )

        if extension == ".docx":

            return read_docx_ordered(
                uploaded_file
            )

        if extension in [
            ".xlsx",
            ".xls"
        ]:

            return read_excel_structured(
                uploaded_file
            )

        return ""

    except Exception as e:

        return (
            "[LỖI ĐỌC FILE: "
            + str(e)
            + "]"
        )


def read_multiple_files(
    files,
    range_str="",
    is_pdf_target=False
):

    result = []

    for uploaded_file in files or []:

        filename = getattr(
            uploaded_file,
            "name",
            "Tài liệu"
        )

        result.append(
            f"\n--- TÀI LIỆU NGUỒN: "
            f"{filename} ---"
        )

        content = read_uploaded_file(
            uploaded_file,
            range_str,
            is_pdf_target
        )

        result.append(content)

    return "\n".join(result)


def read_template_local(
    path="templates/KHBD_Mau.docx"
):

    if not os.path.exists(path):

        return ""

    try:

        return read_docx_ordered(path)

    except Exception:

        return ""


# ============================================================
# 10. KIỂM ĐỊNH CHẤT LƯỢNG NGUỒN
# ============================================================

def inspect_source_quality(
    text,
    source_name="Tài liệu nguồn"
):

    text = safe_text(text)

    chars = len(text)

    words = count_words(text)

    has_error = (
        text.startswith("[LỖI")
        or "LỖI ĐỌC" in text[:500]
    )

    if has_error:

        return {
            "valid": False,
            "level": "error",
            "chars": chars,
            "words": words,
            "message": (
                f"{source_name} có lỗi khi đọc."
            )
        }

    if chars < MIN_SOURCE_CHARS:

        return {
            "valid": False,
            "level": "error",
            "chars": chars,
            "words": words,
            "message": (
                f"{source_name} không đủ dữ liệu "
                f"để xây dựng giáo án.\n\n"
                f"Số ký tự: {chars}\n"
                f"Số từ: {words}\n\n"
                "Nguyên nhân thường gặp:\n"
                "• PDF là bản scan;\n"
                "• PDF không có lớp văn bản;\n"
                "• Phạm vi trang được chọn quá hẹp;\n"
                "• Tài liệu tải lên không phải nội dung SGK."
            )
        }

    if words < MIN_SOURCE_WORDS:

        return {
            "valid": False,
            "level": "error",
            "chars": chars,
            "words": words,
            "message": (
                f"{source_name} có quá ít từ "
                "để xây dựng giáo án chi tiết."
            )
        }

    if (
        chars < WARNING_SOURCE_CHARS
        or words < WARNING_SOURCE_WORDS
    ):

        return {
            "valid": True,
            "level": "warning",
            "chars": chars,
            "words": words,
            "message": (
                f"Nguồn đọc được nhưng khá ngắn.\n"
                f"Số ký tự: {chars}\n"
                f"Số từ: {words}\n"
                "Nên kiểm tra lại phạm vi trang."
            )
        }

    return {
        "valid": True,
        "level": "ok",
        "chars": chars,
        "words": words,
        "message": (
            f"Nguồn đạt yêu cầu.\n"
            f"Số ký tự: {chars}\n"
            f"Số từ: {words}"
        )
    }


# ============================================================
# 11. CALLBACKS
# ============================================================

def add_nls():

    linh_vuc = safe_text(
        st.session_state.get(
            "khbd_nls_linh_vuc",
            ""
        )
    )

    thanh_phan = safe_text(
        st.session_state.get(
            "khbd_nls_thanh_phan",
            ""
        )
    )

    muc_do = safe_text(
        st.session_state.get(
            "khbd_nls_muc_do",
            ""
        )
    )

    noi_dung = safe_text(
        st.session_state.get(
            "khbd_nls_noi_dung",
            ""
        )
    )

    if not noi_dung:

        return

    loai_khung = st.session_state.get(
        "khbd_loai_khung_nls",
        ""
    )

    van_ban = (
        NLS_GV_VAN_BAN_MAC_DINH
        if loai_khung == "Giáo viên (Thông tư 18)"
        else "DigComp"
    )

    item = {
        "van_ban": van_ban,
        "linh_vuc": linh_vuc,
        "thanh_phan": thanh_phan,
        "muc_do": muc_do,
        "noi_dung": noi_dung,
    }

    if item not in st.session_state.khbd_nls_list:

        st.session_state.khbd_nls_list.append(
            item
        )


def format_nls():

    items = st.session_state.khbd_nls_list

    if not items:

        return (
            "Không tích hợp năng lực số cụ thể."
        )

    result = []

    for index, item in enumerate(
        items,
        start=1
    ):

        result.append(
            f"{index}. "
            f"[{item.get('van_ban', '')}] "
            f"{item.get('linh_vuc', '')} - "
            f"Thành phần: "
            f"{item.get('thanh_phan', '')} "
            f"({item.get('muc_do', '')}): "
            f"{item.get('noi_dung', '')}"
        )

    return "\n".join(result)


def add_activity():

    value = safe_text(
        st.session_state.get(
            "khbd_new_activity",
            ""
        )
    )

    if (
        value
        and value not in
        st.session_state.khbd_hoat_dong_list
    ):

        st.session_state.khbd_hoat_dong_list.append(
            value
        )

    st.session_state.khbd_new_activity = ""


# ============================================================
# 12. AI ENGINE
# ============================================================

def load_task_config():

    config_path = (
        "prompts/task_config_khbd.txt"
    )

    if os.path.exists(config_path):

        try:

            with open(
                config_path,
                "r",
                encoding="utf-8"
            ) as file:

                content = file.read().strip()

                if content:

                    return content

        except Exception:

            pass

    return (
        "BẠN LÀ CHUYÊN GIA SƯ PHẠM "
        "THIẾT KẾ KẾ HOẠCH BÀI DẠY "
        "THEO PHỤ LỤC 4 CÔNG VĂN 5512."
    )


def normalize_ai_result(result):

    if result is None:

        return ""

    if isinstance(result, str):

        return result.strip()

    if isinstance(result, dict):

        # OpenAI / OpenRouter
        try:

            choices = result.get(
                "choices",
                []
            )

            if choices:

                message = choices[0].get(
                    "message",
                    {}
                )

                content = message.get(
                    "content"
                )

                if isinstance(
                    content,
                    str
                ):

                    return content.strip()

                if isinstance(
                    content,
                    list
                ):

                    parts = []

                    for item in content:

                        if isinstance(
                            item,
                            dict
                        ) and item.get(
                            "type"
                        ) == "text":

                            parts.append(
                                item.get(
                                    "text",
                                    ""
                                )
                            )

                    if parts:

                        return "\n".join(
                            parts
                        ).strip()

        except Exception:

            pass

        # Gemini
        try:

            candidates = result.get(
                "candidates",
                []
            )

            if candidates:

                content = candidates[0].get(
                    "content",
                    {}
                )

                parts = content.get(
                    "parts",
                    []
                )

                texts = []

                for part in parts:

                    if isinstance(
                        part,
                        dict
                    ) and part.get(
                        "text"
                    ):

                        texts.append(
                            part["text"]
                        )

                if texts:

                    return "\n".join(
                        texts
                    ).strip()

        except Exception:

            pass

        # Generic
        for key in [
            "text",
            "content",
            "response",
            "output",
            "answer"
        ]:

            if key not in result:

                continue

            value = result[key]

            if isinstance(
                value,
                str
            ):

                return value.strip()

            if isinstance(
                value,
                list
            ):

                texts = []

                for item in value:

                    if isinstance(
                        item,
                        dict
                    ):

                        if item.get("text"):

                            texts.append(
                                str(
                                    item["text"]
                                )
                            )

                if texts:

                    return "\n".join(
                        texts
                    ).strip()

    return str(result).strip()


def generate_ai(
    ai_engine,
    prompt
):

    if ai_engine is None:

        raise RuntimeError(
            "Chưa truyền AI Engine."
        )

    if hasattr(
        ai_engine,
        "generate_text"
    ):

        return normalize_ai_result(
            ai_engine.generate_text(
                prompt
            )
        )

    if hasattr(
        ai_engine,
        "generate"
    ):

        return normalize_ai_result(
            ai_engine.generate(
                prompt
            )
        )

    raise RuntimeError(
        "AI Engine không phản hồi."
    )


# ============================================================
# 13. KIỂM TRA SỐ TIẾT
# ============================================================

def extract_lesson_count(
    thong_tin
):

    text = safe_text(
        thong_tin
    )

    patterns = [
        r"Số tiết\s*:\s*(\d+)",
        r"(\d+)\s*tiết",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            try:

                return max(
                    1,
                    int(
                        match.group(1)
                    )
                )

            except Exception:

                pass

    return 1


# ============================================================
# 14. VALIDATE KHBD
# ============================================================

def validate_khbd_result(
    text,
    expected_lessons=1
):

    text = safe_text(text)

    if len(text) < 100:

        return (
            False,
            "Nội dung trả về quá ngắn."
        )

    required_sections = [
        "MỤC TIÊU",
        "THIẾT BỊ DẠY HỌC",
        "TIẾN TRÌNH DẠY HỌC",
    ]

    upper_text = text.upper()

    for section in required_sections:

        if section not in upper_text:

            return (
                False,
                f"Thiếu mục bắt buộc: {section}"
            )

    activity_count = len(
        re.findall(
            r"Hoạt động\s+\d+",
            text,
            flags=re.IGNORECASE
        )
    )

    if activity_count < 3:

        return (
            False,
            "Giáo án có quá ít hoạt động."
        )

    if expected_lessons > 1:

        lesson_count = len(
            re.findall(
                r"(^|\n)#+\s*TIẾT\s+\d+",
                text,
                flags=re.IGNORECASE
            )
        )

        if lesson_count < expected_lessons:

            return (
                False,
                (
                    f"Yêu cầu {expected_lessons} tiết "
                    f"nhưng chỉ phát hiện "
                    f"{lesson_count} phần tiết."
                )
            )

    return (
        True,
        "Hợp lệ"
    )


# ============================================================
# 15. BUILD PROMPT
# ============================================================

def build_prompt(
    thong_tin,
    noi_dung_chinh,
    noi_dung_ga,
    noi_dung_ppct,
    noi_dung_ai,
    noi_dung_mau,
    nls,
    tich_hop_ai,
    tich_hop_hoa_nhap,
    nhu_cau_hoa_nhap,
    hoat_dong,
    mode
):

    if mode not in MODE_LABELS:

        raise ValueError(
            f"Chế độ soạn không hợp lệ: {mode}"
        )

    source_quality = inspect_source_quality(
        noi_dung_chinh,
        "Nguồn kiến thức chính"
    )

    if mode != "chinh_sua" and not source_quality["valid"]:

        raise ValueError(
            source_quality["message"]
        )

    lesson_count = extract_lesson_count(
        thong_tin
    )

    task_config = load_task_config()

    safe_source = safe_text(
        noi_dung_chinh
    )

    safe_ga = safe_text(
        noi_dung_ga
    )

    safe_ppct = safe_text(
        noi_dung_ppct
    )

    safe_ai = safe_text(
        noi_dung_ai
    )

    safe_template = safe_text(
        noi_dung_mau
    )

    safe_nhu_cau = safe_text(
        nhu_cau_hoa_nhap
    )

    safe_activities = safe_text(
        hoat_dong
    )

    if mode == "chinh_sua" and safe_ga:

        source_block = f"""
============================================================
GIÁO ÁN GỐC CẦN CHỈNH SỬA
============================================================
{safe_ga}

YÊU CẦU:
- Kế thừa những điểm tốt của giáo án gốc.
- Không được làm mất các nội dung kiến thức đúng.
- Bổ sung chi tiết nếu giáo án gốc còn sơ sài.
"""

    else:

        source_block = f"""
============================================================
NGUỒN KIẾN THỨC CHÍNH
============================================================
{safe_source}
"""

    ai_block = ""

    if safe_ai:

        ai_block = f"""
============================================================
TÀI LIỆU AI / YÊU CẦU BỔ SUNG
============================================================
{safe_ai}
"""

    ppct_block = ""

    if safe_ppct:

        ppct_block = f"""
============================================================
PHÂN PHỐI CHƯƠNG TRÌNH
============================================================
{safe_ppct}
"""

    hoa_nhap_block = (
        safe_nhu_cau
        if tich_hop_hoa_nhap
        and safe_nhu_cau
        else "Không yêu cầu đặc thù."
    )

    activities_block = (
        safe_activities
        if safe_activities
        else "Không có yêu cầu bổ sung."
    )

    return f"""
{task_config}

################################################################
# VAI TRÒ
################################################################

Bạn là chuyên gia cao cấp thiết kế Kế hoạch bài dạy
theo Chương trình GDPT 2018 và Phụ lục 4 Công văn 5512.

Bạn phải tạo một giáo án thực sự có thể sử dụng trong lớp học.

Không được viết giáo án chung chung.

################################################################
# THÔNG TIN BÀI DẠY
################################################################

{thong_tin}

SỐ TIẾT BẮT BUỘC: {lesson_count}

################################################################
# NGUYÊN TẮC TỐI QUAN TRỌNG
################################################################

NGUỒN KIẾN THỨC LÀ NGUỒN SỰ THẬT DUY NHẤT.

Bạn phải đọc và phân tích toàn bộ nội dung nguồn được cung cấp.

Không được coi phần nguồn kiến thức là một đoạn văn tham khảo hình thức.

Bạn phải thực sự trích xuất:

1. Tên bài học.
2. Các khái niệm.
3. Các định nghĩa.
4. Các đặc điểm.
5. Các quy tắc.
6. Các công thức.
7. Các đơn vị đo.
8. Các ví dụ.
9. Các thí nghiệm.
10. Các câu hỏi.
11. Các bảng số liệu.
12. Các hình ảnh hoặc mô tả thí nghiệm nếu có văn bản.
13. Các bài tập.
14. Các kết luận.
15. Các hoạt động học tập trong SGK.

################################################################
# QUY TRÌNH BẮT BUỘC
################################################################

BƯỚC 1 — ĐỌC NGUỒN

Đọc toàn bộ nguồn kiến thức chính.

BƯỚC 2 — LẬP BẢN ĐỒ KIẾN THỨC NỘI BỘ

Trước khi viết giáo án, phải xác định:

- Chủ đề/bài học chính.
- Các đơn vị kiến thức.
- Các khái niệm then chốt.
- Các công thức hoặc quy tắc.
- Các thí nghiệm.
- Các câu hỏi và bài tập.
- Mối liên hệ giữa các đơn vị kiến thức.

BƯỚC 3 — PHÂN BỔ KIẾN THỨC THEO SỐ TIẾT

Bài có {lesson_count} tiết.

Bắt buộc phân bổ kiến thức thực tế vào từng tiết.

Mỗi tiết phải có nội dung riêng.

Không được viết một giáo án ngắn rồi ghi thêm "tiết 1, tiết 2".

Ví dụ nếu có 4 tiết:

### TIẾT 1
Các nội dung SGK cụ thể thuộc phần đầu.

### TIẾT 2
Các nội dung SGK cụ thể tiếp theo.

### TIẾT 3
Các nội dung SGK cụ thể tiếp theo.

### TIẾT 4
Luyện tập, vận dụng và tổng kết dựa trên nội dung đã học.

Nếu nguồn kiến thức không đủ để phân bổ đủ {lesson_count} tiết,
phải khai thác sâu hơn các ví dụ, câu hỏi, thí nghiệm, bài tập
và hoạt động thực tế đã có trong nguồn.

TUYỆT ĐỐI KHÔNG ĐƯỢC tự thêm kiến thức ngoài nguồn.

################################################################
# QUY TẮC KNOWLEDGE SCOPE
################################################################

ĐƯỢC PHÉP:

- Diễn đạt lại kiến thức trong nguồn bằng ngôn ngữ sư phạm.
- Chia một nội dung lớn thành nhiều nhiệm vụ học tập.
- Chuyển câu hỏi SGK thành nhiệm vụ học tập.
- Tạo câu hỏi mới nhưng chỉ sử dụng kiến thức đã xuất hiện trong nguồn.
- Tạo đáp án và lời giải dựa trên nguồn.
- Thiết kế hoạt động nhóm dựa trên nội dung nguồn.

KHÔNG ĐƯỢC:

- Bịa khái niệm.
- Bịa công thức.
- Bịa số liệu.
- Bịa thí nghiệm.
- Đưa thêm nội dung thuộc bài khác.
- Dùng kiến thức ngoài nguồn để làm nền cho giáo án.
- Viết nội dung chung chung thay cho kiến thức thực tế.

################################################################
# YÊU CẦU CHI TIẾT CHO TỪNG HOẠT ĐỘNG
################################################################

Mỗi hoạt động phải có:

- Mục tiêu cụ thể.
- Nội dung kiến thức cụ thể.
- Nhiệm vụ cụ thể.
- Sản phẩm cụ thể.
- Đáp án hoặc kết luận cụ thể.
- Tổ chức thực hiện theo 4 bước.

Không được viết:

"Học sinh hoàn thành nhiệm vụ."

"Học sinh hiểu bài."

"Học sinh nắm được kiến thức."

Thay vào đó phải viết cụ thể:

- Học sinh trả lời câu hỏi nào.
- Dựa vào dữ kiện nào.
- Thực hiện thao tác nào.
- Tính đại lượng nào.
- Rút ra kết luận nào.
- Sản phẩm cuối cùng là gì.

################################################################
# NGUỒN DỮ LIỆU
################################################################

{source_block}

{ppct_block}

{ai_block}

################################################################
# TÍCH HỢP
################################################################

NĂNG LỰC SỐ:

{nls}

TÍCH HỢP AI:

{
    "Có tích hợp công cụ AI vào hoạt động nhận thức của học sinh."
    if tich_hop_ai
    else
    "Không bắt buộc tích hợp AI."
}

GIÁO DỤC HÒA NHẬP:

{hoa_nhap_block}

HOẠT ĐỘNG GIÁO VIÊN YÊU CẦU:

{activities_block}

################################################################
# CẤU TRÚC ĐẦU RA BẮT BUỘC
################################################################

# [TÊN BÀI HỌC]

## I. MỤC TIÊU

### 1. Về kiến thức

Phải nêu đúng kiến thức thực tế của bài.

### 2. Về năng lực

### 3. Về phẩm chất

## II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU

### 1. Đối với giáo viên

### 2. Đối với học sinh

## III. TIẾN TRÌNH DẠY HỌC

"""

for lesson in range(1, lesson_count + 1):

    pass

return f"""
{task_config}

################################################################
# YÊU CẦU ĐẦU RA THỰC TẾ
################################################################

Hãy viết giáo án hoàn chỉnh ngay bây giờ.

Bắt buộc:

- Có đủ {lesson_count} tiết.
- Mỗi tiết có nội dung kiến thức riêng.
- Nội dung phải dựa trực tiếp vào nguồn.
- Không viết chung chung.
- Có câu hỏi cụ thể.
- Có nhiệm vụ cụ thể.
- Có sản phẩm cụ thể.
- Có đáp án/kết luận cụ thể.
- Có 4 bước tổ chức thực hiện.
- Bám sát Phụ lục 4 Công văn 5512.

Mỗi tiết cần có thể sử dụng các hoạt động:

### Hoạt động 1: Khởi động

### Hoạt động 2: Hình thành kiến thức mới

### Hoạt động 3: Luyện tập

### Hoạt động 4: Vận dụng

Tùy nội dung thực tế của nguồn, có thể chia hoạt động thành
nhiều nhiệm vụ nhỏ hơn.

Không được rút gọn toàn bộ bài thành một đoạn tóm tắt.

Không được chào hỏi.

Không giải thích ngoài lề.

Bắt đầu ngay bằng:

# [TÊN BÀI HỌC]

################################################################
# MẪU KHBD THAM KHẢO
################################################################

{safe_template}
"""
