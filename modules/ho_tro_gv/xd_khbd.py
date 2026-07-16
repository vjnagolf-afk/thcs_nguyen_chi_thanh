import streamlit as st
from pypdf import PdfReader

# Đường dẫn gốc đã được app.py nạp vào hệ thống, chỉ cần import thẳng là được
from export.export_word import WordExportEngine

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    ds_mon = [
        "Ngữ văn", "Toán", "Ngoại ngữ", "Giáo dục công dân", "Lịch sử và Địa lý", 
        "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", "Công nghệ", 
        "Tin học", "Giáo dục thể chất", "Nghệ thuật", "Giáo dục địa phương", 
        "Hoạt động trải nghiệm, hướng nghiệp"
    ]

    col1, col2, col3, col4 = st.columns(4)
    mon_hoc = col1.selectbox("Môn học", ds_mon)
    lop = col2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    hinh_thuc = col3.selectbox("Chọn hình thức", ["KHBD thu gọn", "Chuẩn 5512", "KHBD Stem"])
    so_tiet = col4.number_input("Số tiết", min_value=1, max_value=20, value=2)
    
    ten_bai_hoc = st.text_input("Tên chủ đề / Tên bài học (AI sẽ tìm kiếm từ khóa này trong tài liệu)")
    
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=True)
    yeu_cau = st.text_area("Yêu cầu bổ sung cho AI (Ví dụ: Lồng ghép Năng lực số, tích hợp AI...)")
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    
    c1, c2 = st.columns(2)
    if c1.button("🚀 KHỞI TẠO TIẾN TRÌNH", type="primary"):
        if not ten_bai_hoc.strip():
            st.error("⚠️ Vui lòng nhập 'Tên chủ đề / Tên bài học' để AI thực hiện tìm kiếm!")
        else:
            with st.spinner("⏳ AI đang quét tài liệu và thiết kế giáo án..."):
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
                
                prompt = f"""
                Bạn là một chuyên gia giáo dục. Hãy soạn KHBD cho bài học: '{ten_bai_hoc}'.
                Thông tin: Môn {mon_hoc}, lớp {lop}, {so_tiet} tiết, hình thức {hinh_thuc}.
                
                YÊU CẦU PHÂN TÍCH:
                1. Tìm kiếm và trích xuất nội dung liên quan trực tiếp đến bài '{ten_bai_hoc}' trong tài liệu tham khảo được cung cấp.
                2. Lồng ghép nội dung Năng lực số và giáo dục AI vào các hoạt động.
                3. {yeu_cau}
                
                YÊU CẦU TRÌNH BÀY (BẮT BUỘC TUÂN THỦ):
                1. Bắt đầu ngay từ "I. MỤC TIÊU". Tuyệt đối không có lời chào hỏi hay câu dẫn.
                2. Phải XUỐNG DÒNG và IN ĐẬM các tiêu đề lớn/nhỏ (Ví dụ: **1. Về kiến thức:**).
                3. Sử dụng ký tự gạch đầu dòng (-) hoặc dấu hoa thị (*) cho các ý liệt kê. Tuyệt đối không viết dính liền thành 1 đoạn văn.
                4. Sử dụng LaTeX ($...$) cho mọi công thức toán học/hóa học. 
                5. Tuyệt đối không sử dụng dấu ">" ở đầu các dòng.
                
                Dữ liệu tài liệu tham khảo: 
                {file_context[:8000]} 
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

    # CHỈNH SỬA 1: Không dùng clear() để tránh bị văng khỏi hệ thống
    if c2.button("🗑️ XÓA DỮ LIỆU"):
        st.session_state.pop('khbd_content', None)
        st.session_state.pop('khbd_meta', None)
        st.rerun()

    if st.session_state.get('khbd_content'):
        st.markdown("---")
        st.markdown(st.session_state['khbd_content'])
        
        # CHỈNH SỬA 2: Đưa nút Tải file ra độc lập, chuẩn bị sẵn Word Bytes
        try:
            data_export = st.session_state['khbd_meta'].copy()
            data_export["ai_generated_content"] = st.session_state['khbd_content']
            data_export["is_khbd"] = True
            
            # Quá trình tạo file chạy ngầm ngay khi văn bản sinh xong
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            # Hiển thị nút Tải file mượt mà, không bao giờ bị treo
            st.download_button(
                label="📥 TẢI FILE KẾ HOẠCH BÀI DẠY (WORD)", 
                data=word_bytes, 
                file_name=f"KHBD_{st.session_state['khbd_meta']['title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")
