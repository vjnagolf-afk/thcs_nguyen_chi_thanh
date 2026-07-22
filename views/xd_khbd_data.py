# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY
KIẾN TRÚC KNOWLEDGE SCOPE + OCR + 5512
============================================================

FILE:
views/xd_khbd_data.py

MỤC TIÊU KIẾN TRÚC:

1. Đọc được PDF có lớp text.
2. Phát hiện PDF scan.
3. OCR PDF scan khi có công cụ OCR.
4. Không gửi tài liệu rỗng / tài liệu lỗi cho AI.
5. Tách rõ:
   - SGK / nguồn kiến thức chính
   - Giáo án gốc
   - PPCT
   - Tài liệu AI bổ sung
6. Xây dựng Knowledge Scope trước khi gọi AI.
7. Ép AI bám nội dung thực tế của SGK.
8. Bảo đảm giáo án 1, 2, 3, 4 tiết được phân bổ đúng.
9. Giữ tương thích với UI hiện tại.
============================================================
"""

import streamlit as st
import os
import re
import json
import math
import logging
import tempfile
import subprocess
import shutil

import pandas as pd
import PyPDF2

from docx import Document
from pathlib import Path
from io import BytesIO


# ============================================================
# 0. LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# 1. HẰNG SỐ
# ============================================================

NLS_GV_VAN_BAN_MAC_DINH = "18/2026/TT-BGDĐT"

MODE_LABELS = {
    "chinh_sua": "Chỉnh sửa và nâng cấp giáo án gốc",
    "tao_moi": "Soạn mới hoàn toàn từ tài liệu SGK",
    "tu_dong": "Soạn mới hoàn toàn từ tài liệu SGK",
}

# Ngưỡng chất lượng nguồn
MIN_SOURCE_CHARS = 800
MIN_SOURCE_WORDS = 120

# Nếu PDF ít hơn ngưỡng này, xem xét OCR
PDF_TEXT_MIN_CHARS = 500

# Chunk cho các tài liệu dài
DEFAULT_CHUNK_SIZE = 18000
DEFAULT_CHUNK_OVERLAP = 1000


# ============================================================
# 2. KHUNG NĂNG LỰC SỐ
# ============================================================

KHUNG_NLS_GV = {
    "1. Miền 1: Tổ chức dạy học, giáo dục trong môi trường số": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": (
                "Sử dụng thiết bị cơ bản như máy tính, máy chiếu, "
                "bảng tương tác; dùng ứng dụng di động giáo dục đơn giản."
            ),
            "Thành thạo": (
                "Lựa chọn, tích hợp học liệu số vào kế hoạch hoạt động; "
                "thiết kế hoạt động học tập tương tác."
            ),
            "Nâng cao": (
                "Sáng tạo mô hình giáo dục ứng dụng công nghệ mới; "
                "hướng dẫn đồng nghiệp sử dụng thiết bị số."
            ),
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": (
                "Hướng dẫn học sinh thao tác cơ bản, an toàn trên thiết bị số "
                "có giám sát."
            ),
            "Thành thạo": (
                "Quan sát, hỗ trợ kịp thời khi học sinh gặp khó khăn "
                "trong tương tác với công nghệ."
            ),
            "Nâng cao": (
                "Phát triển phương pháp hỗ trợ học tập trên nền tảng "
                "công nghệ tại nhà."
            ),
        },
    },
    "2. Miền 2: Kiểm tra, đánh giá": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": (
                "Sử dụng thiết bị số ghi lại sản phẩm hoặc khoảnh khắc "
                "học tập của học sinh."
            ),
            "Thành thạo": (
                "Thiết kế hoạt động đánh giá kĩ năng qua công nghệ "
                "và lưu trữ minh chứng."
            ),
        }
    },
    "6. Miền 6: Trí tuệ nhân tạo (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": (
                "Sử dụng công cụ AI tạo sinh cơ bản hỗ trợ soạn thảo "
                "và tìm kiếm ý tưởng."
            ),
            "Thành thạo": (
                "Khai thác công cụ AI chuyên biệt tạo học liệu tương tác "
                "và cá nhân hóa."
            ),
        }
    },
}


KHUNG_NLS_HS = {
    "1. Thông tin và dữ liệu số": {
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu": {
            "Mức 1": (
                "Xác định nhu cầu thông tin, tìm kiếm dữ liệu đơn giản "
                "trong môi trường số."
            ),
            "Mức 2": (
                "Sử dụng kĩ thuật tìm kiếm nâng cao để lấy dữ liệu "
                "và thông tin chính xác."
            ),
        }
    }
}


# ============================================================
# 3. API NĂNG LỰC SỐ
# ============================================================

def get_nls_framework(loai_khung):
    if loai_khung == "Giáo viên (Thông tư 18)":
        return KHUNG_NLS_GV
    return KHUNG_NLS_HS


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
    muc_do,
):
    framework = get_nls_framework(loai_khung)

    try:
        return framework[
            linh_vuc
        ][
            thanh_phan
        ][
            muc_do
        ]
    except Exception:
        return ""


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
        "khbd_source_diagnostics": None,
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
    st.session_state["khbd_source_quality"] = None
    st.session_state["khbd_source_diagnostics"] = None


def set_mode(mode: str):

    if mode not in MODE_LABELS:

        raise ValueError(
            f"Chế độ soạn không hợp lệ: {mode}"
        )

    st.session_state.khbd_mode = mode


# ============================================================
# 5. CHUẨN HÓA VĂN BẢN
# ============================================================

def safe_text(value):

    if value is None:

        return ""

    if not isinstance(value, str):

        value = str(value)

    text = value.replace("\x00", "")

    text = text.replace("\ufeff", "")

    text = text.replace("\u200b", "")

    text = re.sub(r"[\r\t]+", " ", text)

    text = re.sub(
        r"[ ]{2,}",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def normalize_source_text(text):

    text = safe_text(text)

    if not text:

        return ""

    # Ghép các dòng bị ngắt bất thường
    text = re.sub(
        r"(?<![.!?:;])\n(?=[a-zà-ỹA-ZÀ-Ỹ0-9])",
        " ",
        text,
    )

    # Chuẩn hóa khoảng trắng
    text = re.sub(
        r"[ ]{2,}",
        " ",
        text,
    )

    # Giữ khoảng cách đoạn
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def count_words(text):

    if not text:

        return 0

    return len(
        re.findall(
            r"\S+",
            text,
        )
    )


# ============================================================
# 6. CHẨN ĐOÁN CHẤT LƯỢNG TÀI LIỆU
# ============================================================

def diagnose_source_quality(
    text,
    source_name="Tài liệu nguồn",
):

    text = safe_text(text)

    chars = len(text)

    words = count_words(text)

    has_error = (
        "[LỖI ĐỌC"
        in text.upper()
    )

    is_too_short = (
        chars < MIN_SOURCE_CHARS
        or words < MIN_SOURCE_WORDS
    )

    if has_error:

        status = "error"

        message = (
            f"{source_name} có lỗi khi đọc."
        )

    elif is_too_short:

        status = "insufficient"

        message = (
            f"{source_name} không đủ dữ liệu."
        )

    else:

        status = "valid"

        message = (
            f"{source_name} đủ dữ liệu."
        )

    return {
        "source_name": source_name,
        "chars": chars,
        "words": words,
        "status": status,
        "message": message,
    }


# ============================================================
# 7. OCR PDF
# ============================================================

def is_ocr_available():

    return (
        shutil.which("tesseract")
        is not None
    )


def is_ocrmypdf_available():

    return (
        shutil.which("ocrmypdf")
        is not None
    )


def ocr_pdf_with_ocrmypdf(
    uploaded_file,
):

    if not is_ocrmypdf_available():

        return ""

    temp_input = None

    temp_output = None

    try:

        suffix = ".pdf"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as f:

            content = uploaded_file.read()

            f.write(content)

            temp_input = f.name

        temp_output = (
            temp_input
            + "_ocr.pdf"
        )

        command = [
            "ocrmypdf",
            "--skip-text",
            "--force-ocr",
            "--deskew",
            temp_input,
            temp_output,
        ]

        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300,
            check=False,
        )

        if not os.path.exists(
            temp_output
        ):

            return ""

        with open(
            temp_output,
            "rb",
        ) as f:

            reader = PyPDF2.PdfReader(f)

            pages = []

            for index, page in enumerate(
                reader.pages,
                start=1,
            ):

                text = page.extract_text() or ""

                text = safe_text(text)

                if text:

                    pages.append(
                        f"\n[PDF OCR - Trang {index}]\n"
                        f"{text}"
                    )

            return "\n".join(pages)

    except Exception as e:

        logger.warning(
            "OCR PDF lỗi: %s",
            e,
        )

        return ""

    finally:

        for path in [
            temp_input,
            temp_output,
        ]:

            if path and os.path.exists(path):

                try:

                    os.remove(path)

                except Exception:

                    pass


def ocr_pdf_with_pytesseract(
    uploaded_file,
    range_str="",
):

    try:

        import pytesseract

        from pdf2image import convert_from_bytes

    except ImportError:

        return ""

    if not is_ocr_available():

        return ""

    try:

        content = uploaded_file.read()

        start = 1

        end = None

        if range_str and "-" in range_str:

            try:

                s, e = range_str.split("-")

                start = max(
                    1,
                    int(s.strip()),
                )

                end = int(
                    e.strip()
                )

            except Exception:

                pass

        images = convert_from_bytes(
            content,
            dpi=200,
            first_page=start,
            last_page=end,
        )

        pages = []

        for index, image in enumerate(
            images,
            start=start,
        ):

            text = pytesseract.image_to_string(
                image,
                lang="vie+eng",
            )

            text = safe_text(text)

            if text:

                pages.append(
                    f"\n[PDF OCR - Trang {index}]\n"
                    f"{text}"
                )

        return "\n".join(pages)

    except Exception as e:

        logger.warning(
            "Pytesseract OCR lỗi: %s",
            e,
        )

        return ""


# ============================================================
# 8. ĐỌC PDF NHIỀU TẦNG
# ============================================================

def read_pdf(
    uploaded_file,
    range_str="",
    enable_ocr=True,
):

    result = []

    try:

        # ----------------------------------------------------
        # TẦNG 1: ĐỌC TEXT GỐC
        # ----------------------------------------------------

        content = uploaded_file.read()

        reader = PyPDF2.PdfReader(
            BytesIO(content)
        )

        total_pages = len(
            reader.pages
        )

        start = 1

        end = total_pages

        if range_str and "-" in range_str:

            try:

                s, e = range_str.split("-")

                start = max(
                    1,
                    int(s.strip()),
                )

                end = min(
                    total_pages,
                    int(e.strip()),
                )

            except ValueError:

                pass

        for index in range(
            start,
            end + 1,
        ):

            page = reader.pages[
                index - 1
            ]

            text = page.extract_text() or ""

            text = safe_text(text)

            if text:

                result.append(
                    f"\n[PDF - Trang {index}]\n"
                    f"{text}"
                )

        text_result = "\n".join(result)

        # ----------------------------------------------------
        # KIỂM TRA TEXT
        # ----------------------------------------------------

        quality = diagnose_source_quality(
            text_result,
            "PDF",
        )

        if quality["status"] == "valid":

            return normalize_source_text(
                text_result
            )

        # ----------------------------------------------------
        # TẦNG 2: OCRmyPDF
        # ----------------------------------------------------

        if enable_ocr:

            try:

                uploaded_file.seek(0)

                ocr_result = (
                    ocr_pdf_with_ocrmypdf(
                        uploaded_file
                    )
                )

                if len(ocr_result) > len(
                    text_result
                ):

                    ocr_quality = (
                        diagnose_source_quality(
                            ocr_result,
                            "PDF OCR",
                        )
                    )

                    if (
                        ocr_quality[
                            "status"
                        ]
                        == "valid"
                    ):

                        return normalize_source_text(
                            ocr_result
                        )

            except Exception:

                pass

        # ----------------------------------------------------
        # TẦNG 3: PYTESSERACT
        # ----------------------------------------------------

        if enable_ocr:

            try:

                uploaded_file.seek(0)

                ocr_result = (
                    ocr_pdf_with_pytesseract(
                        uploaded_file,
                        range_str,
                    )
                )

                if len(ocr_result) > len(
                    text_result
                ):

                    return normalize_source_text(
                        ocr_result
                    )

            except Exception:

                pass

        # ----------------------------------------------------
        # KHÔNG ĐỌC ĐƯỢC
        # ----------------------------------------------------

        return (
            "[PDF KHÔNG CÓ LỚP VĂN BẢN]\n"
            f"Số ký tự đọc được: {len(text_result)}\n"
            f"Số từ đọc được: {count_words(text_result)}\n"
            "Cần OCR hoặc PDF có lớp văn bản."
        )

    except Exception as e:

        return (
            f"[LỖI ĐỌC PDF: {str(e)}]"
        )


# ============================================================
# 9. ĐỌC DOCX BẢO TOÀN THỨ TỰ
# ============================================================

def read_docx_ordered(source):

    result = []

    try:

        if isinstance(
            source,
            (str, Path),
        ):

            doc = Document(
                source
            )

        elif hasattr(
            source,
            "read",
        ):

            content = source.read()

            if isinstance(
                content,
                str,
            ):

                content = content.encode(
                    "utf-8"
                )

            doc = Document(
                BytesIO(content)
            )

        else:

            doc = Document(
                source
            )

        for element in doc.element.body:

            if (
                element.tag.endswith(
                    "p"
                )
                or element.tag.endswith(
                    "}p"
                )
            ):

                from docx.text.paragraph import Paragraph

                paragraph = Paragraph(
                    element,
                    doc,
                )

                text = safe_text(
                    paragraph.text
                )

                if text:

                    result.append(
                        text
                    )

            elif (
                element.tag.endswith(
                    "tbl"
                )
                or element.tag.endswith(
                    "}tbl"
                )
            ):

                from docx.table import Table

                table = Table(
                    element,
                    doc,
                )

                result.append(
                    "\n[BẢNG DỮ LIỆU]"
                )

                for row in table.rows:

                    cells = [
                        safe_text(
                            cell.text
                        ).replace(
                            "\n",
                            " ",
                        )
                        for cell in row.cells
                    ]

                    row_text = (
                        " | ".join(
                            cells
                        )
                    )

                    if row_text.strip():

                        result.append(
                            row_text
                        )

        return normalize_source_text(
            "\n".join(result)
        )

    except Exception as e:

        return (
            f"[LỖI ĐỌC DOCX: {str(e)}]"
        )


# ============================================================
# 10. ĐỌC EXCEL CÓ CẤU TRÚC
# ============================================================

def read_excel_structured(
    uploaded_file,
):

    result = []

    try:

        sheets = pd.read_excel(
            uploaded_file,
            sheet_name=None,
        )

        for (
            sheet_name,
            dataframe,
        ) in sheets.items():

            result.append(
                f"\n[PHÂN PHỐI CHƯƠNG TRÌNH - "
                f"SHEET: {sheet_name}]"
            )

            dataframe = dataframe.fillna("")

            records = dataframe.to_dict(
                orient="records"
            )

            for idx, rec in enumerate(
                records,
                start=1,
            ):

                clean_rec = {}

                for key, value in rec.items():

                    key = safe_text(
                        key
                    )

                    value = safe_text(
                        value
                    )

                    if value:

                        clean_rec[key] = value

                if clean_rec:

                    result.append(
                        f"Dòng {idx}: "
                        + json.dumps(
                            clean_rec,
                            ensure_ascii=False,
                        )
                    )

        return normalize_source_text(
            "\n".join(result)
        )

    except Exception as e:

        return (
            f"[LỖI ĐỌC EXCEL: {str(e)}]"
        )


# ============================================================
# 11. ĐỌC FILE
# ============================================================

def read_uploaded_file(
    uploaded_file,
    range_str="",
    is_pdf_target=False,
):

    if uploaded_file is None:

        return ""

    filename = getattr(
        uploaded_file,
        "name",
        "file.docx",
    ).lower()

    extension = Path(
        filename
    ).suffix.lower()

    try:

        if extension == ".pdf":

            return read_pdf(
                uploaded_file,
                range_str
                if is_pdf_target
                else "",
                enable_ocr=True,
            )

        if extension == ".docx":

            return read_docx_ordered(
                uploaded_file
            )

        if extension in [
            ".xlsx",
            ".xls",
        ]:

            return read_excel_structured(
                uploaded_file
            )

        return ""

    except Exception as e:

        return (
            f"[LỖI ĐỌC FILE: {e}]"
        )


def read_multiple_files(
    files,
    range_str="",
    is_pdf_target=False,
):

    result = []

    for uploaded_file in files or []:

        fname = getattr(
            uploaded_file,
            "name",
            "Tài liệu",
        )

        result.append(
            f"\n--- TÀI LIỆU NGUỒN: {fname} ---"
        )

        result.append(
            read_uploaded_file(
                uploaded_file,
                range_str,
                is_pdf_target,
            )
        )

    return normalize_source_text(
        "\n".join(result)
    )


def read_template_local(
    path="templates/KHBD_Mau.docx",
):

    if not os.path.exists(path):

        return ""

    try:

        return read_docx_ordered(
            path
        )

    except Exception:

        return ""


# ============================================================
# 12. SESSION CALLBACKS
# ============================================================

def add_nls():

    linh_vuc = safe_text(
        st.session_state.get(
            "khbd_nls_linh_vuc",
            "",
        )
    )

    thanh_phan = safe_text(
        st.session_state.get(
            "khbd_nls_thanh_phan",
            "",
        )
    )

    muc_do = safe_text(
        st.session_state.get(
            "khbd_nls_muc_do",
            "",
        )
    )

    noi_dung = safe_text(
        st.session_state.get(
            "khbd_nls_noi_dung",
            "",
        )
    )

    if not noi_dung:

        return

    if (
        st.session_state.get(
            "khbd_loai_khung_nls"
        )
        == "Giáo viên (Thông tư 18)"
    ):

        van_ban = (
            NLS_GV_VAN_BAN_MAC_DINH
        )

    else:

        van_ban = "DigComp"

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
        start=1,
    ):

        result.append(
            f"{index}. "
            f"[{item['van_ban']}] "
            f"{item['linh_vuc']} - "
            f"Thành phần: "
            f"{item['thanh_phan']} "
            f"({item['muc_do']}): "
            f"{item['noi_dung']}"
        )

    return "\n".join(
        result
    )


def add_activity():

    value = safe_text(
        st.session_state.get(
            "khbd_new_activity",
            "",
        )
    )

    if (
        value
        and value
        not in st.session_state.khbd_hoat_dong_list
    ):

        st.session_state.khbd_hoat_dong_list.append(
            value
        )

    st.session_state.khbd_new_activity = ""


# ============================================================
# 13. AI ENGINE
# ============================================================

def load_task_config():

    config_path = (
        "prompts/task_config_khbd.txt"
    )

    if os.path.exists(
        config_path
    ):

        try:

            with open(
                config_path,
                "r",
                encoding="utf-8",
            ) as f:

                return f.read().strip()

        except Exception:

            pass

    return (
        "BẠN LÀ CHUYÊN GIA SƯ PHẠM "
        "CHUẨN PHỤ LỤC 4 CÔNG VĂN 5512."
    )


def normalize_ai_result(result):

    if result is None:

        return ""

    if isinstance(
        result,
        str,
    ):

        return result.strip()

    if isinstance(
        result,
        dict,
    ):

        try:

            if (
                "choices"
                in result
                and result["choices"]
            ):

                message = (
                    result[
                        "choices"
                    ][0].get(
                        "message",
                        {},
                    )
                )

                content = message.get(
                    "content"
                )

                if content:

                    return str(
                        content
                    ).strip()

        except Exception:

            pass

        try:

            if (
                "candidates"
                in result
                and result["candidates"]
            ):

                parts = (
                    result[
                        "candidates"
                    ][0]
                    .get(
                        "content",
                        {},
                    )
                    .get(
                        "parts",
                        [],
                    )
                )

                texts = []

                for part in parts:

                    if (
                        isinstance(
                            part,
                            dict,
                        )
                        and part.get(
                            "text"
                        )
                    ):

                        texts.append(
                            str(
                                part[
                                    "text"
                                ]
                            )
                        )

                if texts:

                    return "\n".join(
                        texts
                    ).strip()

        except Exception:

            pass

        for key in [
            "text",
            "content",
            "response",
            "output",
            "answer",
        ]:

            if key not in result:

                continue

            value = result[key]

            if isinstance(
                value,
                str,
            ):

                return value.strip()

            if isinstance(
                value,
                list,
            ):

                texts = []

                for item in value:

                    if (
                        isinstance(
                            item,
                            dict,
                        )
                        and item.get(
                            "text"
                        )
                    ):

                        texts.append(
                            str(
                                item[
                                    "text"
                                ]
                            )
                        )

                if texts:

                    return "\n".join(
                        texts
                    ).strip()

    return str(
        result
    ).strip()


def generate_ai(
    ai_engine,
    prompt,
):

    if ai_engine is None:

        raise RuntimeError(
            "Chưa truyền AI Engine."
        )

    if hasattr(
        ai_engine,
        "generate_text",
    ):

        return normalize_ai_result(
            ai_engine.generate_text(
                prompt
            )
        )

    if hasattr(
        ai_engine,
        "generate",
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
# 14. XÂY DỰNG KNOWLEDGE SCOPE
# ============================================================

def build_knowledge_scope(
    noi_dung_chinh,
    noi_dung_ga="",
    noi_dung_ppct="",
    noi_dung_ai="",
):

    source = safe_text(
        noi_dung_chinh
    )

    if not source:

        raise ValueError(
            "Nguồn kiến thức chính đang rỗng."
        )

    diagnostics = diagnose_source_quality(
        source,
        "Nguồn kiến thức chính",
    )

    if (
        diagnostics["status"]
        != "valid"
    ):

        raise ValueError(
            "Tài liệu nguồn không đủ dữ liệu "
            "để xây dựng giáo án.\n\n"
            f"{diagnostics['message']}\n"
            f"Số ký tự: {diagnostics['chars']}\n"
            f"Số từ: {diagnostics['words']}"
        )

    return {
        "source": source,

        "source_chars": diagnostics[
            "chars"
        ],

        "source_words": diagnostics[
            "words"
        ],

        "source_quality": diagnostics,

        "original_lesson_plan": safe_text(
            noi_dung_ga
        ),

        "curriculum": safe_text(
            noi_dung_ppct
        ),

        "ai_reference": safe_text(
            noi_dung_ai
        ),
    }


# ============================================================
# 15. CHUNK TÀI LIỆU
# ============================================================

def split_text_chunks(
    text,
    chunk_size=DEFAULT_CHUNK_SIZE,
    overlap=DEFAULT_CHUNK_OVERLAP,
):

    text = safe_text(text)

    if len(text) <= chunk_size:

        return [
            text
        ]

    chunks = []

    start = 0

    while start < len(text):

        end = min(
            start + chunk_size,
            len(text),
        )

        if end < len(text):

            boundary = text.rfind(
                "\n\n",
                start,
                end,
            )

            if boundary > start:

                end = boundary

        chunk = text[
            start:end
        ].strip()

        if chunk:

            chunks.append(
                chunk
            )

        if end >= len(text):

            break

        start = max(
            end - overlap,
            start + 1,
        )

    return chunks


# ============================================================
# 16. VALIDATION GIÁO ÁN
# ============================================================

def validate_khbd_result(
    text,
):

    text = safe_text(
        text
    )

    if len(text) < 1000:

        return (
            False,
            "Nội dung giáo án quá ngắn."
        )

    upper = text.upper()

    required_keywords = [
        "MỤC TIÊU",
        "THIẾT BỊ DẠY HỌC",
        "TIẾN TRÌNH DẠY HỌC",
    ]

    for keyword in required_keywords:

        if keyword not in upper:

            return (
                False,
                f"Thiếu phần bắt buộc: "
                f"{keyword}",
            )

    activity_count = len(
        re.findall(
            r"HOẠT ĐỘNG\s+[1-9]",
            upper,
        )
    )

    if activity_count < 3:

        return (
            False,
            "Giáo án có quá ít hoạt động."
        )

    return (
        True,
        "Hợp lệ",
    )


# ============================================================
# 17. BUILD PROMPT CHUYÊN SÂU
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
    mode,
):

    if mode not in MODE_LABELS:

        raise ValueError(
            f"Chế độ soạn không hợp lệ: {mode}"
        )

    mode_text = MODE_LABELS[
        mode
    ]

    source = safe_text(
        noi_dung_chinh
    )

    quality = diagnose_source_quality(
        source,
        "SGK",
    )

    if quality["status"] != "valid":

        raise ValueError(
            "Tài liệu nguồn không đủ dữ liệu "
            "để xây dựng giáo án.\n"
            f"Số ký tự: {quality['chars']}\n"
            f"Số từ: {quality['words']}"
        )

    task_config = load_task_config()

    safe_ai = safe_text(
        noi_dung_ai
    )

    ai_block = ""

    if safe_ai:

        ai_block = f"""
