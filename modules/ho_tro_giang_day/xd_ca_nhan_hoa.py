# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_ca_nhan_hoa.py
Nhiệm vụ: Trợ lý Tạo Game Tương tác bằng AI.
Chức năng: Đọc giáo án, tự động lập trình ra mini-game HTML5
dựa trên thiết lập Giao diện, Màu sắc, Font chữ của giáo viên.
============================================================
"""

import io
import re
import base64
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Bắt buộc import AIEngine2 để dùng Smart Router
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# Hàm đọc nội dung file
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
        logger.error(f"Lỗi đọc file: {e}")
    return extracted_text

def render_xd_ca_nhan_hoa(ai_engine_cu=None):
    if "game_html" not in st.session_state:
        st.session_state.game_html = None
    if "game_name" not in st.session_state:
        st.session_state.game_name = "AI_Edu_Game"

    st.markdown("### 🎮 Trợ lý Thiết kế Game Học tập bằng AI")
    st.caption("AI tự động phân tích giáo án và lập trình ra một mini-game tương tác hoàn chỉnh (chơi trực tiếp trên tab mới hoặc tải về HTML).")

    with st.container(border=True):
        # 1. Tải lên giáo án
        st.markdown("#### 1️⃣ Tải lên File Giáo Án")
        uploaded_file = st.file_uploader("Kéo thả hoặc click để chọn file (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])

        st.markdown("---")
        
        # 2. Chọn loại trò chơi
        st.markdown("#### 2️⃣ Chọn loại trò chơi")
        loai_tro_choi = st.selectbox(
            "Hình thức tương tác:",
            [
                "🌟 AI tự động chọn (Khuyên dùng - Phù hợp nhất với tài liệu)",
                "✅ Trắc nghiệm (Quiz)",
                "🗂️ Nối cặp (Matching)",
                "📝 Điền từ vào chỗ trống",
                "⚖️ Đúng / Sai",
                "🧠 Lật hình ghi nhớ (Memory Match)"
            ]
        )

        st.markdown("---")
        
        # 3. Theme Builder
        st.markdown("#### 3️⃣ Theme Builder (Cấu hình giao diện)")
        col_color, col_font = st.columns(2)
        with col_color:
            mau_chu_dao = st.selectbox("Màu chủ đạo:", ["Xanh dương (Blue)", "Xanh ngọc (Teal)", "Tím violet (Purple)", "Hồng rose (Pink)", "Vàng hổ phách (Amber)"])
        with col_font:
            font_chu = st.selectbox("Font chữ:", ["Inter (Hiện đại)", "Quicksand (Mềm mại)", "Nunito (Đáng yêu)", "Roboto (Cơ bản)"])

        st.markdown("---")
        
        # 4, 5, 6. Cấu hình chi tiết
        col_sl, col_ten = st.columns([1, 2])
        with col_sl:
            st.markdown("#### 4️⃣ Số lượng câu hỏi")
            so_luong = st.number_input("Số lượng", min_value=3, max_value=40, value=5, label_visibility="collapsed")
        with col_ten:
            st.markdown("#### 5️⃣ Tên trò chơi (Tùy chọn)")
            ten_game = st.text_input("Nhập tên", placeholder="VD: Thử tài Lịch Sử...", label_visibility="collapsed")

        st.markdown("#### 6️⃣ Yêu cầu thêm (Tùy chọn)")
        yeu_cau = st.text_area("Yêu cầu thêm", placeholder="VD: Thêm hiệu ứng pháo hoa khi chiến thắng, có đồng hồ đếm ngược 10s...", label_visibility="collapsed", height=80)

        st.markdown("---")

        # 7. Chế độ AI
        st.markdown("#### 7️⃣ Chế độ ưu tiên AI")
        che_do_ai = st.radio(
            "Chọn Model:",
            ["🎯 Chất lượng cao (Dùng Gemini Pro: Thông minh, lập trình logic game phức tạp. Chờ 30s-60s)", 
             "⚡ Tốc độ nhanh (Dùng Gemini Flash: Phù hợp game đơn giản. Chờ 5s-15s)"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # 8. Tùy chọn hiển thị
        st.markdown("#### 8️⃣ Tùy chọn hiển thị")
        dung_emoji = st.checkbox("Sử dụng biểu tượng vui nhộn (Emoji) làm hình ảnh minh họa")

        # NÚT TẠO GAME
        btn_tao_game = st.button("🚀 TẠO GAME NGAY", type="primary", use_container_width=True)

    # ========================================================
    # XỬ LÝ LẬP TRÌNH GAME BẰNG AI
    # ========================================================
    if btn_tao_game:
        if not uploaded_file:
            st.warning("⚠️ Vui lòng tải lên giáo án để AI có dữ liệu làm game.")
            return
            
        if AIEngine2 is None:
            st.error("❌ Chưa kết nối được AI Engine.")
            return

        with st.spinner("⏳ AI đang đọc giáo án và lập trình giao diện (HTML/CSS/JS)..."):
            noidung_giaosan = extract_text_from_file(uploaded_file)
            
            model_to_use = "gemini-2.5-pro" if "Chất lượng cao" in che_do_ai else "gemini-2.5-flash"
            mau_css = {"Xanh dương": "#3B82F6", "Xanh ngọc": "#14B8A6", "Tím violet": "#8B5CF6", "Hồng rose": "#F43F5E", "Vàng hổ phách": "#F59E0B"}
            font_css = mau_chu_dao.split(" (")[0]
            hex_color = mau_css.get(font_css, "#3B82F6")
            font_family = font_chu.split(" (")[0]
            game_title = ten_game if ten_game.strip() else "Trò chơi Học tập"

            luat_choi = ""
            if "Trắc nghiệm" in loai_tro_choi:
                luat_choi = "Giao diện phải hiển thị câu hỏi và 4 đáp án lựa chọn (A,B,C,D)."
            elif "Nối cặp" in loai_tro_choi:
                luat_choi = "TẠO GAME NỐI CỘT TRÁI VÀ CỘT PHẢI. Phải chia 2 cột danh sách hiển thị cùng lúc trên màn hình, click chọn nối với nhau. TUYỆT ĐỐI KHÔNG LẬP TRÌNH DẠNG LẬT THẺ BÀI ÚP."
            elif "Điền từ" in loai_tro_choi:
                luat_choi = "Hiển thị câu hỏi bị khuyết từ (có ô trống) và từ khóa gợi ý để điền vào."
            elif "Đúng / Sai" in loai_tro_choi:
                luat_choi = "Lần lượt hiển thị các câu nhận định kèm 2 nút ĐÚNG hoặc SAI."
            elif "Lật hình" in loai_tro_choi:
                luat_choi = "TẠO GAME LẬT THẺ BÀI ÚP (Memory Match) dạng lưới thẻ bài úp."
            else:
                luat_choi = "Tự động chọn hình thức game phù hợp nhất với dữ liệu."

            prompt = f"""
