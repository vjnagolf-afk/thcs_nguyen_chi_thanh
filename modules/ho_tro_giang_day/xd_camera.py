import streamlit as st
import google.generativeai as genai
from PIL import Image
def render_camera_module():
    # 1. Cấu hình bảo mật từ Secrets (Trái tim bảo mật của dự án)
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("🚨 Chưa cấu hình GOOGLE_API_KEY trong Secrets!")
        return
    
    # 2. Giao diện người dùng
    st.markdown("### 📷 Camera chấm bài")
    
    col_img, col_key = st.columns([1, 1])
    
    with col_img:
        input_method = st.radio("Nguồn ảnh bài làm:", ["📷 Chụp từ Camera", "📂 Tải từ máy"], horizontal=True)
        image_data = None
        if input_method == "📷 Chụp từ Camera":
            img_file = st.camera_input("Chụp bài làm của học sinh")
            if img_file: image_data = Image.open(img_file)
        else:
            uploaded_file = st.file_uploader("Tải ảnh bài làm (JPG, PNG)", type=['jpg', 'jpeg', 'png'])
            if uploaded_file: image_data = Image.open(uploaded_file)
            
    with col_key:
        loai_bai = st.selectbox("Phân loại bài kiểm tra", [
            "Trắc nghiệm khách quan (MCQ)", "Tự luận ngắn", "Toán học / Tự nhiên", "Ngữ văn"
        ])
        dap_an = st.text_area("Nhập Đáp án chuẩn hoặc Rubric:", height=200)

    # 3. Xử lý logic chấm điểm (Kết nối AI Vision)
    if st.button("🤖 AI KÍCH HOẠT QUÉT & CHẤM ĐIỂM", type="primary", use_container_width=True):
        if not image_data or not dap_an.strip():
            st.warning("⚠️ Vui lòng cung cấp cả ảnh bài làm và đáp án!")
            return
            
        try:
            # Sử dụng key từ st.secrets (Đúng cấu trúc dự án)
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""Bạn là Giám khảo chấm thi. Hãy phân tích bài làm của học sinh theo loại: {loai_bai}. 
            Đáp án chuẩn: {dap_an}. Trình bày chi tiết lỗi sai và tổng hợp điểm số (thang 10)."""
            
            with st.spinner("AI đang quét ảnh và chấm điểm..."):
                response = model.generate_content([prompt, image_data])
                st.session_state['current_vision_grading'] = response.text
                st.rerun() # Tự động làm mới để hiển thị kết quả
        except Exception as e:
            st.error(f"❌ Lỗi hệ thống: {str(e)}")

    # 4. Hiển thị kết quả
    if 'current_vision_grading' in st.session_state:
        with st.expander("✅ KẾT QUẢ CHẤM BÀI CHI TIẾT", expanded=True):
            st.markdown(st.session_state['current_vision_grading'])
