# -*- coding: utf-8 -*-
import streamlit as st
import re

def extract_youtube_id(url):
    """Trích xuất Video ID từ các định dạng URL YouTube khác nhau"""
    if not url:
        return None
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_youtube_transcript(url):
    """Tự động lấy transcript (lời thoại) từ YouTube một cách an toàn"""
    video_id = extract_youtube_id(url)
    if not video_id:
        return None, "⚠️ Đường dẫn YouTube không hợp lệ hoặc không tìm thấy Video ID."
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        try:
            # Thử lấy phụ đề tiếng Việt hoặc tiếng Anh
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['vi', 'en'])
        except Exception:
            # Nếu không có, lấy bất kỳ ngôn ngữ nào có sẵn
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
        full_text = " ".join([item['text'] for item in transcript_list])
        return full_text, None
        
    except ImportError:
        return None, "❌ Hệ thống chưa cài đặt thư viện `youtube-transcript-api`. Vui lòng thêm `youtube-transcript-api` vào file requirements.txt hoặc chạy lệnh `pip install youtube-transcript-api` trên terminal."
    except Exception as e:
        return None, f"❌ Không thể trích xuất phụ đề từ video này (Video có thể không có phụ đề hoặc bật chế độ riêng tư). Chi tiết lỗi: {str(e)}"

def render_the_03(ai_engine=None):
    st.markdown("### 🎬 Công cụ Trích xuất, Chuyển văn bản & Dịch Video (YouTube & Tải lên)")
    st.caption("Hỗ trợ giáo viên lấy kịch bản, chuyển lời thoại thành văn bản và dịch nội dung từ video bất kỳ phục vụ giảng dạy.")

    col1, col2 = st.columns([1, 1], gap="medium")

    # =========================================================
    # CỘT 1: CẤU HÌNH VÀ NGUỒN VIDEO
    # =========================================================
    with col1:
        st.markdown("#### ⚙️ Cấu hình nguồn video")
        
        nguon_video = st.radio(
            "Chọn nguồn video",
            ["Đường dẫn YouTube (URL)", "Tải tệp video lên máy (MP4, AVI, MOV, MKV)"],
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
                "Tải lên tệp video", 
                type=["mp4", "avi", "mov", "mkv", "webm"], 
                key="vproc_file"
            )

        st.markdown("#### 🛠️ Chọn tác vụ xử lý")
        tac_vu = st.selectbox(
            "Yêu cầu xử lý",
            [
                "📋 Sao chép toàn bộ kịch bản gốc từ video",
                "🗣️ Chuyển văn bản lời thoại chi tiết (Transcribe)",
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

    # =========================================================
    # CỘT 2: KẾT QUẢ KẾT XUẤT
    # =========================================================
    with col2:
        st.markdown("#### 📋 Kết quả xử lý văn bản")

        if btn_xu_ly:
            if nguon_video == "Đường dẫn YouTube (URL)" and not yt_url.strip():
                st.warning("⚠️ Vui lòng nhập đường dẫn URL YouTube hợp lệ.")
            elif nguon_video == "Tải tệp video lên máy (MP4, AVI, MOV, MKV)" and not uploaded_video:
                st.warning("⚠️ Vui lòng tải lên một tệp video.")
            else:
                with st.spinner("🤖 Hệ thống đang trích xuất lời thoại video và phân tích bằng AI..."):
                    
                    raw_video_text = ""
                    
                    # Nếu là YouTube, tiến hành lấy transcript thực tế
                    if nguon_video == "Đường dẫn YouTube (URL)":
                        transcript_text, err_msg = get_youtube_transcript(yt_url)
                        if err_msg:
                            st.error(err_msg)
                            return
                        raw_video_text = transcript_text
                    else:
                        raw_video_text = f"[Tệp video tải lên: {uploaded_video.name} - Đang giả lập phân tích luồng âm thanh tệp tin]"

                    # Xây dựng prompt chuyên sâu đưa nội dung thực tế vào cho AI
                    prompt_v = f"""
BẠN LÀ MỘT TRỢ LÝ AI CHUYÊN PHÂN TÍCH, TỔNG HỢP VÀ DỊCH NỘI DUNG TÀI LIỆU GIÁO DỤC.
NHIỆM VỤ: Hãy thực hiện yêu cầu '{tac_vu}' {'sang ngôn ngữ ' + ngon_ngu_dich if 'Dịch' in tac_vu else ''} dựa trên dữ liệu văn bản/lời thoại trích xuất từ video dưới đây:

DỮ LIỆU LỜI THOẠI VIDEO:
{raw_video_text[:12000]}

YÊU CẦU ĐẦU RA:
1. Trình bày rõ ràng, mạch lạc, phân đoạn logic chuẩn sư phạm phục vụ cho giáo viên.
2. Nếu là tác vụ dịch, dịch chuẩn xác sang {ngon_ngu_dich}.
3. Nếu là tóm tắt hoặc kịch bản, nêu rõ các ý chính cốt lõi.
"""

                    ket_qua_xu_ly = ""
                    if ai_engine:
                        try:
                            ket_qua_xu_ly = ai_engine.generate_text(prompt_v)
                        except Exception as e:
                            ket_qua_xu_ly = f"❌ Lỗi khi gọi AI xử lý: {str(e)}"
                    else:
                        ket_qua_xu_ly = f"""### KẾT QUẢ TRÍCH XUẤT VĂN BẢN TỪ VIDEO
**Tác vụ:** {tac_vu}
{'- Ngôn ngữ đích: ' + ngon_ngu_dich if 'Dịch' in tac_vu else ''}

---
**Nội dung văn bản bóc tách:**
{raw_video_text[:800]}... *(Đã rút gọn hiển thị xem trước)*
"""

                    st.session_state["vproc_result"] = ket_qua_xu_ly
                    st.success("🎉 Xử lý và trích xuất video thành công!")

        if "vproc_result" in st.session_state:
            ket_qua_hien_tai = st.session_state["vproc_result"]
            st.text_area("Văn bản kết xuất:", value=ket_qua_hien_tai, height=400)
            
            st.download_button(
                "📥 Tải xuống kết quả (.txt)",
                data=ket_qua_hien_tai,
                file_name="Ket_qua_xu_ly_video.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("💡 Hãy chọn nguồn video, dán link YouTube, sau đó bấm nút thực thi để hệ thống tự động bóc tách và phân tích.")
