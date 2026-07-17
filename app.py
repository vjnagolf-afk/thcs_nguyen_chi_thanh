import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
# Lưu ý: Cần cài thêm 'pytesseract' và 'pdf2image' nếu muốn OCR ảnh/PDF chuyên sâu
# Hiện tại em dùng thư viện xử lý cơ bản để thầy test trước

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return " ".join([p.text for p in soup.find_all('p')])
    except Exception as e:
        return f"Lỗi đọc link: {e}"

def render_xd_hoc_lieu(ai_engine):
    st.markdown("### 📚 Trợ lý Quản lý & Khai thác Học liệu (Nâng cấp)")
    
    # 1. Chọn nguồn dữ liệu
    nguon = st.radio("Nguồn tài liệu:", ["Tải file (PDF/Word/TXT/Ảnh)", "Nhập đường link (URL)"])
    
    content = ""
    if nguon == "Tải file (PDF/Word/TXT/Ảnh)":
        files = st.file_uploader("Tải lên:", accept_multiple_files=True, type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
        if files:
            for file in files:
                # Thầy tích hợp hàm extract_text_from_file đã có vào đây
                content += f"\n[Nội dung từ {file.name}]: ..." 
    else:
        url = st.text_input("Dán đường link tài liệu:")
        if url:
            with st.spinner("⏳ Đang lấy nội dung từ link..."):
                content = extract_text_from_url(url)
    
    # 2. Thao tác
    hanh_dong = st.selectbox("Chọn thao tác:", [
        "Tóm tắt nội dung chính",
        "Trích xuất từ khóa & Định nghĩa",
        "Chuyển đổi thành nội dung bài giảng ngắn",
        "Tạo các câu hỏi thảo luận"
    ])
    
    if st.button("🚀 XỬ LÝ HỌC LIỆU", type="primary"):
        if not content:
            st.error("⚠️ Vui lòng cung cấp tài liệu hoặc link!")
        else:
            with st.spinner("⏳ AI đang xử lý..."):
                prompt = f"Thực hiện '{hanh_dong}' cho nội dung sau:\n{content[:10000]}"
                try:
                    res = ai_engine.generate_text(prompt)
                    st.markdown("---")
                    st.markdown(res)
                except Exception as e:
                    st.error(f"Lỗi: {e}")
