import streamlit as st
import sys
from pathlib import Path

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
                return ""
        elif uploaded_file.name.endswith('.txt'):
            return uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.warning(f"Không thể đọc file: {e}")
    return ""

def render_xd_de_kt(ai_engine):
    st.markdown("### 📝 Soạn thảo Ma trận, Đặc tả & Đề KT (Chuẩn 5512)")
    
    # 1. BẢNG ĐIỀU KHIỂN CHUNG
    c1, c2, c3, c4 = st.columns(4)
    mon_hoc = c1.selectbox("Chọn Môn", ["Toán", "Ngữ văn", "Ngoại ngữ", "Giáo dục công dân", "Lịch sử và Địa lý", "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", "Công nghệ", "Tin học", "Giáo dục thể chất", "Nghệ thuật", "Giáo dục địa phương"])
    lop = c2.selectbox("Chọn Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2)
    hinh_thuc = c3.selectbox("Hình thức ra đề", ["Trắc nghiệm & Tự luận", "100% Trắc nghiệm", "100% Tự luận"])
    thoi_gian = c4.selectbox("Thời gian", ["15 phút", "45 phút", "60 phút", "90 phút", "120 phút"], index=1)
    
    ten_de = st.text_input("Tên bài kiểm tra", placeholder="Ví dụ: Kiểm tra cuối kỳ I")
    
    # 2. CẤU HÌNH CHI TIẾT (TỰ ĐỘNG TÍNH TOÁN)
    with st.expander("Cấu hình Tỷ lệ nhận thức & Số lượng câu", expanded=True):
        st.markdown("<p style='color: #dc3545; font-weight: bold;'>1. Tỷ lệ nhận thức (%)</p>", unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        nb = r1.number_input("Nhận biết (%)", 0, 100, 40)
        th = r2.number_input("Thông hiểu (%)", 0, 100, 30)
        vd = r3.number_input("Vận dụng (%)", 0, 100, 20)
        vdc = r4.number_input("Vận dụng cao (%)", 0, 100, 10)
        
        st.markdown("<p style='color: #dc3545; font-weight: bold;'>2. Thông số Trắc nghiệm</p>", unsafe_allow_html=True)
        cols = st.columns(4)
        n_nlc = cols[0].number_input("Số câu Nhiều lựa chọn", 0, value=10)
        d_nlc = cols[1].number_input("Điểm/câu NLC", 0.0, value=0.25, step=0.05)
        n_ds = cols[0].number_input("Số câu Đúng/Sai", 0, value=2)
        d_ds = cols[1].number_input("Điểm/câu Đúng/Sai", 0.0, value=0.25, step=0.05)
        n_dk = cols[0].number_input("Số câu Điền khuyết", 0, value=2)
        d_dk = cols[1].number_input("Điểm/câu Điền khuyết", 0.0, value=0.25, step=0.05)
        n_ngan = cols[0].number_input("Số câu Trả lời ngắn", 0, value=2)
        d_ngan = cols[1].number_input("Điểm/câu TL ngắn", 0.0, value=0.50, step=0.05)

        # TỰ ĐỘNG TÍNH TOÁN
        total_cau_tn = n_nlc + n_ds + n_dk + n_ngan
        total_diem_tn = (n_nlc * d_nlc) + (n_ds * d_ds) + (n_dk * d_dk) + (n_ngan * d_ngan)
        total_diem_tl = 10.0 - total_diem_tn
        
        st.markdown("---")
        c_res1, c_res2, c_res3 = st.columns(3)
        c_res1.metric("Tổng câu TN", total_cau_tn)
        c_res2.metric("Tổng điểm TN", f"{total_diem_tn:.2f}")
        c_res3.metric("Tổng điểm TL", f"{total_diem_tl:.2f}")

    # 3. NÚT XỬ LÝ
    if st.button("🚀 TỰ ĐỘNG KHỞI TẠO MA TRẬN VÀ ĐỀ THI", type="primary", use_container_width=True):
        with st.spinner("⏳ AI đang thiết lập Ma trận và trộn Đề kiểm tra..."):
            prompt = f"""
            Bạn là chuyên gia khảo thí. Hãy soạn đề kiểm tra môn {mon_hoc} lớp {lop}.
            
            QUY TẮC CẤU TRÚC ĐỀ (BẮT BUỘC):
            1. PHẦN TRẮC NGHIỆM:
               - Số câu hỏi: {total_cau_tn} câu.
               - Tổng điểm: {total_diem_tn:.2f} điểm.
               - Phân bổ cụ thể: {n_nlc} câu Nhiều lựa chọn ({d_nlc}đ/c), {n_ds} câu Đúng/Sai ({d_ds}đ/c), {n_dk} câu Điền khuyết ({d_dk}đ/c), {n_ngan} câu Trả lời ngắn ({d_ngan}đ/c).
            
            2. PHẦN TỰ LUẬN:
               - Tổng điểm: {total_diem_tl:.2f} điểm.
               - Các câu hỏi phải được thiết kế để phân loại học sinh theo tỷ lệ: {nb}% NB, {th}% TH, {vd}% VD, {vdc}% VDC.
            
            YÊU CẦU:
            - Trình bày rõ ràng: I. MA TRẬN, II. BẢN ĐẶC TẢ, III. ĐỀ KIỂM TRA, IV. ĐÁP ÁN.
            - Sử dụng LaTeX ($...$) cho công thức.
            - Đáp án chi tiết và hướng dẫn chấm theo thang điểm.
            """
            
            try:
                content = ai_engine.generate_text(prompt)
                st.session_state['de_kt_content'] = content
                st.session_state['de_kt_meta'] = {"title": ten_de, "mon": mon_hoc}
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {e}")

    # 4. HIỂN THỊ KẾT QUẢ
    if st.session_state.get('de_kt_content'):
        st.markdown(st.session_state['de_kt_content'])
        # Code download Word giữ nguyên như cũ
