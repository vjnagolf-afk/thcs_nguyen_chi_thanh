# -*- coding: utf-8 -*-

import streamlit as st
import streamlit.components.v1 as components
import re
import json
from datetime import datetime


# ============================================================
# CẤU HÌNH
# ============================================================

PHET_URL = "https://phet.colorado.edu/vi/"

MOZAWEB_URL = (
    "https://mozaweb.vn/vi/lexikon.php"
    "?cmd=getlist&let=3D&sid=BIO"
)


# ============================================================
# HÀM TIỆN ÍCH
# ============================================================

def _extract_html_code(text):

    if not text:
        return ""

    # Tìm code trong markdown code block
    match = re.search(
        r"```(?:html)?\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE
    )

    if match:

        code = match.group(1).strip()

    else:

        code = text.strip()

    # Nếu AI trả thêm nội dung trước/sau HTML
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


# ============================================================
# PROMPT XÂY DỰNG KỊCH BẢN
# ============================================================

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

THÔNG TIN:

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

Hãy trình bày theo cấu trúc:

1. TÊN MÔ PHỎNG

2. MỤC TIÊU HỌC TẬP

3. HIỆN TƯỢNG KHOA HỌC

4. CƠ SỞ LÝ THUYẾT

5. CÁC BIẾN SỐ ĐẦU VÀO

6. CÁC ĐẠI LƯỢNG ĐẦU RA

7. CÔNG THỨC KHOA HỌC

8. KỊCH BẢN TƯƠNG TÁC

9. CÁC BƯỚC HOẠT ĐỘNG CỦA HỌC SINH

10. CÂU HỎI KHÁM PHÁ

11. CÂU HỎI VẬN DỤNG

12. GỢI Ý MỞ RỘNG

Nội dung phải phù hợp với học sinh THCS,
chính xác về mặt khoa học và có thể chuyển
thành mô phỏng HTML/JavaScript.
"""


# ============================================================
# PROMPT SINH MÃ MÔ PHỎNG
# ============================================================

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

TÊN MÔ PHỎNG:
{ten_mo_phong}

MÔN HỌC:
{mon_hoc}

KHỐI LỚP:
{khoi_lop}

KỊCH BẢN:
{scenario}

YÊU CẦU:
{yeu_cau}

YÊU CẦU KỸ THUẬT BẮT BUỘC:

1. Chỉ trả về một file HTML hoàn chỉnh.

2. Bao gồm đầy đủ:
   - <!DOCTYPE html>
   - HTML
   - CSS
   - JavaScript

3. Không sử dụng backend.

4. Không sử dụng API Key.

5. Không phụ thuộc vào server bên ngoài.

6. Có giao diện tiếng Việt.

7. Có các điều khiển tương tác phù hợp.

8. Có slider hoặc input để thay đổi
   các đại lượng quan trọng.

9. Hiển thị kết quả theo thời gian thực.

10. Có nút:
    - Bắt đầu
    - Tạm dừng
    - Đặt lại

11. Hiển thị công thức khoa học.

12. Có phần giải thích hiện tượng.

13. Có câu hỏi khám phá.

14. Mã phải chạy được khi lưu thành file .html
    và mở bằng trình duyệt.

CHỈ TRẢ VỀ MÃ HTML.
KHÔNG GIẢI THÍCH NGOÀI MÃ.
"""


# ============================================================
# PROMPT KIỂM TRA / SỬA MÃ
# ============================================================

def _build_fix_prompt(
    code,
    error_description
):

    return f"""
Bạn là chuyên gia sửa lỗi mã mô phỏng HTML.

MÃ HIỆN TẠI:

```html
{code}
