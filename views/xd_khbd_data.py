# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY
FILE: views/xd_khbd_data.py
============================================================
"""

import streamlit as st
import os
import pandas as pd
import PyPDF2
from docx import Document
from pathlib import Path

# ============================================================
# 1. DICTIONARY NĂNG LỰC SỐ THÔNG TƯ 18/2026 & DIGCOMP
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
            "Nâng cao": "Xây dựng môi trường tự tự tin, an toàn để học sinh thể hiện bản thân; Hướng dẫn đồng nghiệp phương pháp tăng cường tương tác bằng công nghệ."
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
# 2. KHỞI TẠO SESSION STATE
# ============================================================
def init_session_state():
    defaults = {
        "khbd_mode": "chinh_sua",
        "khbd_result": None,
        "khbd_nls_list": [],
        "khbd_hoat_dong_list": [],
        "khbd_processing": False,
        "khbd_nls_noi_dung": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_ket_qua():
    st.session_state["khbd_result"] = None

def set_mode(mode: str):
    st.session_state.khbd_mode = mode

# ============================================================
# 3. HÀM ĐỌC FILE TỐI ƯU CÓ GIỚI HẠN TRANG
# ============================================================
def safe_text(value):
    if value is None: return ""
    return str(value).replace("\x00", "").strip()

def read_pdf(uploaded_file, range_str=""):
    result = []
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
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

def read_uploaded_file(uploaded_file, range_str=""):
    if uploaded_file is None: return ""
    filename = uploaded_file.name.lower()
    extension = Path(filename).suffix.lower()
    try:
        if extension == ".pdf": return read_pdf(uploaded_file, range_str)
        if extension == ".docx": return read_docx(uploaded_file)
        if extension in [".xlsx", ".xls"]: return read_excel(uploaded_file)
        return f"[Định dạng file: {extension}]"
    except Exception as e:
        return f"[LỖI ĐỌC FILE: {uploaded_file.name}]\n{str(e)}"

def read_multiple_files(files, range_str=""):
    result = []
    for uploaded_file in files or []:
        result.append(f"\n\n==================================================\n"
                      f"TỆP TIẾN TRÌNH: {uploaded_file.name}\n"
                      f"==================================================\n")
        result.append(read_uploaded_file(uploaded_file, range_str))
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
    except Exception:
        return ""

# ============================================================
# 4. CÁC HÀM XỬ LÝ SỰ KIỆN (UI EVENT CALLBACKS)
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

def add_activity():
    value = st.session_state.get("khbd_new_activity", "").strip()
    if value and value not in st.session_state.khbd_hoat_dong_list:
        st.session_state.khbd_hoat_dong_list.append(value)
    st.session_state.khbd_new_activity = ""

# ============================================================
# 5. ENGINE AI & XÂY DỰNG PROMPT
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
    raise RuntimeError("AI Engine không trả về nội dung giáo án hoàn chỉnh.")

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ppct, noi_dung_ai, noi_dung_mau, nls, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, hoat_dong, mode):
    if mode == "chinh_sua":
        nhiem_vu = "Phân tích, kế thừa nội dung thô và chuẩn hóa cấu trúc giáo án theo đúng Phụ lục 4 Công văn 5512."
    else:
        nhiem_vu = "Soạn mới hoàn toàn Kế hoạch bài dạy chi tiết từ dữ liệu Sách giáo khoa (SGK) được cung cấp."
        
    return f"""
BẠN LÀ CHUYÊN GIA SƯ PHẠM CAO CẤP VÀ THẨM ĐỊNH CHƯƠNG TRÌNH GIÁO DỤC PHỔ THÔNG 2018.
NHIỆM VỤ CỦA BẠN: {nhiem_vu}

==================================================================================
🚨 QUY TẮC ÉP SƯ PHẠM CHI TIẾT - CHỐNG VIẾT CHUNG CHUNG (BẮT BUỘC TUÂN THỦ 100%) 🚨
==================================================================================
Tuyệt đối KHÔNG sử dụng câu văn mang tính tóm tắt, bao quát mơ hồ. Bạn phải viết chi tiết cụ thể hành vi sư phạm:
❌ CẤM VIẾT CHUNG CHUNG: "Giáo viên yêu cầu học sinh làm bài tập", "Học sinh thảo luận nhóm", "GV kết luận kiến thức", "Sản phẩm: HS hoàn thành vở bài tập".
✅ PHẢI CHI TIẾT HÓA MÔ HÌNH:
- Mục Nội dung: Ghi chính xác câu hỏi, đề bài, phiếu học tập mà GV giao cho HS.
- Mục Sản phẩm: Ghi ĐẦY ĐỦ lời giải, đáp án khoa học chi tiết, phương trình toán học/hóa học, kết luận cuối cùng mà học sinh phải làm ra.
- Mục Kết luận, nhận định: Ghi RÕ RÀNG NỘI DUNG TRỌNG TÂM kiến thức khoa học để học sinh chép vào vở học (Không ghi "GV nhận xét chung").

