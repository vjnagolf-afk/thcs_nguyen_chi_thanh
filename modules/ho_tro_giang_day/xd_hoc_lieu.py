# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_hoc_lieu.py
Nhiệm vụ: Trợ lý Tổng hợp & Thiết kế Học liệu.
Nâng cấp: 
- Hỗ trợ Tải Video trực tiếp từ máy tính.
- TỰ ĐỘNG CÀO PHỤ ĐỀ YOUTUBE (Transcript) & WEB trước khi gửi cho AI.
============================================================
"""

import io
import urllib.parse as urlparse
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

# HÀM MỚI: Tự động trích xuất nội dung từ Link Web / YouTube
def extract_content_from_url(url):
    text_content = ""
    url = url.strip()
    
    if "youtube.com" in url or "youtu.be" in url:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            # Trích xuất Video ID
            parsed_url = urlparse.urlparse(url)
            video_id = ""
            if parsed_url.hostname in ['youtu.be']:
                video_id = parsed_url.path[1:]
            elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
                if parsed_url.path == '/watch':
                    video_id = urlparse.parse_qs(parsed_url.query)['v'][0]
            
            if video_id:
                # Ưu tiên lấy phụ đề tiếng Việt, nếu không có lấy tiếng Anh
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['vi', 'en'])
                text_content = " ".join([entry['text'] for entry in transcript])
                return True, f"[PHỤ ĐỀ YOUTUBE TỰ ĐỘNG TRÍCH XUẤT]:\n{text_content}"
            else:
                return False, "❌ Không thể nhận diện được Video ID từ đường link YouTube này."
                
        except ImportError:
            return False, "❌ Hệ thống thiếu thư viện. Vui lòng thêm `youtube-transcript-api` vào file requirements.txt"
        except Exception as e:
            return False, f"❌ Không thể lấy phụ đề (Video này có thể không hỗ trợ phụ đề hoặc bị khóa). Lỗi chi tiết: {e}"
            
    else:
        # Xử lý Link Web bình thường
        try:
            import requests
            from bs4 import BeautifulSoup
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Lấy toàn bộ chữ trong các thẻ p (đoạn văn)
            paragraphs = soup.find_all('p')
            text_content = "\n".join([p.get_text() for p in paragraphs])
            return True, f"[NỘI DUNG WEBSITE TỰ ĐỘNG TRÍCH XUẤT]:\n{text_content}"
        except ImportError:
            return False, "❌ Hệ thống thiếu thư viện. Vui lòng thêm `beautifulsoup4` và `requests` vào file requirements.txt"
        except Exception as e:
            return False, f"❌ Không thể truy cập trang web này (Có thể trang web chặn bot). Lỗi chi tiết: {e}"

def render_xd_hoc_lieu(ai_engine_cu=None):
    if "hl_result" not in st.session_state:
        st.session_state["hl_result"] = None
    if "hl_topic" not in st.session_state:
        st.session_state["hl_topic"] = "Hoc_Lieu"

    st.markdown("### 📚 Trợ lý Tổng hợp & Thiết kế Học liệu Đa phương tiện")
    st.info("💡 **Góc chuyên gia:** Hệ thống tự động phân tích từ đa nguồn (Văn bản, File, Upload Video, hoặc Link). Đối với Link YouTube, hệ thống sẽ tự động bóc tách phụ đề (transcript) để đảm bảo độ chính xác 100%.")

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
        url_input = ""

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
                st.success(f"✅ Đã tải lên Video: {uploaded_video.name}. Sẵn sàng bóc tách bằng Multimodal AI!")
                
        else:
            url_input = st.text_input("Dán đường dẫn (URL) Website hoặc Video YouTube:", placeholder="https://www.youtube.com/watch?v=...")
            st.caption("Hệ thống sẽ tự động truy cập và cào dữ liệu phụ đề (transcript) của Video trước khi gửi cho AI.")

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

        if not input_data_content.strip() and not uploaded_file and not uploaded_video and not url_input.strip():
            st.warning("⚠️ Vui lòng cung cấp văn bản, tải tệp, tải video hoặc dán Link tài liệu.")
            return

        # Nếu người dùng nhập URL, tiến hành cào dữ liệu trước
        if "Link" in nguon_nhap and url_input.strip():
            with st.spinner("⏳ Đang cào dữ liệu Phụ đề (Transcript) từ Link..."):
                success, extracted_info = extract_content_from_url(url_input)
                if not success:
                    st.error(extracted_info) # Báo lỗi nếu video không có phụ đề
                    return
                else:
                    st.success("✅ Đã lấy được nội dung từ Link! Đang chuyển cho AI xử lý...")
                    input_data_content = extracted_info

        with st.spinner(f"⏳ AI đang tiêu hóa tài liệu và chuyển hóa thành {loai_hoc_lieu.split('(')[0]}..."):
            prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA THIẾT KẾ HỌC LIỆU VÀ SƯ PHẠM ĐỈNH CAO.
Nhiệm vụ của bạn là phân tích nguồn dữ liệu do giáo viên cung cấp và chuyển đổi nó thành định dạng học liệu chuyên nghiệp.

--- THÔNG SỐ ĐẦU RA ---
- Định dạng yêu cầu: {loai_hoc_lieu}
- Đối tượng tiếp cận: {doi_tuong}
- Yêu cầu bổ sung: {yeu_cau_them if yeu_cau_them else 'Không có'}

--- NGUỒN DỮ LIỆU ĐẦU VÀO ---
{input_data_content[:20000] if input_data_content else "(Dữ liệu đầu vào là Video được đính kèm trực tiếp)"}

--- [QUY TRÌNH XỬ LÝ BẮT BUỘC] ---
Nếu dữ liệu đầu vào là văn bản Trích xuất từ Video/YouTube hoặc Video đính kèm: 
Bắt buộc mục đầu tiên trong kết quả của bạn phải là:
### 🎙️ Tóm tắt Nội dung cốt lõi của Video
SAY ĐÓ mới dùng chính nội dung này để thiết kế học liệu ở các phần tiếp theo. KHÔNG được tự bịa ra nội dung bên ngoài.

--- QUY TẮC THIẾT KẾ BẮT BUỘC TÙY THEO ĐỊNH DẠNG ---
1. Nếu là "Tóm tắt": Dùng Bullet points rõ ràng, bôi đậm từ khóa.
2. Nếu là "Sơ đồ tư duy": Trình bày dạng cây phân cấp logic (Sử dụng các ký tự -, *, > để thụt lề rõ ràng).
3. Nếu là "Kịch bản Thuyết trình": Chia rõ từng trang [Slide 1, Slide 2...]. Mỗi Slide phải có: Tiêu đề, Nội dung chữ, và Gợi ý hình ảnh/video minh họa.
4. Nếu là "Thẻ ghi nhớ (Flashcards)": Trình bày [Mặt trước: Câu hỏi] - [Mặt sau: Trả lời].
5. Nếu là "Ngân hàng câu hỏi": Đưa ra câu hỏi, đáp án và giải thích chi tiết.

[KỶ LUẬT ĐỊNH DẠNG SỐNG CÒN]
- Trình bày mạch lạc bằng Markdown.
- NẾU có công thức Toán/Lý/Hóa, TUYỆT ĐỐI bọc trong dấu `$ ... $`. KHÔNG dùng backtick (`) cho công thức Toán.
"""
            try:
                engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                
                # Xử lý nếu có tải lên Video từ máy tính (Multimodal)
                if uploaded_video:
                    video_part = {
                        "mime_type": uploaded_video.type,
                        "data": uploaded_video.getvalue()
                    }
                    contents = [prompt, video_part]
                    
                    if hasattr(engine_v2, "generate_multimodal"):
                        result = engine_v2.generate_multimodal(contents)
                    else:
                        result = "❌ Cần cập nhật hàm `generate_multimodal` trong `AIEngine2` để nhận file Video."
                else:
                    # Xử lý Text / Document / Web Transcript bình thường
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
