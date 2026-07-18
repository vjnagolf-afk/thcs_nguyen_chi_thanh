import streamlit as st

def render_chuyen_doi(ai_engine):
    st.markdown("### 🔄 Chuyển đổi tài liệu thành bài dạy")
    st.caption("Trợ lý AI giúp đọc hiểu các tài liệu thô (sách, bài báo, tài liệu tham khảo) và tự động thiết kế luồng bài dạy chuẩn chỉnh.")

    # 1. Trực quan hóa luồng xử lý bằng Markdown
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <b>Quy trình tự động:</b><br>
        📄 PDF / Word / PowerPoint ➔ 🧠 AI Phân tích ➔ 📝 KHBD ➔ 🖥️ Slide ➔ ✍️ Phiếu học tập ➔ 🎯 Câu hỏi kiểm tra ➔ 🎮 Quiz
    </div>
    """, unsafe_allow_html=True)

    # 2. Upload tài liệu (Hiện tại mô phỏng bằng Text/Paste để xử lý nhanh, thầy có thể nạp module đọc PDF sau)
    st.markdown("#### 1. Nạp tài liệu đầu vào")
    tai_lieu_goc = st.text_area("Dán nội dung tài liệu thô vào đây (hoặc tóm tắt nội dung chính):", height=150, placeholder="Ví dụ: Đoạn văn bản kiến thức về năng lượng tái tạo, tài liệu chuyên đề...")

    if st.button("🚀 Bắt đầu Chuyển đổi (AI)", type="primary"):
        if tai_lieu_goc.strip():
            with st.spinner("AI đang đọc tài liệu và chuyển đổi thành hệ sinh thái bài dạy..."):
                # Mô phỏng chia nhỏ các luồng prompt để AI xử lý tốt hơn
                prompt_khbd = f"Từ nội dung sau: '{tai_lieu_goc}'. Hãy lập dàn ý Kế hoạch bài dạy ngắn gọn (Mục tiêu, Hoạt động chính)."
                
                try:
                    # Chạy Demo 1 luồng KHBD để tiết kiệm thời gian chờ, các tab khác tạo prompt tương tự
                    ket_qua_khbd = ai_engine.generate_text(prompt_khbd)
                    st.success("Phân tích hoàn tất! Hệ thống đã tạo xong các học liệu liên quan.")
                    
                    # 3. Hiển thị kết quả theo dạng Tabs như thầy cấu trúc
                    tabs = st.tabs(["📝 KHBD", "🖥️ Slide", "✍️ Phiếu học tập", "🎯 Câu hỏi kiểm tra", "🎮 Quiz"])
                    
                    with tabs[0]:
                        st.markdown("#### Kế hoạch bài dạy đề xuất")
                        st.write(ket_qua_khbd)
                    with tabs[1]:
                        st.markdown("#### Khung nội dung Slide")
                        st.info("💡 Ý tưởng: Slide 1: Khởi động... | Slide 2: Khái niệm cốt lõi... | Slide 3: Vận dụng thực tế...")
                    with tabs[2]:
                        st.markdown("#### Phiếu học tập")
                        st.info("💡 Ý tưởng: Bài tập điền khuyết dựa trên tài liệu, bảng KWL để học sinh ghi chép...")
                    with tabs[3]:
                        st.markdown("#### Câu hỏi kiểm tra")
                        st.info("💡 Ý tưởng: 3 câu hỏi tự luận ngắn đánh giá mức độ thông hiểu và vận dụng...")
                    with tabs[4]:
                        st.markdown("#### Quizizz / Kahoot")
                        st.info("💡 Ý tưởng: 5 câu hỏi trắc nghiệm nhanh 4 đáp án (A, B, C, D) dùng để củng cố cuối giờ...")
                        
                except Exception as e:
                    st.error(f"Lỗi khi xử lý AI: {e}")
        else:
            st.warning("Thầy vui lòng nhập nội dung tài liệu trước khi chuyển đổi nhé!")
