# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY
KIẾN TRÚC: KNOWLEDGE SCOPE + 5512 + MULTI-PERIOD PLANNING
============================================================

FILE:
    views/xd_khbd_data.py

MỤC TIÊU:
    1. Đọc chính xác tài liệu SGK.
    2. Không để con trỏ file bị đọc đến cuối.
    3. Phát hiện PDF scan / PDF không có text.
    4. Không gửi AI khi dữ liệu nguồn không đủ.
    5. Ép AI khai thác nội dung thực tế từ SGK.
    6. Ép phân bổ kiến thức theo đúng số tiết.
    7. Không sinh giáo án 4 tiết thành một đoạn chung chung.
============================================================
"""

import streamlit as st
import os
import re
import json
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
    "tu_dong": "Soạn mới hoàn toàn từ tài liệu SGK",
}


# ============================================================
# 2. KHUNG NĂNG LỰC SỐ
# ============================================================

KHUNG_NLS_GV = {
    "1. Miền 1: Tổ chức dạy học, giáo dục trong môi trường số": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": (
                "Sử dụng thiết bị cơ bản như máy tính, máy chiếu, "
                "bảng tương tác; sử dụng ứng dụng giáo dục đơn giản."
            ),
            "Thành thạo": (
                "Lựa chọn và tích hợp học liệu số vào kế hoạch hoạt động; "
                "thiết kế hoạt động học tập tương tác."
            ),
            "Nâng cao": (
                "Sáng tạo mô hình giáo dục ứng dụng công nghệ mới; "
                "hướng dẫn đồng nghiệp sử dụng thiết bị số."
            ),
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": (
                "Hướng dẫn học sinh thao tác cơ bản, an toàn trên thiết bị số."
            ),
            "Thành thạo": (
                "Quan sát và hỗ trợ kịp thời khi học sinh gặp khó khăn "
                "trong tương tác với công nghệ."
            ),
            "Nâng cao": (
                "Phát triển phương pháp hỗ trợ học tập trên nền tảng công nghệ "
                "tại nhà."
            ),
        },
    },
    "2. Miền 2: Kiểm tra, đánh giá": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": (
                "Sử dụng thiết bị số ghi lại sản phẩm hoặc minh chứng học tập."
            ),
            "Thành thạo": (
                "Thiết kế hoạt động đánh giá kĩ năng qua công nghệ "
                "và lưu trữ minh chứng."
            ),
        },
    },
    "6. Miền 6: Trí tuệ nhân tạo (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": (
                "Sử dụng công cụ AI tạo sinh cơ bản hỗ trợ soạn thảo "
                "và tìm kiếm ý tưởng."
            ),
            "Thành thạo": (
                "Khai thác công cụ AI chuyên biệt để tạo học liệu tương tác "
                "và cá nhân hóa."
            ),
        },
    },
}


KHUNG_NLS_HS = {
    "1. Thông tin và dữ liệu số": {
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu": {
            "Mức 1": (
                "Xác định nhu cầu thông tin và tìm kiếm dữ liệu đơn giản "
                "trong môi trường số."
            ),
            "Mức 2": (
                "Sử dụng kĩ thuật tìm kiếm nâng cao để lấy dữ liệu "
                "và thông tin chính xác."
            ),
        },
    },
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
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


def reset_ket_qua():

    st.session_state["khbd_result"] = None


def reset_toan_bo_khbd():

    keys_to_reset = {
        "khbd_result": None,
        "khbd_nls_list": [],
        "khbd_hoat_dong_list": [],
        "khbd_nls_noi_dung": "",
        "khbd_mode": "tu_dong",
        "khbd_processing": False,
    }

    for key, value in keys_to_reset.items():
        st.session_state[key] = value


def set_mode(mode: str):

    if mode not in MODE_LABELS:

        raise ValueError(
            f"Chế độ soạn không hợp lệ: {mode}"
        )

    st.session_state["khbd_mode"] = mode


# ============================================================
# 5. LÀM SẠCH VĂN BẢN
# ============================================================

def safe_text(value):

    if value is None:
        return ""

    if not isinstance(value, str):
        value = str(value)

    text = value.replace("\x00", "")

    text = re.sub(
        r"[\r\t]+",
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

    # Loại bỏ các dòng trắng quá nhiều
    text = re.sub(
        r"\n\s*\n\s*\n+",
        "\n\n",
        text,
    )

    # Chuẩn hóa khoảng trắng
    text = re.sub(
        r"[ ]{2,}",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# 6. RESET FILE POINTER
# ============================================================

def reset_file_pointer(source):

    """
    Đưa con trỏ file về đầu.

    Đây là phần rất quan trọng với:
        - Streamlit UploadedFile
        - BytesIO
        - file-like object
    """

    try:

        if hasattr(source, "seek"):
            source.seek(0)

    except Exception:

        pass


# ============================================================
# 7. ĐỌC PDF AN TOÀN
# ============================================================

def read_pdf(
    uploaded_file,
    range_str="",
):

    result = []

    try:

        reset_file_pointer(uploaded_file)

        reader = PyPDF2.PdfReader(
            uploaded_file
        )

        total_pages = len(
            reader.pages
        )

        if total_pages == 0:

            return (
                "[LỖI PDF] "
                "Tệp PDF không có trang dữ liệu."
            )

        start_page = 1
        end_page = total_pages

        if range_str and "-" in range_str:

            try:

                start_raw, end_raw = (
                    range_str.split("-", 1)
                )

                start_page = max(
                    1,
                    int(start_raw.strip()),
                )

                end_page = min(
                    total_pages,
                    int(end_raw.strip()),
                )

            except Exception:

                start_page = 1
                end_page = total_pages

        extracted_pages = 0
        total_chars = 0

        for page_index in range(
            start_page,
            end_page + 1,
        ):

            try:

                page = reader.pages[
                    page_index - 1
                ]

                raw_text = (
                    page.extract_text()
                    or ""
                )

                cleaned_text = (
                    normalize_source_text(
                        raw_text
                    )
                )

                if cleaned_text:

                    extracted_pages += 1
                    total_chars += len(
                        cleaned_text
                    )

                    result.append(
                        f"\n"
                        f"[PDF - Trang "
                        f"{page_index}]\n"
                        f"{cleaned_text}"
                    )

            except Exception as page_error:

                result.append(
                    f"\n"
                    f"[LỖI TRANG "
                    f"{page_index}: "
                    f"{page_error}]"
                )

        final_text = "\n".join(result)

        # ----------------------------------------------------
        # PDF không có text layer
        # ----------------------------------------------------

        if total_chars < 100:

            return (
                "[PDF_KHONG_CO_TEXT]\n"
                f"Tổng số trang: {total_pages}\n"
                f"Số trang đọc được: "
                f"{extracted_pages}\n"
                f"Số ký tự trích xuất: "
                f"{total_chars}\n\n"
                "PDF có thể là bản scan hình ảnh "
                "hoặc không có lớp văn bản."
            )

        return final_text

    except Exception as error:

        return (
            "[LỖI ĐỌC PDF]\n"
            f"{str(error)}"
        )


# ============================================================
# 8. ĐỌC DOCX
# ============================================================

def read_docx_ordered(source):

    result = []

    try:

        if isinstance(
            source,
            (str, Path),
        ):

            document = Document(
                source
            )

        elif hasattr(source, "read"):

            reset_file_pointer(source)

            content = source.read()

            if isinstance(
                content,
                str,
            ):

                content = content.encode(
                    "utf-8"
                )

            document = Document(
                BytesIO(content)
            )

        else:

            document = Document(
                source
            )

        for element in (
            document.element.body
        ):

            tag = element.tag

            if (
                tag.endswith("}p")
                or tag.endswith("p")
            ):

                from docx.text.paragraph import (
                    Paragraph,
                )

                paragraph = Paragraph(
                    element,
                    document,
                )

                text = normalize_source_text(
                    paragraph.text
                )

                if text:

                    result.append(
                        text
                    )

            elif (
                tag.endswith("}tbl")
                or tag.endswith("tbl")
            ):

                from docx.table import Table

                table = Table(
                    element,
                    document,
                )

                result.append(
                    "\n[BẢNG DỮ LIỆU]"
                )

                for row in table.rows:

                    cells = []

                    for cell in row.cells:

                        cell_text = (
                            normalize_source_text(
                                cell.text
                            )
                        )

                        cells.append(
                            cell_text
                        )

                    row_text = (
                        " | ".join(
                            cells
                        )
                    )

                    if row_text.strip():

                        result.append(
                            row_text
                        )

        final_text = "\n".join(
            result
        )

        return final_text.strip()

    except Exception as error:

        return (
            "[LỖI ĐỌC DOCX]\n"
            f"{str(error)}"
        )


# ============================================================
# 9. ĐỌC EXCEL
# ============================================================

def read_excel_structured(
    uploaded_file,
):

    result = []

    try:

        reset_file_pointer(
            uploaded_file
        )

        sheets = pd.read_excel(
            uploaded_file,
            sheet_name=None,
        )

        for sheet_name, dataframe in (
            sheets.items()
        ):

            result.append(
                f"\n"
                f"[SHEET: "
                f"{sheet_name}]"
            )

            dataframe = (
                dataframe.fillna("")
            )

            records = dataframe.to_dict(
                orient="records"
            )

            for index, record in enumerate(
                records,
                start=1,
            ):

                clean_record = {}

                for key, value in (
                    record.items()
                ):

                    value_text = safe_text(
                        value
                    )

                    if value_text:

                        clean_record[
                            str(key).strip()
                        ] = value_text

                if clean_record:

                    result.append(
                        f"Dòng {index}: "
                        + json.dumps(
                            clean_record,
                            ensure_ascii=False,
                        )
                    )

        return "\n".join(
            result
        ).strip()

    except Exception as error:

        return (
            "[LỖI ĐỌC EXCEL]\n"
            f"{str(error)}"
        )


# ============================================================
# 10. ĐỌC FILE TỔNG QUÁT
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
        "file",
    )

    extension = (
        Path(filename)
        .suffix
        .lower()
    )

    try:

        if extension == ".pdf":

            return read_pdf(
                uploaded_file,
                range_str
                if is_pdf_target
                else "",
            )

        if extension == ".docx":

            return read_docx_ordered(
                uploaded_file
            )

        if extension in (
            ".xlsx",
            ".xls",
        ):

            return read_excel_structured(
                uploaded_file
            )

        return (
            "[ĐỊNH DẠNG KHÔNG ĐƯỢC HỖ TRỢ]"
        )

    except Exception as error:

        return (
            "[LỖI ĐỌC FILE]\n"
            f"{str(error)}"
        )


# ============================================================
# 11. ĐỌC NHIỀU FILE
# ============================================================

def read_multiple_files(
    files,
    range_str="",
    is_pdf_target=False,
):

    result = []

    for uploaded_file in files or []:

        filename = getattr(
            uploaded_file,
            "name",
            "Tài liệu",
        )

        content = read_uploaded_file(
            uploaded_file,
            range_str,
            is_pdf_target,
        )

        result.append(
            "\n"
            "==================================================\n"
            f"TÀI LIỆU NGUỒN: {filename}\n"
            "==================================================\n"
        )

        result.append(
            content
        )

    return "\n".join(
        result
    ).strip()


# ============================================================
# 12. ĐỌC MẪU KHBD
# ============================================================

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
# 13. PHÂN TÍCH CHẤT LƯỢNG NGUỒN
# ============================================================

def analyze_source_quality(
    source_text,
):

    text = safe_text(
        source_text
    )

    char_count = len(
        text
    )

    words = re.findall(
        r"\S+",
        text,
    )

    word_count = len(
        words
    )

    has_pdf_error = (
        "[PDF_KHONG_CO_TEXT]"
        in text
    )

    has_read_error = (
        "[LỖI ĐỌC"
        in text
    )

    if has_pdf_error:

        return {
            "valid": False,
            "status": "PDF_SCAN",
            "characters": char_count,
            "words": word_count,
            "message": (
                "PDF không có lớp văn bản. "
                "Cần OCR hoặc tải PDF có text."
            ),
        }

    if has_read_error:

        return {
            "valid": False,
            "status": "READ_ERROR",
            "characters": char_count,
            "words": word_count,
            "message": (
                "Có lỗi trong quá trình đọc tài liệu."
            ),
        }

    if char_count < 300:

        return {
            "valid": False,
            "status": "TOO_SHORT",
            "characters": char_count,
            "words": word_count,
            "message": (
                "Nội dung tài liệu nguồn quá ngắn."
            ),
        }

    return {
        "valid": True,
        "status": "OK",
        "characters": char_count,
        "words": word_count,
        "message": (
            "Nguồn dữ liệu đủ điều kiện xử lý."
        ),
    }


# ============================================================
# 14. TẠO KNOWLEDGE SCOPE
# ============================================================

def build_knowledge_scope(
    source_text,
):

    quality = analyze_source_quality(
        source_text
    )

    if not quality["valid"]:

        raise ValueError(
            "Tài liệu nguồn không đủ dữ liệu "
            "để xây dựng giáo án.\n\n"
            f"{quality['message']}\n\n"
            f"Số ký tự đọc được: "
            f"{quality['characters']}\n"
            f"Số từ đọc được: "
            f"{quality['words']}"
        )

    text = normalize_source_text(
        source_text
    )

    return f"""
