# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_phan_tich_bh.py
Nhiệm vụ: Trợ lý Phân tích Bài học (Lesson Study Analytics).
Chức năng: Phân tích Video tiết học, đối chiếu Giáo án, 
đánh giá tương tác và cung cấp Chatbot hỗ trợ phản ngẫm chuyên môn.
============================================================
"""

import io
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

def extract_text_from_file(uploaded_file):
    if not uploaded_file:
        return ""
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    extracted_text = ""
    try:
        if file_name.endswith('.docx'):
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            extracted_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
        elif file_name.endswith('.pdf'):
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_text = "\n".join([page.get_text("text") for page in doc])
        elif file_name.endswith(('.txt', '.md')):
            extracted_text = file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Lỗi đọc file: {e}")
        st.error(f"Không thể đọc file {file_name}. Vui lòng kiểm tra định dạng.")
    return extracted_text

def render_xd_phan_tich_bh(ai_engine_cu=None):
    if "ls_result" not in st.session_state:
        st.session_state["ls_result"] = None
    if "ls_chat_history" not in st.session_state:
        st.session_state["ls_chat_history"] = []

    st.markdown("### 🔬 Trợ lý Phân tích Bài học (Lesson Study AI)")
    st.info("💡 **Góc chuyên gia:** Phân tích toàn diện mức độ hiệu quả của tiết học bằng cách đối chiếu thực tế (Video) với kế hoạch (Giáo án). AI sẽ đo lường tương tác, phát hiện điểm nghẽn và đưa ra khuyến nghị phương pháp dạy học tích cực.")

    # ========================================================
    # BƯỚC 1: TẢI LÊN DỮ LIỆU ĐẦU VÀO (DATA INPUTS)
    # ========================================================
    with st.expander("📥 BƯỚC 1: Cung cấp Dữ liệu Phân tích", expanded=(st.session_state["ls_result"] is None)):
        col_file, col_vid = st.columns(2)
        
        with col_file:
            st.markdown("**1. Kế hoạch Bài dạy & Biên bản**")
            upl_giao_an = st.file_uploader("Tải lên Giáo án (PDF, Word):", type=["pdf", "docx"])
            ghi_chu_quan_sat = st.text_area("Ghi chú của người dự giờ (Tùy chọn):", height=100, placeholder="VD: Phút thứ 15 học sinh có vẻ chưa hiểu rõ lệnh của giáo viên...")
            
        with col_vid:
            st.markdown("**2. Thực tế Tiết học**")
            upl_video = st.file_uploader("Tải lên Video/Audio ghi hình tiết học (MP4, MP3):", type=["mp4", "mov", "mp3", "wav", "m4a"])
            if upl_video:
                if upl_video.name.endswith(('mp4', 'mov')):
                    st.video(upl_video)
                else:
                    st.audio(upl_video)
                    
        btn_phan_tich = st.button("🚀 BƯỚC 2: TIẾN HÀNH PHÂN TÍCH TIẾT HỌC", type="primary", use_container_width=True)

    # ========================================================
    # BƯỚC 2: AI XỬ LÝ ĐA PHƯƠNG TIỆN (MULTIMODAL)
    # ========================================================
    if btn_phan_tich:
        if AIEngine2 is None:
            st.error("❌ Không tìm thấy hệ thống AIEngine2.")
            return
            
        if not upl_giao_an and not upl_video:
            st.warning("⚠️ Vui lòng cung cấp ít nhất một file Giáo án hoặc Video/Audio để AI có cơ sở phân tích.")
            return

        with st.spinner("⏳ Khởi động Trợ lý Lesson Study... Đang tổng hợp đối chiếu Video và Giáo án. Quá trình này có thể mất 1-2 phút..."):
            
            # Trích xuất văn bản giáo án
            noi_dung_giao_an = extract_text_from_file(upl_giao_an) if upl_giao_an else "Không có giáo án đối chiếu."
            
            prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA PHÂN TÍCH CHƯƠNG TRÌNH DẠY HỌC (LESSON STUDY ANALYST) VÀ CHUYÊN GIA SƯ PHẠM ĐỈNH CAO.
Nhiệm vụ của bạn là đánh giá tiết học dựa trên các dữ liệu đầu vào.

--- DỮ LIỆU ĐẦU VÀO ---
1. Kế hoạch bài dạy (Giáo án dự kiến): 
{noi_dung_giao_an[:15000]}

2. Ghi chú của người dự giờ:
{ghi_chu_quan_sat if ghi_chu_quan_sat else 'Không có.'}

3. Dữ liệu thực tế: (File Video/Audio được đính kèm trực tiếp)

--- YÊU CẦU PHÂN TÍCH CỐT LÕI (Dashboard Report) ---
Hãy tạo ra một Báo cáo Trực quan (Sử dụng Markdown chuẩn, biểu tượng cảm xúc) bao gồm 3 phần chính:

### 🎥 1. Phân tích Diễn biến & Tương tác (Interaction Mapping)
- Đánh giá tỷ lệ thời gian giáo viên nói (TTT) so với học sinh nói/hoạt động (STT). Cho biết tỷ lệ này đã phù hợp với phương pháp dạy học tích cực chưa (lý tưởng là giáo viên < 40%).
- Phân tích trạng thái, sự hào hứng và mức độ tham gia của học sinh qua các giai đoạn trong video.

### 📉 2. Đánh giá Độ vênh Giáo án (Lesson Plan Alignment)
- So sánh thời lượng thực tế với timeline trong giáo án. Có hoạt động nào bị lướt quá nhanh hoặc "cháy giáo án" không?
- Mục tiêu bài học đề ra có đạt được qua các hoạt động thực tế không?

### 💡 3. Phát hiện Điểm nghẽn & Khuyến nghị Sư phạm
- Chỉ ra các "Điểm nghẽn học tập" (những lúc học sinh im lặng, lúng túng hoặc hiểu sai lệnh).
- Gợi ý cụ thể các kỹ thuật dạy học tích cực (như Khăn trải bàn, Mảnh ghép, Trạm, Think-Pair-Share...) để thay thế hoặc cải thiện các hoạt động chưa hiệu quả.

[KỶ LUẬT ĐẦU RA]
Chỉ xuất ra Báo cáo theo đúng 3 cấu trúc trên. Lời văn chuyên nghiệp, mang tính xây dựng, tôn trọng giáo viên dạy thực nghiệm.
"""
            try:
                engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                contents = []
                
                # Nạp văn bản
                contents.append(prompt)
                
                # Nạp Video/Audio nếu có
                if upl_video:
                    media_part = {
                        "mime_type": upl_video.type,
                        "data": upl_video.getvalue()
                    }
                    contents.append(media_part)
                
                if hasattr(engine_v2, "generate_multimodal") and upl_video:
                    result = engine_v2.generate_multimodal(contents)
                else:
                    result = engine_v2.generate_text(prompt, temperature=0.3)
                    
                if result.startswith("❌"):
                    st.error(result)
                else:
                    st.session_state["ls_result"] = result
                    # Reset chat khi có bài phân tích mới
                    st.session_state["ls_chat_history"] = [{"role": "assistant", "content": "Báo cáo phân tích đã sẵn sàng! Thầy/Cô muốn thảo luận sâu hơn về hoạt động nào trong tiết học vừa rồi?"}]
            except Exception as e:
                st.error(f"❌ Lỗi xử lý AI: {e}")

    # ========================================================
    # BƯỚC 3: DASHBOARD BÁO CÁO KẾT QUẢ
    # ========================================================
    if st.session_state["ls_result"]:
        st.markdown("---")
        st.markdown("### 📊 BƯỚC 3: Báo cáo Phân tích Bài học (Dashboard)")
        
        with st.container(border=True):
            st.markdown(st.session_state["ls_result"], unsafe_allow_html=True)
            
            st.markdown("#### 📥 Xuất Biên bản Lesson Study")
            if export_word is None:
                st.warning("⚠️ Module Word chưa sẵn sàng.")
            else:
                try:
                    export_data = {
                        "ai_generated_content": st.session_state["ls_result"],
                        "is_dkt": False
                    }
                    word_bytes = export_word(export_data)
                    st.download_button(
                        label="📘 TẢI BÁO CÁO (.DOCX)",
                        data=word_bytes,
                        file_name="Bien_Ban_Lesson_Study.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Lỗi xuất Word: {e}")

        # ========================================================
        # BƯỚC 4: CHATBOT THẢO LUẬN & ĐÀO SÂU (COLLABORATIVE REFLECTION)
        # ========================================================
        st.markdown("---")
        st.markdown("### 💬 BƯỚC 4: Chatbot Thảo luận Chuyên môn")
        st.caption("Hãy đặt câu hỏi trực tiếp cho AI dựa trên báo cáo trên (VD: 'Làm sao cải thiện hoạt động nhóm ở phút 20?', 'Lệnh giao việc của tôi có vấn đề gì?').")
        
        chat_container = st.container(height=400, border=True)
        
        with chat_container:
            for message in st.session_state["ls_chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
        if user_query := st.chat_input("Hỏi Trợ lý về cách cải thiện tiết học..."):
            st.session_state["ls_chat_history"].append({"role": "user", "content": user_query})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_query)
                    
                with st.chat_message("assistant"):
                    with st.spinner("Đang tư vấn chuyên môn..."):
                        # Gom ngữ cảnh phân tích trước đó vào prompt
                        chat_context = "\n".join([f"{'GV' if m['role']=='user' else 'AI'}: {m['content']}" for m in st.session_state["ls_chat_history"][-4:-1]])
                        
                        chat_prompt = f"""
BẠN LÀ CHUYÊN GIA SƯ PHẠM ĐANG THẢO LUẬN RÚT KINH NGHIỆM TIẾT DẠY (LESSON STUDY) VỚI GIÁO VIÊN.
Dựa vào bản Báo cáo phân tích bài học dưới đây:
{st.session_state['ls_result']}

Và lịch sử trò chuyện ngắn:
{chat_context}

Giáo viên vừa hỏi: "{user_query}"
Hãy trả lời một cách mang tính xây dựng, thực tế, chỉ ra lỗi sai (nếu có) một cách khéo léo và đề xuất cách làm chi tiết, dễ áp dụng vào lớp học.
"""
                        try:
                            engine_v2 = AIEngine2(default_model="gemini-2.5-flash")
                            reply = engine_v2.generate_text(chat_prompt)
                            st.markdown(reply)
                            st.session_state["ls_chat_history"].append({"role": "assistant", "content": reply})
                        except Exception as e:
                            st.error(f"Lỗi truy vấn: {e}")
