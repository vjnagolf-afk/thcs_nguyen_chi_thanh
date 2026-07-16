import streamlit as st
from docxtpl import DocxTemplate
from pathlib import Path
from loguru import logger
import io
import os
from pypdf import PdfReader

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # 1. GIAO DIỆN NHẬP LIỆU
    col1, col2 = st.columns(2)
    ten_bai = col1.text_input("Tên bài dạy / Chủ đề")
    mon_hoc = col2.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học Tự nhiên", "Tiếng Anh", "Tin học", "Công nghệ"])
    
    col3, col4 = st.columns(2)
    lop = col3.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10"])
    hinh_thuc = col4.selectbox("Hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    bam_sat = st.checkbox("Bám sát 100% tài liệu tải lên", value=True)
    
    # 2. XỬ LÝ TIẾN TRÌNH AI
    if st.button("🚀 KHỞI TẠO TIẾN TRÌNH KẾ HOẠCH BÀI DẠY", type="primary", use_container_width=True):
        if not ten_bai.strip():
            st.warning("⚠️ Vui lòng điền 'Tên bài học'")
        else:
            with st.spinner("⏳ Trợ lý AI đang thiết kế giáo án..."):
                file_context = ""
                if bam_sat and file_tai_len:
                    if file_tai_len.name.endswith('.pdf'):
                        reader = PdfReader(file_tai_len)
                        for page in reader.pages:
                            txt = page.extract_text()
                            if txt: file_context += txt + "\n"
                            if len(file_context) > 4000: break
                    elif file_tai_len.name.endswith('.txt'):
                        file_context = file_tai_len.read().decode("utf-8")[:4000]

                prompt = f"Soạn KHBD môn {mon_hoc}, lớp {lop}, bài '{ten_bai}', hình thức {hinh_thuc}. Dựa trên tài liệu: {file_context}. Trình bày bằng Markdown rõ ràng."
                
                try:
                    # Gọi AI và lưu kết quả vào session_state để hiển thị
                    response = ai_engine.generate_text(prompt)
                    st.session_state['khbd_content'] = response
                    st.session_state['khbd_meta'] = {"ten": ten_bai, "mon": mon_hoc}
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Lỗi AI: {e}")

    # 3. HIỂN THỊ VÀ XUẤT FILE
    if 'khbd_content' in st.session_state:
        st.markdown("---")
        st.subheader(f"📄 Kết quả: {st.session_state['khbd_meta']['ten']}")
        
        # Xem trước
        with st.expander("👁️ Xem trước Kế hoạch bài dạy", expanded=True):
            st.markdown(st.session_state['khbd_content'])
        
        # Nút Xuất file (Sử dụng đường dẫn Pathlib an toàn)
        if st.button("📥 Tải file Word"):
            BASE_DIR = Path(__file__).resolve().parents[2]
            template_path = BASE_DIR / "templates" / "KHBD_Mau.docx"
            
            try:
                doc = DocxTemplate(str(template_path))
                # Gán dữ liệu vào biến nội dung (Key này phải khớp với biến trong file .docx của thầy)
                doc.render({"NOI_DUNG_GIAO_AN": st.session_state['khbd_content']})
                
                bio = io.BytesIO()
                doc.save(bio)
                st.download_button("Tải file về máy", data=bio.getvalue(), file_name=f"KHBD_{st.session_state['khbd_meta']['ten']}.docx")
            except Exception as e:
                st.error(f"Lỗi xuất file: {e}")
