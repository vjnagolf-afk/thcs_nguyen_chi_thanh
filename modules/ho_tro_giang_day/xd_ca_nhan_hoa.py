# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_ca_nhan_hoa.py
Nhiệm vụ: Trợ lý Chuyên gia Thiết kế Trò chơi Học tập (AI Edu-Game Architect).
Kiến trúc: Áp dụng Game Loop chuẩn, CSS Responsive, Ép buộc Nội dung Text.
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
                ]
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

        with st.spinner("⏳ Đang phân tích logic sư phạm và ép kiểu kiến trúc giao diện..."):
            noidung_giaosan = extract_text_from_file(uploaded_file)
            
            mau_css = {"Xanh dương": "#3B82F6", "Xanh ngọc": "#14B8A6", "Tím violet": "#8B5CF6", "Hồng rose": "#F43F5E", "Vàng hổ phách": "#F59E0B"}
            hex_color = mau_css.get(mau_chu_dao.split(" (")[0], "#3B82F6")
            font_family = font_chu.split(" (")[0]
            game_title = ten_game if ten_game.strip() else "Trải nghiệm Học tập Tương tác"

            luat_choi = ""
            if "Trắc nghiệm" in loai_tro_choi:
                luat_choi = "Cơ chế: Trắc nghiệm 4 đáp án. BẤM CHỌN MỘT ĐÁP ÁN, nếu đúng chuyển câu, nếu sai rung lắc nút."
            elif "Nối cặp" in loai_tro_choi:
                luat_choi = "Cơ chế: Nối cặp (Matching). TUYỆT ĐỐI DÙNG CLICK-TO-MATCH (Click ô A, click ô B). KHÔNG DÙNG Drag-and-Drop."
            elif "Điền khuyết" in loai_tro_choi:
                luat_choi = "Cơ chế: Hiện câu có chỗ trống (___). Cung cấp các nút từ khóa bên dưới để click."
            elif "Đúng / Sai" in loai_tro_choi:
                luat_choi = "Cơ chế: Hiển thị 1 nhận định và 2 nút bấm chữ to 'ĐÚNG' hoặc 'SAI'."
            elif "Thẻ bài" in loai_tro_choi:
                luat_choi = "Cơ chế: Memory Match (Lật thẻ bài). Sinh ra lưới thẻ bài. Bấm vào thẻ sẽ lật thẻ hiện chữ. Giống nhau giữ nguyên, khác nhau úp lại."
            else:
                luat_choi = "Bạn tự chọn cơ chế (Quiz trắc nghiệm hoặc Thẻ bài) phù hợp nhất với dữ liệu."

            # SIÊU PROMPT - ÉP BUỘC NỘI DUNG VÀ KHUNG CSS
            prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA THIẾT KẾ TRÒ CHƠI SƯ PHẠM VÀ KỸ SƯ FRONT-END BẬC THẦY.
Nhiệm vụ: Lập trình 1 Mini-Game Web hoàn chỉnh chỉ trong 1 file HTML duy nhất dựa vào giáo án.

--- 1. YÊU CẦU NỘI DUNG & VĂN BẢN (BẮT BUỘC TUÂN THỦ) ---
- Cảnh báo lỗi: BẠN TUYỆT ĐỐI KHÔNG ĐƯỢC XÓA CHỮ (TEXT). Mọi nút bấm, thẻ bài BẮT BUỘC phải hiển thị đầy đủ văn bản nội dung.
- Sử dụng Emoji: { "CHỈ DÙNG EMOJI NHƯ MỘT ICON ĐỨNG TRƯỚC CHỮ (Ví dụ: '✅ Đúng', '🌟 Năng lượng'). TUYỆT ĐỐI KHÔNG DÙNG EMOJI THAY THẾ CHỮ." if dung_emoji else "Không dùng Emoji, chỉ dùng văn bản thuần túy." }
- Số lượng: {so_luong} câu hỏi/cặp. Tên trò chơi: {game_title}
- Thể loại & Cơ chế: {loai_tro_choi}. {luat_choi}

