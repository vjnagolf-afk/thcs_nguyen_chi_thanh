# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (KIẾN TRÚC ENTERPRISE & 5512)
FILE: views/xd_khbd_data.py
============================================================
"""

import streamlit as st
import os
import re
import json
import logging
import tempfile
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
# 1. HẰNG SỐ & CẤU HÌNH
# ============================================================
NLS_GV_VAN_BAN_MAC_DINH = "18/2026/TT-BGDĐT"

MODE_LABELS = {
    "chinh_sua": "Chỉnh sửa và nâng cấp giáo án gốc",
    "tao_moi": "Soạn mới hoàn toàn từ tài liệu SGK",
    "tu_dong": "Soạn mới hoàn toàn từ tài liệu SGK",
}

MIN_SOURCE_CHARS = 800
MIN_SOURCE_WORDS = 120

# ============================================================
# 2. KHUNG NĂNG LỰC SỐ (ĐẦY ĐỦ 6 MIỀN TT18 & DIGCOMP)
# ============================================================
KHUNG_NLS_GV = {
    "1. Miền 1: Tổ chức dạy học, giáo dục trong môi trường số": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "Sử dụng thiết bị cơ bản (máy tính, máy chiếu, bảng tương tác); Dùng ứng dụng di động giáo dục đơn giản; Quản lý thiết bị trong lớp học đảm bảo an toàn.",
            "Thành thạo": "Lựa chọn, tích hợp học liệu số vào kế hoạch hoạt động; Thiết kế hoạt động học tập, vui chơi có ứng dụng công nghệ; Xử lý sự cố thiết bị và kết nối cơ bản.",
            "Nâng cao": "Sáng tạo, thử nghiệm mô hình giáo dục ứng dụng công nghệ mới phù hợp lứa tuổi; Hướng dẫn đồng nghiệp cách sử dụng và quản lý thiết bị."
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": "Hướng dẫn học sinh thực hiện thao tác cơ bản, an toàn trên thiết bị số có giám sát; Giải đáp câu hỏi liên quan đến nội dung số.",
            "Thành thạo": "Quan sát, hỗ trợ kịp thời khi học sinh gặp khó khăn tương tác công nghệ; Tổ chức hoạt động gợi mở, khuyến khích tư duy khám phá dựa trên nội dung số.",
            "Nâng cao": "Phát triển phương pháp hỗ trợ học tập trên nền tảng công nghệ; Phối hợp phụ huynh hỗ trợ học sinh tại nhà; Đổi mới phương pháp tích hợp công cụ số."
        },
        "1.3. Cá nhân hóa người học": {
            "Cơ bản": "Nhận biết hứng thú của học sinh với hoạt động công nghệ; Lựa chọn học liệu số phù hợp với sở thích chung.",
            "Thành thạo": "Thiết kế tình huống ứng dụng công nghệ giải quyết vấn đề; Lựa chọn ứng dụng, trò chơi số theo mức độ phù hợp với từng nhóm học sinh; Cá nhân hóa học liệu.",
            "Nâng cao": "Sáng tạo giải pháp cá nhân hóa hoạt động giáo dục; Hướng dẫn đồng nghiệp ứng dụng công nghệ cá nhân hóa cho học sinh có nhu cầu đặc biệt."
        },
        "1.4. Học tập cộng tác": {
            "Cơ bản": "Sử dụng công cụ số đơn giản tổ chức hoạt động nhóm; Thiết kế nhiệm vụ, chia sẻ ý tưởng trên nền tảng số.",
            "Thành thạo": "Thiết kế nhiệm vụ cộng tác phức tạp, tích hợp đa dạng công cụ số; Hướng dẫn kĩ năng giao tiếp có sử dụng công nghệ trong nhóm.",
            "Nâng cao": "Sáng tạo mô hình học tập cộng tác ứng dụng nền tảng số; Xây dựng văn hóa hợp tác, chia sẻ trong tập thể sư phạm nhà trường."
        }
    },
    "2. Miền 2: Kiểm tra, đánh giá": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": "Sử dụng thiết bị số (máy ảnh, điện thoại) ghi lại sản phẩm/khoảnh khắc học tập; Dùng công cụ số lưu trữ minh chứng tiến bộ.",
            "Thành thạo": "Thiết kế hoạt động đánh giá kĩ năng qua công nghệ; Tổ chức giao tiếp hiệu quả với phụ huynh qua kênh số (gửi thông báo, chia sẻ minh chứng có chọn lọc).",
            "Nâng cao": "Sáng tạo, triển khai phương pháp đánh giá sự phát triển thông qua phân tích dữ liệu tương tác số; Hướng dẫn đồng nghiệp đánh giá dựa trên minh chứng số."
        },
        "2.2. Phân tích kết quả học tập": {
            "Cơ bản": "Sử dụng công cụ số cơ bản nhận xét, đánh giá; Lựa chọn, sắp xếp minh chứng số phù hợp theo từng lĩnh vực phát triển.",
            "Thành thạo": "Xây dựng hồ sơ số, báo cáo trực quan về sự tiến bộ của học sinh chia sẻ với phụ huynh; Phân tích dữ liệu đánh giá xu hướng cá nhân.",
            "Nâng cao": "Hướng dẫn đồng nghiệp cách khai thác và diễn giải dữ liệu số để cải tiến hoạt động chăm sóc, nuôi dưỡng và giáo dục."
        },
        "2.3. Phản hồi và đánh giá cải tiến": {
            "Cơ bản": "Sử dụng công cụ số cơ bản cung cấp phản hồi thông tin hằng ngày; Dùng đa dạng công cụ (ghi âm, video ngắn) nhận xét hoạt động.",
            "Thành thạo": "Thiết kế quy trình phản hồi và đánh giá cải tiến có sự tham gia của phụ huynh/học sinh bằng công nghệ; Tổ chức tương tác trực tuyến.",
            "Nâng cao": "Hướng dẫn đồng nghiệp sử dụng phản hồi số và dữ liệu học tập để cải tiến liên tục chương trình và hoạt động giáo dục."
        }
    },
    "3. Miền 3: Trao quyền cho người học": {
        "3.1. Tiếp cận và hòa nhập": {
            "Cơ bản": "Sử dụng thiết bị, công cụ số đảm bảo mọi học sinh đều có cơ hội tham gia; Hỗ trợ học sinh khuyết tật/nhu cầu đặc biệt ở mức cơ bản.",
            "Thành thạo": "Lựa chọn tài nguyên số tính đến sự đa dạng của học sinh; Sử dụng công nghệ hỗ trợ chuyên biệt và thiết kế hoạt động linh hoạt cho học sinh hòa nhập.",
            "Nâng cao": "Thiết kế hoạt động học tập số linh hoạt, đa dạng hóa cách tham gia; Hướng dẫn đồng nghiệp triển khai sáng kiến xóa bỏ rào cản giáo dục hòa nhập."
        },
        "3.2. Giải quyết vấn đề": {
            "Cơ bản": "Tổ chức hoạt động tìm kiếm thông tin đơn giản từ nội dung giáo viên cung cấp.",
            "Thành thạo": "Thiết kế hoạt động/dự án nhỏ yêu cầu sử dụng công nghệ tìm kiếm câu trả lời, khám phá dưới sự định hướng của giáo viên.",
            "Nâng cao": "Tổ chức hoạt động học tập dựa trên vấn đề, hiện tượng thực tiễn, khuyến khích dùng công cụ số nghiên cứu và trình bày giải pháp sáng tạo."
        },
        "3.3. Khuyến khích sự tham gia tích cực": {
            "Cơ bản": "Sử dụng công cụ số đơn giản, an toàn thu hút sự chú ý và tương tác của học sinh trong giờ học.",
            "Thành thạo": "Tích hợp yếu tố trò chơi hóa (gamification), công cụ sáng tạo số đơn giản để học sinh thể hiện ý tưởng cá nhân và sản phẩm số.",
            "Nâng cao": "Xây dựng môi trường tự tin, an toàn để học sinh thể hiện bản thân; Hướng dẫn đồng nghiệp phương pháp tăng cường tương tác bằng công nghệ."
        }
    },
    "4. Miền 4: Kĩ năng công nghệ số": {
        "4.1. Kĩ năng thông tin và dữ liệu": {
            "Cơ bản": "Sử dụng công cụ tìm kiếm cơ bản tìm thông tin phục vụ bài giảng; Lưu trữ và sắp xếp tệp tin trên máy tính hoặc đám mây.",
            "Thành thạo": "Khai thác kho học liệu số (video, bài hát, truyện, tài nguyên mở); Hướng dẫn học sinh tìm kiếm, đánh giá độ tin cậy nguồn thông tin an toàn.",
            "Nâng cao": "Phát triển năng lực thông tin nâng cao; Hướng dẫn đồng nghiệp phương pháp rèn luyện tư duy phản biện khi tiếp nhận thông tin số."
        },
        "4.2. Sáng tạo nội dung số": {
            "Cơ bản": "Sử dụng phần mềm soạn thảo văn bản, trình chiếu thiết kế giáo án; Tạo video, album ảnh đơn giản từ hoạt động lớp học.",
            "Thành thạo": "Sử dụng công cụ thiết kế, chỉnh sửa ảnh, video, âm thanh tạo học liệu trực quan, sinh động; Tổ chức kho học liệu cá nhân khoa học.",
            "Nâng cao": "Khai thác nền tảng tích hợp AI, thực tế ảo (VR/AR) để thiết kế học liệu số nâng cao; Hướng dẫn đồng nghiệp ứng dụng chuyên sâu."
        },
        "4.3. An toàn": {
            "Cơ bản": "Hiểu biết bảo vệ sức khỏe khi tiếp xúc thiết bị số; Đặt mật khẩu thiết bị/tài khoản cá nhân; Nhận diện rủi ro cơ bản trên mạng.",
            "Thành thạo": "Giám sát biện pháp đảm bảo an toàn cho học sinh khi dùng thiết bị; Cài đặt kiểm soát truy cập; Bảo vệ hình ảnh, thông tin cá nhân học sinh.",
            "Nâng cao": "Xử lí sự cố an ninh mạng cơ bản; Cập nhật, hướng dẫn đồng nghiệp và phụ huynh phương pháp giáo dục an toàn số."
        }
    },
    "5. Miền 5: Phát triển chuyên môn": {
        "5.1. Giao tiếp trong tổ chức": {
            "Cơ bản": "Sử dụng email, mạng xã hội, công cụ trực tuyến phổ biến của nhà trường để trao đổi thông tin công việc và giao tiếp với phụ huynh.",
            "Thành thạo": "Sử dụng hiệu quả kênh giao tiếp số chính thức của trường; Xây dựng, quản lí kênh truyền thông số của lớp kết nối tích cực.",
            "Nâng cao": "Hướng dẫn đồng nghiệp xây dựng kế hoạch truyền thông số, tăng cường minh bạch và tương tác hiệu quả với cộng đồng."
        },
        "5.2. Hợp tác phát triển chuyên môn": {
            "Cơ bản": "Tham gia cộng đồng học tập trực tuyến của giáo viên; Tự đánh giá thuận lợi, khó khăn khi ứng dụng công nghệ.",
            "Thành thạo": "Chủ động tìm kiếm, tham gia khóa học cập nhật kiến thức kĩ năng số; Áp dụng giải pháp công nghệ giải quyết vấn đề chuyên môn.",
            "Nâng cao": "Hướng dẫn đồng nghiệp sử dụng công nghệ số xây dựng kế hoạch phát triển năng lực cá nhân và đổi mới phương pháp."
        },
        "5.3. Phát triển, quản lí học liệu số": {
            "Cơ bản": "Lựa chọn tài nguyên số phù hợp mục tiêu giáo dục; Sử dụng nguồn tài nguyên hợp pháp, có bản quyền.",
            "Thành thạo": "Khai thác kho học liệu mở (OER); Tổ chức lưu trữ, chia sẻ kho học liệu số cá nhân an toàn; Đánh giá chất lượng và tính pháp lí.",
            "Nâng cao": "Xây dựng chính sách, hướng dẫn tôn trọng bản quyền trong nhà trường; Hướng dẫn đồng nghiệp quản trị kho học liệu."
        }
    },
    "6. Miền 6: Trí tuệ nhân tạo (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": "Hiểu biết về công cụ AI tạo sinh cơ bản và tiềm năng ứng dụng trong giáo dục; Sử dụng AI hỗ trợ công việc cơ bản.",
            "Thành thạo": "Khai thác công cụ AI chuyên biệt tạo học liệu tương tác, cá nhân hóa hoạt động học tập; Phòng chống rủi ro, đảm bảo đạo đức.",
            "Nâng cao": "Triển khai đổi mới phương pháp dạy học tích hợp sâu AI đáp ứng cá nhân hóa; Hướng dẫn đồng nghiệp lựa chọn công cụ AI phù hợp."
        },
        "6.2. Đạo đức AI": {
            "Cơ bản": "Nhận diện khả năng thu thập dữ liệu cá nhân của AI; Thể hiện cẩn trọng, trách nhiệm với quyền riêng tư của học sinh và gia đình.",
            "Thành thạo": "Giám sát học sinh tương tác với AI; Đánh giá ứng dụng AI dựa trên tiêu chí đạo đức, bảo mật, công bằng; Tích hợp hướng dẫn AI an toàn.",
            "Nâng cao": "Chủ động cập nhật, chia sẻ với đồng nghiệp vấn đề đạo đức AI; Tham gia xây dựng chính sách sử dụng AI có trách nhiệm."
        },
        "6.3. Sư phạm AI": {
            "Cơ bản": "Nhận biết tương tác 3 chiều (giáo viên - học sinh - AI) trong môi trường số; Nhận diện giới hạn của AI trong giáo dục.",
            "Thành thạo": "Sử dụng AI hỗ trợ giao tiếp, tổ chức hoạt động nhận thức; Khai thác ứng dụng AI thử nghiệm đổi mới tổ chức lớp học.",
            "Nâng cao": "Khai thác AI cải thiện chất lượng dạy học toàn diện; Hướng dẫn đồng nghiệp tổ chức hoạt động hợp tác trên nền tảng số."
        },
        "6.4. AI cho phát triển chuyên môn": {
            "Cơ bản": "Tìm kiếm, khai thác khóa học trực tuyến về AI phục vụ phát triển chuyên môn; Sẵn sàng thử nghiệm ứng dụng AI.",
            "Thành thạo": "Vận dụng tư duy phản biện xác định vấn đề phức tạp và đề xuất giải pháp AI phù hợp; Cá nhân hóa hoạt động phát triển bản thân.",
            "Nâng cao": "Hướng dẫn đồng nghiệp sáng kiến đổi mới áp dụng AI giải quyết vấn đề hệ thống; Đánh giá rủi ro và lợi ích dài hạn."
        }
    }
}

KHUNG_NLS_HS = {
    "1. Thông tin và dữ liệu số": {
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu": {
            "Mức 1": "Xác định nhu cầu thông tin, tìm kiếm dữ liệu đơn giản trong môi trường số.",
            "Mức 2": "Sử dụng kĩ thuật tìm kiếm nâng cao để lấy dữ liệu, thông tin chính xác.",
            "Mức 3": "Vận dụng chiến lược tìm kiếm và tổng hợp thông tin phức tạp phục vụ học tập."
        }
    },
    "2. Giao tiếp và hợp tác": {
        "2.1. Tương tác qua công nghệ số": {
            "Mức 1": "Sử dụng công cụ số cơ bản để giao tiếp, trao đổi học tập.",
            "Mức 2": "Lựa chọn nền tảng giao tiếp phù hợp với yêu cầu nhiệm vụ học tập nhóm.",
            "Mức 3": "Tổ chức và điều phối hiệu quả hoạt động giao tiếp, tương tác nhóm trực tuyến."
        }
    }
}

# ============================================================
# 3. API NĂNG LỰC SỐ
# ============================================================
def get_nls_framework(loai_khung):
    return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS

def get_nls_domains(loai_khung):
    return list(get_nls_framework(loai_khung).keys())

def get_nls_components(loai_khung, linh_vuc):
    framework = get_nls_framework(loai_khung)
    return list(framework.get(linh_vuc, {}).keys())

def get_nls_levels(loai_khung, linh_vuc, thanh_phan):
    framework = get_nls_framework(loai_khung)
    return list(framework.get(linh_vuc, {}).get(thanh_phan, {}).keys())

def get_nls_content(loai_khung, linh_vuc, thanh_phan, muc_do):
    framework = get_nls_framework(loai_khung)
    try:
        return framework[linh_vuc][thanh_phan][muc_do]
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
        raise ValueError(f"Chế độ soạn không hợp lệ: {mode}")
    st.session_state.khbd_mode = mode

# ============================================================
# 5. CHUẨN HÓA VĂN BẢN
# ============================================================
def safe_text(value):
    if value is None: return ""
    if not isinstance(value, str):
        value = str(value)
    text = value.replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = re.sub(r"[\r\t]+", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def normalize_source_text(text):
    text = safe_text(text)
    if not text: return ""
    text = re.sub(r"(?<![.!?:;])\n(?=[a-zà-ỹA-ZÀ-Ỹ0-9])", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def count_words(text):
    if not text: return 0
    return len(re.findall(r"\S+", text))

# ============================================================
# 6. CHẨN ĐOÁN CHẤT LƯỢNG TÀI LIỆU
# ============================================================
def diagnose_source_quality(text, source_name="Tài liệu nguồn"):
    text = safe_text(text)
    chars = len(text)
    words = count_words(text)
    has_error = "[LỖI ĐỌC" in text.upper()
    is_too_short = chars < MIN_SOURCE_CHARS or words < MIN_SOURCE_WORDS

    if has_error:
        status = "error"
        message = f"{source_name} có lỗi khi đọc."
    elif is_too_short:
        status = "insufficient"
        message = f"{source_name} không đủ dữ liệu."
    else:
        status = "valid"
        message = f"{source_name} đủ dữ liệu."

    return {
        "source_name": source_name,
        "chars": chars,
        "words": words,
        "status": status,
        "message": message,
    }

# ============================================================
# 7. ĐỌC PDF & DOCX & EXCEL
# ============================================================
def read_pdf(uploaded_file, range_str=""):
    result = []
    try:
        content = uploaded_file.read()
        reader = PyPDF2.PdfReader(BytesIO(content))
        total_pages = len(reader.pages)
        start, end = 1, total_pages

        if range_str and "-" in range_str:
            try:
                s, e = range_str.split("-")
                start = max(1, int(s.strip()))
                end = min(total_pages, int(e.strip()))
            except ValueError:
                pass

        for index in range(start, end + 1):
            page = reader.pages[index - 1]
            text = page.extract_text() or ""
            text = safe_text(text)
            if text:
                result.append(f"\n[PDF - Trang {index}]\n{text}")

        text_result = "\n".join(result)
        return normalize_source_text(text_result)
    except Exception as e:
        return f"[LỖI ĐỌC PDF: {str(e)}]"

def read_docx_ordered(source):
    result = []
    try:
        if isinstance(source, (str, Path)):
            doc = Document(source)
        elif hasattr(source, "read"):
            content = source.read()
            if isinstance(content, str):
                content = content.encode("utf-8")
            doc = Document(BytesIO(content))
        else:
            doc = Document(source)

        for element in doc.element.body:
            if element.tag.endswith('p') or element.tag.endswith('}p'):
                from docx.text.paragraph import Paragraph
                paragraph = Paragraph(element, doc)
                text = safe_text(paragraph.text)
                if text:
                    result.append(text)
            elif element.tag.endswith('tbl') or element.tag.endswith('}tbl'):
                from docx.table import Table
                table = Table(element, doc)
                result.append("\n[BẢNG DỮ LIỆU]")
                for row in table.rows:
                    cells = [safe_text(cell.text).replace("\n", " ") for cell in row.cells]
                    row_text = " | ".join(cells)
                    if row_text.strip():
                        result.append(row_text)
        return normalize_source_text("\n".join(result))
    except Exception as e:
        return f"[LỖI ĐỌC DOCX: {str(e)}]"

def read_excel_structured(uploaded_file):
    result = []
    try:
        sheets = pd.read_excel(uploaded_file, sheet_name=None)
        for sheet_name, dataframe in sheets.items():
            result.append(f"\n[PHÂN PHỐI CHƯƠNG TRÌNH - SHEET: {sheet_name}]")
            dataframe = dataframe.fillna("")
            records = dataframe.to_dict(orient="records")
            for idx, rec in enumerate(records, start=1):
                clean_rec = {}
                for key, value in rec.items():
                    k = safe_text(key)
                    v = safe_text(value)
                    if v:
                        clean_rec[k] = v
                if clean_rec:
                    result.append(f"Dòng {idx}: " + json.dumps(clean_rec, ensure_ascii=False))
        return normalize_source_text("\n".join(result))
    except Exception as e:
        return f"[LỖI ĐỌC EXCEL: {str(e)}]"

def read_uploaded_file(uploaded_file, range_str="", is_pdf_target=False):
    if uploaded_file is None: return ""
    filename = getattr(uploaded_file, "name", "file.docx").lower()
    extension = Path(filename).suffix.lower()
    try:
        if extension == ".pdf":
            return read_pdf(uploaded_file, range_str if is_pdf_target else "")
        if extension == ".docx":
            return read_docx_ordered(uploaded_file)
        if extension in [".xlsx", ".xls"]:
            return read_excel_structured(uploaded_file)
        return ""
    except Exception as e:
        return f"[LỖI ĐỌC FILE: {e}]"

def read_multiple_files(files, range_str="", is_pdf_target=False):
    result = []
    for uploaded_file in files or []:
        fname = getattr(uploaded_file, "name", "Tài liệu")
        result.append(f"\n--- TÀI LIỆU NGUỒN: {fname} ---")
        result.append(read_uploaded_file(uploaded_file, range_str, is_pdf_target))
    return normalize_source_text("\n".join(result))

def read_template_local(path="templates/KHBD_Mau.docx"):
    if not os.path.exists(path): return ""
    try:
        return read_docx_ordered(path)
    except Exception:
        return ""

# ============================================================
# 8. SESSION CALLBACKS
# ============================================================
def add_nls():
    linh_vuc = safe_text(st.session_state.get("khbd_nls_linh_vuc", ""))
    thanh_phan = safe_text(st.session_state.get("khbd_nls_thanh_phan", ""))
    muc_do = safe_text(st.session_state.get("khbd_nls_muc_do", ""))
    noi_dung = safe_text(st.session_state.get("khbd_nls_noi_dung", ""))
    if not noi_dung: return

    van_ban = NLS_GV_VAN_BAN_MAC_DINH if st.session_state.get("khbd_loai_khung_nls") == "Giáo viên (Thông tư 18)" else "DigComp"
    item = {
        "van_ban": van_ban,
        "linh_vuc": linh_vuc,
        "thanh_phan": thanh_phan,
        "muc_do": muc_do,
        "noi_dung": noi_dung,
    }
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

# ============================================================
# 9. AI ENGINE & VALIDATION & PROMPT BUILDER
# ============================================================
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
                message = result["choices"][0].get("message", {})
                content = message.get("content")
                if content: return str(content).strip()
        except Exception:
            pass
        try:
            if "candidates" in result and result["candidates"]:
                parts = result["candidates"][0].get("content", {}).get("parts", [])
                texts = []
                for part in parts:
                    if isinstance(part, dict) and part.get("text"):
                        texts.append(str(part["text"]))
                if texts: return "\n".join(texts).strip()
        except Exception:
            pass
        for key in ["text", "content", "response", "output", "answer"]:
            if key not in result: continue
            value = result[key]
            if isinstance(value, str): return value.strip()
    return str(result).strip()

def generate_ai(ai_engine, prompt):
    if ai_engine is None: raise RuntimeError("Chưa truyền AI Engine.")
    if hasattr(ai_engine, "generate_text"):
        return normalize_ai_result(ai_engine.generate_text(prompt))
    if hasattr(ai_engine, "generate"):
        return normalize_ai_result(ai_engine.generate(prompt))
    raise RuntimeError("AI Engine không phản hồi.")

def validate_khbd_result(text):
    text = safe_text(text)
    if len(text) < 1000:
        return False, "Nội dung giáo án quá ngắn."
    upper = text.upper()
    required_keywords = ["MỤC TIÊU", "THIẾT BỊ DẠY HỌC", "TIẾN TRÌNH DẠY HỌC"]
    for keyword in required_keywords:
        if keyword not in upper:
            return False, f"Thiếu phần bắt buộc: {keyword}"
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, noi_dung_ppct, noi_dung_ai, noi_dung_mau, nls, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, hoat_dong, mode):
    if mode not in MODE_LABELS:
        raise ValueError(f"Chế độ soạn không hợp lệ: {mode}")
    mode_text = MODE_LABELS[mode]

    source = safe_text(noi_dung_chinh)
    quality = diagnose_source_quality(source, "SGK")
    if quality["status"] != "valid":
        raise ValueError(f"Tài liệu nguồn không đủ dữ liệu để xây dựng giáo án.\nSố ký tự: {quality['chars']}\nSố từ: {quality['words']}")

    task_config = load_task_config()
    safe_ai = safe_text(noi_dung_ai)
    ai_block = f"\n------------------------------------------------------------\nTÀI LIỆU / HƯỚNG DẪN AI BỔ SUNG\n------------------------------------------------------------\n{safe_ai}\n" if safe_ai else ""

    safe_need = safe_text(nhu_cau_hoa_nhap)
    if tich_hop_hoa_nhap and safe_need:
        inclusion_block = f"Học sinh cần hỗ trợ hòa nhập: {safe_need}\nBắt buộc điều chỉnh trực tiếp trong từng hoạt động: Câu hỏi, Phiếu học tập, Thời gian, Mức độ nhiệm vụ."
    else:
        inclusion_block = "Không có yêu cầu hòa nhập đặc thù."

    safe_activity = safe_text(hoat_dong)
    activity_block = f"\n------------------------------------------------------------\nHOẠT ĐỘNG BỔ SUNG THEO YÊU CẦU GIÁO VIÊN\n------------------------------------------------------------\n{safe_activity}\n" if safe_activity else ""

    ga_block = ""
    if mode == "chinh_sua" and safe_text(noi_dung_ga):
        ga_block = f"\n------------------------------------------------------------\nGIÁO ÁN GỐC\n------------------------------------------------------------\nChỉ được kế thừa cấu trúc và các ý tưởng phù hợp.\n{safe_text(noi_dung_ga)}\n"

    return f"""
{task_config}

