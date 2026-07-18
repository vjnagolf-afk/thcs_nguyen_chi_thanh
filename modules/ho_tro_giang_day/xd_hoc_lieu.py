import streamlit as st
import docx
import PyPDF2

# --- HÀM HỖ TRỢ ĐỌC FILE ---
def extract_text_from_file(uploaded_file):
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
    except Exception as e:
        text = f"[Lỗi khi đọc file: {e}]"
    return text

# --- GIAO DIỆN CHÍNH ---
def render_xd_tuong_tac(ai_engine):
    st.markdown("### 📚 Trợ lý Quản lý & Khai thác Học liệu")
    
    # 1. Gom các chế độ nhập liệu vào 1 khối
    che_do = st.radio("Nguồn tài liệu:", ["🔗 Nhập đường link (URL)", "📎 Tải file lên (PDF/Word/TXT)"], horizontal=True)

    file_context = ""
    if che_do == "🔗 Nhập đường link (URL)":
        url = st.text_input("Dán đường link tài liệu web vào đây:")
        if st.button("Lấy nội dung từ link"):
            st.info("Chức năng đang phát triển. Thầy có thể copy nội dung web dán vào box bên dưới.")
    else:
        uploaded_files = st.file_uploader("Tải lên file để AI đọc:", accept_multiple_files=True, type=["pdf", "docx", "txt"])
        if uploaded_files:
            for file in uploaded_files:
                file_context += f"\n--- Nội dung: {file.name} ---\n{extract_text_from_file(file)}\n"
            st.success(f"Đã đọc xong {len(uploaded_files)} file.")

    # 2. Khung chat chung
    if "chat_messages" not in st.session_state: st.session_state.chat_messages = []
    
    chat_container = st.container(height=350)
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]): st.markdown(message["content"])

    if prompt := st.chat_input("Hỏi AI về tài liệu hoặc yêu cầu phân tích..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                full_prompt = f"Tài liệu: {file_context}\n\nCâu hỏi: {prompt}"
                response = ai_engine.generate_text(full_prompt)
                st.markdown(response)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})

def render_camera_cham_bai():
    st.markdown("### 📷 Camera chấm bài")
    st.info("Tính năng này sử dụng Camera để quét bài thi và AI tự động chấm điểm.")
    
    # Placeholder cho tính năng Camera (Thầy sẽ tích hợp sau)
    img_file = st.camera_input("Chụp ảnh bài kiểm tra")
    if img_file:
        st.success("Đã nhận ảnh bài làm. Đang xử lý...")
        # Code gọi AI xử lý ảnh nằm ở đây