BẠN LÀ MỘT LẬP TRÌNH VIÊN FRONT-END VÀ CHUYÊN GIA GIÁO DỤC.
Nhiệm vụ: Đọc giáo án dưới đây và LẬP TRÌNH ra một Mini-Game Web hoàn chỉnh bằng duy nhất 1 file HTML (chứa sẵn CSS và Javascript).

--- THÔNG TIN ---
- Thể loại: {loai_tro_choi}
- Cơ chế: {luat_choi}
- Số lượng: {so_luong}
- Tên game: {game_title}
- Màu chủ đạo: {hex_color}
- Font chữ: {font_family}
- Emoji: {'Có' if dung_emoji else 'Không'}
- Yêu cầu thêm: {yeu_cau if yeu_cau.strip() else 'Giao diện hiện đại, bo tròn, có hiệu ứng.'}
- Nội dung: {noidung_giaosan[:8000]}

--- YÊU CẦU LẬP TRÌNH ---
1. Viết mã HTML5, CSS3, JS gộp chung vào 1 khối duy nhất.
2. Giao diện đẹp, dùng màu {hex_color}, có thanh cuộn dọc (`overflow-y: auto`) để không bị che khuất nội dung khi có nhiều câu hỏi.
3. Nhúng thư viện MathJax qua CDN: `<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>` để hiển thị công thức toán học. Dùng định dạng `\\( ... \\)` cho công thức. Gọi `MathJax.typesetPromise()` sau khi thay đổi nội dung câu hỏi.
4. TUYỆT ĐỐI CHỈ TRẢ VỀ MÃ HTML ĐƯỢC BỌC TRONG KHUNG ```html ... ```. Không giải thích gì thêm.
"""
            try:
                engine_v2 = AIEngine2(default_model=model_to_use)
                res = engine_v2.generate_text(prompt, temperature=0.7)
                
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
                    st.success("✅ AI đã lập trình game thành công!")
            except Exception as e:
                st.error(f"❌ Lỗi khi sinh code: {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ VÀ NÚT TRẢI NGHIỆM AN TOÀN
    # ========================================================
    if st.session_state.game_html:
        st.markdown("---")
        st.markdown("### 🕹️ TRÒ CHƠI ĐÃ SẴN SÀNG")
        
        st.info("🎉 Hệ thống đã tạo xong Game! Thầy/Cô có thể bấm vào nút màu xanh bên dưới để chơi trực tiếp trên Tab mới hoặc tải file về máy.")
        
        try:
            b64_html = base64.b64encode(st.session_state.game_html.encode('utf-8')).decode('utf-8')
            btn_play_html = f"""
            <a href="data:text/html;base64,{b64_html}" target="_blank" style="display: block; text-align: center; background-color: #10B981; color: white; padding: 14px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; margin-bottom: 20px; transition: 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                🎮 BẤM VÀO ĐÂY ĐỂ CHƠI NGAY TRÊN TAB MỚI
            </a>
            """
            st.markdown(btn_play_html, unsafe_allow_html=True)
        except Exception:
            pass

        st.download_button(
            label="💾 TẢI XUỐNG FILE GAME (.HTML)",
            data=st.session_state.game_html,
            file_name=f"Game_{st.session_state.game_name}.html",
            mime="text/html",
            use_container_width=True,
            type="primary"
        )
        
        with st.expander("🔍 Xem trước mã nguồn HTML"):
            st.code(st.session_state.game_html, language="html")
