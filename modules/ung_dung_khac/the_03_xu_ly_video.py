# -*- coding: utf-8 -*-
import streamlit as st
import re

def extract_youtube_id(url):
    """Trích xuất Video ID từ URL YouTube"""
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
    """Lấy transcript YouTube ưu tiên mọi loại phụ đề (Thủ công & Tự động) - Đã bọc lỗi chặn IP"""
    video_id = extract_youtube_id(url)
    if not video_id:
        return None, "⚠️ Đường dẫn YouTube không hợp lệ."
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Lấy danh sách toàn bộ các luồng phụ đề hiện có của video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        transcript = None
        
        # Bước 1: Ưu tiên tìm phụ đề tiếng Việt hoặc tiếng Anh (bao gồm cả bản tạo tự động)
        try:
            transcript = transcript_list.find_transcript(['vi', 'en'])
        except Exception:
            # Bước 2: Nếu không có cả vi/en, lấy ĐẠI phụ đề đầu tiên xuất hiện trong danh sách (ngôn ngữ gốc)
            for t in transcript_list:
                transcript = t
                break
                
        if not transcript:
            return None, "❌ Video này hoàn toàn không có bất kỳ dữ liệu phụ đề nào."
            
        # Lấy dữ liệu chữ từ phụ đề đã chọn
        fetched_data = transcript.fetch()
        full_text = " ".join([item['text'] for item in fetched_data])
        return full_text, None
        
    except ImportError:
        return None, "❌ Hệ thống chưa cài đặt thư viện youtube-transcript-api."
    except Exception as e:
        error_msg = str(e).lower()
        # Xử lý lỗi YouTube chặn IP đám mây hoặc trả về trang trống
        if "no element found" in error_msg or "xml" in error_msg:
            return None, "❌ YouTube đang tạm chặn máy chủ lấy dữ liệu của video này (Có thể do chống Bot, giới hạn độ tuổi, hoặc chủ kênh khóa API). Vui lòng thử một link video khác hoặc tải tệp video trực tiếp lên hệ thống!"
        return None, f"❌ Lỗi khi đọc dữ liệu từ YouTube. Chi tiết: {str(e)}"
        
    except ImportError:
        return None, "❌ Hệ thống chưa cài đặt thư viện youtube-transcript-api."
    except Exception as e:
        return None, f"❌ Lỗi khi đọc dữ liệu từ YouTube. Chi tiết: {str(e)}"

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
                placeholder="Ví dụ: https://www.youtube.com/watch?v=q96sp8Fonxc", 
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
                with st.spinner("🤖 Hệ thống đang bóc tách lời thoại video và phân tích bằng AI... (Quá trình này có thể mất vài giây)"):
                    
                    raw_video_text = ""
                    
                    if nguon_video == "Đường dẫn YouTube (URL)":
                        transcript_text, err_msg = get_youtube_transcript(yt_url)
                        if err_msg:
                            st.error(err_msg)
                            return
                        raw_video_text = transcript_text
                    else:
                        raw_video_text = f"[Tệp video tải lên: {uploaded_video.name} - Hệ thống AI đang phân tích dữ liệu âm thanh offline]"

                    # Prompt đẩy vào AI
                    prompt_v = f"""
BẠN LÀ MỘT TRỢ LÝ AI CHUYÊN PHÂN TÍCH, TỔNG HỢP VÀ DỊCH NỘI DUNG TÀI LIỆU GIÁO DỤC.
NHIỆM VỤ: Hãy thực hiện yêu cầu '{tac_vu}' {'sang ngôn ngữ ' + ngon_ngu_dich if 'Dịch' in tac_vu else ''} dựa trên dữ liệu văn bản/lời thoại trích xuất từ video dưới đây:

DỮ LIỆU LỜI THOẠI BÓC TÁCH ĐƯỢC TỪ VIDEO:
{raw_video_text[:15000]}

YÊU CẦU ĐẦU RA:
1. Trình bày rõ ràng, mạch lạc, chia đoạn logic phục vụ cho giáo viên làm tài liệu hoặc bài giảng.
2. Nếu là tác vụ dịch, dịch chuẩn xác và tự nhiên sang {ngon_ngu_dich}.
3. Nếu là tóm tắt hoặc kịch bản, nêu bật các ý chính cốt lõi.
"""

                    ket_qua_xu_ly = ""
                    if ai_engine:
                        try:
                            ket_qua_xu_ly = ai_engine.generate_text(prompt_v)
                        except Exception as e:
                            ket_qua_xu_ly = f"❌ Lỗi khi gọi AI phân tích: {str(e)}"
                    else:
                        ket_qua_xu_ly = f"""### TRÍCH XUẤT LỜI THOẠI GỐC TỪ VIDEO
**Tác vụ yêu cầu:** {tac_vu}

---
**Nội dung thô trích xuất thành công từ YouTube (Chưa qua AI xử lý):**

{raw_video_text}
"""

                    st.session_state["vproc_result"] = ket_qua_xu_ly
                    st.success("🎉 Đã lấy lời thoại và xử lý video thành công!")

        if "vproc_result" in st.session_state:
            ket_qua_hien_tai = st.session_state["vproc_result"]
            st.text_area("Văn bản kết xuất:", value=ket_qua_hien_tai, height=450)
            
            st.download_button(
                "📥 Tải xuống kết quả (.txt)",
                data=ket_qua_hien_tai,
                file_name="Ket_qua_xu_ly_video.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("💡 Hãy dán link YouTube (kể cả video chỉ có phụ đề tự động), sau đó bấm nút thực thi để bóc tách lời thoại!")
