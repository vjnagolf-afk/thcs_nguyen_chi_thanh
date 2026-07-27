# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: views/xd_de_kt_data.py
Logic xử lý Xây dựng Đề kiểm tra (Đọc dữ liệu, Bóc tách Metadata, Gọi AI)
Tích hợp Kỷ luật thép: Toán OMML ($), Ảnh [IMAGE:ID], Bảng [TABLE:ID].
============================================================
"""

import os
import re
import json
import logging
import base64
from io import BytesIO
import streamlit as st
from docx import Document

logger = logging.getLogger(__name__)

# ============================================================
# 1. QUẢN LÝ SESSION STATE
# ============================================================
def init_session_state_de_kt():
    defaults = {
        "dkt_result": None,
        "dkt_processing": False,
        "current_dkt_metadata": {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_dkt_result():
    st.session_state["dkt_result"] = None
    st.session_state["current_dkt_metadata"] = {}

def safe_text(value):
    if value is None: 
        return ""
    text = str(value).replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\r", "").replace("\t", " ")
    return re.sub(r"[ ]{2,}", " ", text).strip()

# ============================================================
# 2. BỘ ĐỌC TÀI LIỆU CÓ CẤU TRÚC (TRÍCH XUẤT ẢNH & BẢNG)
# ============================================================
def parse_pdf_structured_dkt(uploaded_file):
    if uploaded_file is None:
        return {"source_name": "unknown", "pages": []}
    content = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    file_name = getattr(uploaded_file, 'name', 'document.pdf')
    pages_data = []
    
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=content, filetype="pdf")
        for i in range(len(doc)):
            page = doc[i]
            page_text = safe_text(page.get_text("text"))
            
            # Trích xuất ảnh
            page_images = []
            for img_idx, img in enumerate(page.get_images(full=True)):
                try:
                    base_image = doc.extract_image(img[0])
                    page_images.append({
                        "id": f"IMG_DKT_P{i+1}_{img_idx+1}",
                        "page": i + 1,
                        "ext": base_image["ext"],
                        "base64": base64.b64encode(base_image["image"]).decode("utf-8")
                    })
                except: 
                    pass
                
            # Trích xuất bảng
            page_tables = []
            try:
                tabs = page.find_tables()
                if tabs and tabs.tables:
                    for t_idx, tab in enumerate(tabs.tables):
                        extracted_df = tab.extract()
                        if extracted_df and len(extracted_df) > 0:
                            page_tables.append({
                                "id": f"TAB_DKT_P{i+1}_{t_idx+1}",
                                "page": i + 1,
                                "headers": [str(c) if c is not None else "" for c in extracted_df[0]],
                                "rows": [[str(c) if c is not None else "" for c in r] for r in extracted_df[1:]]
                            })
            except: 
                pass
            
            pages_data.append({
                "page_number": i + 1, 
                "text": page_text, 
                "images": page_images, 
                "tables": page_tables
            })
    except Exception as e:
        logger.error(f"Lỗi đọc PDF trong module Đề KT: {e}")
    return {"source_name": file_name, "pages": pages_data}

def parse_docx_structured_dkt(uploaded_file):
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
                tables_data.append({
                    "id": f"TAB_DKT_DOCX_{t_idx+1}", 
                    "page": 1, 
                    "headers": rows_raw[0], 
                    "rows": rows_raw[1:] if len(rows_raw) > 1 else []
                })
    except Exception as e:
        logger.error(f"Lỗi đọc DOCX trong module Đề KT: {e}")
    return {
        "source_name": file_name, 
        "pages": [{"page_number": 1, "text": "\n".join(paragraphs_text), "images": [], "tables": tables_data}]
    }

def read_multiple_files_dkt(files):
    combined = {"source_name": "multi_files", "pages": []}
    offset = 0
    for f in files or []:
        if f.name.lower().endswith('.pdf'):
            parsed = parse_pdf_structured_dkt(f) 
        else:
            parsed = parse_docx_structured_dkt(f)
        
        for p in parsed["pages"]:
            p["page_number"] += offset
            combined["pages"].append(p)
        offset += len(parsed["pages"])
        
    # LƯU TRỮ METADATA VÀO SESSION STATE ĐỂ MODULE XUẤT WORD NHẬN DIỆN
    st.session_state["current_dkt_metadata"] = combined
    
    # Render thành văn bản trung gian cho AI
    source_lines = []
    for page in combined["pages"]:
        p_num = page["page_number"]
        source_lines.append(f"=== TRANG {p_num} ===")
        if page["text"]: 
            source_lines.append(f"[TEXT - Trang {p_num}]\n{page['text']}")
        for tab in page.get("tables", []):
            source_lines.append(f"BẢNG DỮ LIỆU [TABLE: {tab['id']}]\nHeaders: {' | '.join(tab['headers'])}\nRows:\n" + "\n".join([' | '.join(r) for r in tab['rows']]))
        for img in page.get("images", []): 
            source_lines.append(f"HÌNH MINH HỌA [IMAGE: {img['id']}]")
            
    return "\n\n".join(source_lines)

# ============================================================
# 3. GỌI AI VỚI KỶ LUẬT THÉP
# ============================================================
def get_prompt_template():
    prompt_path = "prompt_de_kt.txt"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Bạn là chuyên gia giáo dục. Dựa vào tài liệu, hãy lập Ma trận, Bản đặc tả, Đề kiểm tra và Hướng dẫn chấm."

def generate_dkt_ai(model_name: str, config: dict, source_text: str):
    """
    config: dict chứa thông tin môn, lớp, thời gian, số lượng câu TN/TL, yêu cầu đặc biệt.
    """
    base_prompt = get_prompt_template()
    
    # Thay thế các placeholder nếu trong prompt có
    prompt = base_prompt.replace("{MON_HOC}", config.get("mon_hoc", ""))
    prompt = prompt.replace("{LOP_HOC}", config.get("lop", ""))
    prompt = prompt.replace("{THOI_GIAN}", str(config.get("thoi_gian", "")))
    prompt = prompt.replace("{TY_LE}", config.get("ty_le", ""))
    prompt = prompt.replace("{YEU_CAU}", config.get("yeu_cau_dac_biet", ""))
    
    ky_luat_thep = r"""
