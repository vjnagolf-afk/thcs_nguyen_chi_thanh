import streamlit as st
import time

def render_xd_live(ai_engine):
    st.markdown("### 🔴 Trạm điều khiển Lớp học Live")
    st.info("💡 Trợ lý đắc lực giúp giáo viên quản lý lớp học trực tuyến, phản xạ nhanh với câu hỏi của học sinh và tạo tương tác tức thì.")

    # 1. Bảng thông tin phòng học
    with st.expander("🔗 Thông tin Phòng học (Meet / Zoom / Teams)", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            link_phong = st.text_input("Đường dẫn phòng học:", placeholder="Ví dụ: https://meet.google.com/abc-xyz")
        with col2:
            st.button("Mở phòng học 🚀", type="primary", use_container_width=True, on_click=lambda: st.markdown(f'<meta http-equiv="refresh" content="0;url={link_phong}">', unsafe_allow_html=True) if link_phong else st.warning("Vui lòng nhập link!"))

    st.markdown("---")

    col3, col4 = st.columns(2)

    # 2. Trợ lý phản xạ nhanh (Hỏi đáp Live)
    with col3:
        st.markdown("#### ⚡ Trợ lý Phản xạ nhanh")
        st.caption("Nhập câu hỏi hóc búa của học sinh trong khung chat để AI gợi ý câu trả lời sư phạm.")
        
        if "live_qna_result" not in st.session_state:
            st.session_state.live_qna_result = ""
            
        cau_hoi_hs = st.text_area("Câu hỏi của học sinh:", height=100, placeholder="Ví dụ: Thầy ơi tại sao hố đen lại hút được ánh sáng ạ?")
        
        if st.button("Trợ giúp trả lời nhanh", type="secondary"):
            if cau_hoi_hs.strip():
                with st.spinner("Đang tìm câu trả lời..."):
                    prompt = f"Tôi đang dạy học trực tuyến cấp THCS. Học sinh vừa hỏi câu này: '{cau_hoi_hs}'. Hãy gợi ý cho tôi một câu trả lời NGẮN GỌN, DỄ HIỂU, CÓ TÍNH TƯƠNG TÁC (khoảng 3-4 câu) để tôi có thể đọc hoặc nhắn lại cho học sinh ngay lập tức."
                    try:
                        st.session_state.live_qna_result = ai_engine.generate_text(prompt)
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
            else:
                st.warning("Vui lòng nhập câu hỏi!")
                
        if st.session_state.live_qna_result:
            st.success(st.session_state.live_qna_result)

    # 3. Tạo tương tác nhanh (Poll/Quiz)
    with col4:
        st.markdown("#### 🎯 Tạo Mini-game / Khảo sát")
        st.caption("Sinh nhanh 1 câu hỏi trắc nghiệm hoặc tình huống để thả vào khung chat giúp lấy lại sự tập trung.")
        
        if "live_poll_result" not in st.session_state:
            st.session_state.live_poll_result = ""
            
        chu_de_tuong_tac = st.text_input("Chủ đề bài đang dạy:", placeholder="Ví dụ: Định luật Newton, Khí hậu Châu Á...")
        loai_tuong_tac = st.selectbox("Loại tương tác:", ["Câu hỏi Trắc nghiệm (Đố vui)", "Câu hỏi Đúng/Sai", "Tình huống thảo luận ngắn"])
        
        if st.button("Tạo câu hỏi tương tác", type="secondary"):
            if chu_de_tuong_tac.strip():
                with st.spinner("Đang tạo..."):
                    prompt = f"Tôi đang dạy live bài '{chu_de_tuong_tac}' cho học sinh THCS và lớp đang hơi trầm. Hãy tạo NHANH 1 {loai_tuong_tac} thật thú vị, hài hước hoặc gắn với thực tế để tôi copy thả vào khung chat. Bắt buộc có kèm đáp án."
                    try:
                        st.session_state.live_poll_result = ai_engine.generate_text(prompt)
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
            else:
                st.warning("Vui lòng nhập chủ đề!")
                
        if st.session_state.live_poll_result:
            st.info(st.session_state.live_poll_result)