------------------------------------------------------------
TÀI LIỆU / HƯỚNG DẪN AI BỔ SUNG
------------------------------------------------------------
{safe_ai}
"""

    safe_need = safe_text(
        nhu_cau_hoa_nhap
    )

    if (
        tich_hop_hoa_nhap
        and safe_need
    ):

        inclusion_block = f"""
Học sinh cần hỗ trợ hòa nhập:
{safe_need}

Bắt buộc điều chỉnh trực tiếp trong từng hoạt động:
- Câu hỏi.
- Phiếu học tập.
- Thời gian.
- Mức độ nhiệm vụ.
- Hình thức hỗ trợ.
"""

    else:

        inclusion_block = (
            "Không có yêu cầu hòa nhập đặc thù."
        )

    safe_activity = safe_text(
        hoat_dong
    )

    activity_block = ""

    if safe_activity:

        activity_block = f"""
------------------------------------------------------------
HOẠT ĐỘNG BỔ SUNG THEO YÊU CẦU GIÁO VIÊN
------------------------------------------------------------
{safe_activity}
"""

    ga_block = ""

    if (
        mode == "chinh_sua"
        and safe_text(noi_dung_ga)
    ):

        ga_block = f"""
------------------------------------------------------------
GIÁO ÁN GỐC
------------------------------------------------------------
Chỉ được kế thừa cấu trúc và các ý tưởng phù hợp.
Không được thay thế hoặc làm mất nội dung kiến thức SGK.

