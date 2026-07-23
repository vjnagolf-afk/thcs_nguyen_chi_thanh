# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_tro_choi(ai_engine=None):
    st.markdown("### 🎯 Trợ lý Thiết kế Trò chơi & Gamification")
    st.caption("Chuyển hóa bài học thành các kịch bản trò chơi hóa (Gamification), trò chơi nhập vai hoặc phòng thoát hiểm (Escape Room).")

    with st.container(border=True):
        chu_de = st.text_input("Chủ đề kiến thức cần trò chơi hóa:", placeholder="VD: Ôn tập Lịch sử Chương 2, Bảng tuần hoàn hóa học...")
        
        col1, col2 = st.columns(2)
        with col1:
            the_loai = st.selectbox("Thể loại trò chơi:", ["Phòng thoát hiểm giải đố (Escape Room)", "Hành trình nhập vai (Role-playing)", "Truy tìm kho báu", "Ai là triệu phú / Show truyền hình"])
        with col2:
            quy_mo = st.selectbox("Hình thức tổ chức:", ["Chơi theo nhóm trên lớp", "Hoạt động cá nhân trên giấy", "Chơi trực tuyến (Cần phần mềm)"])
            
        mong_muon = st.text_area("Yêu cầu thêm (Luật chơi, số vòng, phần thưởng):", placeholder="Gồm 3 vòng, trả lời đúng nhận gợi ý mảnh ghép...")
        
        btn_game = st.button("🎲 Thiết kế Kịch bản Game", type="primary", use_container_width=True)

    if btn_game:
        if not chu_de.strip():
            st.warning("⚠️ Vui lòng nhập chủ đề kiến thức.")
        else:
            with st.spinner("AI đang sáng tạo luật chơi và xây dựng thử thách..."):
                prompt = f"""
                Bạn là một Chuyên gia Thiết kế Trò chơi Học tập (Gamification Expert).
                Hãy thiết kế một kịch bản trò chơi học tập hoàn chỉnh:
                - Kiến thức cốt lõi: {chu_de}
                - Thể loại: {the_loai}
                - Hình thức: {quy_mo}
                - Yêu cầu đặc biệt: {mong_muon}
                
                KỊCH BẢN CẦN CÓ:
                1. Cốt truyện & Bối cảnh (Hấp dẫn, khơi gợi trí tò mò).
                2. Luật chơi & Cách thức ghi điểm/chiến thắng.
                3. Thiết kế các Thử thách/Vòng chơi (Gắn chặt với kiến thức chuyên môn).
                4. Gợi ý công cụ / Vật dụng cần chuẩn bị cho Giáo viên.
                """
                
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown("#### 🏆 Kịch bản Trò chơi hóa (Gamification)")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
