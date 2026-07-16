import streamlit as st
from pypdf import PdfReader

# Logic xử lý RAG (Retrieval Augmented Generation) cơ bản
def get_pdf_text(pdf_file):
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def render_rag(ai_engine):
    st.markdown("### 🤖 AI Hỏi - Đáp Theo Tài Liệu (RAG)")
    
    # Khu vực tải tài liệu
    uploaded_file = st.file_uploader("Tải tài liệu PDF để AI học:", type=["pdf"])
    
    # Khởi tạo session state cho RAG
    if "rag_context" not in st.session_state:
        st.session_state.rag_context = ""
    
    # Xử lý file PDF khi upload
    if uploaded_file:
        with st.spinner("⏳ AI đang đọc và nạp tài liệu..."):
            st.session_state.rag_context = get_pdf_text(uploaded_file)
            st.success(f"✅ Đã nạp xong tài liệu: {uploaded_file.name}")

    # Giao diện chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Nhập câu hỏi dựa trên tài liệu đã tải lên..."):
        if not st.session_state.rag_context:
            st.warning("⚠️ Vui lòng tải tài liệu lên trước khi đặt câu hỏi!")
            return

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Prompt đặc chế cho RAG
            full_prompt = f"""
            Dựa trên tài liệu dưới đây, hãy trả lời câu hỏi của người dùng một cách chính xác và sư phạm. 
            Nếu thông tin không có trong tài liệu, hãy trả lời dựa trên kiến thức chung nhưng phải báo trước cho người dùng.

            [TÀI LIỆU]:
            {st.session_state.rag_context[:10000]} 

            [CÂU HỎI]:
            {prompt}
            """
            try:
                response = ai_engine.generate_text(full_prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Lỗi truy vấn AI: {e}")