{safe_text(noi_dung_ga)}
"""

    return f"""
{task_config}

================================================================
VAI TRÒ
================================================================

Bạn là chuyên gia xây dựng kế hoạch bài dạy Khoa học tự nhiên
theo Chương trình GDPT 2018 và cấu trúc Phụ lục 4 Công văn 5512.

Nhiệm vụ của bạn là xây dựng một giáo án CHI TIẾT, CỤ THỂ,
CÓ THỂ DÙNG TRỰC TIẾP TRONG LỚP HỌC.

================================================================
CHẾ ĐỘ SOẠN
================================================================

{mode_text}

Thông tin bài học và thời lượng:
{thong_tin}

================================================================
QUY TẮC PHÂN BỔ THỜI LƯỢNG
================================================================

Đây là quy tắc bắt buộc:

1. Xác định chính xác bài có bao nhiêu tiết.

2. Nếu bài có 1 tiết:
   - Xây dựng tiến trình cho 1 tiết.

3. Nếu bài có 2 tiết:
   - Bắt buộc có:
     ### TIẾT 1
     ### TIẾT 2

4. Nếu bài có 3 tiết:
   - Bắt buộc có:
     ### TIẾT 1
     ### TIẾT 2
     ### TIẾT 3

5. Nếu bài có 4 tiết:
   - Bắt buộc có:
     ### TIẾT 1
     ### TIẾT 2
     ### TIẾT 3
     ### TIẾT 4

