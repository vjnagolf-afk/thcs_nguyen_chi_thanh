import streamlit as st
import sys
from pathlib import Path
from string import Template
from pypdf import PdfReader
from models.khbd import KHBD

# Hàm đọc nội dung file
def extract_text_from_file(uploaded_file):
    if not uploaded_file: return ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            return "\n".join([p.extract_text() for p in PdfReader(uploaded_file).pages if p.extract_text()])
        elif uploaded_file.name.endswith('.docx'):
            import docx
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        elif uploaded_file.name.endswith('.txt'):
            return uploaded_file.read().decode("utf-8")
    except: return ""
    return ""

# Hàm đọc cấu trúc mẫu
def read_khbd_template():
    root_path = Path(__file__).resolve().parents[1]
    template_path = root_path / "templates" / "khbd_mau.docx"
    if not template_path.exists():
        return "Chuẩn Công văn 5512: I. Mục tiêu, II. Thiết bị, III. Tiến trình..."
    try:
        import docx
        doc = docx.Document(template_path)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except: return "Chuẩn Công văn 5512."

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ - Chuẩn 5512)")

    # Giao diện
    ds_mon = ["Ngữ văn", "Toán", "Ngoại ngữ", "Giáo dục công dân", "Lịch sử và Địa lý", "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", "Công nghệ", "Tin học", "Giáo dục thể chất", "Nghệ thuật", "Giáo dục địa phương", "Hoạt động trải nghiệm, hướng nghiệp"]
    col1, col2, col3 = st.columns([1, 1, 1])
    mon_hoc = col1.selectbox("Môn học", ds_mon)
    lop = col2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    hinh_thuc = col3.selectbox("Chọn hình thức", ["KHBD chi tiết (Chuẩn 5512)"])
    so_tiet = st.number_input("Số tiết", min_value=1, max_value=20, value=2)
    ten_bai_hoc = st.text_input("Tên chủ đề / Tên bài học")
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=True)
    yeu_cau = st.text_area("Yêu cầu bổ sung (Ví dụ: Lồng ghép Năng lực số, tích hợp AI...)")
    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    
    # Logic xử lý
    c1, c2 = st.columns(2)
    if c1.button("🚀 KHỞI TẠO TIẾN TRÌNH", type="primary"):
        if not ten_bai_hoc.strip():
            st.error("⚠️ Vui lòng nhập tên bài học!")
        else:
            with st.spinner("⏳ AI đang thiết kế giáo án chuẩn..."):
                file_context = extract_text_from_file(file_tai_len) if (file_tai_len and bam_sat) else "Dùng kiến thức chuẩn."
                
                # Load prompt
                root_path = Path(__file__).resolve().parents[1]
                with open(root_path / "prompts" / "task_config_khbd.txt", 'r', encoding='utf-8') as f:
                    task_template = f.read()
                
                prompt = Template(task_template).substitute(
                    mon_hoc=mon_hoc, lop=lop, ten_bai_hoc=ten_bai_hoc, so_tiet=so_tiet,
                    yeu_cau=yeu_cau if yeu_cau else "Không có",
                    file_context=file_context[:10000], mau_cau_truc=read_khbd_template()
                )
                
                try:
                    content = ai_engine.generate_text(prompt)
                    khbd = KHBD(ten_bai_hoc, mon_hoc, lop, so_tiet, yeu_cau, content)
                    st.session_state['khbd_data'] = khbd.to_dict()
                    st.rerun()
                except Exception as e: st.error(f"Lỗi AI: {e}")

    if c2.button("🗑️ XÓA DỮ LIỆU"):
        st.session_state.pop('khbd_data', None)
        st.rerun()

    # Hiển thị
    if 'khbd_data' in st.session_state:
        khbd = KHBD.from_dict(st.session_state['khbd_data'])
        st.markdown("---")
        st.markdown(khbd.ai_generated_content)
        
        try:
            from export.export_word import WordExportEngine
            data_export = st.session_state['khbd_data'].copy()
            data_export["is_khbd"] = True
            word_bytes = WordExportEngine.export_to_word(data_export)
            st.download_button("📥 TẢI FILE WORD", data=word_bytes, file_name=f"KHBD_{khbd.ten_bai_hoc}.docx", type="primary")
        except Exception as e: st.error(f"Lỗi xuất file: {e}")
