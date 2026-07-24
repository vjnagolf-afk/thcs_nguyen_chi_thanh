# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (CẤU TRÚC DỮ LIỆU NGUỒN & CHỐNG CHUNG CHUNG)
FILE: views/xd_khbd_data.py
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

def get_nls_framework(loai_khung): return KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS
def get_nls_domains(loai_khung): return list(get_nls_framework(loai_khung).keys())
def get_nls_components(loai_khung, linh_vuc): return list(get_nls_framework(loai_khung).get(linh_vuc, {}).keys())
def get_nls_levels(loai_khung, linh_vuc, thanh_phan): return list(get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).keys())
def get_nls_content(loai_khung, linh_vuc, thanh_phan, muc_do): return get_nls_framework(loai_khung).get(linh_vuc, {}).get(thanh_phan, {}).get(muc_do, "")

def add_nls():
    linh_vuc = safe_text(st.session_state.get("khbd_nls_linh_vuc", ""))
    thanh_phan = safe_text(st.session_state.get("khbd_nls_thanh_phan", ""))
    muc_do = safe_text(st.session_state.get("khbd_nls_muc_do", ""))
    noi_dung = safe_text(st.session_state.get("khbd_nls_noi_dung", ""))
    if not noi_dung: return
    van_ban = NLS_GV_VAN_BAN_MAC_DINH if st.session_state.get("khbd_loai_khung_nls") == "Giáo viên (Thông tư 18)" else "Khung DigComp"
    item = {"van_ban": van_ban, "linh_vuc": linh_vuc, "thanh_phan": thanh_phan, "muc_do": muc_do, "noi_dung": noi_dung}
    if item not in st.session_state.khbd_nls_list: st.session_state.khbd_nls_list.append(item)

def format_nls():
    items = st.session_state.get("khbd_nls_list", [])
    if not items:
        return "- Năng lực 1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ > 1.1. Dạy học và giáo dục trong môi trường số (Thành thạo): Xây dựng kế hoạch bài dạy theo tiếp cận công nghệ."
    return "\n".join([f"- Năng lực {item['linh_vuc']} > {item['thanh_phan']} ({item['muc_do']}): {item['noi_dung']}" for item in items])

def safe_text(value):
    if value is None: return ""
    text = str(value).replace("\x00", "").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\r", "").replace("\t", " ")
    return re.sub(r"[ ]{2,}", " ", text).strip()

def diagnose_source_quality(text, source_name="Tài liệu nguồn"):
    text = safe_text(text)
    if len(text) < MIN_SOURCE_CHARS:
        return {"status": "insufficient", "message": f"{source_name} quá ngắn hoặc không đọc được chữ."}
    return {"status": "valid", "message": "Dữ liệu hợp lệ."}