[KỶ LUẬT THÉP CẤP ĐỘ CAO NHẤT ĐỐI VỚI ĐỀ KIỂM TRA]:

1. KỶ LUẬT VỀ CÔNG THỨC TOÁN - LÝ - HÓA (CHỐNG SYNTAX ERROR):
- CẤM TUYỆT ĐỐI dùng dấu backtick (`) cho công thức.
- MỌI biểu thức, biến số, phép tính phải được bọc trong cặp dấu $...$. 
- ĐÚNG: $\frac{\sin i}{\sin r}$, $x^2 = 49$, $H_2SO_4$.
- LƯU Ý SỐ MŨ: Cấm viết liền số mũ (vd: không viết 108, phải viết $10^8$). Dùng dấu gạch chéo ngược \ (vd: \sqrt, \frac, \Delta). Cấm dùng dấu gạch đứng |.

2. KỶ LUẬT VỀ HÌNH ẢNH VÀ BẢNG:
- Nếu tài liệu nguồn có HÌNH MINH HỌA [IMAGE: ID...] hoặc BẢNG DỮ LIỆU [TABLE: ID...], khi lấy nội dung đó làm câu hỏi trắc nghiệm hoặc tự luận, bạn BẮT BUỘC chèn lại chính xác thẻ `[IMAGE: ID]` hoặc `[TABLE: ID]` vào đề bài.
- Ví dụ: "Câu 1: Quan sát hình sau và cho biết... [IMAGE: IMG_DKT_P1_1]"

3. MA TRẬN VÀ BẢN ĐẶC TẢ:
- Trình bày dạng Bảng Markdown chuẩn (| Cột 1 | Cột 2 |). Hệ thống sẽ tự động vẽ bảng Word.
- Không được gộp ô bằng HTML, chỉ dùng Markdown Table tiêu chuẩn.
"""
    
    full_prompt = (
        ky_luat_thep 
        + f"\n\n--- THÔNG TIN CẤU HÌNH ĐỀ KIỂM TRA ---\nMôn: {config.get('mon_hoc')}\nLớp: {config.get('lop')}\nThời gian: {config.get('thoi_gian')} phút\nTỉ lệ TN/TL: {config.get('ty_le')}\nYêu cầu thêm: {config.get('yeu_cau_dac_biet')}\n\n"
        + f"--- HƯỚNG DẪN BIÊN SOẠN ---\n{prompt}\n\n"
        + f"--- NGUỒN TÀI LIỆU TRUNG GIAN ---\n{source_text[:40000]}"
    )

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
                messages=[{"role": "system", "content": "Bạn là chuyên gia xây dựng Đề kiểm tra, Ma trận và Đặc tả. Bạn tuân thủ tuyệt đối quy định định dạng công thức Toán học bằng $...$."}, 
                          {"role": "user", "content": full_prompt}],
                max_tokens=8192
            )
            text_out = response.choices[0].message.content.strip()
        else:
            # SỬ DỤNG GOOGLE.GENAI MỚI NHẤT
            from google import genai
            client_genai = genai.Client(api_key=api_key or "AIzaSy_dummy")
            api_model = "gemini-2.5-pro" if "Pro" in model_name else "gemini-2.5-flash"
            response = client_genai.models.generate_content(
                model=api_model,
                contents=full_prompt
            )
            text_out = response.text.strip()
    except Exception as e:
        logger.error(f"AI Generation Error (Đề KT): {e}")
        raise RuntimeError(f"Lỗi kết nối AI khi tạo Đề kiểm tra: {e}")

    if not text_out: 
        raise RuntimeError("Không thể nhận phản hồi từ AI.")
        
    # Lược bỏ các phần dư thừa thường gặp của Markdown markdown block
    text_out = re.sub(r'^```markdown\s*', '', text_out, flags=re.MULTILINE)
    text_out = re.sub(r'^```\s*$', '', text_out, flags=re.MULTILINE)
    
    return text_out
