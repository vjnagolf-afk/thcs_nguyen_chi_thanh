# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (ÉP CHI TIẾT SƯ PHẠM SGK)
FILE: views/xd_khbd_data.py
============================================================
"""

import streamlit as st
import os
import re
import json
import pandas as pd
import PyPDF2
from docx import Document
from pathlib import Path
from io import BytesIO

# ============================================================
# 1. HẰNG SỐ VÀ CẤU HÌNH PHÁP LÝ CHUẨN
# ============================================================
NLS_GV_VAN_BAN_MAC_DINH = "18/2026/TT-BGDĐT"

MODE_LABELS = {
    "chinh_sua": "Chỉnh sửa và nâng cấp giáo án gốc",
    "tao_moi": "Soạn mới hoàn toàn từ tài liệu SGK",
    "tu_dong": "Soạn mới hoàn toàn từ tài liệu SGK"
}

KHUNG_NLS_GV = {
    "1. Miền 1: Tổ chức dạy học, giáo dục trong môi trường số": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "Sử dụng thiết bị cơ bản (máy tính, máy chiếu, bảng tương tác); Dùng ứng dụng di động giáo dục đơn giản.",
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
# 2. API NỘI BỘ QUẢN LÝ NĂNG LỰC SỐ
# ============================================================
def get_nls_framework(loai_khung):
    return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS

def get_nls_domains(loai_khung):
    fw = get_nls_framework(loai_khung)
    return list(fw.keys())

def get_nls_components(loai_khung, linh_vuc):
    fw = get_nls_framework(loai_khung)
    if linh_vuc in fw:
        return list(fw[linh_vuc].keys())
    return []

def get_nls_levels(loai_khung, linh_vuc, thanh_phan):
    fw = get_nls_framework(loai_khung)
    if linh_vuc in fw and thanh_phan in fw[linh_vuc]:
        return list(fw[linh_vuc][thanh_phan].keys())
    return []

def get_nls_content(loai_khung, linh_vuc, thanh_phan, muc_do):
    fw = get_nls_framework(loai_khung)
    try:
        return fw[linh_vuc][thanh_phan][muc_do]
    except Exception:
        return ""

# ============================================================
# 3. KHỞI TẠO SESSION STATE & RESET TOÀN DIỆN
# ============================================================
def init_session_state():
    defaults = {
        "khbd_mode": "tu_dong",
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

def reset_toan_bo_khbd():
    st.session_state["khbd_result"] = None
    st.session_state["khbd_nls_list"] = []
    st.session_state["khbd_hoat_dong_list"] = []
    st.session_state["khbd_nls_noi_dung"] = ""
    st.session_state["khbd_mode"] = "tu_dong"
    st.session_state["khbd_processing"] = False

def set_mode(mode: str):
    if mode not in MODE_LABELS:
        raise ValueError(f"Chế độ soạn không hợp lệ: {mode}")
    st.session_state.khbd_mode = mode

# ============================================================
# 4. LÀM SẠCH VĂN BẢN VÀ ĐỌC TỆP CHUẨN HÓA ĐA ĐỊNH DẠNG
# ============================================================
def safe_text(value):
    if value is None: 
        return ""
    if not isinstance(value, str):
        value = str(value)
    text = value.replace("\x00", "")
    text = re.sub(r"[\r\t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

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
            cleaned = safe_text(text)
            if cleaned:
                result.append(f"\n[PDF - Trang {index}]\n{cleaned}")
    except Exception as e:
        result.append(f"[LỖI ĐỌC PDF: {str(e)}]")
    return "\n".join(result)

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
                p = Paragraph(element, doc)
                text = safe_text(p.text)
                if text:
                    result.append(text)
            elif element.tag.endswith('tbl') or element.tag.endswith('}tbl'):
                from docx.table import Table
                table = Table(element, doc)
                result.append("\n[Bảng dữ liệu]")
                for row in table.rows:
                    cells = [safe_text(cell.text).replace("\n", " ") for cell in row.cells]
                    row_text = " | ".join(cells)
                    if row_text.strip():
                        result.append(row_text)
    except Exception as e:
        result.append(f"[LỖI ĐỌC DOCX: {str(e)}]")
    return "\n".join(result)

def read_excel_structured(uploaded_file):
    result = []
    try:
        sheets = pd.read_excel(uploaded_file, sheet_name=None)
        for sheet_name, dataframe in sheets.items():
            result.append(f"\n[Phân phối chương trình - Sheet: {sheet_name}]")
            dataframe = dataframe.fillna("")
            records = dataframe.to_dict(orient="records")
            for idx, rec in enumerate(records, start=1):
                clean_rec = {str(k).strip(): safe_text(v) for k, v in rec.items() if str(v).strip()}
                if clean_rec:
                    result.append(f"Dòng {idx}: " + json.dumps(clean_rec, ensure_ascii=False))
    except Exception as e:
        result.append(f"[LỖI ĐỌC EXCEL: {str(e)}]")
    return "\n".join(result)

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
    return "\n".join(result)

def read_template_local(path="templates/KHBD_Mau.docx"):
    if not os.path.exists(path): return ""
    try:
        with open(path, "rb") as f:
            return read_docx_ordered(f)
    except Exception:
        return ""

# ============================================================
# 5. CALLBACKS & FORMATORS
# ============================================================
def add_nls():
    linh_vuc = safe_text(st.session_state.get("khbd_nls_linh_vuc", ""))
    thanh_phan = safe_text(st.session_state.get("khbd_nls_thanh_phan", ""))
    muc_do = safe_text(st.session_state.get("khbd_nls_muc_do", ""))
    noi_dung = safe_text(st.session_state.get("khbd_nls_noi_dung", ""))
    if not noi_dung: return
    
    van_ban_su_dung = NLS_GV_VAN_BAN_MAC_DINH if st.session_state.get("khbd_loai_khung_nls") == "Giáo viên (Thông tư 18)" else "DigComp"
    item = {
        "van_ban": van_ban_su_dung,
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
# 6. AI ENGINE, VALIDATION & BUILD PROMPT (ÉP CHI TIẾT SÂU SGK)
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
    if result is None: 
        return ""
    if isinstance(result, str): 
        return result.strip()
    
    if isinstance(result, dict):
        try:
            if "choices" in result and len(result["choices"]) > 0:
                msg = result["choices"][0].get("message", {})
                if "content" in msg:
                    return str(msg["content"]).strip()
        except Exception:
            pass

        try:
            if "candidates" in result and len(result["candidates"]) > 0:
                parts = result["candidates"][0].get("content", {}).get("parts", [])
                if len(parts) > 0 and "text" in parts[0]:
                    return str(parts[0]["text"]).strip()
        except Exception:
            pass

        for key in ["text", "content", "response", "output", "answer"]:
            if key in result: 
                val = result[key]
                if isinstance(val, str):
                    return val.strip()
                elif isinstance(val, list):
                    texts = []
                    for item in val:
                        if isinstance(item, dict) and "text" in item:
                            texts.append(str(item["text"]))
                    if texts:
                        return "\n".join(texts).strip()
                elif isinstance(val, dict):
                    if "parts" in val:
                        parts = val["parts"]
                        if isinstance(parts, list) and len(parts) > 0 and "text" in parts[0]:
                            return str(parts[0]["text"]).strip()
                            
    return str(result).strip()

def generate_ai(ai_engine, prompt):
    if ai_engine is None: 
        raise RuntimeError("Chưa truyền AI Engine.")
    if hasattr(ai_engine, "generate_text"):
        return normalize_ai_result(ai_engine.generate_text(prompt))
    if hasattr(ai_engine, "generate"):
        return normalize_ai_result(ai_engine.generate(prompt))
    raise RuntimeError("AI Engine không phản hồi.")

def validate_khbd_result(text):
    if not text or len(text.strip()) < 100:
        return False, "Nội dung trả về quá ngắn hoặc rỗng."
    
    required_keywords = ["MỤC TIÊU", "THIẾT BỊ DẠY HỌC", "TIẾN TRÌNH DẠY HỌC"]
    for kw in required_keywords:
        if kw not in text.upper():
            return False, f"Thiếu phần bắt buộc theo chuẩn 5512: {kw}"
            
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, noi_dung_ppct, noi_dung_ai, noi_dung_mau, nls, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, hoat_dong, mode):
    if mode not in MODE_LABELS:
        raise ValueError(f"Chế độ soạn không hợp lệ: {mode}")
    mode_text = MODE_LABELS[mode]

    task_config_content = load_task_config()

    safe_noi_dung_ai = safe_text(noi_dung_ai)
    ai_block = f"\n- Tài liệu / Hướng dẫn AI bổ sung: {safe_noi_dung_ai}" if safe_noi_dung_ai else ""

    safe_nhu_cau = safe_text(nhu_cau_hoa_nhap)
    if tich_hop_hoa_nhap and safe_nhu_cau:
        hoa_nhap_block = f"\n- Đối tượng học sinh hòa nhập cần hỗ trợ đặc biệt ({safe_nhu_cau}): Bắt buộc phải thiết kế phương án điều chỉnh trực tiếp vào mục Tổ chức thực hiện."
    else:
        hoa_nhap_block = "Môi trường học tập đại trà."

    safe_hoat_dong = safe_text(hoat_dong)
    hoat_dong_block = f"\n- Hoạt động bổ sung theo yêu cầu giáo viên: {safe_hoat_dong}" if safe_hoat_dong else ""

    ga_block = ""
    if mode == "chinh_sua" and noi_dung_ga.strip():
        ga_block = f"""