# ============================================================
# II, III, IV. BỘ ĐỌC TÀI LIỆU NGUỒN CÓ CẤU TRÚC (PDF & DOCX)
# ============================================================
def parse_pdf_structured(uploaded_file, range_str=""):
    if uploaded_file is None:
        return {"source_name": "unknown", "pages": []}
    
    content = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    file_name = getattr(uploaded_file, 'name', 'document.pdf')
    pages_data = []
    
    try:
        import fitz  # PyMuPDF
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
            image_list = page.get_images(full=True)
            for img_idx, img in enumerate(image_list):
                xref = img[0]
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_id = f"IMG_P{i+1}_{img_idx+1}"
                    b64_str = base64.b64encode(image_bytes).decode("utf-8")
                    page_images.append({
                        "id": image_id,
                        "page": i + 1,
                        "ext": image_ext,
                        "base64": b64_str
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
                            headers = [str(cell) for cell in extracted_df[0]]
                            rows = [[str(cell) for cell in row] for row in extracted_df[1:]]
                            page_tables.append({
                                "id": f"TAB_P{i+1}_{t_idx+1}",
                                "page": i + 1,
                                "headers": headers,
                                "rows": rows
                            })
            except:
                pass

            pages_data.append({
                "page_number": i + 1,
                "text": page_text,
                "images": page_images,
                "tables": page_tables,
                "figures": [],
                "charts": []
            })
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
        if hasattr(uploaded_file, "getvalue"):
            source = uploaded_file.getvalue()
        elif hasattr(uploaded_file, "read"):
            source = uploaded_file.read()
        else:
            source = uploaded_file

        if isinstance(source, bytes):
            doc = Document(BytesIO(source))
        else:
            doc = Document(source)
        
        for p in doc.paragraphs:
            if p.text.strip():
                paragraphs_text.append(p.text.strip())
                
        for t_idx, table in enumerate(doc.tables):
            rows_raw = []
            for row in table.rows:
                rows_raw.append([cell.text.strip().replace('\n', ' ') for cell in row.cells])
            if rows_raw:
                tables_data.append({
                    "id": f"TAB_DOCX_{t_idx+1}",
                    "page": 1,
                    "headers": rows_raw[0],
                    "rows": rows_raw[1:] if len(rows_raw) > 1 else []
                })
    except Exception as e:
        logger.error(f"Lỗi đọc cấu trúc DOCX: {e}")
        
    full_text = "\n".join(paragraphs_text)
    return {
        "source_name": file_name,
        "pages": [{
            "page_number": 1,
            "text": full_text,
            "images": [],
            "tables": tables_data,
            "figures": [],
            "charts": []
        }]
    }

# ============================================================
# V. XÂY DỰNG NGUỒN KIẾN THỨC TRUNG GIAN CHO AI
# ============================================================
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
            tab_id = tab["id"]
            headers_str = " | ".join(tab["headers"])
            rows_str = "\n".join([" | ".join(r) for r in tab["rows"]])
            source_lines.append(f"[TABLE - ID: {tab_id} - Trang {p_num}]\nHeaders: {headers_str}\nRows:\n{rows_str}")
        for img in page.get("images", []):
            img_id = img["id"]
            source_lines.append(f"[IMAGE - ID: {img_id} - Trang {p_num} (Hình ảnh nhúng tài liệu)]")
        for fig in page.get("figures", []):
            source_lines.append(f"[FIGURE - ID: {fig.get('id')} - Trang {p_num}]: {fig.get('description', '')}")
        for chart in page.get("charts", []):
            source_lines.append(f"[CHART - ID: {chart.get('id')} - Trang {p_num}]: {chart.get('description', '')}")
            
    return "\n\n".join(source_lines)

# Tương thích ngược với các hàm gọi cũ
def read_pdf(uploaded_file, range_str=""):
    data = parse_pdf_structured(uploaded_file, range_str)
    return "\n".join([p["text"] for p in data["pages"]])

def read_docx_ordered(source):
    data = parse_docx_structured(source)
    return "\n".join([p["text"] for p in data["pages"]])

def read_multiple_files(files, range_str="", is_pdf_target=False):
    combined_structured = {"source_name": "multi_files", "pages": []}
    page_offset = 0
    for f in files or []:
        file_name = getattr(f, 'name', '').lower()
        if file_name.endswith('.pdf'):
            parsed = parse_pdf_structured(f, range_str)
        else:
            parsed = parse_docx_structured(f)
            
        for p in parsed["pages"]:
            p["page_number"] += page_offset
            combined_structured["pages"].append(p)
        page_offset += len(parsed["pages"])
        
    return build_intermediate_knowledge_source(combined_structured)


# ============================================================
# VI. HỆ THỐNG GỌI AI & RÀ BUỘC PROMPT CHỐNG CHUNG CHUNG
# ============================================================
def generate_ai(client, prompt, model_name="3.5 Flash"):
    system_instruction = """
[KỶ LUẬT THÉP VỀ NỘI DUNG VÀ CẤU TRÚC TEMPLATE - CHỐNG CỤT NGỦN VÀ CHỐNG CHUNG CHUNG 100%]:
1. CẤM VIẾT LỜI CHÀO/KẾT LUẬN. Bắt đầu ngay lập tức bằng "# TÊN BÀI HỌC:".
2. BẠN PHẢI SỬ DỤNG TRỰC TIẾP VÀ CHÍNH XÁC DỮ LIỆU TỪ NGUỒN KIẾN THỨC TRUNG GIAN ([TEXT], [TABLE], [IMAGE], [FIGURE], [CHART]) ĐƯỢC CUNG CẤP. 
3. TUYỆT ĐỐI CẤM các câu văn chung chung vô nghĩa sau đây trong mọi hoạt động:
   - "Học sinh thực hiện nhiệm vụ học tập theo hướng dẫn của giáo viên."
   - "Học sinh thảo luận và trình bày kết quả."
   - "Giáo viên nhận xét và kết luận."
   - "Kết quả thảo luận của nhóm."
   - "Câu trả lời của học sinh."
4. QUY TẮC BẮT BUỘC CHO TỪNG HOẠT ĐỘNG:
   - a) Mục tiêu: Nêu cụ thể kiến thức, kỹ năng, năng lực đặc thù cần đạt.
   - b) Nội dung: Trích xuất chính xác câu hỏi, bài tập, biểu thức, bảng dữ liệu hoặc hình ảnh từ nguồn.
   - c) Sản phẩm: BẮT BUỘC là một đầu ra cụ thể, quan sát hoặc đánh giá được.
   - d) Tổ chức thực hiện PHẢI ĐỦ 4 BƯỚC VÀ GẮN LIỀN NỘI DUNG NGUỒN (Chuyển giao, Thực hiện, Báo cáo, Kết luận).

5. KỶ LUẬT THÉP VỀ ĐỊNH DẠNG TOÁN/LÝ/HÓA HỌC:
   - BẠN ĐANG BỊ PHẠM LỖI RẤT NẶNG LÀ KHÔNG BỌC DẤU $ CHO CÔNG THỨC VÀ BIẾN SỐ.
   - CẤM TUYỆT ĐỐI viết mã LaTeX trần mà không bọc trong dấu $...$.
   - LỖI SAI BỊ CẤM: Chiết suất n21 = \frac{\sin i}{\sin r}
   - BẮT BUỘC SỬA THÀNH: Chiết suất $n_{21} = \frac{\sin i}{\sin r}$
   - LỖI SAI BỊ CẤM: 3 \times 108 m/s
   - BẮT BUỘC SỬA THÀNH: $3 \times 10^8$ m/s
   - TẤT CẢ các biến số đơn lẻ (i, r, I, S, n), công thức, phép toán đều phải BỌC TRONG DẤU $.
   - Chỉ số dưới dùng dấu _ (VD: $H_2O$). Số mũ dùng dấu ^ (VD: $x^2$).
    """
    full_prompt = system_instruction + "\n\n" + prompt

    api_key = st.session_state.get("user_api_key", "").strip()
    if not api_key:
        try: api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        except: pass
    if not api_key:
        try: api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
        except: pass

    text_out = ""
    try:
        if api_key.startswith("sk-") or "proj-" in api_key:
            import openai
            oai_client = openai.OpenAI(api_key=api_key)
            gpt_model = "gpt-4o" if "Pro" in model_name else "gpt-4o-mini"
            response = oai_client.chat.completions.create(
                model=gpt_model,
                messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}],
                max_tokens=8192
            )
            text_out = response.choices[0].message.content.strip()
        else:
            import google.generativeai as genai
            genai.configure(api_key=api_key or "AIzaSy_dummy")
            api_model = "gemini-2.5-pro" if "Pro" in model_name else "gemini-2.5-flash"
            model = genai.GenerativeModel(model_name=api_model)
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
    
    # Màng lọc Auto-Fix cứu hộ các công thức bị AI quên bọc dấu $
    text_out = re.sub(r'(?<!\$)(?<!\\)(\\frac\s*\{[^{}]*\}\s*\{[^{}]*\})(?!\$)', r'$\1$', text_out)
    text_out = re.sub(r'(?<!\$)(?<!\\)(\\sqrt\s*(?:\[[^\]]*\])?\s*\{[^{}]*\})(?!\$)', r'$\1$', text_out)
    
    text_out = re.sub(r'([^\n])\s*([a-d]\)\s+)', r'\1\n\n\2', text_out)
    text_out = re.sub(r'([^\n])\s*(\*(?:Chuyển giao nhiệm vụ học tập|Thực hiện nhiệm vụ học tập|Báo cáo kết quả và thảo luận|Kết luận)[^:\n]*:)', r'\1\n\n\2', text_out)
    
    return text_out