============================================================
KNOWLEDGE SCOPE - PHẠM VI KIẾN THỨC ĐƯỢC PHÉP SỬ DỤNG
============================================================

Số ký tự nguồn: {quality["characters"]}
Số từ nguồn: {quality["words"]}

QUY TẮC TUYỆT ĐỐI:

1. Chỉ sử dụng kiến thức có trong tài liệu nguồn.
2. Không tự bịa thêm khái niệm ngoài tài liệu.
3. Không được viết hoạt động chung chung.
4. Mọi hoạt động phải gắn với một nội dung cụ thể.
5. Mọi câu hỏi phải có nguồn từ nội dung được cung cấp.
6. Mọi sản phẩm phải thể hiện kết quả học tập cụ thể.
7. Nếu tài liệu không có dữ liệu để trả lời, phải ghi:
   "Tài liệu nguồn chưa cung cấp thông tin này."
8. Không được tự lấy kiến thức ngoài SGK để lấp chỗ trống.

============================================================
TOÀN BỘ NỘI DUNG NGUỒN
============================================================

{text}

============================================================
KẾT THÚC KNOWLEDGE SCOPE
============================================================
"""


# ============================================================
# 15. CALLBACKS NĂNG LỰC SỐ
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

    if (
        item
        not in st.session_state.khbd_nls_list
    ):

        st.session_state.khbd_nls_list.append(
            item
        )


def format_nls():

    items = (
        st.session_state.khbd_nls_list
    )

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

    st.session_state[
        "khbd_new_activity"
    ] = ""


# ============================================================
# 16. TASK CONFIG
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
            ) as file:

                content = file.read()

                if content.strip():

                    return content.strip()

        except Exception:

            pass

    return (
        "BẠN LÀ CHUYÊN GIA XÂY DỰNG "
        "KẾ HOẠCH BÀI DẠY THEO PHỤ LỤC 4 "
        "CÔNG VĂN 5512."
    )


# ============================================================
# 17. CHUẨN HÓA KẾT QUẢ AI
# ============================================================

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

        # OpenAI / OpenRouter
        try:

            choices = result.get(
                "choices",
                [],
            )

            if choices:

                message = (
                    choices[0]
                    .get(
                        "message",
                        {}
                    )
                )

                content = (
                    message
                    .get(
                        "content",
                        ""
                    )
                )

                if content:

                    return str(
                        content
                    ).strip()

        except Exception:

            pass

        # Gemini
        try:

            candidates = result.get(
                "candidates",
                [],
            )

            if candidates:

                content = (
                    candidates[0]
                    .get(
                        "content",
                        {}
                    )
                )

                parts = (
                    content
                    .get(
                        "parts",
                        []
                    )
                )

                texts = []

                for part in parts:

                    if (
                        isinstance(
                            part,
                            dict,
                        )
                        and "text"
                        in part
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

        # Các cấu trúc thông dụng
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
                        and "text"
                        in item
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


# ============================================================
# 18. GỌI AI
# ============================================================

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

        result = (
            ai_engine.generate_text(
                prompt
            )
        )

        return normalize_ai_result(
            result
        )

    if hasattr(
        ai_engine,
        "generate",
    ):

        result = (
            ai_engine.generate(
                prompt
            )
        )

        return normalize_ai_result(
            result
        )

    raise RuntimeError(
        "AI Engine không phản hồi."
    )


# ============================================================
# 19. VALIDATE KẾT QUẢ
# ============================================================

def validate_khbd_result(
    text,
):

    if not text:

        return (
            False,
            "AI trả về nội dung rỗng."
        )

    text = text.strip()

    if len(text) < 1000:

        return (
            False,
            (
                "Giáo án AI sinh quá ngắn "
                f"({len(text)} ký tự). "
                "Không đạt yêu cầu giáo án chi tiết."
            ),
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

    return (
        True,
        "Giáo án hợp lệ."
    )


# ============================================================
# 20. PHÂN TÍCH SỐ TIẾT
# ============================================================

def extract_lesson_count(
    thong_tin,
):

    text = safe_text(
        thong_tin
    ).lower()

    patterns = [

        r"(\d+)\s*tiết",

        r"(\d+)\s*tiet",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
        )

        if match:

            return max(
                1,
                int(
                    match.group(
                        1
                    )
                ),
            )

    return 1


# ============================================================
# 21. TẠO BẢN ĐỒ PHÂN BỔ KIẾN THỨC
# ============================================================

def build_period_plan(
    thong_tin,
):

    lesson_count = (
        extract_lesson_count(
            thong_tin
        )
    )

    lines = []

    lines.append(
        f"SỐ TIẾT BẮT BUỘC: "
        f"{lesson_count}"
    )

    lines.append(
        "Mỗi tiết phải có nội dung "
        "kiến thức cụ thể từ SGK."
    )

    lines.append(
        "Không được gom toàn bộ bài học "
        "vào một hoạt động chung."
    )

    for index in range(
        1,
        lesson_count + 1,
    ):

        lines.append(
            f"""
