# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/quan_ly_to/kiem_tra_khbd.py
Nhiệm vụ: Kiểm tra, phê duyệt Kế hoạch bài dạy (Giáo án).
Chức năng: Đọc file PDF/Word, quét lỗi đa chiều theo CV 5512, 
hỗ trợ chat thông minh tương tác và báo cáo thẩm định toàn diện.
============================================================
"""

import streamlit as st
from pypdf import PdfReader
import re
import docx

def render_kiem_tra_khbd(ai_engine=None):
    st.markdown("### 🔎 Kiểm tra, phê duyệt Kế hoạch bài dạy (Giáo án)")
    st.caption("AI đọc trực tiếp file KHBD tải lên (hỗ trợ PDF và Word), rà soát lỗi đa chiều và trích dẫn minh chứng thực tế từ văn bản.")

    # --- KHỞI TẠO BỘ NHỚ TẠM ---
    if "chat_history_khbd" not in st.session_state:
        st.session_state.chat_history_khbd = [{"role": "assistant", "content": "Chào thầy/cô! Hãy nạp file KHBD ở cột bên trái và nhấn **'Quét & Phân tích'** nhé!"}]
    
    if "noidung_khbd" not in st.session_state:
        st.session_state.noidung_khbd = ""
        
    if "ai_analysis_report" not in st.session_state:
        st.session_state.ai_analysis_report = ""

    # --- HỖ TRỢ GỌI AI LINH HOẠT CHO MỌI LOẠI KHÓA ---
    def call_ai(prompt_text):
        # 1. Thử qua ai_engine truyền vào hoặc trong session
        engine = ai_engine or st.session_state.get("ai_engine", None)
        if engine and hasattr(engine, "generate_text"):
            try:
                return engine.generate_text(prompt_text)
            except Exception:
                pass

        # 2. Dự phòng gọi trực tiếp OpenAI bằng khóa sk-
        api_key = None
        for key, val in st.session_state.items():
            if isinstance(val, str) and val.startswith("sk-"):
                api_key = val
                break
        
        if not api_key:
            for k in ["user_api_key", "api_key", "openai_api_key", "sk_key"]:
                if st.session_state.get(k) and str(st.session_state.get(k)).startswith("sk-"):
                    api_key = st.session_state.get(k)
                    break
        
        if not api_key and "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]

        if api_key:
            from openai import OpenAI
            client = OpenAI(api_key=str(api_key).strip())
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_text}]
            )
            return response.choices[0].message.content
        
        return "❌ Không tìm thấy API Key hoặc AI Engine hợp lệ. Vui lòng kiểm tra lại cấu hình."

    # --- BỐ CỤC GIAO DIỆN CHÍNH ---
    col_left, col_right = st.columns([1, 2.2])

    # ==========================================
    # CỘT TRÁI: CONTROL PANEL 
    # ==========================================
    with col_left:
        with st.container(border=True):
            st.markdown("#### ⚙️ Cấu hình Kiểm tra")
            mon_hoc = st.selectbox("Môn học:", ["Khoa học Tự nhiên", "Toán học", "Ngữ Văn", "Tiếng Anh", "Tin học", "Khác"])
            khoi_lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
            
            st.markdown("**Tải file giáo án lên đây:**")
            file_khbd = st.file_uploader("Hỗ trợ định dạng PDF và Word (.docx)", type=["pdf", "docx"], label_visibility="collapsed")
            
            if st.button("🚀 Quét & Phân tích (Thực tế)", type="primary", use_container_width=True):
                if file_khbd:
                    valid_mime = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
                    if file_khbd.type not in valid_mime and not file_khbd.name.endswith(('.pdf', '.docx')):
                        st.error("⚠️ Định dạng file không hợp lệ! Hệ thống chỉ chấp nhận file PDF hoặc DOCX chuẩn.")
                    else:
                        with st.spinner("AI đang đọc file, trích xuất dữ liệu và lập bảng phân tích..."):
                            try:
                                st.session_state.chat_history_khbd = []
                                st.session_state.ai_analysis_report = ""
                                st.session_state.noidung_khbd = ""
                                
                                extracted_text = ""
                                
                                # XỬ LÝ NẾU LÀ FILE WORD (.docx)
                                if file_khbd.name.endswith(".docx"):
                                    doc = docx.Document(file_khbd)
                                    for para in doc.paragraphs:
                                        if para.text.strip():
                                            extracted_text += para.text + "\n"
                                    for table in doc.tables:
                                        for row in table.rows:
                                            row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                                            if row_data:
                                                extracted_text += " | ".join(row_data) + "\n"
                                
                                # XỬ LÝ NẾU LÀ FILE PDF (.pdf)
                                elif file_khbd.name.endswith(".pdf"):
                                    reader = PdfReader(file_khbd)
                                    for page in reader.pages:
                                        text = page.extract_text()
                                        if text:
                                            extracted_text += text + "\n"
                                
                                noidung = extracted_text[:60000]
                                noidung = re.sub(r'\s+', ' ', noidung).strip()
                                st.session_state.noidung_khbd = noidung
                                
                                prompt_scan = f"""
                                Bạn là chuyên gia thẩm định Kế hoạch bài dạy (KHBD) theo Công văn 5512. Hãy phân tích KHBD dưới đây và lập Báo cáo chi tiết theo 2 phần:

                                PHẦN 1: CẢNH BÁO LỖI & MÂU THUẪN (Kèm trích dẫn)
                                Chỉ ra các lỗi có thật trong văn bản theo 3 nhóm. BẮT BUỘC phải trích dẫn nguyên văn đoạn sai và chỉ rõ vị trí. Nếu không có lỗi, ghi "Không phát hiện lỗi".
                                - 🔤 Lỗi chính tả & Câu từ: Bỏ qua các lỗi do dính chữ khoảng trắng ngẫu nhiên, chỉ báo lỗi khi sai âm vần thực sự (VD: 'xắp xếp', 'năng lự').
                                - 🧠 Lỗi kiến thức khoa học.
                                - 🔗 Mâu thuẫn Logic & Hình thức (VD: Mục tiêu yêu cầu nhóm nhưng tổ chức cá nhân, mục tiêu yêu cầu vẽ sơ đồ nhưng sản phẩm không có...).

                                PHẦN 2: BẢNG ĐÁNH GIÁ 4 HOẠT ĐỘNG
                                Kẻ một bảng Markdown (gồm các cột: Hoạt động | Mục tiêu | Nội dung | Sản phẩm | Tổ chức thực hiện).
                                Đánh giá trạng thái thực tế của từng cột trong 4 hoạt động bằng các từ: Đạt / Cần sửa / Thiếu / Trống.

                                NỘI DUNG KHBD THỰC TẾ CẦN PHÂN TÍCH:
                                '''{st.session_state.noidung_khbd}'''
                                """
                                
                                report = call_ai(prompt_scan)
                                st.session_state.ai_analysis_report = report.replace("**", "")
                                
                                st.session_state.chat_history_khbd.append({"role": "assistant", "content": f"✅ Tôi đã phân tích xong giáo án **{mon_hoc} {khoi_lop}**. Mời thầy/cô xem **Báo cáo chi tiết** ở tab bên cạnh."})
                                st.rerun()
                            except Exception as e:
                                st.error(f"Lỗi hệ thống hoặc lỗi kết nối AI: {e}")
                else:
                    st.warning("⚠️ Vui lòng tải file KHBD (.pdf hoặc .docx) lên trước.")

    # ==========================================
    # CỘT PHẢI: KHUNG CHAT & DASHBOARD
    # ==========================================
    with col_right:
        tab_chat, tab_report = st.tabs(["💬 Trò chuyện với AI", "📊 Báo cáo AI phân tích (Thực tế)"])

        with tab_chat:
            chat_container = st.container(height=450)

            st.markdown("⚡ **Gợi ý kiểm tra nhanh:**")
            q1, q2 = st.columns(2)
            clicked_quick_prompt = None
            
            with q1:
                if st.button("🎯 Kiểm tra Mục tiêu (Bloom)", use_container_width=True): 
                    clicked_quick_prompt = "Hãy rà soát xem phần Mục tiêu đã dùng đúng động từ Bloom chưa? Nếu sai, hãy trích dẫn câu sai và gợi ý cách sửa."
                if st.button("🔄 Đề xuất lại HĐ Vận dụng", use_container_width=True): 
                    clicked_quick_prompt = "Dựa vào nội dung bài này, hãy đề xuất một Hoạt động Vận dụng gắn với thực tiễn đời sống để bổ sung vào giáo án."
            with q2:
                if st.button("💻 Gợi ý Tích hợp Năng lực số", use_container_width=True): 
                    clicked_quick_prompt = "Với bài học này, tôi có thể lồng ghép công cụ số, AI hay thí nghiệm ảo nào? Hãy gợi ý chi tiết."
                if st.button("📝 Chỉnh lại văn phong", use_container_width=True): 
                    clicked_quick_prompt = "Hãy tìm các đoạn diễn đạt lủng củng trong giáo án và viết lại chúng sao cho chuẩn văn phong sư phạm."

            st.markdown("---")
            btn_tham_dinh = st.button("🧐 BÁO CÁO THẨM ĐỊNH TOÀN DIỆN (5 TIÊU CHÍ TỔ TRƯỞNG)", use_container_width=True, type="primary")

            user_input = st.chat_input("Hỏi AI về nội dung giáo án đang tải lên...")
            
            prompt = user_input or clicked_quick_prompt
            
            if btn_tham_dinh:
                if not st.session_state.noidung_khbd:
                    st.warning("⚠️ Thầy cần tải file KHBD lên và bấm 'Quét & Phân tích' trước khi thẩm định!")
                else:
                    st.session_state.chat_history_khbd.append({"role": "user", "content": "Hãy thẩm định KHBD này theo 5 tiêu chí của Tổ trưởng chuyên môn."})
            
            elif prompt:
                if not st.session_state.noidung_khbd:
                    st.warning("⚠️ Hãy tải file và Quét KHBD trước khi hỏi AI nhé!")
                else:
                    st.session_state.chat_history_khbd.append({"role": "user", "content": prompt})

            with chat_container:
                for msg in st.session_state.chat_history_khbd:
                    with st.chat_message(msg["role"]): 
                        st.markdown(msg["content"])
                
                if btn_tham_dinh and st.session_state.noidung_khbd:
                    with st.chat_message("assistant"):
                        with st.spinner("🕵️‍♂️ Tổ trưởng AI đang phân tích sâu 5 tiêu chí..."):
                            try:
                                prompt_template = ""
                                try:
                                    with open("prompts/prompt_tham_dinh_khbd.txt", "r", encoding="utf-8") as f:
                                        prompt_template = f.read()
                                except FileNotFoundError:
                                    # Fallback prompt chuẩn nếu chưa có file ngoài
                                    prompt_template = "Hãy thẩm định chi tiết Kế hoạch bài dạy sau theo 5 tiêu chí giáo dục phổ thông:\n[NOI_DUNG_KHBD_ODAY]"

                                prompt_hoan_thien = prompt_template.replace("[NOI_DUNG_KHBD_ODAY]", st.session_state.noidung_khbd)
                                
                                ket_qua_tham_dinh = call_ai(prompt_hoan_thien).replace("**", "")
                                
                                st.markdown(ket_qua_tham_dinh)
                                st.session_state.chat_history_khbd.append({"role": "assistant", "content": ket_qua_tham_dinh})
                            except Exception as e:
                                st.error(f"Lỗi hệ thống: {e}")

                elif prompt and st.session_state.noidung_khbd:
                    with st.chat_message("assistant"):
                        with st.spinner("AI đang đọc lại giáo án và trả lời..."):
                            try:
                                chat_prompt = f"Dựa vào nội dung KHBD sau:\n\n{st.session_state.noidung_khbd}\n\nThực hiện yêu cầu sau: {prompt}"
                                ai_response = call_ai(chat_prompt).replace("**", "")
                                
                                st.markdown(ai_response)
                                st.session_state.chat_history_khbd.append({"role": "assistant", "content": ai_response})
                            except Exception as e:
                                st.error(f"Lỗi gọi AI: {e}")

        with tab_report:
            if st.session_state.ai_analysis_report:
                st.success("Báo cáo dưới đây được AI tổng hợp TRỰC TIẾP từ dữ liệu file vừa tải lên.")
                st.markdown(st.session_state.ai_analysis_report)
            else:
                st.info("💡 Bảng điều khiển đang trống. Vui lòng tải file giáo án (.docx hoặc .pdf) lên và nhấn 'Quét & Phân tích'.")
