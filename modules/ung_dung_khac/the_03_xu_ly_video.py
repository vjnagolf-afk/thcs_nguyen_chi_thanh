# -*- coding: utf-8 -*-
import streamlit as st
import re
import tempfile
import os
import time

# =========================================================
# KHỞI TẠO STATE
# =========================================================
def init_state():
    if "vproc_result" not in st.session_state:
        st.session_state["vproc_result"] = None

# =========================================================
# HÀM XỬ LÝ YOUTUBE (Cập nhật API mới >= 1.2.x)
# =========================================================
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

def get_youtube_transcript_new(url):
    """
    Sử dụng API mới của youtube-transcript-api (>=1.2.4).
    Trả về: (văn_bản, thông_báo_lỗi, có_thể_dùng_fallback_âm_thanh_không?)
    """
    video_id = extract_youtube_id(url)
    if not video_id: 
        return None, "⚠️ Đường dẫn YouTube không hợp lệ.", False
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        
        # Cố gắng lấy phụ đề tiếng Việt hoặc tiếng Anh
        try:
            fetched_transcript = ytt_api.fetch(video_id, languages=["vi", "en"])
        except Exception:
            # Nếu không có vi/en, lấy danh sách và chọn cái đầu tiên
            transcript_list = ytt_api.list(video_id)
            fetched_transcript = next(iter(transcript_list)).fetch()
            
        full_text = " ".join([item['text'] for item in fetched_transcript])
        return full_text, None, False
        
    except ImportError:
        return None, "❌ Thư viện 'youtube-transcript-api' chưa được cài đặt.", False
    except Exception as e:
        error_msg = str(e).lower()
        
        # CHỈ TỪ CHỐI khi video yêu cầu đăng nhập / giới hạn độ tuổi (vì tool cũng không tải được)
        if "age restricted" in error_msg or "login" in error_msg:
            return None, "🔒 Video có thể bị giới hạn quyền truy cập (giới hạn độ tuổi/riêng tư). Vui lòng thử video khác.", False
            
        # VỚI MỌI LỖI KHÁC: Bật cờ True để ép hệ thống chuyển sang tải File Âm thanh!
        else:
            return None, f"⚠️ Không lấy được phụ đề chữ (Chi tiết: {str(e)[:80]}...).", True