TIẾT {index}:
- Phải có nội dung kiến thức cụ thể.
- Phải có hoạt động học tập cụ thể.
- Phải có sản phẩm học tập cụ thể.
- Phải có câu hỏi hoặc nhiệm vụ cụ thể.
- Phải thể hiện sự phát triển kiến thức từ tiết trước.
"""
        )

    return "\n".join(
        lines
    )


# ============================================================
# 22. BUILD PROMPT CHÍNH
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

    # --------------------------------------------------------
    # KIỂM TRA NGUỒN TRƯỚC KHI GỌI AI
    # --------------------------------------------------------

    source_quality = (
        analyze_source_quality(
            noi_dung_chinh
        )
    )

    if not source_quality["valid"]:

        raise ValueError(
            "Tài liệu nguồn không đủ dữ liệu "
            "để xây dựng giáo án.\n\n"
            f"{source_quality['message']}\n"
            f"Số ký tự: "
            f"{source_quality['characters']}\n"
            f"Số từ: "
            f"{source_quality['words']}"
        )

    # --------------------------------------------------------
    # THÔNG TIN
    # --------------------------------------------------------

    mode_text = (
        MODE_LABELS[mode]
    )

    task_config = (
        load_task_config()
    )

    lesson_plan = (
        build_period_plan(
            thong_tin
        )
    )

    safe_ai = safe_text(
        noi_dung_ai
    )

    safe_need = safe_text(
        nhu_cau_hoa_nhap
    )

    safe_activity = safe_text(
        hoat_dong
    )

    # --------------------------------------------------------
    # GIÁO ÁN GỐC
    # --------------------------------------------------------

    ga_block = ""

    if (
        mode == "chinh_sua"
        and safe_text(
            noi_dung_ga
        )
    ):

        ga_block = f"""

