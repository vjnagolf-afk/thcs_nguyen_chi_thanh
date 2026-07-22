# -*- coding: utf-8 -*-
"""
============================================================
VIEW: XÂY DỰNG KẾ HOẠCH BÀI DẠY - KHBD
============================================================

Chức năng:
- Soạn KHBD từ giáo án gốc / SGK / tài liệu bài học
- Đọc PDF / DOCX / XLSX / XLS / ảnh
- OCR ảnh nếu có pytesseract
- Tích hợp AI Engine trung tâm
- Tích hợp Năng lực số
- Tích hợp AI
- Dạy học hòa nhập
- Hỗ trợ hoạt động dạy học do giáo viên yêu cầu
- Xuất Word thông qua hệ thống export trung tâm

Kiến trúc:
views/xd_khbd_view.py
        ↓
AI Engine
        ↓
export/
    ├── export_word.py
    ├── word_export_engine.py
    ├── word_markdown.py
    ├── word_math.py
    ├── word_tables.py
    ├── word_styles.py
    ├── word_utils.py
    └── ...

============================================================
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
import pandas as pd
import PyPDF2

from docx import Document


# ============================================================
# 1. IMPORT EXPORT ENGINE
# ============================================================

try:
    from export.export_word import export_word

except ImportError:

    export_word = None


# ============================================================
# 2. THÔNG TIN KHUNG NĂNG LỰC SỐ
# ============================================================

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


KHUNG_NLS_TT18_2026 = {

    "1. Thông tin và dữ liệu số": {

        "1.1. Duyệt, tìm kiếm và lọc dữ liệu, thông tin và nội dung số": {

            "Mức 1":
                "Xác định được nhu cầu thông tin; tìm kiếm dữ liệu, "
                "thông tin và nội dung số bằng các phương thức đơn giản.",

            "Mức 2":
                "Sử dụng được các phương pháp tìm kiếm, duyệt và lọc "
                "dữ liệu, thông tin và nội dung số phù hợp với nhu cầu chuyên môn.",

            "Mức 3":
                "Vận dụng được các chiến lược tìm kiếm, đánh giá và lựa chọn "
                "dữ liệu, thông tin và nội dung số phục vụ hoạt động giáo dục.",
        },

        "1.2. Đánh giá dữ liệu, thông tin và nội dung số": {

            "Mức 1":
                "Nhận biết được độ tin cậy cơ bản của nguồn dữ liệu, "
                "thông tin và nội dung số.",

            "Mức 2":
                "Phân tích và đánh giá được độ tin cậy, tính chính xác "
                "và mức độ phù hợp của dữ liệu, thông tin và nội dung số.",

            "Mức 3":
                "Có khả năng kiểm chứng, đối chiếu và đánh giá có hệ thống "
                "các nguồn dữ liệu, thông tin và nội dung số.",
        },

        "1.3. Quản lý dữ liệu, thông tin và nội dung số": {

            "Mức 1":
                "Lưu trữ và sắp xếp được dữ liệu, thông tin và nội dung số "
                "ở mức cơ bản.",

            "Mức 2":
                "Tổ chức, quản lý và truy xuất được dữ liệu, thông tin "
                "và nội dung số phục vụ công việc.",

            "Mức 3":
                "Xây dựng và vận hành được hệ thống quản lý dữ liệu, "
                "thông tin và nội dung số có cấu trúc.",
        },
    },


    "2. Giao tiếp và hợp tác trong môi trường số": {

        "2.1. Tương tác thông qua công nghệ số": {

            "Mức 1":
                "Sử dụng được các công cụ số cơ bản để giao tiếp và tương tác.",

            "Mức 2":
                "Lựa chọn và sử dụng được công nghệ số phù hợp với mục đích "
                "giao tiếp, dạy học và phối hợp công việc.",

            "Mức 3":
                "Tổ chức và điều phối hiệu quả hoạt động giao tiếp, tương tác "
                "và phối hợp trong môi trường số.",
        },

        "2.2. Chia sẻ thông tin và nội dung thông qua công nghệ số": {

            "Mức 1":
                "Chia sẻ được dữ liệu, thông tin và nội dung số "
                "thông qua các công cụ phù hợp.",

            "Mức 2":
                "Chia sẻ nội dung số có chọn lọc, đúng đối tượng và đúng mục đích.",

            "Mức 3":
                "Thiết kế và tổ chức được hoạt động chia sẻ, cộng tác "
                "và phổ biến nội dung số có hiệu quả.",
        },

        "2.3. Thực hiện trách nhiệm công dân thông qua công nghệ số": {

            "Mức 1":
                "Nhận biết được một số quyền, nghĩa vụ và trách nhiệm cơ bản "
                "khi tham gia môi trường số.",

            "Mức 2":
                "Thực hiện được hành vi phù hợp, có trách nhiệm và an toàn "
                "trong môi trường số.",

            "Mức 3":
                "Hướng dẫn và hỗ trợ người học thực hiện trách nhiệm công dân "
                "trong môi trường số.",
        },

        "2.4. Hợp tác thông qua công nghệ số": {

            "Mức 1":
                "Tham gia được các hoạt động hợp tác đơn giản bằng công nghệ số.",

            "Mức 2":
                "Sử dụng được công cụ số để phối hợp và làm việc nhóm.",

            "Mức 3":
                "Tổ chức, điều phối và đánh giá được hoạt động hợp tác số.",
        },

        "2.5. Quy tắc ứng xử trong môi trường số": {

            "Mức 1":
                "Nhận biết được các quy tắc ứng xử cơ bản trong môi trường số.",

            "Mức 2":
                "Thực hiện được hành vi giao tiếp phù hợp, tôn trọng "
                "và có trách nhiệm.",

            "Mức 3":
                "Hướng dẫn người học xây dựng văn hóa giao tiếp "
                "và ứng xử có trách nhiệm.",
        },

        "2.6. Quản lý danh tính số": {

            "Mức 1":
                "Nhận biết được danh tính số và một số nguy cơ liên quan.",

            "Mức 2":
                "Quản lý được thông tin và danh tính số cá nhân.",

            "Mức 3":
                "Hướng dẫn và hỗ trợ việc quản lý danh tính số an toàn.",
        },
    },


    "3. Sáng tạo nội dung số": {

        "3.1. Phát triển nội dung số": {

            "Mức 1":
                "Tạo được nội dung số đơn giản bằng các công cụ phù hợp.",

            "Mức 2":
                "Tạo và chỉnh sửa được nội dung số phục vụ dạy học.",

            "Mức 3":
                "Thiết kế, phát triển và tối ưu hóa các sản phẩm nội dung số "
                "phục vụ hoạt động giáo dục.",
        },

        "3.2. Tích hợp và tái tạo nội dung số": {

            "Mức 1":
                "Sử dụng được nội dung số có sẵn trong sản phẩm đơn giản.",

            "Mức 2":
                "Tích hợp và kết hợp được nhiều nguồn nội dung số.",

            "Mức 3":
                "Thiết kế được sản phẩm số tích hợp từ nhiều nguồn khác nhau.",
        },

        "3.3. Bản quyền và giấy phép": {

            "Mức 1":
                "Nhận biết được một số vấn đề cơ bản về bản quyền và giấy phép.",

            "Mức 2":
                "Sử dụng và chia sẻ nội dung số phù hợp với quy định về bản quyền.",

            "Mức 3":
                "Hướng dẫn và kiểm soát việc sử dụng nội dung số theo quy định.",
        },

        "3.4. Lập trình và tư duy tính toán": {

            "Mức 1":
                "Nhận biết được một số khái niệm và quy trình lập trình cơ bản.",

            "Mức 2":
                "Sử dụng được tư duy thuật toán và công cụ lập trình phù hợp.",

            "Mức 3":
                "Thiết kế, phát triển và đánh giá được giải pháp số "
                "hoặc chương trình.",
        },
    },


    "4. An toàn trong môi trường số": {

        "4.1. Bảo vệ thiết bị": {

            "Mức 1":
                "Nhận biết được một số nguy cơ đối với thiết bị số.",

            "Mức 2":
                "Thực hiện được các biện pháp bảo vệ thiết bị và dữ liệu.",

            "Mức 3":
                "Tổ chức và hướng dẫn các biện pháp bảo đảm an toàn thiết bị.",
        },

        "4.2. Bảo vệ dữ liệu cá nhân và quyền riêng tư": {

            "Mức 1":
                "Nhận biết được thông tin cá nhân và nguy cơ mất an toàn dữ liệu.",

            "Mức 2":
                "Áp dụng được các biện pháp bảo vệ dữ liệu cá nhân "
                "và quyền riêng tư.",

            "Mức 3":
                "Đánh giá và tổ chức được các biện pháp bảo vệ dữ liệu cá nhân.",
        },

        "4.3. Bảo vệ sức khỏe và an sinh số": {

            "Mức 1":
                "Nhận biết được một số nguy cơ ảnh hưởng đến sức khỏe "
                "khi sử dụng công nghệ.",

            "Mức 2":
                "Thực hiện được các biện pháp sử dụng công nghệ an toàn "
                "và cân bằng.",

            "Mức 3":
                "Hướng dẫn và hỗ trợ người học sử dụng công nghệ lành mạnh.",
        },

        "4.4. Bảo vệ môi trường": {

            "Mức 1":
                "Nhận biết được tác động cơ bản của công nghệ số đối với môi trường.",

            "Mức 2":
                "Thực hiện được các biện pháp sử dụng công nghệ tiết kiệm "
                "và thân thiện môi trường.",

            "Mức 3":
                "Đề xuất và triển khai được giải pháp sử dụng công nghệ số bền vững.",
        },
    },


    "5. Giải quyết vấn đề trong môi trường số": {

        "5.1. Giải quyết vấn đề kỹ thuật": {

            "Mức 1":
                "Nhận biết và xử lý được một số sự cố kỹ thuật đơn giản.",

            "Mức 2":
                "Phân tích và giải quyết được các vấn đề kỹ thuật thông thường.",

            "Mức 3":
                "Phân tích có hệ thống và đề xuất giải pháp "
                "cho các vấn đề kỹ thuật phức tạp.",
        },

        "5.2. Xác định nhu cầu và giải pháp công nghệ": {

            "Mức 1":
                "Nhận biết được nhu cầu sử dụng công nghệ trong tình huống đơn giản.",

            "Mức 2":
                "Lựa chọn được công cụ và giải pháp số phù hợp.",

            "Mức 3":
                "Thiết kế và đánh giá được giải pháp công nghệ "
                "phù hợp với nhu cầu.",
        },

        "5.3. Sáng tạo và sử dụng công nghệ một cách sáng tạo": {

            "Mức 1":
                "Sử dụng được công nghệ số để giải quyết nhiệm vụ đơn giản.",

            "Mức 2":
                "Vận dụng công nghệ số để giải quyết nhiệm vụ và tạo sản phẩm.",

            "Mức 3":
                "Sáng tạo và đổi mới trong việc sử dụng công nghệ số.",
        },

        "5.4. Xác định khoảng cách năng lực số": {

            "Mức 1":
                "Nhận biết được những hạn chế cơ bản về năng lực số của bản thân.",

            "Mức 2":
                "Xác định được nhu cầu học tập và phát triển năng lực số.",

            "Mức 3":
                "Xây dựng và thực hiện được kế hoạch phát triển năng lực số.",
        },
    },


    "6. Sử dụng trí tuệ nhân tạo": {

        "6.1. Hiểu biết về trí tuệ nhân tạo": {

            "Mức 1":
                "Nhận biết được khái niệm, khả năng và một số hạn chế cơ bản của AI.",

            "Mức 2":
                "Giải thích được vai trò, khả năng, giới hạn và rủi ro của AI.",

            "Mức 3":
                "Đánh giá được tác động của AI đối với hoạt động giáo dục và xã hội.",
        },

        "6.2. Sử dụng trí tuệ nhân tạo": {

            "Mức 1":
                "Sử dụng được công cụ AI đơn giản với sự hướng dẫn.",

            "Mức 2":
                "Sử dụng AI để hỗ trợ học tập, dạy học và giải quyết nhiệm vụ.",

            "Mức 3":
                "Thiết kế, điều phối và đánh giá việc sử dụng AI trong giáo dục.",
        },

        "6.3. Đánh giá và sử dụng AI có trách nhiệm": {

            "Mức 1":
                "Nhận biết được nguy cơ sai lệch, sai sót và rủi ro khi sử dụng AI.",

            "Mức 2":
                "Kiểm chứng, đánh giá và sử dụng có trách nhiệm nội dung do AI tạo ra.",

            "Mức 3":
                "Xây dựng và tổ chức được quy trình sử dụng AI an toàn, "
                "có đạo đức và phù hợp với mục tiêu giáo dục.",
        },
    },
}


# ============================================================
# 3. SESSION STATE
# ============================================================

def init_session_state():

    defaults = {

        "khbd_soan_mode": "chinh_sua",

        "khbd_hoat_dong_list": [],

        "khbd_nls_list": [],

        "khbd_ket_qua": None,

        "khbd_file_template": None,

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


# ============================================================
# 4. HÀM HỖ TRỢ
# ============================================================

def safe_text(value):

    if value is None:

        return ""

    return str(value).replace("\x00", "").strip()


def normalize_ai_result(result):

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


def add_hoat_dong():

    value = st.session_state.get(
        "khbd_new_hoat_dong",
        ""
    ).strip()

    if value:

        if value not in st.session_state.khbd_hoat_dong_list:

            st.session_state.khbd_hoat_dong_list.append(value)

    st.session_state.khbd_new_hoat_dong = ""


def add_nls():

    linh_vuc = st.session_state.get(
        "khbd_nls_linh_vuc",
        ""
    )

    thanh_phan = st.session_state.get(
        "khbd_nls_thanh_phan",
        ""
    )

    muc_do = st.session_state.get(
        "khbd_nls_muc_do",
        ""
    )

    noi_dung = st.session_state.get(
        "khbd_nls_noi_dung",
        ""
    ).strip()

    if not noi_dung:

        return

    item = {

        "van_ban": THONG_TU_NLS["so"],

        "linh_vuc": linh_vuc,

        "thanh_phan": thanh_phan,

        "muc_do": muc_do,

        "noi_dung": noi_dung,
    }

    if item not in st.session_state.khbd_nls_list:

        st.session_state.khbd_nls_list.append(item)

    st.session_state.khbd_nls_noi_dung = ""


# ============================================================
# 5. ĐỌC PDF
# ============================================================

def doc_pdf(uploaded_file):

    result = []

    reader = PyPDF2.PdfReader(uploaded_file)

    for index, page in enumerate(
        reader.pages,
        start=1
    ):

        try:

            text = page.extract_text() or ""

        except Exception:

            text = ""

        if text.strip():

            result.append(
                f"\n===== PDF - TRANG {index} =====\n"
                f"{text.strip()}"
            )

    return "\n".join(result)


# ============================================================
# 6. ĐỌC DOCX
# ============================================================

def doc_docx(uploaded_file):

    result = []

    document = Document(uploaded_file)

    for index, paragraph in enumerate(
        document.paragraphs,
        start=1
    ):

        text = safe_text(
            paragraph.text
        )

        if text:

            result.append(
                f"[ĐOẠN {index}] {text}"
            )

    for table_index, table in enumerate(
        document.tables,
        start=1
    ):

        result.append(
            f"\n===== BẢNG WORD {table_index} ====="
        )

        for row in table.rows:

            cells = []

            for cell in row.cells:

                cells.append(
                    safe_text(
                        cell.text
                    ).replace(
                        "\n",
                        " "
                    )
                )

            result.append(
                " | ".join(cells)
            )

    return "\n".join(result)


# ============================================================
# 7. ĐỌC EXCEL
# ============================================================

def doc_excel(uploaded_file):

    result = []

    sheets = pd.read_excel(
        uploaded_file,
        sheet_name=None,
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


# ============================================================
# 8. OCR ẢNH
# ============================================================

def ocr_image(uploaded_file):

    try:

        import pytesseract

        from PIL import Image

        image = Image.open(
            uploaded_file
        )

        text = pytesseract.image_to_string(
            image,
            lang="vie+eng"
        )

        return text.strip()

    except ImportError:

        return (
            "[ẢNH: Chưa cài pytesseract. "
            "Có thể sử dụng AI Vision nếu AI Engine hỗ trợ.]"
        )

    except Exception as e:

        return f"[OCR lỗi: {str(e)}]"


# ============================================================
# 9. ĐỌC FILE TỔNG QUÁT
# ============================================================

def doc_noi_dung_file(
    uploaded_file,
    ai_engine=None
):

    if not uploaded_file:

        return ""

    try:

        file_name = uploaded_file.name.lower()

        ext = Path(
            file_name
        ).suffix.lower()

        if ext == ".pdf":

            return doc_pdf(
                uploaded_file
            )

        if ext == ".docx":

            return doc_docx(
                uploaded_file
            )

        if ext in [
            ".xlsx",
            ".xls",
        ]:

            return doc_excel(
                uploaded_file
            )

        if ext in [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        ]:

            return ocr_image(
                uploaded_file
            )

        return (
            f"[Không hỗ trợ định dạng: {ext}]"
        )

    except Exception as e:

        return (
            f"[LỖI ĐỌC FILE: {uploaded_file.name}]\n"
            f"{str(e)}"
        )


# ============================================================
# 10. GỌI AI ENGINE
# ============================================================

def ai_generate_text_safe(
    ai_engine,
    prompt
):

    if ai_engine is None:

        raise RuntimeError(
            "Chưa truyền AI Engine vào render_xd_khbd()."
        )

    errors = []

    if hasattr(
        ai_engine,
        "generate_text"
    ):

        try:

            result = ai_engine.generate_text(
                prompt
            )

            text = normalize_ai_result(
                result
            )

            if text:

                return text

        except Exception as e:

            errors.append(
                f"generate_text: {str(e)}"
            )

    if hasattr(
        ai_engine,
        "generate"
    ):

        try:

            result = ai_engine.generate(
                prompt
            )

            text = normalize_ai_result(
                result
            )

            if text:

                return text

        except Exception as e:

            errors.append(
                f"generate: {str(e)}"
            )

    raise RuntimeError(
        "AI Engine không thể tạo nội dung.\n"
        + "\n".join(errors)
    )


# ============================================================
# 11. NLS PROMPT
# ============================================================

def format_nls_prompt():

    items = st.session_state.get(
        "khbd_nls_list",
        []
    )

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
            f"""
