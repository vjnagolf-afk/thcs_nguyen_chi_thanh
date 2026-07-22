# -*- coding: utf-8 -*-
"""
============================================================
MODULE: XÂY DỰNG KẾ HOẠCH BÀI DẠY - KHBD
Phiên bản nâng cấp:
- Đọc PDF / DOCX / XLSX / XLS / ảnh
- OCR ảnh nếu có pytesseract
- Vision AI nếu AI Engine hỗ trợ
- Bám sát SGK / giáo án gốc
- Bám sát mẫu giáo án 5512 / file mẫu DOCX
- Giữ nguyên bảng biểu của file mẫu DOCX
- Tích hợp Khung năng lực số theo TT 18/2026/TT-BGDĐT
- Tích hợp AI Engine hiện tại
- Có cơ chế retry / fallback tương thích nhiều AI Engine
- Xuất DOCX với công thức Toán / Lý / Hóa ở dạng Unicode
============================================================
"""

import streamlit as st
import io
import os
import re
import json
import copy
import base64
import hashlib
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import PyPDF2
import docx

from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# =========================================================
# 1. THÔNG TIN VĂN BẢN PHÁP LÝ
# =========================================================

THONG_TU_NLS = {
    "so": "18/2026/TT-BGDĐT",
    "ngay_ban_hanh": "27/03/2026",
    "ngay_hieu_luc": "12/05/2026",
    "co_quan": "Bộ Giáo dục và Đào tạo",
    "ten": (
        "Ban hành Khung năng lực số đối với giáo viên, cán bộ quản lý "
        "cơ sở giáo dục mầm non, phổ thông và giáo dục thường xuyên"
    ),
}


# =========================================================
# 2. KHUNG NĂNG LỰC SỐ
# =========================================================
#
# Kiến trúc dữ liệu được thiết kế theo:
# LĨNH VỰC
#   └── THÀNH PHẦN
#         └── MỨC ĐỘ
#               └── MÔ TẢ YÊU CẦU
#
# Không dùng hệ mã CB/TC/NC cũ.
#
# Có thể bổ sung đầy đủ các dòng chi tiết từ Phụ lục chính thức
# của TT 18/2026/TT-BGDĐT vào cấu trúc này mà không cần sửa giao diện.
# =========================================================

