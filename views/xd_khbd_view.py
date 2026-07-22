# -*- coding: utf-8 -*-
import streamlit as st
import PyPDF2
import docx
import pandas as pd
import io
import os
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =========================================================
# 1. CÁC HÀM TIỆN ÍCH VÀ QUẢN LÝ TRẠNG THÁI (STATE)
# =========================================================
def init_session_state():
    if "hoat_dong_list" not in st.session_state:
        st.session_state.hoat_dong_list = []
    if "soan_mode" not in st.session_state:
        st.session_state.soan_mode = "chinh_sua" 
    if "nls_list" not in st.session_state:
        st.session_state.nls_list = []

def add_hoat_dong():
    new_hd = st.session_state.get("new_hoat_dong", "").strip()
    if new_hd and new_hd not in st.session_state.hoat_dong_list:
        st.session_state.hoat_dong_list.append(new_hd)
    st.session_state["new_hoat_dong"] = ""

def set_mode(mode):
    st.session_state.soan_mode = mode

def add_nls_item():
    tp = st.session_state.get("nls_tp", "")
    md = st.session_state.get("nls_md", "")
    nd = st.session_state.get("nls_nd_input", "").strip()
    
    if nd:
        st.session_state.nls_list.append({"thanh_phan": tp, "muc_do": md, "noi_dung": nd})
        st.session_state["nls_nd_input"] = ""

def doc_noi_dung_file(uploaded_file, ai_engine=None):
    if not uploaded_file: return ""
    try:
        ext = uploaded_file.name.split('.')[-1].lower()
        text = ""
        if ext == "pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
        
        elif ext == "docx":
            doc_file = docx.Document(uploaded_file)
            for para in doc_file.paragraphs:
                text += para.text + "\n"
            for table in doc_file.tables:
                for row in table.rows:
                    row_data = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
                    text += " | ".join(row_data) + "\n"
                    
        elif ext in ["xlsx", "xls"]:
            all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
            for sheet_name, df in all_sheets.items():
                text += f"\n--- SHEET: {sheet_name} ---\n"
                text += df.to_string(index=False) + "\n"
                
        elif ext in ["jpg", "png", "jpeg"]:
            text += f"\n[Tệp đính kèm: {uploaded_file.name}. Hệ thống AI vui lòng tự động phân tích hình ảnh này nếu có khả năng Vision.]\n"
                
        return text
    except Exception as e:
        return f"\n[⚠️ Có lỗi khi đọc file {uploaded_file.name}. Chi tiết lỗi: {str(e)}]\n"

def doc_file_mau_local():
    """Hàm tự động đọc file mẫu KHBD trên máy chủ (templates/KHBD_Mau.docx)"""
    path = "templates/KHBD_Mau.docx"
    if os.path.exists(path):
        try:
            doc_file = docx.Document(path)
            text = ""
            for para in doc_file.paragraphs:
                text += para.text + "\n"
            for table in doc_file.tables:
                for row in table.rows:
                    row_data = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
                    text += " | ".join(row_data) + "\n"
            return text
        except Exception:
            return ""
    return ""