# =========================================================
# HÀM DỰ PHÒNG: TẢI ÂM THANH TỪ YOUTUBE (Fallback)
# =========================================================
def download_youtube_audio_fallback(url):
    """Tải luồng âm thanh nhẹ nhất từ YouTube để nạp cho Gemini"""
    try:
        import yt_dlp
    except ImportError:
        return None, "⚠️ Không thể chạy tính năng dự phòng vì thiếu thư viện 'yt-dlp'."

    temp_dir = tempfile.gettempdir()
    out_tmpl = os.path.join(temp_dir, 'yt_audio_%(id)s.%(ext)s')
    
    ydl_opts = {
        'format': 'm4a/bestaudio/best', # Lấy trực tiếp m4a/webm cho nhẹ, không cần ffmpeg convert
        'outtmpl': out_tmpl,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get('ext', 'm4a')
            audio_path = os.path.join(temp_dir, f"yt_audio_{info['id']}.{ext}")
            if os.path.exists(audio_path):
                return audio_path, None
            return None, "Lỗi: Không tìm thấy file âm thanh sau khi tải."
    except Exception as e:
        return None, f"Không thể tải âm thanh dự phòng: {str(e)}"

# =========================================================
# HÀM XỬ LÝ ĐA PHƯƠNG TIỆN VỚI GEMINI
# =========================================================
def get_gemini_api_key():
    if st.session_state.get("is_admin_mode"): return st.secrets.get("GEMINI_API_KEY")
    key = st.session_state.get("user_api_key")
    if key and key.startswith("AIza"): return key
    return None

def process_multimodal_gemini(file_path, prompt, api_key):
    """Xử lý trực tiếp File Video/Audio bằng Gemini Multimodal"""
    try:
        import google.generativeai as genai
    except ImportError:
        return "❌ Máy chủ chưa cài đặt thư viện 'google-generativeai'."

    genai.configure(api_key=api_key)
    
    # Lấy tên model từ cấu hình (Khắc phục lỗi hardcode model)
    model_name = st.secrets.get("GEMINI_VIDEO_MODEL", "gemini-2.5-flash")
    if "2.5" not in model_name: # Fallback an toàn nếu chưa có bản 2.5
        model_name = "gemini-1.5-flash"
        
    try:
        status_text = st.empty()
        status_text.info(f"⏳ Đang tải tệp lên hệ thống AI của Google ({model_name})...")
        media_file = genai.upload_file(path=file_path)
        
        status_text.info("🧠 AI đang phân tích dữ liệu âm thanh/hình ảnh. Vui lòng đợi...")
        while media_file.state.name == "PROCESSING":
            time.sleep(3)
            media_file = genai.get_file(media_file.name)
            
        if media_file.state.name == "FAILED":
            raise Exception("Google AI từ chối xử lý tệp này.")
            
        status_text.info("✍️ AI đang tổng hợp và viết kịch bản...")
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content([prompt, media_file])
        
        genai.delete_file(media_file.name)
        status_text.empty()
        
        return response.text
    except Exception as e:
        return f"❌ Lỗi xử lý Đa phương tiện AI: {str(e)}"


# =========================================================
# GIAO DIỆN CHÍNH
# =========================================================
def render_the_03(ai_engine=None):
    init_state()
    st.markdown("### 🎬 Công cụ Trích xuất, Chuyển văn bản & Dịch Video (YouTube & Tải lên)")
    st.caption("Hỗ trợ giáo viên lấy kịch bản, chuyển lời thoại thành văn bản và dịch nội dung từ video bất kỳ phục vụ giảng dạy.")

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown("#### ⚙️ Cấu hình nguồn video")
        nguon_video = st.radio(
            "Chọn nguồn video",
            ["Đường dẫn YouTube (URL)", "Tải tệp lên máy (MP4, MP3, WAV, MOV)"],
            key="vproc_source"
        )

        yt_url = ""
        uploaded_video = None

        if nguon_video == "Đường dẫn YouTube (URL)":
            yt_url = st.text_input("Nhập URL YouTube", placeholder="Ví dụ: https://www.youtube.com/watch?v=...", key="vproc_yt_url")
        else:
            uploaded_video = st.file_uploader(
                "Tải lên tệp video/âm thanh (Dung lượng < 200MB)", 
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
            ngon_ngu_dich = st.selectbox("Ngôn ngữ đích dịch", ["Tiếng Việt", "Tiếng Anh", "Tiếng Trung"], key="vproc_lang")

        btn_xu_ly = st.button("🚀 THỰC THI XỬ LÝ VIDEO", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### 📋 Kết quả xử lý văn bản")

        if btn_xu_ly:
            # Validation
            if nguon_video == "Đường dẫn YouTube (URL)" and not yt_url.strip():
                st.warning("⚠️ Vui lòng nhập đường dẫn URL YouTube.")
                st.stop()
            elif nguon_video != "Đường dẫn YouTube (URL)":
                if not uploaded_video:
                    st.warning("⚠️ Vui lòng tải lên một tệp.")
                    st.stop()
                # Kiểm tra dung lượng tệp (Khắc phục Nhược điểm 3)
                if uploaded_video.size > 200 * 1024 * 1024:
                    st.error("❌ Tệp vượt quá giới hạn dung lượng cho phép (200MB). Vui lòng thử tệp nhẹ hơn.")
                    st.stop()

            # BẮT ĐẦU XỬ LÝ
            gemini_key = get_gemini_api_key()
            
            prompt_chung = f"""
            BẠN LÀ TRỢ LÝ AI CHUYÊN PHÂN TÍCH, TỔNG HỢP VÀ DỊCH TÀI LIỆU GIÁO DỤC.
            Nhiệm vụ: {tac_vu} {'sang ' + ngon_ngu_dich if 'Dịch' in tac_vu else ''}.
            YÊU CẦU: Trình bày rõ ràng, mạch lạc, phân đoạn logic chuẩn sư phạm.
            """

            # ---------------------------------------------------------
            # NHÁNH 1: YOUTUBE (Kèm cơ chế Dự phòng)
            # ---------------------------------------------------------
            if nguon_video == "Đường dẫn YouTube (URL)":
                with st.spinner("🤖 Đang kết nối YouTube..."):
                    raw_text, err_msg, can_fallback = get_youtube_transcript_new(yt_url)
                    
                    if raw_text:
                        # 1A. Có Transcript -> Dùng AI Engine chính
                        if ai_engine:
                            try:
                                # Không hardcode [:20000] nữa, gửi toàn bộ text cho AI Engine phân mảnh/tự xử lý
                                prompt_full = prompt_chung + f"\n\nDỮ LIỆU LỜI THOẠI TRÍCH XUẤT:\n{raw_text}"
                                st.session_state["vproc_result"] = ai_engine.generate_text(prompt_full)
                                st.success("🎉 Xử lý qua Phụ đề YouTube thành công!")
                            except Exception as e:
                                st.error(f"❌ Lỗi AI Engine: {str(e)}")
                        else:
                            st.error("❌ Không thể gọi AI (Chưa khởi tạo AI Engine).")
                            
                    elif can_fallback:
                        # 1B. Không có Transcript -> Kích hoạt Fallback tải âm thanh
                        st.warning(f"{err_msg}\n\n🔄 Đang kích hoạt phương án dự phòng: Tự động tải âm thanh và nghe trực tiếp (Speech-to-Text)...")
                        
                        if not gemini_key:
                            st.error("❌ Tính năng nghe âm thanh dự phòng yêu cầu API Key của Gemini. Vui lòng đăng nhập bằng API Key bắt đầu với 'AIza...'.")
                        else:
                            with st.spinner("📥 Đang tải luồng âm thanh từ YouTube..."):
                                audio_path, dl_err = download_youtube_audio_fallback(yt_url)
                                
                            if audio_path:
                                # Đẩy file âm thanh cho Gemini Multimodal
                                res = process_multimodal_gemini(audio_path, prompt_chung + "\nHãy dựa vào nội dung âm thanh đính kèm.", gemini_key)
                                st.session_state["vproc_result"] = res
                                st.success("🎉 Xử lý thành công bằng phương án dự phòng (Nghe trực tiếp)!")
                                if os.path.exists(audio_path):
                                    os.remove(audio_path) # Dọn dẹp
                            else:
                                st.error(f"❌ Tải âm thanh dự phòng thất bại: {dl_err}")
                    else:
                        # 1C. Lỗi nghiêm trọng (Mạng, tuổi, chặn máy chủ)
                        st.error(err_msg)

            # ---------------------------------------------------------
            # NHÁNH 2: XỬ LÝ FILE TẢI LÊN 
            # ---------------------------------------------------------
            else:
                if not gemini_key:
                    st.error("❌ Tính năng Phân tích File yêu cầu API Key Gemini (Bắt đầu bằng 'AIza...').")
                else:
                    with st.spinner("🤖 Đang chuẩn bị tệp tin đa phương tiện..."):
                        # Lưu file tạm ra đĩa để đẩy lên Google
                        file_ext = os.path.splitext(uploaded_video.name)[1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                            tmp.write(uploaded_video.read())
                            tmp_path = tmp.name
                            
                        res = process_multimodal_gemini(tmp_path, prompt_chung + "\nHãy dựa vào tệp đa phương tiện đính kèm.", gemini_key)
                        st.session_state["vproc_result"] = res
                        st.success("🎉 AI đã phân tích tệp tin thành công!")
                        
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

        # ---------------------------------------------------------
        # HIỂN THỊ KẾT QUẢ TỪ STATE CHUẨN
        # ---------------------------------------------------------
        if st.session_state["vproc_result"]:
            st.text_area("Văn bản kết xuất:", value=st.session_state["vproc_result"], height=450)
            st.download_button(
                "📥 Tải xuống kết quả (.txt)",
                data=st.session_state["vproc_result"],
                file_name="Ket_qua_xu_ly_Video.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("💡 Tính năng đã được nâng cấp! Hệ thống tự động kích hoạt Nghe thông minh (Speech-to-Text) nếu video YouTube không có sẵn phụ đề.")
