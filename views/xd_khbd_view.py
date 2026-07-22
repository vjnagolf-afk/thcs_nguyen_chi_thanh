# -*- coding: utf-8 -*-
"""
============================================================
VIEW: XÂY DỰNG KẾ HOẠCH BÀI DẠY
FILE: views/xd_khbd_view.py
============================================================
"""

import streamlit as st
import os
import json
from pathlib import Path

import pandas as pd
import PyPDF2
from docx import Document

# ============================================================
# IMPORT EXPORT WORD TỪ LÕI CỦA DỰ ÁN
# ============================================================
try:
    from export.word_export_engine import WordExportEngine
    from export.template_loader import TemplateLoader
except ImportError as e:
    WordExportEngine = None
    TemplateLoader = None
    EXPORT_WORD_IMPORT_ERROR = str(e)


# ============================================================
# KHUNG NĂNG LỰC SỐ
# ============================================================

# 1. KHUNG DÀNH CHO HỌC SINH (DigComp)
KHUNG_NLS_HS = {
    "1. Thông tin và dữ liệu số": {
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu, thông tin và nội dung số": {
            "Mức 1": "Xác định được nhu cầu thông tin; tìm kiếm dữ liệu, thông tin và nội dung số bằng các phương thức đơn giản.",
            "Mức 2": "Sử dụng được các phương pháp tìm kiếm, duyệt và lọc dữ liệu, thông tin và nội dung số phù hợp với nhu cầu chuyên môn.",
            "Mức 3": "Vận dụng được các chiến lược tìm kiếm, đánh giá và lựa chọn dữ liệu, thông tin và nội dung số phục vụ hoạt động giáo dục.",
        },
        "1.2. Đánh giá dữ liệu, thông tin và nội dung số": {
            "Mức 1": "Nhận biết được độ tin cậy cơ bản của nguồn dữ liệu, thông tin và nội dung số.",
            "Mức 2": "Phân tích và đánh giá được độ tin cậy, tính chính xác và mức độ phù hợp của dữ liệu, thông tin và nội dung số.",
            "Mức 3": "Có khả năng kiểm chứng, đối chiếu và đánh giá có hệ thống các nguồn dữ liệu, thông tin và nội dung số.",
        },
    },
    "2. Giao tiếp và hợp tác trong môi trường số": {
        "2.1. Tương tác thông qua công nghệ số": {
            "Mức 1": "Sử dụng được các công cụ số cơ bản để giao tiếp và tương tác.",
            "Mức 2": "Lựa chọn và sử dụng được công nghệ số phù hợp với mục đích giao tiếp, dạy học và phối hợp công việc.",
            "Mức 3": "Tổ chức và điều phối hiệu quả hoạt động giao tiếp, tương tác và phối hợp trong môi trường số.",
        },
        "2.4. Hợp tác thông qua công nghệ số": {
            "Mức 1": "Tham gia được các hoạt động hợp tác đơn giản bằng công nghệ số.",
            "Mức 2": "Sử dụng được công cụ số để phối hợp và làm việc nhóm.",
            "Mức 3": "Tổ chức, điều phối và đánh giá được hoạt động hợp tác số.",
        },
    },
    "3. Sáng tạo nội dung số": {
        "3.1. Phát triển nội dung số": {
            "Mức 1": "Tạo được nội dung số đơn giản bằng các công cụ phù hợp.",
            "Mức 2": "Tạo và chỉnh sửa được nội dung số phục vụ dạy học.",
            "Mức 3": "Thiết kế, phát triển và tối ưu hóa các sản phẩm nội dung số phục vụ hoạt động giáo dục.",
        },
    },
    "4. An toàn trong môi trường số": {
        "4.2. Bảo vệ dữ liệu cá nhân và quyền riêng tư": {
            "Mức 1": "Nhận biết được thông tin cá nhân và nguy cơ mất an toàn dữ liệu.",
            "Mức 2": "Áp dụng được các biện pháp bảo vệ dữ liệu cá nhân và quyền riêng tư.",
            "Mức 3": "Đánh giá và tổ chức được các biện pháp bảo vệ dữ liệu cá nhân.",
        },
    },
    "5. Giải quyết vấn đề trong môi trường số": {
        "5.2. Xác định nhu cầu và giải pháp công nghệ": {
            "Mức 1": "Nhận biết được nhu cầu sử dụng công nghệ trong tình huống đơn giản.",
            "Mức 2": "Lựa chọn được công cụ và giải pháp số phù hợp.",
            "Mức 3": "Thiết kế và đánh giá được giải pháp công nghệ phù hợp với nhu cầu.",
        },
    },
    "6. Sử dụng trí tuệ nhân tạo": {
        "6.1. Hiểu biết về trí tuệ nhân tạo": {
            "Mức 1": "Nhận biết được khái niệm, khả năng và một số hạn chế cơ bản của AI.",
            "Mức 2": "Giải thích được vai trò, khả năng, giới hạn và rủi ro của AI.",
            "Mức 3": "Đánh giá được tác động của AI đối với hoạt động giáo dục và xã hội.",
        },
        "6.2. Sử dụng trí tuệ nhân tạo": {
            "Mức 1": "Sử dụng được công cụ AI đơn giản với sự hướng dẫn.",
            "Mức 2": "Sử dụng AI để hỗ trợ học tập, dạy học và giải quyết nhiệm vụ.",
            "Mức 3": "Thiết kế, điều phối và đánh giá việc sử dụng AI trong giáo dục.",
        },
        "6.3. Đánh giá và sử dụng AI có trách nhiệm": {
            "Mức 1": "Nhận biết được nguy cơ sai lệch, sai sót và rủi ro khi sử dụng AI.",
            "Mức 2": "Kiểm chứng, đánh giá và sử dụng có trách nhiệm nội dung do AI tạo ra.",
            "Mức 3": "Xây dựng và tổ chức được quy trình sử dụng AI an toàn, có đạo đức và phù hợp với mục tiêu giáo dục.",
        },
    },
}