--- 2. BẮT BUỘC TUÂN THỦ KHUNG CSS CẤU TRÚC (CHỐNG VỠ GIAO DIỆN) ---
BẠN BẮT BUỘC PHẢI THÊM CÁC QUY TẮC CSS SAU VÀO MÃ:
- Font chữ: '{font_family}', sans-serif. Màu chủ đạo: {hex_color}
- Nền trang (Body): `margin: 0; padding: 20px; min-height: 100vh; display: flex; justify-content: center; align-items: center; background-color: #f3f4f6;`
- Container Chính: `.game-container {{ width: 100%; max-width: 900px; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); min-height: 500px; }}`
- Lưới Grid: `.grid-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; width: 100%; padding-top: 20px; }}`
- Định dạng Thẻ bài/Nút bấm để KHÔNG BỊ TRÀN CHỮ: `.btn, .card {{ width: 100%; min-height: 80px; padding: 15px; font-size: 1.2rem; white-space: normal !important; word-wrap: break-word; line-height: 1.4; display: flex; align-items: center; justify-content: center; text-align: center; cursor: pointer; }}`

--- 3. CSS & JS RIÊNG CHO GAME LẬT THẺ (Nếu thể loại là Memory Match) ---
Nếu là game Memory Match, BẮT BUỘC phải dùng cấu trúc lật 3D:
- HTML cấu trúc thẻ: `<div class="card" onclick="flip(this)"><div class="front">❓</div><div class="back">Nội Dung Chữ</div></div>`
- CSS lật thẻ: 
`.card {{ perspective: 1000px; position: relative; transform-style: preserve-3d; transition: transform 0.6s; }}`
`.card.flipped {{ transform: rotateY(180deg); }}`
`.front, .back {{ width: 100%; height: 100%; position: absolute; backface-visibility: hidden; display: flex; justify-content: center; align-items: center; padding: 10px; box-sizing: border-box; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}`
`.front {{ background: {hex_color}; color: white; font-size: 2rem; }}`
`.back {{ background: white; color: black; transform: rotateY(180deg); font-size: 1.1rem; border: 2px solid {hex_color}; }}`

--- 4. KIẾN TRÚC GAME LOOP (Bằng Javascript) ---
Phải có 3 màn hình ẩn/hiện (`display: none` / `display: block`):
1. `start-screen`: Tiêu đề, hướng dẫn chơi, nút Bắt đầu.
2. `play-screen`: Chứa Progress bar, nội dung, lưới tương tác.
3. `end-screen`: Kết quả điểm số, thông điệp khen ngợi, nút Chơi lại (Reset toàn bộ trạng thái).

--- NỘI DUNG GIÁO ÁN GỐC (ĐỂ LẤY DỮ LIỆU) ---
{noidung_giaosan[:10000]}

TUYỆT ĐỐI CHỈ TRẢ VỀ DUY NHẤT MÃ HTML BỌC TRONG ```html ... ```, KHÔNG GIẢI THÍCH!
"""
            try:
                model_to_use = "gemini-2.5-pro" if "Tư duy Sâu" in che_do_ai else "gemini-2.5-flash"
                
                # Gọi API thông qua AIEngine2 (OpenRouter) hoặc AIEngine (Gemini gốc)
                if AIEngine2 is not None:
                    engine_v2 = AIEngine2()
                    # Sử dụng temperature=0.1 để AI giữ sự chính xác tuyệt đối trong code và text
                    res = engine_v2.generate_text(prompt, temperature=0.1) 
                elif hasattr(ai_engine, "generate_text"):
                    res = ai_engine.generate_text(prompt, model_name=model_to_use)
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
                    st.success("✅ Tuyệt vời! Nội dung văn bản và CSS lật thẻ đã được ép khuôn thành công!")
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
        
        # iframe hiển thị giao diện mượt mà
        components.html(st.session_state.game_html, width=None, height=800, scrolling=True)