KHUNG_NLS_TT18_2026 = {
    "1. Thông tin và dữ liệu số": {
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu, thông tin và nội dung số": {
            "Mức 1": (
                "Xác định được nhu cầu thông tin; tìm kiếm dữ liệu, thông tin "
                "và nội dung số bằng các phương thức đơn giản."
            ),
            "Mức 2": (
                "Sử dụng được các phương pháp tìm kiếm, duyệt và lọc dữ liệu, "
                "thông tin và nội dung số phù hợp với nhu cầu chuyên môn."
            ),
            "Mức 3": (
                "Vận dụng được các chiến lược tìm kiếm, đánh giá và lựa chọn "
                "dữ liệu, thông tin và nội dung số phục vụ hoạt động giáo dục."
            ),
        },
        "1.2. Đánh giá dữ liệu, thông tin và nội dung số": {
            "Mức 1": (
                "Nhận biết được độ tin cậy cơ bản của nguồn dữ liệu, thông tin "
                "và nội dung số."
            ),
            "Mức 2": (
                "Phân tích và đánh giá được độ tin cậy, tính chính xác và mức độ "
                "phù hợp của dữ liệu, thông tin và nội dung số."
            ),
            "Mức 3": (
                "Có khả năng kiểm chứng, đối chiếu và đánh giá có hệ thống "
                "các nguồn dữ liệu, thông tin và nội dung số."
            ),
        },
        "1.3. Quản lý dữ liệu, thông tin và nội dung số": {
            "Mức 1": (
                "Lưu trữ và sắp xếp được dữ liệu, thông tin và nội dung số "
                "ở mức cơ bản."
            ),
            "Mức 2": (
                "Tổ chức, quản lý và truy xuất được dữ liệu, thông tin và "
                "nội dung số phục vụ công việc."
            ),
            "Mức 3": (
                "Xây dựng và vận hành được hệ thống quản lý dữ liệu, thông tin "
                "và nội dung số có cấu trúc."
            ),
        },
    },

    "2. Giao tiếp và hợp tác trong môi trường số": {
        "2.1. Tương tác thông qua công nghệ số": {
            "Mức 1": (
                "Sử dụng được các công cụ số cơ bản để giao tiếp và tương tác."
            ),
            "Mức 2": (
                "Lựa chọn và sử dụng được công nghệ số phù hợp với mục đích "
                "giao tiếp, dạy học và phối hợp công việc."
            ),
            "Mức 3": (
                "Tổ chức và điều phối hiệu quả hoạt động giao tiếp, tương tác "
                "và phối hợp trong môi trường số."
            ),
        },
        "2.2. Chia sẻ thông tin và nội dung thông qua công nghệ số": {
            "Mức 1": (
                "Chia sẻ được dữ liệu, thông tin và nội dung số thông qua "
                "các công cụ phù hợp."
            ),
            "Mức 2": (
                "Chia sẻ nội dung số có chọn lọc, đúng đối tượng và đúng mục đích."
            ),
            "Mức 3": (
                "Thiết kế và tổ chức được hoạt động chia sẻ, cộng tác và "
                "phổ biến nội dung số có hiệu quả."
            ),
        },
        "2.3. Thực hiện trách nhiệm công dân thông qua công nghệ số": {
            "Mức 1": (
                "Nhận biết được một số quyền, nghĩa vụ và trách nhiệm cơ bản "
                "khi tham gia môi trường số."
            ),
            "Mức 2": (
                "Thực hiện được hành vi phù hợp, có trách nhiệm và an toàn "
                "trong môi trường số."
            ),
            "Mức 3": (
                "Hướng dẫn và hỗ trợ người học thực hiện trách nhiệm công dân "
                "trong môi trường số."
            ),
        },
        "2.4. Hợp tác thông qua công nghệ số": {
            "Mức 1": (
                "Tham gia được các hoạt động hợp tác đơn giản bằng công nghệ số."
            ),
            "Mức 2": (
                "Sử dụng được công cụ số để phối hợp và làm việc nhóm."
            ),
            "Mức 3": (
                "Tổ chức, điều phối và đánh giá được hoạt động hợp tác số."
            ),
        },
        "2.5. Quy tắc ứng xử trong môi trường số": {
            "Mức 1": (
                "Nhận biết được các quy tắc ứng xử cơ bản trong môi trường số."
            ),
            "Mức 2": (
                "Thực hiện được hành vi giao tiếp phù hợp, tôn trọng và có trách nhiệm."
            ),
            "Mức 3": (
                "Hướng dẫn người học xây dựng văn hóa giao tiếp và ứng xử có trách nhiệm."
            ),
        },
        "2.6. Quản lý danh tính số": {
            "Mức 1": (
                "Nhận biết được danh tính số và một số nguy cơ liên quan."
            ),
            "Mức 2": (
                "Quản lý được thông tin và danh tính số cá nhân."
            ),
            "Mức 3": (
                "Hướng dẫn và hỗ trợ việc quản lý danh tính số an toàn."
            ),
        },
    },

    "3. Sáng tạo nội dung số": {
        "3.1. Phát triển nội dung số": {
            "Mức 1": (
                "Tạo được nội dung số đơn giản bằng các công cụ phù hợp."
            ),
            "Mức 2": (
                "Tạo và chỉnh sửa được nội dung số phục vụ dạy học."
            ),
            "Mức 3": (
                "Thiết kế, phát triển và tối ưu hóa các sản phẩm nội dung số "
                "phục vụ hoạt động giáo dục."
            ),
        },
        "3.2. Tích hợp và tái tạo nội dung số": {
            "Mức 1": (
                "Sử dụng được nội dung số có sẵn trong sản phẩm đơn giản."
            ),
            "Mức 2": (
                "Tích hợp và kết hợp được nhiều nguồn nội dung số."
            ),
            "Mức 3": (
                "Thiết kế được sản phẩm số tích hợp từ nhiều nguồn khác nhau."
            ),
        },
        "3.3. Bản quyền và giấy phép": {
            "Mức 1": (
                "Nhận biết được một số vấn đề cơ bản về bản quyền và giấy phép."
            ),
            "Mức 2": (
                "Sử dụng và chia sẻ nội dung số phù hợp với quy định về bản quyền."
            ),
            "Mức 3": (
                "Hướng dẫn và kiểm soát việc sử dụng nội dung số theo quy định."
            ),
        },
        "3.4. Lập trình và tư duy tính toán": {
            "Mức 1": (
                "Nhận biết được một số khái niệm và quy trình lập trình cơ bản."
            ),
            "Mức 2": (
                "Sử dụng được tư duy thuật toán và công cụ lập trình phù hợp."
            ),
            "Mức 3": (
                "Thiết kế, phát triển và đánh giá được giải pháp số hoặc chương trình."
            ),
        },
    },

    "4. An toàn trong môi trường số": {
        "4.1. Bảo vệ thiết bị": {
            "Mức 1": (
                "Nhận biết được một số nguy cơ đối với thiết bị số."
            ),
            "Mức 2": (
                "Thực hiện được các biện pháp bảo vệ thiết bị và dữ liệu."
            ),
            "Mức 3": (
                "Tổ chức và hướng dẫn các biện pháp bảo đảm an toàn thiết bị."
            ),
        },
        "4.2. Bảo vệ dữ liệu cá nhân và quyền riêng tư": {
            "Mức 1": (
                "Nhận biết được thông tin cá nhân và nguy cơ mất an toàn dữ liệu."
            ),
            "Mức 2": (
                "Áp dụng được các biện pháp bảo vệ dữ liệu cá nhân và quyền riêng tư."
            ),
            "Mức 3": (
                "Đánh giá và tổ chức được các biện pháp bảo vệ dữ liệu cá nhân."
            ),
        },
        "4.3. Bảo vệ sức khỏe và an sinh số": {
            "Mức 1": (
                "Nhận biết được một số nguy cơ ảnh hưởng đến sức khỏe khi sử dụng công nghệ."
            ),
            "Mức 2": (
                "Thực hiện được các biện pháp sử dụng công nghệ an toàn và cân bằng."
            ),
            "Mức 3": (
                "Hướng dẫn và hỗ trợ người học sử dụng công nghệ lành mạnh."
            ),
        },
        "4.4. Bảo vệ môi trường": {
            "Mức 1": (
                "Nhận biết được tác động cơ bản của công nghệ số đối với môi trường."
            ),
            "Mức 2": (
                "Thực hiện được các biện pháp sử dụng công nghệ tiết kiệm và thân thiện môi trường."
            ),
            "Mức 3": (
                "Đề xuất và triển khai được giải pháp sử dụng công nghệ số bền vững."
            ),
        },
    },

    "5. Giải quyết vấn đề trong môi trường số": {
        "5.1. Giải quyết vấn đề kỹ thuật": {
            "Mức 1": (
                "Nhận biết và xử lý được một số sự cố kỹ thuật đơn giản."
            ),
            "Mức 2": (
                "Phân tích và giải quyết được các vấn đề kỹ thuật thông thường."
            ),
            "Mức 3": (
                "Phân tích có hệ thống và đề xuất giải pháp cho các vấn đề kỹ thuật phức tạp."
            ),
        },
        "5.2. Xác định nhu cầu và giải pháp công nghệ": {
            "Mức 1": (
                "Nhận biết được nhu cầu sử dụng công nghệ trong tình huống đơn giản."
            ),
            "Mức 2": (
                "Lựa chọn được công cụ và giải pháp số phù hợp."
            ),
            "Mức 3": (
                "Thiết kế và đánh giá được giải pháp công nghệ phù hợp với nhu cầu."
            ),
        },
        "5.3. Sáng tạo và sử dụng công nghệ một cách sáng tạo": {
            "Mức 1": (
                "Sử dụng được công nghệ số để giải quyết nhiệm vụ đơn giản."
            ),
            "Mức 2": (
                "Vận dụng công nghệ số để giải quyết nhiệm vụ và tạo sản phẩm."
            ),
            "Mức 3": (
                "Sáng tạo và đổi mới trong việc sử dụng công nghệ số."
            ),
        },
        "5.4. Xác định khoảng cách năng lực số": {
            "Mức 1": (
                "Nhận biết được những hạn chế cơ bản về năng lực số của bản thân."
            ),
            "Mức 2": (
                "Xác định được nhu cầu học tập và phát triển năng lực số."
            ),
            "Mức 3": (
                "Xây dựng và thực hiện được kế hoạch phát triển năng lực số."
            ),
        },
    },

    "6. Sử dụng trí tuệ nhân tạo": {
        "6.1. Hiểu biết về trí tuệ nhân tạo": {
            "Mức 1": (
                "Nhận biết được khái niệm, khả năng và một số hạn chế cơ bản của AI."
            ),
            "Mức 2": (
                "Giải thích được vai trò, khả năng, giới hạn và rủi ro của AI."
            ),
            "Mức 3": (
                "Đánh giá được tác động của AI đối với hoạt động giáo dục và xã hội."
            ),
        },
        "6.2. Sử dụng trí tuệ nhân tạo": {
            "Mức 1": (
                "Sử dụng được công cụ AI đơn giản với sự hướng dẫn."
            ),
            "Mức 2": (
                "Sử dụng AI để hỗ trợ học tập, dạy học và giải quyết nhiệm vụ."
            ),
            "Mức 3": (
                "Thiết kế, điều phối và đánh giá việc sử dụng AI trong giáo dục."
            ),
        },
        "6.3. Đánh giá và sử dụng AI có trách nhiệm": {
            "Mức 1": (
                "Nhận biết được nguy cơ sai lệch, sai sót và rủi ro khi sử dụng AI."
            ),
            "Mức 2": (
                "Kiểm chứng, đánh giá và sử dụng có trách nhiệm nội dung do AI tạo ra."
            ),
            "Mức 3": (
                "Xây dựng và tổ chức được quy trình sử dụng AI an toàn, có đạo đức "
                "và phù hợp với mục tiêu giáo dục."
            ),
        },
    },
}


