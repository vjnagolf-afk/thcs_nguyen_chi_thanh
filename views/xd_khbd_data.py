# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (SIÊU CHI TIẾT SƯ PHẠM SGK)
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
# 1. KHUNG NĂNG LỰC SỐ (TT18 & DIGCOMP)
# ============================================================
KHUNG_NLS_GV = {
    "1. Miền 1: Tổ chức dạy học, giáo dục trong môi trường số": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "Sử dụng thiết bị cơ bản (máy tính, máy chiếu); Dùng ứng dụng di động giáo dục đơn giản.",
            "Thành thạo": "Lựa chọn, tích hợp học liệu số vào kế hoạch hoạt động; Thiết kế hoạt động học tập tương tác.",
            "Nâng cao": "Sáng tạo mô hình giáo dục ứng dụng công nghệ mới; Hướng dẫn đồng nghiệp sử dụng thiết bị số."
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": "Hướng dẫn học sinh thao tác cơ bản, an toàn trên thiết bị số có giám sát.",
            "Thành thạo": "Quan sát, hỗ trợ kịp thời khi học sinh gặp khó khăn tương tác công nghệ.",
            "Nâng cao": "Phát triển phương pháp hỗ trợ học tập trên nền tảng công nghệ tại nhà."
        }
    },
    "2. Miền 2: Kiểm tra, đánh giá": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": "Sử dụng thiết bị số ghi lại sản phẩm/khoảnh khắc học tập của học sinh.",
            "Thành thạo": "Thiết kế hoạt động đánh giá kĩ năng qua công nghệ và lưu trữ minh chứng."
        }
    },
    "6. Miền 6: Trí tuệ nhân tạo (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": "Sử dụng công cụ AI tạo sinh cơ bản hỗ trợ soạn thảo, tìm kiếm ý tưởng.",
            "Thành thạo": "Khai thác công cụ AI chuyên biệt tạo học liệu tương tác, cá nhân hóa."
        }
    }
}