NĂNG LỰC SỐ {index}
- Văn bản: {item["van_ban"]}
- Lĩnh vực: {item["linh_vuc"]}
- Thành phần: {item["thanh_phan"]}
- Mức độ: {item["muc_do"]}
- Yêu cầu cần đạt:
  {item["noi_dung"]}
"""
        )

    return "\n".join(result)


# ============================================================
# 12. TẠO PROMPT KHBD
# ============================================================

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
Phân tích và nâng cấp giáo án gốc được cung cấp.

YÊU CẦU:
- Giữ nguyên tên bài.
- Giữ nguyên phạm vi kiến thức.
- Giữ lại các hoạt động phù hợp trong giáo án gốc.
- Không tự ý đưa kiến thức ngoài tài liệu nguồn.
- Có thể sửa lỗi kiến thức, lỗi logic, lỗi sư phạm.
- Bổ sung chi tiết hoạt động giáo viên và học sinh.
"""

    else:

        nhiem_vu = """

NHIỆM VỤ:
Xây dựng Kế hoạch bài dạy mới dựa trực tiếp trên SGK/tài liệu nguồn.

YÊU CẦU:
- Chỉ sử dụng kiến thức có trong tài liệu nguồn.
- Không tự ý mở rộng sang bài khác.
- Không tự bịa số trang.
- Không tự thêm kiến thức không có trong tài liệu.
- Mọi hoạt động phải có mục tiêu, nhiệm vụ, sản phẩm và cách tổ chức.
"""

    prompt = f"""

BẠN LÀ CHUYÊN GIA XÂY DỰNG KẾ HOẠCH BÀI DẠY
THEO CHƯƠNG TRÌNH GDPT 2018 TẠI VIỆT NAM.

{nhiem_vu}

============================================================
I. THÔNG TIN BÀI DẠY
============================================================

{thong_tin_bai_day}

============================================================
II. NGUYÊN TẮC KIỂM SOÁT NGUỒN
============================================================

TÀI LIỆU NGUỒN LÀ NGUỒN KIẾN THỨC ƯU TIÊN CAO NHẤT.

Chỉ sử dụng kiến thức có căn cứ trong:

1. SGK hoặc tài liệu bài học.
2. Giáo án gốc.
3. Tài liệu PPCT.
4. Tài liệu bổ sung do giáo viên cung cấp.

Nếu tài liệu không đủ dữ kiện:

- Không được tự bịa.
- Không được tự gán số trang.
- Không được tự thêm kiến thức bài khác.

Nếu có mâu thuẫn:

1. Tài liệu bài học trực tiếp.
2. Giáo án gốc.
3. Tài liệu bổ sung.

============================================================
III. CẤU TRÚC KHBD
============================================================

A. MỤC TIÊU

1. Kiến thức.
2. Năng lực.
3. Phẩm chất.

B. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU.

C. TIẾN TRÌNH DẠY HỌC.

Mỗi hoạt động phải có:

1. Mục tiêu.
2. Nội dung.
3. Sản phẩm.
4. Tổ chức thực hiện.

Tổ chức thực hiện phải thể hiện:

- Chuyển giao nhiệm vụ.
- Thực hiện nhiệm vụ.
- Báo cáo, thảo luận.
- Kết luận, nhận định.

Phải viết cụ thể:

- Lời dẫn của giáo viên.
- Câu hỏi.
- Nhiệm vụ của học sinh.
- Sản phẩm học tập.
- Cách đánh giá.

Không viết chung chung như:

"GV hướng dẫn HS thực hiện nhiệm vụ."

============================================================
IV. NĂNG LỰC SỐ
============================================================

Văn bản:

{THONG_TU_NLS["so"]}

{nls_text}

Nếu có năng lực số:

- Gắn với hoạt động cụ thể.
- Mô tả thao tác số của học sinh.
- Xác định sản phẩm/minh chứng.
- Nêu cách đánh giá.

Không được tự đổi tên lĩnh vực.
Không được tự đổi tên thành phần.
Không được tự đổi mức độ.
Không được tạo năng lực số ngoài dữ liệu đã chọn.

============================================================
V. TÍCH HỢP AI
============================================================

{
" CÓ TÍCH HỢP AI.\n"
"Phải nêu rõ:\n"
"- Hoạt động sử dụng AI.\n"
"- Nhiệm vụ AI hỗ trợ.\n"
"- Cách học sinh kiểm chứng kết quả AI.\n"
"- Sản phẩm học tập.\n"
"- AI không được xem là nguồn chân lý tuyệt đối."
if tich_hop_ai
else
"KHÔNG TÍCH HỢP AI."
}

============================================================
VI. DẠY HỌC HÒA NHẬP
============================================================

{
f"Có học sinh thuộc nhóm: {dang_khuyet_tat}.\n"
"Phải điều chỉnh nhiệm vụ, phương tiện, thời gian hoặc cách thể hiện sản phẩm phù hợp."
if tich_hop_kt
else
"Không yêu cầu tích hợp dạy học hòa nhập."
}

============================================================
VII. HOẠT ĐỘNG GIÁO VIÊN YÊU CẦU
============================================================

{hoat_dong}

============================================================
VIII. FILE MẪU KHBD
============================================================

{noi_dung_mau or "Không có file mẫu riêng. Sử dụng cấu trúc KHBD theo Công văn 5512."}

============================================================
IX. PPCT
============================================================

{noi_dung_ppct or "Không có dữ liệu PPCT."}

============================================================
X. BẢNG TÍCH HỢP AI
============================================================

{noi_dung_ai_file or "Không có bảng tích hợp AI."}

============================================================
XI. TÀI LIỆU NGUỒN CỐT LÕI
============================================================

{noi_dung_chinh}

============================================================
XII. QUY TẮC CÔNG THỨC
============================================================

TUYỆT ĐỐI KHÔNG DÙNG LATEX.

Dùng Unicode hoặc văn bản thường.

ĐÚNG:

v = s/t
F = m.a
U = I.R
A = U.I.t
H₂O
CO₂
H₂SO₄
x²
√a
Δt

SAI:

\\frac{{s}}{{t}}
$E = mc^2$
\\[F = ma\\]

============================================================
XIII. NGÔN NGỮ ĐẦU RA
============================================================

Ngôn ngữ đầu ra:

{thong_tin_bai_day}

============================================================
XIV. QUY TẮC ĐẦU RA
============================================================

Chỉ trả về nội dung KHBD.

Không chào hỏi.
Không giải thích quá trình.
Không nói "dưới đây là".
Không thêm nhận xét ngoài giáo án.

Nội dung phải đầy đủ, chi tiết và có thể sử dụng trực tiếp trong dạy học.
"""

    return prompt