KHÔNG ĐƯỢC viết một đoạn tiến trình chung chung cho toàn bộ bài.

Mỗi tiết phải có:
- Nội dung kiến thức cụ thể.
- Hoạt động học cụ thể.
- Câu hỏi / nhiệm vụ cụ thể.
- Sản phẩm học tập cụ thể.
- Đánh giá cụ thể.

================================================================
KNOWLEDGE SCOPE
================================================================

NGUỒN KIẾN THỨC CHÍNH DUY NHẤT:

---------------- SGK / TÀI LIỆU BÀI HỌC ----------------

{source}

---------------- KẾT THÚC NGUỒN KIẾN THỨC ----------------

QUY TẮC:

- Chỉ sử dụng kiến thức có trong nguồn trên.
- Không tự thêm kiến thức ngoài phạm vi.
- Không viết nội dung chung chung.
- Không được tạo ví dụ không có căn cứ từ nguồn.
- Không được bỏ qua các mục kiến thức quan trọng trong nguồn.

================================================================
BẮT BUỘC LẬP BẢN ĐỒ KIẾN THỨC TRƯỚC KHI SOẠN
================================================================

Trước khi viết giáo án, hãy âm thầm phân tích nguồn SGK
và xác định:

1. Tên bài học.
2. Các mục lớn.
3. Các tiểu mục.
4. Khái niệm / định nghĩa.
5. Công thức / quy tắc.
6. Thí nghiệm / quan sát.
7. Hình ảnh / bảng biểu được mô tả trong văn bản.
8. Câu hỏi hình thành kiến thức.
9. Bài tập luyện tập.
10. Nhiệm vụ vận dụng.