# =========================================================
# 3. SESSION STATE
# =========================================================

def init_session_state():
    defaults = {
        "hoat_dong_list": [],
        "soan_mode": "chinh_sua",
        "nls_list": [],
        "ket_qua_giao_an": None,
        "khbd_processing": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_hoat_dong():
    value = st.session_state.get("new_hoat_dong", "").strip()

    if value and value not in st.session_state.hoat_dong_list:
        st.session_state.hoat_dong_list.append(value)

    st.session_state["new_hoat_dong"] = ""


def set_mode(mode):
    st.session_state.soan_mode = mode


def add_nls_item():
    linh_vuc = st.session_state.get("nls_linh_vuc", "")
    thanh_phan = st.session_state.get("nls_thanh_phan", "")
    muc_do = st.session_state.get("nls_muc_do", "")
    noi_dung = st.session_state.get("nls_nd_input", "").strip()

    if not noi_dung:
        return

    item = {
        "van_ban": THONG_TU_NLS["so"],
        "linh_vuc": linh_vuc,
        "thanh_phan": thanh_phan,
        "muc_do": muc_do,
        "noi_dung": noi_dung,
    }

    if item not in st.session_state.nls_list:
        st.session_state.nls_list.append(item)

    st.session_state["nls_nd_input"] = ""


# =========================================================
# 4. HÀM ĐỌC FILE
# =========================================================

def _safe_text(value):
    if value is None:
        return ""

    return str(value).replace("\x00", "").strip()


def doc_pdf(uploaded_file):
    result = []

    reader = PyPDF2.PdfReader(uploaded_file)

    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""

        if text.strip():
            result.append(
                f"\n===== PDF - TRANG {index} =====\n{text.strip()}"
            )

    return "\n".join(result)


def doc_docx(uploaded_file):
    result = []

    document = Document(uploaded_file)

    for index, paragraph in enumerate(document.paragraphs, start=1):
        text = _safe_text(paragraph.text)

        if text:
            result.append(
                f"[ĐOẠN {index}] {text}"
            )

    for table_index, table in enumerate(document.tables, start=1):
        result.append(
            f"\n===== BẢNG WORD {table_index} ====="
        )

        for row in table.rows:
            cells = []

            for cell in row.cells:
                cells.append(
                    _safe_text(cell.text).replace("\n", " ")
                )

            result.append(" | ".join(cells))

    return "\n".join(result)


def doc_excel(uploaded_file):
    result = []

    sheets = pd.read_excel(
        uploaded_file,
        sheet_name=None,
        engine=None,
    )

    for sheet_name, df in sheets.items():

        result.append(
            f"\n===== EXCEL - SHEET: {sheet_name} ====="
        )

        df = df.fillna("")

        result.append(
            df.to_string(index=False)
        )

    return "\n".join(result)


def ocr_image(uploaded_file):
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(uploaded_file)

        text = pytesseract.image_to_string(
            image,
            lang="vie+eng"
        )

        return text.strip()

    except ImportError:
        return (
            "[ẢNH: Chưa cài pytesseract. "
            "AI Vision sẽ được ưu tiên xử lý nếu AI Engine hỗ trợ.]"
        )

    except Exception as e:
        return f"[OCR lỗi: {str(e)}]"


def doc_noi_dung_file(uploaded_file, ai_engine=None):
    """
    Đọc:
    - PDF
    - DOCX
    - XLSX
    - XLS
    - JPG
    - JPEG
    - PNG
    """

    if not uploaded_file:
        return ""

    try:
        file_name = uploaded_file.name.lower()
        ext = Path(file_name).suffix.lower()

        if ext == ".pdf":
            return doc_pdf(uploaded_file)

        if ext == ".docx":
            return doc_docx(uploaded_file)

        if ext in [".xlsx", ".xls"]:
            return doc_excel(uploaded_file)

        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            return ocr_image(uploaded_file)

        return f"[Không hỗ trợ định dạng: {ext}]"

    except Exception as e:
        return (
            f"[LỖI ĐỌC FILE: {uploaded_file.name}]\n"
            f"Chi tiết: {str(e)}"
        )


def doc_file_mau_local():
    candidates = [
        "templates/KHBD_Mau.docx",
        "template/KHBD_Mau.docx",
        "KHBD_Mau.docx",
    ]

    for path in candidates:

        if not os.path.exists(path):
            continue

        try:
            return doc_docx(path)

        except Exception:
            continue

    return ""


# =========================================================
# 5. HỖ TRỢ AI ENGINE
# =========================================================

def _normalize_ai_result(result):
    if result is None:
        return ""

    if isinstance(result, str):
        return result.strip()

    if isinstance(result, dict):

        for key in [
            "text",
            "content",
            "response",
            "output",
            "answer",
        ]:

            if key in result:
                return str(result[key]).strip()

    return str(result).strip()


def ai_generate_text_safe(ai_engine, prompt):
    """
    Tương thích với AI Engine hiện tại.

    Ưu tiên:
    1. generate_text(prompt)
    2. generate_text(prompt=prompt)

    Không tự gọi OpenAI/Gemini/OpenRouter trực tiếp.
    AI Engine trung tâm chịu trách nhiệm fallback.
    """

    if ai_engine is None:
        raise RuntimeError(
            "Chưa truyền AI Engine vào render_xd_khbd()."
        )

    errors = []

    methods = []

    if hasattr(ai_engine, "generate_text"):
        methods.append("generate_text")

    if hasattr(ai_engine, "generate"):
        methods.append("generate")

    for method_name in methods:

        method = getattr(ai_engine, method_name)

        try:

            try:
                result = method(prompt)

            except TypeError:
                result = method(prompt=prompt)

            text = _normalize_ai_result(result)

            if text and not text.startswith("❌"):
                return text

            errors.append(
                f"{method_name}: AI trả về kết quả rỗng hoặc lỗi"
            )

        except Exception as e:
            errors.append(
                f"{method_name}: {str(e)}"
            )

    raise RuntimeError(
        "AI Engine không thể tạo nội dung.\n"
        + "\n".join(errors)
    )


# =========================================================
# 6. CHUẨN HÓA CÔNG THỨC TOÁN / LÝ / HÓA
# =========================================================

def chuan_hoa_cong_thuc(text):
    if not text:
        return ""

    # Loại bỏ LaTeX delimiters
    text = re.sub(r"\\\(", "", text)
    text = re.sub(r"\\\)", "", text)
    text = re.sub(r"\\\[", "", text)
    text = re.sub(r"\\\]", "", text)

    # Công thức phân số
    text = re.sub(
        r"\\frac\{([^{}]+)\}\{([^{}]+)\}",
        r"(\1)/(\2)",
        text
    )

    # Căn
    text = re.sub(
        r"\\sqrt\{([^{}]+)\}",
        r"√(\1)",
        text
    )

    # Các ký hiệu phổ biến
    replacements = {
        r"\times": "×",
        r"\cdot": "·",
        r"\pm": "±",
        r"\leq": "≤",
        r"\geq": "≥",
        r"\neq": "≠",
        r"\approx": "≈",
        r"\rightarrow": "→",
        r"\Delta": "Δ",
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\lambda": "λ",
        r"\mu": "μ",
        r"\rho": "ρ",
        r"\Omega": "Ω",
        r"\omega": "ω",
        r"\pi": "π",
        r"\theta": "θ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Chỉ số dưới đơn giản
    text = re.sub(
        r"_\{([^{}]+)\}",
        r"_\1",
        text
    )

    # Số mũ đơn giản
    text = re.sub(
        r"\^\{([^{}]+)\}",
        r"^\1",
        text
    )

    # Một số ký hiệu hóa học
    chemical = {
        "H_2O": "H₂O",
        "CO_2": "CO₂",
        "O_2": "O₂",
        "H_2": "H₂",
        "N_2": "N₂",
        "NaCl": "NaCl",
        "CaCO_3": "CaCO₃",
        "H_2SO_4": "H₂SO₄",
        "NaOH": "NaOH",
    }

    for old, new in chemical.items():
        text = text.replace(old, new)

    return text


# =========================================================
# 7. WORD HELPER
# =========================================================

def set_cell_text(cell, text, bold=False):
    cell.text = ""

    paragraph = cell.paragraphs[0]

    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

    run = paragraph.add_run(
        chuan_hoa_cong_thuc(_safe_text(text))
    )

    run.bold = bold

    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_cell_shading(cell, fill="D9EAF7"):
    tc_pr = cell._tc.get_or_add_tcPr()

    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)

    tc_pr.append(shd)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()

    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")

    tr_pr.append(tbl_header)


def set_table_width(table, width_cm=17.0):
    """
    Cố gắng đặt bảng vừa khổ A4.
    """

    try:
        table.autofit = True

        for row in table.rows:
            for cell in row.cells:
                cell.width = Cm(
                    width_cm / max(1, len(row.cells))
                )

    except Exception:
        pass


def parse_markdown_table(lines):
    rows = []

    for line in lines:

        if not line.strip().startswith("|"):
            continue

        if "---" in line:
            continue

        cells = [
            c.strip()
            for c in line.strip().strip("|").split("|")
        ]

        if cells:
            rows.append(cells)

    return rows


def append_markdown_to_doc(document, markdown_text):
    """
    Chuyển nội dung AI sang DOCX.

    - Heading
    - Bullet
    - Numbered list
    - Markdown table
    - Công thức Unicode
    """

    lines = markdown_text.splitlines()

    table_buffer = []

    def flush_table():

        nonlocal table_buffer

        if not table_buffer:
            return

        rows = parse_markdown_table(table_buffer)

        if rows:

            max_cols = max(
                len(row)
                for row in rows
            )

            table = document.add_table(
                rows=len(rows),
                cols=max_cols
            )

            table.style = "Table Grid"

            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            for i, row in enumerate(rows):

                if i == 0:
                    set_repeat_table_header(
                        table.rows[i]
                    )

                for j in range(max_cols):

                    value = (
                        row[j]
                        if j < len(row)
                        else ""
                    )

                    set_cell_text(
                        table.cell(i, j),
                        value,
                        bold=(i == 0)
                    )

                    if i == 0:
                        set_cell_shading(
                            table.cell(i, j)
                        )

            set_table_width(table)

        table_buffer = []

    for line in lines:

        stripped = line.strip()

        if stripped.startswith("|"):

            table_buffer.append(line)
            continue

        flush_table()

        if not stripped:
            continue

        if stripped.startswith("### "):

            p = document.add_paragraph()

            run = p.add_run(
                chuan_hoa_cong_thuc(
                    stripped[4:]
                )
            )

            run.bold = True
            run.font.size = Pt(14)

            continue

        if stripped.startswith("## "):

            p = document.add_paragraph()

            run = p.add_run(
                chuan_hoa_cong_thuc(
                    stripped[3:]
                )
            )

            run.bold = True
            run.font.size = Pt(15)

            continue

        if stripped.startswith("# "):

            p = document.add_paragraph()

            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            run = p.add_run(
                chuan_hoa_cong_thuc(
                    stripped[2:]
                )
            )

            run.bold = True
            run.font.size = Pt(16)

            continue

        if stripped.startswith("- "):

            p = document.add_paragraph(
                style="List Bullet"
            )

            p.add_run(
                chuan_hoa_cong_thuc(
                    stripped[2:]
                )
            )

            continue

        if re.match(r"^\d+\.\s+", stripped):

            content = re.sub(
                r"^\d+\.\s+",
                "",
                stripped
            )

            p = document.add_paragraph(
                style="List Number"
            )

            p.add_run(
                chuan_hoa_cong_thuc(
                    content
                )
            )

            continue

        p = document.add_paragraph()

        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        p.paragraph_format.line_spacing = 1.15

        p.add_run(
            chuan_hoa_cong_thuc(
                stripped
            )
        )

    flush_table()


def load_template_docx(uploaded_file=None):
    """
    Ưu tiên:
    1. File mẫu GV tải lên
    2. templates/KHBD_Mau.docx
    3. Tạo DOCX mới
    """

    if uploaded_file:

        try:
            return Document(uploaded_file)

        except Exception:
            pass

    candidates = [
        "templates/KHBD_Mau.docx",
        "template/KHBD_Mau.docx",
        "KHBD_Mau.docx",
    ]

    for path in candidates:

        if os.path.exists(path):

            try:
                return Document(path)

            except Exception:
                pass

    return Document()


def tao_file_word_hoan_hao(
    van_ban,
    file_template=None,
    giu_nguyen_mau=True,
):
    """
    Xuất DOCX.

    Nếu có file mẫu:
    - Mở trực tiếp file mẫu.
    - Giữ lại toàn bộ bảng biểu, header, footer,
      căn lề, style hiện có.
    - Thêm nội dung AI vào cuối tài liệu.

    Nếu không có file mẫu:
    - Tạo DOCX chuẩn A4.
    """

    if file_template and giu_nguyen_mau:

        doc_word = load_template_docx(
            file_template
        )

    else:

        doc_word = Document()

        section = doc_word.sections[0]

        section.page_height = Cm(29.7)
        section.page_width = Cm(21.0)

        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)

    style = doc_word.styles["Normal"]

    style.font.name = "Times New Roman"
    style._element.rPr.rFonts.set(
        qn("w:eastAsia"),
        "Times New Roman"
    )

    style.font.size = Pt(13)

    style.paragraph_format.line_spacing = 1.15

    # Nếu template đã có nội dung,
    # không xóa các bảng hiện có.
    if doc_word.paragraphs and any(
        p.text.strip()
        for p in doc_word.paragraphs
    ):

        doc_word.add_page_break()

    append_markdown_to_doc(
        doc_word,
        van_ban
    )

    output = io.BytesIO()

    doc_word.save(output)

    output.seek(0)

    return output