def tao_file_word_hoan_hao(van_ban):
    doc_word = docx.Document()
    
    section = doc_word.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

    style = doc_word.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(13)
    
    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = 1.15
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    lines = van_ban.split('\n')
    table_data = []
    num_cols = 0
    
    for line in lines:
        line_str = line.strip()
        if line_str.startswith('|') and line_str.endswith('|'):
            if '---' in line_str or '===' in line_str: 
                continue
            row_cells = [cell.strip().replace('**', '') for cell in line_str.strip('|').split('|')]
            
            if not table_data:
                table_data.append(row_cells)
                num_cols = len(row_cells)
            else:
                row_cells = row_cells[:num_cols] + [''] * max(0, num_cols - len(row_cells))
                table_data.append(row_cells)
            continue
        else:
            if table_data:
                table = doc_word.add_table(rows=len(table_data), cols=len(table_data[0]))
                table.style = 'Table Grid'
                for i, row in enumerate(table_data):
                    for j, cell_text in enumerate(row):
                        if j < len(table.columns): 
                            cell = table.cell(i, j)
                            cell.text = cell_text
                            for paragraph in cell.paragraphs:
                                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                table_data = []
        
        if not line_str: continue
        clean_line = line_str.replace('**', '').replace('*', '').replace('`', '')
        
        if clean_line.startswith('### '):
            p = doc_word.add_paragraph(clean_line.replace('### ', ''))
            p.runs[0].bold = True
        elif clean_line.startswith('## '):
            p = doc_word.add_paragraph(clean_line.replace('## ', ''))
            p.runs[0].bold = True
        elif clean_line.startswith('# '):
            p = doc_word.add_heading(clean_line.replace('# ', ''), level=1)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif clean_line.startswith('- '):
            doc_word.add_paragraph(clean_line[2:], style='List Bullet')
        else:
            doc_word.add_paragraph(clean_line)
            
    if table_data:
        table = doc_word.add_table(rows=len(table_data), cols=len(table_data[0]))
        table.style = 'Table Grid'
        for i, row in enumerate(table_data):
            for j, cell_text in enumerate(row):
                if j < len(table.columns): table.cell(i, j).text = cell_text

    bio = io.BytesIO()
    doc_word.save(bio)
    bio.seek(0)
    return bio

