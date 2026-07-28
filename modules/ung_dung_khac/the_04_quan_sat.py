# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ung_dung_khac/the_04_quan_sat.py
Nhiệm vụ: Trợ lý Phân tích Đa phương thức (Ảnh/Video Màn hình, Camera & Giọng nói).
Giao diện: Lấy cảm hứng từ Dashboard Recorder.
============================================================
"""

import streamlit as st
import tempfile
import os
import time

def get_clean_gemini_key(ai_engine=None):
    """Hàm tự động dọn dẹp và lấy API Key chuẩn của Google"""
    # 1. Lấy từ ô nhập liệu ở Sidebar
    key = st.session_state.get("user_api_key", "")
    if key and isinstance(key, str) and key.strip().startswith("AI"):
        return key.strip()
        
    # 2. Lấy từ bộ nhớ AI Engine (nếu có)
    if ai_engine:
        for attr in ["api_key", "key", "_api_key"]:
            if hasattr(ai_engine, attr):
                val = getattr(ai_engine, attr)
                if val and isinstance(val, str) and val.strip().startswith("AI"):
                    return val.strip()
                    
    # 3. Lấy từ thư mục bảo mật
    try:
        if "GEMINI_API_KEY" in st.secrets:
            sec_key = st.secrets["GEMINI_API_KEY"]
            if sec_key and isinstance(sec_key, str) and sec_key.strip().startswith("AI"):
                return sec_key.strip()
    except Exception:
        pass
        
    return None

def render_the_04(ai_engine=None):
    st.markdown("### 👁️‍🗨️ Studio Phân Tích Đa Phương Thức (AI Vision)")
    st.caption("Cung cấp hình ảnh/video quay màn hình, chụp camera và ghi âm. AI sẽ kết hợp tất cả để phân tích vấn đề một cách toàn diện nhất.")

    # Khởi tạo khóa (key) động để có thể Xóa/Reset khung ghi âm
    if "audio_key" not in st.session_state:
        st.session_state["audio_key"] = 0

    # ==========================================
    # GIAO DIỆN BẢNG ĐIỀU KHIỂN
    # ==========================================
    st.markdown("#### 🎛️ Bảng điều khiển Đầu vào (Inputs)")
    
    col_screen, col_cam, col_mic = st.columns(3)
    
    with col_screen:
        st.info("🖥️ **Màn hình (Screen/Video)**")
        use_screen = st.toggle("Tải File / Dán Ảnh", value=True, key="tgl_screen")
        
    with col_cam:
        st.info("📷 **Webcam (Camera)**")
        use_cam = st.toggle("Chụp ảnh trực tiếp", value=False, key="tgl_cam")
        
    with col_mic:
        st.info("🎙️ **Microphone / Ghi âm**")
        use_mic = st.toggle("Kích hoạt Ghi âm Web", value=True, key="tgl_mic")

    st.markdown("---")

    # ==========================================
    # KHU VỰC THU THẬP DỮ LIỆU
    # ==========================================
    uploaded_media = None
    captured_img = None
    recorded_audio = None
    text_prompt = ""

    c_left, c_right = st.columns([1.2, 1], gap="large")

    with c_left:
        # NHÁNH 1: FILE UPLOAD (MÀN HÌNH / ẢNH SẴN CÓ)
        if use_screen:
            st.markdown("**1A. Hình ảnh / Video Màn hình**")
            
            with st.expander("💡 HƯỚNG DẪN DÁN (CTRL+V) VÀ KÉO THẢ ĐÚNG CÁCH", expanded=False):
                st.write("""
                * **Để Dán (Ctrl+V):** Chụp màn hình (Win+Shift+S) -> **Click chuột trực tiếp vào biểu tượng Đám Mây** bên dưới để khung sáng lên -> Bấm `Ctrl+V`.
                * **Để Kéo Thả:** Chỉ nhận thao tác kéo một file vật lý từ **Thư mục máy tính (File Explorer)**. Không hỗ trợ kéo ảnh từ Web hay Word.
                * **Chắc chắn nhất:** Bấm nút **Browse files** (Tìm tệp) để chọn trực tiếp!
                """)
            
            uploaded_media = st.file_uploader(
                "Click vào đám mây & nhấn Ctrl+V để Dán:", 
                type=["png", "jpg", "jpeg", "mp4", "mov", "webm", "avi"],
                key="the4_media"
            )
            
            if uploaded_media:
                file_ext = os.path.splitext(uploaded_media.name)[1].lower()
                if file_ext in [".png", ".jpg", ".jpeg"]:
                    st.image(uploaded_media, caption="Ảnh tải lên đã nhận", use_column_width=True)
                else:
                    st.video(uploaded_media)

        # NHÁNH 2: CAMERA 
        if use_cam:
            st.markdown("**1B. Chụp ảnh từ Webcam**")
            st.caption("Thầy có thể giơ trực tiếp SGK, bài toán viết tay lên trước Camera.")
            captured_img = st.camera_input("Chụp ảnh:", key="the4_camera")

        # NHÁNH 3: MICROPHONE GHI ÂM
        if use_mic:
            st.markdown("**2. Ghi âm lệnh (Trên Trình Duyệt)**")
            
            audio_widget_key = f"the4_mic_input_{st.session_state['audio_key']}"
            recorded_audio = st.audio_input("Bấm biểu tượng Micro để ghi âm lệnh:", key=audio_widget_key)
            
            if recorded_audio:
                st.success("✅ Đã ghi âm thành công!")
                col_dl, col_del = st.columns(2)
                
                with col_dl:
                    st.download_button(
                        label="📥 Tải file (.wav)",
                        data=recorded_audio.getvalue(),
                        file_name="Ghi_am_AI_Studio.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
                with col_del:
                    if st.button("🗑️ Xóa file ghi âm này", use_container_width=True):
                        st.session_state["audio_key"] += 1
                        st.rerun()

        # NHÁNH 4: VĂN BẢN
        st.markdown("**3. Lệnh văn bản bổ sung**")
        text_prompt = st.text_area("Nhập câu hỏi (Ví dụ: Hãy giải thích lỗi sai trong bức ảnh):", height=68)

        btn_analyze = st.button("🔴 BẮT ĐẦU PHÂN TÍCH CHO AI", type="primary", use_container_width=True)

    # ==========================================
    # KHU VỰC XỬ LÝ VÀ HIỂN THỊ KẾT QUẢ AI
    # ==========================================
    with c_right:
        st.markdown("#### 🧠 Trợ lý AI Phản hồi")
        
        if btn_analyze:
            has_visual = uploaded_media is not None or captured_img is not None
            if not has_visual and not text_prompt.strip() and not recorded_audio:
                st.warning("⚠️ Vui lòng cung cấp ít nhất một dữ liệu (Hình ảnh, Giọng nói hoặc Văn bản).")
                st.stop()
                
            api_key = get_clean_gemini_key(ai_engine)

            if not api_key:
                st.error("❌ Lỗi: Mã API Key không hợp lệ hoặc chưa được nhập. Mã chuẩn của Google Gemini phải bắt đầu bằng chữ 'AIza...'. Thầy vui lòng kiểm tra lại ở thanh Sidebar!")
                st.stop()

            with st.spinner("🤖 AI đang đồng bộ và phân tích dữ liệu đa phương thức..."):
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    contents = []
                    master_prompt = "Hãy đóng vai một chuyên gia, phân tích các dữ liệu tôi cung cấp. "
                    if text_prompt.strip():
                        master_prompt += f"\nYêu cầu bằng văn bản: '{text_prompt.strip()}'. "
                    if recorded_audio:
                        master_prompt += "\nTôi có gửi kèm một đoạn ghi âm. Hãy nghe và thực hiện theo yêu cầu trong đó."
                        
                    contents.append(master_prompt)
                    
                    # 1. Gửi File Âm thanh (Mic)
                    uploaded_audio_file = None
                    tmp_audio_path = None
                    if recorded_audio:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                            tmp_audio.write(recorded_audio.getvalue())
                            tmp_audio_path = tmp_audio.name
                        uploaded_audio_file = genai.upload_file(path=tmp_audio_path)
                        contents.append(uploaded_audio_file)

                    # 2. Gửi Ảnh từ Webcam
                    if captured_img:
                        from PIL import Image
                        img_cam = Image.open(captured_img)
                        contents.append(img_cam)

                    # 3. Gửi File Upload / Dán
                    uploaded_vision_file = None
                    tmp_vid_path = None
                    if uploaded_media:
                        ext = os.path.splitext(uploaded_media.name)[1].lower()
                        if ext in [".png", ".jpg", ".jpeg"]:
                            from PIL import Image
                            img_up = Image.open(uploaded_media)
                            contents.append(img_up)
                        else:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_vid:
                                tmp_vid.write(uploaded_media.getvalue())
                                tmp_vid_path = tmp_vid.name
                                
                            status_txt = st.empty()
                            status_txt.info("⏳ Đang tải Video lên máy chủ AI...")
                            uploaded_vision_file = genai.upload_file(path=tmp_vid_path)
                            
                            while uploaded_vision_file.state.name == "PROCESSING":
                                time.sleep(2)
                                uploaded_vision_file = genai.get_file(uploaded_vision_file.name)
                            status_txt.empty()
                            
                            contents.append(uploaded_vision_file)
                    
                    # 4. Yêu cầu AI sinh nội dung
                    response = model.generate_content(contents)
                    
                    st.success("🎉 Hoàn tất phân tích!")
                    st.session_state["the4_result"] = response.text
                    
                except Exception as e:
                    # Bắt và hiển thị lỗi rõ ràng hơn nếu vẫn bị lỗi
                    error_str = str(e)
                    if "API_KEY_INVALID" in error_str:
                        st.error("❌ Lỗi: Mã API Key bị Google từ chối (API_KEY_INVALID). Thầy hãy kiểm tra lại mã đã nhập ở Sidebar, đảm bảo sao chép chính xác từ Google AI Studio.")
                    else:
                        st.error(f"❌ Lỗi xử lý Đa phương thức: {error_str}")
                finally:
                    if 'uploaded_audio_file' in locals() and uploaded_audio_file:
                        try: genai.delete_file(uploaded_audio_file.name)
                        except: pass
                    if 'uploaded_vision_file' in locals() and uploaded_vision_file:
                        try: genai.delete_file(uploaded_vision_file.name)
                        except: pass
                    if tmp_audio_path and os.path.exists(tmp_audio_path):
                        os.remove(tmp_audio_path)
                    if tmp_vid_path and os.path.exists(tmp_vid_path):
                        os.remove(tmp_vid_path)

        if st.session_state.get("the4_result"):
            with st.container(border=True):
                st.markdown(st.session_state["the4_result"])
