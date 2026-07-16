import streamlit as st
import sys
from pathlib import Path

# Hàm tiện ích đọc file bài làm của học sinh
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

def render_xd_cham_viet(ai_engine):
    st.markdown("### ✍️ Trợ lý Chấm bài & Hỗ trợ Kỹ năng Viết (Writing)")

    # 1. BẢNG ĐIỀU KHIỂN
    c1, c2, c3, c4 = st.columns([2, 1, 2, 2])
    mon_hoc = c1.selectbox("Môn học", ["Ngữ văn", "Tiếng Anh", "Lịch sử", "Địa lý", "Khác"])
    lop = c2.selectbox("Lớp", ["6", "7", "8", "9", "10", "11", "12", "Tự do"], index=3)
    loai_bai = c3.selectbox("Thể loại bài viết", [
        "Nghị luận xã hội", 
        "Nghị luận văn học", 
        "Tự sự / Miêu tả / Biểu cảm",
        "IELTS Writing Task 1 (Mô tả biểu đồ)",
        "IELTS Writing Task 2 (Essay)",
        "Viết thư / Email",
        "Báo cáo / Tiểu luận"
    ])
    thang_diem = c4.selectbox("Thang điểm đánh giá", ["Thang điểm 10", "Thang điểm 100", "Thang điểm IELTS (1.0 - 9.0)", "Khung Châu Âu CEFR (A1 - C2)"])

    st.markdown("---")

    # 2. KHU VỰC NHẬP LIỆU
    de_bai = st.text_area("Đề bài / Yêu cầu viết (Prompt)", placeholder="Ví dụ: Phân tích bài thơ Đồng chí của Chính Hữu... hoặc 'Do you agree or disagree with the statement...'")
    
    tieu_chi = st.text_input("Tiêu chí đặc biệt (Tùy chọn)", placeholder="VD: Khắt khe về lỗi chính tả, tập trung vào cấu trúc câu, sử dụng từ vựng nâng cao...")

    st.markdown("<p style='color: #0056b3; font-weight: bold;'>Bài làm của học sinh</p>", unsafe_allow_html=True)
    c_text, c_file = st.columns([2, 1])
    bai_lam_text = c_text.text_area("Nhập/Dán nội dung bài làm vào đây", height=200, label_visibility="collapsed")
    file_tai_len = c_file.file_uploader("Hoặc tải file bài làm lên", type=["pdf", "docx", "txt"])

    # 3. NÚT XỬ LÝ LOGIC
    st.write("")
    c_btn1, c_btn2 = st.columns([3, 1])
    
    if c_btn1.button("🚀 CHẤM BÀI & NHẬN XÉT", type="primary", use_container_width=True):
        # Ghép bài làm từ text hoặc file
        bai_lam = bai_lam_text.strip()
        if file_tai_len:
            bai_lam += "\n" + extract_text_from_file(file_tai_len)

        if not de_bai.strip():
            st.error("⚠️ Vui lòng nhập Đề bài / Yêu cầu viết!")
        elif not bai_lam.strip():
            st.error("⚠️ Vui lòng nhập hoặc tải lên Bài làm của học sinh!")
        else:
            with st.spinner("⏳ AI đang đọc bài, soi lỗi và viết nhận xét chi tiết..."):
                prompt = f"""
                Bạn là một Giáo viên / Giám khảo ngôn ngữ cực kỳ xuất sắc, có nhiều năm kinh nghiệm chấm bài thi.
                Nhiệm vụ của bạn là chấm điểm, nhận xét và hỗ trợ cải thiện kỹ năng viết cho học sinh.

                THÔNG TIN BÀI CHẤM:
                - Môn học: {mon_hoc} (Lớp {lop})
                - Thể loại: {loai_bai}
                - Thang điểm: {thang_diem}
                - Yêu cầu đặc biệt từ giáo viên: {tieu_chi if tieu_chi else "Chấm công tâm, chi tiết, bám sát các tiêu chí chuẩn."}

                [ĐỀ BÀI]:
                {de_bai}

                [BÀI LÀM CỦA HỌC SINH]:
                {bai_lam}

                YÊU CẦU TRẢ VỀ (Trình bày bằng Markdown chuyên nghiệp, rõ ràng):
                **1. ĐÁNH GIÁ CHUNG & ĐIỂM SỐ DỰ KIẾN:**
                   - Điểm số ước lượng (Theo thang {thang_diem}).
                   - Nhận xét tổng quan về bố cục, lập luận, đáp ứng đề bài.
                
                **2. PHÂN TÍCH CHI TIẾT (ƯU ĐIỂM & HẠN CHẾ):**
                   - Điểm mạnh (Từ vựng, ngữ pháp, ý tưởng...).
                   - Điểm yếu/Lỗi sai (Chỉ ra lỗi sai cụ thể, trích dẫn câu sai từ bài làm).
                
                **3. BẢNG CHỮA LỖI & NÂNG CẤP TỪ VỰNG:**
                   - Kẻ một bảng gồm 3 cột: [Câu gốc có lỗi/chưa hay] | [Lỗi sai/Phân tích] | [Câu sửa lại/Nâng cấp].
                
                **4. BÀI VIẾT GỢI Ý (ĐÃ ĐƯỢC CHỈNH SỬA / NÂNG CẤP):**
                   - Viết lại hoặc cung cấp một phiên bản bài làm tốt hơn dựa trên ý tưởng gốc của học sinh để các em tham khảo.
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['chamviet_content'] = content
                    st.session_state['chamviet_meta'] = {
                        "title": loai_bai.replace("/", "_").replace(" ", "_"),
                        "mon": mon_hoc
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    if c_btn2.button("🗑️ Xóa & Nhập lại", use_container_width=True):
        st.session_state.pop('chamviet_content', None)
        st.session_state.pop('chamviet_meta', None)
        st.rerun()

    # 4. KHU VỰC KẾT QUẢ VÀ TẢI VỀ
    if st.session_state.get('chamviet_content'):
        st.markdown("---")
        st.markdown(st.session_state['chamviet_content'])
        
        try:
            # Lazy Import
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = st.session_state['chamviet_meta'].copy()
            data_export["ai_generated_content"] = st.session_state['chamviet_content']
            data_export["is_rubric"] = True # Mượn cờ format đơn giản của rubric
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 TẢI PHIẾU CHẤM ĐIỂM (WORD)", 
                data=word_bytes, 
                file_name=f"PhieuChamBai_{st.session_state['chamviet_meta']['mon']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")
