# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (CẤU TRÚC DỮ LIỆU NGUỒN & CHỐNG CHUNG CHUNG)
FILE: views/xd_khbd_data.py
(Bản khóa chốt Metadata và Tiêm Kỷ luật thép tuyệt đối)
============================================================
"""

import streamlit as st
import os
import re
import json
import logging
import base64
from docx import Document
from io import BytesIO

logger = logging.getLogger(__name__)

NLS_GV_VAN_BAN_MAC_DINH = "Thông tư 18/2026/TT-BGDĐT"

MODE_LABELS = {
    "chinh_sua": "Chỉnh sửa và nâng cấp giáo án gốc",
    "tu_dong": "Tự động soạn từ SGK",
}

MIN_SOURCE_CHARS = 100

def init_session_state():
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

KHUNG_NLS_GV = {
    "1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "Sử dụng được các chức năng và công cụ cơ bản của nền tảng quản lí học tập (LMS).",
            "Thành thạo": "Xây dựng được kế hoạch bài dạy theo tiếp cận công nghệ, thiết kế hoạt động kết hợp.",
            "Nâng cao": "Sáng tạo và đổi mới các mô hình dạy học ứng dụng công nghệ số."
        }
    },
    "2. KIỂM TRA, ĐÁNH GIÁ": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": "Sử dụng công cụ tạo bài kiểm tra online đơn giản.",
            "Thành thạo": "Sử dụng các công cụ số phổ biến để đánh giá quá trình và tổng kết."
        }
    }
}

KHUNG_NLS_HS = {
    "1. Sử dụng thông tin và dữ liệu số": {
        "1.1. Tìm kiếm và chọn lọc": {
            "Mức 1": "Biết sử dụng công cụ tìm kiếm cơ bản để thu thập thông tin học tập.",
            "Mức 2": "Biết đánh giá độ tin cậy và nguồn gốc thông tin trên Internet."
        }
    },
    "2. Giao tiếp và hợp tác trực tuyến": {
        "2.1. Tương tác qua môi trường số": {
            "Mức 1": "Biết sử dụng email, chat để trao đổi học tập.",
            "Mức 2": "Biết sử dụng hiệu quả các nền tảng học tập nhóm."
        }
    },
    "3. Sáng tạo nội dung số": {
        "3.1. Phát triển nội dung số": {
            "Mức 1": "Biết soạn thảo văn bản và trình chiếu cơ bản.",
            "Mức 2": "Biết thiết kế học liệu số đơn giản phục vụ học tập."
        }
    },
    "4. An toàn trong môi trường số": {
        "4.1. Bảo vệ thiết bị và dữ liệu cá nhân": {
            "Mức 1": "Biết đặt mật khẩu mạnh và bảo vệ tài khoản.",
            "Mức 2": "Biết nhận diện nguy cơ mất an toàn thông tin và lừa đảo trực tuyến."
        }
    },
    "5. Giải quyết vấn đề bằng công nghệ số": {
        "5.1. Sáng tạo giải pháp học tập": {
            "Mức 1": "Biết sử dụng công cụ số giải quyết nhiệm vụ.",
            "Mức 2": "Ứng dụng công nghệ giải quyết vấn đề thực tiễn."
        }
    }
}

def get_nls_framework(loai_khung): 
    return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS

def get_nls_domains(loai_khung): 
    return list(get_nls_framework(loai_khung).keys())

def get_nls_components(loai_khung, linh_vuc): 
    return list(get_nls_framework(loai_khung).get(linh_vuc, {}).keys())

def get_nls_levels(loai_khung, linh_vuc, thanh_phan): 
    return list(get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).keys())

def get_nls_content(loai_khung, linh_vuc, thanh_phan, muc_do): 
    return get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).get(muc_do, "")

def add_nls():
    linh_vuc = safe_text(st.session_state.get("khbd_nls_linh_vuc", ""))
    thanh_phan = safe_text(st.session_state.get("khbd_nls_thanh_phan", ""))
    muc_do = safe_text(st.session_state.get("khbd_nls_muc_do", ""))
    noi_dung = safe_text(st.session_state.get("khbd_nls_noi_dung", ""))
    
    if not noi_dung: 
        return
        
    van_ban = NLS_GV_VAN_BAN_MAC_DINH if st.session_state.get("khbd_loai_khung_nls") == "Giáo viên (Thông tư 18)" else "Khung DigComp"
    item = {"van_ban": van_ban, "linh_vuc": linh_vuc, "thanh_phan": thanh_phan, "muc_do": muc_do, "noi_dung": noi_dung}
    if item not in st.session_state.khbd_nls_list: 
        st.session_state.khbd_nls_list.append(item)

def format_nls():
    items = st.session_state.get("khbd_nls_list", [])
    if not items:
        return "- Năng lực 1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ > 1.1. Dạy học và giáo dục trong môi trường số (Thành thạo): Xây dựng kế hoạch bài dạy theo tiếp cận công nghệ."
    return "\n".join([f"- Năng lực {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}" for item in items])

def safe_text(value):
    if value is None: 
        return ""
    text = str(value).replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\r", "").replace("\t", " ")
    return re.sub(r"[ ]{2,}", " ", text).strip()

def diagnose_source_quality(text, source_name="Tài liệu nguồn"):
    text = safe_text(text)
    if len(text) < MIN_SOURCE_CHARS:
        return {"status": "insufficient", "message": f"{source_name} quá ngắn hoặc không đọc được chữ."}
    return {"status": "valid", "message": "Dữ liệu hợp lệ."}

def parse_pdf_structured(uploaded_file, range_str=""):
    if uploaded_file is None:
        return {"source_name": "unknown", "pages": []}
    content = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    file_name = getattr(uploaded_file, 'name', 'document.pdf')
    pages_data = []
    try:
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        target_pages = set()
        if range_str.strip():
            for part in range_str.split(','):
                if '-' in part:
                    try:
                        start, end = map(int, part.split('-'))
                        for p in range(start, end + 1): 
                            target_pages.add(p - 1)
                    except: 
                        pass
                else:
                    try: 
                        target_pages.add(int(part.strip()) - 1)
                    except: 
                        pass
        for i in range(len(doc)):
            if target_pages and i not in target_pages: 
                continue
            page = doc[i]
            page_text = safe_text(page.get_text("text"))
            
            page_images = []
            for img_idx, img in enumerate(page.get_images(full=True)):
                try:
                    base_image = doc.extract_image(img[0])
                    page_images.append({
                        "id": f"IMG_P{i+1}_{img_idx+1}",
                        "page": i + 1,
                        "ext": base_image["ext"],
                        "base64": base64.b64encode(base_image["image"]).decode("utf-8")
                    })
                except: 
                    pass
                
            page_tables = []
            try:
                tabs = page.find_tables()
                if tabs and tabs.tables:
                    for t_idx, tab in enumerate(tabs.tables):
                        extracted_df = tab.extract()
                        if extracted_df and len(extracted_df) > 0:
                            page_tables.append({
                                "id": f"TAB_P{i+1}_{t_idx+1}",
                                "page": i + 1,
                                "headers": [str(c) if c is not None else "" for c in extracted_df[0]],
                                "rows": [[str(c) if c is not None else "" for c in r] for r in extracted_df[1:]]
                            })
            except: 
                pass
            
            pages_data.append({"page_number": i + 1, "text": page_text, "images": page_images, "tables": page_tables, "figures": [], "charts": []})
    except Exception as e:
        logger.error(f"Lỗi đọc cấu trúc PDF: {e}")
    return {"source_name": file_name, "pages": pages_data}

def parse_docx_structured(uploaded_file):
    if uploaded_file is None: 
        return {"source_name": "unknown", "pages": []}
    file_name = getattr(uploaded_file, 'name', 'document.docx')
    paragraphs_text = []
    tables_data = []
    try:
        source = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
        doc = Document(BytesIO(source))
        for p in doc.paragraphs:
            if p.text.strip(): 
                paragraphs_text.append(p.text.strip())
        for t_idx, table in enumerate(doc.tables):
            rows_raw = [[cell.text.strip().replace('\n', ' ') for cell in row.cells] for row in table.rows]
            if rows_raw:
                tables_data.append({"id": f"TAB_DOCX_{t_idx+1}", "page": 1, "headers": rows_raw[0], "rows": rows_raw[1:] if len(rows_raw) > 1 else []})
    except Exception as e:
        logger.error(f"Lỗi đọc cấu trúc DOCX: {e}")
    return {"source_name": file_name, "pages": [{"page_number": 1, "text": "\n".join(paragraphs_text), "images": [], "tables": tables_data, "figures": [], "charts": []}]}

def build_intermediate_knowledge_source(structured_data):
    if not structured_data or not structured_data.get("pages"): 
        return "Không có dữ liệu nguồn."
    source_lines = []
    for page in structured_data["pages"]:
        p_num = page["page_number"]
        source_lines.append(f"=== TRANG {p_num} ===")
        if page["text"]: 
            source_lines.append(f"[TEXT - Trang {p_num}]\n{page['text']}")
        for tab in page.get("tables", []):
            source_lines.append(f"BẢNG DỮ LIỆU [TABLE: {tab['id']}]\nHeaders: {' | '.join(tab['headers'])}\nRows:\n" + "\n".join([' | '.join(r) for r in tab['rows']]))
        for img in page.get("images", []): 
            source_lines.append(f"HÌNH MINH HỌA [IMAGE: {img['id']}]")
    return "\n\n".join(source_lines)

def read_pdf(uploaded_file, range_str=""): 
    return "\n".join([p["text"] for p in parse_pdf_structured(uploaded_file, range_str)["pages"]])

def read_docx_ordered(source): 
    return "\n".join([p["text"] for p in parse_docx_structured(source)["pages"]])

def read_multiple_files(files, range_str="", is_pdf_target=False):
    combined = {"source_name": "multi_files", "pages": []}
    offset = 0
    for f in files or []:
        if f.name.lower().endswith('.pdf'):
            parsed = parse_pdf_structured(f, range_str) 
        else:
            parsed = parse_docx_structured(f)
        for p in parsed["pages"]:
            p["page_number"] += offset
            combined["pages"].append(p)
        offset += len(parsed["pages"])
        
    # LƯU TRỮ METADATA VÀO BỘ NHỚ TRUNG TÂM ĐỂ EXPORT_WORD SỬ DỤNG
    st.session_state["current_source_metadata"] = combined
    
    return build_intermediate_knowledge_source(combined)

def generate_ai(client, prompt, model_name="3.5 Flash"):
    system_instruction = r"""
