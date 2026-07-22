# -*- coding: utf-8 -*-

# """

DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY
KIẾN TRÚC 5512 - PHÂN TÍCH SGK - SOẠN THEO SỐ TIẾT
FILE: views/xd_khbd_data.py
===========================

"""

import os
import re
import json
from pathlib import Path
from io import BytesIO

import streamlit as st
import pandas as pd
import PyPDF2

from docx import Document

# ============================================================

# 1. CẤU HÌNH

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
"bảng tương tác và ứng dụng giáo dục đơn giản."
),
"Thành thạo": (
"Lựa chọn, tích hợp học liệu số vào kế hoạch hoạt động "
"và thiết kế hoạt động học tập tương tác."
),
"Nâng cao": (
"Sáng tạo mô hình giáo dục ứng dụng công nghệ mới "
"và hướng dẫn đồng nghiệp sử dụng thiết bị số."
),
},
"1.2. Hướng dẫn, hỗ trợ học tập": {
"Cơ bản": (
"Hướng dẫn học sinh thao tác cơ bản, an toàn "
"trên thiết bị số có giám sát."
),
"Thành thạo": (
"Quan sát, hỗ trợ kịp thời khi học sinh gặp khó khăn "
"trong tương tác với công nghệ."
),
"Nâng cao": (
"Phát triển phương pháp hỗ trợ học tập "
"trên nền tảng công nghệ tại nhà."
),
},
},
"2. Miền 2: Kiểm tra, đánh giá": {
"2.1. Phương thức đánh giá": {
"Cơ bản": (
"Sử dụng thiết bị số ghi lại sản phẩm "
"hoặc khoảnh khắc học tập của học sinh."
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
"Sử dụng công cụ AI tạo sinh cơ bản "
"hỗ trợ soạn thảo và tìm kiếm ý tưởng."
),
"Thành thạo": (
"Khai thác công cụ AI chuyên biệt để tạo học liệu "
"tương tác và cá nhân hóa."
),
},
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
},
},
}

# ============================================================

# 3. API NĂNG LỰC SỐ

# ============================================================

def get_nls_framework(loai_khung):
if loai_khung == "Giáo viên (Thông tư 18)":
return KHUNG_NLS_GV

```
return KHUNG_NLS_HS
```

def get_nls_domains(loai_khung):
return list(get_nls_framework(loai_khung).keys())

def get_nls_components(loai_khung, linh_vuc):
framework = get_nls_framework(loai_khung)

```
if linh_vuc not in framework:
    return []

return list(framework[linh_vuc].keys())
```

def get_nls_levels(loai_khung, linh_vuc, thanh_phan):
framework = get_nls_framework(loai_khung)

```
if linh_vuc not in framework:
    return []

if thanh_phan not in framework[linh_vuc]:
    return []

return list(framework[linh_vuc][thanh_phan].keys())
```

def get_nls_content(
loai_khung,
linh_vuc,
thanh_phan,
muc_do,
):
try:
framework = get_nls_framework(loai_khung)

```
    return framework[
        linh_vuc
    ][
        thanh_phan
    ][
        muc_do
    ]

except Exception:
    return ""
```

# ============================================================

# 4. SESSION STATE

# ============================================================

def init_session_state():

```
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
```

def reset_ket_qua():

```
st.session_state["khbd_result"] = None
```

def reset_toan_bo_khbd():

```
st.session_state["khbd_result"] = None
st.session_state["khbd_nls_list"] = []
st.session_state["khbd_hoat_dong_list"] = []
st.session_state["khbd_nls_noi_dung"] = ""
st.session_state["khbd_mode"] = "tu_dong"
st.session_state["khbd_processing"] = False
```

def set_mode(mode):

```
if mode not in MODE_LABELS:

    raise ValueError(
        f"Chế độ soạn không hợp lệ: {mode}"
    )

st.session_state["khbd_mode"] = mode
```

# ============================================================

# 5. LÀM SẠCH VĂN BẢN

# ============================================================

def safe_text(value):

```
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
```

# ============================================================

# 6. ĐỌC PDF

# ============================================================

def _parse_page_range(range_str, total_pages):

```
start_page = 1
end_page = total_pages

if not range_str:

    return start_page, end_page

range_str = str(range_str).strip()

match = re.match(
    r"^\s*(\d+)\s*-\s*(\d+)\s*$",
    range_str,
)

if not match:

    return start_page, end_page

start_page = int(match.group(1))
end_page = int(match.group(2))

start_page = max(
    1,
    start_page,
)

end_page = min(
    total_pages,
    end_page,
)

if start_page > end_page:

    return 1, total_pages

return start_page, end_page
```

def read_pdf(uploaded_file, range_str=""):

```
result = []

try:

    if hasattr(uploaded_file, "seek"):

        uploaded_file.seek(0)

    reader = PyPDF2.PdfReader(
        uploaded_file
    )

    total_pages = len(
        reader.pages
    )

    start_page, end_page = _parse_page_range(
        range_str,
        total_pages,
    )

    for page_number in range(
        start_page,
        end_page + 1,
    ):

        page = reader.pages[
            page_number - 1
        ]

        text = page.extract_text()

        if not text:

            continue

        text = safe_text(text)

        if text:

            result.append(
                "\n[PDF - Trang {}]\n{}".format(
                    page_number,
                    text,
                )
            )

except Exception as exc:

    result.append(
        "[LỖI ĐỌC PDF: {}]".format(
            exc
        )
    )

return "\n".join(result)
```

# ============================================================

# 7. ĐỌC DOCX THEO ĐÚNG THỨ TỰ

# ============================================================

def read_docx_ordered(source):

```
result = []

try:

    if isinstance(
        source,
        (
            str,
            Path,
        ),
    ):

        document = Document(
            source
        )

    elif hasattr(
        source,
        "read",
    ):

        source.seek(0)

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

    from docx.text.paragraph import Paragraph
    from docx.table import Table

    for element in document.element.body:

        tag = element.tag

        if tag.endswith("}p"):

            paragraph = Paragraph(
                element,
                document,
            )

            text = safe_text(
                paragraph.text
            )

            if text:

                result.append(
                    text
                )

        elif tag.endswith("}tbl"):

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

                    cell_text = safe_text(
                        cell.text
                    ).replace(
                        "\n",
                        " ",
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

except Exception as exc:

    result.append(
        "[LỖI ĐỌC DOCX: {}]".format(
            exc
        )
    )

return "\n".join(result)
```

# ============================================================

# 8. ĐỌC EXCEL

# ============================================================

def read_excel_structured(uploaded_file):

```
result = []

try:

    if hasattr(
        uploaded_file,
        "seek",
    ):

        uploaded_file.seek(0)

    sheets = pd.read_excel(
        uploaded_file,
        sheet_name=None,
    )

    for sheet_name, dataframe in sheets.items():

        result.append(
            "\n[PHÂN PHỐI CHƯƠNG TRÌNH - SHEET: {}]".format(
                sheet_name
            )
        )

        dataframe = dataframe.fillna("")

        records = dataframe.to_dict(
            orient="records"
        )

        for index, record in enumerate(
            records,
            start=1,
        ):

            clean_record = {}

            for key, value in record.items():

                value_text = safe_text(
                    value
                )

                if value_text:

                    clean_record[
                        str(key).strip()
                    ] = value_text

            if clean_record:

                result.append(
                    "Dòng {}: {}".format(
                        index,
                        json.dumps(
                            clean_record,
                            ensure_ascii=False,
                        ),
                    )
                )

except Exception as exc:

    result.append(
        "[LỖI ĐỌC EXCEL: {}]".format(
            exc
        )
    )

return "\n".join(result)
```

# ============================================================

# 9. ĐỌC MỘT FILE

# ============================================================

def read_uploaded_file(
uploaded_file,
range_str="",
is_pdf_target=False,
):

```
if uploaded_file is None:

    return ""

filename = getattr(
    uploaded_file,
    "name",
    "file.docx",
)

extension = Path(
    filename
).suffix.lower()

try:

    if extension == ".pdf":

        if hasattr(
            uploaded_file,
            "seek",
        ):

            uploaded_file.seek(0)

        return read_pdf(
            uploaded_file,
            range_str if is_pdf_target else "",
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

    return ""

except Exception as exc:

    return (
        "[LỖI ĐỌC FILE: {}]".format(
            exc
        )
    )
```

# ============================================================

# 10. ĐỌC NHIỀU FILE

# ============================================================

def read_multiple_files(
files,
range_str="",
is_pdf_target=False,
):

```
if not files:

    return ""

result = []

for uploaded_file in files:

    filename = getattr(
        uploaded_file,
        "name",
        "Tài liệu",
    )

    result.append(
        "\n--- TÀI LIỆU NGUỒN: {} ---".format(
            filename
        )
    )

    content = read_uploaded_file(
        uploaded_file,
        range_str=range_str,
        is_pdf_target=is_pdf_target,
    )

    result.append(
        content
    )

return "\n".join(result)
```

# ============================================================

# 11. ĐỌC MẪU KHBD

# ============================================================

def read_template_local(
path="templates/KHBD_Mau.docx",
):

```
if not os.path.exists(path):

    return ""

try:

    with open(
        path,
        "rb",
    ) as file:

        return read_docx_ordered(
            file
        )

except Exception:

    return ""
```

# ============================================================

# 12. CALLBACK NĂNG LỰC SỐ

# ============================================================

def add_nls():

```
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
```

def format_nls():

```
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
        "{}. [{}] {} - Thành phần: {} ({}) : {}".format(
            index,
            item["van_ban"],
            item["linh_vuc"],
            item["thanh_phan"],
            item["muc_do"],
            item["noi_dung"],
        )
    )

return "\n".join(
    result
)
```

# ============================================================

# 13. CALLBACK HOẠT ĐỘNG

# ============================================================

def add_activity():

```
value = safe_text(
    st.session_state.get(
        "khbd_new_activity",
        "",
    )
)

if value and value not in st.session_state.khbd_hoat_dong_list:

    st.session_state.khbd_hoat_dong_list.append(
        value
    )

st.session_state.khbd_new_activity = ""
```

# ============================================================

# 14. LOAD TASK CONFIG

# ============================================================

def load_task_config():

```
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

            content = file.read().strip()

            if content:

                return content

    except Exception:

        pass

return (
    "BẠN LÀ CHUYÊN GIA SƯ PHẠM "
    "XÂY DỰNG KẾ HOẠCH BÀI DẠY "
    "THEO PHỤ LỤC 4 CÔNG VĂN 5512."
)
```

# ============================================================

# 15. CHUẨN HÓA KẾT QUẢ AI

# ============================================================

def normalize_ai_result(result):

```
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

    choices = result.get(
        "choices"
    )

    if choices:

        message = choices[0].get(
            "message",
            {},
        )

        content = message.get(
            "content"
        )

        if content:

            return str(
                content
            ).strip()

    candidates = result.get(
        "candidates"
    )

    if candidates:

        content = candidates[0].get(
            "content",
            {},
        )

        parts = content.get(
            "parts",
            [],
        )

        texts = []

        for part in parts:

            if isinstance(
                part,
                dict,
            ) and part.get(
                "text"
            ):

                texts.append(
                    str(
                        part["text"]
                    )
                )

        if texts:

            return "\n".join(
                texts
            ).strip()

    for key in (
        "text",
        "content",
        "response",
        "output",
        "answer",
    ):

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

                if isinstance(
                    item,
                    dict,
                ) and item.get(
                    "text"
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
```

# ============================================================

# 16. GỌI AI ENGINE

# ============================================================

def generate_ai(
ai_engine,
prompt,
):

```
if ai_engine is None:

    raise RuntimeError(
        "Chưa truyền AI Engine."
    )

if hasattr(
    ai_engine,
    "generate_text",
):

    result = ai_engine.generate_text(
        prompt
    )

    return normalize_ai_result(
        result
    )

if hasattr(
    ai_engine,
    "generate",
):

    result = ai_engine.generate(
        prompt
    )

    return normalize_ai_result(
        result
    )

raise RuntimeError(
    "AI Engine không có phương thức "
    "generate_text() hoặc generate()."
)
```

# ============================================================

# 17. KIỂM TRA KẾT QUẢ

# ============================================================

def validate_khbd_result(text):

```
if not text:

    return (
        False,
        "Nội dung trả về rỗng.",
    )

if len(
    text.strip()
) < 100:

    return (
        False,
        "Nội dung trả về quá ngắn.",
    )

upper_text = text.upper()

required_keywords = [
    "MỤC TIÊU",
    "THIẾT BỊ DẠY HỌC",
    "TIẾN TRÌNH DẠY HỌC",
]

for keyword in required_keywords:

    if keyword not in upper_text:

        return (
            False,
            "Thiếu phần bắt buộc: {}".format(
                keyword
            ),
        )

return (
    True,
    "Hợp lệ",
)
```

# ============================================================

# 18. BUILD PROMPT

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

```
if mode not in MODE_LABELS:

    raise ValueError(
        "Chế độ soạn không hợp lệ: {}".format(
            mode
        )
    )

task_config = load_task_config()

mode_text = MODE_LABELS[
    mode
]

if mode == "chinh_sua":

    source_label = (
        "GIÁO ÁN GỐC CẦN CHỈNH SỬA"
    )

    main_source = noi_dung_ga

else:

    source_label = (
        "NGUỒN KIẾN THỨC CHÍNH "
        "TỪ SGK / TÀI LIỆU BÀI HỌC"
    )

    main_source = noi_dung_chinh

if tich_hop_hoa_nhap and nhu_cau_hoa_nhap:

    inclusion_text = (
        "Có học sinh cần hỗ trợ: {}. "
        "Phải điều chỉnh nhiệm vụ, cách giao nhiệm vụ "
        "và sản phẩm học tập phù hợp."
    ).format(
        nhu_cau_hoa_nhap
    )

else:

    inclusion_text = (
        "Dạy học theo điều kiện lớp học đại trà."
    )

if tich_hop_ai:

    ai_integration = (
        "Có tích hợp công cụ AI trong hoạt động "
        "nhận thức của học sinh."
    )

else:

    ai_integration = (
        "Không bắt buộc tích hợp AI."
    )

additional_activity = safe_text(
    hoat_dong
)

if not additional_activity:

    additional_activity = (
        "Không có yêu cầu hoạt động bổ sung."
    )

# --------------------------------------------------------
# PROMPT ĐƯỢC GHÉP BẰNG CÁC MẢNH CHUỖI
# --------------------------------------------------------
# Không dùng f-string khổng lồ.
# Mục đích: tránh lỗi cú pháp do dấu ngoặc trong tài liệu.
# --------------------------------------------------------

prompt_parts = []

prompt_parts.append(
    task_config
)

prompt_parts.append(
    """