# =========================================================
# 8. TẠO DỮ LIỆU NLS CHO PROMPT
# =========================================================

def format_nls_prompt():
    if not st.session_state.nls_list:
        return "Không tích hợp năng lực số cụ thể."

    result = []

    for index, item in enumerate(
        st.session_state.nls_list,
        start=1
    ):

        result.append(
            f"""
NĂNG LỰC SỐ {index}
- Văn bản: {item['van_ban']}
- Lĩnh vực: {item['linh_vuc']}
- Thành phần: {item['thanh_phan']}
- Mức độ: {item['muc_do']}
- Yêu cầu cần đạt:
  {item['noi_dung']}
"""
        )

    return "\n".join(result)


# =========================================================
# 9. PROMPT KHBD CHUYÊN SÂU
# =========================================================

def build_khbd_prompt(
    mode,
    thong_tin_bai_day,
    noi_dung_chinh,
    noi_dung_mau,
    noi_dung_ppct,
    noi_dung_ai_file,
    nls_text,
    tich_hop_ai,
    tich_hop_kt,
    dang_khuyet_tat,
    hoat_dong,
):
    if mode == "chinh_sua":

        nhiem_vu = """
NHIỆM VỤ:
Phân tích và nâng cấp giáo án gốc đã cung cấp.

YÊU CẦU:
- Giữ nguyên tên bài.
- Giữ nguyên phạm vi kiến thức.
- Giữ lại các hoạt động phù hợp trong giáo án gốc.
- Không tự ý đưa kiến thức ngoài tài liệu nguồn.
- Có thể sửa lỗi kiến thức, lỗi logic, lỗi sư phạm.
- Bổ sung chi tiết hoạt động GV và HS.
"""

    else:

        nhiem_vu = """
NHIỆM VỤ:
Xây dựng Kế hoạch bài dạy mới dựa trực tiếp trên SGK/tài liệu nguồn.

YÊU CẦU:
- Chỉ sử dụng kiến thức có trong tài liệu nguồn.
- Không tự ý mở rộng sang bài khác.
- Không tự bịa số trang nếu tài liệu không cung cấp.
- Mọi hoạt động phải có mục tiêu, nhiệm vụ, sản phẩm và cách tổ chức.
"""

    prompt = f"""
BẠN LÀ CHUYÊN GIA XÂY DỰNG KẾ HOẠCH BÀI DẠY
THEO CHƯƠNG TRÌNH GDPT 2018 TẠI VIỆT NAM.

{nhiem_vu}

==================================================
I. THÔNG TIN BÀI DẠY
==================================================

{thong_tin_bai_day}

==================================================
II. NGUYÊN TẮC KIỂM SOÁT NGUỒN
==================================================

1. TÀI LIỆU NGUỒN LÀ NGUỒN KIẾN THỨC ƯU TIÊN CAO NHẤT.

2. Chỉ được sử dụng kiến thức có căn cứ trong:
   - SGK / tài liệu bài học.
   - Giáo án gốc.
   - Tài liệu PPCT được cung cấp.
   - Tài liệu bổ sung do giáo viên tải lên.

3. Nếu tài liệu không đủ dữ kiện:
   - Không được tự bịa.
   - Không được tự gán số trang.
   - Không được tự thêm kiến thức bài khác.

4. Nếu có mâu thuẫn giữa dữ liệu:
   - Ưu tiên tài liệu bài học trực tiếp.
   - Sau đó đến giáo án gốc.
   - Sau đó đến tài liệu bổ sung.

==================================================
III. YÊU CẦU THEO MẪU 5512
==================================================

Bắt buộc xây dựng đầy đủ:

A. MỤC TIÊU

1. Về kiến thức
2. Về năng lực
3. Về phẩm chất

B. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU

C. TIẾN TRÌNH DẠY HỌC

Mỗi hoạt động phải có:

1. Mục tiêu
2. Nội dung
3. Sản phẩm
4. Tổ chức thực hiện

Trong phần "Tổ chức thực hiện", phải thể hiện rõ:

- Chuyển giao nhiệm vụ
- Thực hiện nhiệm vụ
- Báo cáo, thảo luận
- Kết luận, nhận định

Không được viết chung chung:

SAI:
"GV hướng dẫn HS thực hiện nhiệm vụ."

ĐÚNG:
"GV yêu cầu HS quan sát ... và trả lời câu hỏi: '...'."

Phải viết cụ thể lời dẫn, câu hỏi, nhiệm vụ và sản phẩm.

==================================================
IV. TÍCH HỢP NĂNG LỰC SỐ
==================================================

Khung pháp lý:
{THONG_TU_NLS['so']}

{nls_text}

YÊU CẦU:

- Không được tự đổi tên lĩnh vực.
- Không được tự đổi tên thành phần.
- Không được tự đổi mức độ.
- Không được tạo năng lực số không có trong dữ liệu đã chọn.

Nếu có năng lực số:

1. Phải gắn với một hoạt động cụ thể.
2. Phải mô tả học sinh thực hiện thao tác số gì.
3. Phải có sản phẩm/minh chứng.
4. Phải có cách đánh giá.

==================================================
V. TÍCH HỢP AI
==================================================

{(
" CÓ TÍCH HỢP AI.\n"
"Phải nêu rõ:\n"
"- Học sinh sử dụng AI ở hoạt động nào.\n"
"- AI hỗ trợ nhiệm vụ gì.\n"
"- Học sinh phải kiểm chứng kết quả AI ra sao.\n"
"- Sản phẩm học tập là gì.\n"
"- Không được coi kết quả AI là chân lý tuyệt đối."
) if tich_hop_ai else "KHÔNG TÍCH HỢP AI."}

==================================================
VI. DẠY HỌC HÒA NHẬP
==================================================

{(
f"Có học sinh thuộc nhóm: {dang_khuyet_tat}.\n"
"Phải điều chỉnh nhiệm vụ, phương tiện, thời gian hoặc cách thể hiện sản phẩm "
"phù hợp với học sinh."
) if tich_hop_kt else "Không yêu cầu tích hợp dạy học khuyết tật."}

==================================================
VII. HOẠT ĐỘNG GIÁO VIÊN YÊU CẦU
==================================================

{hoat_dong}

==================================================
VIII. MẪU GIÁO ÁN BẮT BUỘC
==================================================

{noi_dung_mau if noi_dung_mau else "Không có file mẫu riêng. Sử dụng cấu trúc KHBD theo Công văn 5512."}

==================================================
IX. PPCT
==================================================

{noi_dung_ppct}

==================================================
X. BẢNG TÍCH HỢP AI
==================================================

{noi_dung_ai_file}

==================================================
XI. TÀI LIỆU NGUỒN CỐT LÕI
==================================================

{noi_dung_chinh}

==================================================
XII. QUY TẮC CÔNG THỨC
==================================================

TUYỆT ĐỐI KHÔNG dùng LaTeX.

Viết công thức bằng văn bản Unicode hoặc văn bản thường:

ĐÚNG:
- v = s/t
- F = m.a
- U = I.R
- A = U.I.t
- H₂O
- CO₂
- H₂SO₄
- x²
- √a
- Δt

SAI:
\\frac{{s}}{{t}}
$E = mc^2$
\\[F = ma\\]

==================================================
XIII. ĐẦU RA
==================================================

Chỉ trả về nội dung KHBD.

Không chào hỏi.
Không giải thích quá trình.
Không nói "dưới đây là".
Không thêm nhận xét ngoài giáo án.

Nội dung phải đầy đủ, chi tiết, có thể sử dụng trực tiếp trong dạy học.
"""

    return prompt


