# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_sinh_video(ai_engine=None):
    st.markdown("### 🎬 Trợ lý Kịch bản & Sinh Video Giáo dục")
    st.caption("AI hỗ trợ viết kịch bản phân cảnh chi tiết (Script) và câu lệnh (Prompt) tạo ảnh/video cho các công cụ AI Text-to-Video.")

    with st.container(border=True):
        col_info, col_setting = st.columns([1, 1])
        
        with col_info:
            chu_de_video = st.text_input("Chủ đề Video:", placeholder="VD: Cấu tạo Trái Đất, Sự hình thành lỗ đen...")
            đoi_tuong = st.selectbox("Khán giả mục tiêu:", ["Học sinh Tiểu học (Vui nhộn, đơn giản)", "Học sinh THCS (Trực quan, logic)", "Học sinh THPT (Chuyên sâu, học thuật)"])
        
        with col_setting:
            thoi_luong = st.selectbox("Thời lượng dự kiến:", ["Dưới 1 phút (Short/Reel/TikTok)", "1 - 3 phút", "3 - 5 phút"])
            phong_cach = st.selectbox("Phong cách Video:", ["Hoạt hình (Animation/2D)", "Tài liệu khoa học (Documentary)", "Bảng trắng giảng bài (Whiteboard)"])
            
        noi_dung_chinh = st.text_area("Các ý chính bắt buộc phải có trong video:", height=100, placeholder="1. Lớp vỏ, 2. Lớp Manti, 3. Lõi...")
        
        btn_tao = st.button("🎥 Lên kịch bản Video", type="primary", use_container_width=True)

    if btn_tao:
        if not chu_de_video.strip():
            st.warning("⚠️ Vui lòng nhập chủ đề video.")
        else:
            with st.spinner("AI đang xây dựng phân cảnh và viết kịch bản lời thoại..."):
                prompt = f"""
                Bạn là một Đạo diễn Video Giáo dục và Người viết kịch bản chuyên nghiệp.
                Hãy viết một kịch bản chi tiết để sản xuất video học tập với các thông số:
                - Chủ đề: {chu_de_video}
                - Khán giả: {đoi_tuong}
                - Thời lượng: {thoi_luong}
                - Phong cách: {phong_cach}
                - Nội dung bắt buộc: {noi_dung_chinh}
                
                YÊU CẦU TRÌNH BÀY (Dạng Bảng Markdown hoặc Cấu trúc Phân cảnh):
                Với mỗi Cảnh (Scene), phải nêu rõ 3 yếu tố:
                1. Visual (Hình ảnh hiển thị/Chuyển động trên màn hình)
                2. Audio/Voiceover (Lời thoại của MC)
                3. Prompt tạo ảnh/video (Câu lệnh tiếng Anh để copy ném vào các công cụ AI tạo video).
                """
                
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown("#### 🎞️ Kịch bản Video Chi tiết")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