```

============================================================
THÔNG TIN BÀI DẠY
=================

{}
""".format(
thong_tin
)
)

```
prompt_parts.append(
    """
```

============================================================
CHẾ ĐỘ THỰC THI
===============

{}
""".format(
mode_text
)
)

```
prompt_parts.append(
    """
```

============================================================
NGUYÊN TẮC BẮT BUỘC VỀ SỐ TIẾT
==============================

Phải đọc chính xác thời lượng được giao trong phần thông tin bài dạy.

Nếu bài có 2 tiết:

* Phải có TIẾT 1 và TIẾT 2.

Nếu bài có 3 tiết:

* Phải có TIẾT 1, TIẾT 2 và TIẾT 3.

Nếu bài có 4 tiết:

* Phải có TIẾT 1, TIẾT 2, TIẾT 3 và TIẾT 4.

Không được viết một giáo án ngắn chung chung rồi gắn nhãn 4 tiết.

Mỗi tiết phải có:

1. Mục tiêu của tiết.
2. Nội dung kiến thức thực tế của tiết.
3. Hoạt động học tập cụ thể.
4. Sản phẩm học tập cụ thể.
5. Cách tổ chức thực hiện.
6. Kiểm tra, đánh giá phù hợp.

Phải phân bổ nội dung theo tiến trình thực tế của nguồn kiến thức.
"""
)

```
prompt_parts.append(
    """
