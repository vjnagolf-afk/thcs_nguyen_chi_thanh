# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_tro_choi.py
Nhiệm vụ: Trợ lý Thiết kế Trò chơi & Gamification.
Nâng cấp: Bổ sung thêm nhiều thể loại trò chơi sinh động, trực quan,
tích hợp AI tư duy sâu và xuất kịch bản ra file Word (.docx).
============================================================
"""

import logging
import streamlit as st

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

def render_xd_tro_choi(ai_engine_cu=None):
    if "game_script_result" not in st.session_state:
        st.session_state["game_script_result"] = None
    if "game_topic_name" not in st.session_state:
        st.session_state["game_topic_name"] = "Gamification"

    st.markdown("### 🎯 Trợ lý Thiết kế Trò chơi & Gamification")
    st.caption("Chuyển hóa bài học thành các kịch bản trò chơi hóa sinh động, phòng thoát hiểm, đấu trường đối kháng hoặc hành trình phiêu lưu trực quan.")

    with st.container(border=True):
        chu_de = st.text_input("Chủ đề kiến thức cần trò chơi hóa:", placeholder="VD: Ôn tập Lịch sử Chương 2, Bảng tuần hoàn hóa học, Các thì trong tiếng Anh...")
        
        col1, col2 = st.columns(2)
        with col1:
            the_loai = st.selectbox(
                "Thể loại trò chơi sinh động:", 
                [
                    "🏰 Phòng thoát hiểm giải đố (Escape Room)", 
                    "🗺️ Hành trình phiêu lưu / Săn khoang không gian (Adventure Quest)", 
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