# =========================================================
# 2. GIAO DIỆN CHÍNH (RENDER)
# =========================================================
def render_xd_khbd(ai_engine=None):
    init_session_state()

    st.markdown('''
        <style>
        .stButton button[kind="primary"] { background-color: #9333ea; color: white; border: none; border-radius: 8px; font-weight: bold; transition: 0.3s;}
        .stButton button[kind="primary"]:hover { background-color: #7e22ce; border: none; }
        .stButton button[kind="secondary"] { color: #6b7280; border: 1px solid #e5e7eb; border-radius: 8px; font-weight: 600; background-color: #f9fafb; transition: 0.3s;}
        .stButton button[kind="secondary"]:hover { border-color: #9333ea; color: #9333ea; background-color: #f3e8ff;}
        button:has(div:contains("Thêm vào danh sách")) { background-color: #e81e63 !important; border-color: #e81e63 !important; }
        button:has(div:contains("Thêm vào danh sách")):hover { background-color: #c2185b !important; }
        .upload-card { text-align: center; padding: 10px; }
        .upload-icon { font-size: 2.5rem; color: #9333ea; margin-bottom: 10px; }
        .upload-title { font-weight: bold; font-size: 1.1rem; color: #1f2937; margin-bottom: 5px; }
        .upload-desc { font-size: 0.85rem; color: #6b7280; line-height: 1.4; }
        </style>
    ''', unsafe_allow_html=True)

    THANH_PHAN_NLS = ["1.1. Duyệt, tìm kiếm, lọc dữ liệu", "1.2. Đánh giá dữ liệu", "1.3. Quản lý dữ liệu", "2.1. Tương tác công nghệ số", "2.2. Chia sẻ thông tin", "2.3. Thực hiện trách nhiệm công dân", "2.4. Hợp tác công nghệ số", "2.5. Quy tắc ứng xử", "2.6. Quản lý danh tính số", "3.1. Phát triển nội dung", "3.2. Tích hợp nội dung", "3.3. Bản quyền, giấy phép", "3.4. Lập trình", "4.1. Bảo vệ thiết bị", "4.2. Bảo vệ dữ liệu cá nhân", "4.3. Bảo vệ sức khỏe", "4.4. Bảo vệ môi trường", "5.1. Giải quyết vấn đề kỹ thuật", "5.2. Giải pháp công nghệ", "5.3. Sáng tạo công nghệ", "5.4. Xác định vấn đề NLS", "6.1. Hiểu biết AI", "6.2. Sử dụng AI", "6.3. Đánh giá AI"]
    MUC_DO_NLS = ["-- Tự nhập --", "CB1a", "CB1b", "CB1c", "CB2a", "CB2b", "CB2c", "CB2d", "TC1a", "TC1b", "TC1c", "TC1d", "TC2a", "TC2b", "TC2c", "TC2d", "NC1a", "NC1b", "NC1c", "NC1d"]
    
    tu_dien_nls = {
        "CB1a": "Xác định được nhu cầu thông tin, tìm kiếm dữ liệu, thông tin và nội dung thông qua tìm kiếm đơn giản trong môi trường số.",
        "CB1b": "Biết cách duyệt qua các trang web hoặc tài liệu số cơ bản.",
        "NC1b": "Áp dụng được kỹ thuật tìm kiếm để lấy được dữ liệu, thông tin và nội dung trong môi trường số."
    }

    st.markdown("### 🎛️ Thông tin bài dạy")
    c_khoi, c_mon = st.columns(2)
    with c_khoi:
        st.selectbox("KHỐI LỚP", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], key="khbd_khoi_lop")
    with c_mon:
        st.selectbox("MÔN HỌC", ["Toán", "Ngữ văn", "Tiếng Anh", "Khoa học tự nhiên", "Lịch sử và Địa lí", "Vật lí", "Hóa học", "Sinh học", "Lịch sử", "Địa lí", "Giáo dục công dân", "Tin học", "Công nghệ", "Khác"], key="khbd_mon_hoc")

    st.write("")
    st.markdown("#### ✨ Chế độ tích hợp")
    c_th1, c_th2, c_th3 = st.columns(3)
    with c_th1:
        with st.container(border=True): tich_hop_nls = st.checkbox("**Tích hợp Năng lực số**", key="chk_nls")
    with c_th2:
        with st.container(border=True): tich_hop_ai = st.checkbox("**Tích hợp Năng lực AI**", key="chk_ai")
    with c_th3:
        with st.container(border=True): tich_hop_kt = st.checkbox("**Dạy học khuyết tật**", key="chk_kt")

    st.write("")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1: st.button("📄 CHỈNH SỬA GIÁO ÁN GỐC", type="primary" if st.session_state.soan_mode == "chinh_sua" else "secondary", use_container_width=True, on_click=set_mode, args=("chinh_sua",))
    with c_btn2: st.button("⚡ TỰ ĐỘNG SOẠN TỪ SGK", type="primary" if st.session_state.soan_mode == "tu_dong" else "secondary", use_container_width=True, on_click=set_mode, args=("tu_dong",))
    st.divider()

    if st.session_state.soan_mode == "chinh_sua":
        with st.container(border=True):
            st.markdown("### 📤 Tài liệu đầu vào (Chỉ nên tải lên giáo án 1 tiết hoặc 1 bài)")
            c_up1, c_up2, c_up3 = st.columns(3)
            with c_up1:
                with st.container(border=True):
                    st.markdown('''<div class="upload-card"><div class="upload-icon">📄</div><div class="upload-title">Giáo án gốc</div><div class="upload-desc">Hỗ trợ Word, PDF, JPG, PNG</div></div>''', unsafe_allow_html=True)
                    st.file_uploader("Upload GA", type=["docx", "pdf", "jpg", "jpeg", "png"], accept_multiple_files=True, label_visibility="collapsed", key="file_ga")
                st.markdown("<div style='text-align: center; color: #ef4444; font-size: 0.9em; margin-top: -10px;'>⚠️ Yêu cầu bắt buộc</div>", unsafe_allow_html=True)
            with c_up2:
                with st.container(border=True):
                    st.markdown('''<div class="upload-card"><div class="upload-icon" style="color: #6b7280;">📊</div><div class="upload-title">Tải lên PPCT</div><div class="upload-desc">Dùng để trích xuất NLS</div></div>''', unsafe_allow_html=True)
                    st.file_uploader("Upload PPCT", type=["pdf", "docx", "xlsx"], label_visibility="collapsed", key="file_ppct")
            with c_up3:
                with st.container(border=True):
                    st.markdown('''<div class="upload-card"><div class="upload-icon" style="color: #6b7280;">📋</div><div class="upload-title">Bảng tích hợp AI</div><div class="upload-desc">Để hệ thống tự phân tích</div></div>''', unsafe_allow_html=True)
                    st.file_uploader("Upload AI", type=["pdf", "docx", "xlsx"], label_visibility="collapsed", key="file_ai")
    else:
        st.markdown("### 📄 Thông tin giáo án soạn mới")
        c_cap, c_mau = st.columns(2)
        with c_cap: st.selectbox("Cấp học", ["THCS", "Tiểu học", "THPT"], key="khbd_cap_hoc")
        with c_mau: st.selectbox("Mẫu giáo án", ["Công văn 5512 (Chuẩn Bộ)", "Mẫu rút gọn", "Mẫu tư duy"], key="khbd_mau_giao_an")
        
        c_ten, c_tg = st.columns(2)
        with c_ten: st.text_input("Tên bài dạy", placeholder="VD: Phân thức đại số", key="khbd_ten_bai")
        with c_tg: st.text_input("Thời lượng (Số tiết)", placeholder="VD: 2 tiết", key="khbd_so_tiet")

        st.markdown("**Hình ảnh / PDF SGK cơ sở** *(Khuyến nghị chụp thật nét)*")
        with st.container(border=True):
            st.file_uploader("Kéo thả hoặc Nhấn để tải lên Sách Giáo Khoa", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True, key="file_sgk")

        # Nâng cấp: Tùy chọn cho giáo viên tải lên File Mẫu riêng của trường nếu không muốn dùng mẫu chung
        st.markdown("**📄 Tải lên File Mẫu Giáo Án (Tùy chọn)** *(Nếu không tải lên, AI sẽ tự động đọc file templates/KHBD_Mau.docx trên hệ thống)*")
        with st.container(border=True):
            st.file_uploader("Kéo thả File Word (.docx) chứa bộ khung mẫu của trường", type=["docx"], key="file_template_custom")

        st.markdown("**Kế hoạch Hoạt động (Tùy chọn)**")
        c_input, c_add = st.columns([4, 1])
        with c_input: st.text_input("Nhập hoạt động", placeholder="VD: Tìm hiểu cấu trúc...", key="new_hoat_dong", label_visibility="collapsed", on_change=add_hoat_dong)
        with c_add: st.button("Thêm", on_click=add_hoat_dong, type="primary", use_container_width=True)
        
        if st.session_state.hoat_dong_list:
            for i, hd in enumerate(st.session_state.hoat_dong_list):
                c_tag1, c_tag2 = st.columns([11, 1])
                with c_tag1: st.info(f"📍 {hd}")
                with c_tag2:
                    if st.button("Xóa", key=f"del_{i}"): st.session_state.hoat_dong_list.remove(hd); st.rerun()

        if tich_hop_nls or tich_hop_ai:
            st.markdown("### 📤 Tài liệu tích hợp bổ sung")
            c_tl1, c_tl2 = st.columns(2)
            if tich_hop_nls:
                with c_tl1:
                    with st.container(border=True): st.file_uploader("📄 Tải lên PPCT (Năng lực số)", type=["pdf", "docx", "xlsx"], key="file_ppct_tu_dong")
            if tich_hop_ai:
                with c_tl2:
                    with st.container(border=True): st.file_uploader("📋 Tải lên Bảng tích hợp AI", type=["pdf", "docx", "xlsx"], key="file_ai_tu_dong")

    dang_khuyet_tat_chon = []
    if tich_hop_kt:
        with st.container(border=True):
            st.markdown("#### 🎯 Chọn dạng khuyết tật hòa nhập")
            dang_khuyet_tat_chon = st.pills("Chọn khuyết tật", ["Vận động", "Nghe", "Nói", "Nhìn", "Thần kinh", "Tâm thần", "Trí tuệ", "Tự kỷ", "Khác", "Chung"], selection_mode="multi", default=["Chung"], key="pill_kt")

    if tich_hop_nls:
        with st.container(border=True):
            if st.checkbox("🎯 **Yêu cầu Năng lực số cụ thể (Tùy chọn)**", value=True, key="chk_nls_ct"):
                c_tp, c_md, c_nd = st.columns([1.5, 1, 2.5])
                with c_tp: 
                    st.selectbox("**1. THÀNH PHẦN**", THANH_PHAN_NLS, key="nls_tp")
                with c_md: 
                    chon_md = st.selectbox("**2. MỨC ĐỘ**", MUC_DO_NLS, key="nls_md")
                with c_nd: 
                    noi_dung_mac_dinh = ""
                    if chon_md != "-- Tự nhập --" and chon_md in tu_dien_nls:
                        noi_dung_mac_dinh = tu_dien_nls[chon_md]
                        
                    st.text_area("**3. NỘI DUNG YÊU CẦU**", value=noi_dung_mac_dinh, placeholder="Mô tả...", key="nls_nd_input", height=70)
                
                c_space, c_btn_add = st.columns([3, 1])
                with c_btn_add: st.button("➕ Thêm vào danh sách", type="primary", on_click=add_nls_item, use_container_width=True)
                
                if st.session_state.nls_list:
                    for i, item in enumerate(st.session_state.nls_list):
                        with st.container(border=True):
                            c_info, c_del = st.columns([11, 1])
                            with c_info: st.write(f"**{item['thanh_phan']}** (`{item['muc_do']}`) 👉 *{item['noi_dung']}*")
                            with c_del:
                                if st.button("Xóa", key=f"del_nls_{i}"): st.session_state.nls_list.pop(i); st.rerun()

    st.write("")
    with st.container(border=True):
        is_english = st.checkbox("Giáo án viết bằng ngôn ngữ Tiếng Anh", key="khbd_ngon_ngu")

    st.write("")
    if st.button("⚡ KÍCH HOẠT XỬ LÝ AI", type="primary", use_container_width=True):
        st.session_state.pop("ket_qua_giao_an", None)
        
        if not ai_engine:
            st.error("❌ Chưa cấu hình AI Engine. Lỗi tại file gọi hàm (app.py) chưa truyền tham số `ai_engine`."); st.stop()

        if st.session_state.soan_mode == "chinh_sua" and not st.session_state.get("file_ga"):
            st.error("⚠️ Vui lòng tải lên ít nhất 1 Giáo án gốc để AI có cơ sở phân tích!")
            st.stop()
        elif st.session_state.soan_mode == "tu_dong" and not st.session_state.get("file_sgk"):
            st.error("⚠️ Vui lòng tải lên Sách Giáo Khoa (PDF/Ảnh) để AI biên soạn!")
            st.stop()

        with st.spinner("🧠 AI đang đọc, xử lý dữ liệu và thiết kế giáo án... (Xin đợi 1-3 phút để AI viết thật chi tiết)"):
            try:
                noi_dung_chinh = ""
                noi_dung_mau_khbd = ""
                
                if st.session_state.soan_mode == "chinh_sua":
                    noi_dung_ppct = doc_noi_dung_file(st.session_state.get("file_ppct"))
                    noi_dung_ai_file = doc_noi_dung_file(st.session_state.get("file_ai"))
                    for f in st.session_state.get("file_ga", []): noi_dung_chinh += f"\n--- GIÁO ÁN GỐC ({f.name}) ---\n" + doc_noi_dung_file(f)
                else:
                    noi_dung_ppct = doc_noi_dung_file(st.session_state.get("file_ppct_tu_dong"))
                    noi_dung_ai_file = doc_noi_dung_file(st.session_state.get("file_ai_tu_dong"))
                    for f in st.session_state.get("file_sgk", []): noi_dung_chinh += f"\n--- SÁCH GIÁO KHOA ({f.name}) ---\n" + doc_noi_dung_file(f)
                    
                    # Ưu tiên đọc File Mẫu do GV tải lên, nếu không có thì tự tìm đọc file Mẫu local
                    file_template_custom = st.session_state.get("file_template_custom")
                    if file_template_custom:
                        noi_dung_mau_khbd = doc_noi_dung_file(file_template_custom)
                    else:
                        noi_dung_mau_khbd = doc_file_mau_local()

                if len(noi_dung_chinh) > 80000:
                    st.warning("⚠️ Tài liệu đầu vào rất dài. AI sẽ tự động cô đọng thông tin để xử lý.")
                    noi_dung_chinh = noi_dung_chinh[:80000] + "... [Đã cắt bớt do quá dài]"

                cap_hoc = st.session_state.get('khbd_cap_hoc', 'Không xác định')
                khoi_lop = st.session_state.get('khbd_khoi_lop', 'Không xác định')
                mon_hoc = st.session_state.get('khbd_mon_hoc', 'Không xác định')
                ten_bai = st.session_state.get('khbd_ten_bai', 'Không cung cấp. Căn cứ hoàn toàn vào tài liệu')
                so_tiet = st.session_state.get('khbd_so_tiet', '1 tiết')
                mau_giao_an = st.session_state.get('khbd_mau_giao_an', 'Công văn 5512')
                ngon_ngu = 'Tiếng Anh' if is_english else 'Tiếng Việt'
                
                thong_tin_bai_day = f"Cấp học: {cap_hoc}, Khối lớp: {khoi_lop}, Môn học: {mon_hoc}, Tên bài dạy: {ten_bai}, Thời lượng: {so_tiet}, Mẫu giáo án: {mau_giao_an}, Ngôn ngữ: {ngon_ngu}"
                
                lenh_chinh_sua = """
1. TUYỆT ĐỐI BẢO TOÀN KIẾN THỨC VÀ TÊN BÀI GỐC: Không được thay đổi tên bài, không tự ý thêm bớt kiến thức ngoài SGK.
2. BẢO TỒN NỘI DUNG TỐT: Giữ lại những hoạt động, nội dung hay của giáo án gốc.
3. NÂNG CẤP CHUYÊN MÔN: Phát hiện và âm thầm sửa các lỗi sai kiến thức, thiếu sót logic. Cải tiến mục tiêu, hoạt động cho khoa học hơn.
4. CHI TIẾT HÓA TỐI ĐA (CHỐNG LƯỜI): Không được viết sơ sài, tóm tắt. Bổ sung rõ ràng Hoạt động của Giáo viên (giáo viên nói câu gì, đặt câu hỏi gì), Hoạt động của Học sinh (dự kiến học sinh trả lời ra sao) và Sản phẩm học tập mong đợi.
"""
                lenh_tu_dong = """
1. Xây dựng Kế hoạch bài dạy HOÀN TOÀN MỚI, SIÊU CHI TIẾT DẠNG KỊCH BẢN LÊN LỚP (Ít nhất 2000 - 3000 từ) dựa TRỰC TIẾP vào nội dung SGK đính kèm.
2. CHỐNG BỆNH LƯỜI: TUYỆT ĐỐI KHÔNG VIẾT TẮT, KHÔNG TÓM TẮT. Trong mỗi hoạt động (Khởi động, Hình thành KT, Luyện tập, Vận dụng) phải mô tả chi tiết:
   - GIÁO VIÊN: Nói câu gì để dẫn dắt? Đặt câu hỏi gì? (Viết chi tiết trong ngoặc kép).
   - HỌC SINH: Thực hiện thao tác gì? Dự kiến trả lời câu hỏi ra sao?
   - SẢN PHẨM: Kết quả cụ thể học sinh đạt được.
"""

                chuoi_khung_mau = f"\n\n🔹 [CẤU TRÚC MẪU GIÁO ÁN BẮT BUỘC]\nBẠN BẮT BUỘC PHẢI SAO CHÉP Y HỆT 100% CÁC ĐỀ MỤC LỚN, NHỎ VÀ BẢNG BIỂU của File Mẫu dưới đây. Chỉ thay thế nội dung chuyên môn vào các mục tương ứng:\n{noi_dung_mau_khbd}\n" if noi_dung_mau_khbd else ""

                tich_hop_nls_str = 'CÓ. ' + str(st.session_state.nls_list) if tich_hop_nls else 'KHÔNG'
                tich_hop_ai_str = 'CÓ. Phải thiết kế rõ học sinh dùng AI làm gì, ở hoạt động nào, tạo ra sản phẩm AI gì.' if tich_hop_ai else 'KHÔNG'
                tich_hop_kt_str = ', '.join(dang_khuyet_tat_chon) if (tich_hop_kt and dang_khuyet_tat_chon) else 'KHÔNG'
                hoat_dong_str = str(st.session_state.hoat_dong_list) if st.session_state.hoat_dong_list else 'Không có.'
                ppct_str = noi_dung_ppct if noi_dung_ppct else 'Không cung cấp.'
                ai_file_str = noi_dung_ai_file if noi_dung_ai_file else 'Không cung cấp.'

                prompt = f"""BẠN LÀ CHUYÊN GIA SƯ PHẠM VÀ PHÁT TRIỂN CHƯƠNG TRÌNH ĐÀO TẠO TẠI VIỆT NAM.

NHIỆM VỤ CỐT LÕI: {lenh_chinh_sua if st.session_state.soan_mode == 'chinh_sua' else lenh_tu_dong}

🚨 QUY TẮC BẮT BUỘC (CẤM VI PHẠM - NẾU VI PHẠM BẠN SẼ BỊ ĐÁNH GIÁ 0 ĐIỂM):
1. Bám sát 100% nội dung tài liệu gốc. Không bịa kiến thức bài khác.
2. TUYỆT ĐỐI KHÔNG DÙNG MÃ LATEX. Viết công thức Toán/Lý/Hóa bằng văn bản thường (vd: a/b, x^2, can bac hai) để chống lỗi font Word.
3. BẢO TOÀN THỜI LƯỢNG: Phân bổ thời gian cho các hoạt động khớp với tổng số tiết đã khai báo.
4. HOẠT ĐỘNG BẮT BUỘC: Nếu có [Danh sách Hoạt động mong muốn], BẮT BUỘC phải ưu tiên tích hợp chúng vào các pha dạy học phù hợp. Không được bỏ qua.
5. VIẾT DÀI, SÂU SẮC, ĐẦY ĐỦ CHI TIẾT KỊCH BẢN. Không dùng các từ chung chung như "GV hướng dẫn HS", mà phải ghi rõ "GV yêu cầu HS làm bài tập X trang Y...".{chuoi_khung_mau}

🔹 [THÔNG TIN NỀN TẢNG]
{thong_tin_bai_day}

🔹 [YÊU CẦU TÍCH HỢP ĐẶC BIỆT]
- Tích hợp Năng lực số: {tich_hop_nls_str}
- Tích hợp Năng lực AI: {tich_hop_ai_str}
- Dạy học hòa nhập Khuyết tật: {tich_hop_kt_str}
- Danh sách Hoạt động mong muốn của Giáo viên: {hoat_dong_str}

🔹 [DỮ LIỆU ĐẦU VÀO CỐT LÕI (SÁCH/GIÁO ÁN)]
{noi_dung_chinh}

🔹 [TÀI LIỆU CHỈ ĐẠO BỔ SUNG]
- Nội dung PPCT: {ppct_str}
- Nội dung Bảng AI: {ai_file_str}

Hãy viết ngay giáo án cực kỳ chi tiết (chuẩn Markdown), KHÔNG dạo đầu, KHÔNG chào hỏi.
"""
                ket_qua_ai = ai_engine.generate_text(prompt)
                
                if not ket_qua_ai:
                    st.error("❌ Hệ thống AI không trả về dữ liệu. Vui lòng thử lại.")
                elif isinstance(ket_qua_ai, str) and not ket_qua_ai.startswith("❌"):
                    st.session_state["ket_qua_giao_an"] = ket_qua_ai
                    st.success("🎉 Xử lý Giáo án thành công!")
                else:
                    st.error(f"❌ Lỗi từ AI Engine (Kết quả không hợp lệ hoặc lỗi API): {str(ket_qua_ai)}")
                    
            except Exception as e:
                st.error(f"❌ Lỗi hệ thống trong quá trình thực thi: {str(e)}")

    if st.session_state.get("ket_qua_giao_an"):
        st.markdown("### 📝 Kết quả Giáo án")
        with st.container(border=True): st.markdown(st.session_state["ket_qua_giao_an"])
            
        st.download_button(
            "📥 Tải xuống Giáo án chuẩn (.docx)", 
            data=tao_file_word_hoan_hao(st.session_state["ket_qua_giao_an"]), 
            file_name="Giao_An_Thong_Minh.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
            use_container_width=True
        )
