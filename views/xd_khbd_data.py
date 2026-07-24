# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (ÉP CẤU TRÚC CHI TIẾT & FIX LỖI XUỐNG DÒNG)
FILE: views/xd_khbd_data.py
============================================================
"""

import streamlit as st
import os
import re
import json
import logging
import base64
import pandas as pd
from docx import Document
from pathlib import Path
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

# ============================================================
# TỪ ĐIỂN KHUNG NĂNG LỰC SỐ THÔNG TƯ 18 (ĐẦY ĐỦ 100%)
# ============================================================
KHUNG_NLS_GV = {
    "1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "Sử dụng được các chức năng và công cụ cơ bản của nền tảng quản lí học tập (LMS).",
            "Thành thạo": "Xây dựng được kế hoạch bài dạy theo tiếp cận công nghệ. Thiết kế và triển khai được các hoạt động dạy học theo mô hình kết hợp hiệu quả.",
            "Nâng cao": "Sáng tạo và đổi mới các mô hình dạy học ứng dụng công nghệ số."
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": "Sử dụng được các kênh giao tiếp số để trả lời câu hỏi.",
            "Thành thạo": "Sử dụng dữ liệu học tập số để xác định người học cần hỗ trợ.",
            "Nâng cao": "Sáng tạo, phát triển các công cụ hỗ trợ dạy học thông minh."
        }
    },
    "2. KIỂM TRA, ĐÁNH GIÁ": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": "Sử dụng công cụ tạo bài kiểm tra online đơn giản.",
            "Thành thạo": "Sử dụng các công cụ số phổ biến để đánh giá quá trình và tổng kết.",
            "Nâng cao": "Sáng tạo triển khai các phương pháp đánh giá số tiến tiến."
        }
    },
    "3. TRAO QUYỀN CHO NGƯỜI HỌC": {
        "3.1. Tiếp cận và hòa nhập": {
            "Cơ bản": "Lựa chọn tài nguyên số có tính đến sự đa dạng của người học.",
            "Thành thạo": "Thiết kế tài nguyên số đảm bảo tính tiếp cận và hòa nhập."
        }
    },
    "4. KĨ NĂNG CÔNG NGHỆ SỐ": {
        "4.1. Kĩ năng thông tin và dữ liệu": {
            "Cơ bản": "Sử dụng công cụ tìm kiếm thông tin, tài liệu bài giảng.",
            "Thành thạo": "Đánh giá độ tin cậy của nguồn tin trên Internet, mạng xã hội."
        }
    },
    "5. PHÁT TRIỂN CHUYÊN MÔN": {
        "5.1. Giao tiếp trong tổ chức": {
            "Cơ bản": "Sử dụng email, nhóm chat trao đổi công việc."
        }
    },
    "6. ỨNG DỤNG TRÍ TUỆ NHÂN TẠO (AI)": {
        "6.2. Đạo đức AI": {
            "Cơ bản": "Sử dụng các công cụ AI tạo sinh đơn giản hỗ trợ dạy học.",
            "Thành thạo": "Khai thác công cụ AI chuyên biệt để tạo học liệu số tương tác."
        }
    }
}

# ============================================================
# KHUNG NĂNG LỰC SỐ HỌC SINH (HOÀN CHỈNH ĐẦY ĐỦ 5 LĨNH VỰC)
# ============================================================
KHUNG_NLS_HS = {
    "1. Sử dụng thông tin và dữ liệu số": {
        "1.1. Tìm kiếm và chọn lọc": {
            "Mức 1": "Biết sử dụng công cụ tìm kiếm cơ bản để thu thập thông tin học tập.",
            "Mức 2": "Biết đánh giá độ tin cậy, tính chính xác và nguồn gốc của thông tin trên Internet."
        },
        "1.2. Quản lý và lưu trữ": {
            "Mức 1": "Biết lưu trữ tệp tin đơn giản theo thư mục trên thiết bị cá nhân.",
            "Mức 2": "Biết sắp xếp, quản lý và lưu trữ tài liệu học tập khoa học trên điện toán đám mây."
        }
    },
    "2. Giao tiếp và hợp tác trực tuyến": {
        "2.1. Tương tác qua môi trường số": {
            "Mức 1": "Biết sử dụng email, chat để trao đổi học tập với giáo viên và bạn bè.",
            "Mức 2": "Biết sử dụng hiệu quả các nền tảng học tập và làm việc nhóm trực tuyến (Padlet, Azota, Teams...)."
        },
        "2.2. Chia sẻ thông tin và ứng xử": {
            "Mức 1": "Biết chia sẻ tài liệu học tập đơn giản qua mạng xã hội hoặc nhóm lớp.",
            "Mức 2": "Biết tuân thủ quy tắc ứng xử, văn hóa giao tiếp và tôn trọng bản quyền khi chia sẻ trên không gian mạng."
        }
    },
    "3. Sáng tạo nội dung số": {
        "3.1. Phát triển nội dung số": {
            "Mức 1": "Biết soạn thảo văn bản hoặc tạo bài trình chiếu (PowerPoint) cơ bản.",
            "Mức 2": "Biết thiết kế, chỉnh sửa hình ảnh, video hoặc tạo học liệu số đơn giản phục vụ học tập."
        },
        "3.2. Bản quyền và tôn trọng tác giả": {
            "Mức 1": "Biết trích dẫn nguồn tài liệu đơn giản khi sử dụng lại thông tin.",
            "Mức 2": "Hiểu và tuân thủ các quy định về quyền tác giả, giấy phép mở khi sử dụng sản phẩm số của người khác."
        }
    },
    "4. An toàn trong môi trường số": {
        "4.1. Bảo vệ thiết bị và dữ liệu cá nhân": {
            "Mức 1": "Biết đặt mật khẩu mạnh và bảo vệ tài khoản học tập cá nhân cơ bản.",
            "Mức 2": "Biết nhận diện các nguy cơ mất an toàn thông tin, lừa đảo trực tuyến, mã độc và cách phòng tránh."
        },
        "4.2. Bảo vệ sức khỏe và môi trường": {
            "Mức 1": "Biết điều chỉnh thời gian sử dụng thiết bị số hợp lý để bảo vệ thị lực và sức khỏe.",
            "Mức 2": "Có ý thức phòng tránh các tác động tiêu cực của không gian mạng đối với sức khỏe thể chất và tinh thần."
        }
    },
    "5. Giải quyết vấn đề bằng công nghệ số": {
        "5.1. Giải quyết vấn đề kỹ thuật": {
            "Mức 1": "Biết xử lý các sự cố công nghệ đơn giản trên thiết bị học tập cá nhân.",
            "Mức 2": "Biết tự tìm kiếm giải pháp hoặc nhờ hỗ trợ công nghệ khi gặp khó khăn về phần mềm, phần cứng."
        },
        "5.2. Sáng tạo giải pháp học tập": {
            "Mức 1": "Biết sử dụng công cụ số để giải quyết các nhiệm vụ học tập được phân công.",
            "Mức 2": "Biết ứng dụng công nghệ số để thực hiện các dự án học tập, nghiên cứu khoa học kỹ thuật hoặc giải quyết vấn đề thực tiễn."
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
        return "- Năng lực 1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ > 1.1. Dạy học và giáo dục trong môi trường số (Thành thạo): Xây dựng được kế hoạch bài dạy theo tiếp cận công nghệ, lựa chọn công cụ số phù hợp."
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

def read_pdf(uploaded_file, range_str=""):
    if uploaded_file is None: return ""
    content = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    extracted_text = ""
    try:
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        extracted_text = "\n\n".join([doc[i].get_text("text").strip() for i in range(len(doc))])
    except: pass
    return safe_text(extracted_text)

def read_docx_ordered(source):
    try:
        doc = Document(BytesIO(source.getvalue())) if hasattr(source, "getvalue") else Document(source)
        return safe_text("\n".join([p.text for p in doc.paragraphs]))
    except: return ""

def read_multiple_files(files, range_str="", is_pdf_target=False):
    result = []
    for f in files or []:
        file_name = getattr(f, 'name', '').lower()
        if file_name.endswith('.pdf'): content = read_pdf(f)
        else: content = read_docx_ordered(f)
        if len(content) > 30: result.append(content)
    return safe_text("\n".join(result))

def generate_ai(client, prompt, model_name="3.5 Flash"):
    system_instruction = """
