# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_ca_nhan_hoa.py
Nhiệm vụ: Trợ lý Chuyên gia Thiết kế Trò chơi Học tập (AI Edu-Game Architect).
Kiến trúc: Áp dụng Game Loop chuẩn và Ép buộc CSS Responsive.
============================================================
"""

import io
import re
import logging
import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# ============================================================
# UTILS: ĐỌC DỮ LIỆU TỪ GIÁO ÁN
# ============================================================
def extract_text_from_file(uploaded_file):
    if not uploaded_file:
        return ""
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    extracted_text = ""
    try:
        if file_name.endswith('.docx'):
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            extracted_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
        elif file_name.endswith('.pdf'):
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_text = "\n".join([page.get_text("text") for page in doc])
        elif file_name.endswith(('.txt', '.md')):
            extracted_text = file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Lỗi đọc file giáo án: {e}")
    return extracted_text

# ============================================================
# MAIN COMPONENT: GIAO DIỆN TỔ CHỨC THIẾT KẾ
# ============================================================
def render_xd_ca_nhan_hoa(ai_engine=None):
    if "game_html" not in st.session_state:
        st.session_state.game_html = None
    if "game_name" not in st.session_state:
        st.session_state.game_name = "AI_Edu_Game"

    st.markdown("### 🎮 Chuyên gia Thiết kế Trò chơi Học tập AI")
    st.caption("Ứng dụng triết lý Gamification: Chuyển hóa tài liệu nhàm chán thành trải nghiệm tương tác cao.")

    with st.container(border=True):
        st.markdown("#### 📖 Bước 1: Nạp Tri thức (Giáo án/Tài liệu)")
        uploaded_file = st.file_uploader("Tải lên File Giáo Án (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"], help="AI sẽ tự động trích xuất các từ khóa, khái niệm và câu hỏi từ tài liệu này.")

        st.divider()
        
        st.markdown("#### 🕹️ Bước 2: Kịch bản Thiết kế (Game Design Document)")
        
        col1, col2 = st.columns(2)
        with col1:
            loai_tro_choi = st.selectbox(
                "Định dạng cơ chế trò chơi:",
                [
                    "🌟 Phân tích Tự động (Khuyên dùng)",
                    "✅ Quiz Trắc nghiệm (Đa lựa chọn)",
                    "🗂️ Nối cặp khái niệm (Matching)",
                    "📝 Điền khuyết (Fill in the blanks)",
                    "⚖️ Biện luận Đúng/Sai",
                    "🧠 Thẻ bài Ghi nhớ (Memory Match)"
                ],
                help="Chọn cơ chế tương tác phù hợp nhất với mục tiêu sư phạm của bài học."
            )
            
            so_luong = st.number_input("Số lượng thử thách (câu hỏi/cặp):", min_value=3, max_value=30, value=5)
            
        with col2:
            mau_chu_dao = st.selectbox(
                "Bảng màu (UI Theme):", 
                ["Xanh dương (Học thuật)", "Xanh ngọc (Thư giãn)", "Tím violet (Sáng tạo)", "Hồng rose (Năng động)", "Vàng hổ phách (Cảnh giác)"]
            )
            font_chu = st.selectbox(
                "Kiểu chữ (Typography):", 
                ["Nunito (Dễ thương, Tiểu học)", "Quicksand (Mềm mại, THCS)", "Inter (Hiện đại, THPT)", "Roboto (Tiêu chuẩn)"]
            )

        st.markdown("#### ⚙️ Bước 3: Tuỳ chỉnh Nâng cao (Tùy chọn)")
        ten_game = st.text_input("Tên trò chơi:", placeholder="Ví dụ: Chinh phục Vũ trụ Lịch sử lớp 9...")
        yeu_cau = st.text_area(
            "Luật chơi hoặc Yêu cầu đặc biệt bổ sung:", 
            placeholder="Ví dụ: Có đồng hồ đếm ngược 15s mỗi câu, thêm hiệu ứng pháo hoa khi kết thúc, dùng từ ngữ cổ vũ vui nhộn...", 
            height=68
        )

        col_ai, col_emoji = st.columns([1, 1])
        with col_ai:
            che_do_ai = st.radio("Bộ não Kiến trúc AI:", ["🎯 Tư duy Sâu (Gemini 2.5 Pro / GPT-4o)", "⚡ Phản xạ Nhanh (Gemini 2.5 Flash / GPT-4o-mini)"])
        with col_emoji:
            dung_emoji = st.checkbox("Sử dụng Emojis làm đồ họa minh họa", value=True)

        btn_tao_game = st.button("🚀 KHỞI TẠO & LẬP TRÌNH TRÒ CHƠI", type="primary", use_container_width=True)

    # ========================================================
    # XỬ LÝ LẬP TRÌNH GAME (AI ARCHITECT CORE)
    # ========================================================
    if btn_tao_game:
        if not uploaded_file:
            st.warning("⚠️ Chuyên gia cần tài liệu gốc để lên ý tưởng. Thầy vui lòng tải file lên nhé!")
            return

        with st.spinner("⏳ Đang thiết kế kiến trúc và ép kiểu CSS chống vỡ giao diện..."):
            noidung_giaosan = extract_text_from_file(uploaded_file)
            
            mau_css = {"Xanh dương": "#3B82F6", "Xanh ngọc": "#14B8A6", "Tím violet": "#8B5CF6", "Hồng rose": "#F43F5E", "Vàng hổ phách": "#F59E0B"}
            hex_color = mau_css.get(mau_chu_dao.split(" (")[0], "#3B82F6")
            font_family = font_chu.split(" (")[0]
            game_title = ten_game if ten_game.strip() else "Trải nghiệm Học tập Tương tác"

            luat_choi = ""
            if "Trắc nghiệm" in loai_tro_choi:
                luat_choi = "Cơ chế: Trắc nghiệm 4 đáp án. Chọn sai rung lắc, chọn đúng qua câu."
            elif "Nối cặp" in loai_tro_choi:
                luat_choi = "Cơ chế: Nối cặp (Matching). TUYỆT ĐỐI DÙNG CƠ CHẾ CLICK CHỌN 2 Ô, KHÔNG DÙNG DRAG & DROP."
            elif "Điền khuyết" in loai_tro_choi:
                luat_choi = "Cơ chế: Hiện câu có chỗ trống (___). Cung cấp các nút từ khóa bên dưới để click."
            elif "Đúng / Sai" in loai_tro_choi:
                luat_choi = "Cơ chế: Quẹt thẻ hoặc 2 nút Bấm Đúng/Sai khổng lồ."
            elif "Thẻ bài" in loai_tro_choi:
                luat_choi = "Cơ chế: Lật thẻ Memory Match dạng lưới (Grid)."
            else:
                luat_choi = "Bạn tự chọn cơ chế (Quiz hoặc Nối cặp) phù hợp nhất với dữ liệu."

            # SIÊU PROMPT BẮT BUỘC CSS RESPONSIVE & CHỐNG TRÀN CHỮ
            prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA THIẾT KẾ TRÒ CHƠI SƯ PHẠM VÀ KỸ SƯ FRONT-END BẬC THẦY.
Nhiệm vụ: Lập trình 1 Mini-Game Web hoàn chỉnh chỉ trong 1 file HTML duy nhất dựa vào giáo án.

--- 1. CỐT LÕI SƯ PHẠM ---
- Thể loại: {loai_tro_choi}. Cơ chế: {luat_choi}
- Số lượng: {so_luong} câu hỏi/cặp. Tên trò chơi: {game_title}
- Đồ họa Emoji: {'Có' if dung_emoji else 'Không'}

--- 2. BẮT BUỘC TUÂN THỦ KHUNG CSS (ĐỂ TRÁNH VỠ GIAO DIỆN) ---
BẠN BẮT BUỘC PHẢI ÁP DỤNG CÁC QUY TẮC CSS SAU VÀO MÃ:
- Font chữ: '{font_family}', sans-serif. Màu chủ đạo: {hex_color}
- Bố cục nền (Body): `margin: 0; padding: 20px; min-height: 100vh; display: flex; justify-content: center; align-items: center; background-color: #f3f4f6; font-family: '{font_family}', sans-serif;`
- Container Chính (Bắt buộc rộng rãi): `.game-container {{ width: 100%; max-width: 900px; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; box-sizing: border-box; }}`
- Bố cục Lưới/Nút bấm (Grid chống tràn): Dành cho các đáp án hoặc thẻ bài. `.grid-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; width: 100%; margin-top: 30px; }}`
- Chống trào chữ (Text Wrapping) cho mọi nút bấm/thẻ bài: `.btn, .card {{ width: 100%; padding: 20px; white-space: normal !important; word-wrap: break-word; overflow-wrap: break-word; line-height: 1.5; font-size: 1.1rem; box-sizing: border-box; }}`
- Hiệu ứng: Cần có hover đổi màu nhẹ, transform translateY(-2px). Có class `.shake` để rung lắc khi sai.

--- 3. KIẾN TRÚC GAME LOOP (Bằng Javascript) ---
Phải có 3 trạng thái ẩn/hiện (`display: none` / `display: flex`):
1. `start-screen`: Tiêu đề to, luật chơi, nút Bắt đầu chơi.
2. `play-screen`: Chứa Progress bar, Câu hỏi hiện tại, lưới Đáp án/Thẻ bài.
3. `end-screen`: Kết quả điểm số, thông điệp, nút Chơi lại.

--- 4. TÍCH HỢP TOÁN HỌC ---
Nhúng script MathJax qua CDN vào thẻ <head>:
`<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>`
Sử dụng cú pháp `\\( ... \\)`. JS gọi `MathJax.typesetPromise()` khi thay đổi câu hỏi.

--- NỘI DUNG GIÁO ÁN GỐC ---
{noidung_giaosan[:10000]}

TUYỆT ĐỐI CHỈ TRẢ VỀ DUY NHẤT MÃ HTML BỌC TRONG ```html ... ```, KHÔNG GIẢI THÍCH!
"""
            try:
                # Tự động nhận diện model OpenAI hoặc Gemini tùy theo khóa thầy nhập
                if AIEngine2 is not None:
                    engine_v2 = AIEngine2() # Mặc định tự lấy config từ st.secrets hoặc API key sidebar
                    res = engine_v2.generate_text(prompt, temperature=0.2) # Giảm temperature để code HTML ổn định hơn
                elif hasattr(ai_engine, "generate_text"):
                    res = ai_engine.generate_text(prompt)
                else:
                    res = str(ai_engine(prompt))
                
                if res.startswith("❌"):
                    st.error(res)
                else:
                    match = re.search(r'```html(.*?)```', res, re.DOTALL | re.IGNORECASE)
                    if match:
                        code_html = match.group(1).strip()
                        code_html = code_html.replace("\\`", "`")
                        st.session_state.game_html = code_html
                    else:
                        st.session_state.game_html = res
                    st.session_state.game_name = game_title.replace(" ", "_")
                    st.success("✅ Hoàn hảo! Giao diện đã được thiết kế lại chuẩn Responsive!")
                    st.balloons()
            except Exception as e:
                st.error(f"❌ Lỗi hệ thống khi sinh mã trò chơi: {e}")

    # ========================================================
    # MÀN HÌNH TRẢI NGHIỆM VÀ XUẤT BẢN
    # ========================================================
    if st.session_state.game_html:
        st.markdown("---")
        col_title, col_download = st.columns([3, 1])
        with col_title:
            st.markdown("### 🕹️ PLAYTEST (TRẢI NGHIỆM THỰC TẾ)")
        with col_download:
            st.download_button(
                label="💾 TẢI FILE GAME (.HTML)",
                data=st.session_state.game_html,
                file_name=f"Game_HocTap_{st.session_state.game_name}.html",
                mime="text/html",
                use_container_width=True,
                type="primary"
            )
        
        # Tăng width lên tối đa và đảm bảo hiển thị đẹp trên mọi màn hình
        components.html(st.session_state.game_html, width=None, height=800, scrolling=True)
