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

def render_xd_stem(ai_engine):
    st.markdown("### 🤖 Thiết kế Bài dạy STEM chuyên sâu (AI Hỗ trợ)")

    # 1. BẢNG ĐIỀU KHIỂN
    ds_mon = [
        "Khoa học tự nhiên", "Toán", "Công nghệ", "Tin học", "Vật lí", "Hoá học", "Sinh học"
    ]

    c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
    mon_chu_dao = c1.selectbox("Môn học chủ đạo", ds_mon)
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2)
    so_tiet = c3.number_input("Số tiết", min_value=1, max_value=10, value=2)
    mon_tich_hop = c4.text_input("Môn học tích hợp (T-E-A-M)", placeholder="VD: Toán học, Mỹ thuật (Art)...")
    
    st.write("") # Tạo khoảng cách
    
    c1, c2 = st.columns([1, 1])
    ten_chu_de = c1.text_input("Tên chủ đề STEM", placeholder="Ví dụ: Chế tạo xe thế năng, Máy lọc nước mini...")
    vat_lieu = c2.text_input("Vật liệu / Thiết bị dự kiến (Gợi ý cho AI)", placeholder="VD: Bìa carton, ống nhựa, keo nến, motor mini...")

    yeu_cau_chi_tiet = st.text_area("Yêu cầu/Tiêu chí sản phẩm (Tùy chọn)", placeholder="VD: Xe phải chạy được ít nhất 2 mét, sử dụng vật liệu tái chế, chi phí dưới 50k...")
    
    c_file, c_check = st.columns([3, 1])
    file_tai_len = c_file.file_uploader("Tài liệu tham khảo (Sách giáo khoa, bài viết nền tảng)", type=["pdf", "docx", "txt"])
    bam_sat = c_check.checkbox("Bám sát nội dung file", value=True)

    # 2. XỬ LÝ LOGIC
    st.write("")
    c_btn1, c_btn2 = st.columns(2)
    if c_btn1.button("🚀 KHỞI TẠO BÀI DẠY STEM", type="primary", use_container_width=True):
        if not ten_chu_de.strip():
            st.error("⚠️ Vui lòng nhập Tên chủ đề STEM!")
        else:
            with st.spinner("⏳ AI đang phân tích quy trình Engineering Design Process (EDP) và soạn bài..."):
                file_context = ""
                if bam_sat and file_tai_len:
                    file_context = extract_text_from_file(file_tai_len)

                prompt = f"""
                Bạn là một chuyên gia giáo dục STEM xuất sắc tại Việt Nam. Hãy soạn một Kế hoạch bài dạy (Giáo án) STEM hoàn chỉnh.
                
                THÔNG TIN CHỦ ĐỀ:
                - Tên chủ đề STEM: {ten_chu_de}
                - Môn học chủ đạo: {mon_chu_dao}
                - Môn học/Lĩnh vực tích hợp: {mon_tich_hop if mon_tich_hop else "Các môn STEM liên quan"}
                - Cấp học: {lop}, Thời lượng: {so_tiet} tiết.
                - Vật liệu dự kiến: {vat_lieu if vat_lieu else "Sử dụng vật liệu dễ tìm, tái chế"}
                - Tiêu chí/Yêu cầu riêng: {yeu_cau_chi_tiet}

                YÊU CẦU CẤU TRÚC BẮT BUỘC (Chuẩn giáo án STEM):
                **I. MỤC TIÊU** (Trình bày rõ Kiến thức khoa học (S), Công nghệ (T), Kỹ thuật (E), Toán học (M) và Năng lực, Phẩm chất).
                **II. THIẾT BỊ VÀ HỌC LIỆU** (Liệt kê rõ công cụ của GV và vật tư của HS).
                **III. TIẾN TRÌNH DẠY HỌC** (Phải tuân thủ quy trình 5 hoạt động chuẩn):
                   * Hoạt động 1: Xác định vấn đề / Giao nhiệm vụ STEM. (Mô tả tình huống thực tiễn).
                   * Hoạt động 2: Nghiên cứu kiến thức nền và đề xuất giải pháp.
                   * Hoạt động 3: Lựa chọn giải pháp và thiết kế (Vẽ bản vẽ/phác thảo).
                   * Hoạt động 4: Chế tạo mẫu, thử nghiệm và điều chỉnh.
                   * Hoạt động 5: Trình bày, thảo luận và đánh giá sản phẩm.
                (Mỗi hoạt động cần làm rõ: Mục tiêu, Nội dung, Sản phẩm dự kiến, Tổ chức thực hiện).
                **IV. PHỤ LỤC: BẢNG TIÊU CHÍ ĐÁNH GIÁ (RUBRIC)** (Kẻ bảng markdown rõ ràng tiêu chí chấm điểm bản thiết kế và sản phẩm).

                LƯU Ý KỸ THUẬT BẮT BUỘC:
                - Bắt đầu ngay từ "I. MỤC TIÊU". Không có câu chào hỏi dư thừa.
                - Sử dụng Markdown để in đậm tiêu đề.
                - Sử dụng ký tự gạch đầu dòng (-) hoặc dấu (*).
                - KHÔNG sử dụng ký tự ">" ở đầu dòng.
                - Sử dụng LaTeX ($...$) cho công thức tự nhiên.

                TÀI LIỆU NỀN TẢNG THAM CHIẾU:
                {file_context[:8000]}
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['stem_content'] = content
                    st.session_state['stem_meta'] = {
                        "title": ten_chu_de.replace(" ", "_"), 
                        "mon": mon_chu_dao, 
                        "lop": lop
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    if c_btn2.button("🗑️ XÓA DỮ LIỆU BÀI STEM", use_container_width=True):
        st.session_state.pop('stem_content', None)
        st.session_state.pop('stem_meta', None)
        st.rerun()

    # 3. KHU VỰC KẾT QUẢ VÀ TẢI VỀ
    if st.session_state.get('stem_content'):
        st.markdown("---")
        st.markdown(st.session_state['stem_content'])
        
        try:
            # Lazy Import
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = st.session_state['stem_meta'].copy()
            data_export["ai_generated_content"] = st.session_state['stem_content']
            data_export["is_khbd"] = True # Dùng chung template với KHBD
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 TẢI FILE BÀI DẠY STEM (WORD)", 
                data=word_bytes, 
                file_name=f"STEM_{st.session_state['stem_meta']['title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")
