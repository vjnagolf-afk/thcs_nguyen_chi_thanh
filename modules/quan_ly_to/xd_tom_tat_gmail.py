import streamlit as st

def render_tom_tat_gmail(ai_engine):
    st.markdown("### 📧 Đọc và Tóm tắt Văn bản / Email")
    st.caption("Trợ lý AI giúp đọc các email/công văn dài từ nhà trường, Phòng/Sở GD&ĐT và trích xuất lại các ý chính, lịch công tác quan trọng.")

    # --- Chia làm 2 Tab (Dán tay và Kết nối sau này) ---
    tab_nhap, tab_api = st.tabs(["✍️ Xử lý Email thủ công", "🔗 Kết nối tài khoản Gmail (Sắp ra mắt)"])

    with tab_nhap:
        col_input, col_options = st.columns([2, 1])
        
        with col_input:
            email_content = st.text_area("Dán nội dung Email / Công văn vào đây:", height=250, placeholder="Kính gửi các đồng chí Tổ trưởng...\nNội dung công việc tuần tới như sau...")
            
        with col_options:
            st.markdown("**Mục tiêu phân tích:**")
            yeu_cau = st.radio("AI sẽ tập trung tìm kiếm:", [
                "📝 Tóm tắt gọn gàng ý chính",
                "⏰ Trích xuất Hạn chót (Deadlines)",
                "✅ Liệt kê công việc cần làm",
                "📊 Phân tích yêu cầu chuyên môn"
            ])
            
            st.markdown("<br>", unsafe_allow_html=True)
            btn_tom_tat = st.button("🪄 Phân tích bằng AI", type="primary", use_container_width=True)

        # Xử lý khi bấm nút Tóm tắt
        if btn_tom_tat:
            if not email_content.strip():
                st.warning("⚠️ Thầy vui lòng dán nội dung Email hoặc công văn vào ô trống trước nhé!")
            else:
                with st.spinner("AI đang đọc văn bản và nhặt ra các thông tin quan trọng..."):
                    prompt = f"""
                    Bạn là Trợ lý cá nhân của Tổ trưởng chuyên môn trường THCS. Hãy đọc nội dung Email/Công văn hành chính dưới đây và thực hiện yêu cầu: {yeu_cau}.
                    
                    NGUYÊN TẮC BẮT BUỘC:
                    1. Trình bày cực kỳ ngắn gọn, rõ ràng bằng gạch đầu dòng (bullet points).
                    2. Bôi đậm (bold) các mốc thời gian, hạn chót và người chịu trách nhiệm (nếu có).
                    3. Bỏ qua các câu chào hỏi, kính gửi rườm rà. Đi thẳng vào việc.
                    4. Sử dụng văn phong hành chính chuyên nghiệp.

                    NỘI DUNG VĂN BẢN:
                    '''{email_content}'''
                    """
                    try:
                        summary = ai_engine.generate_text(prompt)
                        st.success("✅ Đã xử lý xong văn bản!")
                        
                        st.markdown("#### 📌 Kết quả Phân tích:")
                        # Đặt kết quả vào một khung container cho đẹp
                        with st.container(border=True):
                            st.markdown(summary)
                            
                        # Nút copy nhanh
                        st.download_button(
                            label="⬇️ Lưu kết quả về máy (.txt)",
                            data=summary,
                            file_name="TomTat_Email.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Lỗi hệ thống hoặc lỗi kết nối AI: {e}")

    with tab_api:
        st.info("💡 Tính năng tự động quét hộp thư đến (Inbox) đòi hỏi cấp quyền API (OAuth2) từ Google Workspace. Chúng ta sẽ phát triển tính năng này sau khi ứng dụng đã được BGH nhà trường duyệt đưa vào sử dụng chính thức.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Gmail2020.logo.png/512px-Gmail2020.logo.png", width=100)
        st.write("Sắp tích hợp...")