Sau đó phân bổ các đơn vị kiến thức này vào đúng số tiết.

KHÔNG ĐƯỢC trả về bản đồ kiến thức.
Chỉ sử dụng bản đồ đó để tạo giáo án.

================================================================
YÊU CẦU CHỐNG SOẠN SƠ SÀI
================================================================

Trong mỗi hoạt động:

NỘI DUNG phải:
- Nêu rõ học sinh học phần kiến thức nào.
- Ghi rõ câu hỏi / nhiệm vụ.
- Nêu tên thí nghiệm / quan sát nếu có.
- Nêu dữ liệu, hiện tượng hoặc vấn đề cần xử lý.

SẢN PHẨM phải:
- Có câu trả lời cụ thể.
- Có kết luận cụ thể.
- Có công thức / quy tắc nếu có.
- Có bảng kết quả nếu hoạt động yêu cầu.
- Có đáp án hoặc kết quả mong đợi.

TUYỆT ĐỐI KHÔNG dùng các câu:

- "Học sinh hoàn thành nhiệm vụ."
- "Học sinh hiểu bài."
- "Học sinh nắm được kiến thức."
- "Học sinh thảo luận nhóm."
- "Học sinh trình bày sản phẩm."

nếu không kèm nội dung cụ thể.

================================================================
TÀI LIỆU PHỤ
================================================================

