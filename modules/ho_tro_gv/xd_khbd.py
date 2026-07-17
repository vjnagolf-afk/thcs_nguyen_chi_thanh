import streamlit as st
import sys
from pathlib import Path
from pypdf import PdfReader

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ - Chuẩn 5512)")

    ds_mon = [
        "Ngữ văn", "Toán", "Ngoại ngữ", "Giáo dục công dân", "Lịch sử và Địa lý", 
        "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", "Công nghệ", 
        "Tin học", "Giáo dục thể chất", "Nghệ thuật", "Giáo dục địa phương", 
        "Hoạt động trải nghiệm, hướng nghiệp"
    ]

    col1, col2, col3 = st.columns([1, 1, 1])
    mon_hoc = col1.selectbox("Môn học", ds_mon)
    lop = col2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    # Chỉ còn 1 tùy chọn duy nhất
    hinh_thuc = col3.selectbox("Chọn hình thức", ["KHBD chi tiết (Chuẩn 5512)"])
    
    so_tiet = st.number_input("Số tiết", min_value=1, max_value=20, value=2)
    ten_bai_hoc = st.text_input("Tên chủ đề / Tên bài học")
    
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=True)
    yeu_cau = st.text_area("Yêu cầu bổ sung (Ví dụ: Lồng ghép Năng lực số, tích hợp AI...)")
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    
    c1, c2 = st.columns(2)
    if c1.button("🚀 KHỞI TẠO TIẾN TRÌNH", type="primary"):
        if not ten_bai_hoc.strip():
            st.error("⚠️ Vui lòng nhập 'Tên chủ đề / Tên bài học'!")
        else:
            with st.spinner("⏳ AI đang quét tài liệu và thiết kế giáo án chuẩn 5512..."):
                file_context = ""
                if file_tai_len and bam_sat:
                    try:
                        if file_tai_len.name.endswith('.pdf'):
                            reader = PdfReader(file_tai_len)
                            file_context = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                        elif file_tai_len.name.endswith('.txt'):
                            file_context = file_tai_len.read().decode("utf-8")
                    except Exception as e:
                        st.warning(f"Không thể đọc tài liệu: {e}")
                
                # Prompt được tối ưu cho chuẩn 5512
                prompt = f"""
                Bạn là chuyên gia giáo dục. Hãy soạn KHBD cho bài học: '{ten_bai_hoc}' theo đúng chuẩn Công văn 5512.
                
                THÔNG TIN CHUNG:
                - Môn {mon_hoc}, lớp {lop}, thời lượng {so_tiet} tiết.
                - Bắt buộc tuân thủ cấu trúc của file mẫu đã tải lên dưới đây.
                
                DỮ LIỆU ĐẦU VÀO (Dùng để lấy nội dung kiến thức):
                {file_context[:10000]}
                
                YÊU CẦU BẮT BUỘC:
                1. CẤU TRÚC: Phải bám sát từng mục (I, II, III...) trong file mẫu. Không được bỏ qua mục nào.
                2. CHI TIẾT: Soạn chi tiết, không tóm tắt. Mỗi hoạt động dạy học phải có đầy đủ 4 bước: (1) Mục tiêu; (2) Nội dung; (3) Sản phẩm; (4) Tổ chức thực hiện.
                3. ĐỊNH DẠNG:
                   - Công thức toán học/hóa học phải viết dạng LaTeX ($...$).
                   - Các mục lớn phải in đậm.
                   - Không dùng ký tự ">" hay các ký tự markdown lạ.
                4. TÍCH HỢP: {yeu_cau}
                
                Bắt đầu ngay với mục I. MỤC TIÊU. Không chào hỏi.
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['khbd_content'] = content
                    st.session_state['khbd_meta'] = {
                        "title": ten_bai_hoc, 
                        "mon": mon_hoc, 
                        "lop": lop, 
                        "so_tiet": so_tiet
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    if c2.button("🗑️ XÓA DỮ LIỆU"):
        st.session_state.pop('khbd_content', None)
        st.session_state.pop('khbd_meta', None)
        st.rerun()

    if st.session_state.get('khbd_content'):
        st.markdown("---")
        st.markdown(st.session_state['khbd_content'])
        
        try:
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = st.session_state['khbd_meta'].copy()
            data_export["ai_generated_content"] = st.session_state['khbd_content']
            data_export["is_khbd"] = True
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 TẢI FILE KẾ HOẠCH BÀI DẠY (WORD)", 
                data=word_bytes, 
                file_name=f"KHBD_{st.session_state['khbd_meta']['title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
        except Exception as e:
            st.error(f"❌ Lỗi xuất file Word: {e}")