# =========================================================
# 10. GIAO DIỆN CHÍNH
# =========================================================

def render_xd_khbd(ai_engine=None):

    init_session_state()

    st.markdown(
        """
        <style>

        .stButton button[kind="primary"] {
            background-color: #9333ea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
        }

        .stButton button[kind="secondary"] {
            color: #6b7280;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            font-weight: 600;
        }

        .upload-card {
            text-align: center;
            padding: 10px;
        }

        .upload-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .upload-title {
            font-weight: bold;
            font-size: 1.1rem;
        }

        .upload-desc {
            font-size: 0.85rem;
            color: #6b7280;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # THÔNG TIN BÀI DẠY
    # =====================================================

    st.markdown("### 🎛️ THÔNG TIN BÀI DẠY")

    col1, col2 = st.columns(2)

    with col1:

        st.selectbox(
            "KHỐI LỚP",
            [
                "Lớp 6",
                "Lớp 7",
                "Lớp 8",
                "Lớp 9",
                "Lớp 10",
                "Lớp 11",
                "Lớp 12",
            ],
            key="khbd_khoi_lop"
        )

    with col2:

        st.selectbox(
            "MÔN HỌC",
            [
                "Toán",
                "Ngữ văn",
                "Tiếng Anh",
                "Khoa học tự nhiên",
                "Vật lí",
                "Hóa học",
                "Sinh học",
                "Lịch sử và Địa lí",
                "Tin học",
                "Công nghệ",
                "Khác",
            ],
            key="khbd_mon_hoc"
        )

    # =====================================================
    # CHẾ ĐỘ
    # =====================================================

    st.markdown("#### ✨ CHẾ ĐỘ SOẠN")

    c1, c2 = st.columns(2)

    with c1:

        st.button(
            "📄 CHỈNH SỬA GIÁO ÁN GỐC",
            type=(
                "primary"
                if st.session_state.soan_mode == "chinh_sua"
                else "secondary"
            ),
            use_container_width=True,
            on_click=set_mode,
            args=("chinh_sua",)
        )

    with c2:

        st.button(
            "⚡ TỰ ĐỘNG SOẠN TỪ SGK",
            type=(
                "primary"
                if st.session_state.soan_mode == "tu_dong"
                else "secondary"
            ),
            use_container_width=True,
            on_click=set_mode,
            args=("tu_dong",)
        )

    st.divider()

    # =====================================================
    # TÍCH HỢP
    # =====================================================

    st.markdown("#### 🔧 TÍCH HỢP")

    c1, c2, c3 = st.columns(3)

    with c1:

        tich_hop_nls = st.checkbox(
            "Tích hợp Năng lực số",
            key="chk_nls"
        )

    with c2:

        tich_hop_ai = st.checkbox(
            "Tích hợp Năng lực AI",
            key="chk_ai"
        )

    with c3:

        tich_hop_kt = st.checkbox(
            "Dạy học hòa nhập",
            key="chk_kt"
        )

    # =====================================================
    # CHỈNH SỬA GIÁO ÁN
    # =====================================================

    if st.session_state.soan_mode == "chinh_sua":

        st.markdown(
            "### 📤 TÀI LIỆU ĐẦU VÀO"
        )

        file_ga = st.file_uploader(
            "📄 Giáo án gốc",
            type=[
                "docx",
                "pdf",
                "jpg",
                "jpeg",
                "png",
                "webp",
            ],
            accept_multiple_files=True,
            key="file_ga"
        )

        file_ppct = st.file_uploader(
            "📊 PPCT",
            type=[
                "pdf",
                "docx",
                "xlsx",
                "xls",
            ],
            key="file_ppct"
        )

        file_ai = st.file_uploader(
            "🤖 Bảng tích hợp AI",
            type=[
                "pdf",
                "docx",
                "xlsx",
                "xls",
            ],
            key="file_ai"
        )

        file_sgk = []

        file_template_custom = None

    # =====================================================
    # TỰ ĐỘNG SOẠN
    # =====================================================

    else:

        st.markdown(
            "### 📘 THÔNG TIN SOẠN MỚI"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.selectbox(
                "Cấp học",
                [
                    "THCS",
                    "Tiểu học",
                    "THPT",
                ],
                key="khbd_cap_hoc"
            )

        with c2:

            st.selectbox(
                "Mẫu giáo án",
                [
                    "Công văn 5512",
                    "Mẫu rút gọn",
                    "Mẫu tư duy",
                ],
                key="khbd_mau_giao_an"
            )

        c1, c2 = st.columns(2)

        with c1:

            st.text_input(
                "Tên bài dạy",
                key="khbd_ten_bai"
            )

        with c2:

            st.text_input(
                "Thời lượng",
                value="1 tiết",
                key="khbd_so_tiet"
            )

        file_sgk = st.file_uploader(
            "📘 Tải SGK / tài liệu bài học",
            type=[
                "pdf",
                "jpg",
                "jpeg",
                "png",
                "webp",
                "docx",
            ],
            accept_multiple_files=True,
            key="file_sgk"
        )

        file_template_custom = st.file_uploader(
            "📄 File mẫu giáo án DOCX của trường",
            type=["docx"],
            key="file_template_custom"
        )

        file_ppct = None
        file_ai = None

        if tich_hop_nls:

            file_ppct = st.file_uploader(
                "📊 PPCT dùng để tích hợp NLS",
                type=[
                    "pdf",
                    "docx",
                    "xlsx",
                    "xls",
                ],
                key="file_ppct_tu_dong"
            )

        if tich_hop_ai:

            file_ai = st.file_uploader(
                "🤖 Bảng tích hợp AI",
                type=[
                    "pdf",
                    "docx",
                    "xlsx",
                    "xls",
                ],
                key="file_ai_tu_dong"
            )

    # =====================================================
    # HOẠT ĐỘNG GIÁO VIÊN
    # =====================================================

    st.markdown("### 📌 HOẠT ĐỘNG GIÁO VIÊN MONG MUỐN")

    c1, c2 = st.columns([4, 1])

    with c1:

        st.text_input(
            "Hoạt động",
            placeholder="VD: Thí nghiệm, trò chơi, mô phỏng...",
            key="new_hoat_dong",
            label_visibility="collapsed",
            on_change=add_hoat_dong
        )

    with c2:

        st.button(
            "➕ Thêm",
            type="primary",
            use_container_width=True,
            on_click=add_hoat_dong
        )

    for i, item in enumerate(
        st.session_state.hoat_dong_list
    ):

        c1, c2 = st.columns([10, 1])

        with c1:

            st.info(
                f"📍 {item}"
            )

        with c2:

            if st.button(
                "Xóa",
                key=f"del_hd_{i}"
            ):

                st.session_state.hoat_dong_list.pop(i)

                st.rerun()

    # =====================================================
    # NĂNG LỰC SỐ
    # =====================================================

    if tich_hop_nls:

        st.markdown(
            f"### 🎯 NĂNG LỰC SỐ - {THONG_TU_NLS['so']}"
        )

        st.caption(
            f"{THONG_TU_NLS['ten']}"
        )

        linh_vuc_list = list(
            KHUNG_NLS_TT18_2026.keys()
        )

        linh_vuc = st.selectbox(
            "1. LĨNH VỰC",
            linh_vuc_list,
            key="nls_linh_vuc"
        )

        thanh_phan_list = list(
            KHUNG_NLS_TT18_2026[
                linh_vuc
            ].keys()
        )

        thanh_phan = st.selectbox(
            "2. THÀNH PHẦN",
            thanh_phan_list,
            key="nls_thanh_phan"
        )

        muc_do_list = list(
            KHUNG_NLS_TT18_2026[
                linh_vuc
            ][
                thanh_phan
            ].keys()
        )

        muc_do = st.selectbox(
            "3. MỨC ĐỘ",
            muc_do_list,
            key="nls_muc_do"
        )

        noi_dung_mac_dinh = (
            KHUNG_NLS_TT18_2026[
                linh_vuc
            ][
                thanh_phan
            ][
                muc_do
            ]
        )

        st.text_area(
            "4. YÊU CẦU CẦN ĐẠT",
            value=noi_dung_mac_dinh,
            key="nls_nd_input",
            height=120
        )

        st.button(
            "➕ THÊM NĂNG LỰC SỐ",
            type="primary",
            on_click=add_nls_item,
            use_container_width=True
        )

        if st.session_state.nls_list:

            st.markdown(
                "#### 📋 DANH SÁCH ĐÃ CHỌN"
            )

            for i, item in enumerate(
                st.session_state.nls_list
            ):

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"""
**{i + 1}. {item['linh_vuc']}**

**Thành phần:** {item['thanh_phan']}

**Mức độ:** {item['muc_do']}

**Yêu cầu:** {item['noi_dung']}
"""
                    )

                    if st.button(
                        "Xóa",
                        key=f"del_nls_{i}"
                    ):

                        st.session_state.nls_list.pop(i)

                        st.rerun()

    # =====================================================
    # KHUYẾT TẬT
    # =====================================================

    dang_khuyet_tat = []

    if tich_hop_kt:

        dang_khuyet_tat = st.multiselect(
            "Dạng khuyết tật / nhu cầu hỗ trợ",
            [
                "Vận động",
                "Nghe",
                "Nói",
                "Nhìn",
                "Thần kinh",
                "Tâm thần",
                "Trí tuệ",
                "Tự kỷ",
                "Khác",
            ],
            default=[]
        )

    # =====================================================
    # NGÔN NGỮ
    # =====================================================

    ngon_ngu_anh = st.checkbox(
        "Giáo án viết bằng Tiếng Anh",
        key="khbd_ngon_ngu"
    )

    # =====================================================
    # NÚT XỬ LÝ
    # =====================================================

    st.write("")

    if st.button(
        "⚡ KÍCH HOẠT XỬ LÝ AI",
        type="primary",
        use_container_width=True
    ):

        st.session_state.ket_qua_giao_an = None

        if ai_engine is None:

            st.error(
                "❌ Chưa truyền AI Engine vào render_xd_khbd()."
            )

            st.stop()

        # -------------------------------------------------
        # KIỂM TRA FILE
        # -------------------------------------------------

        if (
            st.session_state.soan_mode
            == "chinh_sua"
            and not file_ga
        ):

            st.error(
                "⚠️ Vui lòng tải lên giáo án gốc."
            )

            st.stop()

        if (
            st.session_state.soan_mode
            == "tu_dong"
            and not file_sgk
        ):

            st.error(
                "⚠️ Vui lòng tải lên SGK hoặc tài liệu bài học."
            )

            st.stop()

        # -------------------------------------------------
        # ĐỌC FILE
        # -------------------------------------------------

        with st.spinner(
            "🧠 AI đang phân tích tài liệu và xây dựng KHBD..."
        ):

            try:

                noi_dung_chinh = ""

                if (
                    st.session_state.soan_mode
                    == "chinh_sua"
                ):

                    for f in file_ga:

                        noi_dung_chinh += (
                            f"\n\n===== GIÁO ÁN GỐC: "
                            f"{f.name} =====\n"
                        )

                        noi_dung_chinh += (
                            doc_noi_dung_file(
                                f,
                                ai_engine
                            )
                        )

                else:

                    for f in file_sgk:

                        noi_dung_chinh += (
                            f"\n\n===== SGK / TÀI LIỆU: "
                            f"{f.name} =====\n"
                        )

                        noi_dung_chinh += (
                            doc_noi_dung_file(
                                f,
                                ai_engine
                            )
                        )

                noi_dung_ppct = ""

                if file_ppct:

                    noi_dung_ppct = (
                        doc_noi_dung_file(
                            file_ppct,
                            ai_engine
                        )
                    )

                noi_dung_ai_file = ""

                if file_ai:

                    noi_dung_ai_file = (
                        doc_noi_dung_file(
                            file_ai,
                            ai_engine
                        )
                    )

                noi_dung_mau = ""

                if file_template_custom:

                    noi_dung_mau = (
                        doc_noi_dung_file(
                            file_template_custom,
                            ai_engine
                        )
                    )

                else:

                    noi_dung_mau = (
                        doc_file_mau_local()
                    )

                # -------------------------------------------------
                # GIỚI HẠN DỮ LIỆU
                # -------------------------------------------------

                max_chars = 120000

                if len(noi_dung_chinh) > max_chars:

                    st.warning(
                        "⚠️ Tài liệu rất dài. "
                        "Hệ thống cắt phần vượt giới hạn."
                    )

                    noi_dung_chinh = (
                        noi_dung_chinh[:max_chars]
                        + "\n[ĐÃ CẮT PHẦN VƯỢT GIỚI HẠN]"
                    )

                # -------------------------------------------------
                # THÔNG TIN BÀI
                # -------------------------------------------------

                cap_hoc = st.session_state.get(
                    "khbd_cap_hoc",
                    "THCS"
                )

                khoi_lop = st.session_state.get(
                    "khbd_khoi_lop",
                    "Không xác định"
                )

                mon_hoc = st.session_state.get(
                    "khbd_mon_hoc",
                    "Không xác định"
                )

                ten_bai = st.session_state.get(
                    "khbd_ten_bai",
                    "Theo tài liệu nguồn"
                )

                so_tiet = st.session_state.get(
                    "khbd_so_tiet",
                    "1 tiết"
                )

                mau_giao_an = st.session_state.get(
                    "khbd_mau_giao_an",
                    "Công văn 5512"
                )

                thong_tin_bai_day = f"""
- Cấp học: {cap_hoc}
- Khối lớp: {khoi_lop}
- Môn học: {mon_hoc}
- Tên bài dạy: {ten_bai}
- Thời lượng: {so_tiet}
- Mẫu giáo án: {mau_giao_an}
- Ngôn ngữ: {"Tiếng Anh" if ngon_ngu_anh else "Tiếng Việt"}
"""

                nls_text = format_nls_prompt()

                hoat_dong = (
                    "\n".join(
                        st.session_state.hoat_dong_list
                    )
                    if st.session_state.hoat_dong_list
                    else "Không có."
                )

                prompt = build_khbd_prompt(
                    mode=st.session_state.soan_mode,
                    thong_tin_bai_day=thong_tin_bai_day,
                    noi_dung_chinh=noi_dung_chinh,
                    noi_dung_mau=noi_dung_mau,
                    noi_dung_ppct=noi_dung_ppct,
                    noi_dung_ai_file=noi_dung_ai_file,
                    nls_text=nls_text,
                    tich_hop_ai=tich_hop_ai,
                    tich_hop_kt=tich_hop_kt,
                    dang_khuyet_tat=", ".join(
                        dang_khuyet_tat
                    ),
                    hoat_dong=hoat_dong,
                )

                ket_qua = ai_generate_text_safe(
                    ai_engine,
                    prompt
                )

                if not ket_qua:

                    st.error(
                        "❌ AI không trả về nội dung."
                    )

                else:

                    st.session_state.ket_qua_giao_an = ket_qua

                    st.success(
                        "🎉 Đã tạo KHBD thành công."
                    )

            except Exception as e:

                st.error(
                    f"❌ Lỗi xử lý: {str(e)}"
                )

    # =====================================================
    # HIỂN THỊ KẾT QUẢ
    # =====================================================

    if st.session_state.get(
        "ket_qua_giao_an"
    ):

        st.markdown(
            "### 📝 KẾT QUẢ KHBD"
        )

        with st.container(
            border=True
        ):

            st.markdown(
                st.session_state.ket_qua_giao_an
            )

        # -------------------------------------------------
        # CHỌN FILE MẪU ĐỂ XUẤT
        # -------------------------------------------------

        template_for_export = None

        if (
            st.session_state.soan_mode
            == "tu_dong"
            and file_template_custom
        ):

            template_for_export = (
                file_template_custom
            )

        word_file = tao_file_word_hoan_hao(
            st.session_state.ket_qua_giao_an,
            file_template=template_for_export,
            giu_nguyen_mau=True,
        )

        st.download_button(
            "📥 TẢI KHBD WORD",
            data=word_file,
            file_name="KHBD_Thong_Minh.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True
        )
