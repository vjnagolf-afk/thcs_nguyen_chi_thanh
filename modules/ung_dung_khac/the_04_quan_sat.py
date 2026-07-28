# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ung_dung_khac/the_04_quan_sat.py
Nhiệm vụ: Trợ lý Phân tích Đa phương thức (Ảnh/Video Màn hình & Giọng nói).
Giao diện: Lấy cảm hứng từ Dashboard Recorder.
============================================================
"""

import streamlit as st
import tempfile
import os
import time

def render_the_04(ai_engine=None):
    st.markdown("### 👁️‍🗨️ Studio Phân Tích Màn Hình & Giọng Nói (AI Vision)")
    st.caption("Cung cấp hình ảnh/video quay màn hình và ghi âm lệnh của thầy. AI sẽ kết hợp đa phương thức để phân tích vấn đề.")

    # ==========================================
    # GIAO DIỆN BẢNG ĐIỀU KHIỂN (Giống Camtasia)
    # ==========================================
    st.markdown("#### 🎛️ Bảng điều khiển Đầu vào (Inputs)")
    
    # Tạo 3 cột giống giao diện Camtasia
    col_screen, col_mic, col_sys = st.columns(3)
    
    with col_screen:
        st.info("🖥️ **Màn hình (Screen/Video)**")
        use_screen = st.toggle("Kích hoạt tải Màn hình", value=True, key="tgl_screen")
        
    with col_mic:
        st.info("🎙️ **Microphone (Voice)**")
        use_mic = st.toggle("Kích hoạt Micro bên ngoài", value=True, key="tgl_mic")
        
    with col_sys:
        st.info("🔊 **System Audio**")
        st.toggle("Âm thanh máy tính", value=False, disabled=True, help="Web Browser hiện chưa hỗ trợ thu trực tiếp System Audio. Vui lòng quay video có sẵn âm thanh hệ thống để tải lên ô Màn hình.")

    st.markdown("---")

    # ==========================================
    # KHU VỰC THU THẬP DỮ LIỆU DỰA TRÊN TOGGLES
    # ==========================================
    uploaded_media = None
    recorded_audio = None
    text_prompt = ""

    c_left, c_right = st.columns([1.2, 1], gap="large")

    with c_left:
        if use_screen:
            st.markdown("**1. Hình ảnh / Video Màn hình**")
            st.caption("Dán ảnh (Ctrl+V) hoặc tải lên Video quay màn hình (MP4, MOV).")
            uploaded_media = st.file_uploader(
                "Tải lên Ảnh/Video màn hình", 
                type=["png", "jpg", "jpeg", "mp4", "mov", "webm", "avi"],
                label_visibility="collapsed",
                key="the4_media"
            )
            
            if uploaded_media:
                file_ext = os.path.splitext(uploaded_media.name)[1].lower()
                if file_ext in [".png", ".jpg", ".jpeg"]:
                    st.image(uploaded_media, caption="Ảnh màn hình đã nhận", use_column_width=True)
                else:
                    st.video(uploaded_media)

        if use_mic:
            st.markdown("**2. Ghi âm lệnh (Microphone)**")
            recorded_audio = st.audio_input("Ghi âm giọng nói của thầy:", key="the4_mic_input")

        st.markdown("**3. Lệnh văn bản bổ sung**")
        text_prompt = st.text_area("Nhập câu hỏi (Ví dụ: Lỗi ở dòng code nào?):", height=68)

        btn_analyze = st.button("🔴 BẮT ĐẦU PHÂN TÍCH (REC)", type="primary", use_container_width=True)

    # ==========================================
    # KHU VỰC XỬ LÝ VÀ HIỂN THỊ KẾT QUẢ AI
    # ==========================================
    with c_right:
        st.markdown("#### 🧠 Trợ lý AI Phản hồi")
        
        if btn_analyze:
            if not uploaded_media and not text_prompt.strip() and not recorded_audio:
                st.warning("⚠️ Vui lòng cung cấp ít nhất một dữ liệu (Màn hình, Giọng nói hoặc Văn bản).")
                st.stop()
                
            api_key = None
            if st.session_state.get("user_api_key"):
                api_key = st.session_state["user_api_key"]
            elif "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]

            if not api_key:
                st.error("❌ Hệ thống chưa tìm thấy API Key của Google Gemini ở thanh Sidebar.")
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
                        master_prompt += "\nTôi có gửi kèm một đoạn ghi âm giọng nói (Microphone). Hãy nghe và thực hiện theo yêu cầu trong đó."
                        
                    contents.append(master_prompt)
                    
                    # Xử lý File Ghi âm (Mic)
                    uploaded_audio_file = None
                    if recorded_audio:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                            tmp_audio.write(recorded_audio.read())
                            tmp_audio_path = tmp_audio.name
                        uploaded_audio_file = genai.upload_file(path=tmp_audio_path)
                        contents.append(uploaded_audio_file)

                    # Xử lý Ảnh/Video Màn hình
                    uploaded_vision_file = None
                    if uploaded_media:
                        ext = os.path.splitext(uploaded_media.name)[1].lower()
                        if ext in [".png", ".jpg", ".jpeg"]:
                            from PIL import Image
                            img = Image.open(uploaded_media)
                            contents.append(img)
                        else:
                            # Nếu là Video, đẩy lên Gemini
                            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_vid:
                                tmp_vid.write(uploaded_media.read())
                                tmp_vid_path = tmp_vid.name
                                
                            status_txt = st.empty()
                            status_txt.info("⏳ Đang tải Video màn hình lên máy chủ AI...")
                            uploaded_vision_file = genai.upload_file(path=tmp_vid_path)
                            
                            while uploaded_vision_file.state.name == "PROCESSING":
                                time.sleep(2)
                                uploaded_vision_file = genai.get_file(uploaded_vision_file.name)
                            status_txt.empty()
                            
                            contents.append(uploaded_vision_file)
                    
                    # Gọi AI sinh kết quả
                    response = model.generate_content(contents)
                    
                    st.success("🎉 Hoàn tất phân tích!")
                    st.session_state["the4_result"] = response.text
                    
                except Exception as e:
                    st.error(f"❌ Lỗi xử lý Đa phương thức: {e}")
                finally:
                    # Dọn dẹp Rác (Files tạm)
                    if 'uploaded_audio_file' in locals() and uploaded_audio_file:
                        try: genai.delete_file(uploaded_audio_file.name)
                        except: pass
                    if 'uploaded_vision_file' in locals() and uploaded_vision_file:
                        try: genai.delete_file(uploaded_vision_file.name)
                        except: pass
                    if 'tmp_audio_path' in locals() and os.path.exists(tmp_audio_path):
                        os.remove(tmp_audio_path)
                    if 'tmp_vid_path' in locals() and os.path.exists(tmp_vid_path):
                        os.remove(tmp_vid_path)

        # Hiển thị
        if st.session_state.get("the4_result"):
            with st.container(border=True):
                st.markdown(st.session_state["the4_result"])