PHÂN PHỐI CHƯƠNG TRÌNH:

{safe_text(noi_dung_ppct)}

{ga_block}

{ai_block}

================================================================
TÍCH HỢP
================================================================

NĂNG LỰC SỐ:

{nls}

TÍCH HỢP AI:

{
    "Có tích hợp công cụ AI hỗ trợ hoạt động nhận thức của học sinh."
    if tich_hop_ai
    else
    "Không bắt buộc."
}

GIÁO DỤC HÒA NHẬP:

{inclusion_block}

{activity_block}

================================================================
SCHEMA ĐẦU RA BẮT BUỘC
================================================================

# [TÊN BÀI HỌC]

## I. MỤC TIÊU

### 1. Về kiến thức
...

### 2. Về năng lực
...

### 3. Về phẩm chất
...

## II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU

### 1. Đối với giáo viên
...

### 2. Đối với học sinh
...

## III. TIẾN TRÌNH DẠY HỌC

### TIẾT 1

#### Hoạt động 1: Khởi động

- Mục tiêu:
- Nội dung:
- Sản phẩm:
- Tổ chức thực hiện:

  + Bước 1: Chuyển giao nhiệm vụ:
  + Bước 2: Thực hiện nhiệm vụ:
  + Bước 3: Báo cáo, thảo luận:
  + Bước 4: Kết luận, nhận định:

#### Hoạt động 2: Hình thành kiến thức mới

...

#### Hoạt động 3: Luyện tập

...

#### Hoạt động 4: Vận dụng

...

### TIẾT 2

...

### TIẾT 3

...

### TIẾT 4

...

Chỉ giữ lại số tiết thực tế của bài.

## IV. HỒ SƠ DẠY HỌC

Nếu phù hợp, bổ sung:
- Phiếu học tập.
- Câu hỏi.
- Bảng dữ liệu.
- Đáp án.
- Rubric đánh giá.

================================================================
QUY TẮC CUỐI CÙNG
================================================================

- Trả về Markdown sạch.
- Bắt đầu ngay bằng # TÊN BÀI HỌC.
- Không chào hỏi.
- Không giải thích.
- Không nói về quá trình suy luận.
- Không trả về bản đồ kiến thức.
- Không viết giáo án ngắn nếu nguồn SGK có nhiều nội dung.
- Giáo án 4 tiết phải có 4 phần TIẾT riêng biệt.
"""