================================================================
VAI TRÒ & NHIỆM VỤ
================================================================
Bạn là chuyên gia xây dựng kế hoạch bài dạy theo Chương trình GDPT 2018 và cấu trúc Phụ lục 4 Công văn 5512.
Nhiệm vụ của bạn là xây dựng một giáo án CHI TIẾT, CỤ THỂ, BÁM SÁT 100% NỘI DUNG SGK.

================================================================
CHẾ ĐỘ & THÔNG TIN BÀI HỌC
================================================================
{mode_text}
Thông tin bài học và thời lượng:
{thong_tin}

================================================================
QUY TẮC PHÂN BỔ SỐ TIẾT (BẮT BUỘC)
================================================================
1. Nếu bài 1 tiết: Tiến trình chuẩn 1 tiết.
2. Nếu bài 2 tiết: Bắt buộc phân tách rõ: ### TIẾT 1 và ### TIẾT 2.
3. Nếu bài 3 tiết: Bắt buộc phân tách rõ: ### TIẾT 1, ### TIẾT 2, ### TIẾT 3.
4. Nếu bài 4 tiết: Bắt buộc phân tách rõ: ### TIẾT 1, ### TIẾT 2, ### TIẾT 3, ### TIẾT 4.
Không được viết chung chung. Mỗi tiết phải có đầy đủ hoạt động và nội dung cụ thể.

