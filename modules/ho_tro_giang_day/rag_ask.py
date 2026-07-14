import streamlit as st
from utils.ai_engine import AIEngine
import PyPDF2 # Thầy nhớ cài thêm thư viện này nhé

def render(ai_engine):
    st.markdown("### 🤖 AI Hỏi - Đáp Theo Tài Liệu (RAG)")
    
    # 1. Tải tài liệu lên
    uploaded_file = st.file_uploader("Tải tài liệu PDF để AI học:", type=["pdf"])
    
    if uploaded_file:
        # Xử lý trích xuất văn bản (đơn giản hóa cho MVP)
        reader = PyPDF2.PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() for page in reader.pages])
        st.success("Đã nạp tài liệu thành công!")
        
        # 2. Khung chat
        query = st.text_input("Thầy/cô muốn hỏi gì về tài liệu này?")
        
        if query and st.button("Hỏi AI"):
            prompt = f"Dựa vào tài liệu sau đây, hãy trả lời câu hỏi của tôi.\n\nTài liệu: {text[:5000]}...\n\nCâu hỏi: {query}"
            
            with st.spinner("AI đang suy nghĩ..."):
                response = ai_engine.ask(prompt)
                st.markdown("### Câu trả lời:")
                st.write(response)

# Để tương thích với app.py, em dùng hàm render
def render_rag(ai_engine):
    render(ai_engine)
