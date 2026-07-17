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

    # 2. BẢNG EXPANDER CẤU HÌNH CHI TIẾT (UI Clone 100%)
    with st.expander("Cấu hình Tỷ lệ nhận thức & Số lượng câu", expanded=True):
        
        # Hàm hỗ trợ render nhãn màu xanh dương
        def blue_label(text):
            st.markdown(f"<p style='color: #0056b3; font-weight: 600; font-size: 14px; margin-bottom: 0px;'>{text}</p>", unsafe_allow_html=True)

        # PHẦN 1
        st.markdown("<p style='color: #dc3545; font-weight: bold; font-size: 16px;'>1. Tỷ lệ nhận thức (%)</p>", unsafe_allow_html=True)
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        with r1_c1: blue_label("Mức độ Nhận biết (%)"); tl_nhan_biet = st.number_input("nb", min_value=0, max_value=100, value=40, step=5, label_visibility="collapsed")
        with r1_c2: blue_label("Mức độ Thông hiểu (%)"); tl_thong_hieu = st.number_input("th", min_value=0, max_value=100, value=30, step=5, label_visibility="collapsed")
        with r1_c3: blue_label("Mức độ Vận dụng (%)"); tl_van_dung = st.number_input("vd", min_value=0, max_value=100, value=20, step=5, label_visibility="collapsed")
        with r1_c4: blue_label("Mức độ Vận dụng cao (%)"); tl_vd_cao = st.number_input("vdc", min_value=0, max_value=100, value=10, step=5, label_visibility="collapsed")
        
        st.write("")

        # PHẦN 2
        st.markdown("<p style='color: #dc3545; font-weight: bold; font-size: 16px;'>2. Thông số Trắc nghiệm</p>", unsafe_allow_html=True)
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        with r2_c1: blue_label("Số câu hỏi nhiều lựa chọn"); tn_nhieu_lua_chon = st.number_input("tn_nlc", min_value=0, value=12, label_visibility="collapsed")
        with r2_c2: blue_label("Điểm cho câu hỏi nhiều lựa chọn"); diem_nhieu_lua_chon = st.number_input("d_nlc", min_value=0.0, value=0.25, step=0.25, format="%.2f", label_visibility="collapsed")
        with r2_c3: blue_label("Số câu hỏi Đúng/Sai"); tn_dung_sai = st.number_input("tn_ds", min_value=0, value=4, label_visibility="collapsed")
        with r2_c4: blue_label("Điểm cho câu Đ/S"); diem_dung_sai = st.number_input("d_ds", min_value=0.0, value=0.25, step=0.25, format="%.2f", label_visibility="collapsed")
        
        r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
        with r3_c1: blue_label("Số câu Điền khuyết"); tn_dien_khuyet = st.number_input("tn_dk", min_value=0, value=4, label_visibility="collapsed")
        with r3_c2: blue_label("Điểm cho câu Điền khuyết"); diem_dien_khuyet = st.number_input("d_dk", min_value=0.0, value=0.25, step=0.25, format="%.2f", label_visibility="collapsed")
        with r3_c3: blue_label("Số câu trả lời ngắn"); tl_ngan = st.number_input("tl_n", min_value=0, value=2, label_visibility="collapsed")
        with r3_c4: blue_label("Điểm câu trả lời ngắn"); diem_tl_ngan = st.number_input("d_tl_n", min_value=0.0, value=0.50, step=0.25, format="%.2f", label_visibility="collapsed")

        st.write("")

        # PHẦN 3
        st.markdown("<p style='color: #dc3545; font-weight: bold; font-size: 16px;'>3. Thông số Trắc nghiệm và Tự luận</p>", unsafe_allow_html=True)
        r4_c1, r4_c2, r4_c3, r4_c4 = st.columns(4)
        with r4_c1: blue_label("Tổng câu TN"); tong_cau_tn = st.number_input("tc_tn", value=20, label_visibility="collapsed")
        with r4_c2: blue_label("Tổng điểm TN"); tong_diem_tn = st.number_input("td_tn", value=4.00, step=0.25, format="%.2f", label_visibility="collapsed")
        with r4_c3: blue_label("Tổng câu TL"); tong_cau_tl = st.number_input("tc_tl", value=4, label_visibility="collapsed")
        with r4_c4: blue_label("Tổng điểm"); tong_diem_tl = st.number_input("td_tl", value=6.00, step=0.25, format="%.2f", label_visibility="collapsed")

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
                Bạn là một chuyên gia khảo thí xuất sắc của Bộ GD&ĐT. Hãy xây dựng Đề kiểm tra, Ma trận và Đặc tả đề chuẩn sư phạm theo đúng Thông tư hiện hành.
                
                THÔNG TIN CHUNG:
                - Môn: {mon_hoc}, Cấp độ: {lop}
                - Tên bài kiểm tra/Phạm vi: {ten_de}
                - Hình thức: {hinh_thuc}
                - Thời gian làm bài: {thoi_gian}

                TÀI LIỆU THAM CHIẾU (Ngữ cảnh ra đề):
                {file_context[:12000]}

                YÊU CẦU NỘI DUNG (TUÂN THỦ TUYỆT ĐỐI):
                1. BÁM SÁT ĐỀ CƯƠNG: Chỉ thiết kế câu hỏi xoay quanh kiến thức có trong [NỘI DUNG ĐỀ CƯƠNG BẮT BUỘC SỬ DỤNG]. Tuyệt đối KHÔNG tự bịa thêm kiến thức ngoài phạm vi.
                2. BÁM SÁT MA TRẬN: Nếu có [CẤU TRÚC MA TRẬN MẪU], bắt buộc phải vẽ cấu trúc bảng (số cột, tên cột, định dạng) giống hệt 100% mẫu đó.
                3. Tỷ lệ nhận thức: Nhận biết {tl_nhan_biet}%, Thông hiểu {tl_thong_hieu}%, Vận dụng {tl_van_dung}%, Vận dụng cao {tl_vd_cao}%.
                4. Phần Trắc nghiệm ({tong_cau_tn} câu, tổng {tong_diem_tn} điểm):
                   - Dạng 1: {tn_nhieu_lua_chon} câu nhiều lựa chọn (4 phương án A, B, C, D), mỗi câu {diem_nhieu_lua_chon} điểm.
                   - Dạng 2: {tn_dung_sai} câu Đúng/Sai (Mỗi câu gồm 4 ý a,b,c,d), tính điểm {diem_dung_sai} đ/câu chuẩn.
                   - Dạng 3: {tn_dien_khuyet} câu điền khuyết, mỗi câu {diem_dien_khuyet} điểm.
                5. Phần Tự luận/Trả lời ngắn ({tong_cau_tl} câu, tổng {tong_diem_tl} điểm):
                   - {tl_ngan} câu trả lời ngắn (mỗi câu {diem_tl_ngan} điểm).
                   - Các câu tự luận còn lại phân bổ điểm hợp lý sao cho tổng phần này đạt {tong_diem_tl} điểm.
                6. Yêu cầu chi tiết từ giáo viên: {yeu_cau_chi_tiet}

                CẤU TRÚC BẮT BUỘC TRẢ VỀ (Phân chia rõ ràng bằng Markdown):
                I. MA TRẬN ĐỀ KIỂM TRA (Kẻ bảng Markdown hoàn chỉnh phân bổ chi tiết các mức độ nhận thức).
                II. BẢN ĐẶC TẢ ĐỀ KIỂM TRA (Kẻ bảng Markdown chi tiết Yêu cầu cần đạt).
                III. ĐỀ KIỂM TRA (Trình bày khoa học. Trắc nghiệm phải có 4 đáp án A, B, C, D xuống dòng rõ ràng).
                IV. ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM (Bảng đáp án trắc nghiệm chuẩn. Hướng dẫn chấm tự luận chi tiết theo từng mức điểm).

                LƯU Ý KỸ THUẬT (CỰC KỲ QUAN TRỌNG ĐỂ HIỂN THỊ ĐÚNG GIAO DIỆN):
                - ĐỊNH DẠNG CÔNG THỨC MÔN TOÁN/LÝ/HÓA/SINH: Mọi công thức, ký hiệu, phương trình hóa học BẮT BUỘC dùng cú pháp LaTeX. 
                  (Ví dụ: Inline: $x^2 + y^2 = 1$, $H_2SO_4$, $\\frac{{P(x)}}{{Q(x)}}$. Block: $$E = mc^2$$). Tuyệt đối KHÔNG viết text thường cho phân số hoặc chỉ số.
                - ĐỒ THỊ/HÌNH ẢNH: Nếu câu hỏi cần hình minh họa, hãy ghi chú bằng dòng in nghiêng: *[Chèn hình ảnh đồ thị / mạch điện / tế bào tại đây]*.
                - BẢNG BIỂU: Phải sử dụng Markdown Table (`| Cột 1 | Cột 2 |`) chuẩn xác, gióng cột đàng hoàng để giao diện xem trước (Preview) không bị vỡ.
                - Tuyệt đối KHÔNG dùng ký tự ">" ở đầu các dòng (Sẽ làm lỗi định dạng quote).
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['de_kt_content'] = content
                    st.session_state['de_kt_meta'] = {
                        "title": ten_de.replace(" ", "_") if ten_de else "De_KT", 
                        "mon": mon_hoc, 
                        "lop": lop, 
                        "thoi_gian": thoi_gian
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    # 4. KHU VỰC KẾT QUẢ VÀ TẢI VỀ
    c1, c2 = st.columns([8, 2])
    if st.session_state.get('de_kt_content'):
        if c2.button("🗑️ XÓA ĐỀ NÀY", use_container_width=True):
            st.session_state.pop('de_kt_content', None)
            st.session_state.pop('de_kt_meta', None)
            st.rerun()
            
        st.markdown("---")
        st.markdown(st.session_state['de_kt_content'])
        
        try:
            # Lazy Import
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = st.session_state['de_kt_meta'].copy()
            data_export["ai_generated_content"] = st.session_state['de_kt_content']
            data_export["is_de_kt"] = True 
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 TẢI FILE ĐỀ KIỂM TRA (WORD)", 
                data=word_bytes, 
                file_name=f"De_KT_{st.session_state['de_kt_meta']['title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")

    # Footer
    st.write("")
    st.info("⏳ Chào mừng quý thầy cô đến với nền tảng số AI tích hợp chuyên sâu, trường THCS Nguyễn Chí Thanh, P.Tân Lập, tỉnh Đắk Lắk.")
