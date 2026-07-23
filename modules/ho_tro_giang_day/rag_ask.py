# -*- coding: utf-8 -*-
import streamlit as st

def render_rag_ask(ai_engine=None):
    st.markdown("### 📚 Trợ lý Chat & Hỏi đáp trên Tài liệu (RAG Ask)")
    st.caption("Tải lên sách giáo khoa, tài liệu bài giảng. AI sẽ đọc và trả lời mọi câu hỏi của học sinh dựa trên nội dung tài liệu đó.")

    if "rag_chat_history" not in st.session_state:
        st.session_state.rag_chat_history = [{"role": "assistant", "content": "Chào bạn! Hãy tải tài liệu lên và đặt câu hỏi nhé."}]
    
    if "rag_document" not in st.session_state:
        st.session_state.rag_document = ""

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### 📤 Nạp dữ liệu")
        uploaded_file = st.file_uploader("Tải tài liệu (TXT, Markdown)", type=["txt", "md"])
        if uploaded_file:
            try:
                text = uploaded_file.read().decode("utf-8")
                st.session_state.rag_document = text[:50000] # Giới hạn context
                st.success("✅ Đã nạp tài liệu vào bộ nhớ AI!")
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")
                
        if st.button("🗑️ Xóa bộ nhớ", use_container_width=True):
            st.session_state.rag_chat_history = [{"role": "assistant", "content": "Đã xóa bộ nhớ. Hãy tải tài liệu mới!"}]
            st.session_state.rag_document = ""
            st.rerun()

    with col2:
        st.markdown("#### 💬 Khung Chatbot")
        chat_container = st.container(height=400)
        
        user_query = st.chat_input("Hỏi AI về nội dung trong tài liệu...")
        
        if user_query:
            st.session_state.rag_chat_history.append({"role": "user", "content": user_query})
            
            with chat_container:
                for msg in st.session_state.rag_chat_history:
                    st.chat_message(msg["role"]).write(msg["content"])
                
                with st.chat_message("assistant"):
                    with st.spinner("AI đang tìm kiếm câu trả lời..."):
                        if not ai_engine:
                            st.error("Chưa kết nối AI Engine.")
                        else:
                            # Prompt kết hợp RAG cơ bản
                            context = st.session_state.rag_document
                            if context:
                                prompt = f"Dựa vào tài liệu sau:\n\n{context}\n\nHãy trả lời câu hỏi: {user_query}\nNếu thông tin không có trong tài liệu, hãy nói rõ là tài liệu không đề cập."
                            else:
                                prompt = f"Trả lời câu hỏi sau một cách ngắn gọn: {user_query}"
                                
                            try:
                                response = ai_engine.generate_text(prompt)
                                st.write(response)
                                st.session_state.rag_chat_history.append({"role": "assistant", "content": response})
                            except Exception as e:
                                st.error(f"Lỗi AI: {e}")
        else:
            with chat_container:
                for msg in st.session_state.rag_chat_history:
                    st.chat_message(msg["role"]).write(msg["content"])
