# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY
KIẾN TRÚC: SOURCE VALIDATION
        → KNOWLEDGE SCOPE
        → PERIOD PLANNING
        → AI GENERATION
        → OUTPUT VALIDATION

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


# ============================================================
# 2. KHUNG NĂNG LỰC SỐ
# ============================================================

KHUNG_NLS_GV = {
    "1. Miền 1: Tổ chức dạy học, giáo dục trong môi trường số": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": (
                "Sử dụng thiết bị cơ bản như máy tính, máy chiếu, bảng tương tác; "
                "sử dụng ứng dụng giáo dục đơn giản."
            ),
            "Thành thạo": (
                "Lựa chọn và tích hợp học liệu số vào kế hoạch hoạt động; "
                "thiết kế hoạt động học tập tương tác."
            ),
            "Nâng cao": (
                "Sáng tạo mô hình giáo dục ứng dụng công nghệ mới; "
                "hướng dẫn đồng nghiệp sử dụng thiết bị số."
            )
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
                "Phát triển phương pháp hỗ trợ học tập trên nền tảng công nghệ "
                "tại nhà."
            )
        }
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
            )
        }
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
                "Sử dụng kĩ thuật tìm kiếm nâng cao để lấy dữ liệu "
                "và thông tin chính xác."
            )
        }
    }
}


# ============================================================
# 3. API NĂNG LỰC SỐ
# ============================================================

def get_nls_framework(loai_khung):
    """
    Trả về khung năng lực số tương ứng.
    """

    if loai_khung == "Giáo viên (Thông tư 18)":
        return KHUNG_NLS_GV

    return KHUNG_NLS_HS


def get_nls_domains(loai_khung):
    return list(get_nls_framework(loai_khung).keys())


def get_nls_components(loai_khung, linh_vuc):
    framework = get_nls_framework(loai_khung)

    if linh_vuc in framework:
        return list(framework[linh_vuc].keys())

    return []


def get_nls_levels(loai_khung, linh_vuc, thanh_phan):
    framework = get_nls_framework(loai_khung)

    if (
        linh_vuc in framework
        and thanh_phan in framework[linh_vuc]
    ):
        return list(framework[linh_vuc][thanh_phan].keys())

    return []


