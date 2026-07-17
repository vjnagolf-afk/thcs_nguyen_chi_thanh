import streamlit as st
from gtts import gTTS
import io

def render_xd_sinh_video(ai_engine):
    st.markdown("### 🎬 Trợ lý Sinh Kịch bản & Khung Video Bài giảng")
    st.info("💡 Hệ thống tự động tạo Kịch bản chi tiết (Hình ảnh + Lời đọc) và sinh trực tiếp **Giọng đọc AI (Voiceover)** để giáo viên ghép vào video.")

    # Khởi tạo session state
    if "video_script" not in st.session_state:
        st.session_state.video_script = ""
    if "video_audio_text" not in st.session_state:
        st.session_state.video_audio_text = ""

    col1, col2 = st.columns([2, 1])
    with col1:
        chu_de = st.text_input(
            "Chủ đề hoặc nội dung cần làm Video:", 
            placeholder="Ví dụ: Hiện tượng Nhật thực, hoặc tóm tắt tiểu sử Hồ Chí Minh..."
        )
    with col2:
        thoi_luong = st.selectbox("Thời lượng dự kiến:", ["1 phút (Shorts/Reels)", "3 phút (Tóm tắt)", "5 phút (Chi tiết)"])

    yeu_cau_hinh_anh = st.text_input("Yêu cầu về hình ảnh (Tùy chọn):", placeholder="Ví dụ: Phong cách hoạt hình, 3D chân thực, sơ đồ tư duy...")

    st.markdown("---")

    if st.button("🚀 TIẾN HÀNH TẠO KỊCH BẢN & GIỌNG ĐỌC AI", type="primary"):
        if chu_de.strip():
            with st.spinner("⏳ AI đang viết kịch bản và thu âm giọng đọc... (có thể mất 10-15 giây)"):
                # Lệnh 1: Tạo kịch bản chi tiết
                prompt_script = f"""Đóng vai là một đạo diễn và chuyên gia giáo dục. Hãy viết kịch bản cho một video bài giảng thời lượng {thoi_luong} về chủ đề: '{chu_de}'.
                Yêu cầu hình ảnh: {yeu_cau_hinh_anh if yeu_cau_hinh_anh else 'Phù hợp với môi trường sư phạm'}.
                
                Trình bày theo dạng bảng Markdown với 3 cột:
                | Cảnh số | Mô tả Hình ảnh (Visual/Prompt) | Lời đọc thuyết minh (Voiceover/Audio) |
                
                Sau bảng, hãy tóm tắt lại TOÀN BỘ Lời đọc thuyết minh thành 1 đoạn văn liền mạch để tôi dùng làm kịch bản thu âm."""
                
                try:
                    # Gọi AI tạo kịch bản
                    script_res = ai_engine.generate_text(prompt_script)
                    st.session_state.video_script = script_res
                    
                    # Lệnh 2: Tạo một đoạn văn bản ngắn, thuần chữ để đưa vào máy đọc (tránh AI đọc cả các ký tự đặc biệt)
                    prompt_audio = f"Dựa vào chủ đề '{chu_de}', hãy viết ĐÚNG 1 đoạn văn (khoảng 150-200 chữ) dùng làm lời thuyết minh video. Viết tự nhiên, truyền cảm, KHÔNG dùng các ký tự đặc biệt, gạch đầu dòng hay bảng biểu."
                    audio_res = ai_engine.generate_text(prompt_audio)
                    st.session_state.video_audio_text = audio_res
                    
                except Exception as e:
                    st.error(f"Lỗi khi gọi AI: {e}")
        else:
            st.warning("⚠️ Vui lòng nhập chủ đề cần làm video!")

    # HIỂN THỊ KẾT QUẢ NGAY TRÊN GIAO DIỆN
    if st.session_state.video_script:
        st.markdown("### 📝 1. Kịch bản Video chi tiết")
        st.markdown(st.session_state.video_script)
        
        st.markdown("---")
        st.markdown("### 🎧 2. Giọng đọc AI (Voiceover tự động)")
        st.success("Tệp âm thanh dưới đây được tạo hoàn toàn tự động từ kịch bản. Thầy có thể bấm nút ba chấm (⋮) ở góc phải trình phát để tải về làm video ghép!")
        
        try:
            # Dùng gTTS để biến văn bản thành giọng nói thật và xuất ra giao diện
            tts = gTTS(text=st.session_state.video_audio_text, lang='vi', slow=False)
            bio = io.BytesIO()
            tts.write_to_fp(bio)
            st.audio(bio.getvalue(), format='audio/mp3')
        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi tạo âm thanh: {e}")
            
        st.markdown("---")
        st.markdown("### 🎞️ 3. Khung phát Video (Trình chiếu)")
        st.info("💡 Để sinh video người ảo (AI Avatar) trực tiếp, cần tích hợp API trả phí (HeyGen/D-ID). Dưới đây là khung phát video mẫu sẵn sàng để giáo viên upload video thành phẩm.")
        
        # Khung phát Video (Mô phỏng 1 video có sẵn)
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")
