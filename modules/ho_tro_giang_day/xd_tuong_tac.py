import streamlit as st
import io
import docx
import PyPDF2

def extract_text_from_file(uploaded_file):
    """Hàm trích xuất văn bản từ các định dạng file phổ biến"""
    text = ""
    try:
        if uploaded_file.name.endswith('.txt'):
            text = uploaded_file.getvalue().decode('utf-8')
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif uploaded_file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            text = "[Thông báo: Đây là file ảnh. Nếu Động cơ AI không hỗ trợ Vision, nó sẽ không thể đọc nội dung ảnh này. Vui lòng chuyển ảnh sang dạng PDF hoặc Text để có kết quả tốt nhất.]"
        else:
            text = "[Định dạng file chưa được hỗ trợ trích xuất văn bản]"
    except Exception as e:
        text = f"[Lỗi khi đọc file: {e}]"
    return text

def render_xd_tuong_tac(ai_engine):
    st.markdown("### 💬 Trợ lý AI Tương tác Trực tiếp & Đọc Tài liệu")
    st.info("💡 Thầy/Cô có thể tải tài liệu lên (PDF, Word, TXT) và chat trực tiếp với AI để hỏi đáp, tóm tắt hoặc yêu cầu phân tích tài liệu đó.")

    # 1. Khởi tạo bộ nhớ Chat (Session State)
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # 2. Khu vực Tải file
    with st.expander("📎 Đính kèm tài liệu (Tùy chọn)", expanded=False):
        uploaded_files = st.file_uploader(
            "Tải lên file (PDF, DOCX, TXT, Ảnh) để AI đọc:", 
            accept_multiple_files=True,
            type=["pdf", "docx", "txt", "png", "jpg", "jpeg"]
        )
        
        file_context = ""
        if uploaded_files:
            st.success(f"Đã tải lên {len(uploaded_files)} file. Đang trích xuất nội dung...")
            for file in uploaded_files:
                extracted = extract_text_from_file(file)
                file_context += f"\n--- Nội dung file: {file.name} ---\n{extracted}\n"
            
            # Cắt bớt nội dung nếu quá dài (tránh lỗi vượt quá token của AI)
            if len(file_context) > 20000:
                file_context = file_context[:20000] + "\n...[Nội dung đã được cắt bớt do quá dài]..."
                st.warning("⚠️ Tài liệu khá dài, AI sẽ chỉ đọc phần nội dung quan trọng nhất.")

    st.markdown("---")

    # 3. Khu vực hiển thị Lịch sử Chat
    chat_container = st.container(height=400)
    with chat_container:
        if not st.session_state.chat_messages:
            st.markdown("<div style='text-align: center; color: gray; padding-top: 50px;'>Hãy đặt câu hỏi hoặc tải file lên để bắt đầu trò chuyện với Trợ lý AI 👋</div>", unsafe_allow_html=True)
            
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 4. Khung nhập liệu Chat (Chat Input) ở dưới cùng
    if prompt := st.chat_input("Nhập tin nhắn hoặc câu hỏi của thầy..."):
        # Lưu câu hỏi của người dùng vào bộ nhớ và hiển thị
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Xây dựng câu lệnh gửi cho AI (Gộp cả nội dung file nếu có)
        full_prompt = prompt
        if file_context.strip():
            full_prompt = f"""Dựa vào các tài liệu được cung cấp dưới đây, hãy trả lời câu hỏi của tôi. Nếu tài liệu không chứa thông tin để trả lời, hãy sử dụng kiến thức sư phạm của bạn.
            
            [TÀI LIỆU ĐÍNH KÈM]:
            {file_context}
            
            [CÂU HỎI CỦA TÔI]:
            {prompt}
            """

        # Xử lý phản hồi từ AI
        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("AI đang suy nghĩ..."):
                    try:
                        response = ai_engine.generate_text(full_prompt)
                        message_placeholder.markdown(response)
                        # Lưu phản hồi vào bộ nhớ
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Lỗi phản hồi: {e}"
                        message_placeholder.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