```

============================================================
PHẠM VI KIẾN THỨC ĐƯỢC PHÉP SỬ DỤNG
===================================

Chỉ sử dụng kiến thức có trong nguồn chính bên dưới.

Không được tự bịa:

* khái niệm;
* công thức;
* số liệu;
* thí nghiệm;
* câu hỏi;
* ví dụ;
* kết luận;
* nội dung bài học.

Nếu nguồn không có đủ thông tin để kết luận một nội dung,
phải ghi rõ: "Nguồn tài liệu chưa cung cấp thông tin này".

Không được thay thế nội dung SGK bằng kiến thức chung chung.
"""
)

```
prompt_parts.append(
    """
```

============================================================
{}
==

{}
""".format(
source_label,
main_source
)
)

```
if noi_dung_ppct:

    prompt_parts.append(
        """
```

============================================================
PHÂN PHỐI CHƯƠNG TRÌNH
======================

{}
""".format(
noi_dung_ppct
)
)

```
if noi_dung_ai:

    prompt_parts.append(
        """
```

============================================================
TÀI LIỆU AI BỔ SUNG
===================

{}
""".format(
noi_dung_ai
)
)

```
prompt_parts.append(
    """
```

============================================================
YÊU CẦU TÍCH HỢP
================

Năng lực số:
{}

Tích hợp AI:
{}

Giáo dục hòa nhập:
{}

Hoạt động bổ sung:
{}
""".format(
nls,
ai_integration,
inclusion_text,
additional_activity,
)
)