KHUNG_NLS_HS = {
    "1. Thông tin và dữ liệu số": {
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu": {
            "Mức 1": "Xác định nhu cầu thông tin, tìm kiếm dữ liệu đơn giản trong môi trường số.",
            "Mức 2": "Sử dụng kĩ thuật tìm kiếm nâng cao để lấy dữ liệu, thông tin chính xác."
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
# 3. ĐỌC TỆP VÀ LỌC TRANG THÔNG MINH
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
                result.append(f"\n[Trang {index}]\n{text.strip()}")
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
            result.append(f"\n[Bảng {index}]")
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
            result.append(f"\n[Sheet: {sheet_name}]")
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
        return ""
    except Exception as e:
        return f"[LỖI ĐỌC FILE: {e}]"

def read_multiple_files(files, range_str=""):
    result = []
    for uploaded_file in files or []:
        result.append(f"\n--- TÀI LIỆU NGUỒN: {uploaded_file.name} ---")
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
            return "\n".join(result)
    except Exception:
        return ""

# ============================================================
# 4. CALLBACKS & FORMATORS
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
        result.append(f"- [{item['van_ban']}] {item['linh_vuc']} ({item['muc_do']}): {item['noi_dung']}")
    return "\n".join(result)

def add_activity():
    value = st.session_state.get("khbd_new_activity", "").strip()
    if value and value not in st.session_state.khbd_hoat_dong_list:
        st.session_state.khbd_hoat_dong_list.append(value)
    st.session_state.khbd_new_activity = ""

# ============================================================
# 5. ĐỌC TASK CONFIG & XÂY DỰNG PROMPT TRÍCH XUẤT SÂU TỪ SGK
# ============================================================
def load_task_config():
    config_path = "prompts/task_config_khbd.txt"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "BẠN LÀ CHUYÊN GIA SƯ PHẠM VÀ THẨM ĐỊNH CHƯƠNG TRÌNH GDPT 2018. BẮT BUỘC SOẠN GIÁO ÁN CHUẨN PHỤ LỤC 4 CÔNG VĂN 5512."

def normalize_ai_result(result):
    if result is None: return ""
    if isinstance(result, str): return result.strip()
    if isinstance(result, dict):
        for key in ["text", "content", "response", "output", "answer"]:
            if key in result: return str(result[key]).strip()
    return str(result).strip()

def generate_ai(ai_engine, prompt):
    if ai_engine is None: raise RuntimeError("Chưa truyền AI Engine.")
    if hasattr(ai_engine, "generate_text"):
        return normalize_ai_result(ai_engine.generate_text(prompt))
    if hasattr(ai_engine, "generate"):
        return normalize_ai_result(ai_engine.generate(prompt))
    raise RuntimeError("AI Engine không phản hồi.")

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ppct, noi_dung_ai, noi_dung_mau, nls, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, hoat_dong, mode):
    task_config_content = load_task_config()

    return f"""
{task_config_content}

==================================================================================
🔎 QUY TẮC BẮT BUỘC: TRÍCH DẪN TRỰC TIẾP VÀ SẢN PHẨM HÓA TỪ SGK
==================================================================================
1. BẠN PHẢI ĐỌC KỸ "TÀI LIỆU SGK / NGUỒN CỐT LÕI" DƯỚI ĐÂY. 
2. TRONG TỪNG HOẠT ĐỘNG, BẮT BUỘC PHẢI TRÍCH XUẤT CÁC VÍ DỤ, HĐTP (Hoạt động thực hiện/khám phá), CÂU HỎI HOẠT ĐỘNG (Ví dụ: Hoạt động 1, Câu hỏi..., Ví dụ 1...) CÓ THẬT TRONG SÁCH vào phần **Nội dung**.
3. TỪ DỮ LIỆU ĐÓ, PHẢI XÂY DỰNG PHẦN **Sản phẩm** LÀ LỜI GIẢI, ĐÁP ÁN HOÀN CHỈNH, CHI TIẾT TỪNG BƯỚC cho các câu hỏi và ví dụ vừa trích xuất đó. Tuyệt đối không được tóm tắt chung chung.

==================================================================================
🎯 ĐIỀU KHIỂN THỜI LƯỢNG VÀ PHÂN BỔ TIẾT DẠY
==================================================================================
- Thông tin thời lượng bài học: {thong_tin}
- Phân bổ khối lượng kiến thức, số lượng hoạt động khớp tuyệt đối với số tiết được giao (Ví dụ 3 tiết thì phải chia rõ các phần kiến thức trọng tâm cho Tiết 1, Tiết 2, Tiết 3).

==================================================================================
📐 QUY TẮC ĐỊNH DẠNG TƯƠNG THÍCH BỘ XUẤT FILE WORD VÀ MẪU TRƯỜNG
==================================================================================
- Sử dụng tiêu đề Markdown chuẩn (`#`, `##`, `###`).
- Bảng biểu phải dùng định dạng Markdown table chuẩn (`| Cột 1 | Cột 2 |`).
- Công thức toán học, hóa học viết tuyến tính rõ ràng (x^2, H₂O, CO₂). Tránh dùng thẻ LaTeX phức tạp.
- Mẫu giáo án tham khảo của trường để đồng bộ cấu trúc:
{noi_dung_mau}

==================================================================================
TÀI LIỆU SGK / NGUỒN CỐT LÕI (BẮT BUỘC PHẢI BÓC TÁCH NỘI DUNG TỪ ĐÂY):
==================================================================================
{noi_dung_chinh}

==================================================================================
DỮ LIỆU ĐẦU VÀO ĐỂ BIÊN SOẠN:
- Thông tin chung: {thong_tin}
- PPCT: {noi_dung_ppct}
- Tích hợp Năng lực số: {nls}
- Tích hợp AI / Hòa nhập: {'Tích hợp AI sư phạm' if tich_hop_ai else ''} | Đối tượng hòa nhập ({nhu_cau_hoa_nhap})
- Yêu cầu thêm từ giáo viên: {hoat_dong}

Trả về kết quả hoàn chỉnh bằng Markdown sạch sẽ bắt đầu ngay từ tiêu đề bài học. Không giải thích thêm.
"""