def get_nls_content(
    loai_khung,
    linh_vuc,
    thanh_phan,
    muc_do
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

        # Dữ liệu kiểm tra nguồn
        "khbd_source_report": None,

        # Bản đồ kiến thức
        "khbd_knowledge_scope": None,

        # Kế hoạch phân bổ tiết
        "khbd_period_plan": None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


def reset_ket_qua():

    st.session_state["khbd_result"] = None


def reset_toan_bo_khbd():

    keys_to_reset = [
        "khbd_result",
        "khbd_source_report",
        "khbd_knowledge_scope",
        "khbd_period_plan",
    ]

    for key in keys_to_reset:

        st.session_state[key] = None


    st.session_state["khbd_nls_list"] = []

    st.session_state["khbd_hoat_dong_list"] = []

    st.session_state["khbd_nls_noi_dung"] = ""

    st.session_state["khbd_mode"] = "tu_dong"

    st.session_state["khbd_processing"] = False


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


    if not isinstance(value, str):

        value = str(value)


    text = value.replace("\x00", "")

    text = text.replace("\ufeff", "")

    text = text.replace("\u200b", "")

    text = re.sub(
        r"[\r\t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def normalize_source_text(text):

    text = safe_text(text)

    # Chuẩn hóa khoảng trắng
    text = re.sub(
        r"[ ]{2,}",
        " ",
        text
    )

    # Chuẩn hóa dòng
    text = re.sub(
        r"\n[ ]+",
        "\n",
        text
    )

    return text.strip()


# ============================================================
# 6. ĐỌC PDF
# ============================================================

def _reset_file_pointer(uploaded_file):

    try:

        uploaded_file.seek(0)

    except Exception:

        pass


def parse_page_range(range_str, total_pages):

    start = 1

    end = total_pages


    if not range_str:

        return start, end


    if "-" not in str(range_str):

        return start, end


    try:

        s, e = str(range_str).split("-", 1)

        start = max(
            1,
            int(s.strip())
        )

        end = min(
            total_pages,
            int(e.strip())
        )

    except Exception:

        start = 1

        end = total_pages


    if start > end:

        start, end = end, start


    return start, end


def read_pdf(uploaded_file, range_str=""):

    result = []


    try:

        _reset_file_pointer(uploaded_file)

        reader = PyPDF2.PdfReader(uploaded_file)

        total_pages = len(reader.pages)


        if total_pages == 0:

            return ""


        start, end = parse_page_range(
            range_str,
            total_pages
        )


        for index in range(start, end + 1):

            page = reader.pages[index - 1]

            text = page.extract_text() or ""

            text = normalize_source_text(text)


            if text:

                result.append(
                    f"\n[PDF - TRANG {index}]\n{text}"
                )


    except Exception as e:

        result.append(
            f"[LỖI ĐỌC PDF: {str(e)}]"
        )


    return "\n".join(result).strip()


# ============================================================
# 7. ĐỌC DOCX THEO ĐÚNG THỨ TỰ DOM
# ============================================================

def read_docx_ordered(source):

    result = []


    try:

        if isinstance(source, (str, Path)):

            document = Document(source)


        elif hasattr(source, "read"):

            _reset_file_pointer(source)

            content = source.read()


            if isinstance(content, str):

                content = content.encode(
                    "utf-8"
                )


            document = Document(
                BytesIO(content)
            )


        else:

            document = Document(source)


        for element in document.element.body:


            tag = element.tag


            if tag.endswith("}p") or tag.endswith("p"):

                from docx.text.paragraph import Paragraph

                paragraph = Paragraph(
                    element,
                    document
                )


                text = normalize_source_text(
                    paragraph.text
                )


                if text:

                    result.append(text)


            elif tag.endswith("}tbl") or tag.endswith("tbl"):

                from docx.table import Table

                table = Table(
                    element,
                    document
                )


                result.append(
                    "\n[BẢNG DỮ LIỆU]"
                )


                for row in table.rows:

                    cells = []


                    for cell in row.cells:

                        cell_text = normalize_source_text(
                            cell.text
                        )

                        cell_text = cell_text.replace(
                            "\n",
                            " "
                        )

                        cells.append(cell_text)


                    row_text = " | ".join(cells)


                    if row_text.strip():

                        result.append(row_text)


    except Exception as e:

        result.append(
            f"[LỖI ĐỌC DOCX: {str(e)}]"
        )


    return "\n".join(result).strip()


# ============================================================
# 8. ĐỌC EXCEL
# ============================================================

def read_excel_structured(uploaded_file):

    result = []


    try:

        _reset_file_pointer(uploaded_file)

        sheets = pd.read_excel(
            uploaded_file,
            sheet_name=None
        )


        for sheet_name, dataframe in sheets.items():

            result.append(
                f"\n[PHÂN PHỐI CHƯƠNG TRÌNH - SHEET: {sheet_name}]"
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

                    key_text = safe_text(key)

                    value_text = safe_text(value)


                    if value_text:

                        clean_record[
                            key_text
                        ] = value_text


                if clean_record:

                    result.append(
                        f"Dòng {index}: "
                        + json.dumps(
                            clean_record,
                            ensure_ascii=False
                        )
                    )


    except Exception as e:

        result.append(
            f"[LỖI ĐỌC EXCEL: {str(e)}]"
        )


    return "\n".join(result).strip()


# ============================================================
# 9. ĐỌC FILE TỔNG QUÁT
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
        "file.docx"
    )


    extension = Path(
        filename.lower()
    ).suffix


    try:

        if extension == ".pdf":

            return read_pdf(
                uploaded_file,
                range_str if is_pdf_target else ""
            )


        if extension == ".docx":

            return read_docx_ordered(
                uploaded_file
            )


        if extension in [".xlsx", ".xls"]:

            return read_excel_structured(
                uploaded_file
            )


        return ""


    except Exception as e:

        return (
            f"[LỖI ĐỌC FILE: {str(e)}]"
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


        content = read_uploaded_file(
            uploaded_file,
            range_str,
            is_pdf_target
        )


        result.append(
            f"\n--- TÀI LIỆU NGUỒN: {filename} ---\n"
        )

        result.append(content)


    return "\n".join(result).strip()


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
# 10. KIỂM TRA CHẤT LƯỢNG NGUỒN SGK
# ============================================================

def analyze_source_text(text):

    """
    Phân tích sơ bộ dữ liệu nguồn trước khi gọi AI.

    Mục đích:
    - Phát hiện file rỗng.
    - Phát hiện PDF scan không có lớp text.
    - Phát hiện lỗi đọc file.
    - Đếm các đơn vị kiến thức có thể khai thác.
    """

    text = normalize_source_text(text)

    report = {
        "valid": False,
        "length": len(text),
        "word_count": len(text.split()),
        "line_count": len(text.splitlines()),
        "headings": [],
        "questions": [],
        "activities": [],
        "examples": [],
        "formulas": [],
        "errors": [],
        "warning": "",
    }


    if not text:

        report["warning"] = (
            "Không đọc được nội dung tài liệu nguồn."
        )

        return report


    if "[LỖI ĐỌC" in text.upper():

        report["errors"] = re.findall(
            r"\[LỖI ĐỌC[^\]]*\]",
            text,
            flags=re.IGNORECASE
        )


    if len(text) < 300:

        report["warning"] = (
            "Nội dung tài liệu nguồn quá ngắn. "
            "Có thể file PDF là bản scan hoặc chưa được đọc đầy đủ."
        )


    # Heading / tiêu đề
    heading_patterns = [
        r"(?im)^(?:Bài|Chủ đề|Chương|Phần)\s+.+$",
        r"(?im)^(?:[IVX]+\.|\d+\.)\s+.+$",
        r"(?im)^#+\s+.+$",
    ]


    for pattern in heading_patterns:

        report["headings"].extend(
            re.findall(
                pattern,
                text
            )
        )


    # Câu hỏi
    question_lines = re.findall(
        r"(?im)^.*(?:\?|？|Hãy|Em hãy|Quan sát|Thảo luận|Trả lời).*$",
        text
    )


    report["questions"] = [
        safe_text(item)
        for item in question_lines
        if safe_text(item)
    ]


    # Hoạt động / thí nghiệm / thực hành
    activity_patterns = [
        r"(?im)^.*(?:Thí nghiệm|Thực hành|Hoạt động|Luyện tập|Vận dụng|Khám phá).*$",
        r"(?im)^.*(?:Tiến hành|Quan sát|Đo|Tính|Xác định|Nhận xét).*$",
    ]


    for pattern in activity_patterns:

        report["activities"].extend(
            re.findall(
                pattern,
                text
            )
        )


    # Ví dụ
    report["examples"] = re.findall(
        r"(?im)^.*(?:Ví dụ|Ví dụ:|Bài tập).*$",
        text
    )


    # Công thức
    report["formulas"] = re.findall(
        r"(?m)^.*(?:=|≈|≤|≥|→|⇔).*$",
        text
    )


    # Loại trùng
    for key in [
        "headings",
        "questions",
        "activities",
        "examples",
        "formulas"
    ]:

        report[key] = list(
            dict.fromkeys(
                safe_text(item)
                for item in report[key]
                if safe_text(item)
            )
        )


    # Nguồn được xem là tạm đủ
    if (
        len(text) >= 300
        and not report["errors"]
    ):

        report["valid"] = True


    return report


# ============================================================
# 11. XÂY DỰNG KNOWLEDGE SCOPE CÓ CẤU TRÚC
# ============================================================

def build_knowledge_scope(
    noi_dung_chinh,
    max_source_chars=90000
):

    """
    Không chỉ ném toàn bộ SGK dạng text vào AI.

    Tạo một Knowledge Scope có:
    1. Toàn văn nguồn.
    2. Danh mục tiêu đề.
    3. Câu hỏi thực tế.
    4. Hoạt động / thí nghiệm.
    5. Ví dụ / bài tập.
    6. Công thức / biểu thức.

    Đây là lớp trung gian giúp AI nhìn thấy
    cấu trúc nội dung thay vì một khối text vô định.
    """

    source = normalize_source_text(
        noi_dung_chinh
    )


    if not source:

        raise ValueError(
            "Không có nội dung SGK/tài liệu nguồn."
        )


    report = analyze_source_text(
        source
    )


    if not report["valid"]:

        raise ValueError(
            "Tài liệu nguồn không đủ dữ liệu để xây dựng giáo án.\n"
            + report["warning"]
        )


    # Tránh prompt vượt quá khả năng context
    source_for_ai = source[:max_source_chars]


    scope = {
        "source_text": source_for_ai,
        "source_report": report,
        "headings": report["headings"],
        "questions": report["questions"],
        "activities": report["activities"],
        "examples": report["examples"],
        "formulas": report["formulas"],
    }


    return scope


def format_knowledge_scope(scope):

    report = scope.get(
        "source_report",
        {}
    )


    def numbered(items):

        if not items:

            return "Không phát hiện rõ."


        return "\n".join(
            f"{index}. {item}"
            for index, item in enumerate(
                items,
                start=1
            )
        )


    return f"""
================ KNOWLEDGE SCOPE =================

[THỐNG KÊ NGUỒN]
- Số ký tự: {report.get("length", 0)}
- Số từ: {report.get("word_count", 0)}
- Số dòng: {report.get("line_count", 0)}

[TIÊU ĐỀ / ĐƠN VỊ KIẾN THỨC]
{numbered(scope.get("headings", []))}

[CÂU HỎI / YÊU CẦU TRONG SGK]
{numbered(scope.get("questions", []))}

[HOẠT ĐỘNG / THÍ NGHIỆM / THỰC HÀNH]
{numbered(scope.get("activities", []))}

[VÍ DỤ / BÀI TẬP]
{numbered(scope.get("examples", []))}

[CÔNG THỨC / BIỂU THỨC]
{numbered(scope.get("formulas", []))}

[TOÀN VĂN NGUỒN]
{scope.get("source_text", "")}

================ END KNOWLEDGE SCOPE ==============
""".strip()


# ============================================================
# 12. PHÂN TÍCH SỐ TIẾT
# ============================================================

def extract_period_count(thong_tin):

    """
    Tìm số tiết từ thông tin bài học.

    Hỗ trợ:
    - 4 tiết
    - 4 tiết (2 tiết lý thuyết + ...)
    - Số tiết: 4
    - 4 tiết học
    """

    text = safe_text(
        thong_tin
    )


    patterns = [
        r"(\d+)\s*tiết",
        r"số tiết\s*[:\-]?\s*(\d+)",
        r"(\d+)\s*tiết học",
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )


        if match:

            try:

                value = int(
                    match.group(1)
                )


                if 1 <= value <= 50:

                    return value


            except Exception:

                pass


    return 1


def build_period_plan(
    thong_tin,
    knowledge_scope
):

    """
    Tạo bản đồ phân bổ tiết trước khi AI sinh nội dung.

    Đây là điểm sửa quan trọng nhất.

    AI không còn nhận:
        "Bài X - 4 tiết"

    mà nhận:

        TIẾT 1
        TIẾT 2
        TIẾT 3
        TIẾT 4

    và phải gắn nội dung SGK vào từng tiết.
    """

    period_count = extract_period_count(
        thong_tin
    )


    headings = knowledge_scope.get(
        "headings",
        []
    )

    activities = knowledge_scope.get(
        "activities",
        []
    )

    questions = knowledge_scope.get(
        "questions",
        []
    )

    examples = knowledge_scope.get(
        "examples",
        []
    )


    # Tập các đơn vị kiến thức
    knowledge_units = []


    for item in headings:

        knowledge_units.append(
            item
        )


    for item in activities:

        if item not in knowledge_units:

            knowledge_units.append(
                item
            )


    for item in questions:

        if item not in knowledge_units:

            knowledge_units.append(
                item
            )


    for item in examples:

        if item not in knowledge_units:

            knowledge_units.append(
                item
            )


    # Chia đều các đơn vị kiến thức
    # chỉ để tạo khung định hướng,
    # không phải AI được phép bỏ qua nội dung.
    chunks = [
        []
        for _ in range(period_count)
    ]


    if knowledge_units:

        for index, item in enumerate(
            knowledge_units
        ):

            target = index % period_count

            chunks[target].append(
                item
            )


    periods = []


    for index in range(period_count):

        periods.append({

            "period": index + 1,

            "title": (
                f"TIẾT {index + 1}"
            ),

            "source_anchors": chunks[index],

        })


    return {

        "period_count": period_count,

        "periods": periods,

        "knowledge_units": knowledge_units,

    }


def format_period_plan(period_plan):

    lines = []


    lines.append(
        "================ PHÂN BỔ BẮT BUỘC THEO TIẾT ================"
    )


    lines.append(
        f"SỐ TIẾT BẮT BUỘC: {period_plan['period_count']}"
    )


    for period in period_plan["periods"]:

        lines.append(
            f"\n### TIẾT {period['period']}"
        )


        anchors = period.get(
            "source_anchors",
            []
        )


        if anchors:

            for item in anchors:

                lines.append(
                    f"- Nội dung SGK cần xử lý: {item}"
                )

        else:

            lines.append(
                "- Phải tiếp tục khai thác trực tiếp nội dung SGK."
            )


    lines.append(
        "\n================ END PHÂN BỔ THEO TIẾT ================"
    )


    return "\n".join(lines)


# ============================================================
# 13. CALLBACKS
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


    if (
        st.session_state.get(
            "khbd_loai_khung_nls"
        )
        == "Giáo viên (Thông tư 18)"
    ):

        van_ban = NLS_GV_VAN_BAN_MAC_DINH

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
        start=1
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
# 14. TASK CONFIG
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


    return """
BẠN LÀ CHUYÊN GIA THIẾT KẾ KẾ HOẠCH BÀI DẠY
KHOA HỌC TỰ NHIÊN THEO CHƯƠNG TRÌNH GDPT 2018
VÀ CẤU TRÚC PHỤ LỤC 4 CÔNG VĂN 5512.

ƯU TIÊN:
1. Trung thành với tài liệu nguồn.
2. Không bịa kiến thức.
3. Phân bổ đúng số tiết.
4. Mỗi tiết phải có nội dung và sản phẩm cụ thể.
5. Giáo án phải đủ chi tiết để giáo viên có thể sử dụng trực tiếp.
""".strip()


# ============================================================
# 15. CHUẨN HÓA KẾT QUẢ AI
# ============================================================

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
                    ) and part.get("text"):

                        texts.append(
                            str(
                                part["text"]
                            )
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

                    if (
                        isinstance(
                            item,
                            dict
                        )
                        and item.get("text")
                    ):

                        texts.append(
                            str(
                                item["text"]
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
# 16. GỌI AI
# ============================================================

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

        result = ai_engine.generate_text(
            prompt
        )


        return normalize_ai_result(
            result
        )


    if hasattr(
        ai_engine,
        "generate"
    ):

        result = ai_engine.generate(
            prompt
        )


        return normalize_ai_result(
            result
        )


    raise RuntimeError(
        "AI Engine không phản hồi."
    )


# ============================================================
# 17. VALIDATOR CHUYÊN SÂU
# ============================================================

def validate_khbd_result(
    text,
    expected_periods=1,
    source_scope=None
):

    if not text:

        return False, (
            "AI không trả về nội dung."
        )


    text = text.strip()


    if len(text) < 1000:

        return False, (
            "Giáo án quá ngắn. "
            "Không đạt độ chi tiết tối thiểu."
        )


    upper = text.upper()


    required_sections = [

        "MỤC TIÊU",

        "THIẾT BỊ DẠY HỌC",

        "TIẾN TRÌNH DẠY HỌC",

    ]


    for section in required_sections:

        if section not in upper:

            return False, (
                f"Thiếu phần bắt buộc: {section}"
            )


    # Kiểm tra số tiết
    if expected_periods > 1:

        period_matches = re.findall(

            r"(?im)^#+\s*(?:TIẾT|TIẾT HỌC)\s+(\d+)",

            text

        )


        period_numbers = sorted(

            set(

                int(
                    number
                )

                for number in period_matches

            )

        )


        expected_numbers = list(

            range(
                1,
                expected_periods + 1
            )

        )


        if not all(

            number in period_numbers

            for number in expected_numbers

        ):


            return False, (

                f"Giáo án yêu cầu "
                f"{expected_periods} tiết nhưng "
                f"chỉ phát hiện các tiết: "
                f"{period_numbers}."
            )


    # Kiểm tra hoạt động
    activity_count = len(

        re.findall(

            r"(?im)^###\s*Hoạt động\s+\d+",

            text

        )

    )


    if activity_count < 4:

        return False, (

            "Tiến trình dạy học chưa đủ "
            "4 loại hoạt động chính."
        )


    # Kiểm tra nội dung cụ thể
    content_count = len(

        re.findall(

            r"(?im)^-\s*Nội dung\s*:",

            text

        )

    )


    product_count = len(

        re.findall(

            r"(?im)^-\s*Sản phẩm\s*:",

            text

        )

    )


    if expected_periods > 1:

        minimum_blocks = (
            expected_periods * 4
        )


        if content_count < minimum_blocks:

            return False, (

                "Số lượng mục Nội dung "
                "không tương xứng với số tiết."
            )


        if product_count < minimum_blocks:

            return False, (

                "Số lượng mục Sản phẩm "
                "không tương xứng với số tiết."
            )


    # Kiểm tra mức độ trống
    generic_phrases = [

        "học sinh hoàn thành nhiệm vụ",

        "học sinh hiểu bài",

        "học sinh nắm được kiến thức",

        "thảo luận nhóm",

        "trình bày kết quả",

    ]


    generic_count = 0


    for phrase in generic_phrases:

        generic_count += upper.count(
            phrase.upper()
        )


    if generic_count >= 15:

        return False, (

            "Giáo án có dấu hiệu "
            "sinh nội dung chung chung "
            "thay vì khai thác SGK."
        )


    # Kiểm tra có dấu hiệu nội dung nguồn
    if source_scope:

        source_text = source_scope.get(
            "source_text",
            ""
        )


        # Lấy một số từ khóa nội dung
        source_words = re.findall(

            r"\b[\wÀ-ỹ]{6,}\b",

            source_text.lower()

        )


        source_words = list(

            dict.fromkeys(

                source_words

            )

        )[:100]


        matched = 0


        text_lower = text.lower()


        for word in source_words:

            if word in text_lower:

                matched += 1


        # Không yêu cầu tỷ lệ quá cao vì
        # thuật ngữ có thể bị biến đổi.
        if (
            len(source_words) >= 20
            and matched < 5
        ):

            return False, (

                "Giáo án gần như không sử dụng "
                "từ khóa thực tế từ tài liệu nguồn."
            )


    return True, "Hợp lệ"


# ============================================================
# 18. BUILD PROMPT CHÍNH
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


    mode_text = MODE_LABELS[
        mode
    ]


    # --------------------------------------------------------
    # 1. XÂY DỰNG KNOWLEDGE SCOPE
    # --------------------------------------------------------

    knowledge_scope = build_knowledge_scope(
        noi_dung_chinh
    )


    scope_text = format_knowledge_scope(
        knowledge_scope
    )


    # --------------------------------------------------------
    # 2. XÂY DỰNG PHÂN BỔ TIẾT
    # --------------------------------------------------------

    period_plan = build_period_plan(

        thong_tin,

        knowledge_scope

    )


    period_plan_text = format_period_plan(

        period_plan

    )


    # --------------------------------------------------------
    # 3. TÀI LIỆU BỔ SUNG
    # --------------------------------------------------------

    safe_ai = safe_text(
        noi_dung_ai
    )


    ai_block = ""


    if safe_ai:

        ai_block = f"""

[TÀI LIỆU / YÊU CẦU AI BỔ SUNG]

{safe_ai}

"""


    # --------------------------------------------------------
    # 4. GIÁO ÁN GỐC
    # --------------------------------------------------------

    ga_block = ""


    if (

        mode == "chinh_sua"

        and safe_text(
            noi_dung_ga
        )

    ):

        ga_block = f"""

================ GIÁO ÁN GỐC ================

{safe_text(noi_dung_ga)}

================ END GIÁO ÁN GỐC ============

"""


    # --------------------------------------------------------
    # 5. HÒA NHẬP
    # --------------------------------------------------------

    safe_nhu_cau = safe_text(
        nhu_cau_hoa_nhap
    )


    if (

        tich_hop_hoa_nhap

        and safe_nhu_cau

    ):

        hoa_nhap_block = (

            "Có học sinh cần hỗ trợ đặc biệt: "

            + safe_nhu_cau

            + ". "

            "Phải điều chỉnh nhiệm vụ, "

            "câu hỏi, thời gian và hình thức hỗ trợ "

            "trực tiếp trong từng hoạt động."

        )


    else:

        hoa_nhap_block = (
            "Không có yêu cầu giáo dục hòa nhập đặc biệt."
        )


    # --------------------------------------------------------
    # 6. HOẠT ĐỘNG BỔ SUNG
    # --------------------------------------------------------

    safe_hoat_dong = safe_text(
        hoat_dong
    )


    activity_block = ""


    if safe_hoat_dong:

        activity_block = f"""

[HOẠT ĐỘNG BỔ SUNG THEO YÊU CẦU GIÁO VIÊN]

{safe_hoat_dong}

"""


    # --------------------------------------------------------
    # 7. TASK CONFIG
    # --------------------------------------------------------

    task_config = load_task_config()


    # --------------------------------------------------------
    # 8. PROMPT
    # --------------------------------------------------------

    prompt = f"""
{task_config}

================================================================
VAI TRÒ VÀ MỤC TIÊU
================================================================

Hãy xây dựng một KẾ HOẠCH BÀI DẠY CHI TIẾT,
có thể sử dụng trực tiếp trong thực tế dạy học.

Chế độ soạn:
{mode_text}

Thông tin bài học:
{safe_text(thong_tin)}

================================================================
QUY TẮC TUYỆT ĐỐI VỀ SỐ TIẾT
================================================================

{period_plan_text}

ĐÂY LÀ QUY ĐỊNH BẮT BUỘC.

Nếu số tiết là {period_plan["period_count"]},
kết quả bắt buộc phải có đủ:

### TIẾT 1
### TIẾT 2
...
### TIẾT {period_plan["period_count"]}

KHÔNG được gộp nhiều tiết thành một đoạn chung.

MỖI TIẾT phải có nội dung dạy học riêng,
nhiệm vụ riêng,
sản phẩm riêng,
đánh giá riêng.

================================================================
QUY TẮC KNOWLEDGE SCOPE
================================================================

Chỉ được sử dụng kiến thức có trong:

{scope_text}

NGHIÊM CẤM:

1. Bịa thêm khái niệm ngoài tài liệu nguồn.
2. Viết các nội dung chung chung không gắn với SGK.
3. Ghi "học sinh hoàn thành bài tập" mà không nêu bài tập cụ thể.
4. Ghi "học sinh hiểu bài" mà không nêu kiến thức cụ thể.
5. Ghi "thảo luận nhóm" mà không nêu câu hỏi thảo luận.
6. Ghi "tiến hành thí nghiệm" mà không nêu thí nghiệm nào.
7. Ghi "vận dụng kiến thức" mà không nêu tình huống vận dụng.

================================================================
QUY TẮC KHAI THÁC SGK
================================================================

Mỗi tiết phải khai thác trực tiếp các thành phần phù hợp
từ tài liệu nguồn:

- Tên mục / tiêu đề kiến thức.
- Câu hỏi trong SGK.
- Hoạt động khám phá.
- Thí nghiệm.
- Thực hành.
- Ví dụ.
- Bài tập.
- Công thức.
- Kết luận.
- Số liệu.
- Hiện tượng.
- Quy trình.

Trong mục "Nội dung":

PHẢI ghi rõ học sinh đang học nội dung nào,
câu hỏi nào,
thí nghiệm nào,
ví dụ nào
hoặc bài tập nào.

Trong mục "Sản phẩm":

PHẢI ghi rõ:

- Câu trả lời cụ thể.
- Kết quả quan sát.
- Kết luận.
- Công thức.
- Phép tính.
- Đáp án.
- Bảng kết quả.
- Sơ đồ.
- Sản phẩm học tập cụ thể.

================================================================
PHÂN BỔ NỘI DUNG THEO TỪNG TIẾT
================================================================

Không được tự động chia giáo án thành các đoạn giống nhau.

Hãy phân tích toàn bộ SGK trước,
sau đó phân bổ logic:

- TIẾT 1: Nội dung đầu tiên của bài.
- TIẾT 2: Nội dung tiếp theo.
- TIẾT 3: Nội dung tiếp theo.
- TIẾT 4: Nội dung còn lại, luyện tập, vận dụng phù hợp.

Nếu bài có nhiều nội dung kiến thức,
phải phân bổ theo trình tự logic của SGK.

================================================================
YÊU CẦU ĐỘ CHI TIẾT
================================================================

Mỗi tiết phải có tối thiểu:

- Hoạt động khởi động.
- Hoạt động hình thành kiến thức.
- Hoạt động luyện tập.
- Hoạt động vận dụng hoặc mở rộng phù hợp.

Mỗi hoạt động phải có:

- Mục tiêu.
- Nội dung.
- Sản phẩm.
- Tổ chức thực hiện.

Mỗi phần "Tổ chức thực hiện" phải có đủ:

Bước 1: Chuyển giao nhiệm vụ.

Bước 2: Thực hiện nhiệm vụ.

Bước 3: Báo cáo, thảo luận.

Bước 4: Kết luận, nhận định.

Không được dùng một đoạn mô tả chung cho toàn bộ 4 tiết.

================================================================
TÍCH HỢP
================================================================

Năng lực số:

{nls}

Tích hợp AI:

{
    "Có tích hợp AI sư phạm vào hoạt động nhận thức của học sinh."
    if tich_hop_ai
    else
    "Không bắt buộc tích hợp AI."
}

Giáo dục hòa nhập:

{hoa_nhap_block}

{activity_block}

================================================================
GIÁO ÁN THAM KHẢO
================================================================

Mẫu này chỉ dùng để tham khảo cách trình bày,
không được lấy nội dung kiến thức thay thế SGK:

{safe_text(noi_dung_mau)}

{ga_block}

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

================================================================
TỰ KIỂM TRA TRƯỚC KHI TRẢ KẾT QUẢ
================================================================

Trước khi trả lời, phải tự kiểm tra:

[ ] Đủ {period_plan["period_count"]} tiết.

[ ] Mỗi tiết có nội dung riêng.

[ ] Mỗi tiết có sản phẩm riêng.

[ ] Nội dung bám trực tiếp tài liệu nguồn.

[ ] Có sử dụng câu hỏi / hoạt động / ví dụ / bài tập
nếu chúng xuất hiện trong SGK.

[ ] Không viết chung chung.

[ ] Không bỏ qua phần kiến thức quan trọng của SGK.

[ ] Không gộp 4 tiết thành một đoạn.

Chỉ trả về giáo án hoàn chỉnh bằng Markdown.

Không chào hỏi.

Không giải thích ngoài lề.

Bắt đầu ngay từ tiêu đề bài học.
"""


    return prompt


# ============================================================
# 19. HÀM TẠO GIÁO ÁN HOÀN CHỈNH
# ============================================================

def generate_khbd(

    ai_engine,

    thong_tin,

    noi_dung_chinh,

    noi_dung_ga="",

    noi_dung_ppct="",

    noi_dung_ai="",

    noi_dung_mau="",

    nls="",

    tich_hop_ai=False,

    tich_hop_hoa_nhap=False,

    nhu_cau_hoa_nhap="",

    hoat_dong="",

    mode="tu_dong"

):

    """
    Luồng hoàn chỉnh:

    1. Kiểm tra SGK.
    2. Xây Knowledge Scope.
    3. Xác định số tiết.
    4. Tạo Period Plan.
    5. Xây prompt.
    6. Gọi AI.
    7. Validate kết quả.
    8. Chỉ trả kết quả nếu đạt.
    """

    # --------------------------------------------------------
    # BƯỚC 1: KIỂM TRA NGUỒN
    # --------------------------------------------------------

    source_scope = build_knowledge_scope(
        noi_dung_chinh
    )


    # --------------------------------------------------------
    # BƯỚC 2: XÁC ĐỊNH SỐ TIẾT
    # --------------------------------------------------------

    period_plan = build_period_plan(

        thong_tin,

        source_scope

    )


    # --------------------------------------------------------
    # BƯỚC 3: LƯU THÔNG TIN DEBUG
    # --------------------------------------------------------

    st.session_state[
        "khbd_source_report"
    ] = source_scope.get(
        "source_report"
    )


    st.session_state[
        "khbd_knowledge_scope"
    ] = source_scope


    st.session_state[
        "khbd_period_plan"
    ] = period_plan


    # --------------------------------------------------------
    # BƯỚC 4: BUILD PROMPT
    # --------------------------------------------------------

    prompt = build_prompt(

        thong_tin=thong_tin,

        noi_dung_chinh=noi_dung_chinh,

        noi_dung_ga=noi_dung_ga,

        noi_dung_ppct=noi_dung_ppct,

        noi_dung_ai=noi_dung_ai,

        noi_dung_mau=noi_dung_mau,

        nls=nls,

        tich_hop_ai=tich_hop_ai,

        tich_hop_hoa_nhap=tich_hop_hoa_nhap,

        nhu_cau_hoa_nhap=nhu_cau_hoa_nhap,

        hoat_dong=hoat_dong,

        mode=mode

    )


    # --------------------------------------------------------
    # BƯỚC 5: GỌI AI
    # --------------------------------------------------------

    result = generate_ai(

        ai_engine,

        prompt

    )


    # --------------------------------------------------------
    # BƯỚC 6: VALIDATE
    # --------------------------------------------------------

    valid, message = validate_khbd_result(

        result,

        expected_periods=period_plan[
            "period_count"
        ],

        source_scope=source_scope

    )


    if not valid:

        raise RuntimeError(

            "AI tạo giáo án không đạt kiểm tra chất lượng:\n"

            + message

        )


    # --------------------------------------------------------
    # BƯỚC 7: LƯU KẾT QUẢ
    # --------------------------------------------------------

    st.session_state[
        "khbd_result"
    ] = result


    return result


# ============================================================
# 20. HÀM DEBUG LUỒNG KHBD
# ============================================================

def get_khbd_debug_report():

    source_report = st.session_state.get(
        "khbd_source_report"
    )


    period_plan = st.session_state.get(
        "khbd_period_plan"
    )


    result = st.session_state.get(
        "khbd_result"
    )


    return {

        "source_report": source_report,

        "period_plan": period_plan,

        "result_length": len(
            result
        )
        if result
        else 0,

        "result_word_count": len(
            result.split()
        )
        if result
        else 0,

    }
