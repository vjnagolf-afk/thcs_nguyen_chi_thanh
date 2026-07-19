import streamlit as st
import PyPDF2
from docx import Document

def extract_text_from_file(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif uploaded_file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
    return text

def render_cham_sang_kien(ai_engine):
    st.markdown("### 🔍 Chấm & Góp ý Sáng kiến (Hỗ trợ file)")
    
    # 1. Khu vực tải file
    uploaded_file = st.file_uploader("Tải lên bản sáng kiến (PDF hoặc DOCX):", type=["pdf", "docx"])
    
    # 2. Hoặc nhập tay
    van_ban_input = st.text_area("Hoặc dán nội dung sáng kiến:", height=200)
    
    if st.button("⚖️ BẮT ĐẦU CHẤM ĐIỂM"):
        content = ""
        if uploaded_file:
            with st.spinner("Đang đọc nội dung file..."):
                content = extract_text_from_file(uploaded_file)
        else:
            content = van_ban_input

        if not content.strip():
            st.warning("⚠️ Vui lòng tải file hoặc dán nội dung sáng kiến!")
            return
            
        # 3. Gọi AI phân tích với Prompt chuyên sâu
        with st.spinner("AI đang chấm điểm và phân tích..."):
            prompt = f"""Bạn là chuyên gia giáo dục hội đồng chấm sáng kiến kinh nghiệm.
            Hãy phân tích bản sáng kiến dưới đây dựa trên các tiêu chí: 
            1. Tính mới, 2. Tính khả thi, 3. Hiệu quả áp dụng, 4. Bố cục sư phạm.
            
            Sau đó, xuất ra bảng điểm Rubrics và gợi ý chỉnh sửa chi tiết.
            
            Nội dung: {content}"""
            
            try:
                response = ai_engine.generate_text(prompt)
                st.markdown("---")
                st.markdown(response)
                
                # Lưu vào session để xuất file sau
                st.session_state['last_result'] = response
            except Exception as e:
                st.error(f"❌ Lỗi khi gọi AI: {str(e)}")

    # 4. Nút xuất kết quả
    if 'last_result' in st.session_state:
        st.download_button(
            label="💾 Tải kết quả chấm điểm (TXT)",
            data=st.session_state['last_result'],
            file_name="ket_qua_cham_sk.txt",
            mime="text/plain"
        )
