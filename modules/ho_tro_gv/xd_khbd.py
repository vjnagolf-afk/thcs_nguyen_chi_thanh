import streamlit as st
import sys
from pathlib import Path
from pypdf import PdfReader

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
    hinh_thuc = col3.selectbox("Chọn hình thức", ["KHBD chi tiết (Chuẩn 5512)", "KHBD thu gọn"])
    so_tiet = col4.number_input("Số tiết", min_value=1, max_value=20, value=2)
    
    ten_bai_hoc = st.text_input("Tên chủ đề / Tên bài học")
    
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=True)
    yeu_cau = st.text_area("Yêu cầu bổ sung (Ví dụ: Lồng ghép Năng lực số, tích hợp AI...)")
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    
    c1, c2 = st.columns(2)
    if c1.button("🚀 KHỞI TẠO TIẾN TRÌNH", type="primary"):
        if not ten_bai_hoc.strip():
            st.error("⚠️ Vui lòng nhập 'Tên chủ đề / Tên bài học'!")
        else:
            with st.spinner("⏳ AI đang quét tài liệu và thiết kế giáo án chuyên sâu..."):
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
                
                # Logic phân biệt thu gọn và chi tiết
                huong_dan_do_dai = (
                    "viết ngắn gọn, súc tích, chỉ tập trung vào các ý chính, hoạt động cốt lõi, không cần trình bày quá chi tiết các bước thực hiện." 
                    if hinh_thuc == "KHBD thu gọn" 
                    else "viết chi tiết từng bước, mỗi hoạt động bắt buộc phải có đầy đủ: [Mục tiêu] - [Nội dung thực hiện] - [Phương pháp] - [Sản phẩm dự kiến]. Đừng tóm tắt, hãy viết chi tiết."
                )

                prompt = f"""
                Bạn là chuyên gia thiết kế giáo dục. Hãy soạn KHBD cho bài học: '{ten_bai_hoc}'.
                Thông tin: Môn {mon_hoc}, lớp {lop}, {so_tiet} tiết.
                
                YÊU CẦU CỐT LÕI:
                1. DỰA TRÊN TÀI LIỆU: Phải bám sát nội dung, cấu trúc và kiến thức trong file đính kèm dưới đây:
                   {file_context[:8000]}
                
                2. ĐỊNH DẠNG & CẤU TRÚC:
                   - Tuân thủ tuyệt đối cấu trúc của tài liệu gốc (Các mục I, II, III...). Nếu mục nào tài liệu không có, hãy để tiêu đề đó và ghi "Nội dung đang cập nhật".
                   - {huong_dan_do_dai}
                   - CÔNG THỨC TOÁN HỌC: Mọi công thức phải viết dạng LaTeX ($...$) để hiển thị đẹp (Ví dụ: $x^2 + y^2 = z^2$).
                
                3. NỘI DUNG TÍCH HỢP:
                   - {yeu_cau}
                
                4. TRÌNH BÀY:
                   - Bắt đầu ngay từ "I. MỤC TIÊU". Tuyệt đối không chào hỏi.
                   - Dùng In đậm cho các tiêu đề mục.
                   - Dùng gạch đầu dòng (-) cho các ý. Không được dùng ký tự ">".
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

    # HIỂN THỊ KẾT QUẢ VÀ XUẤT FILE
    if st.session_state.get('khbd_content'):
        st.markdown("---")
        st.markdown(st.session_state['khbd_content'])
        
        try:
            # Lazy Import
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