```
prompt_parts.append(
    """
```

============================================================
CẤU TRÚC ĐẦU RA BẮT BUỘC
========================

# [TÊN BÀI HỌC]

## I. MỤC TIÊU

1. Về kiến thức:
2. Về năng lực:
3. Về phẩm chất:

## II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU

1. Đối với giáo viên:
2. Đối với học sinh:

## III. TIẾN TRÌNH DẠY HỌC

Phải chia rõ theo từng tiết.

Ví dụ với bài 4 tiết:

### TIẾT 1

#### Hoạt động 1: Khởi động

#### Hoạt động 2: Hình thành kiến thức

#### Hoạt động 3: Luyện tập

### TIẾT 2

#### Hoạt động 1: Khởi động

#### Hoạt động 2: Hình thành kiến thức

#### Hoạt động 3: Luyện tập

### TIẾT 3

#### Hoạt động 1: Khởi động

#### Hoạt động 2: Hình thành kiến thức

#### Hoạt động 3: Luyện tập

### TIẾT 4

#### Hoạt động 1: Khởi động

#### Hoạt động 2: Luyện tập

#### Hoạt động 3: Vận dụng

Mỗi hoạt động phải có:

* Mục tiêu:
* Nội dung:
* Sản phẩm:
* Tổ chức thực hiện:

  * Bước 1: Chuyển giao nhiệm vụ:
  * Bước 2: Thực hiện nhiệm vụ:
  * Bước 3: Báo cáo, thảo luận:
  * Bước 4: Kết luận, nhận định:

