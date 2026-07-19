# -*- coding: utf-8 -*-

import streamlit as st
import streamlit.components.v1 as components
import re
from datetime import datetime


PHET_URL = "https://phet.colorado.edu/vi/"

MOZAWEB_URL = (
    "https://mozaweb.vn/vi/lexikon.php"
    "?cmd=getlist&let=3D&sid=BIO"
)


def _extract_html_code(text):

    if not text:
        return ""

    match = re.search(
        r"```(?:html)?\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        code = match.group(1).strip()
    else:
        code = text.strip()

    html_start = code.lower().find("<!doctype html>")

    if html_start == -1:
        html_start = code.lower().find("<html")

    if html_start >= 0:
        code = code[html_start:]

    return code.strip()


def _is_valid_html(code):

    if not code:
        return False

    code_lower = code.lower()

    return (
        "<html" in code_lower
        or "<!doctype html>" in code_lower
    )


def _get_current_code():

    return st.session_state.get(
        "mo_phong_code",
        ""
    )


def _build_scenario_prompt(
    ten_mo_phong,
    mon_hoc,
    khoi_lop,
    muc_tieu,
    bien_so,
    yeu_cau
):

    return f"""
Bạn là chuyên gia thiết kế mô phỏng khoa học
và giáo dục STEM cho học sinh THCS.

Hãy xây dựng một kịch bản mô phỏng tương tác.

Tên mô phỏng:
{ten_mo_phong}

Môn học:
{mon_hoc}

Khối lớp:
{khoi_lop}

Mục tiêu giáo dục:
{muc_tieu}

Các đại lượng hoặc biến số cần điều chỉnh:
{bien_so}

Yêu cầu bổ sung:
{yeu_cau}

Hãy trình bày:

1. Tên mô phỏng
2. Mục tiêu học tập
3. Hiện tượng khoa học
4. Cơ sở lý thuyết
5. Các biến số đầu vào
6. Các đại lượng đầu ra
7. Công thức khoa học
8. Kịch bản tương tác
9. Hoạt động của học sinh
10. Câu hỏi khám phá
11. Câu hỏi vận dụng
12. Gợi ý mở rộng

Nội dung phải phù hợp với học sinh THCS,
chính xác về mặt khoa học và có thể chuyển
thành mô phỏng HTML/JavaScript.
"""


def _build_code_prompt(
    ten_mo_phong,
    mon_hoc,
    khoi_lop,
    scenario,
    yeu_cau
):

    return f"""
Bạn là chuyên gia lập trình mô phỏng khoa học
cho giáo dục THCS.

Hãy tạo một mô phỏng tương tác hoàn chỉnh.

Tên mô phỏng:
{ten_mo_phong}

Môn học:
{mon_hoc}

Khối lớp:
{khoi_lop}

Kịch bản:
{scenario}

Yêu cầu:
{yeu_cau}

YÊU CẦU KỸ THUẬT:

1. Chỉ trả về một file HTML hoàn chỉnh.

2. Bao gồm đầy đủ HTML, CSS và JavaScript.

3. Không sử dụng backend.

4. Không sử dụng API Key.

5. Không phụ thuộc vào server bên ngoài.

6. Có giao diện tiếng Việt.

7. Có các điều khiển tương tác.

8. Có slider hoặc input.

9. Hiển thị kết quả theo thời gian thực.

10. Có nút Bắt đầu.

11. Có nút Tạm dừng.

12. Có nút Đặt lại.

13. Hiển thị công thức khoa học.

14. Có phần giải thích hiện tượng.

15. Có câu hỏi khám phá.

16. Chạy được khi lưu thành file .html.

CHỈ TRẢ VỀ MÃ HTML.
KHÔNG GIẢI THÍCH NGOÀI MÃ.
"""


def _build_fix_prompt(
    code,
    error_description
):

    return f"""
Bạn là chuyên gia sửa lỗi mã mô phỏng HTML.

MÃ HIỆN TẠI:

```html
{code}