def validate_khbd_result(text):
    if not text or len(text) < 500:
        return False, "Nội dung giáo án quá ngắn hoặc trống."
        
    text_lower = text.lower()
    if "c) sản phẩm:" not in text_lower and "sản phẩm:" not in text_lower:
        return False, "Thiếu mục c) Sản phẩm trong các hoạt động dạy học."
        
    forbidden_phrases = [
        "học sinh thực hiện nhiệm vụ học tập theo hướng dẫn",
        "học sinh thảo luận và trình bày kết quả",
        "giáo viên nhận xét và kết luận",
        "kết quả thảo luận của nhóm",
        "câu trả lời của học sinh"
    ]
    for phrase in forbidden_phrases:
        if phrase in text_lower:
            return False, f"Giáo án chứa câu văn chung chung bị cấm: '{phrase}'."
            
    required_steps = [
        "chuyển giao nhiệm vụ học tập",
        "thực hiện nhiệm vụ học tập",
        "báo cáo kết quả và thảo luận",
        "kết luận"
    ]
    for step in required_steps:
        if step not in text_lower:
            return False, f"Thiếu bước tổ chức thực hiện bắt buộc: '{step}'."
            
    return True, "Hợp lệ"


def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, nls_str, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, mode, so_tiet):
    source = safe_text(noi_dung_chinh)[:35000] 
    ga_block = f"--- GIÁO ÁN CŨ ĐỂ CHỈNH SỬA ---\n{safe_text(noi_dung_ga)[:10000]}\n" if mode == "chinh_sua" else ""
    hoa_nhap_block = f"- Dạy học hòa nhập: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else ""
    ai_block = f"- Tích hợp AI: Đề xuất hoạt động ứng dụng." if tich_hop_ai else ""

    nhiem_vu = f"""
NHIỆM VỤ: SOẠN KẾ HOẠCH BÀI DẠY SIÊU CHI TIẾT TỪ NGUỒN KIẾN THỨC CÓ CẤU TRÚC.
1. BẮT BUỘC SỬ DỤNG DỮ LIỆU CỤ THỂ TỪ NGUỒN DƯỚI ĐÂY. Tuyệt đối không tự bịa đặt hoặc dùng từ ngữ chung chung.
2. Bài học kéo dài {so_tiet} tiết. Phân bổ kiến thức đều đặn qua các hoạt động.
3. DÀN Ý BẮT BUỘC CHO TỪNG HOẠT ĐỘNG:

# TÊN BÀI HỌC: ...
I. MỤC TIÊU
1. Kiến thức
2. Năng lực
   a) Năng lực chung:
   b) Năng lực đặc thù:
3. Năng lực số và AI
   {nls_str} 
   {ai_block} 
   {hoa_nhap_block}
4. Phẩm chất
II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
1. Giáo viên:
2. Học sinh:
III. TIẾN TRÌNH DẠY HỌC
### TIẾT 1 (hoặc các tiết tiếp theo)
**Hoạt động 1: MỞ ĐẦU (hoặc HÌNH THÀNH KIẾN THỨC, LUYỆN TẬP, VẬN DỤNG)**
a) Mục tiêu: ...
b) Nội dung: [Trích xuất nguyên văn câu hỏi, bài toán hoặc tham chiếu bảng/hình ID từ nguồn]
c) Sản phẩm: [Nêu rõ tên sản phẩm cụ thể: Phiếu học tập đã hoàn thành, bảng số liệu, kết quả tính toán...]
d) Tổ chức thực hiện: 
*Chuyển giao nhiệm vụ học tập: [Mô tả chi tiết việc giao nhiệm vụ, chỉ rõ câu hỏi hoặc ID đối tượng]
*Thực hiện nhiệm vụ học tập: [Mô tả chi tiết việc học sinh thực hiện, tính toán, đọc tài liệu]
*Báo cáo kết quả và thảo luận: [Mô tả chi tiết việc báo cáo sản phẩm và tiêu chí nhận xét]
*Kết luận: [Mô tả chi tiết nội dung kiến thức chuyên môn chốt lại bám sát nguồn]

PHỤ LỤC
PHIẾU HỌC TẬP (Trích xuất các bài tập cụ thể từ nguồn)
"""
    return f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\n{nhiem_vu}\n\n--- NGUỒN KIẾN THỨC TRUNG GIAN ĐÃ TRÍCH XUẤT ---\n{source}\n\n{ga_block}"