[KỶ LUẬT THÉP VỀ NỘI DUNG VÀ CẤU TRÚC TEMPLATE - ĐỌC KỸ VÀ TUÂN THỦ 100%]:
1. CẤM VIẾT LỜI CHÀO/KẾT LUẬN. Bắt đầu ngay lập tức bằng "# TÊN BÀI HỌC:".
2. BẠN PHẢI TUÂN THỦ TUYỆT ĐỐI CẤU TRÚC TEMPLATE SAU:
   I. MỤC TIÊU
   1. Kiến thức
   2. Năng lực
      a) Năng lực chung:
      b) Năng lực đặc thù:
   3. Năng lực số và AI
   4. Phẩm chất
   II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
   1. Giáo viên:
   2. Học sinh:
   III. TIẾN TRÌNH DẠY HỌC
   (Chia các HOẠT ĐỘNG rõ ràng)
   PHỤ LỤC
   PHIẾU HỌC TẬP

3. QUY TẮC CỨNG CHỐNG LƯỜI (RẤT QUAN TRỌNG):
   - Mọi hoạt động dạy học PHẢI TRÌNH BÀY ĐỦ 4 TIỂU MỤC: a) Mục tiêu, b) Nội dung, c) Sản phẩm, d) Tổ chức thực hiện. Các tiểu mục này PHẢI nằm ở các dòng độc lập, tuyệt đối không được dính chung một dòng.
   - TUYỆT ĐỐI KHÔNG TÓM TẮT CHUNG CHUNG (Cấm viết: "Học sinh làm bài tập SGK"). BẮT BUỘC TRÍCH XUẤT NGUYÊN VĂN đề bài, số liệu, định lý, ví dụ cụ thể từ tài liệu nguồn vào phần "b) Nội dung".
   - Ở phần "c) Sản phẩm", phải ghi rõ đáp án, lời giải chi tiết cho từng bài toán/câu hỏi đã nêu ở phần b.
   - Ở phần "d) Tổ chức thực hiện", bắt buộc dùng chính xác 4 dòng bắt đầu bằng dấu * như sau:
     *Chuyển giao nhiệm vụ học tập: ...
     *Thực hiện nhiệm vụ học tập: ...
     *Báo cáo kết quả và thảo luận: ...
     *Kết luận: ...

