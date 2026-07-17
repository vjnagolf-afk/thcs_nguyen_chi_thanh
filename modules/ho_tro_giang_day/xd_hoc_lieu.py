import streamlit as st
from pathlib import Path

def render_xd_hoc_lieu(ai_engine):
    st.markdown("### 📚 Trợ lý Quản lý & Khai thác Học liệu")
    
    st.info("💡 Tải lên tài liệu (PDF/DOCX) để AI giúp tóm tắt, trích xuất từ khóa, hoặc chuyển đổi nội dung thành bài giảng ngắn.")
    
    uploaded_file = st.file_uploader("Tải tài liệu học liệu:", type=["pdf", "docx", "txt"])
    
    hanh_dong = st.selectbox("Chọn thao tác:", [
        "Tóm tắt nội dung chính",
        "Trích xuất từ khóa & Định nghĩa",
        "Chuyển đổi thành nội dung bài giảng ngắn",
        "Tạo các câu hỏi thảo luận"
    ])
    
    if st.button("🚀 XỬ LÝ HỌC LIỆU", type="primary"):
        if not uploaded_file:
            st.error("⚠️ Vui lòng tải tài liệu lên!")
        else:
            with st.spinner("⏳ AI đang xử lý học liệu..."):
                # Giả định có hàm extract_text_from_file dùng chung
                content = "Nội dung từ tài liệu..." 
                
                prompt = f"""
                Bạn là trợ lý học liệu. Hãy thực hiện thao tác: {hanh_dong}
                Dựa trên nội dung sau: {content}
                
                Yêu cầu: Trình bày rõ ràng, sư phạm, sử dụng Markdown.
                """
                try:
                    res = ai_engine.generate_text(prompt)
                    st.markdown("---")
                    st.markdown(res)
                except Exception as e:
                    st.error(f"Lỗi: {e}")
