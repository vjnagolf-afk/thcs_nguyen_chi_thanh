import streamlit as st
import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    """Hàm cào dữ liệu văn bản từ đường link web"""
    try:
        # Thêm Header để giả lập trình duyệt, tránh bị các trang web chặn
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Bóc tách text từ các thẻ tiêu đề và đoạn văn để có nội dung đầy đủ nhất
        text_elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
        content = " ".join([elem.get_text(strip=True) for elem in text_elements])
        
        return content
    except Exception as e:
        return f"Lỗi đọc link: {e}"

def render_xd_hoc_lieu(ai_engine):
    st.markdown("### 📚 Trợ lý Quản lý & Khai thác Học liệu")
    
    # Khởi tạo biến lưu trữ nội dung trong session_state để không bị mất khi thao tác
    if "hoc_lieu_content" not in st.session_state:
        st.session_state.hoc_lieu_content = ""
        
    nguon = st.radio("Nguồn tài liệu:", ["Nhập đường link (URL)", "Tải file (PDF/Word/TXT/Ảnh)"])
    
    st.markdown("---")
    
    if nguon == "Nhập đường link (URL)":
        url = st.text_input("🔗 Dán đường link bài viết / tài liệu web vào đây:")
        if st.button("📥 Lấy nội dung từ link"):
            if url:
                with st.spinner("⏳ Đang trích xuất dữ liệu từ trang web..."):
                    extracted_text = extract_text_from_url(url)
                    
                    if "Lỗi đọc link" in extracted_text:
                        st.error(extracted_text)
                    else:
                        st.session_state.hoc_lieu_content = extracted_text
                        st.success("Đã lấy nội dung thành công!")
            else:
                st.warning("⚠️ Hãy dán link trước khi nhấn nút!")
                
    else:
        files = st.file_uploader("Tải lên tài liệu:", accept_multiple_files=True, type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
        if files:
            st.info("Chức năng đọc file đang được hoàn thiện. Tạm thời AI sẽ dùng nội dung demo.")
            st.session_state.hoc_lieu_content = "Nội dung demo từ file..."
            
    # Phần xử lý AI chỉ hiện ra KHI ĐÃ CÓ NỘI DUNG
    if st.session_state.hoc_lieu_content and not st.session_state.hoc_lieu_content.startswith("Nội dung demo"):
        with st.expander("👁️ Xem trước nội dung gốc đã trích xuất", expanded=False):
            st.text_area("Văn bản thô:", value=st.session_state.hoc_lieu_content, height=200, disabled=True)
            
        st.markdown("#### 🤖 Tóm tắt & Xử lý với AI")
        hanh_dong = st.selectbox("Thầy muốn AI làm gì với tài liệu này?", [
            "Tóm tắt nội dung chính",
            "Trích xuất từ khóa & Định nghĩa",
            "Chuyển đổi thành nội dung bài giảng ngắn",
            "Tạo các câu hỏi trắc nghiệm/thảo luận"
        ])
        
        if st.button("🚀 BẮT ĐẦU XỬ LÝ", type="primary"):
            with st.spinner(f"⏳ AI đang {hanh_dong.lower()}..."):
                # Giới hạn số lượng ký tự gửi đi (khoảng 15000 ký tự) để tránh lỗi vượt quá giới hạn token của AI
                safe_content = st.session_state.hoc_lieu_content[:15000]
                
                # Cấu trúc câu lệnh (prompt) tối ưu cho mục đích sư phạm
                prompt = f"Thực hiện yêu cầu: '{hanh_dong}' dựa trên nội dung tài liệu sau đây. Hãy trình bày rõ ràng, khoa học và phù hợp với môi trường sư phạm:\n\n{safe_content}"
                
                try:
                    res = ai_engine.generate_text(prompt)
                    st.success("Hoàn thành!")
                    st.markdown("### 📝 Kết quả:")
                    st.markdown(res)
                except Exception as e:
                    st.error(f"Lỗi khi gọi AI: {e}")
