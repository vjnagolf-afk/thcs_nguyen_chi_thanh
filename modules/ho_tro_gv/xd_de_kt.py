import streamlit as st
import sys
from pathlib import Path

# Hàm tiện ích đọc file (Hỗ trợ cả PDF, DOCX và TXT)
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

def render_xd_de_kt(ai_engine):
    # 1. BẢNG ĐIỀU KHIỂN CHUNG (ROW 1 & 2)
    ds_mon = [
        "Toán", "Ngữ văn", "Ngoại ngữ", "Giáo dục công dân", "Lịch sử và Địa lý", 
        "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", "Công nghệ", 
        "Tin học", "Giáo dục thể chất", "Nghệ thuật", "Giáo dục địa phương"
    ]

    c1, c2, c3, c4 = st.columns(4)
    mon_hoc = c1.selectbox("Chọn Môn", ds_mon)
    lop = c2.selectbox("Chọn Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2)
    hinh_thuc = c3.selectbox("Hình thức ra đề", ["Trắc nghiệm & Tự luận", "100% Trắc nghiệm", "100% Tự luận"])
    thoi_gian = c4.selectbox("Thời gian", ["15 phút", "45 phút", "60 phút", "90 phút", "120 phút"], index=1)
    
    st.write("") # Tạo khoảng cách
    
    c1, c2, c3 = st.columns([2, 1, 1])
    ten_de = c1.text_input("Tên bài kiểm tra / Đề số", placeholder="Ví dụ: Kiểm tra giữa kì I")
    file_de_cuong = c2.file_uploader("Tải đề cương lên", type=["pdf", "docx", "txt"], help="200MB per file • DOCX, PDF, TXT")
    file_ma_tran = c3.file_uploader("Tải ma trận mẫu (nếu cần)", type=["pdf", "docx", "txt"], help="200MB per file • DOCX, PDF, TXT")

    bam_sat = st.checkbox("Bám sát nội dung đề cương/ma trận tải lên", value=True)
    yeu_cau_chi_tiet = st.text_area("Yêu cầu chi tiết", placeholder="Thầy cô yêu cầu thêm. Ví dụ: Phần tự luận bám sát kiến thức phần ... ra theo tỷ lệ phân hóa HS, v.v....")

    # 2. BẢNG EXPANDER CẤU HÌNH CHI TIẾT
    with st.expander("Cấu hình Tỷ lệ nhận thức & Số lượng câu", expanded=True):
        def blue_label(text):
            st.markdown(f"<p style='color: #0056b3; font-weight: 600; font-size: 14px; margin-bottom: 0px;'>{text}</p>", unsafe_allow_html=True)

        st.markdown("<p style='color: #dc3545; font-weight: bold; font-size: 16px;'>1. Tỷ lệ nhận thức (%)</p>", unsafe_allow_html=True)
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        with r1_c1: blue_label("Nhận biết (%)"); tl_nhan_biet = st.number_input("nb", min_value=0, max_value=100, value=40, step=5, label_visibility="collapsed")
        with r1_c2: blue_label("Thông hiểu (%)"); tl_thong_hieu = st.number_input("th", min_value=0, max_value=100, value=30, step=5, label_visibility="collapsed")
        with r1_c3: blue_label("Vận dụng (%)"); tl_van_dung = st.number_input("vd", min_value=0, max_value=100, value=20, step=5, label_visibility="collapsed")
        with r1_c4: blue_label("Vận dụng cao (%)"); tl_vd_cao = st.number_input("vdc", min_value=0, max_value=100, value=10, step=5, label_visibility="collapsed")
        
        st.write("")

        st.markdown("<p style='color: #dc3545; font-weight: bold; font-size: 16px;'>2. Thông số Trắc nghiệm (Phải thỏa mãn Tổng = 16 câu, Tổng = 4 điểm)</p>", unsafe_allow_html=True)
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        with r2_c1: blue_label("Số câu nhiều lựa chọn"); tn_nhieu_lua_chon = st.number_input("tn_nlc", min_value=0, value=10, label_visibility="collapsed")
        with r2_c2: blue_label("Số câu Đúng/Sai"); tn_dung_sai = st.number_input("tn_ds", min_value=0, value=2, label_visibility="collapsed")
        with r2_c3: blue_label("Số câu Điền khuyết"); tn_dien_khuyet = st.number_input("tn_dk", min_value=0, value=2, label_visibility="collapsed")
        with r2_c4: blue_label("Số câu trả lời ngắn"); tl_ngan = st.number_input("tl_n", min_value=0, value=2, label_visibility="collapsed")

    # 3. NÚT XỬ LÝ
    st.write("")
    if st.button("TỰ ĐỘNG KHỞI TẠO MA TRẬN VÀ ĐỀ THI", type="primary", use_container_width=True):
        if not ten_de.strip() and not file_de_cuong:
            st.error("⚠️ Vui lòng nhập Tên bài kiểm tra/Đề số hoặc tải Đề cương lên!")
        else:
            with st.spinner("⏳ AI đang thiết lập Ma trận và trộn Đề kiểm tra..."):
                file_context = ""
                if bam_sat:
                    if file_de_cuong: file_context += f"\n[NỘI DUNG ĐỀ CƯƠNG BẮT BUỘC SỬ DỤNG]:\n{extract_text_from_file(file_de_cuong)}"
                    if file_ma_tran: file_context += f"\n[CẤU TRÚC MA TRẬN MẪU BẮT BUỘC TUÂN THỦ]:\n{extract_text_from_file(file_ma_tran)}"

                prompt = f"""
                Bạn là chuyên gia khảo thí. Hãy soạn đề kiểm tra môn {mon_hoc} lớp {lop} theo đúng quy định 5512.
                
                QUY TẮC TOÁN HỌC BẮT BUỘC (TUÂN THỦ TUYỆT ĐỐI):
                1. PHẦN TRẮC NGHIỆM (TỔNG 16 CÂU = 4.0 ĐIỂM):
                   Bạn phải tự tính toán số câu và điểm số sao cho:
                   - Số câu hỏi nhiều lựa chọn: {tn_nhieu_lua_chon} câu.
                   - Số câu hỏi Đúng/Sai (mỗi câu gồm 4 ý a,b,c,d): {tn_dung_sai} câu.
                   - Số câu Điền khuyết: {tn_dien_khuyet} câu.
                   - Số câu Trả lời ngắn: {tl_ngan} câu.
                   - Tổng số câu = {tn_nhieu_lua_chon} + {tn_dung_sai} + {tn_dien_khuyet} + {tl_ngan} = 16 câu.
                   - Tổng điểm = 4.0 điểm. Hãy tự phân bổ điểm cho từng dạng câu hỏi (Ví dụ: câu nhiều lựa chọn thường 0.25đ/câu) để tổng đạt chính xác 4.0 điểm.
                
                2. PHẦN TỰ LUẬN (TỔNG 6.0 ĐIỂM):
                   Soạn đề chi tiết, có phân chia câu hỏi theo mức độ nhận thức (Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao).
                   Tỷ lệ mức độ: {tl_nhan_biet}% Nhận biết, {tl_thong_hieu}% Thông hiểu, {tl_van_dung}% Vận dụng, {tl_vd_cao}% Vận dụng cao.

                YÊU CẦU NỘI DUNG:
                - Bám sát kiến thức: {file_context[:8000]}
                - Trình bày cấu trúc:
                  I. MA TRẬN ĐỀ KIỂM TRA (Bảng Markdown)
                  II. BẢN ĐẶC TẢ (Bảng Markdown)
                  III. ĐỀ KIỂM TRA (Trắc nghiệm có 4 phương án A,B,C,D rõ ràng).
                  IV. ĐÁP ÁN VÀ BIỂU ĐIỂM CHI TIẾT.

                LƯU Ý KỸ THUẬT:
                - Sử dụng LaTeX cho tất cả công thức ($...$).
                - KHÔNG dùng dấu ">" đầu dòng.
                - Nếu cần hình vẽ/đồ thị, ghi: *[Chèn hình ảnh tại đây]*.
                - Yêu cầu thêm từ giáo viên: {yeu_cau_chi_tiet}
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['de_kt_content'] = content
                    st.session_state['de_kt_meta'] = {
                        "title": ten_de.replace(" ", "_") if ten_de else "De_KT", 
                        "mon": mon_hoc
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    # 4. KHU VỰC KẾT QUẢ
    if st.session_state.get('de_kt_content'):
        if st.button("🗑️ XÓA ĐỀ NÀY"):
            st.session_state.pop('de_kt_content', None)
            st.rerun()
        st.markdown("---")
        st.markdown(st.session_state['de_kt_content'])
        
        # Lazy Import cho việc xuất file Word
        try:
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path: sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine
            
            data_export = st.session_state['de_kt_meta'].copy()
            data_export["ai_generated_content"] = st.session_state['de_kt_content']
            data_export["is_de_kt"] = True 
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            st.download_button("📥 TẢI FILE ĐỀ KIỂM TRA (WORD)", data=word_bytes, file_name=f"De_KT_{st.session_state['de_kt_meta']['title']}.docx")
        except Exception as e:
            st.error(f"❌ Lỗi xuất Word: {e}")