==================================================================================
⏱️ QUY ĐỊNH BÁM SÁT THỜI LƯỢNG VÀ NỘI DUNG TÀI LIỆU NGUỒN SGK
==================================================================================
1. Toàn bộ tiến trình dạy học phải phân bổ logic khớp hoàn toàn với thời lượng quy định trong thông tin bài dạy.
2. Trích xuất TOÀN BỘ kiến thức, khái niệm, thuật ngữ từ "TÀI LIỆU NGUỒN CỐT LÕI (SGK)". Tuyệt đối không tự bịa kiến thức ngoài SGK hoặc viết tóm lược lược bỏ nội dung chính của bài.

==================================================================================
📐 QUY TẮC ĐỊNH DẠNG CÔNG THỨC TOÁN, LÝ, HÓA (ĐỂ XUẤT FILE WORD CHUẨN)
==================================================================================
- TUYỆT ĐỐI KHÔNG dùng mã LaTeX phức tạp.
- BẮT BUỘC DÙNG KÝ TỰ UNICODE VÀ PHƯƠNG PHÁP VIẾT TUYẾN TÍNH TRUYỀN THỐNG:
  + Công thức Toán/Lý: x^2 + 2x - 1 = 0; Phân số ghi dạng a/b (Ví dụ: (x + 1)/(x - 1)); Căn bậc hai ghi là căn(x) hoặc dùng ký tự √x.
  + Công thức Hóa học/Đơn vị (Dùng sub/superscript chuẩn): H₂O, CO₂, H₂SO₄, Fe + CuSO₄ -> FeSO₄ + Cu, m/s², kg/m³.

==================================================================================
📋 ĐỀ MỤC KHUNG GIÁO ÁN ĐẦU RA (BẮT BUỘC THEO PHỤ LỤC 4 CÔNG VĂN 5512)
==================================================================================
I. MỤC TIÊU: (Ghi rõ: 1. Về kiến thức; 2. Về năng lực; 3. Về phẩm chất)
II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU: (Mô tả thiết bị, phiếu học tập số mấy)
III. TIẾN TRÌNH DẠY HỌC:
Mỗi Hoạt động học (Khởi động, Hình thành kiến thức, Luyện tập, Vận dụng) bắt buộc phải triển khai cấu trúc cô đọng gồm 4 mục:
  a) Mục tiêu: (Hoạt động này giúp đạt được yêu cầu cần đạt cụ thể nào)
  b) Nội dung: (Chi tiết nội dung câu hỏi/nhiệm vụ)
  c) Sản phẩm học tập: (Đáp án toàn diện, chi tiết, cụ thể của học sinh)
  d) Tổ chức thực hiện: (Triển khai đầy đủ theo 4 bước nhỏ:)
     - Bước 1: Chuyển giao nhiệm vụ (Ghi rõ GV hướng dẫn như thế nào, thời gian bao lâu)
     - Bước 2: Thực hiện nhiệm vụ (HS làm việc cá nhân/nhóm, GV hỗ trợ trực tiếp)
     - Bước 3: Báo cáo, thảo luận (Cách thức gọi HS lên bảng báo cáo, tranh luận chéo)
     - Bước 4: Kết luận, nhận định (Ghi lại nội dung kiến thức chính xác kiến thức để học sinh ghi vở)

==================================================================================
[DỮ LIỆU BỐ CỤC ĐẦU VÀO]
I. THÔNG TIN BÀI DẠY:
{thong_tin}
II. MẪU GIÁO ÁN GỐC / THAM KHẢO TRƯỜNG:
{noi_dung_mau}
III. TÀI LIỆU NGUỒN CỐT LÕI (SGK / GIÁO ÁN GỐC):
{noi_dung_chinh}
IV. TÀI LIỆU CHỈ ĐẠO BỔ SUNG:
- Phân phối chương trình: {noi_dung_ppct}
- Khung AI tích hợp: {noi_dung_ai}
V. YÊU CẦU ĐẶC BIỆT TÍCH HỢP:
1. Năng lực số chuẩn mới: {nls}
2. Tích hợp AI: {'Yêu cầu tích hợp sâu AI sư phạm vào nội dung bài giảng.' if tich_hop_ai else 'Không bắt buộc chuyên sâu.'}
3. Hòa nhập học sinh chuyên biệt ({nhu_cau_hoa_nhap}): {'Điều chỉnh câu hỏi trực quan, phân tách thời gian trong từng tiến trình.' if tich_hop_hoa_nhap else 'Môi trường đại trà.'}
4. Hoạt động bổ sung từ GV: {hoat_dong}

Trả về thẳng nội dung giáo án hoàn chỉnh dưới dạng Markdown sạch sẽ từ dòng đầu tiên, không chào hỏi, không giải thích ngoài lề.
"""