YÊU CẦU ĐẶC BIỆT:

Phần "Nội dung" phải chỉ rõ học sinh làm gì
với nội dung nào của SGK.

Phần "Sản phẩm" phải ghi kết quả cụ thể:

* câu trả lời;
* bảng kết quả;
* công thức;
* kết luận;
* sơ đồ;
* bản thiết kế;
* lời giải;
* kết quả thí nghiệm;

tùy đúng với nội dung nguồn.

Không được viết:
"Học sinh hoàn thành nhiệm vụ."

Không được viết:
"Học sinh hiểu bài."

Không được viết:
"Học sinh trả lời câu hỏi."

Phải nêu rõ câu trả lời hoặc sản phẩm cụ thể
mà học sinh cần tạo ra.

"""
)

```
if noi_dung_mau:

    prompt_parts.append(
        """
```

============================================================
MẪU KHBD THAM KHẢO
==================

{}
""".format(
noi_dung_mau
)
)

```
prompt_parts.append(
    """
```

============================================================
YÊU CẦU CUỐI CÙNG
=================

Chỉ trả về nội dung giáo án hoàn chỉnh bằng Markdown.

Không chào hỏi.

Không giải thích ngoài lề.

Không mô tả quá trình suy nghĩ.

Bắt đầu ngay bằng tiêu đề bài học.

Đảm bảo số lượng tiết trong giáo án
khớp với số tiết được giao.
"""
)

```
return "\n".join(
    prompt_parts
)
```
