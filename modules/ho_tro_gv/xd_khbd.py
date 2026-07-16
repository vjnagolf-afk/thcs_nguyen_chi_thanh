import streamlit as st
import sys
import io
from pathlib import Path
from loguru import logger
from pypdf import PdfReader

# Thiết lập đường dẫn để import module từ thư mục gốc
sys.path.append(str(Path(__file__).resolve().parents[2]))
from export.export_word import WordExportEngine

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # Khởi tạo session state
    if 'khbd_content' not in st.session_state: st.session_state['khbd_content'] = None
    if 'khbd_meta' not in st.session_state: st.session_state['khbd_meta'] = {}

    # Giao diện nhập liệu
    col1, col2 = st.columns(2)
    ten_bai = col1.text_input("Tên bài dạy / Chủ đề")
    mon_hoc = col2.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học Tự nhiên", "Tiếng Anh", "Tin học", "Công nghệ"])
    
    col3, col4 = st.columns(2)
    lop = col3.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10"])
    hinh_thuc = col4.selectbox("Hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    bam_sat = st.checkbox("Bám sát 100% tài liệu tải lên", value=True)

    # Nút khởi tạo AI
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
                    elif file_tai_len.name.endswith('.txt'):
                        file_context = file_tai_len.read().decode("utf-8")

                prompt = f"Soạn KHBD môn {mon_hoc}, lớp {lop}, bài '{ten_bai}', hình thức {hinh_thuc}. Dựa trên tài liệu: {file_context[:4000]}. Trình bày bằng Markdown chuyên nghiệp."
                
                try:
                    # Truyền model_name chuẩn
                    model_chon = ai_engine.MODELS["flash"] 
                    response = ai_engine.generate_text(prompt, model_name=model_chon)
                    
                    st.session_state['khbd_content'] = response
                    st.session_state['khbd_meta'] = {"ten": ten_bai, "mon": mon_hoc, "lop": lop}
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Lỗi AI: {e}")

    # Hiển thị và Xuất file
    if st.session_state['khbd_content']:
        st.markdown("---")
        st.subheader(f"📄 Kết quả: {st.session_state['khbd_meta'].get('ten')}")
        
        with st.expander("👁️ Xem trước Kế hoạch bài dạy", expanded=True):
            st.markdown(st.session_state['khbd_content'])
        
        if st.button("📥 Tải file Word"):
            try:
                data_export = {
                    "title": st.session_state['khbd_meta'].get('ten'),
                    "content": st.session_state['khbd_content'],
                    "subject": st.session_state['khbd_meta'].get('mon'),
                    "grade": st.session_state['khbd_meta'].get('lop')
                }
                
                # Gọi Engine từ thư mục export
                word_bytes = WordExportEngine.export_to_word(data_export)
                
                st.download_button(
                    label="Tải file về máy",
                    data=word_bytes,
                    file_name=f"KHBD_{st.session_state['khbd_meta'].get('ten')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"Lỗi xuất file: {e}")
                logger.exception("Lỗi xuất Word")
