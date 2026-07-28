# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ung_dung_khac/the_03_xu_ly_video.py
Nhiệm vụ: Trích xuất, Chuyển văn bản & Dịch Video (YouTube & Tải lên).
Chức năng: Lấy kịch bản, chuyển lời thoại thành văn bản, dịch nội dung 
và phân tích đa phương tiện bằng AI.
============================================================
"""

import streamlit as st
import re
import tempfile
import os
import time
import glob
import logging

logger = logging.getLogger(__name__)

# =========================================================
# KHỞI TẠO STATE
# =========================================================
def init_state():
    if "vproc_result" not in st.session_state:
        st.session_state["vproc_result"] = None

# =========================================================
# HÀM XỬ LÝ YOUTUBE
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
    video_id = extract_youtube_id(url)
    if not video_id: 
        return None, "⚠️ Đường dẫn YouTube không hợp lệ.", False
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        
        try:
            fetched_transcript = ytt_api.fetch(video_id, languages=["vi", "en"])
        except Exception:
            transcript_list = ytt_api.list(video_id)
            fetched_transcript = next(iter(transcript_list)).fetch()
            
        text_parts = []
        for item in fetched_transcript:
            if isinstance(item, dict) and 'text' in item:
                text_parts.append(item['text'])
            elif hasattr(item, 'text'):
                text_parts.append(item.text)
                
        full_text = " ".join(text_parts)
        return full_text, None, False
        
    except ImportError:
        return None, "❌ Thư viện 'youtube-transcript-api' chưa được cài đặt.", False
    except Exception as e:
        error_msg = str(e).lower()
        if "age restricted" in error_msg or "login" in error_msg:
            return None, "🔒 Video bị giới hạn quyền truy cập (giới hạn độ tuổi/riêng tư).", False
        else:
            return None, f"⚠️ Không lấy được phụ đề chữ từ YouTube.", True

# =========================================================
# HÀM DỰ PHÒNG: TẢI ÂM THANH
# =========================================================
def download_youtube_audio_fallback(url):
    try:
        import yt_dlp
    except ImportError:
        return None, "⚠️ Không thể chạy tính năng dự phòng vì thiếu thư viện 'yt-dlp'."

    temp_dir = tempfile.gettempdir()
    out_tmpl = os.path.join(temp_dir, 'yt_audio_%(id)s.%(ext)s')
    
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': out_tmpl,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            search_pattern = os.path.join(temp_dir, f"yt_audio_{info['id']}.*")
            found_files = glob.glob(search_pattern)
            
            if found_files:
                return found_files[0], None
            return None, "❌ Lỗi: Không tìm thấy file âm thanh trên hệ thống sau khi tải."
    except Exception as e:
        return None, f"❌ Không thể tải âm thanh dự phòng: {str(e)}"

# =========================================================
# HÀM XỬ LÝ ĐA PHƠNG TIỆN GEMINI (ĐÃ NÂNG CẤP TÌM API KEY)
# =========================================================
def get_gemini_api_key(ai_engine=None):
    # 1. Kiểm tra từ session_state (do người dùng nhập ở sidebar)
    key = st.session_state.get("user_api_key")
    if key and not key.startswith("sk-"): 
        return key
        
    # 2. Kiểm tra biến môi trường hệ thống
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key
        
    # 3. Kiểm tra trong st.secrets an toàn
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass 
        
    # 4. Kiểm tra xem ai_engine có lưu trữ khóa API bên trong không
    if ai_engine:
        for attr in ["api_key", "key", "_api_key"]:
            if hasattr(ai_engine, attr):
                val = getattr(ai_engine, attr)
                if val:
                    return val

    return None

def show_missing_key_warning():
    st.error("""
    ❌ **Hệ thống chưa tìm thấy mã API Key của Google Gemini!**
    
    Để AI có thể tự động "nghe" video dự phòng hoặc xử lý File tải lên, thầy cần cung cấp mã khóa API.
    
    💡 **CÁCH XỬ LÝ NHANH NHẤT:**
    1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey) để lấy 1 mã Key.
    2. Điền vào ô nhập API Key ở cột bên trái Sidebar để hệ thống ghi nhận.
    """)

def process_multimodal_gemini(file_path, prompt, api_key):
    try:
        import google.generativeai as genai
    except ImportError:
        return "❌ Máy chủ chưa cài đặt thư viện 'google-generativeai'."

    genai.configure(api_key=api_key)
    
    try:
        model_name = st.secrets.get("GEMINI_VIDEO_MODEL", "gemini-2.5-flash")
    except Exception:
        model_name = "gemini-2.5-flash"
        
    media_file = None
    try:
        status_text = st.empty()
        status_text.info(f"⏳ Đang tải luồng âm thanh lên AI ({model_name})...")
        media_file = genai.upload_file(path=file_path)
        
        status_text.info("🧠 AI đang 'nghe' toàn bộ video. Vui lòng đợi...")
        while media_file.state.name == "PROCESSING":
            time.sleep(3)
            media_file = genai.get_file(media_file.name)
            
        if media_file.state.name == "FAILED":
            raise Exception("Google AI từ chối xử lý tệp này.")
            
        status_text.info("✍️ AI đã nghe xong, đang tổng hợp và viết kịch bản...")
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content([prompt, media_file])
        
        status_text.empty()
        return response.text
        
    except Exception as e:
        return f"❌ Lỗi xử lý Đa phương tiện AI: {str(e)}"
    
    finally:
        if media_file:
            try:
                genai.delete_file(media_file.name)
            except Exception:
                pass

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
            yt_url = st.text_input("Nhập URL YouTube", placeholder="Ví dụ: https://youtu.be/...", key="vproc_yt_url")
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
            if nguon_video == "Đường dẫn YouTube (URL)" and not yt_url.strip():
                st.warning("⚠️ Vui lòng nhập đường dẫn URL YouTube.")
                st.stop()
            elif nguon_video != "Đường dẫn YouTube (URL)":
                if not uploaded_video:
                    st.warning("⚠️ Vui lòng tải lên một tệp.")
                    st.stop()
                if uploaded_video.size > 200 * 1024 * 1024:
                    st.error("❌ Tệp vượt quá giới hạn 200MB. Vui lòng thử tệp nhẹ hơn.")
                    st.stop()

            # Lấy API Key có truyền vào ai_engine để kiểm tra linh hoạt
            gemini_key = get_gemini_api_key(ai_engine)
            
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
                        if ai_engine:
                            try:
                                prompt_full = prompt_chung + f"\n\nDỮ LIỆU LỜI THOẠI TRÍCH XUẤT:\n{raw_text}"
                                res_text = ai_engine.generate_text(prompt_full)
                                
                                if res_text and str(res_text).startswith("❌"):
                                    st.error(res_text)
                                else:
                                    st.session_state["vproc_result"] = res_text
                                    st.success("🎉 Đã lấy lời thoại có sẵn trên YouTube thành công!")
                            except Exception as e:
                                st.error(f"❌ Lỗi AI Engine: {str(e)}")
                        else:
                            st.error("❌ Không thể gọi AI (Chưa khởi tạo AI Engine).")
                            
                    elif can_fallback:
                        st.warning(f"{err_msg}\n\n🔄 Đang kích hoạt AI tự động nghe video (Speech-to-Text)...")
                        
                        if not gemini_key:
                            show_missing_key_warning()
                        else:
                            with st.spinner("📥 Đang tải luồng âm thanh từ YouTube..."):
                                audio_path, dl_err = download_youtube_audio_fallback(yt_url)
                                
                            if audio_path:
                                res = process_multimodal_gemini(audio_path, prompt_chung + "\nHãy lắng nghe nội dung âm thanh đính kèm.", gemini_key)
                                
                                if res and str(res).startswith("❌"):
                                    st.error(res)
                                else:
                                    st.session_state["vproc_result"] = res
                                    st.success("🎉 Quá trình AI nghe trực tiếp video đã thành công!")
                                
                                if os.path.exists(audio_path):
                                    os.remove(audio_path)
                            else:
                                st.error(dl_err)
                    else:
                        st.error(err_msg)

            # ---------------------------------------------------------
            # NHÁNH 2: XỬ LÝ FILE TẢI LÊN
            # ---------------------------------------------------------
            else:
                if not gemini_key:
                    show_missing_key_warning()
                else:
                    with st.spinner("🤖 Đang chuẩn bị tệp tin đa phương tiện..."):
                        file_ext = os.path.splitext(uploaded_video.name)[1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                            tmp.write(uploaded_video.read())
                            tmp_path = tmp.name
                            
                        res = process_multimodal_gemini(tmp_path, prompt_chung + "\nHãy phân tích dựa vào tệp đa phương tiện đính kèm.", gemini_key)
                        
                        if res and str(res).startswith("❌"):
                            st.error(res)
                        else:
                            st.session_state["vproc_result"] = res
                            st.success("🎉 AI đã nghe/xem tệp tin thành công!")
                        
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

        # ---------------------------------------------------------
        # HIỂN THỊ KẾT QUẢ
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
            st.info("💡 Tính năng đã sẵn sàng! Đã cập nhật chế độ nhận diện File Âm thanh/Video thông minh.")