# ============================================================
# 13. XUẤT WORD
# ============================================================

def export_khbd_word(
    markdown_text,
    template_file=None
):

    if export_word is None:

        raise RuntimeError(
            "Không import được export.export_word.export_word."
        )

    try:

        return export_word(
            markdown_text=markdown_text,
            template_file=template_file,
        )

    except TypeError:

        try:

            return export_word(
                markdown_text,
                template_file
            )

        except TypeError:

            return export_word(
                markdown_text
            )


# ============================================================
# 14. GIAO DIỆN CHÍNH
# ============================================================

def render_xd_khbd(
    ai_engine=None
):

    init_session_state()

    st.markdown(
        """
        <style>

        .khbd-title {
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 10px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="khbd-title">📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # THÔNG TIN BÀI DẠY
    # ========================================================

    st.markdown("### 🎛️ THÔNG TIN BÀI DẠY")

    col1, col2 = st.columns(2)

    with col1:

        st.selectbox(
            "Khối lớp",
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
            "Môn học",
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

    # ========================================================
    # CHẾ ĐỘ SOẠN
    # ========================================================

    st.markdown("### ✨ CHẾ ĐỘ SOẠN")

    mode = st.radio(
        "Chọn chế độ",
        [
            "📄 Chỉnh sửa giáo án gốc",
            "⚡ Tự động soạn từ SGK",
        ],
        horizontal=True,
        key="khbd_mode_radio"
    )

    if mode.startswith("📄"):

        st.session_state.khbd_soan_mode = "chinh_sua"

    else:

        st.session_state.khbd_soan_mode = "tu_dong"

    # ========================================================
    # TÍCH HỢP
    # ========================================================

    st.markdown("### 🔧 TÍCH HỢP")

    c1, c2, c3 = st.columns(3)

    with c1:

        tich_hop_nls = st.checkbox(
            "🎯 Năng lực số",
            key="khbd_chk_nls"
        )

    with c2:

        tich_hop_ai = st.checkbox(
            "🤖 Tích hợp AI",
            key="khbd_chk_ai"
        )

    with c3:

        tich_hop_kt = st.checkbox(
            "♿ Dạy học hòa nhập",
            key="khbd_chk_kt"
        )

    # ========================================================
    # THÔNG TIN TỰ ĐỘNG SOẠN
    # ========================================================

    file_sgk = []

    file_ga = []

    file_ppct = None

    file_ai = None

    file_template_custom = None

    if st.session_state.khbd_soan_mode == "chinh_sua":

        st.markdown("### 📤 TÀI LIỆU ĐẦU VÀO")

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
            key="khbd_file_ga"
        )

        file_ppct = st.file_uploader(
            "📊 PPCT",
            type=[
                "pdf",
                "docx",
                "xlsx",
                "xls",
            ],
            key="khbd_file_ppct"
        )

        file_ai = st.file_uploader(
            "🤖 Bảng tích hợp AI",
            type=[
                "pdf",
                "docx",
                "xlsx",
                "xls",
            ],
            key="khbd_file_ai"
        )

        file_template_custom = st.file_uploader(
            "📄 File mẫu giáo án DOCX",
            type=["docx"],
            key="khbd_template_custom"
        )

    else:

        st.markdown("### 📘 THÔNG TIN SOẠN MỚI")

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
            "📘 SGK / tài liệu bài học",
            type=[
                "pdf",
                "jpg",
                "jpeg",
                "png",
                "webp",
                "docx",
            ],
            accept_multiple_files=True,
            key="khbd_file_sgk"
        )

        file_template_custom = st.file_uploader(
            "📄 File mẫu giáo án DOCX của trường",
            type=["docx"],
            key="khbd_template_custom_auto"
        )

        if tich_hop_nls:

            file_ppct = st.file_uploader(
                "📊 PPCT",
                type=[
                    "pdf",
                    "docx",
                    "xlsx",
                    "xls",
                ],
                key="khbd_file_ppct_auto"
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
                key="khbd_file_ai_auto"
            )

    # ========================================================
    # HOẠT ĐỘNG GIÁO VIÊN
    # ========================================================

    st.markdown("### 📌 HOẠT ĐỘNG GIÁO VIÊN MONG MUỐN")

    c1, c2 = st.columns([5, 1])

    with c1:

        st.text_input(
            "Hoạt động",
            placeholder="VD: Thí nghiệm, trò chơi, mô phỏng...",
            key="khbd_new_hoat_dong",
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

    for index, item in enumerate(
        st.session_state.khbd_hoat_dong_list
    ):

        c1, c2 = st.columns([10, 1])

        with c1:

            st.info(
                f"📍 {item}"
            )

        with c2:

            if st.button(
                "Xóa",
                key=f"khbd_delete_hd_{index}"
            ):

                st.session_state.khbd_hoat_dong_list.pop(
                    index
                )

                st.rerun()

    # ========================================================
    # NĂNG LỰC SỐ
    # ========================================================

    if tich_hop_nls:

        st.markdown(
            f"### 🎯 NĂNG LỰC SỐ - {THONG_TU_NLS['so']}"
        )

        st.caption(
            THONG_TU_NLS["ten"]
        )

        linh_vuc = st.selectbox(
            "1. Lĩnh vực",
            list(
                KHUNG_NLS_TT18_2026.keys()
            ),
            key="khbd_nls_linh_vuc"
        )

        thanh_phan = st.selectbox(
            "2. Thành phần",
            list(
                KHUNG_NLS_TT18_2026[
                    linh_vuc
                ].keys()
            ),
            key="khbd_nls_thanh_phan"
        )

        muc_do = st.selectbox(
            "3. Mức độ",
            list(
                KHUNG_NLS_TT18_2026[
                    linh_vuc
                ][
                    thanh_phan
                ].keys()
            ),
            key="khbd_nls_muc_do"
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
            "4. Yêu cầu cần đạt",
            value=noi_dung_mac_dinh,
            key="khbd_nls_noi_dung",
            height=130
        )

        st.button(
            "➕ THÊM NĂNG LỰC SỐ",
            type="primary",
            use_container_width=True,
            on_click=add_nls
        )

        for index, item in enumerate(
            st.session_state.khbd_nls_list
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    f"""
**{index + 1}. {item["linh_vuc"]}**

**Thành phần:** {item["thanh_phan"]}

**Mức độ:** {item["muc_do"]}

**Yêu cầu cần đạt:** {item["noi_dung"]}
"""
                )

                if st.button(
                    "Xóa",
                    key=f"khbd_delete_nls_{index}"
                ):

                    st.session_state.khbd_nls_list.pop(
                        index
                    )

                    st.rerun()

    # ========================================================
    # DẠY HỌC HÒA NHẬP
    # ========================================================

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
            key="khbd_dang_khuyet_tat"
        )

    # ========================================================
    # NGÔN NGỮ
    # ========================================================

    ngon_ngu_anh = st.checkbox(
        "🌐 Giáo án viết bằng Tiếng Anh",
        key="khbd_ngon_ngu_anh"
    )

    # ========================================================
    # NÚT TẠO KHBD
    # ========================================================

    st.divider()

    if st.button(
        "⚡ KÍCH HOẠT XỬ LÝ AI",
        type="primary",
        use_container_width=True
    ):

        if ai_engine is None:

            st.error(
                "❌ Chưa truyền AI Engine vào render_xd_khbd()."
            )

            return

        if (
            st.session_state.khbd_soan_mode
            == "chinh_sua"
            and not file_ga
        ):

            st.error(
                "⚠️ Vui lòng tải lên giáo án gốc."
            )

            return

        if (
            st.session_state.khbd_soan_mode
            == "tu_dong"
            and not file_sgk
        ):

            st.error(
                "⚠️ Vui lòng tải lên SGK hoặc tài liệu bài học."
            )

            return

        with st.spinner(
            "🧠 AI đang phân tích tài liệu và xây dựng KHBD..."
        ):

            try:

                # ------------------------------------------------
                # ĐỌC TÀI LIỆU CHÍNH
                # ------------------------------------------------

                noi_dung_chinh = ""

                if (
                    st.session_state.khbd_soan_mode
                    == "chinh_sua"
                ):

                    for file in file_ga:

                        noi_dung_chinh += (
                            f"\n\n===== GIÁO ÁN GỐC: "
                            f"{file.name} =====\n"
                        )

                        noi_dung_chinh += (
                            doc_noi_dung_file(
                                file,
                                ai_engine
                            )
                        )

                else:

                    for file in file_sgk:

                        noi_dung_chinh += (
                            f"\n\n===== SGK / TÀI LIỆU: "
                            f"{file.name} =====\n"
                        )

                        noi_dung_chinh += (
                            doc_noi_dung_file(
                                file,
                                ai_engine
                            )
                        )

                # ------------------------------------------------
                # ĐỌC PPCT
                # ------------------------------------------------

                noi_dung_ppct = ""

                if file_ppct:

                    noi_dung_ppct = (
                        doc_noi_dung_file(
                            file_ppct,
                            ai_engine
                        )
                    )

                # ------------------------------------------------
                # ĐỌC FILE AI
                # ------------------------------------------------

                noi_dung_ai_file = ""

                if file_ai:

                    noi_dung_ai_file = (
                        doc_noi_dung_file(
                            file_ai,
                            ai_engine
                        )
                    )

                # ------------------------------------------------
                # ĐỌC FILE MẪU
                # ------------------------------------------------

                noi_dung_mau = ""

                if file_template_custom:

                    noi_dung_mau = (
                        doc_noi_dung_file(
                            file_template_custom,
                            ai_engine
                        )
                    )

                # ------------------------------------------------
                # GIỚI HẠN KÍCH THƯỚC
                # ------------------------------------------------

                max_chars = 120000

                if len(noi_dung_chinh) > max_chars:

                    noi_dung_chinh = (
                        noi_dung_chinh[:max_chars]
                        + "\n[ĐÃ CẮT PHẦN VƯỢT GIỚI HẠN]"
                    )

                    st.warning(
                        "⚠️ Tài liệu chính quá dài. "
                        "Hệ thống đã cắt phần vượt giới hạn."
                    )

                # ------------------------------------------------
                # THÔNG TIN BÀI DẠY
                # ------------------------------------------------

                thong_tin_bai_day = f"""

- Cấp học: {st.session_state.get("khbd_cap_hoc", "THCS")}
- Khối lớp: {st.session_state.get("khbd_khoi_lop", "Không xác định")}
- Môn học: {st.session_state.get("khbd_mon_hoc", "Không xác định")}
- Tên bài dạy: {st.session_state.get("khbd_ten_bai", "Theo tài liệu nguồn")}
- Thời lượng: {st.session_state.get("khbd_so_tiet", "1 tiết")}
- Mẫu giáo án: {st.session_state.get("khbd_mau_giao_an", "Công văn 5512")}
- Ngôn ngữ đầu ra: {"Tiếng Anh" if ngon_ngu_anh else "Tiếng Việt"}
"""

                nls_text = format_nls_prompt()

                hoat_dong = "\n".join(
                    st.session_state.khbd_hoat_dong_list
                )

                if not hoat_dong:

                    hoat_dong = "Không có yêu cầu riêng."

                # ------------------------------------------------
                # TẠO PROMPT
                # ------------------------------------------------

                prompt = build_khbd_prompt(

                    mode=st.session_state.khbd_soan_mode,

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

                # ------------------------------------------------
                # GỌI AI DUY NHẤT
                # ------------------------------------------------

                ket_qua = ai_generate_text_safe(
                    ai_engine,
                    prompt
                )

                if not ket_qua:

                    st.error(
                        "❌ AI không trả về nội dung."
                    )

                    return

                st.session_state.khbd_ket_qua = ket_qua

                st.success(
                    "🎉 Đã xây dựng KHBD thành công."
                )

            except Exception as e:

                st.error(
                    f"❌ Lỗi xử lý KHBD: {str(e)}"
                )

    # ========================================================
    # HIỂN THỊ KẾT QUẢ
    # ========================================================

    ket_qua = st.session_state.get(
        "khbd_ket_qua"
    )

    if ket_qua:

        st.markdown(
            "### 📝 KẾT QUẢ KHBD"
        )

        with st.container(
            border=True
        ):

            st.markdown(
                ket_qua
            )

        st.divider()

        # ====================================================
        # XUẤT WORD
        # ====================================================

        try:

            word_data = export_khbd_word(
                markdown_text=ket_qua,
                template_file=file_template_custom
            )

            st.download_button(
                "📥 TẢI KHBD WORD",
                data=word_data,
                file_name="KHBD_Thong_Minh.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"❌ Lỗi xuất Word: {str(e)}"
            )