# 2. KHUNG DÀNH CHO GIÁO VIÊN (Theo TT18/2026/TT-BGDĐT)
KHUNG_NLS_GV = {
    "1. Tổ chức dạy học, giáo dục trong môi trường số": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "Sử dụng được các chức năng và công cụ cơ bản của nền tảng quản lí học tập (LMS); Sử dụng được công cụ hỗ trợ trực tuyến.",
            "Thành thạo": "Xây dựng kế hoạch bài dạy theo tiếp cận công nghệ; Triển khai mô hình kết hợp (blended learning); Dạy học dự án trực tuyến.",
            "Nâng cao": "Sáng tạo và đổi mới các mô hình dạy học ứng dụng công nghệ số; Hướng dẫn đồng nghiệp thiết kế trải nghiệm học tập số hóa tiên tiến."
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": "Sử dụng được các kênh giao tiếp số (email, diễn đàn) để trả lời câu hỏi và hỗ trợ người học khi cần thiết.",
            "Thành thạo": "Sử dụng kênh số tương tác, giải đáp thắc mắc; Dùng dữ liệu học tập số để xác định và hỗ trợ người học kịp thời.",
            "Nâng cao": "Hướng dẫn đồng nghiệp xây dựng văn hóa hỗ trợ tích cực trên nền tảng số; Phát triển công cụ hỗ trợ dạy học thông minh."
        },
        "1.3. Cá nhân hóa người học": {
            "Cơ bản": "Xác định nhu cầu, sự khác biệt của người học; Lựa chọn, điều chỉnh công cụ và nội dung số phù hợp.",
            "Thành thạo": "Thiết kế hệ thống hướng dẫn học tập cá nhân hóa, lộ trình học tập linh hoạt; Phân hóa trình độ trong môi trường trực tuyến.",
            "Nâng cao": "Thiết kế môi trường học tập số cá nhân hóa, cung cấp công cụ tự định hướng; Đánh giá hiệu quả dạy học cá nhân hóa."
        },
        "1.4. Học tập cộng tác": {
            "Cơ bản": "Sử dụng công cụ số cơ bản tổ chức làm việc nhóm đơn giản; Thiết kế nhiệm vụ chia sẻ ý tưởng trên nền tảng số.",
            "Thành thạo": "Thiết kế nhiệm vụ cùng xây dựng nội dung; Hướng dẫn người học giao tiếp số; Dùng công nghệ đánh giá làm việc nhóm.",
            "Nâng cao": "Xây dựng dự án cộng tác phức tạp; Quản lí cộng đồng học tập trực tuyến; Hướng dẫn đồng nghiệp triển khai học tập cộng tác số."
        }
    },
    "2. Kiểm tra, đánh giá": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": "Sử dụng hình thức kiểm tra truyền thống kết hợp nhập điểm hệ thống số; Áp dụng công cụ tạo bài kiểm tra online đơn giản.",
            "Thành thạo": "Sử dụng công cụ số phổ biến để tạo bài kiểm tra quá trình và tổng kết; Thiết kế đa dạng công cụ đánh giá số.",
            "Nâng cao": "Sáng tạo triển khai mô hình đánh giá số tiên tiến đáp ứng năng lực phức hợp; Hướng dẫn đồng nghiệp áp dụng đánh giá số."
        },
        "2.2. Phân tích kết quả học tập": {
            "Cơ bản": "Sử dụng chức năng cơ bản của LMS xem báo cáo hoạt động người học; Xây dựng báo cáo đánh giá sự tiến bộ.",
            "Thành thạo": "Phân tích dữ liệu từ hệ thống đánh giá để nhận diện tiến bộ; Xây dựng bảng điều khiển tự động (dashboard) dữ liệu trực quan.",
            "Nâng cao": "Áp dụng kĩ thuật phân tích dữ liệu nâng cao dự đoán xu hướng, phát hiện sớm vấn đề; Hướng dẫn đồng nghiệp diễn giải dữ liệu."
        },
        "2.3. Phản hồi và đánh giá cải tiến": {
            "Cơ bản": "Cung cấp phản hồi trên hệ thống LMS, phản hồi kịp thời bằng văn bản/điểm số qua nền tảng số.",
            "Thành thạo": "Sử dụng đa dạng công cụ (ghi âm, video, bình luận trực tiếp) đưa ra phản hồi chi tiết; Thiết kế qui trình có sự tham gia của người học.",
            "Nâng cao": "Sử dụng dữ liệu phân tích điều chỉnh kế hoạch bài dạy; Hướng dẫn đồng nghiệp dùng phản hồi số cải tiến liên tục."
        }
    },
    "3. Trao quyền cho người học": {
        "3.1. Tiếp cận và hòa nhập": {
            "Cơ bản": "Sử dụng công cụ số hỗ trợ người học gặp khó khăn; Đảm bảo mọi người học có cơ hội dùng thiết bị, hạ tầng số.",
            "Thành thạo": "Khai thác, điều chỉnh tài nguyên số đáp ứng đa dạng người học (ngôn ngữ, khuyết tật); Thiết kế nội dung đảm bảo tính hòa nhập.",
            "Nâng cao": "Hướng dẫn đồng nghiệp chiến lược và công nghệ số hỗ trợ giáo dục hòa nhập."
        },
        "3.2. Giải quyết vấn đề": {
            "Cơ bản": "Thiết kế nhiệm vụ yêu cầu người học dùng Internet tìm thông tin, trả lời câu hỏi, giải quyết vấn đề đơn giản.",
            "Thành thạo": "Thiết kế dự án yêu cầu người học thu thập, phân tích thông tin bằng số; Tổ chức học tập dựa trên vấn đề (problem-based).",
            "Nâng cao": "Hướng dẫn đồng nghiệp xây dựng hệ sinh thái học tập số, kết nối chuyên gia giải quyết vấn đề thực tế cộng đồng."
        },
        "3.3. Khuyến khích sự tham gia tích cực": {
            "Cơ bản": "Sử dụng công cụ trực quan hóa và tương tác số đơn giản để thu hút sự chú ý, khuyến khích học sinh tham gia.",
            "Thành thạo": "Tích hợp trò chơi hóa (gamification); Thiết kế hoạt động người học tự tạo nội dung số, mô phỏng, thực tế ảo (VR/AR).",
            "Nâng cao": "Sáng tạo dự án năng động lấy người học làm trung tâm; Hướng dẫn đồng nghiệp hoạt động học tập tích cực bằng công nghệ."
        }
    },
    "4. Kĩ năng công nghệ số": {
        "4.1. Kĩ năng thông tin và dữ liệu": {
            "Cơ bản": "Sử dụng công cụ tìm kiếm tài liệu; Lưu trữ, sắp xếp khoa học dữ liệu trên máy tính hoặc đám mây.",
            "Thành thạo": "Đánh giá độ tin cậy nguồn tin; Hướng dẫn người học tư duy phản biện khi tiếp nhận thông tin số; Tìm kiếm nâng cao.",
            "Nâng cao": "Sử dụng công cụ thu thập, trực quan hóa và phân tích dữ liệu; Hướng dẫn tích hợp năng lực thông tin vào chương trình."
        },
        "4.2. Sáng tạo nội dung số": {
            "Cơ bản": "Sử dụng công cụ phổ biến tạo nội dung định dạng số; Tích hợp định dạng số vào nhiệm vụ học tập.",
            "Thành thạo": "Hướng dẫn người học công cụ tạo nội dung số, bản quyền, trích dẫn; Sử dụng nền tảng chia sẻ nội dung hợp lệ.",
            "Nâng cao": "Thành thạo công cụ chuyên dụng tạo học liệu số tương tác cao; Phát triển nền tảng học tập tích hợp AI, thực tế ảo."
        },
        "4.3. An toàn": {
            "Cơ bản": "Hiểu biết bảo vệ sức khỏe thể chất/tinh thần; Bố trí không gian, thời gian sử dụng thiết bị hợp lí.",
            "Thành thạo": "Tích hợp phòng tránh rủi ro mạng; Áp dụng biện pháp bảo vệ dữ liệu cá nhân; Xử lí bắt nạt trực tuyến.",
            "Nâng cao": "Áp dụng phương pháp dạy học giảm căng thẳng số; Cập nhật xu hướng an toàn số cho giáo viên, phụ huynh."
        }
    },
    "5. Phát triển chuyên môn": {
        "5.1. Giao tiếp trong tổ chức": {
            "Cơ bản": "Sử dụng email, nhóm chat trao đổi thông tin và giao tiếp phụ huynh.",
            "Thành thạo": "Sử dụng hiệu quả kênh giao tiếp chính thức; Xây dựng kế hoạch đổi mới giao tiếp chuyên môn.",
            "Nâng cao": "Xây dựng chiến lược truyền thông số; Hướng dẫn đồng nghiệp đổi mới giao tiếp tăng tính minh bạch."
        },
        "5.2. Hợp tác phát triển chuyên môn": {
            "Cơ bản": "Tham gia cộng đồng học tập trực tuyến; Tự đánh giá thách thức ứng dụng công nghệ số.",
            "Thành thạo": "Giao tiếp, chia sẻ chuyên môn bằng công cụ số; Cập nhật kiến thức qua khóa học trực tuyến.",
            "Nâng cao": "Hướng dẫn xây dựng yêu cầu dạy học môi trường số; Phát triển công cụ phản ánh năng lực số."
        },
        "5.3. Phát triển, quản lí học liệu số": {
            "Cơ bản": "Tìm kiếm tài nguyên (OER) bằng công cụ phổ biến; Lựa chọn tài nguyên phù hợp mục tiêu.",
            "Thành thạo": "Lưu trữ, chia sẻ kho học liệu an toàn; Đánh giá chất lượng, bản quyền học liệu; Tạo tài nguyên từ nguồn có sẵn.",
            "Nâng cao": "Xây dựng hệ thống quản lí tài nguyên cho tổ/trường; Hướng dẫn quản trị kho học liệu mở."
        }
    },
    "6. Trí tuệ nhân tạo (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": "Nhận diện cách vận hành của AI; Tự đánh giá, cải tiến ứng dụng công nghệ trong dạy học.",
            "Thành thạo": "Thiết kế hoạt động tích hợp AI sáng tạo, có trách nhiệm.",
            "Nâng cao": "Triển khai phương pháp dạy học mới tích hợp sâu AI cá nhân hóa; Hướng dẫn, đề xuất dùng công cụ AI."
        },
        "6.2. Đạo đức AI": {
            "Cơ bản": "Nhận diện rủi ro thu thập dữ liệu; Thể hiện cẩn trọng, trách nhiệm với quyền riêng tư của người học.",
            "Thành thạo": "Đánh giá ứng dụng AI theo đạo đức; Hướng dẫn người học dùng AI an toàn, nhận biết ưu/nhược điểm AI.",
            "Nâng cao": "Cập nhật, chia sẻ vấn đề đạo đức AI; Tham gia xây dựng chính sách dùng AI có đạo đức trong nhà trường."
        },
        "6.3. Sư phạm AI": {
            "Cơ bản": "Hiểu lợi ích sư phạm của công cụ AI hỗ trợ dạy học; Tích hợp AI cá nhân hóa.",
            "Thành thạo": "Ứng dụng AI linh hoạt trong các bước dạy học lấy người học làm trung tâm; Quản lý tương tác 3 chiều GV-HS-AI.",
            "Nâng cao": "Xây dựng nguyên tắc sư phạm dùng AI; Hướng dẫn đồng nghiệp thiết kế AI lấy con người làm trung tâm."
        },
        "6.4. AI cho phát triển chuyên môn": {
            "Cơ bản": "Theo dõi và phân tích quá trình phát triển chuyên môn bằng công cụ AI phù hợp.",
            "Thành thạo": "Dùng AI tạo sinh hỗ trợ học tập suốt đời; Dùng nền tảng AI tìm tài nguyên, tham gia cộng đồng thực hành.",
            "Nâng cao": "Hướng dẫn đổi mới sáng tạo cho đồng nghiệp qua nền tảng AI; Xây dựng công cụ AI tạo sinh hỗ trợ đồng nghiệp."
        }
    }
}


