# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG KẾ HOẠCH BÀI DẠY (SIÊU CHI TIẾT 4 BƯỚC SƯ PHẠM)
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
# KHUNG NĂNG LỰC SỐ GIÁO VIÊN & HỌC SINH (ĐẦY ĐỦ 100%)
# ============================================================
KHUNG_NLS_GV = {
    "1. TỔ CHỨC DẠY HỌC, GIÁO DỤC TRONG MÔI TRƯỜNG SỐ": {
        "1.1. Dạy học và giáo dục trong môi trường số": {
            "Cơ bản": "Sử dụng được các chức năng và công cụ cơ bản của nền tảng quản lí học tập (LMS). Sử dụng các công cụ hỗ trợ dạy học trực tuyến đơn giản.",
            "Thành thạo": "Xây dựng được kế hoạch bài dạy theo tiếp cận công nghệ, thiết kế và triển khai hoạt động dạy học theo mô hình kết hợp (blended learning) hiệu quả.",
            "Nâng cao": "Sáng tạo và đổi mới các mô hình dạy học ứng dụng công nghệ số, hướng dẫn đồng nghiệp."
        },
        "1.2. Hướng dẫn, hỗ trợ học tập": {
            "Cơ bản": "Sử dụng kênh giao tiếp số (email, diễn đàn) để trả lời câu hỏi và hỗ trợ người học.",
            "Thành thạo": "Sử dụng dữ liệu học tập số để xác định người học cần hỗ trợ và lựa chọn biện pháp can thiệp phù hợp, cá nhân hóa.",
            "Nâng cao": "Sáng tạo, phát triển các công cụ/phương pháp hỗ trợ dạy học thông minh trên nền tảng số."
        },
        "1.3. Cá nhân hóa người học": {
            "Cơ bản": "Xác định nhu cầu, sự khác biệt của người học trong sử dụng công nghệ số để điều chỉnh nội dung.",
            "Thành thạo": "Sử dụng công nghệ số thiết kế lộ trình học tập linh hoạt, phân hóa theo trình độ và sở thích người học.",
            "Nâng cao": "Thiết kế môi trường học tập số cá nhân hóa nâng cao, đánh giá hiệu quả chiến lược cá nhân hóa."
        },
        "1.4. Học tập cộng tác": {
            "Cơ bản": "Sử dụng công cụ số cơ bản tổ chức cho người học làm việc nhóm đơn giản, chia sẻ tài liệu.",
            "Thành thạo": "Thiết kế nhiệm vụ học tập yêu cầu người học dùng đa dạng công cụ số để cùng xây dựng kiến thức.",
            "Nâng cao": "Xây dựng dự án cộng tác phức tạp, quản lý cộng đồng học tập trực tuyến."
        }
    },
    "2. KIỂM TRA, ĐÁNH GIÁ": {
        "2.1. Phương thức đánh giá": {
            "Cơ bản": "Sử dụng hình thức kiểm tra truyền thống kết hợp nhập điểm hệ thống số, tạo bài kiểm tra online đơn giản.",
            "Thành thạo": "Sử dụng công cụ số phổ biến tạo bài kiểm tra, khảo sát đánh giá quá trình và tổng kết.",
            "Nâng cao": "Sáng tạo phương pháp, mô hình đánh giá số tiên tiến đáp ứng năng lực phức hợp."
        },
        "2.2. Phân tích kết quả học tập": {
            "Cơ bản": "Sử dụng chức năng cơ bản của LMS xem báo cáo hoạt động và kết quả người học.",
            "Thành thạo": "Phân tích dữ liệu hệ thống đánh giá số nhận diện tiến bộ, trực quan hóa dữ liệu kết quả học tập.",
            "Nâng cao": "Áp dụng kỹ thuật phân tích dữ liệu học tập nâng cao dự đoán xu hướng, đề xuất can thiệp sớm."
        },
        "2.3. Phản hồi và đánh giá cải tiến": {
            "Cơ bản": "Cung cấp phản hồi kịp thời cho người học bằng văn bản hoặc điểm số thông qua nền tảng số.",
            "Thành thạo": "Sử dụng đa dạng công cụ số (ghi âm, video ngắn) đưa ra phản hồi chi tiết, quy trình tự đánh giá chéo.",
            "Nâng cao": "Sử dụng dữ liệu phân tích điều chỉnh kế hoạch bài dạy, cải tiến liên tục chương trình giáo dục."
        }
    },
    "3. TRAO QUYỀN CHO NGƯỜI HỌC": {
        "3.1. Tiếp cận và hòa nhập": {
            "Cơ bản": "Hỗ trợ người học gặp khó khăn, lựa chọn tài nguyên số có tính đến sự đa dạng người học.",
            "Thành thạo": "Khai thác và điều chỉnh tài nguyên, đa dạng hóa công cụ số đáp ứng nhu cầu đặc biệt, giáo dục hòa nhập.",
            "Nâng cao": "Hướng dẫn đồng nghiệp chiến lược và công nghệ số hỗ trợ giáo dục hòa nhập."
        },
        "3.2. Giải quyết vấn đề": {
            "Cơ bản": "Thiết kế nhiệm vụ yêu cầu tìm kiếm Internet trả lời câu hỏi hoặc giải quyết vấn đề đơn giản.",
            "Thành thạo": "Tổ chức hoạt động học tập dựa trên vấn đề (problem-based) hoặc dự án (project-based) dùng công nghệ số.",
            "Nâng cao": "Kết nối người học với chuyên gia và vấn đề thực tiễn bên ngoài nhà trường giải quyết vấn đề cộng đồng."
        },
        "3.3. Khuyến khích sự tham gia tích cực": {
            "Cơ bản": "Sáng tạo tương tác số đơn giản thu hút sự chú ý, trực quan hóa nội dung dạy học.",
            "Thành thạo": "Tích hợp trò chơi hóa (gamification), công cụ sáng tạo thúc đẩy người học chủ động tạo ra nội dung số.",
            "Nâng cao": "Thiết kế môi trường học tập số năng động, mô phỏng thí nghiệm ảo, thực tế ảo (VR/AR)."
        }
    },
    "4. KĨ NĂNG CÔNG NGHỆ SỐ": {
        "4.1. Kĩ năng thông tin và dữ liệu": {
            "Cơ bản": "Sử dụng công cụ tìm kiếm tìm thông tin bài giảng, lưu trữ sắp xếp khoa học trên đám mây.",
            "Thành thạo": "Đánh giá độ tin cậy nguồn tin Internet, hướng dẫn tư duy phản biện khi tiếp nhận thông tin số.",
            "Nâng cao": "Thu thập, trực quan hóa dữ liệu nâng cao, tích hợp phát triển năng lực thông tin vào chương trình."
        },
        "4.2. Sáng tạo nội dung số": {
            "Cơ bản": "Sử dụng công cụ phổ biến tạo nội dung dạy học theo định dạng số khác nhau.",
            "Thành thạo": "Xây dựng kho học liệu số, hướng dẫn người học quyền tác giả, trích dẫn tài nguyên hợp pháp.",
            "Nâng cao": "Sử dụng công cụ chuyên dụng tạo học liệu số tương tác cao, tích hợp AI, thực tế ảo."
        },
        "4.3. An toàn": {
            "Cơ bản": "Bảo vệ sức khỏe thể chất tinh thần, bố trí thời gian sử dụng thiết bị hợp lý, xử lý bắt nạt trực tuyến.",
            "Thành thạo": "Phòng tránh rủi ro mạng, bảo vệ dữ liệu cá nhân, định danh số, hướng dẫn học sinh dấu vết số.",
            "Nâng cao": "Áp dụng phương pháp giảm căng thẳng môi trường số, xây dựng môi trường học tập an toàn lành mạnh."
        }
    },
    "5. PHÁT TRIỂN CHUYÊN MÔN": {
        "5.1. Giao tiếp trong tổ chức": {
            "Cơ bản": "Sử dụng email, nhóm chat trao đổi công việc với đồng nghiệp và phụ huynh.",
            "Thành thạo": "Sử dụng hiệu quả kênh giao tiếp số chính thức tương tác phụ huynh, chia sẻ dữ liệu chuyên môn.",
            "Nâng cao": "Xây dựng chiến lược truyền thông số, kết nối cộng đồng giáo dục."
        },
        "5.2. Hợp tác phát triển chuyên môn": {
            "Cơ bản": "Tham gia cộng đồng học tập trực tuyến, tự đánh giá thuận lợi khó khăn ứng dụng công nghệ.",
            "Thành thạo": "Xây dựng kế hoạch cải tiến ứng dụng công nghệ số, tham gia khóa học cập nhật kỹ năng số.",
            "Nâng cao": "Cập nhật xu hướng công nghệ mới, hướng dẫn đồng nghiệp phát triển năng lực số."
        },
        "5.3. Phát triển, sử dụng, chia sẻ học liệu số": {
            "Cơ bản": "Tìm kiếm tài nguyên, kho học liệu số, thư viện trực tuyến, tài nguyên giáo dục mở (OER).",
            "Thành thạo": "Tạo học liệu số từ nguồn có sẵn, quản lý kho học liệu cá nhân an toàn, đánh giá chất lượng.",
            "Nâng cao": "Xây dựng và quản trị hệ thống quản lý, chia sẻ tài nguyên số mở cho toàn trường."
        }
    },
    "6. ỨNG DỤNG TRÍ TUỆ NHÂN TẠO (AI)": {
        "6.1. Tư duy lấy con người làm trung tâm": {
            "Cơ bản": "Nhận diện cách vận hành của AI và các công nghệ tích hợp AI.",
            "Thành thạo": "Thiết kế hoạt động dạy học tích hợp AI sáng tạo và có trách nhiệm.",
            "Nâng cao": "Triển khai đổi mới phương pháp dạy học thích ứng sâu bằng AI, hướng dẫn đồng nghiệp."
        },
        "6.2. Đạo đức AI": {
            "Cơ bản": "Sử dụng công cụ AI tạo sinh đơn giản hỗ trợ dạy học, nhận diện rủi ro dữ liệu cá nhân.",
            "Thành thạo": "Khai thác công cụ AI giáo dục tạo học liệu tương tác, hướng dẫn học sinh dùng AI có trách nhiệm.",
            "Nâng cao": "Đánh giá vấn đề đạo đức AI, tham gia xây dựng chính sách sử dụng AI có đạo đức trong nhà trường."
        },
        "6.3. Sư phạm AI": {
            "Cơ bản": "Nhận diện khả năng tích hợp AI hướng cá nhân hóa, hiểu lợi ích sư phạm của AI.",
            "Thành thạo": "Ứng dụng AI linh hoạt các bước dạy học lấy người học làm trung tâm, giáo dục hòa nhập.",
            "Nâng cao": "Xây dựng nguyên tắc sư phạm sử dụng AI, hướng dẫn đồng nghiệp thiết kế đồng sáng tạo."
        },
        "6.4. AI cho phát triển chuyên môn": {
            "Cơ bản": "Sử dụng AI lập kế hoạch, theo dõi phân tích quá trình phát triển chuyên môn bản thân.",
            "Thành thạo": "Sử dụng AI hỗ trợ học tập suốt đời, tìm kiếm tài nguyên phát triển bản thân, phòng ngừa rủi ro.",
            "Nâng cao": "Xây dựng bộ công cụ AI tạo sinh hỗ trợ phát triển chuyên môn cho đồng nghiệp."
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

3. QUY TẮC CỨNG CHỐNG "CỤT NGỦN", CHỐNG NÓI CHUNG CHUNG:
   - TUYỆT ĐỐI KHÔNG sử dụng ký tự `**` trước các mục a), b), c), d). Trình bày thuần túy dạng `a) Mục tiêu:`, `b) Nội dung:`, `c) Sản phẩm:`, `d) Tổ chức thực hiện:`.
   - Các tiểu mục a, b, c, d phải nằm trên các dòng riêng biệt.
   - Các bài tập, ví dụ trong mục b) Nội dung và c) Sản phẩm PHẢI được ngắt dòng riêng biệt, trích xuất đầy đủ từng câu hỏi và lời giải chi tiết, tuyệt đối KHÔNG viết dồn thành một đoạn văn dài.
   - Phần d) Tổ chức thực hiện BẮT BUỘC phải viết văn bản hướng dẫn sư phạm đầy đủ nội dung, cụ thể từng bước cho 4 gạch đầu dòng sau (CẤM viết chung chung kiểu "Giải quyết bài toán"):
     *Chuyển giao nhiệm vụ học tập: [Giáo viên giao nhiệm vụ cụ thể gì, yêu cầu học sinh làm bài tập nào]
     *Thực hiện nhiệm vụ học tập: [Học sinh thực hiện cá nhân/nhóm ra sao, tính toán thế nào]
     *Báo cáo kết quả và thảo luận: [Học sinh lên bảng trình bày, gọi học sinh nhận xét]
     *Kết luận: [Giáo viên đánh giá, chốt kiến thức trọng tâm và công thức cụ thể]

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
        
    # BỘ LỌC HẬU XỬ LÝ: XÓA SẠCH DẤU ** VÀ ÉP XUỐNG DÒNG
    text_out = text_out.replace("**", "")

    text_out = re.sub(r'([^\n])\s*([a-d]\)\s+)', r'\1\n\n\2', text_out)
    text_out = re.sub(r'([^\n])\s*(\*(?:Chuyển giao nhiệm vụ học tập|Thực hiện nhiệm vụ học tập|Báo cáo kết quả và thảo luận|Kết luận)[^:\n]*:)', r'\1\n\n\2', text_out)
    
    return text_out