============================================================
GIÁO ÁN GỐC
============================================================

{noi_dung_ga}

============================================================
HẾT GIÁO ÁN GỐC
============================================================
"""

    # --------------------------------------------------------
    # TÍCH HỢP
    # --------------------------------------------------------

    ai_block = ""

    if safe_ai:

        ai_block = f"""

TÀI LIỆU / HƯỚNG DẪN AI BỔ SUNG:

{safe_ai}
"""

    if (
        tich_hop_hoa_nhap
        and safe_need
    ):

        inclusion_block = f"""

GIÁO DỤC HÒA NHẬP:

{safe_need}

Bắt buộc thiết kế phương án hỗ trợ trực tiếp
trong từng hoạt động phù hợp.
"""

    else:

        inclusion_block = (
            "Không có yêu cầu giáo dục hòa nhập đặc biệt."
        )

    activity_block = ""

    if safe_activity:

        activity_block = f"""

HOẠT ĐỘNG BỔ SUNG THEO YÊU CẦU GIÁO VIÊN:

{safe_activity}
"""

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    return f"""

{task_config}

============================================================
VAI TRÒ
============================================================

Bạn là chuyên gia cao cấp xây dựng Kế hoạch bài dạy
môn Khoa học tự nhiên theo Chương trình GDPT 2018
và Phụ lục 4 Công văn 5512.

