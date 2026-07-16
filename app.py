import google.generativeai as genai
import streamlit as st

def test_available_models():
    # Sử dụng Key từ session state để kiểm tra đúng quyền của người dùng hiện tại
    api_key = st.session_state.get("user_api_key")
    if not api_key:
        return "Vui lòng nhập API Key trước!"
    
    genai.configure(api_key=api_key)
    available_models = []
    
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            available_models.append(m.name)
            
    return available_models

# Thầy có thể gọi hàm này để in ra màn hình:
if st.button("Kiểm tra Model khả dụng"):
    st.write(test_available_models())