================================================================
KNOWLEDGE SCOPE (NGUỒN KIẾN THỨC CHÍNH DUY NHẤT)
================================================================
---------------- SGK / TÀI LIỆU BÀI HỌC ----------------
{source}
---------------- KẾT THÚC NGUỒN KIẾN THỨC ----------------

QUY TẮC BẮT BUỘC:
- Mọi nội dung, câu hỏi, ví dụ, thí nghiệm phải trích xuất trực tiếp từ nguồn trên.
- Không tự bịa đặt kiến thức ngoài phạm vi.

================================================================
TÀI LIỆU PHỤ & TÍCH HỢP
================================================================
PHÂN PHỐI CHƯƠNG TRÌNH:
{safe_text(noi_dung_ppct)}

{ga_block}
{ai_block}

NĂNG LỰC SỐ:
{nls}

TÍCH HỢP AI:
{"Có tích hợp công cụ AI hỗ trợ hoạt động nhận thức của học sinh." if tich_hop_ai else "Không bắt buộc."}

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
*(Phân tách theo số tiết thực tế: ### TIẾT 1, ### TIẾT 2...)*

### Hoạt động 1: Khởi động
- Mục tiêu: ...
- Nội dung: ...
- Sản phẩm: ...
- Tổ chức thực hiện:
  + Bước 1: Chuyển giao nhiệm vụ: ...
  + Bước 2: Thực hiện nhiệm vụ: ...
  + Bước 3: Báo cáo, thảo luận: ...
  + Bước 4: Kết luận, nhận định: ...

### Hoạt động 2: Hình thành kiến thức mới
...

### Hoạt động 3: Luyện tập
...

### Hoạt động 4: Vận dụng
...

## IV. HỒ SƠ DẠY HỌC (Phiếu học tập, bài tập, đáp án...)

================================================================
QUY TẮC CUỐI CÙNG
================================================================
- Trả về Markdown sạch.
- Bắt đầu ngay bằng # TÊN BÀI HỌC.
- Không chào hỏi, không giải thích ngoài lề.
"""
