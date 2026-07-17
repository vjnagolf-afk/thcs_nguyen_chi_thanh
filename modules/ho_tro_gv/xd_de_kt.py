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
            except: return ""
        elif uploaded_file.name.endswith('.txt'):
            return uploaded_file.read().decode("utf-8")
    except: return ""
    return ""

def render_xd_de_kt(ai_engine):
    st.markdown("### 📝 Soạn thảo Đề kiểm tra (Chuẩn 5512)")
    
    # 1. THÔNG TIN CHUNG
    c1, c2, c3, c4 = st.columns(4)
    mon_hoc = c1.selectbox("Chọn Môn", ["Toán", "Ngữ văn", "Ngoại ngữ", "KHTN", "Lịch sử & Địa lý", "Tin học"])
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10"], index=2)
    hinh_thuc = c3.selectbox("Hình thức", ["Trắc nghiệm & Tự luận", "100% Trắc nghiệm", "100% Tự luận"])
    thoi_gian = c4.selectbox("Thời gian", ["15 phút", "45 phút", "90 phút"])
    ten_de = st.text_input("Tên bài kiểm tra", placeholder="Ví dụ: Kiểm tra giữa kì I")
    
    # 2. CẤU HÌNH TỶ LỆ NHẬN THỨC
    with st.expander("Cấu hình Tỷ lệ nhận thức", expanded=True):
        r1, r2, r3, r4 = st.columns(4)
        nb = r1.number_input("Nhận biết (%)", 0, 100, 40)
        th = r2.number_input("Thông hiểu (%)", 0, 100, 30)
        vd = r3.number_input("Vận dụng (%)", 0, 100, 20)
        vdc = r4.number_input("Vận dụng cao (%)", 0, 100, 10)

        # 3. THÔNG SỐ TRẮC NGHIỆM (1 HÀNG)
        st.markdown("<p style='color: #dc3545; font-weight: bold;'>2. Thông số Trắc nghiệm</p>", unsafe_allow_html=True)
        cols = st.columns(8)
        n_nlc = cols[0].number_input("Số câu NLC", value=10, key="n_nlc")
        d_nlc = cols[1].number_input("Đ.NLC", value=0.25, step=0.05, key="d_nlc")
        n_ds = cols[2].number_input("Số câu Đ/S", value=2, key="n_ds")
        d_ds = cols[3].number_input("Đ.Đ/S", value=0.25, step=0.05, key="d_ds")
        n_dk = cols[4].number_input("Số câu DK", value=2, key="n_dk")
        d_dk = cols[5].number_input("Đ.DK", value=0.25, step=0.05, key="d_dk")
        n_ngan = cols[6].number_input("Số câu TL Ngắn", value=2, key="n_ngan")
        d_ngan = cols[7].number_input("Đ.TLN", value=0.50, step=0.05, key="d_ngan")

        # 4. SỐ CÂU TỰ LUẬN ĐỘNG
        st.markdown("<p style='color: #dc3545; font-weight: bold;'>3. Thông số Tự luận</p>", unsafe_allow_html=True)
        num_tl = st.number_input("Số câu Tự luận", min_value=1, max_value=4, value=2)
        tl_cols = st.columns(num_tl)
        tl_points = {}
        for i in range(num_tl):
            tl_points[i+1] = tl_cols[i].number_input(f"Câu {i+1} (điểm)", value=1.5, step=0.25)

    # NÚT XỬ LÝ
    if st.button("🚀 TỰ ĐỘNG KHỞI TẠO MA TRẬN VÀ ĐỀ THI", type="primary", use_container_width=True):
        tl_str = ", ".join([f"Câu {k}: {v}đ" for k, v in tl_points.items()])
        
        prompt = f"""
        Bạn là chuyên gia khảo thí. Soạn đề {mon_hoc} lớp {lop} bài {ten_de}.
        
        THÔNG SỐ BẮT BUỘC:
        - TRẮC NGHIỆM: {n_nlc} câu NLC ({d_nlc}đ/c), {n_ds} câu Đúng/Sai ({d_ds}đ/c), {n_dk} câu Điền khuyết ({d_dk}đ/c), {n_ngan} câu Trả lời ngắn ({d_ngan}đ/c).
        - TỰ LUẬN: {num_tl} câu với thang điểm: {tl_str}.
        - Tỷ lệ: {nb}% NB, {th}% TH, {vd}% VD, {vdc}% VDC.
        
        CẤU TRÚC PHẢI TRẢ VỀ:
        1. MA TRẬN: (Kẻ bảng Markdown đơn giản, rõ ràng, cột: [Chủ đề | Nội dung | Nhận biết | Thông hiểu | Vận dụng | Vận dụng cao]).
        2. BẢN ĐẶC TẢ: (Kẻ bảng Markdown cột: [STT | Nội dung | Yêu cầu cần đạt | Số câu]).
        3. ĐỀ KIỂM TRA: (Ghi rõ Phần Trắc nghiệm và Tự luận).
        4. ĐÁP ÁN: (Chi tiết).
        
        Lưu ý: Không vẽ bảng quá phức tạp để tránh lỗi hiển thị. Dùng LaTeX cho công thức.
        """
        
        try:
            content = ai_engine.generate_text(prompt)
            st.session_state['de_kt_content'] = content
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi: {e}")

    # HIỂN THỊ
    if 'de_kt_content' in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state['de_kt_content'])