[KỶ LUẬT THÉP CẤP ĐỘ CAO NHẤT - HỦY BỎ MỌI THÓI QUEN CỦA AI]:

1. CẤM TUYỆT ĐỐI DÙNG DẤU BACKTICK (`) CHO CÔNG THỨC TOÁN:
- Bạn đang dùng `sin i / sin r` hoặc `n21` -> ĐÂY LÀ LỖI RẤT NẶNG.
- BẮT BUỘC dùng dấu $...$ cho TẤT CẢ công thức Toán, Lý, Hóa.
- ĐÚNG: $\frac{\sin i}{\sin r}$
- ĐÚNG: $n_{21}$
- ĐÚNG: $c = 3 \times 10^8 \text{ m/s}$

2. ÉP BUỘC CHÈN HÌNH ẢNH VÀ BẢNG:
- NGUYÊN TẮC: Phần mềm chỉ hiển thị được Ảnh và Bảng khi bạn viết đúng thẻ ID.
- Nếu Nguồn Kiến Thức có ghi `HÌNH MINH HỌA [IMAGE: ID...]`, bạn CẤM được phép viết "Giáo viên mô tả hình vẽ".
- BẠN BẮT BUỘC PHẢI COPY CHÍNH XÁC THẺ `[IMAGE: ID]` VÀ `[TABLE: ID]` VÀO NỘI DUNG BÀI SOẠN.
- Ví dụ: Học sinh quan sát hình dưới đây: [IMAGE: IMG_P1_1]

3. CẤM TỰ Ý ĐÁNH SỐ THỨ TỰ HOẠT ĐỘNG:
- BẮT BUỘC Giữ nguyên Cấu trúc Hoạt động cốt lõi: 
  **Hoạt động 1: MỞ ĐẦU**
  **Hoạt động 2: HÌNH THÀNH KIẾN THỨC MỚI**
  **Hoạt động 3: LUYỆN TẬP**
  **Hoạt động 4: VẬN DỤNG**
- CẤM TỰ CHIA NHỎ: Không được tự ý chế ra "Hoạt động 1: Tìm hiểu...", "Hoạt động 2: Định nghĩa..." nằm bên trong phần "HÌNH THÀNH KIẾN THỨC MỚI".
"""
    full_prompt = system_instruction + "\n\n" + prompt
    api_key = st.session_state.get("user_api_key", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    
    try: 
        api_key = api_key or st.secrets.get("GEMINI_API_KEY", "").strip()
    except: 
        pass

    text_out = ""
    try:
        if api_key.startswith("sk-") or "proj-" in api_key:
            import openai
            oai_client = openai.OpenAI(api_key=api_key)
            response = oai_client.chat.completions.create(
                model="gpt-4o" if "Pro" in model_name else "gpt-4o-mini",
                messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}],
                max_tokens=8192
            )
            text_out = response.choices[0].message.content.strip()
        else:
            import google.generativeai as genai
            genai.configure(api_key=api_key or "AIzaSy_dummy")
            model = genai.GenerativeModel(model_name="gemini-2.5-pro" if "Pro" in model_name else "gemini-2.5-flash")
            response = model.generate_content(full_prompt)
            text_out = getattr(response, "text", "").strip()
    except Exception as e:
        logger.error(f"AI Generation Error: {e}")
        raise RuntimeError(f"Lỗi kết nối AI: {e}")

    if not text_out: 
        raise RuntimeError("Không thể nhận phản hồi từ AI.")
        
    if "# TÊN BÀI HỌC:" in text_out: 
        text_out = text_out[text_out.find("# TÊN BÀI HỌC:"):]
        
    text_out = text_out.replace("**", "")
    text_out = re.sub(r'([^\n])\s*([a-d]\)\s+)', r'\1\n\n\2', text_out)
    text_out = re.sub(r'([^\n])\s*(\*(?:Chuyển giao nhiệm vụ học tập|Thực hiện nhiệm vụ học tập|Báo cáo kết quả và thảo luận|Kết luận)[^:\n]*:)', r'\1\n\n\2', text_out)
    
    return text_out

def validate_khbd_result(text):
    if not text or len(text) < 500: 
        return False, "Nội dung giáo án quá ngắn hoặc trống."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, nls_str, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, mode, so_tiet):
    source = safe_text(noi_dung_chinh)[:35000]
    ga_block = f"--- GIÁO ÁN CŨ ĐỂ CHỈNH SỬA ---\n{safe_text(noi_dung_ga)[:10000]}\n" if mode == "chinh_sua" else ""
    return f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\nNHIỆM VỤ: SOẠN KẾ HOẠCH BÀI DẠY {so_tiet} TIẾT BÁM SÁT NGUỒN SAU:\n\n--- NGUỒN KIẾN THỨC TRUNG GIAN (CHỨA TEXT, ẢNH VÀ BẢNG) ---\n{source}\n\n{ga_block}"
