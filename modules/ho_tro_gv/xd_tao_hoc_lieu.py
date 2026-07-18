import streamlit as st

def render_tao_hoc_lieu(ai_engine):
    st.markdown("### 📚 Trợ lý Tạo học liệu Đa năng")
    st.caption("Hỗ trợ sinh tự động 9 loại học liệu khác nhau chỉ từ một chủ đề/bài học cụ thể của cấp THCS.")

    # 1. Nhập liệu đầu vào
    col1, col2 = st.columns([3, 1])
    with col1:
        chu_de = st.text_input("Nhập chủ đề bài học:", placeholder="Ví dụ: Định luật Newton, Cấu tạo Tế bào, Vi điều khiển cơ bản...")
    with col2:
        st.write("") # Căn chỉnh nút
        btn_tao = st.button("🪄 Sinh Học Liệu", type="primary", use_container_width=True)

    st.divider()

    # 2. Xử lý và Hiển thị
    if btn_tao:
        if chu_de.strip():
            with st.spinner(f"AI đang biên soạn toàn bộ học liệu cho chủ đề: {chu_de}..."):
                # Mô phỏng prompt tổng hợp
                prompt = f"Tôi đang dạy bài '{chu_de}' cho học sinh cấp THCS. Hãy viết cho tôi phần 'Tóm tắt bài học' thật súc tích, dễ hiểu, phù hợp với học sinh."
                try:
                    tom_tat = ai_engine.generate_text(prompt)
                    
                    st.success("Tạo học liệu thành công! Thầy hãy chuyển qua các thẻ bên dưới để xem.")
                    
                    # 9 Tabs hiển thị 9 loại học liệu theo đúng yêu cầu
                    tabs = st.tabs([
                        "📘 Tóm tắt", "📝 Phiếu HT", "🎯 Trắc nghiệm", 
                        "✍️ Tự luận", "🧪 Phiếu TN", "📊 Rubric", 
                        "🎮 Trò chơi", "🎞️ Kịch bản", "🖥️ Slide"
                    ])
                    
                    with tabs[0]: 
                        st.markdown("#### 📘 Tóm tắt bài học")
                        st.write(tom_tat)
                    
                    with tabs[1]: 
                        st.markdown("#### 📝 Phiếu học tập")
                        st.info("Nội dung phiếu bài tập điền khuyết, ghép nối, thẻ từ vựng...")
                        
                    with tabs[2]: 
                        st.markdown("#### 🎯 Câu hỏi trắc nghiệm")
                        st.info("Hệ thống câu hỏi MCQ 4 đáp án (có đánh dấu đáp án đúng).")
                        
                    with tabs[3]: 
                        st.markdown("#### ✍️ Câu hỏi tự luận")
                        st.info("Câu hỏi tư duy bậc cao, vận dụng kiến thức giải quyết vấn đề thực tiễn.")
                        
                    with tabs[4]: 
                        st.markdown("#### 🧪 Phiếu thí nghiệm")
                        st.info("Bảng hướng dẫn các bước thao tác, thiết bị cần thiết và bảng ghi nhận số liệu...")
                        
                    with tabs[5]: 
                        st.markdown("#### 📊 Rubric Đánh giá")
                        st.info("Bảng tiêu chí chấm điểm (Mức độ: Yếu - Trung bình - Khá - Tốt) cho dự án/bài tập.")
                        
                    with tabs[6]: 
                        st.markdown("#### 🎮 Trò chơi")
                        st.info("Ý tưởng trò chơi khởi động (Warm-up) hoặc đóng vai trải nghiệm.")
                        
                    with tabs[7]: 
                        st.markdown("#### 🎞️ Kịch bản video")
                        st.info("Dàn ý kịch bản (Hình ảnh minh họa + Lời bình) để thầy dựng video TikTok/Youtube bài giảng.")
                        
                    with tabs[8]: 
                        st.markdown("#### 🖥️ Slide bài giảng")
                        st.info("Bố cục chữ và ý tưởng hình ảnh đề xuất cho 5-7 slide trọng tâm.")

                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
        else:
            st.warning("Thầy vui lòng nhập chủ đề bài học trước nhé!")