============================================================
THÔNG TIN NHIỆM VỤ
============================================================

Chế độ:
{mode_text}

Thông tin bài học:
{thong_tin}

============================================================
KẾ HOẠCH PHÂN BỔ SỐ TIẾT
============================================================

{lesson_plan}

============================================================
NGUYÊN TẮC CHỐNG SOẠN CHUNG CHUNG
============================================================

ĐÂY LÀ YÊU CẦU BẮT BUỘC.

1. Không được viết giáo án ngắn chung chung.

2. Không được gom nội dung của nhiều tiết
   vào một đoạn văn duy nhất.

3. Nếu bài có 4 tiết thì phải thể hiện rõ:

   TIẾT 1
   TIẾT 2
   TIẾT 3
   TIẾT 4

4. Mỗi tiết phải có:

   - Nội dung kiến thức cụ thể.
   - Câu hỏi hoặc nhiệm vụ cụ thể.
   - Hoạt động học tập cụ thể.
   - Sản phẩm học tập cụ thể.
   - Kết luận kiến thức cụ thể.

5. Mỗi nội dung trong mục "Nội dung"
   phải truy xuất từ tài liệu SGK.

6. Không được sử dụng câu:

   "Học sinh hoàn thành nhiệm vụ."

   nếu không mô tả rõ nhiệm vụ là gì.

