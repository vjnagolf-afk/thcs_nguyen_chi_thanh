import streamlit as st
import sys
from pathlib import Path

def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.pdf'):
            from pypdf import PdfReader
            return "\n".join([p.extract_text() for p in PdfReader(uploaded_file).pages if p.extract_text()])
        elif uploaded_file.name.endswith('.docx'):
            import docx
            return "\n".join([para.text for para in docx.Document(uploaded_file).paragraphs])
        elif uploaded_file.name.endswith('.txt'):
            return uploaded_file.read().decode("utf-8")
    except: return ""
    return ""

def render_xd_de_kt(ai_engine):
    st.markdown("### 📝 Soạn thảo Ma trận, Đặc tả & Đề KT (Chuẩn 5512)")
    
    # 1. BẢNG ĐIỀU KHIỂN
    c1, c2, c3, c4 = st.columns(4)
    mon_hoc = c1.selectbox("Chọn Môn", ["Toán", "Ngữ văn", "Ngoại ngữ", "KHTN", "Lịch sử & Địa lý", "Tin học", "Khác"])
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10"], index=2)
    hinh_thuc = c3.selectbox("Hình thức", ["Trắc nghiệm & Tự luận", "100% Trắc nghiệm", "100% Tự luận"])
    thoi_gian = c4.selectbox("Thời gian", ["15 phút", "45 phút", "90 phút"])
    
    ten_de = st.text_input("Tên bài kiểm tra")
    
    # FILE UPLOAD
    c_f1, c_f2, c_chk = st.columns([1, 1, 1])
    file_de_cuong = c_f1.file_uploader("Tải đề cương", type=["pdf", "docx", "txt"])
    file_ma_tran = c_f2.file_uploader("Tải ma trận mẫu", type=["pdf", "docx", "txt"])
    bam_sat = c_chk.checkbox("Bám sát tài liệu tải lên", value=True)
    
    yeu_cau_chi_tiet = st.text_area("Yêu cầu thêm")

    # 2. CẤU HÌNH CHI TIẾT
    with st.expander("Cấu hình Tỷ lệ & Số câu", expanded=True):
        st.markdown("**1. Tỷ lệ nhận thức (%)**")
        r1, r2, r3, r4 = st.columns(4)
        nb = r1.number_input("Nhận biết", 0, 100, 40)
        th = r2.number_input("Thông hiểu", 0, 100, 30)
        vd = r3.number_input("Vận dụng", 0, 100, 20)
        vdc = r4.number_input("Vận dụng cao", 0, 100, 10)
        
        st.markdown("**2. Thông số Trắc nghiệm**")
        cols = st.columns(8)
        # Điều chỉnh min_value=0.25 và step=0.25 cho các ô điểm
        n_nlc = cols[0].number_input("NLC", value=10)
        d_nlc = cols[1].number_input("Đ.NLC", min_value=0.25, value=0.25, step=0.25)
        n_ds = cols[2].number_input("Đ/S", value=2)
        d_ds = cols[3].number_input("Đ.Đ/S", min_value=0.25, value=0.25, step=0.25)
        n_dk = cols[4].number_input("Điền K", value=2)
        d_dk = cols[5].number_input("Đ.DK", min_value=0.25, value=0.25, step=0.25)
        n_ngan = cols[6].number_input("TL Ngắn", value=2)
        d_ngan = cols[7].number_input("Đ.TLN", min_value=0.25, value=0.50, step=0.25)

        st.markdown("**3. Thông số Tự luận**")
        total_diem_tn = (n_nlc * d_nlc) + (n_ds * d_ds) + (n_dk * d_dk) + (n_ngan * d_ngan)
        tl_cols = st.columns(4)
        num_tl = tl_cols[0].number_input("Số câu Tự luận", 1, 10, 2)
        
        tl_points = []
        for i in range(num_tl):
            # Điều chỉnh min_value=0.25 và step=0.25 cho điểm tự luận
            p = tl_cols[1].number_input(f"Câu {i+1} (đ)", min_value=0.25, value=1.0, step=0.25, key=f"tl_p_{i}")
            tl_points.append(p)
        
        total_diem_tl = sum(tl_points)
        tl_cols[2].metric("Tổng điểm TN", f"{total_diem_tn:.2f}")
        tl_cols[3].metric("Tổng điểm TL", f"{total_diem_tl:.2f}")

    # 3. NÚT XỬ LÝ
    if st.button("🚀 TỰ ĐỘNG KHỞI TẠO MA TRẬN VÀ ĐỀ THI", type="primary", use_container_width=True):
        with st.spinner("⏳ AI đang làm việc..."):
            file_context = ""
            if bam_sat:
                if file_de_cuong: file_context += f"\nĐỀ CƯƠNG: {extract_text_from_file(file_de_cuong)}"
                if file_ma_tran: file_context += f"\nMA TRẬN MẪU: {extract_text_from_file(file_ma_tran)}"
            
            prompt = f"""
            Bạn là chuyên gia soạn đề kiểm tra chuẩn 5512.
            YÊU CẦU: Soạn đề {mon_hoc} lớp {lop} bài {ten_de}.
            CẤU HÌNH:
            - Phần Trắc nghiệm: Tổng {n_nlc + n_ds + n_dk + n_ngan} câu, Tổng điểm {total_diem_tn:.2f}.
            - Phần Tự luận: {num_tl} câu, Tổng điểm {total_diem_tl:.2f}.
            - Phân bổ: {nb}% NB, {th}% TH, {vd}% VD, {vdc}% VDC.
            
            ĐỊNH DẠNG TRẢ VỀ:
            1. I. MA TRẬN ĐỀ KIỂM TRA (Kẻ bảng Markdown)
            2. II. BẢN ĐẶC TẢ (Kẻ bảng Markdown)
            3. III. ĐỀ KIỂM TRA (Ghi rõ nội dung đề)
            4. IV. ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM (Chi tiết)
            
            TÀI LIỆU: {file_context[:10000]}
            """
            try:
                content = ai_engine.generate_text(prompt)
                st.session_state['de_kt_content'] = content
                st.rerun()
            except Exception as e: st.error(str(e))

    # 4. HIỂN THỊ
    if 'de_kt_content' in st.session_state:
        if st.button("🗑️ XÓA ĐỀ"): del st.session_state['de_kt_content']; st.rerun()
        st.markdown(st.session_state['de_kt_content'])
        
        try:
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path: sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine
            word_bytes = WordExportEngine.export_to_word({"ai_generated_content": st.session_state['de_kt_content'], "is_de_kt": True, "title": ten_de})
            st.download_button("📥 TẢI FILE WORD", data=word_bytes, file_name="De_Thi.docx", use_container_width=True)
        except Exception as e:
            st.warning(f"Chưa thể xuất ra file Word. Lỗi chi tiết: {e}")
