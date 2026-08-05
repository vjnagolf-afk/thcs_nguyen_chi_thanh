# -*- coding: utf-8 -*-
"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_ca_nhan_hoa.py
PHIÊN BẢN TEST (RÚT GỌN CHỐNG SẬP MÁY CHỦ)
============================================================
"""

import io
import re
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Kết nối AI
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

def extract_text_from_file(uploaded_file):
    if not uploaded_file: return ""
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    try:
        if file_name.endswith('.docx'):
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
        elif file_name.endswith('.pdf'):
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            return "\n".join([page.get_text("text") for page in doc])
        else:
            return file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"Lỗi đọc file: {e}"

def render_xd_ca_nhan_hoa(ai_engine_cu=None):
    if "game_html" not in st.session_state:
        st.session_state.game_html = None

    st.markdown("### 🛠️ CHẾ ĐỘ TEST: Trợ lý Thiết kế Game (Bản an toàn)")
    st.warning("⚠️ Bản test này ĐÃ TẮT chức năng chạy thử Game trực tiếp trên web để chặn tuyệt đối lỗi sập máy chủ (GZip). Thầy cô chỉ dùng AI tạo code và tải file về máy.")

    with st.container(border=True):
        uploaded_file = st.file_uploader("1️⃣ Tải lên Giáo Án (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
        loai_tro_choi = st.selectbox("2️⃣ Chọn loại trò chơi:", ["Trắc nghiệm (Quiz)", "Nối cặp (Matching)"])
        btn_tao = st.button("🚀 TẠO GAME TEST NAY", type="primary", use_container_width=True)

    # Xử lý sinh code
    if btn_tao:
        if not uploaded_file:
            st.warning("⚠️ Vui lòng tải file giáo án lên.")
            return
        if AIEngine2 is None:
            st.error("❌ Chưa kết nối AI.")
            return

        with st.spinner("⏳ AI đang tạo mã nguồn HTML/CSS/JS (khoảng 15 giây)..."):
            noidung = extract_text_from_file(uploaded_file)
            prompt = f"""
            Bạn là lập trình viên EdTech. Dựa vào giáo án sau, tạo 1 file HTML5 Mini-game thể loại: {loai_tro_choi}.
            Gộp chung HTML, CSS, JS vào 1 file duy nhất. Giao diện đẹp, hiện đại.
            TUYỆT ĐỐI CHỈ TRẢ VỀ CODE, bọc trong ```html ... ```. Không giải thích.
            Nội dung giáo án: {noidung[:4000]}
            """
            try:
                engine = AIEngine2(default_model="gemini-2.5-flash")
                res = engine.generate_text(prompt, temperature=0.7)
                
                # Trích xuất code
                match = re.search(r'```html(.*?)```', res, re.DOTALL | re.IGNORECASE)
                st.session_state.game_html = match.group(1).strip() if match else res
                st.success("✅ AI đã lập trình xong!")
            except Exception as e:
                st.error(f"Lỗi AI: {e}")

    # Hiển thị nút tải
    if st.session_state.game_html:
        st.markdown("---")
        st.markdown("### 📥 TẢI GAME VỀ MÁY")
        st.download_button(
            label="💾 BẤM VÀO ĐÂY ĐỂ TẢI FILE GAME (.HTML)",
            data=st.session_state.game_html,
            file_name="Game_Test.html",
            mime="text/html",
            use_container_width=True
        )
        with st.expander("🔍 Xem trước mã nguồn code"):
            st.code(st.session_state.game_html, language="html")