----------------------------------------------------------------------------------
GIÁO ÁN GỐC (DÙNG ĐỂ KẾ THỪA CẤU TRÚC VÀ TỐI ƯU):
----------------------------------------------------------------------------------
{noi_dung_ga}
"""

    return f"""
{task_config_content}

==================================================================================
⚙️ ĐIỀU HƯỚNG THỰC THI & PHÂN BỔ THỜI LƯỢNG
==================================================================================
- Chế độ thực thi: {mode_text}
- Thông tin thời lượng và bài học: {thong_tin}
- YÊU CẦU PHÂN BỔ THỜI LƯỢNG: Phải tính toán khối lượng kiến thức khớp tuyệt đối với số tiết được giao. Nếu bài từ 2 tiết trở lên, bắt buộc phải phân tách rõ ràng tiến trình chi tiết theo từng TIẾT (Ví dụ: ### TIẾT 1, ### TIẾT 2).

==================================================================================
🛡️ KNOWLEDGE SCOPE & QUY TẮC CHỐNG SƠ SÀI (BẮT BUỘC TRÍCH XUẤT SGK)
================================================================================--
TUYỆT ĐỐI KHÔNG VIẾT CHUNG CHUNG. Mọi mục **Nội dung** và **Sản phẩm** trong tiến trình dạy học phải bóc tách TRỰC TIẾP từ "1. NGUỒN KIẾN THỨC CHÍNH (SGK)" dưới đây:
- **Nội dung**: Phải ghi rõ tên hoạt động, trích nguyên văn hoặc chi tiết câu hỏi/ví dụ/thực hành có trong SGK.
- **Sản phẩm**: Phải trình bày tường minh lời giải, đáp án chi tiết, công thức hoặc kết quả học sinh cần đạt được. Không được ghi chung chung kiểu "Học sinh hoàn thành bài tập".

----------------------------------------------------------------------------------
1. NGUỒN KIẾN THỨC CHÍNH (SGK / TÀI LIỆU BÀI HỌC):
----------------------------------------------------------------------------------
{noi_dung_chinh}
{ga_block}
----------------------------------------------------------------------------------
2. TÀI LIỆU CHỈ ĐẠO BỔ SUNG & PHÂN PHỐI CHƯƠNG TRÌNH:
----------------------------------------------------------------------------------
- Phân phối chương trình: {noi_dung_ppct}
{ai_block}

----------------------------------------------------------------------------------
3. YÊU CẦU TÍCH HỢP & ĐẶC THÙ:
----------------------------------------------------------------------------------
1. Năng lực số: {nls}
2. Tích hợp AI sư phạm: {'Có tích hợp công cụ AI hỗ trợ hoạt động nhận thức của học sinh.' if tich_hop_ai else 'Không bắt buộc.'}
3. Giáo dục hòa nhập: {hoa_nhap_block}
{hoat_dong_block}

==================================================================================
📋 SCHEMA ĐẦU RA BẮT BUỘC (ĐỂ TƯƠNG THÍCH BỘ XUẤT WORD & PARSER TRƯỜNG)
==================================================================================
Giáo án đầu ra bắt buộc phải tuân thủ nghiêm ngặt cấu trúc Markdown sau đây (Sử dụng heading chuẩn, tuyệt đối không biến đổi tên mục chính):

# [TÊN BÀI HỌC ĐƯỢC XÁC ĐỊNH TỪ SGK]

## I. MỤC TIÊU
1. Về kiến thức: ...
2. Về năng lực: ...
3. Về phẩm chất: ...

## II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
1. Đối với giáo viên: ...
2. Đối với học sinh: ...

## III. TIẾN TRÌNH DẠY HỌC
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
- Mục tiêu: ...
- Nội dung: ...
- Sản phẩm: ...
- Tổ chức thực hiện:
  + Bước 1: Chuyển giao nhiệm vụ: ...
  + Bước 2: Thực hiện nhiệm vụ: ...
  + Bước 3: Báo cáo, thảo luận: ...
  + Bước 4: Kết luận, nhận định: ...

### Hoạt động 3: Luyện tập
- Mục tiêu: ...
- Nội dung: ...
- Sản phẩm: ...
- Tổ chức thực hiện:
  + Bước 1: Chuyển giao nhiệm vụ: ...
  + Bước 2: Thực hiện nhiệm vụ: ...
  + Bước 3: Báo cáo, thảo luận: ...
  + Bước 4: Kết luận, nhận định: ...

### Hoạt động 4: Vận dụng
- Mục tiêu: ...
- Nội dung: ...
- Sản phẩm: ...
- Tổ chức thực hiện:
  + Bước 1: Chuyển giao nhiệm vụ: ...
  + Bước 2: Thực hiện nhiệm vụ: ...
  + Bước 3: Báo cáo, thảo luận: ...
  + Bước 4: Kết luận, nhận định: ...

----------------------------------------------------------------------------------
MẪU KHBD THAM KHẢO CỦA TRƯỜNG (DÙNG ĐỂ ĐỒNG BỘ ĐẶC TẢ TRÌNH BÀY):
----------------------------------------------------------------------------------
{noi_dung_mau}

Trả về thẳng nội dung giáo án hoàn chỉnh bằng Markdown sạch sẽ bắt đầu ngay từ tiêu đề bài học. Không chào hỏi, không giải thích ngoài lề.
"""
