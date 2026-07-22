# -*- coding: utf-8 -*-
import streamlit as st
import re
import tempfile
import os
import time

# --- CÁC HÀM XỬ LÝ YOUTUBE ---
def extract_youtube_id(url):
    if not url: return None
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match: return match.group(1)
    return None

def get_youtube_transcript(url):
    video_id = extract_youtube_id(url)
    if not video_id: return None, "⚠️ Đường dẫn YouTube không hợp lệ."
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None
        try:
            transcript = transcript_list.find_transcript(['vi', 'en'])
        except Exception:
            for t in transcript_list:
                transcript = t
                break
        if not transcript: return None, "❌ Video này không có dữ liệu phụ đề."
        fetched_data = transcript.fetch()
        full_text = " ".join([item['text'] for item in fetched_data])
        return full_text, None
    except ImportError:
        return None, "❌ Hệ thống chưa cài đặt thư viện youtube-transcript-api."
    except Exception as e:
        error_msg = str(e).lower()
        if "no element found" in error_msg or "xml" in error_msg:
            return None, "❌ YouTube đang tạm chặn máy chủ tải dữ liệu. Vui lòng tải video về máy và dùng chức năng 'Tải tệp video lên'!"
        return None, f"❌ Lỗi YouTube API: {str(e)}"


# --- HÀM XỬ LÝ VIDEO TẢI LÊN BẰNG GEMINI MULTIMODAL ---
def get_gemini_api_key():
    """Lấy API Key của Gemini từ hệ thống để xử lý File"""
    if st.session_state.get("is_admin_mode"):
        return st.secrets.get("GEMINI_API_KEY")
    key = st.session_state.get("user_api_key")
    if key and key.startswith("AIza"):
        return key
    return None

def process_video_with_gemini(uploaded_file, prompt, api_key):
    """Lưu tệp tạm, đẩy lên Gemini API, phân tích và dọn dẹp"""
    try:
        import google.generativeai as genai
    except ImportError:
        return "❌ Lỗi: Máy chủ chưa cài đặt thư viện `google-generativeai`."

    genai.configure(api_key=api_key)
    
    # 1. Lưu file từ bộ nhớ tạm của Streamlit ra ổ cứng máy chủ (tạm thời)
    file_extension = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_video_path = tmp_file.name
        
    try:
        # 2. Upload file lên Gemini
        status_text = st.empty()
        status_text.info("⏳ Đang tải tệp lên hệ thống AI của Google... (Tùy dung lượng mà thời gian tải có thể mất từ 10s - 1 phút)")
        video_file = genai.upload_file(path=tmp_video_path)
        
        # 3. Chờ Gemini xử lý dữ liệu Video/Audio (Processing)
        status_text.info("🧠 AI đang 'xem' và 'nghe' video của thầy. Quá trình này đang diễn ra...")
        while video_file.state.name == "PROCESSING":
            time.sleep(3)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            raise Exception("Gemini từ chối xử lý video này (có thể do định dạng không hỗ trợ hoặc lỗi hệ thống Google).")
            
        # 4. Yêu cầu AI sinh văn bản theo Prompt dựa trên Video
        status_text.info("✍️ AI đang tổng hợp, dịch thuật và viết kịch bản...")
        model = genai.GenerativeModel(model_name="gemini-1.5-flash") # Dùng bản Flash cho tốc độ xử lý video cực nhanh
        response = model.generate_content([prompt, video_file])
        
        # 5. Dọn dẹp (Xóa file trên máy chủ Google và máy chủ cục bộ)
        genai.delete_file(video_file.name)
        os.remove(tmp_video_path)
        status_text.empty() # Xóa dòng thông báo trạng thái
        
        return response.text
        
    except Exception as e:
        if os.path.exists(tmp_video_path):
            os.remove(tmp_video_path)
        return f"❌ Lỗi xử lý Video AI: {str(e)}"


