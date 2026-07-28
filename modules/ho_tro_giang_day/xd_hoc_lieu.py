# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_hoc_lieu.py
Nhiệm vụ: Trợ lý Tổng hợp & Thiết kế Học liệu.
Nâng cấp: 
- Hỗ trợ Tải Video trực tiếp từ máy tính.
- Ép AI bám sát phụ đề/lời thoại (Transcript) và tóm tắt lời thoại trước khi tạo học liệu.
============================================================
"""

import io
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word của dự án
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2 để dùng Smart Router
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# Hàm đọc nội dung từ file tài liệu (Văn bản)
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
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_text = "\n".join([page.get_text("text") for page in doc])
        elif file_name.endswith(('.txt', '.md')):
            extracted_text = file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Lỗi đọc file: {e}")
        st.error(f"Không thể đọc file {file_name}. Vui lòng kiểm tra định dạng.")
    return extracted_text

def render_xd_hoc_lieu(ai_engine_cu=None):
    if "hl_result" not in st.session_state:
        st.session_state["hl_result"] = None
    if "hl_topic" not in st.session_state:
        st.session_state["hl_topic"] = "Hoc_Lieu"

    st.markdown("### 📚 Trợ lý Tổng hợp & Thiết kế Học liệu Đa phương tiện")
    st.info("💡 **Góc chuyên gia:** Hệ thống tự động phân tích từ đa nguồn (Văn bản dài, File PDF/Word, Tải Video trực tiếp, hoặc Link YouTube) để chuyển hóa thành các định dạng học liệu trực quan. Đặc biệt bám sát phụ đề/lời thoại để đảm bảo tính chính xác.")

    with st.container(border=True):
        st.markdown("#### 1️⃣ Cấu hình Nguồn Dữ liệu (Input)")
        
        nguon_nhap = st.radio(
            "Chọn phương thức nạp kiến thức thô:",
            ["✍️ Dán văn bản", "📁 Tải lên Tài liệu (PDF/Word)", "🎬 Tải lên Video", "🌐 Dán Link Web / YouTube"],
            horizontal=True
        )

        input_data_content = ""
        uploaded_file = None
        uploaded_video = None

        if "văn bản" in nguon_nhap:
            input_data_content = st.text_area("Dán nội dung kiến thức thô vào đây:", height=150, placeholder="Ví dụ: Đoạn văn bản dài về Lịch sử Việt Nam, tài liệu khoa học...")
        
        elif "Tài liệu" in nguon_nhap:
            uploaded_file = st.file_uploader("Tải lên tài liệu tham khảo (PDF, DOCX, TXT):", type=["pdf", "docx", "txt", "md"])
            if uploaded_file:
                with st.spinner("Đang đọc dữ liệu từ tệp..."):
                    input_data_content = extract_text_from_file(uploaded_file)
                    st.success(f"✅ Đã đọc thành công tài liệu: {uploaded_file.name}")
                    
        elif "Video" in nguon_nhap:
            uploaded_video = st.file_uploader("Tải lên Video bài giảng (MP4, MOV, AVI):", type=["mp4", "mov", "avi"])
            if uploaded_video:
                st.video(uploaded_video)
                st.success(f"✅ Đã tải lên Video: {uploaded_video.name}. Sẵn sàng bóc tách lời thoại!")
                
        else:
            input_data_content = st.text_input("Dán đường dẫn (URL) Website hoặc Video YouTube:", placeholder="https://www.youtube.com/watch?v=... hoặc https://vi.wikipedia.org/...")
            st.caption("AI (Gemini 1.5 Pro) sẽ tự động truy cập, lắng nghe lời thoại và bóc tách phụ đề (transcript) của Video YouTube.")

        st.markdown("---")
        st.markdown("#### 2️⃣ Thiết lập Định dạng Đầu ra (Output)")
        
        col_out1, col_out2 = st.columns(2)
        with col_out1:
            loai_hoc_lieu = st.selectbox(
                "Chọn định dạng học liệu cần tạo:", 
                [
                    "Tóm tắt Ý chính (Bullet points trọng tâm)", 
                    "Sơ đồ tư duy (Mindmap dạng phân cấp văn bản)", 
                    "Kịch bản Thuyết trình (Cấu trúc Slides & hình ảnh gợi ý)", 
                    "Thẻ ghi nhớ (Flashcards dạng Q&A ôn tập)",
                    "Ngân hàng Câu hỏi tự luận & Trắc nghiệm ngắn"
                ]
            )
        with col_out2:
            doi_tuong = st.selectbox(
                "Đối tượng học sinh:", 
                [
                    "Tiểu học (Ngôn từ vui nhộn, hình ảnh sinh động, dễ hiểu)",
                    "Cấp THCS (Trực quan, logic, gắn với thực tế)", 
                    "Cấp THPT (Sâu sắc, phân tích học thuật, tư duy phản biện)", 
                    "Giáo viên / Sinh viên (Học thuật, chuyên sâu)"
                ]
            )
            
        yeu_cau_them = st.text_area("Yêu cầu bổ sung (Tuỳ chọn):", height=60, placeholder="VD: Nhấn mạnh vào các mốc thời gian, có giải thích từ vựng khó...")
        
        btn_tao = st.button("🪄 THIẾT KẾ HỌC LIỆU NGAY", type="primary", use_container_width=True)

    # ========================================================
    # XỬ LÝ GỌI AI THIẾT KẾ HỌC LIỆU
    # ========================================================
    if btn_tao:
        if AIEngine2 is None:
            st.error("❌ Không tìm thấy file `utils/ai_engine_2.py`.")
            return

        if not input_data_content.strip() and not uploaded_file and not uploaded_video:
            st.warning("⚠️ Vui lòng cung cấp văn bản, tải tệp, tải video hoặc dán Link tài liệu.")
        else:
            with st.spinner(f"⏳ AI đang tiêu hóa tài liệu và chuyển hóa thành {loai_hoc_lieu.split('(')[0]}..."):
                prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA THIẾT KẾ HỌC LIỆU VÀ SƯ PHẠM ĐỈNH CAO.
Nhiệm vụ của bạn là phân tích nguồn dữ liệu do giáo viên cung cấp và chuyển đổi nó thành định dạng học liệu chuyên nghiệp.

--- THÔNG SỐ ĐẦU RA ---
- Định dạng yêu cầu: {loai_hoc_lieu}
- Đối tượng tiếp cận: {doi_tuong}
- Yêu cầu bổ sung: {yeu_cau_them if yeu_cau_them else 'Không có'}

--- NGUỒN DỮ LIỆU ĐẦU VÀO ---
{input_data_content[:15000] if input_data_content else "(Dữ liệu đầu vào là Video được đính kèm)"}

--- [QUY TRÌNH XỬ LÝ VIDEO BẮT BUỘC] ---
Nếu dữ liệu đầu vào là Video hoặc Link Video YouTube: Bạn BẮT BUỘC phải lắng nghe, bám sát vào phụ đề (transcript), lời thoại của nhân vật/giảng viên trong video. 
Khởi đầu kết quả, BẮT BUỘC phải có mục:
### 🎙️ Tóm tắt Lời thoại / Phụ đề Video
(Chuyển hóa toàn bộ lời thoại/âm thanh trong video thành một văn bản tóm tắt nội dung cực kỳ chi tiết).
SAY ĐÓ mới dùng chính nội dung tóm tắt này để thiết kế học liệu ở các phần tiếp theo. KHÔNG được tự bịa ra nội dung nếu không có trong lời thoại.

--- QUY TẮC THIẾT KẾ BẮT BUỘC TÙY THEO ĐỊNH DẠNG ---
1. Nếu là "Tóm tắt": Dùng Bullet points rõ ràng, bôi đậm từ khóa cốt lõi.
2. Nếu là "Sơ đồ tư duy": Trình bày dạng cây phân cấp logic (Sử dụng các ký tự -, *, > để thụt lề rõ ràng, từ khóa ngắn gọn).
3. Nếu là "Kịch bản Thuyết trình": Chia rõ từng trang [Slide 1, Slide 2...]. Mỗi Slide phải có: Tiêu đề, Nội dung chữ, và Gợi ý hình ảnh/video.
4. Nếu là "Thẻ ghi nhớ (Flashcards)": Trình bày [Mặt trước: Câu hỏi] - [Mặt sau: Trả lời].
5. Nếu là "Ngân hàng câu hỏi": Đưa ra câu hỏi, đáp án và giải thích.

[KỶ LUẬT ĐỊNH DẠNG SỐNG CÒN]
- Trình bày mạch lạc bằng Markdown.
- NẾU có công thức Toán/Lý/Hóa, TUYỆT ĐỐI bọc trong dấu `$ ... $`. KHÔNG dùng backtick (`) cho công thức Toán.
"""
                try:
                    engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                    
                    # Xử lý nếu có tải lên Video (Multimodal)
                    if uploaded_video:
                        # Gói file video vào định dạng từ điển theo chuẩn API
                        video_part = {
                            "mime_type": uploaded_video.type,
                            "data": uploaded_video.getvalue()
                        }
                        contents = [prompt, video_part]
                        
                        if hasattr(engine_v2, "generate_multimodal"):
                            result = engine_v2.generate_multimodal(contents)
                        else:
                            result = "❌ Cần cập nhật hàm `generate_multimodal` trong `AIEngine2` để có thể nhận trực tiếp file Video."
                    else:
                        # Xử lý Text / Document / Link bình thường
                        result = engine_v2.generate_text(prompt, temperature=0.7)
                    
                    if result.startswith("❌") or result.startswith("⚠️"):
                        st.error(result)
                    else:
                        st.session_state["hl_result"] = result
                        st.session_state["hl_topic"] = loai_hoc_lieu.split("(")[0].strip().replace(" ", "_")
                except Exception as e:
                    st.error(f"❌ Lỗi khi gọi AI: {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ & XUẤT FILE
    # ========================================================
    if st.session_state.get("hl_result"):
        st.markdown("---")
        st.markdown(f"### 📑 Kết quả: {st.session_state['hl_topic'].replace('_', ' ')}")
        st.markdown(st.session_state["hl_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Tải xuống Học liệu")
        col_txt, col_word = st.columns(2)
        
        with col_txt:
            st.download_button(
                label="📄 Tải học liệu (.TXT)",
                data=st.session_state["hl_result"],
                file_name=f"Hoc_Lieu_{st.session_state['hl_topic']}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        with col_word:
            if export_word is None:
                st.warning("⚠️ Module Word chưa sẵn sàng.")
            else:
                try:
                    export_data = {
                        "ai_generated_content": st.session_state["hl_result"],
                        "is_dkt": False
                    }
                    with st.spinner("Đang kết xuất file Word..."):
                        word_bytes = export_word(export_data)
                    
                    st.download_button(
                        label="📘 Tải học liệu (.DOCX)",
                        data=word_bytes,
                        file_name=f"Hoc_Lieu_{st.session_state['hl_topic']}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Lỗi xuất Word: {e}")
                    
        if st.button("🔄 Tạo Học liệu Mới", use_container_width=True):
            st.session_state["hl_result"] = None
            st.rerun()
