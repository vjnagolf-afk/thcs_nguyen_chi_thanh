# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ung_dung_khac/the_04_quan_sat.py
Nhiệm vụ: Trợ lý Phân tích Màn hình & Giọng nói (Đa phương thức).
Chức năng: Nhận ảnh chụp màn hình + Ghi âm giọng nói để AI phân tích.
============================================================
"""

import streamlit as st
import tempfile
import os

def render_the_04(ai_engine=None):
    st.markdown("### 👁️‍🗨️ Trợ lý Phân tích Màn hình & Lệnh Giọng nói")
    st.caption("Chụp lại màn hình máy tính (bài toán, lỗi phần mềm, trang web...) và ghi âm yêu cầu của thầy. AI sẽ kết hợp cả hai để giải quyết vấn đề ngay lập tức.")

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown("#### 1️⃣ Cung cấp Màn hình / Hình ảnh")
        st.info("💡 **Mẹo:** Thầy có thể bấm `Windows + Shift + S` (hoặc `Cmd + Shift + 4`) để chụp màn hình, sau đó chọn ô bên dưới và bấm `Ctrl + V` để dán ảnh vào ngay lập tức!")
        
        uploaded_img = st.file_uploader(
            "Tải lên hoặc Dán ảnh chụp màn hình (PNG, JPG):", 
            type=["png", "jpg", "jpeg"],
            key="the4_img_upload"
        )
        
        if uploaded_img:
            st.image(uploaded_img, caption="Ảnh màn hình đã ghi nhận", use_column_width=True)

        st.markdown("#### 2️⃣ Ghi âm yêu cầu (Tùy chọn)")
        st.write("Sử dụng micro để nói yêu cầu thay vì gõ chữ (Ví dụ: 'Hãy giải thích cho tôi đoạn code trên màn hình này là gì?').")
        
        # Sử dụng tính năng st.audio_input mới nhất của Streamlit
        recorded_audio = st.audio_input("Bấm vào biểu tượng Micro để bắt đầu nói:", key="the4_audio")
        
        st.markdown("#### 3️⃣ Hoặc nhập yêu cầu bằng văn bản")
        text_prompt = st.text_area(
            "Nội dung yêu cầu:", 
            placeholder="Nếu đã ghi âm ở trên, thầy có thể bỏ trống ô này...",
            height=100
        )

        btn_analyze = st.button("🚀 GỬI TẤT CẢ CHO AI PHÂN TÍCH", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### 🧠 Kết quả từ Trợ lý AI")
        
        if btn_analyze:
            if not uploaded_img:
                st.warning("⚠️ Vui lòng cung cấp ít nhất một bức ảnh chụp màn hình.")
                st.stop()
                
            if not recorded_audio and not text_prompt.strip():
                st.warning("⚠️ Vui lòng ghi âm yêu cầu hoặc nhập yêu cầu bằng văn bản.")
                st.stop()
                
            # Lấy API Key từ hệ thống
            api_key = None
            if st.session_state.get("user_api_key"):
                api_key = st.session_state["user_api_key"]
            elif "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]

            if not api_key:
                st.error("❌ Hệ thống chưa tìm thấy API Key của Google Gemini ở thanh Sidebar.")
                st.stop()

            with st.spinner("🤖 Trợ lý AI đang quan sát màn hình và lắng nghe..."):
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.5-flash") # Dùng model hỗ trợ Multimodal
                    
                    # Chuẩn bị dữ liệu để gửi đi
                    contents = []
                    
                    # 1. Thêm prompt văn bản (nếu có)
                    master_prompt = "Dưới đây là một bức ảnh chụp màn hình. "
                    if text_prompt.strip():
                        master_prompt += f"Người dùng có yêu cầu văn bản như sau: '{text_prompt.strip()}'. "
                    
                    if recorded_audio:
                        master_prompt += "Đồng thời, người dùng có gửi kèm một đoạn ghi âm giọng nói yêu cầu. Hãy nghe kỹ đoạn ghi âm này kết hợp với ảnh màn hình để đưa ra câu trả lời chính xác nhất."
                    
                    contents.append(master_prompt)
                    
                    # 2. Thêm file ghi âm (nếu có) bằng API File Upload
                    uploaded_audio_file = None
                    if recorded_audio:
                        audio_ext = ".wav" # Định dạng mặc định của st.audio_input
                        with tempfile.NamedTemporaryFile(delete=False, suffix=audio_ext) as tmp_audio:
                            tmp_audio.write(recorded_audio.read())
                            tmp_audio_path = tmp_audio.name
                            
                        # Đẩy file âm thanh lên Gemini
                        uploaded_audio_file = genai.upload_file(path=tmp_audio_path)
                        contents.append(uploaded_audio_file)

                    # 3. Thêm hình ảnh (Sử dụng đối tượng dạng dictionary hoặc PIL)
                    from PIL import Image
                    img = Image.open(uploaded_img)
                    contents.append(img)
                    
                    # GỌI AI XỬ LÝ ĐỒNG THỜI 3 LUỒNG DỮ LIỆU
                    response = model.generate_content(contents)
                    
                    st.success("🎉 AI đã xử lý xong!")
                    
                    # Hiển thị kết quả
                    st.session_state["the4_result"] = response.text
                    
                except Exception as e:
                    st.error(f"❌ Lỗi xử lý Đa phương thức: {e}")
                finally:
                    # Dọn dẹp file âm thanh tạm trên máy chủ Google (nếu có)
                    if 'uploaded_audio_file' in locals() and uploaded_audio_file:
                        try:
                            genai.delete_file(uploaded_audio_file.name)
                        except:
                            pass
                    # Dọn dẹp file cục bộ
                    if 'tmp_audio_path' in locals() and os.path.exists(tmp_audio_path):
                        os.remove(tmp_audio_path)

        # Hiển thị kết quả lưu trong state
        if st.session_state.get("the4_result"):
            with st.container(border=True):
                st.markdown(st.session_state["the4_result"])
