# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_live(ai_engine=None):
    st.markdown("### 🔴 Trợ lý Kịch bản Tương tác Trực tiếp (Live)")
    st.caption("AI hỗ trợ giáo viên tạo các câu hỏi hâm nóng (warm-up), câu đố nhanh hoặc tình huống tranh biện để sử dụng ngay trong các phiên dạy Live/Trực tiếp.")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            chu_de_live = st.text_input("Chủ đề bài học hôm nay:", placeholder="VD: Hiện tượng nhà kính...")
        with col2:
            muc_dich = st.selectbox("Mục đích của hoạt động:", ["Warm-up (Phá băng đầu giờ)", "Tranh biện (Debate giữa giờ)", "Củng cố kiến thức (Cuối giờ)"])
            
        btn_tao_live = st.button("🔥 Tạo kịch bản tương tác Live", type="primary", use_container_width=True)

    if btn_tao_live:
        if not chu_de_live.strip():
            st.warning("⚠️ Vui lòng nhập chủ đề bài học.")
        else:
            with st.spinner("AI đang sáng tạo các tình huống tương tác hấp dẫn..."):
                prompt = f"""
                Bạn là một MC và Giáo viên truyền cảm hứng chuyên tổ chức các lớp học Live (Trực tiếp) rất sôi động.
                Hãy thiết kế một mini-game hoặc một kịch bản tương tác ngắn cho học sinh THCS.
                
                - Chủ đề: {chu_de_live}
                - Mục đích: {muc_dich}
                
                YÊU CẦU:
                - Viết ra 3 câu hỏi / tình huống ngắn gọn, giật gân, khơi gợi trí tò mò.
                - Đề xuất cách giáo viên yêu cầu học sinh tương tác (VD: Gõ phím 1 nếu đồng ý, phím 2 nếu không; hoặc Giơ tay...).
                - Cung cấp sẵn đáp án hoặc góc nhìn mở để giáo viên chốt lại vấn đề.
                """
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown("#### 🎭 Kịch bản Điều phối Lớp học")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