4. TOÁN HỌC: Sử dụng chuẩn LaTeX `$\sqrt{x}$` cho mọi biểu thức toán.
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
        
    # BỘ LỌC HẬU XỬ LÝ (POST-PROCESSING) ÉP XUỐNG DÒNG CHUẨN XÁC CHO MỌI MỤC
    text_out = re.sub(r'([^\n])\s*(a\)\s+Mục tiêu:)', r'\1\n\n**\2', text_out)
    text_out = re.sub(r'([^\n])\s*(b\)\s+Nội dung:)', r'\1\n\n**\2', text_out)
    text_out = re.sub(r'([^\n])\s*(c\)\s+Sản phẩm:)', r'\1\n\n**\2', text_out)
    text_out = re.sub(r'([^\n])\s*(d\)\s+Tổ chức thực hiện:)', r'\1\n\n**\2', text_out)
    
    text_out = re.sub(r'([^\n])\s*(\*(?:Chuyển giao nhiệm vụ học tập|Thực hiện nhiệm vụ học tập|Báo cáo kết quả và thảo luận|Kết luận)[^:\n]*:)', r'\1\n\n\2', text_out)
    
    return text_out

def validate_khbd_result(text):
    if len(text) < 500: return False, "Nội dung quá ngắn."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, nls_str, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, mode, so_tiet):
    source = safe_text(noi_dung_chinh)[:25000] 
    ga_block = f"--- GIÁO ÁN CŨ ĐỂ CHỈNH SỬA ---\n{safe_text(noi_dung_ga)[:10000]}\n" if mode == "chinh_sua" else ""
    hoa_nhap_block = f"- Dạy học hòa nhập: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else ""
    ai_block = f"- Tích hợp AI: Đề xuất hoạt động ứng dụng công nghệ số." if tich_hop_ai else ""

    nhiem_vu = f"""
NHIỆM VỤ: SOẠN KẾ HOẠCH BÀI DẠY SIÊU CHI TIẾT TỪ NGUỒN TÀI LIỆU CUNG CẤP.
1. TUYỆT ĐỐI KHÔNG TÓM TẮT. Hãy bám sát tài liệu SGK dưới đây, TRÍCH XUẤT NGUYÊN VĂN các hoạt động khám phá, ví dụ, bài tập, công thức (dùng chuẩn LaTeX $...$) vào trong giáo án để giáo viên có thể dạy trực tiếp mà không cần mở sách.
2. Bài học kéo dài {so_tiet} tiết. Phân bổ kiến thức đều đặn, chi tiết từng bước.
3. DÀN Ý BẮT BUỘC PHẢI KHỚP TUYỆT ĐỐI VỚI TEMPLATE SAU:

# TÊN BÀI HỌC: ...
I. MỤC TIÊU
1. Kiến thức
2. Năng lực
   a) Năng lực chung:
   b) Năng lực đặc thù:
3. Năng lực số và AI
   [Nội dung chuẩn Thông tư 18]: {nls_str} 
   {ai_block} 
   {hoa_nhap_block}
4. Phẩm chất
II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
1. Giáo viên:
2. Học sinh:
III. TIẾN TRÌNH DẠY HỌC
### TIẾT 1
**Hoạt động 1: MỞ ĐẦU**
a) Mục tiêu: ...
b) Nội dung: [Trích xuất cụ thể câu hỏi/bài toán từ tài liệu nguồn]
c) Sản phẩm: [Trích xuất cụ thể đáp án/lời giải]
d) Tổ chức thực hiện: 
*Chuyển giao nhiệm vụ học tập: ...
*Thực hiện nhiệm vụ học tập: ...
*Báo cáo kết quả và thảo luận: ...
*Kết luận: ...

**Hoạt động 2: HÌNH THÀNH KIẾN THỨC MỚI**
a) Mục tiêu: ...
b) Nội dung: [Trích xuất nguyên văn lý thuyết, định lý, ví dụ từ SGK]
c) Sản phẩm: [Trích xuất lời giải chi tiết cho ví dụ]
d) Tổ chức thực hiện: 
*Chuyển giao nhiệm vụ học tập: ...
*Thực hiện nhiệm vụ học tập: ...
*Báo cáo kết quả và thảo luận: ...
*Kết luận: ...

(Tiếp tục triển khai đầy đủ các hoạt động Luyện tập, Vận dụng cho các tiết học tiếp theo với cấu trúc a, b, c, d tương tự).

PHỤ LỤC
PHIẾU HỌC TẬP
"""
    return f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\n{nhiem_vu}\n\n--- NGUỒN KIẾN THỨC CỐT LÕI TỪ TÀI LIỆU ---\n{source}\n\n{ga_block}"
