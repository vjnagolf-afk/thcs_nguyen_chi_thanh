import streamlit as st
import sys
from pathlib import Path

# Hàm tiện ích đọc file
def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.pdf'):
            from pypdf import PdfReader
            reader = PdfReader(uploaded_file)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif uploaded_file.name.endswith('.docx'):
            try:
                import docx
                doc = docx.Document(uploaded_file)
                return "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                st.warning("⚠️ Hệ thống chưa cài thư viện `python-docx` để đọc file Word. Hãy cài đặt hoặc dùng file PDF/TXT.")
                return ""
        elif uploaded_file.name.endswith('.txt'):
            return uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.warning(f"Không thể đọc file {uploaded_file.name}: {e}")
    return ""

def render_xd_rubric(ai_engine):
    st.markdown("### 📊 Xây dựng Bảng Tiêu chí Đánh giá (Rubric)")

    # 1. BẢNG ĐIỀU KHIỂN
    ds_mon = [
        "Ngữ văn", "Toán", "Ngoại ngữ", "Giáo dục công dân", "Lịch sử và Địa lý", 
        "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", "Công nghệ", 
        "Tin học", "Giáo dục thể chất", "Nghệ thuật", "Giáo dục địa phương", 
        "Hoạt động trải nghiệm, hướng nghiệp"
    ]

    c1, c2, c3, c4 = st.columns(4)
    mon_hoc = c1.selectbox("Môn học (Rubric)", ds_mon)
    lop = c2.selectbox("Lớp (Rubric)", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2)
    loai_nhiem_vu = c3.selectbox("Loại nhiệm vụ", ["Dự án học tập", "Thuyết trình", "Làm việc nhóm", "Viết luận/Báo cáo", "Thực hành/Thí nghiệm", "Sản phẩm STEM"])
    thang_diem = c4.selectbox("Thang điểm", ["Thang điểm 10", "Thang điểm 100", "Chỉ xếp loại (Đạt/Chưa đạt)"])
    
    st.write("")
    
    c1, c2 = st.columns([2, 1])
    ten_nhiem_vu = c1.text_input("Tên chủ đề / Nhiệm vụ đánh giá", placeholder="Ví dụ: Dự án 'Nước sạch cho mọi người', Bài thuyết trình Lịch sử địa phương...")
    file_tai_len = c2.file_uploader("Tài liệu mô tả nhiệm vụ (nếu có)", type=["pdf", "docx", "txt"])

    with st.expander("Tùy chỉnh Tiêu chí & Mức độ", expanded=True):
        def blue_label(text):
            st.markdown(f"<p style='color: #0056b3; font-weight: 600; font-size: 14px; margin-bottom: 0px;'>{text}</p>", unsafe_allow_html=True)
            
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            blue_label("Số lượng mức độ đánh giá")
            so_muc_do = st.radio("so_muc", ["3 Mức (Tốt, Đạt, Chưa đạt)", "4 Mức (Giỏi, Khá, Đạt, Chưa đạt)"], index=1, horizontal=True, label_visibility="collapsed")
        with r1_c2:
            blue_label("Gợi ý các tiêu chí thành phần (AI sẽ tự chia trọng số)")
            tieu_chi_goi_y = st.text_input("tc", placeholder="VD: Nội dung, Hình thức, Kỹ năng trình bày, Phối hợp nhóm...", label_visibility="collapsed")

    # 2. XỬ LÝ LOGIC
    st.write("")
    c_btn1, c_btn2 = st.columns(2)
    if c_btn1.button("🚀 KHỞI TẠO BẢNG RUBRIC", type="primary", use_container_width=True):
        if not ten_nhiem_vu.strip():
            st.error("⚠️ Vui lòng nhập Tên chủ đề hoặc Nhiệm vụ cần đánh giá!")
        else:
            with st.spinner("⏳ AI đang phân tích kỹ năng và lập ma trận Rubric..."):
                file_context = ""
                if file_tai_len:
                    file_context = extract_text_from_file(file_tai_len)

                prompt = f"""
                Bạn là một chuyên gia Đo lường và Đánh giá giáo dục. Hãy thiết kế một bảng Rubric (Tiêu chí đánh giá) cực kỳ chi tiết, khoa học và chuẩn sư phạm.
                
                THÔNG TIN NHIỆM VỤ:
                - Tên nhiệm vụ/Sản phẩm: {ten_nhiem_vu}
                - Môn học: {mon_hoc}, Cấp độ: {lop}
                - Loại hình đánh giá: {loai_nhiem_vu}
                - Hệ thống điểm: {thang_diem}. Cấu trúc đánh giá gồm: {so_muc_do}.
                - Gợi ý tiêu chí thành phần từ giáo viên: {tieu_chi_goi_y if tieu_chi_goi_y else "Tự động phân bổ 3-5 tiêu chí phù hợp nhất với đặc thù nhiệm vụ."}

                YÊU CẦU TRÌNH BÀY (BẮT BUỘC TUÂN THỦ):
                1. Bắt đầu bằng một đoạn ngắn tóm tắt mục tiêu của Rubric này (Phát triển năng lực/phẩm chất gì).
                2. Lập BẢNG RUBRIC BẰNG MARKDOWN. Bảng phải có các cột:
                   - Cột 1: Tiêu chí (Ví dụ: Nội dung, Hình thức...) kèm Trọng số % hoặc Điểm tối đa.
                   - Các cột tiếp theo: Tương ứng với từng mức độ đánh giá ({so_muc_do}).
                3. Nội dung trong các ô của bảng phải là CÁC CHỈ BÁO HÀNH VI HOẶC SẢN PHẨM RÕ RÀNG (Có thể định lượng được, không dùng từ ngữ chung chung như "tương đối", "khá tốt"). Dùng gạch đầu dòng (-) trong các ô của bảng nếu có nhiều ý.
                4. Cung cấp hướng dẫn sử dụng Rubric ngắn gọn cho giáo viên ở cuối.
                
                TÀI LIỆU/MÔ TẢ THAM CHIẾU:
                {file_context[:6000]}
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['rubric_content'] = content
                    st.session_state['rubric_meta'] = {
                        "title": ten_nhiem_vu.replace(" ", "_"), 
                        "mon": mon_hoc, 
                        "lop": lop
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    if c_btn2.button("🗑️ XÓA DỮ LIỆU RUBRIC", use_container_width=True):
        st.session_state.pop('rubric_content', None)
        st.session_state.pop('rubric_meta', None)
        st.rerun()

    # 3. KHU VỰC KẾT QUẢ VÀ TẢI VỀ
    if st.session_state.get('rubric_content'):
        st.markdown("---")
        st.markdown(st.session_state['rubric_content'])
        
        try:
            # Lazy Import
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = st.session_state['rubric_meta'].copy()
            data_export["ai_generated_content"] = st.session_state['rubric_content']
            data_export["is_rubric"] = True 
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 TẢI FILE RUBRIC (WORD)", 
                data=word_bytes, 
                file_name=f"Rubric_{st.session_state['rubric_meta']['title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")