def validate_khbd_result(text):
    if len(text) < 500: return False, "Nội dung quá ngắn."
    return True, "Hợp lệ"

def build_prompt(thong_tin, noi_dung_chinh, noi_dung_ga, nls_str, tich_hop_ai, tich_hop_hoa_nhap, nhu_cau_hoa_nhap, mode, so_tiet):
    source = safe_text(noi_dung_chinh)[:25000] 
    ga_block = f"--- GIÁO ÁN CŨ ĐỂ CHỈNH SỬA ---\n{safe_text(noi_dung_ga)[:10000]}\n" if mode == "chinh_sua" else ""
    hoa_nhap_block = f"- Dạy học hòa nhập: {safe_text(nhu_cau_hoa_nhap)}." if tich_hop_hoa_nhap else ""
    ai_block = f"- Tích hợp AI: Đề xuất hoạt động ứng dụng." if tich_hop_ai else ""

    nhiem_vu = f"""
NHIỆM VỤ: SOẠN KẾ HOẠCH BÀI DẠY SIÊU CHI TIẾT TỪ TÀI LIỆU CUNG CẤP.
1. TUYỆT ĐỐI KHÔNG TÓM TẮT. Hãy bám sát tài liệu SGK dưới đây, TRÍCH XUẤT NGUYÊN VĂN các hoạt động khám phá, ví dụ, bài tập, công thức (dùng chuẩn LaTeX $...$) vào trong giáo án.
2. Bài học kéo dài {so_tiet} tiết. Phân bổ kiến thức đều đặn.
3. DÀN Ý BẮT BUỘC:

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
### TIẾT 1
**Hoạt động 1: MỞ ĐẦU**
a) Mục tiêu: ...
b) Nội dung: [Trích xuất cụ thể câu hỏi/bài toán từ tài liệu nguồn]
c) Sản phẩm: [Trích xuất cụ thể đáp án/lời giải chi tiết]
d) Tổ chức thực hiện: 
*Chuyển giao nhiệm vụ học tập: [Viết chi tiết nhiệm vụ giao cho HS]
*Thực hiện nhiệm vụ học tập: [Viết chi tiết cách HS làm việc]
*Báo cáo kết quả và thảo luận: [Viết chi tiết cách HS báo cáo và trao đổi]
*Kết luận: [Viết chi tiết nội dung GV chốt kiến thức]

PHỤ LỤC
PHIẾU HỌC TẬP
"""
    return f"--- THÔNG TIN CHUNG ---\n{thong_tin}\n\n{nhiem_vu}\n\n--- NGUỒN KIẾN THỨC CỐT LÕI TỪ TÀI LIỆU ---\n{source}\n\n{ga_block}"
