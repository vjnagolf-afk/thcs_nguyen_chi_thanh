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

def render_xd_quizizz(ai_engine):
    st.markdown("### 🕹️ Tạo câu hỏi Trắc nghiệm (Quizizz / Azota / Kahoot)")
    st.info("💡 Tính năng sinh tự động bộ câu hỏi theo đúng định dạng chuẩn để dán (import) thẳng lên các nền tảng thi trực tuyến mà không cần gõ lại.")

    # 1. BẢNG ĐIỀU KHIỂN
    ds_mon = [
        "Toán", "Ngữ văn", "Ngoại ngữ", "Khoa học tự nhiên", "Lịch sử và Địa lý", 
        "Vật lí", "Hoá học", "Sinh học", "Giáo dục công dân", "Công nghệ", "Tin học"
    ]

    c1, c2, c3, c4 = st.columns(4)
    mon_hoc = c1.selectbox("Môn học (Quiz)", ds_mon)
    lop = c2.selectbox("Lớp (Quiz)", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2)
    so_cau = c3.number_input("Số lượng câu hỏi", min_value=5, max_value=50, value=15, step=5)
    nen_tang = c4.selectbox("Định dạng đích", ["Chuẩn Azota (Dễ copy qua Word)", "Chuẩn Quizizz (Text Import)", "Kahoot / Blooket"])

    st.write("")

    c1, c2 = st.columns([2, 1])
    chu_de = c1.text_input("Nội dung / Chủ đề câu hỏi", placeholder="Ví dụ: Định lý Vi-ét, Sự kiện lịch sử 1945, Thì hiện tại đơn...")
    file_tai_len = c2.file_uploader("Tài liệu bài học (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="file_quizizz")

    bam_sat = st.checkbox("Sinh câu hỏi bám sát nghiêm ngặt tài liệu tải lên", value=True)
    muc_do = st.multiselect(
        "Mức độ phân hóa", 
        ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"],
        default=["Nhận biết", "Thông hiểu", "Vận dụng"]
    )

    # 2. XỬ LÝ LOGIC
    st.write("")
    c_btn1, c_btn2 = st.columns([3, 1])
    
    if c_btn1.button("🚀 TẠO BỘ CÂU HỎI TRẮC NGHIỆM", type="primary", use_container_width=True):
        if not chu_de.strip() and not file_tai_len:
            st.error("⚠️ Vui lòng nhập Chủ đề hoặc Tải tài liệu lên để AI có dữ liệu ra đề!")
        else:
            with st.spinner(f"⏳ AI đang soạn {so_cau} câu hỏi trắc nghiệm chuẩn format {nen_tang}..."):
                file_context = ""
                if file_tai_len and bam_sat:
                    file_context = extract_text_from_file(file_tai_len)

                # Chọn Format Prompt dựa trên Nền tảng
                format_yeu_cau = ""
                if "Azota" in nen_tang:
                    format_yeu_cau = """
                    Trình bày THEO ĐÚNG định dạng nhận diện của Azota như sau:
                    Câu 1: Nội dung câu hỏi 1...
                    A. Đáp án 1
                    B. Đáp án 2
                    C. Đáp án 3
                    D. Đáp án 4
                    Đáp án: A
                    Lời giải: (Giải thích ngắn gọn tại sao chọn A).
                    """
                elif "Quizizz" in nen_tang:
                    format_yeu_cau = """
                    Trình bày DƯỚI DẠNG BẢNG MARKDOWN chuẩn để copy vào Excel/Quizizz gồm các cột:
                    | Question Type | Question Text | Option 1 | Option 2 | Option 3 | Option 4 | Correct Option | Time in seconds |
                    Trong đó: Question Type luôn là "Multiple Choice". Correct Option là số (1, 2, 3 hoặc 4). Time in seconds là 30, 45 hoặc 60.
                    """
                else:
                    format_yeu_cau = """
                    Trình bày theo format text rõ ràng, nhấn mạnh đáp án đúng để giáo viên dễ dàng copy dán vào Kahoot/Blooket.
                    Ghi rõ: [Câu x]: ... | [A] ... | [B] ... | [C] ... | [D] ... | [Đúng]: ...
                    """

                prompt = f"""
                Bạn là một chuyên gia khảo thí và tạo bài tập tương tác xuất sắc.
                Nhiệm vụ của bạn là soạn {so_cau} câu hỏi trắc nghiệm đa lựa chọn (4 phương án) dựa trên yêu cầu sau.

                THÔNG TIN CHUNG:
                - Môn học: {mon_hoc}, Cấp độ: {lop}
                - Chủ đề kiến thức: {chu_de}
                - Mức độ nhận thức: Phân bổ đều giữa các mức độ {', '.join(muc_do)}.
                - Định dạng yêu cầu: CỰC KỲ NGHIÊM NGẶT TUÂN THỦ ĐỊNH DẠNG SAU:
                {format_yeu_cau}

                YÊU CẦU ĐẢM BẢO CHẤT LƯỢNG:
                - Các phương án nhiễu (sai) phải logic và dễ gây nhầm lẫn để kiểm tra năng lực thật của học sinh.
                - Sử dụng LaTeX ($...$) nếu có công thức Toán, Lý, Hóa.
                - KHÔNG dùng ký tự ">" ở đầu các dòng. Không tự ý thay đổi format đã quy định.
                
                TÀI LIỆU KIẾN THỨC NỀN (Dùng để ra đề):
                {file_context[:8000]}
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['quizizz_content'] = content
                    st.session_state['quizizz_meta'] = {
                        "title": chu_de.replace(" ", "_") if chu_de else "Bo_Cau_Hoi_Trac_Nghiem"
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    if c_btn2.button("🗑️ Xóa làm lại", use_container_width=True):
        st.session_state.pop('quizizz_content', None)
        st.session_state.pop('quizizz_meta', None)
        st.rerun()
    # 3. HIỂN THỊ KẾT QUẢ VÀ TẢI VỀ
    if st.session_state.get('quizizz_content'):
        st.markdown("---")
        st.success(f"🎉 **Đã tạo thành công bộ câu hỏi chuẩn {nen_tang}. Thầy cô có thể bôi đen copy trực tiếp hoặc tải file Word bên dưới.**")
        
        st.markdown(st.session_state['quizizz_content'])
        
        try:
            # Lazy Import
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = {"title": st.session_state['quizizz_meta']['title']}
            data_export["ai_generated_content"] = st.session_state['quizizz_content']
            data_export["is_rubric"] = True # Dùng chung template tài liệu
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 TẢI XUỐNG FILE WORD (UP LÊN AZOTA)", 
                data=word_bytes, 
                file_name=f"Quiz_{st.session_state['quizizz_meta']['title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")
