# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_ca_nhan_hoa.py
Nhiệm vụ: Trợ lý Chuyên gia Thiết kế Trò chơi Học tập (AI Edu-Game Architect).
Kiến trúc: Áp dụng Game Loop chuẩn (Start -> Play -> Score -> Replay).
============================================================
"""

import io
import re
import logging
import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

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
            che_do_ai = st.radio("Bộ não Kiến trúc AI:", ["🎯 Tư duy Sâu (Gemini 2.5 Pro - Khuyên dùng cho game phức tạp)", "⚡ Phản xạ Nhanh (Gemini 2.5 Flash)"])
        with col_emoji:
            dung_emoji = st.checkbox("Sử dụng Emojis làm đồ họa minh họa", value=True)

        # BUTTON TRIGGER
        btn_tao_game = st.button("🚀 KHỞI TẠO & LẬP TRÌNH TRÒ CHƠI", type="primary", use_container_width=True)

    # ========================================================
    # XỬ LÝ LẬP TRÌNH GAME (AI ARCHITECT CORE)
    # ========================================================
    if btn_tao_game:
        if not uploaded_file:
            st.warning("⚠️ Chuyên gia cần tài liệu gốc để lên ý tưởng. Thầy vui lòng tải file lên nhé!")
            return
            
        if ai_engine is None:
            st.error("❌ Mất kết nối hệ thống AI. Vui lòng kiểm tra API Key ở menu trái.")
            return

        with st.spinner("⏳ Chuyên gia AI đang phân tích sư phạm và viết mã nguồn (HTML5/CSS3/JS) rập khuôn kiến trúc..."):
            noidung_giaosan = extract_text_from_file(uploaded_file)
            
            # Xử lý CSS Theme
            mau_css = {"Xanh dương": "#3B82F6", "Xanh ngọc": "#14B8A6", "Tím violet": "#8B5CF6", "Hồng rose": "#F43F5E", "Vàng hổ phách": "#F59E0B"}
            hex_color = mau_css.get(mau_chu_dao.split(" (")[0], "#3B82F6")
            font_family = font_chu.split(" (")[0]
            game_title = ten_game if ten_game.strip() else "Trải nghiệm Học tập Tương tác"

            # TỐI ƯU HÓA CƠ CHẾ SƯ PHẠM ĐỂ TRÁNH LỖI UX/UI
            luat_choi = ""
            if "Trắc nghiệm" in loai_tro_choi:
                luat_choi = "Cơ chế: Trắc nghiệm 4 đáp án. Khi chọn sai, rung lắc nút bấm. Khi chọn đúng, hiện màu xanh và tự động qua câu."
            elif "Nối cặp" in loai_tro_choi:
                luat_choi = "Cơ chế: Nối cặp (Matching). TUYỆT ĐỐI KHÔNG DÙNG DRAG & DROP vì hay lỗi trên mobile. Hãy dùng cơ chế CLICK: Người chơi click chọn ô ở cột A, ô đó sáng lên, sau đó click chọn ô tương ứng ở cột B. Nếu đúng thì 2 ô biến mất hoặc chuyển màu xám."
            elif "Điền khuyết" in loai_tro_choi:
                luat_choi = "Cơ chế: Hiện câu có chỗ trống (___). Cung cấp các nút từ khóa bên dưới để người chơi click điền vào thay vì phải gõ phím."
            elif "Đúng / Sai" in loai_tro_choi:
                luat_choi = "Cơ chế: Quẹt thẻ (Tinder-like) hoặc 2 nút Bấm Đúng/Sai khổng lồ. Yêu cầu phản hồi ngay lập tức."
            elif "Thẻ bài" in loai_tro_choi:
                luat_choi = "Cơ chế: Lật thẻ Memory Match dạng lưới (Grid). Chọn 2 thẻ, giống nhau thì lật ngửa mãi, khác nhau thì úp lại sau 1 giây."
            else:
                luat_choi = "Bạn là Chuyên gia thiết kế, hãy tự chọn cơ chế (Quiz hoặc Nối cặp Click-to-Match) phù hợp nhất với dữ liệu đưa vào."

            # SIÊU PROMPT (MASTER PROMPT) CHO KIẾN TRÚC GAME
            prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA THIẾT KẾ TRÒ CHƠI SƯ PHẠM (GAME DESIGNER) VÀ KỸ SƯ FRONT-END (HTML5/JS/CSS3) BẬC THẦY.
Nhiệm vụ: Đọc tài liệu giáo án dưới đây và lập trình ra một Mini-Game Web hoàn chỉnh chỉ trong 1 file HTML duy nhất.

--- 1. CỐT LÕI SƯ PHẠM & CƠ CHẾ ---
- Thể loại Game: {loai_tro_choi}
- Cơ chế bắt buộc (UX rule): {luat_choi}
- Số lượng nội dung: Tự động trích xuất đúng {so_luong} câu hỏi/cặp từ khóa chất lượng nhất từ tài liệu.
- Tên trò chơi: {game_title}

--- 2. YÊU CẦU KIẾN TRÚC HỆ THỐNG (GAME LOOP) ---
Trò chơi BẮT BUỘC phải có 3 Màn hình (States) quản lý bằng Javascript (ẩn/hiện các div):
- SCREEN 1 (START): Chứa Tên trò chơi to, đẹp, luật chơi ngắn gọn và nút "Bắt đầu chơi" (Start).
- SCREEN 2 (GAMEPLAY): Chứa thanh tiến trình (Progress bar), số điểm hiện tại, nội dung câu hỏi/trò chơi, nút tắt âm thanh (nếu có). Có thanh cuộn dọc (overflow-y: auto) để không bị lấp giao diện.
- SCREEN 3 (ENDGAME): Hiển thị khi hoàn thành. Hiện Tổng điểm, Lời chúc mừng động viên (dùng Emoji) và nút "Chơi lại" (Replay) để khởi tạo lại toàn bộ state.

--- 3. YÊU CẦU UI/UX & THẨM MỸ ---
- Bảng màu chủ đạo (Primary color): {hex_color}
- Font chữ: Sử dụng Google Font '{font_family}'.
- Đồ họa: {'Sử dụng phong phú các Emoji để minh họa cho đáp án hoặc nút bấm' if dung_emoji else 'Phong cách tối giản, phẳng (Flat design)'}.
- CSS Animation: Phải có hiệu ứng chuyển cảnh mềm mại (fade in), hiệu ứng hover cho các nút bấm, hiệu ứng rung lắc (shake) nếu trả lời sai, và phóng to nhẹ nếu trả lời đúng.
- Yêu cầu đặc biệt từ giáo viên: {yeu_cau if yeu_cau.strip() else 'Thiết kế bo góc tròn (border-radius), đổ bóng (box-shadow) để nhìn giống một App di động hiện đại.'}

--- 4. TÍCH HỢP TOÁN HỌC (BẮT BUỘC NẾU CÓ CÔNG THỨC) ---
Nhúng script MathJax qua CDN vào thẻ <head>:
`<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>`
Sử dụng cú pháp `\\( ... \\)` cho công thức toán trong HTML/JS. Khi JS kết xuất (render) nội dung mới lên màn hình, BẮT BUỘC phải gọi `MathJax.typesetPromise()` để render lại công thức.

--- NỘI DUNG GIÁO ÁN GỐC ---
{noidung_giaosan[:10000]}

--- QUY TẮC TRẢ VỀ KẾT QUẢ ---
TUYỆT ĐỐI KHÔNG giải thích, KHÔNG chào hỏi, KHÔNG viết markdown dư thừa ngoài khối code.
CHỈ TRẢ VỀ DUY NHẤT mã HTML chuẩn xác bọc trong ```html ... ```
"""
            try:
                model_name = "gemini-2.5-pro" if "Tư duy Sâu" in che_do_ai else "gemini-2.5-flash"
                
                # Gọi qua AI Engine thống nhất
                if hasattr(ai_engine, "generate_text"):
                    res = ai_engine.generate_text(prompt, model_name=model_name)
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
                    st.success("✅ Tuyệt vời! Chuyên gia AI đã thiết kế xong kịch bản và lập trình thành công!")
                    st.balloons() # Hiệu ứng chúc mừng của Streamlit
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
                type="primary",
                help="Tải file này về máy, click đúp là mở chơi được không cần mạng. Gửi cho học sinh chơi rất dễ dàng."
            )
        
        # Mở rộng chiều cao để chứa giao diện game mượt hơn
        components.html(st.session_state.game_html, height=800, scrolling=True)
