import streamlit as st
import sys
import os
from pathlib import Path
from string import Template

# Khai báo đường dẫn gốc
root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from models.exam import Exam

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

def load_prompt(filename):
    file_path = root_path / "prompts" / filename
    if not file_path.exists():
        return f"Lỗi: Không tìm thấy {filename}"
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_template_structure(filename="dkt_mau.docx"):
    """Đọc file mẫu từ thư mục templates và chuyển các bảng thành định dạng Markdown cho AI học theo"""
    template_path = root_path / "templates" / filename
    if not template_path.exists():
        return "Không có cấu trúc mẫu đính kèm."
    try:
        import docx
        doc = docx.Document(template_path)
        result = []
        for table in doc.tables:
            for i, row in enumerate(table.rows):
                row_text = [cell.text.replace("\n", " ").strip() for cell in row.cells]
                result.append("| " + " | ".join(row_text) + " |")
                # Ép tự động tạo dòng phân cách Markdown chuẩn ở hàng thứ 2
                if i == 0:
                    result.append("|" + "|".join(["---"] * len(row.cells)) + "|")
            result.append("\n")
        return "\n".join(result)
    except Exception as e:
        return f"Lỗi xử lý file mẫu: {str(e)}"

def render_xd_de_kt(ai_engine):
    st.markdown("### 📝 Soạn thảo Ma trận, Đặc tả & Đề KT (Chuẩn 5512)")
    
    # 1. GIAO DIỆN BẢNG ĐIỀU KHIỂN
    c1, c2, c3, c4, c5, c6 = st.columns([1, 0.8, 1.2, 1, 2, 0.8])
    mon_hoc = c1.selectbox("Môn", ["Toán", "Ngữ văn", "Ngoại ngữ", "KHTN", "Lịch sử & Địa lý", "Tin học", "Khác"])
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10"], index=2)
    hinh_thuc = c3.selectbox("Hình thức", ["Trắc nghiệm & Tự luận", "100% Trắc nghiệm", "100% Tự luận"])
    thoi_gian = c4.selectbox("Thời gian", ["15 phút", "45 phút", "90 phút"])
    ten_de = c5.text_input("Tên bài kiểm tra")
    with c6:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        bam_sat = st.checkbox("Bám sát", value=True)
    
    file_de = st.file_uploader("Tải đề cương (Tài liệu bám sát)", type=["pdf", "docx", "txt"])

    # 2. CẤU HÌNH TỶ LỆ & SỐ CÂU
    with st.expander("Cấu hình Tỷ lệ & Số câu", expanded=True):
        r1, r2, r3, r4 = st.columns(4)
        nb = r1.number_input("Nhận biết (%)", 0, 100, 40)
        th = r2.number_input("Thông hiểu (%)", 0, 100, 30)
        vd = r3.number_input("Vận dụng (%)", 0, 100, 20)
        vdc = r4.number_input("Vận dụng cao (%)", 0, 100, 10)
        
        cols = st.columns(8)
        n_nlc = cols[0].number_input("NLC", min_value=0, value=10)
        d_nlc = cols[1].number_input("Đ.NLC", min_value=0.0, value=0.25, step=0.25)
        n_ds = cols[2].number_input("Đ/S", min_value=0, value=2)
        d_ds = cols[3].number_input("Đ.Đ/S", min_value=0.0, value=0.25, step=0.25)
        n_dk = cols[4].number_input("Điền K", min_value=0, value=2)
        d_dk = cols[5].number_input("Đ.DK", min_value=0.0, value=0.25, step=0.25)
        n_ngan = cols[6].number_input("TL Ngắn", min_value=0, value=2)
        d_ngan = cols[7].number_input("Đ.TLN", min_value=0.0, value=0.50, step=0.25)

        total_cau_tn = n_nlc + n_ds + n_dk + n_ngan
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

    # 3. CONTROLLER TẠO ĐỀ
    if st.button("🚀 TẠO MA TRẬN & ĐỀ THI", type="primary", use_container_width=True):
        with st.spinner("⏳ AI đang học cấu trúc file dkt_mau.docx và tạo đề..."):
            file_ctx = extract_text_from_file(file_de) if (bam_sat and file_de) else "Không có."
            mau_cau_truc = read_template_structure("dkt_mau.docx") # Lấy khuôn mẫu từ file Word
            
            system_role = load_prompt("system_role.txt")
            task_template = load_prompt("task_config.txt")
            
            prompt = system_role + "\n\n" + Template(task_template).substitute(
                mon_hoc=mon_hoc, lop=lop, ten_de=ten_de,
                tong_cau_tn=total_cau_tn, total_diem_tn=f"{total_diem_tn:.2f}",
                n_nlc=n_nlc, n_ds=n_ds, n_dk=n_dk, n_ngan=n_ngan,
                num_tl=num_tl, total_diem_tl=f"{total_diem_tl:.2f}",
                nb=nb, th=th, vd=vd, vdc=vdc, file_context=file_ctx,
                mau_cau_truc=mau_cau_truc # Ép biến này vào prompt
            )
            
            try:
                content = ai_engine.generate_text(prompt)
                current_exam = Exam(
                    exam_type=hinh_thuc, custom_req=file_ctx[:50], tn_total=total_cau_tn,
                    c1=n_nlc, c2=n_ds, c3=n_dk, c4=n_ngan, tl_scores=tl_points,
                    ai_generated_content=content
                )
                st.session_state['exam_data'] = current_exam.to_dict()
                st.rerun()
            except Exception as e: st.error(f"Lỗi AI: {e}")

    # 4. HIỂN THỊ DỮ LIỆU
    if 'exam_data' in st.session_state:
        exam_obj = Exam.from_dict(st.session_state['exam_data'])
        if st.button("🗑️ XÓA ĐỀ NÀY"): 
            del st.session_state['exam_data']
            st.rerun()
            
        st.markdown(exam_obj.ai_generated_content)
        
        try:
            from export.export_word import WordExportEngine
            word_bytes = WordExportEngine.export_to_word({
                "ai_generated_content": exam_obj.ai_generated_content, 
                "is_de_kt": True, "title": ten_de
            })
            st.download_button("📥 TẢI FILE WORD CHUẨN", data=word_bytes, file_name="De_Thi.docx", use_container_width=True)
        except Exception as e: st.warning(f"Lỗi xuất Word: {e}")
