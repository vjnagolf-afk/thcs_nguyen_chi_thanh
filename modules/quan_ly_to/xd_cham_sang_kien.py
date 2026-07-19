import streamlit as st
import PyPDF2
from docx import Document
from PIL import Image
import io

# 1. HÀM XỬ LÝ FILE (TEXT & IMAGE)
def extract_text_from_file(uploaded_file):
    text = ""
    # Xử lý PDF
    if uploaded_file.name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages: text += page.extract_text() + "\n"
    # Xử lý Word
    elif uploaded_file.name.endswith('.docx'):
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
    return text

def render_cham_sang_kien(ai_engine):
    st.markdown("### 🔍 Chấm & Góp ý Sáng kiến Kinh nghiệm")
    
    # Khu vực tải lên: Hỗ trợ cả file tài liệu và ảnh chụp
    uploaded_files = st.file_uploader("Tải lên bản sáng kiến (PDF, DOCX hoặc Ảnh chụp trang):", 
                                     accept_multiple_files=True, type=["pdf", "docx", "jpg", "png"])
    
    if st.button("⚖️ BẮT ĐẦU CHẤM ĐIỂM & PHÂN TÍCH"):
        if not uploaded_files:
            st.warning("⚠️ Vui lòng tải file sáng kiến lên!")
            return

        with st.spinner("AI đang xử lý nội dung & phân tích chuyên sâu..."):
            full_content = []
            image_payload = []
            
            # Xử lý từng file
            for file in uploaded_files:
                if file.type.startswith('image'):
                    image_payload.append(Image.open(file))
                else:
                    full_content.append(extract_text_from_file(file))
            
            combined_text = "\n".join(full_content)
            
            # 2. PROMPT CHUYÊN GIA (NLP CHUYÊN SÂU)
            prompt = f"""
            Bạn là chuyên gia hội đồng thẩm định sáng kiến kinh nghiệm cấp cơ sở. Hãy phân tích sáng kiến sau:
            Nội dung: {combined_text}
            
            YÊU CẦU PHÂN TÍCH:
            1. Chấm điểm theo thang Rubric: Tính mới (3đ), Tính khả thi (3đ), Hiệu quả (2đ), Phạm vi ảnh hưởng (2đ).
            2. Phát hiện logic: Đối chiếu các giải pháp với thực tế giáo dục.
            3. Kiểm tra tính nguyên gốc: Đưa ra nhận xét về mức độ văn phong tự nhiên.
            4. Bảng nhận xét: Tổng hợp điểm mạnh/điểm yếu chi tiết.
            """
            
            # 3. GỌI AI
            try:
                # Phân tích nội dung + hình ảnh (nếu có ảnh chụp trang)
                response = ai_engine.generate_content([prompt] + image_payload)
                st.session_state['sk_result'] = response.text
                st.markdown(response.text)
            except Exception as e:
                st.error(f"❌ Lỗi xử lý: {str(e)}")

    # 4. XUẤT BÁO CÁO TỰ ĐỘNG
    if 'sk_result' in st.session_state:
        st.download_button(
            label="📄 Xuất kết quả ra File (Markdown)",
            data=st.session_state['sk_result'],
            file_name="Bao_cao_cham_sk.md",
            mime="text/markdown"
        )
        
    # GỢI Ý TÍCH HỢP NGOÀI
    with st.expander("🛡️ Tiện ích kiểm tra nâng cao"):
        st.info("Chức năng kiểm tra đạo văn và AI Detector yêu cầu API Key từ Copyscape/Originality.ai")
        st.write("Thầy có thể liên hệ đơn vị cung cấp API để tích hợp vào khối lệnh này.")