7. Không được sử dụng câu:

   "Học sinh hiểu bài."

   nếu không nêu rõ học sinh hiểu kiến thức nào.

8. Không được tự bịa kiến thức ngoài SGK.

9. Không được dùng kiến thức bên ngoài
   để lấp khoảng trống của tài liệu nguồn.

10. Nếu thông tin không có trong SGK,
    phải ghi rõ:

    "Tài liệu nguồn chưa cung cấp thông tin này."

============================================================
KNOWLEDGE SCOPE
============================================================

{build_knowledge_scope(noi_dung_chinh)}

============================================================
GIÁO ÁN GỐC
============================================================

{ga_block}

============================================================
PHÂN PHỐI CHƯƠNG TRÌNH
============================================================

{noi_dung_ppct}

============================================================
TÍCH HỢP
============================================================

Năng lực số:

{nls}

Tích hợp AI:

{
    "Có tích hợp AI hỗ trợ hoạt động nhận thức của học sinh."
    if tich_hop_ai
    else
    "Không bắt buộc tích hợp AI."
}

Giáo dục hòa nhập:

{inclusion_block}

{ai_block}

{activity_block}

============================================================
CẤU TRÚC ĐẦU RA BẮT BUỘC
============================================================

# [TÊN BÀI HỌC]

## I. MỤC TIÊU

### 1. Về kiến thức

Phải nêu các kiến thức cụ thể
được hình thành từ SGK.

### 2. Về năng lực

Phải gắn với hoạt động học tập thực tế.

### 3. Về phẩm chất

Phải phù hợp với nội dung bài học.

============================================================

## II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU

### 1. Đối với giáo viên

### 2. Đối với học sinh

============================================================

## III. TIẾN TRÌNH DẠY HỌC

"""

    + "\n".join(
        [
            f"""
============================================================
### TIẾT {index}
============================================================

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

- Mục tiêu:
- Nội dung:
- Sản phẩm:
- Tổ chức thực hiện:

  + Bước 1: Chuyển giao nhiệm vụ:
  + Bước 2: Thực hiện nhiệm vụ:
  + Bước 3: Báo cáo, thảo luận:
  + Bước 4: Kết luận, nhận định:

#### Hoạt động 3: Luyện tập

- Mục tiêu:
- Nội dung:
- Sản phẩm:
- Tổ chức thực hiện:

  + Bước 1: Chuyển giao nhiệm vụ:
  + Bước 2: Thực hiện nhiệm vụ:
  + Bước 3: Báo cáo, thảo luận:
  + Bước 4: Kết luận, nhận định:

#### Hoạt động 4: Vận dụng

- Mục tiêu:
- Nội dung:
- Sản phẩm:
- Tổ chức thực hiện:

  + Bước 1: Chuyển giao nhiệm vụ:
  + Bước 2: Thực hiện nhiệm vụ:
  + Bước 3: Báo cáo, thảo luận:
  + Bước 4: Kết luận, nhận định:
"""
            for index in range(
                1,
                extract_lesson_count(
                    thong_tin
                )
                + 1,
            )
        ]
    )

    + f"""

============================================================
MẪU KHBD THAM KHẢO
============================================================

{noi_dung_mau}

============================================================
YÊU CẦU CUỐI CÙNG
============================================================

Trả về trực tiếp giáo án hoàn chỉnh bằng Markdown.

Không chào hỏi.

Không giải thích.

Không viết ngoài giáo án.

Bắt đầu ngay bằng:

# [TÊN BÀI HỌC]

Giáo án phải đủ chi tiết để giáo viên có thể
sử dụng làm cơ sở tổ chức dạy học thực tế.
"""