# ============================================================
# SESSION STATE
# ============================================================

def init_session_state():
    defaults = {
        "khbd_mode": "chinh_sua",
        "khbd_result": None,
        "khbd_nls_list": [],
        "khbd_hoat_dong_list": [],
        "khbd_processing": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_ket_qua():
    st.session_state["khbd_result"] = None

def set_mode(mode: str):
    st.session_state.khbd_mode = mode


# ============================================================
# HÀM ĐỌC FILE
# ============================================================

def safe_text(value):
    if value is None: return ""
    return str(value).replace("\x00", "").strip()

def read_pdf(uploaded_file):
    result = []
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for index, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            if text.strip():
                result.append(f"\n===== PDF - TRANG {index} =====\n{text.strip()}")
    except Exception as e:
        result.append(f"[LỖI ĐỌC PDF: {str(e)}]")
    return "\n".join(result)

def read_docx(uploaded_file):
    result = []
    try:
        document = Document(uploaded_file)
        for paragraph in document.paragraphs:
            text = safe_text(paragraph.text)
            if text: result.append(text)
        for index, table in enumerate(document.tables, start=1):
            result.append(f"\n===== BẢNG WORD {index} =====")
            for row in table.rows:
                cells = [safe_text(cell.text).replace("\n", " ") for cell in row.cells]
                result.append(" | ".join(cells))
    except Exception as e:
        result.append(f"[LỖI ĐỌC DOCX: {str(e)}]")
    return "\n".join(result)

def read_excel(uploaded_file):
    result = []
    try:
        sheets = pd.read_excel(uploaded_file, sheet_name=None)
        for sheet_name, dataframe in sheets.items():
            result.append(f"\n===== EXCEL - SHEET: {sheet_name} =====")
            dataframe = dataframe.fillna("")
            result.append(dataframe.to_string(index=False))
    except Exception as e:
        result.append(f"[LỖI ĐỌC EXCEL: {str(e)}]")
    return "\n".join(result)

def read_image(uploaded_file):
    return "[Ảnh đính kèm. Sử dụng Vision AI nếu AI Engine có hỗ trợ]"

def read_uploaded_file(uploaded_file):
    if uploaded_file is None: return ""
    filename = uploaded_file.name.lower()
    extension = Path(filename).suffix.lower()
    try:
        if extension == ".pdf": return read_pdf(uploaded_file)
        if extension == ".docx": return read_docx(uploaded_file)
        if extension in [".xlsx", ".xls"]: return read_excel(uploaded_file)
        if extension in [".jpg", ".jpeg", ".png", ".webp"]: return read_image(uploaded_file)
        return f"[KHÔNG HỖ TRỢ ĐỊNH DẠNG: {extension}]"
    except Exception as e:
        return f"[LỖI ĐỌC FILE: {uploaded_file.name}]\n{str(e)}"

def read_multiple_files(files):
    result = []
    for uploaded_file in files or []:
        result.append(f"\n\n==================================================\n"
                      f"TỆP: {uploaded_file.name}\n"
                      f"==================================================\n")
        result.append(read_uploaded_file(uploaded_file))
    return "\n".join(result)

def read_template_local(path="templates/KHBD_Mau.docx"):
    if not os.path.exists(path): return ""
    try:
        with open(path, "rb") as f:
            document = Document(f)
            result = []
            for paragraph in document.paragraphs:
                text = safe_text(paragraph.text)
                if text: result.append(text)
            for index, table in enumerate(document.tables, start=1):
                result.append(f"\n===== BẢNG WORD {index} =====")
                for row in table.rows:
                    cells = [safe_text(cell.text).replace("\n", " ") for cell in row.cells]
                    result.append(" | ".join(cells))
            return "\n".join(result)
    except Exception: return ""

# ============================================================
# NLS AUTO-FILL
# ============================================================
def add_nls():
    linh_vuc = st.session_state.get("khbd_nls_linh_vuc", "")
    thanh_phan = st.session_state.get("khbd_nls_thanh_phan", "")
    muc_do = st.session_state.get("khbd_nls_muc_do", "")
    noi_dung = st.session_state.get("khbd_nls_noi_dung", "").strip()

    if not noi_dung: return

    item = {
        "van_ban": "18/2026/TT-BGDĐT" if st.session_state.get("khbd_loai_khung_nls") == "Giáo viên (Thông tư 18)" else "DigComp",
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
        result.append(
            f"NĂNG LỰC SỐ {index}\n"
            f"- Văn bản: {item['van_ban']}\n"
            f"- Lĩnh vực: {item['linh_vuc']}\n"
            f"- Thành phần: {item['thanh_phan']}\n"
            f"- Mức độ: {item['muc_do']}\n"
            f"- Yêu cầu cần đạt: {item['noi_dung']}\n"
        )
    return "\n".join(result)

# ============================================================
# HOẠT ĐỘNG
# ============================================================
def add_activity():
    value = st.session_state.get("khbd_new_activity", "").strip()
    if value and value not in st.session_state.khbd_hoat_dong_list:
        st.session_state.khbd_hoat_dong_list.append(value)
    st.session_state.khbd_new_activity = ""

# ============================================================
# AI ENGINE
# ============================================================
def normalize_ai_result(result):
    if result is None: return ""
    if isinstance(result, str): return result.strip()
    if isinstance(result, dict):
        for key in ["text", "content", "response", "output", "answer"]:
            if key in result: return str(result[key]).strip()
    return str(result).strip()

def generate_ai(ai_engine, prompt):
    if ai_engine is None: raise RuntimeError("Chưa truyền AI Engine vào render_xd_khbd().")
    if hasattr(ai_engine, "generate_text"):
        result = ai_engine.generate_text(prompt)
        text = normalize_ai_result(result)
        if text: return text
    if hasattr(ai_engine, "generate"):
        result = ai_engine.generate(prompt)
        text = normalize_ai_result(result)
        if text: return text
    raise RuntimeError("AI Engine không trả về nội dung.")

# ============================================================
# PROMPT
# ============================================================
def build_prompt(
    thong_tin, noi_dung_chinh, noi_dung_ppct, noi_dung_ai, noi_dung_mau,
    nls, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, hoat_dong, mode
):
    if mode == "chinh_sua":
        nhiem_vu = "\nPhân tích và nâng cấp giáo án gốc.\n- Giữ nguyên tên bài và phạm vi kiến thức.\n- Bổ sung mục tiêu, hoạt động GV/HS thật chi tiết.\n- Sửa lỗi sư phạm nếu cần.\n"
    else:
        nhiem_vu = "\nXây dựng Kế hoạch bài dạy mới từ SGK.\n- Bám sát nội dung SGK, không tự thêm kiến thức bài khác.\n- Mô tả chi tiết kịch bản dạy học.\n"

    return f"""
BẠN LÀ CHUYÊN GIA SƯ PHẠM VÀ PHÁT TRIỂN CHƯƠNG TRÌNH ĐÀO TẠO VIỆT NAM (THEO CV 5512).

{nhiem_vu}

==================================================
I. THÔNG TIN BÀI DẠY
==================================================
{thong_tin}

==================================================
II. MẪU GIÁO ÁN (BẮT BUỘC TUÂN THỦ 100% CẤU TRÚC ĐỀ MỤC VÀ BẢNG BIỂU)
==================================================
{noi_dung_mau}

==================================================
III. TÀI LIỆU NGUỒN CỐT LÕI (SÁCH/GIÁO ÁN GỐC)
==================================================
{noi_dung_chinh}

==================================================
IV. TÀI LIỆU CHỈ ĐẠO
==================================================
- PPCT: {noi_dung_ppct}
- Bảng AI: {noi_dung_ai}

==================================================
V. YÊU CẦU TÍCH HỢP
==================================================
1. Năng Lực Số:
{nls}

2. Tích hợp AI:
{'Được tích hợp AI. Phải nêu rõ nhiệm vụ AI, cách kiểm chứng kết quả AI và sản phẩm học tập.' if tich_hop_ai else 'Không tích hợp AI.'}

3. Dạy học hòa nhập:
{f'Có học sinh cần hỗ trợ: {nhu_cau_hoa_nhap}. Phải điều chỉnh nhiệm vụ, phương tiện, thời gian hoặc cách thể hiện sản phẩm.' if tich_hop_hoa_nhap else 'Không yêu cầu điều chỉnh dạy học hòa nhập.'}

4. Hoạt động GV yêu cầu (Bắt buộc chèn vào):
{hoat_dong}

==================================================
VI. YÊU CẦU CHUYÊN MÔN
==================================================
- KHÔNG SỬ DỤNG MÃ LATEX. Viết công thức bằng văn bản thường (vd: a/b, x^2, can bac hai) để chống lỗi font Word khi kết xuất.
- Sử dụng Markdown phân cấp rõ ràng để công cụ export xuất Word chuẩn. Nếu dùng Bảng, đảm bảo chuẩn cấu trúc | Cột 1 | Cột 2 |.
- Nếu file mẫu yêu cầu viết dưới dạng bảng (Ví dụ: cột Hoạt động của GV | cột Hoạt động của HS), BẮT BUỘC phải kẻ bảng Markdown tương ứng.
- Chi tiết hóa tối đa các hoạt động (GV nói câu gì trong ngoặc kép, HS trả lời ra sao).
- KHÔNG viết dạo đầu, KHÔNG chào hỏi, trả thẳng vào nội dung giáo án.
"""


# ============================================================
# RENDER VIEW
# ============================================================
def render_xd_khbd(ai_engine=None):
    init_session_state()

    st.title("📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY")

    # --------------------------------------------------------
    # THÔNG TIN BÀI DẠY
    # --------------------------------------------------------
    st.subheader("🎛️ Thông tin bài dạy")
    col1, col2 = st.columns(2)
    with col1:
        khoi_lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], key="khbd_khoi_lop")
    with col2:
        mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Tiếng Anh", "Khoa học tự nhiên", "Vật lí", "Hóa học", "Sinh học", "Lịch sử và Địa lí", "Tin học", "Công nghệ", "Khác"], key="khbd_mon_hoc")

    # --------------------------------------------------------
    # CHẾ ĐỘ
    # --------------------------------------------------------
    st.subheader("✨ Chế độ soạn")
    mode = st.radio("Chọn chế độ", ["chinh_sua", "tu_dong"], format_func=lambda x: "📄 Chỉnh sửa giáo án gốc" if x == "chinh_sua" else "⚡ Tự động soạn từ SGK", key="khbd_mode")

    # --------------------------------------------------------
    # TÍCH HỢP
    # --------------------------------------------------------
    st.subheader("🔧 Tích hợp")
    c1, c2, c3 = st.columns(3)
    with c1: tich_hop_nls = st.checkbox("Năng lực số", key="khbd_tich_hop_nls")
    with c2: tich_hop_ai = st.checkbox("Năng lực AI", key="khbd_tich_hop_ai")
    with c3: tich_hop_hoa_nhap = st.checkbox("Dạy học hòa nhập", key="khbd_tich_hop_hoa_nhap")

    # --------------------------------------------------------
    # FILE
    # --------------------------------------------------------
    st.subheader("📤 Tài liệu đầu vào")
    
    if mode == "chinh_sua":
        file_ga = st.file_uploader("Giáo án gốc", type=["docx", "pdf", "jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="khbd_file_ga")
        file_sgk = []
    else:
        file_ga = []
        file_sgk = st.file_uploader("SGK / Tài liệu bài học", type=["pdf", "docx", "jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="khbd_file_sgk")
    
    file_ppct = st.file_uploader("PPCT", type=["pdf", "docx", "xlsx", "xls"], key="khbd_file_ppct")
    file_ai = st.file_uploader("Bảng tích hợp AI", type=["pdf", "docx", "xlsx", "xls"], key="khbd_file_ai")
    file_template = st.file_uploader("File mẫu giáo án DOCX (Nếu trống sẽ dùng templates/KHBD_Mau.docx)", type=["docx"], key="khbd_file_template")

    # --------------------------------------------------------
    # THÔNG TIN CHI TIẾT
    # --------------------------------------------------------
    st.subheader("📚 Thông tin bài học")
    col1, col2 = st.columns(2)
    with col1: ten_bai = st.text_input("Tên bài dạy", key="khbd_ten_bai")
    with col2: so_tiet = st.text_input("Thời lượng", value="1 tiết", key="khbd_so_tiet")

    # --------------------------------------------------------
    # HOẠT ĐỘNG
    # --------------------------------------------------------
    st.subheader("📌 Hoạt động giáo viên mong muốn")
    c1, c2 = st.columns([5, 1])
    with c1: st.text_input("Hoạt động", placeholder="VD: Thí nghiệm, trò chơi, mô phỏng...", key="khbd_new_activity", label_visibility="collapsed", on_change=add_activity)
    with c2: st.button("➕ Thêm", on_click=add_activity, use_container_width=True)

    for index, activity in enumerate(st.session_state.khbd_hoat_dong_list):
        c1, c2 = st.columns([10, 1])
        with c1: st.info(activity)
        with c2:
            if st.button("Xóa", key=f"khbd_del_activity_{index}"):
                st.session_state.khbd_hoat_dong_list.pop(index)
                st.rerun()

    # --------------------------------------------------------
    # NĂNG LỰC SỐ
    # --------------------------------------------------------
    if tich_hop_nls:
        st.subheader("🎯 Năng lực số")

        loai_khung = st.radio("Chọn chuẩn Năng lực số áp dụng:", ["Học sinh (DigComp)", "Giáo viên (Thông tư 18)"], horizontal=True, key="khbd_loai_khung_nls")
        current_khung = KHUNG_NLS_HS if loai_khung == "Học sinh (DigComp)" else KHUNG_NLS_GV

        col_lv, col_tp, col_md = st.columns([2, 2, 1])
        with col_lv: linh_vuc = st.selectbox("Lĩnh vực", list(current_khung.keys()), key="khbd_nls_linh_vuc")
        with col_tp: thanh_phan = st.selectbox("Thành phần", list(current_khung[linh_vuc].keys()), key="khbd_nls_thanh_phan")
        with col_md: muc_do = st.selectbox("Mức độ", list(current_khung[linh_vuc][thanh_phan].keys()), key="khbd_nls_muc_do")

        if "last_khung_state" not in st.session_state: st.session_state.last_khung_state = loai_khung
        if "last_lv_state" not in st.session_state: st.session_state.last_lv_state = linh_vuc
        if "last_tp_state" not in st.session_state: st.session_state.last_tp_state = thanh_phan
        if "last_md_state" not in st.session_state: st.session_state.last_md_state = muc_do

        if (st.session_state.last_khung_state != loai_khung or
            st.session_state.last_lv_state != linh_vuc or
            st.session_state.last_tp_state != thanh_phan or
            st.session_state.last_md_state != muc_do):
            
            st.session_state.last_khung_state = loai_khung
            st.session_state.last_lv_state = linh_vuc
            st.session_state.last_tp_state = thanh_phan
            st.session_state.last_md_state = muc_do
            
            st.session_state.khbd_nls_noi_dung = current_khung[linh_vuc][thanh_phan][muc_do]

        st.text_area("Yêu cầu cần đạt", key="khbd_nls_noi_dung", height=120)
        st.button("➕ Thêm năng lực số", on_click=add_nls, use_container_width=True)

        for index, item in enumerate(st.session_state.khbd_nls_list):
            with st.container(border=True):
                st.markdown(f"**{index + 1}. {item['linh_vuc']}**\n\n**Thành phần:** {item['thanh_phan']}\n\n**Mức độ:** {item['muc_do']}\n\n**Yêu cầu:** {item['noi_dung']}")
                if st.button("Xóa", key=f"khbd_del_nls_{index}"):
                    st.session_state.khbd_nls_list.pop(index)
                    st.rerun()

    # --------------------------------------------------------
    # HÒA NHẬP
    # --------------------------------------------------------
    nhu_cau_hoa_nhap = []
    if tich_hop_hoa_nhap:
        nhu_cau_hoa_nhap = st.multiselect("Nhu cầu hỗ trợ", ["Vận động", "Nghe", "Nói", "Nhìn", "Thần kinh", "Tâm thần", "Trí tuệ", "Tự kỷ", "Khác"], key="khbd_nhu_cau_hoa_nhap")

    # --------------------------------------------------------
    # NGÔN NGỮ
    # --------------------------------------------------------
    tieng_anh = st.checkbox("Giáo án viết bằng ngôn ngữ Tiếng Anh", key="khbd_tieng_anh")

    # --------------------------------------------------------
    # NÚT TẠO
    # --------------------------------------------------------
    st.divider()

    if st.button("⚡ KÍCH HOẠT XỬ LÝ AI", type="primary", use_container_width=True):
        if ai_engine is None:
            st.error("❌ Chưa truyền AI Engine.")
            st.stop()
        if mode == "chinh_sua" and not file_ga:
            st.error("⚠️ Vui lòng tải giáo án gốc.")
            st.stop()
        if mode == "tu_dong" and not file_sgk:
            st.error("⚠️ Vui lòng tải SGK hoặc tài liệu bài học.")
            st.stop()

        with st.spinner("🧠 AI đang phân tích và xây dựng KHBD..."):
            try:
                if mode == "chinh_sua":
                    noi_dung_chinh = read_multiple_files(file_ga)
                else:
                    noi_dung_chinh = read_multiple_files(file_sgk)

                noi_dung_ppct = read_uploaded_file(file_ppct)
                noi_dung_ai = read_uploaded_file(file_ai)
                
                if file_template:
                    noi_dung_mau = read_uploaded_file(file_template)
                else:
                    noi_dung_mau = read_template_local()

                thong_tin = f"- Cấp học: THCS\n- Khối lớp: {khoi_lop}\n- Môn học: {mon_hoc}\n- Tên bài dạy: {ten_bai or 'Theo tài liệu nguồn'}\n- Thời lượng: {so_tiet}\n- Ngôn ngữ: {'Tiếng Anh' if tieng_anh else 'Tiếng Việt'}"
                hoat_dong = "\n".join(st.session_state.khbd_hoat_dong_list) or "Không có yêu cầu riêng."

                prompt = build_prompt(
                    thong_tin=thong_tin,
                    noi_dung_chinh=noi_dung_chinh,
                    noi_dung_ppct=noi_dung_ppct,
                    noi_dung_ai=noi_dung_ai,
                    noi_dung_mau=noi_dung_mau,
                    nls=format_nls(),
                    tich_hop_ai=tich_hop_ai,
                    tich_hop_hoa_nhap=tich_hop_hoa_nhap,
                    nhu_cau_hoa_nhap=", ".join(nhu_cau_hoa_nhap),
                    hoat_dong=hoat_dong,
                    mode=mode
                )

                result = generate_ai(ai_engine, prompt)
                st.session_state.khbd_result = result
                st.success("🎉 Đã tạo KHBD thành công.")

            except Exception as e:
                st.error(f"❌ Lỗi xử lý: {str(e)}")

    # --------------------------------------------------------
    # KẾT QUẢ VÀ XUẤT WORD CHUẨN ENGINE CỦA DỰ ÁN
    # --------------------------------------------------------
    result = st.session_state.get("khbd_result")
    if result:
        st.subheader("📝 Kết quả KHBD")
        st.markdown(result)
        st.divider()

        st.subheader("📄 Xuất Word")

        if WordExportEngine is None or TemplateLoader is None:
            st.error("❌ Lỗi xuất Word: Không import được các module lõi `export.word_export_engine` hoặc `export.template_loader`.")
            st.code(EXPORT_WORD_IMPORT_ERROR, language="text")
        else:
            try:
                # 1. Xác định đường dẫn file template thực tế
                template_path = "templates/KHBD_Mau.docx"
                uploaded_template = st.session_state.get("khbd_file_template")
                
                # Nếu giáo viên có tải file mẫu riêng, lưu tạm ra đĩa để TemplateLoader xử lý
                if uploaded_template:
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                        tmp.write(uploaded_template.getvalue())
                        template_path = tmp.name

                # 2. Sử dụng TemplateLoader để load và điền biến mẫu nếu có
                doc_template = TemplateLoader.load(template_path)
                
                # 3. Sử dụng WordExportEngine kết xuất nội dung Markdown thành bytes chuẩn A4
                word_bytes = WordExportEngine.convert_markdown_to_docx_bytes(result)

                # Cung cấp nút tải xuống cho người dùng
                st.download_button(
                    "📥 TẢI KHBD WORD (Chuẩn định dạng dự án)",
                    data=word_bytes,
                    file_name="Giao_An_Thong_Minh.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

                # Dọn dẹp file temp nếu có tạo riêng
                if uploaded_template and template_path != "templates/KHBD_Mau.docx" and os.path.exists(template_path):
                    os.remove(template_path)

            except Exception as e:
                st.error(f"❌ Lỗi xuất Word từ Core Engine: {str(e)}")