# --- GIAO DIỆN CHÍNH ---
def render_the_03(ai_engine=None):
    st.markdown("### 🎬 Công cụ Trích xuất, Chuyển văn bản & Dịch Video (YouTube & Tải lên)")
    st.caption("Hỗ trợ giáo viên lấy kịch bản, chuyển lời thoại thành văn bản và dịch nội dung từ video bất kỳ phục vụ giảng dạy.")

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown("#### ⚙️ Cấu hình nguồn video")
        
        nguon_video = st.radio(
            "Chọn nguồn video",
            ["Đường dẫn YouTube (URL)", "Tải tệp video/âm thanh lên máy (MP4, MP3, WAV, MOV)"],
            key="vproc_source"
        )

        yt_url = ""
        uploaded_video = None

        if nguon_video == "Đường dẫn YouTube (URL)":
            yt_url = st.text_input(
                "Nhập URL YouTube", 
                placeholder="Ví dụ: https://www.youtube.com/watch?v=...", 
                key="vproc_yt_url"
            )
        else:
            uploaded_video = st.file_uploader(
                "Tải lên tệp video hoặc âm thanh (Dung lượng < 200MB)", 
                type=["mp4", "avi", "mov", "mkv", "webm", "mp3", "wav"], 
                key="vproc_file"
            )

        st.markdown("#### 🛠️ Chọn tác vụ xử lý")
        tac_vu = st.selectbox(
            "Yêu cầu xử lý",
            [
                "📋 Sao chép toàn bộ kịch bản/lời thoại từ video",
                "🌐 Dịch nội dung video sang Tiếng Việt (hoặc ngôn ngữ khác)",
                "📝 Tóm tắt và phân tích nội dung cốt lõi từ video"
            ],
            key="vproc_action"
        )

        ngon_ngu_dich = "Tiếng Việt"
        if "Dịch" in tac_vu:
            ngon_ngu_dich = st.selectbox(
                "Ngôn ngữ đích dịch", 
                ["Tiếng Việt", "Tiếng Anh", "Tiếng Trung", "Tiếng Nhật", "Tiếng Hàn"], 
                key="vproc_lang"
            )

        btn_xu_ly = st.button("🚀 THỰC THI XỬ LÝ VIDEO", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### 📋 Kết quả xử lý văn bản")

        if btn_xu_ly:
            if nguon_video == "Đường dẫn YouTube (URL)" and not yt_url.strip():
                st.warning("⚠️ Vui lòng nhập đường dẫn URL YouTube hợp lệ.")
            elif nguon_video != "Đường dẫn YouTube (URL)" and not uploaded_video:
                st.warning("⚠️ Vui lòng tải lên một tệp video hoặc âm thanh.")
            else:
                # -------------------------------------------------------------
                # TRƯỜNG HỢP 1: XỬ LÝ YOUTUBE (Qua text transcript)
                # -------------------------------------------------------------
                if nguon_video == "Đường dẫn YouTube (URL)":
                    with st.spinner("🤖 Đang bóc tách dữ liệu từ YouTube..."):
                        raw_video_text, err_msg = get_youtube_transcript(yt_url)
                        if err_msg:
                            st.error(err_msg)
                        else:
                            prompt_v = f"""
                            BẠN LÀ TRỢ LÝ AI CHUYÊN PHÂN TÍCH, TỔNG HỢP VÀ DỊCH TÀI LIỆU GIÁO DỤC.
                            NHIỆM VỤ: Hãy thực hiện yêu cầu '{tac_vu}' {'sang ngôn ngữ ' + ngon_ngu_dich if 'Dịch' in tac_vu else ''}.
                            DỮ LIỆU LỜI THOẠI TRÍCH XUẤT:
                            {raw_video_text[:20000]}
                            
                            YÊU CẦU: Trình bày rõ ràng, mạch lạc, chia đoạn logic phục vụ cho giáo viên làm tài liệu hoặc bài giảng.
                            """
                            if ai_engine:
                                try:
                                    st.session_state["vproc_result"] = ai_engine.generate_text(prompt_v)
                                    st.success("🎉 Xử lý YouTube thành công!")
                                except Exception as e:
                                    st.error(f"❌ Lỗi AI: {str(e)}")
                            else:
                                st.error("❌ Không thể gọi AI (Chưa khởi tạo AI Engine).")
                
                # -------------------------------------------------------------
                # TRƯỜNG HỢP 2: XỬ LÝ FILE TẢI LÊN (Qua Gemini Multimodal)
                # -------------------------------------------------------------
                else:
                    gemini_key = get_gemini_api_key()
                    if not gemini_key:
                        st.error("❌ Tính năng Phân tích File Video yêu cầu API Key của Google Gemini. Vui lòng đăng nhập hệ thống bằng API Key bắt đầu với 'AIza...'.")
                    else:
                        prompt_multi = f"""
                        BẠN LÀ TRỢ LÝ AI CHUYÊN PHÂN TÍCH VIDEO/AUDIO CHO GIÁO DỤC.
                        Nhiệm vụ: {tac_vu} {'sang ' + ngon_ngu_dich if 'Dịch' in tac_vu else ''}.
                        Dựa trực tiếp vào nội dung nghe/nhìn được từ tệp đính kèm.
                        YÊU CẦU:
                        - Nếu có lời thoại, hãy trích xuất/dịch chính xác và có các mốc thời gian (timeline) tương đối.
                        - Phân đoạn mạch lạc, dễ hiểu để giáo viên đưa vào giáo án.
                        """
                        # Gọi hàm xử lý chuyên biệt
                        ket_qua_file = process_video_with_gemini(uploaded_video, prompt_multi, gemini_key)
                        st.session_state["vproc_result"] = ket_qua_file
                        st.success("🎉 AI đã xem/nghe và xử lý tệp tin thành công!")

        # Hiển thị kết quả lưu trong session
        if "vproc_result" in st.session_state:
            ket_qua_hien_tai = st.session_state["vproc_result"]
            st.text_area("Văn bản kết xuất:", value=ket_qua_hien_tai, height=500)
            st.download_button(
                "📥 Tải xuống kết quả (.txt)",
                data=ket_qua_hien_tai,
                file_name="Ket_qua_xu_ly_Video_Audio.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("💡 Tính năng đã sẵn sàng! Thầy tải lên một tệp MP4 hoặc dán Link YouTube để hệ thống phân tích nhé.")
