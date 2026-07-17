import streamlit as st
import sys
import os
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

def load_prompt_template(filename):
    """Hàm đọc file prompt từ thư mục prompts"""
    root_path = Path(__file__).resolve().parents[2]
    prompt_path = os.path.join(root_path, "prompts", filename)
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        st.error(f"Không tìm thấy file prompt tại {prompt_path}")
        return ""

def render_xd_de_kt(ai_engine):
    st.markdown("### 📝 Soạn thảo Ma trận, Đặc tả & Đề KT (Chuẩn 5512)")
    
    # 1. BẢNG ĐIỀU KHIỂN
    c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1.2, 1, 1.5, 1])
    mon_hoc = c1.selectbox("Chọn Môn", ["Toán", "Ngữ văn", "Ngoại ngữ", "KHTN", "Lịch sử & Địa lý", "Tin học", "Khác"])
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10"], index=2)
    hinh_thuc = c3.selectbox("Hình thức", ["Trắc nghiệm & Tự luận", "100% Trắc nghiệm", "100% Tự luận"])
    thoi_gian = c4.selectbox("Thời gian", ["15 phút", "45 phút", "90 phút"])
    ten_de = c5.text_input("Tên bài kiểm tra")
    with c6:
        st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
        bam_sat = st.checkbox("Bám sát tài liệu", value=True)
    
    c_f1, c_f2 = st.columns(2)
    file_de_cuong = c_f1.file_uploader("Tải đề cương", type=["pdf", "docx", "txt"])
    file_ma_tran = c_f2.file_uploader("Tải ma trận mẫu (không bắt buộc)", type=["pdf", "docx", "txt"])

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
        n_nlc = cols[0].number_input("NLC", min_value=0, value=10)
        d_nlc = cols[1].number_input("Đ.NLC", min_value=0.0, value=0.25, step=0.25)
        n_ds = cols[2].number_input("Đ/S", min_value=0, value=2)
        d_ds = cols[3].number_input("Đ.Đ/S", min_value=0.0, value=0.25, step=0.25)
        n_dk = cols[4].number_input("Điền K", min_value=0, value=2)
        d_dk = cols[5].number_input("Đ.DK", min_value=0.0, value=0.25, step=0.25)
        n_ngan = cols[6].number_input("TL Ngắn", min_value=0, value=2)
        d_ngan = cols[7].number_input("Đ.TLN", min_value=0.0, value=0.50, step=0.25)

        st.markdown("**3. Thông số Tự luận**")
        total_diem_tn = (n_nlc * d_nlc) + (n_ds * d_ds) + (n_dk * d_dk) + (n_ngan * d_ngan)
        tl_cols = st.columns(4)
        num_tl = tl_cols[0].number_input("Số câu Tự luận", 1, 10, 2)
        
        tl_points = []
        for i in range(num_tl):
            p = tl_cols[1].number_input(f"Câu {i+1} (đ)", min_value=0.0, value=1.0, step=0.25, key=f"tl_p_{i}")
            tl_points.append(p)
        
        total_diem_tl = sum(tl_points)
        tl_cols[2].metric("Tổng điểm TN", f"{total_diem_tn:.2f}")
        tl_cols[3].metric("Tổng điểm TL", f"{total_diem_tl:.2f}")

    # 3. NÚT XỬ LÝ
    if st.button("🚀 TỰ ĐỘNG KHỞI TẠO MA TRẬN VÀ ĐỀ THI", type="primary", use_container_width=True):
        with st.spinner("⏳ AI đang tự do sáng tạo Ma trận và Đề thi (khoảng 1-2 phút)..."):
            file_context = ""
            if bam_sat:
                if file_de_cuong: file_context += f"\nĐỀ CƯƠNG: {extract_text_from_file(file_de_cuong)}"
                if file_ma_tran: file_context += f"\nMA TRẬN MẪU: {extract_text_from_file(file_ma_tran)}"
            if not file_context:
                file_context = "Không có tài liệu đính kèm. Bạn hãy tự chọn các chủ đề trọng tâm để ra đề."

            # ĐỌC PROMPT TỪ FILE VÀ ĐIỀN DỮ LIỆU
            raw_prompt = load_prompt_template("prompt_de_kt.txt")
            if raw_prompt:
                prompt = raw_prompt.format(
                    mon_hoc=mon_hoc, lop=lop, ten_de=ten_de,
                    tong_cau_tn=n_nlc + n_ds + n_dk + n_ngan, total_diem_tn=f"{total_diem_tn:.2f}",
                    n_nlc=n_nlc, n_ds=n_ds, n_dk=n_dk, n_ngan=n_ngan,
                    num_tl=num_tl, total_diem_tl=f"{total_diem_tl:.2f}",
                    nb=nb, th=th, vd=vd, vdc=vdc, file_context=file_context
                )
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['de_kt_content'] = content
                    st.rerun()
                except Exception as e: st.error(f"Lỗi khi gọi AI: {str(e)}")

    # 4. HIỂN THỊ
    if 'de_kt_content' in st.session_state:
        if st.button("🗑️ XÓA ĐỀ NÀY"): del st.session_state['de_kt_content']; st.rerun()
        st.markdown(st.session_state['de_kt_content'])
        
        try:
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path: sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine
            word_bytes = WordExportEngine.export_to_word({"ai_generated_content": st.session_state['de_kt_content'], "is_de_kt": True, "title": ten_de})
            st.download_button("📥 TẢI FILE WORD", data=word_bytes, file_name="De_Thi.docx", use_container_width=True)
        except Exception as e:
            st.warning(f"Chưa thể xuất ra file Word. Lỗi chi tiết: {e}")
