# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_tro_choi.py
Nhiệm vụ: Trợ lý Thiết kế Trò chơi & Gamification tích hợp Kho game tương tác.
============================================================
"""

import logging
import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word của dự án
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# Danh mục các trò chơi và thí nghiệm trực tuyến
KHO_GAME_ONLINE = {
    "📐 Toán học & Hình học": [
        {"name": "Trò chơi Toán cổ 1", "url": "https://trochoitoancovanhsmu.netlify.app/"},
        {"name": "Trò chơi Toán cổ 2 (Đạo hàm)", "url": "https://trochoitoancovandaoham1.netlify.app/"},
        {"name": "Trò chơi Câu lạc bộ Toán 22", "url": "https://trochoicovanclbtoan22.netlify.app/"},
        {"name": "Math 2 Word", "url": "https://math-2-word.vercel.app/"},
        {"name": "Trò chơi Toán học 01", "url": "https://trochoi01.netlify.app/"},
    ],
    "📚 Văn học & Ngôn ngữ": [
        {"name": "Đấu trường Văn học", "url": "https://dautruongvanhoc.netlify.app/"},
        {"name": "Game Cờ thi đua Ngữ văn", "url": "https://gamecothithi.netlify.app/"},
        {"name": "Trò chơi Văn học Thuận 1B", "url": "https://gamethuan1b.netlify.app/"},
        {"name": "Game Bích Phương", "url": "https://gamebbichphuong1.netlify.app/"},
        {"name": "Game Nghiêng đầu", "url": "https://gamenghiengdau.netlify.app/"},
    ],
    "🇬🇧 Tiếng Anh": [
        {"name": "English Grammar Arena", "url": "https://englishgrammararena.netlify.app/"},
    ],
    "💻 Tin học & Lập trình": [
        {"name": "Lập trình cùng Cô Đức", "url": "https://laptrinhcoduc.netlify.app/"},
        {"name": "Mối liên hệ UI", "url": "https://vythiviethals.github.io/moi_lien_he_UI/"},
    ],
    "⚡ Vật lý & Thí nghiệm ảo": [
        {"name": "Thử tài Vật lý", "url": "https://thutaivatly.netlify.app/"},
        {"name": "Phòng thí nghiệm Vật lý tương tác", "url": "http://thinghiemvatly.studyai.id.vn/"},
    ]
}

def render_xd_tro_choi(ai_engine_cu=None):
    if "game_script_result" not in st.session_state:
        st.session_state["game_script_result"] = None
    if "game_topic_name" not in st.session_state:
        st.session_state["game_topic_name"] = "Gamification"

    st.markdown("### 🎯 Trợ lý Thiết kế Trò chơi & Kho Game Tương tác")
    st.caption("Chuyển hóa bài học thành kịch bản trò chơi hóa sinh động bằng AI, đồng thời trải nghiệm trực tiếp các minigame và phòng thí nghiệm ảo ngay trên hệ thống.")

    # Tạo các tab phân chia rõ ràng giữa Trải nghiệm Game trực tuyến và AI Sáng tạo kịch bản
    tab_choi_game, tab_ai_game = st.tabs(["🎮 Kho Game & Thí nghiệm Trực tuyến", "🤖 AI Thiết kế Kịch bản Gamification"])

    # ========================================================
    # TAB 1: KHO GAME & THÍ NGHIỆM TRỰC TUYẾN
    # ========================================================
    with tab_choi_game:
        st.markdown("#### 🌐 Trải nghiệm Trò chơi & Thí nghiệm tương tác giáo dục")
        st.info("💡 Thầy cô có thể chọn trực tiếp các trò chơi dưới đây để đưa vào bài giảng, chiếu trên lớp hoặc cho học sinh trải nghiệm trực tiếp ngay khung bên dưới.")

        # Chọn lĩnh vực
        linh_vuc_chon = st.selectbox("Chọn nhóm môn học / lĩnh vực:", list(KHO_GAME_ONLINE.keys()), key="select_linh_vuc_game")
        
        # Lấy danh sách game trong lĩnh vực
        danh_sach_game = KHO_GAME_ONLINE[linh_vuc_chon]
        game_names = [g["name"] for g in danh_sach_game]
        
        game_chon = st.selectbox("Chọn trò chơi / thí nghiệm cụ thể:", game_names, key="select_game_name")

        # Tìm URL tương ứng
        selected_url = ""
        for g in danh_sach_game:
            if g["name"] == game_chon:
                selected_url = g["url"]
                break

        if selected_url:
            st.markdown(f"🔗 **Đường dẫn liên kết trực tiếp:** [{selected_url}]({selected_url})")
            
            # Nút mở rộng xem trực tiếp iframe
            with st.expander(f"🖥️ Nhấn để mở / Thu gọn không gian trải nghiệm: {game_chon}", expanded=True):
                components.iframe(selected_url, height=650, scrolling=True)

    # ========================================================
    # TAB 2: AI THIẾT KẾ KỊCH BẢN GAMIFICATION
    # ========================================================
    with tab_ai_game:
        with st.container(border=True):
            chu_de = st.text_input("Chủ đề kiến thức cần trò chơi hóa:", placeholder="VD: Ôn tập Lịch sử Chương 2, Bảng tuần hoàn hóa học, Các thì trong tiếng Anh...")
            
            col1, col2 = st.columns(2)
            with col1:
                the_loai = st.selectbox(
                    "Thể loại trò chơi sinh động:", 
                    [
                        "🏰 Phòng thoát hiểm giải đố (Escape Room)", 
                        "🗺️ Hành trình phiêu lưu / Săn kho báu (Adventure Quest)", 
                        "⚔️ Đấu trường đối kháng 1v1 / Chia đội (Battle Arena)", 
                        "📺 Show truyền hình (Ai là triệu phú / Chiếc nón kỳ diệu / Rung chuông vàng)", 
                        "🔍 Trạm thử thách khoa học (Station Rotation)",
                        "🧩 Ghép mảnh ghép bí mật (Mystery Puzzle)"
                    ]
                )
            with col2:
                quy_mo = st.selectbox("Hình thức tổ chức:", ["Hoạt động chia đội nhóm trên lớp", "Trò chơi toàn lớp tương tác chung", "Hoạt động cá nhân / Trải nghiệm số"])
                
            col3, col4 = st.columns(2)
            with col3:
                thoi_luong = st.selectbox("Thời lượng dự kiến:", ["10 - 15 phút (Khởi động / Warm-up)", "20 - 30 phút (Hoạt động trọng tâm)", "Trọn vẹn 1 tiết học (Game-based Lesson)"])
            with col4:
                doi_tuong = st.selectbox("Đối tượng học sinh:", ["Tiểu học (Sinh động, trực quan)", "THCS (Thách thức, hào hứng)", "THPT (Tư duy logic, chiến thuật)"])

            mong_muon = st.text_area("Yêu cầu thêm (Luật chơi đặc biệt, phần thưởng, đạo cụ có sẵn):", placeholder="VD: Gồm 3 vòng, mỗi đội có 3 quyền trợ giúp, cần tích hợp câu hỏi vận dụng cao...")
            
            btn_game = st.button("🎲 THIẾT KẾ KỊCH BẢN GAME CHI TIẾT", type="primary", use_container_width=True)

        if btn_game:
            if not chu_de.strip():
                st.warning("⚠️ Vui lòng nhập chủ đề kiến thức.")
            else:
                if AIEngine2 is None:
                    st.error("❌ Chưa kết nối hệ thống AI Engine.")
                else:
                    with st.spinner("⏳ AI đang sáng tạo cốt truyện, thiết kế thử thách và xây dựng luật chơi cuốn hút..."):
                        prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA THIẾT KẾ TRÒ CHƠI HỌC TẬP (GAMIFICATION EXPERT) VÀ ĐẠO DIỄN SƯ PHẠM.
Hãy thiết kế một kịch bản trò chơi học tập vô cùng sinh động, chi tiết và dễ áp dụng:

--- THÔNG SỐ KỊCH BẢN ---
- Kiến thức cốt lõi / Chủ đề: {chu_de}
- Thể loại trò chơi: {the_loai}
- Hình thức tổ chức: {quy_mo}
- Thời lượng: {thoi_luong}
- Đối tượng: {doi_tuong}
- Yêu cầu riêng từ giáo viên: {mong_muon if mong_muon else 'Không có'}

--- CẤU TRÚC KỊCH BẢN BẮT BUỘC ---
Hãy trình bày bằng Markdown thật bắt mắt với các phần rõ ràng sau:

### 🌟 1. Cốt truyện & Bối cảnh (The Hook)
(Xây dựng một câu chuyện giả tưởng hoặc bối cảnh kích thích trí tò mò, biến học sinh thành nhân vật chính trong game).

### 📜 2. Luật chơi & Cơ chế Tính điểm (Game Mechanics)
(Quy định rõ cách chia đội, thời gian, cách tính điểm thưởng/phạt, quyền trợ giúp để đảm bảo lớp học trật tự nhưng hào hứng).

### 🏆 3. Hệ thống Thử thách / Các Vòng chơi (Challenges & Quests)
(Thiết kế ít nhất 3 vòng chơi tăng dần độ khó. **Mỗi vòng phải chứa nội dung câu hỏi, bài tập hoặc câu đố gắn chặt với kiến thức chuyên môn của chủ đề `{chu_de}` kèm theo Đáp án đầy đủ**).

### 🛠️ 4. Hướng dẫn Chuẩn bị cho Giáo viên (Teacher's Toolkit)
(Liệt kê các đạo cụ, phiếu học tập, slide hoặc trang web công nghệ có thể hỗ trợ tổ chức trò chơi này mượt mà nhất).
"""
                        try:
                            engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                            result = engine_v2.generate_text(prompt, temperature=0.7)
                            
                            if result.startswith("❌"):
                                st.error(result)
                            else:
                                st.session_state["game_script_result"] = result
                                st.session_state["game_topic_name"] = chu_de[:25].strip().replace(" ", "_")
                        except Exception as e:
                            st.error(f"Lỗi kết nối AI: {e}")

        # ========================================================
        # HIỂN THỊ KẾT QUẢ VÀ NÚT TẢI XUỐNG
        # ========================================================
        if st.session_state.get("game_script_result"):
            st.markdown("---")
            st.markdown("### 🏆 Kịch bản Trò chơi hóa (Gamification)")
            st.markdown(st.session_state["game_script_result"], unsafe_allow_html=True)
            
            st.markdown("### 📥 Lưu trữ Kịch bản Trò chơi")
            col_txt, col_word = st.columns(2)
            
            with col_txt:
                st.download_button(
                    label="📄 Tải kịch bản (.TXT)",
                    data=st.session_state["game_script_result"],
                    file_name=f"Game_{st.session_state['game_topic_name']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            with col_word:
                if export_word is None:
                    st.warning("⚠️ Module Word chưa sẵn sàng.")
                else:
                    try:
                        export_data = {
                            "ai_generated_content": st.session_state["game_script_result"],
                            "is_dkt": False
                        }
                        with st.spinner("Đang kết xuất file Word..."):
                            word_bytes = export_word(export_data)
                    
                        st.download_button(
                            label="📘 TẢI KỊCH BẢN (.DOCX)",
                            data=word_bytes,
                            file_name=f"Game_{st.session_state['game_topic_name']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            type="primary"
                        )
                    except Exception as e:
                        st.error(f"Lỗi xuất Word: {e}")
                        
            if st.button("🔄 Thiết kế Trò chơi Mới", use_container_width=True):
                st.session_state["game_script_result"] = None
                st.rerun()
