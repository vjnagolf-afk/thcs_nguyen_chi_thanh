# -*- coding: utf-8 -*-
import streamlit as st
import PyPDF2
import docx
import pandas as pd

def doc_noi_dung_file(uploaded_file):
    """Hàm lõi bóc tách văn bản tự động từ các định dạng file khác nhau"""
    if not uploaded_file:
        return ""
    try:
        ext = uploaded_file.name.split('.')[-1].lower()
        text = ""
        # Xử lý PDF
        if ext == "pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
        # Xử lý Word
        elif ext == "docx":
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        # Xử lý Excel
        elif ext in ["xlsx", "xls"]:
            df = pd.read_excel(uploaded_file)
            text = df.to_string()
        # Xử lý Hình ảnh (Dành cho bản update Multimodal sau này)
        elif ext in ["jpg", "png", "jpeg"]:
            text = f"[Tệp đính kèm là hình ảnh SGK: {uploaded_file.name}. AI vui lòng tự nội suy kiến thức bài học này.]"
        return text
    except Exception as e:
        return f"[⚠️ Có lỗi khi đọc file {uploaded_file.name}. Hệ thống sẽ bỏ qua tệp này.]"
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
    nd = st.session_state.get("nls_nd", "").strip()
    if nd:
        st.session_state.nls_list.append({
            "thanh_phan": tp, 
            "muc_do": md, 
            "noi_dung": nd
        })
        st.session_state["nls_nd"] = ""

def render_xd_khbd(ai_engine=None):
    init_session_state()

    # Nhúng CSS tùy chỉnh
    st.markdown('''
        <style>
        .stButton button[kind="primary"] { background-color: #9333ea; color: white; border: none; border-radius: 8px; font-weight: bold; transition: 0.3s;}
        .stButton button[kind="primary"]:hover { background-color: #7e22ce; border: none; }
        .stButton button[kind="secondary"] { color: #6b7280; border: 1px solid #e5e7eb; border-radius: 8px; font-weight: 600; background-color: #f9fafb; transition: 0.3s;}
        .stButton button[kind="secondary"]:hover { border-color: #9333ea; color: #9333ea; background-color: #f3e8ff;}
        button:has(div:contains("Thêm vào danh sách")) { background-color: #e81e63 !important; border-color: #e81e63 !important; }
        button:has(div:contains("Thêm vào danh sách")):hover { background-color: #c2185b !important; }
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .upload-card { text-align: center; padding: 10px; }
        .upload-icon { font-size: 2.5rem; color: #9333ea; margin-bottom: 10px; }
        .upload-title { font-weight: bold; font-size: 1.1rem; color: #1f2937; margin-bottom: 5px; }
        .upload-desc { font-size: 0.85rem; color: #6b7280; line-height: 1.4; }
        </style>
    ''', unsafe_allow_html=True)
# Dữ liệu Năng lực số, Khối lớp, Môn học
    THANH_PHAN_NLS = [
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu, thông tin và nội dung số", "1.2. Đánh giá dữ liệu, thông tin và nội dung số",
        "1.3. Quản lý dữ liệu, thông tin và nội dung số", "2.1. Tương tác thông qua công nghệ số",
        "2.2. Chia sẻ thông tin và nội dung thông qua công nghệ số", "2.3. Sử dụng công nghệ số để thực hiện trách nhiệm công dân",
        "2.4. Hợp tác thông qua công nghệ số", "2.5. Quy tắc ứng xử trên mạng", "2.6. Quản lý danh tính số",
        "3.1. Phát triển nội dung số", "3.2. Tích hợp và tạo lập lại nội dung số", "3.3. Thực thi bản quyền và giấy phép",
        "3.4. Lập trình", "4.1. Bảo vệ thiết bị", "4.2. Bảo vệ dữ liệu cá nhân và quyền riêng tư",
        "4.3. Bảo vệ sức khỏe và an sinh số", "4.4. Bảo vệ môi trường", "5.1. Giải quyết các vấn đề kỹ thuật",
        "5.2. Xác định nhu cầu và giải pháp công nghệ", "5.3. Sử dụng sáng tạo công nghệ số",
        "5.4. Xác định các vấn đề cần cải thiện về NLS", "6.1. Hiểu biết về trí tuệ nhân tạo",
        "6.2. Sử dụng trí tuệ nhân tạo", "6.3. Đánh giá trí tuệ nhân tạo"
    ]
    MUC_DO_NLS = ["-- Tự nhập --", "CB1a", "CB1b", "CB1c", "CB2a", "CB2b", "CB2c", "CB2d", "TC1a", "TC1b", "TC1c", "TC1d", "TC2a", "TC2b", "TC2c", "TC2d", "NC1a", "NC1b", "NC1c", "NC1d"]
    DANH_SACH_KHOI = ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"]
    DANH_SACH_MON = [
        "Toán", "Ngữ văn", "Tiếng Anh", "Khoa học tự nhiên", "Lịch sử và Địa lí", 
        "Vật lí", "Hóa học", "Sinh học", "Lịch sử", "Địa lí", "Giáo dục công dân", 
        "Giáo dục kinh tế và pháp luật", "Tin học", "Công nghệ", "Giáo dục thể chất", 
        "Nghệ thuật (Âm nhạc, Mĩ thuật)", "Hoạt động trải nghiệm, hướng nghiệp", 
        "Nội dung giáo dục địa phương", "Khác"
    ]

    # =======================================================
    # 1. THÔNG TIN BÀI DẠY & CHẾ ĐỘ TÍCH HỢP
    # =======================================================
    st.markdown("### 🎛️ Thông tin bài dạy")
    c_khoi, c_mon = st.columns(2)
    with c_khoi:
        st.selectbox("KHỐI LỚP", DANH_SACH_KHOI)
    with c_mon:
        st.selectbox("MÔN HỌC", DANH_SACH_MON)

    st.write("")
    st.markdown("#### ✨ Chế độ tích hợp")
    c_th1, c_th2, c_th3 = st.columns(3)
    
    with c_th1:
        with st.container(border=True):
            tich_hop_nls = st.checkbox("**Tích hợp Năng lực số (NLS)**")
            st.caption("Lồng ghép NLS theo PPCT")
    with c_th2:
        with st.container(border=True):
            tich_hop_ai = st.checkbox("**Tích hợp Năng lực AI**")
            st.caption("Lồng ghép AI theo Bảng yêu cầu")
    with c_th3:
        with st.container(border=True):
            tich_hop_kt = st.checkbox("**Tích hợp Dạy học khuyết tật hòa nhập**")
            st.caption("Lồng ghép hỗ trợ HSKT")

    st.write("")
    # =======================================================
    # 2. NÚT CHUYỂN ĐỔI CHẾ ĐỘ (TOGGLE)
    # =======================================================
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        st.button("📄 CHỈNH SỬA GIÁO ÁN GỐC", type="primary" if st.session_state.soan_mode == "chinh_sua" else "secondary", use_container_width=True, on_click=set_mode, args=("chinh_sua",))
    with c_btn2:
        st.button("⚡ TỰ ĐỘNG SOẠN TỪ SGK", type="primary" if st.session_state.soan_mode == "tu_dong" else "secondary", use_container_width=True, on_click=set_mode, args=("tu_dong",))

    st.divider()
# =======================================================
    # 3A. GIAO DIỆN: CHỈNH SỬA GIÁO ÁN GỐC 
    # =======================================================
    if st.session_state.soan_mode == "chinh_sua":
        with st.container(border=True):
            st.markdown("### 📤 Tài liệu đầu vào (Chỉ nên tải lên giáo án 1 tiết hoặc 1 bài)")
            c_up1, c_up2, c_up3 = st.columns(3)
            with c_up1:
                with st.container(border=True):
                    st.markdown('''
                        <div class="upload-card">
                            <div class="upload-icon">📄</div>
                            <div class="upload-title">Tải lên Giáo án gốc</div>
                            <div class="upload-desc">Hỗ trợ Word (.docx), PDF, JPG, PNG.</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    st.file_uploader("Upload GA", type=["docx", "pdf", "jpg", "png", "jpeg"], accept_multiple_files=True, label_visibility="collapsed", key="file_ga")
                st.markdown("<div style='text-align: center; color: #ef4444; font-size: 0.9em; margin-top: -10px;'>⚠️ Yêu cầu bắt buộc</div>", unsafe_allow_html=True)
                
            with c_up2:
                with st.container(border=True):
                    st.markdown('''
                        <div class="upload-card">
                            <div class="upload-icon" style="color: #6b7280;">📊</div>
                            <div class="upload-title">Tải lên PPCT</div>
                            <div class="upload-desc">Trích xuất chính xác năng lực số.</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    st.file_uploader("Upload PPCT", type=["pdf", "docx", "xlsx"], label_visibility="collapsed", key="file_ppct")
                    
            with c_up3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: right; margin-bottom: -15px;'><a href='#' style='font-size: 0.75rem; color: #9333ea; text-decoration: none; font-weight: 600; background: #f3e8ff; padding: 3px 8px; border-radius: 10px;'>Chuyển sang công cụ Tạo Bảng AI ↗</a></div>", unsafe_allow_html=True)
                    st.markdown('''
                        <div class="upload-card">
                            <div class="upload-icon" style="color: #6b7280;">📋</div>
                            <div class="upload-title">Tải lên Bảng tích hợp AI</div>
                            <div class="upload-desc">Để hệ thống tự động phân tích</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    st.file_uploader("Upload AI", type=["pdf", "docx", "xlsx"], label_visibility="collapsed", key="file_ai")
                    
        st.warning("**Lời khuyên:** Xin đừng đưa cả 1 kỳ học hoặc hàng chục trang giáo án vào cùng 1 lúc! Hãy tải **từng bài một (1 - 3 tiết)** để tránh AI bị ngợp và tốn Quota.", icon="⚠️")

    # =======================================================
    # 3B. GIAO DIỆN: TỰ ĐỘNG SOẠN TỪ SGK
    # =======================================================
    else:
        st.markdown("### 📄 Thông tin giáo án soạn mới")
        c_cap, c_mau = st.columns(2)
        with c_cap:
            st.selectbox("Cấp học", ["THCS", "Tiểu học", "THPT"])
        with c_mau:
            st.selectbox("Mẫu giáo án", ["Công văn 5512 (Chuẩn Bộ)", "Mẫu rút gọn", "Mẫu tư duy"])

        c_ten, c_tg = st.columns(2)
        with c_ten:
            st.text_input("Tên bài dạy", placeholder="VD: Định dạng văn bản")
        with c_tg:
            st.text_input("Thời lượng (Số tiết)", placeholder="VD: 2 tiết")

        st.markdown("**Hình ảnh / PDF SGK cơ sở** *(Khuyến nghị chụp thật nét)*")
        with st.container(border=True):
            st.file_uploader("Kéo thả hoặc Nhấn để tải lên Sách Giáo Khoa", type=["pdf", "jpg", "png"], accept_multiple_files=True, key="file_sgk")
# =======================================================
    # 5. TÙY CHỌN NGÔN NGỮ & LÕI XỬ LÝ BACKEND AI
    # =======================================================
    st.write("")
    with st.container(border=True):
        is_english = st.checkbox("Giáo án viết bằng ngôn ngữ Tiếng Anh")

    st.write("")
    if st.button("⚡ KÍCH HOẠT XỬ LÝ AI", type="primary", use_container_width=True):
        
        if not ai_engine:
            st.error("❌ Hệ thống chưa khởi tạo AI Engine. Vui lòng kiểm tra lại cấu hình API Key.")
            st.stop()

        # Hiển thị vòng quay loading siêu mượt
        with st.spinner(f"🧠 AI đang đọc tài liệu và {'phân tích giáo án cũ' if st.session_state.soan_mode == 'chinh_sua' else 'soạn giáo án mới'}... (Có thể mất 30s - 1 phút)"):
            try:
                # ---------------------------------------------------------
                # BƯỚC 1: BÓC TÁCH TOÀN BỘ DỮ LIỆU ĐẦU VÀO
                # ---------------------------------------------------------
                noi_dung_chinh = ""
                
                # 1.1 Đọc file Giáo án hoặc SGK
                if st.session_state.soan_mode == "chinh_sua":
                    files_ga = st.session_state.get("file_ga", [])
                    if files_ga:
                        for f in files_ga:
                            noi_dung_chinh += f"\n--- NỘI DUNG GIÁO ÁN GỐC ({f.name}) ---\n" + doc_noi_dung_file(f)
                    else:
                        noi_dung_chinh += "\n[Giáo viên không tải lên giáo án gốc. AI tự tạo dựa trên tên bài.]"
                else:
                    files_sgk = st.session_state.get("file_sgk", [])
                    if files_sgk:
                        for f in files_sgk:
                            noi_dung_chinh += f"\n--- NỘI DUNG SÁCH GIÁO KHOA ({f.name}) ---\n" + doc_noi_dung_file(f)
                    else:
                        noi_dung_chinh += "\n[Giáo viên không tải lên SGK. AI tự thiết kế theo kiến thức chuẩn.]"

                # 1.2 Đọc file PPCT và File Bảng AI
                noi_dung_ppct = doc_noi_dung_file(st.session_state.get("file_ppct"))
                noi_dung_ai_file = doc_noi_dung_file(st.session_state.get("file_ai"))

                # ---------------------------------------------------------
                # BƯỚC 2: XÂY DỰNG PROMPT SƯ PHẠM (KỸ THUẬT PROMPT ENGINEERING)
                # ---------------------------------------------------------
                prompt = f"""BẠN LÀ MỘT CHUYÊN GIA SƯ PHẠM VÀ PHÁT TRIỂN CHƯƠNG TRÌNH ĐÀO TẠO TẠI VIỆT NAM.

NHIỆM VỤ: {'Phân tích, chỉnh sửa và nâng cấp giáo án dựa trên bản gốc do giáo viên cung cấp' if st.session_state.soan_mode == 'chinh_sua' else 'Xây dựng một kế hoạch bài dạy (giáo án) hoàn toàn mới dựa trên dữ liệu Sách giáo khoa'}.

🔹 [THÔNG TIN CẤU HÌNH BÀI DẠY]
- Ngôn ngữ đầu ra: {'Tiếng Anh (BẮT BUỘC toàn bộ giáo án bằng Tiếng Anh)' if is_english else 'Tiếng Việt'}
- Yêu cầu Tích hợp Năng lực số: {'CÓ' if tich_hop_nls else 'KHÔNG'}
- Yêu cầu Tích hợp Năng lực AI: {'CÓ' if tich_hop_ai else 'KHÔNG'}
- Dạy học hòa nhập (Khuyết tật): {'CÓ' if tich_hop_kt else 'KHÔNG'}

🔹 [DỮ LIỆU ĐẦU VÀO CỐT LÕI]
{noi_dung_chinh}

🔹 [TÀI LIỆU & YÊU CẦU BỔ SUNG TỪ GIÁO VIÊN]
- Trích xuất PPCT: {noi_dung_ppct if noi_dung_ppct else 'Không đính kèm.'}
- Trích xuất Bảng tích hợp AI: {noi_dung_ai_file if noi_dung_ai_file else 'Không đính kèm, hãy tự lồng ghép thông minh.'}
- Các hoạt động cụ thể GV mong muốn: {str(st.session_state.hoat_dong_list) if st.session_state.hoat_dong_list else 'Không có.'}
- Yêu cầu Năng lực số cụ thể (Mức độ/Thành phần): {str(st.session_state.nls_list) if tich_hop_nls and st.session_state.nls_list else 'Hãy tự lồng ghép tự nhiên nhất.'}

🔹 [YÊU CẦU ĐẦU RA SƯ PHẠM]
1. Trình bày bài giảng bằng định dạng Markdown rõ ràng, chuyên nghiệp.
2. Tuân thủ tuyệt đối cấu trúc Công văn 5512 gồm 4 hoạt động: Khởi động, Hình thành kiến thức, Luyện tập, Vận dụng.
3. Mỗi hoạt động cần nêu rõ: Mục tiêu, Nội dung, Sản phẩm, và Tổ chức thực hiện.
4. Lồng ghép mượt mà các công cụ số/AI và phương pháp hỗ trợ khuyết tật (nếu có yêu cầu) vào các pha của bài học mà không làm gượng ép kiến thức nền.
5. TRẢ LỜI TRỰC TIẾP VÀO NỘI DUNG GIÁO ÁN, KHÔNG DẠO ĐẦU LỜI CHÀO.
"""
                # ---------------------------------------------------------
                # BƯỚC 3: GỬI YÊU CẦU CHO GEMINI VÀ NHẬN KẾT QUẢ
                # ---------------------------------------------------------
                ket_qua_ai = ai_engine.generate_text(prompt)
                
                if ket_qua_ai and not str(ket_qua_ai).startswith("❌"):
                    st.session_state["ket_qua_giao_an"] = ket_qua_ai
                    st.success("🎉 Khởi tạo Giáo án thành công!")
                else:
                    st.error(f"❌ Lỗi từ AI Engine: {ket_qua_ai}")

            except Exception as e:
                st.error(f"❌ Có lỗi trong quá trình bóc tách tệp hoặc gọi AI: {str(e)}")
# =======================================================
    # 6. KHỐI GIAO DIỆN HIỂN THỊ KẾT QUẢ SAU KHI CHẠY
    # =======================================================
    if st.session_state.get("ket_qua_giao_an"):
        st.markdown("### 📝 Kết quả Giáo án đã xử lý")
        with st.container(border=True):
            # Render Markdown giáo án tuyệt đẹp trên giao diện web
            st.markdown(st.session_state["ket_qua_giao_an"])
            
        # --- HÀM TỰ ĐỘNG CHUYỂN ĐỔI KẾT QUẢ AI SANG FILE WORD (.DOCX) ---
        import io
        import docx

        def tao_file_word(van_ban):
            doc = docx.Document()
            
            # Tách nội dung AI trả về thành từng dòng để đưa vào Word
            for line in van_ban.split('\n'):
                line = line.strip()
                if not line:
                    continue
                # Xử lý các thẻ tiêu đề (Heading)
                if line.startswith('### '):
                    doc.add_heading(line.replace('### ', '').replace('**', ''), level=3)
                elif line.startswith('## '):
                    doc.add_heading(line.replace('## ', '').replace('**', ''), level=2)
                elif line.startswith('# '):
                    doc.add_heading(line.replace('# ', '').replace('**', ''), level=1)
                # Xử lý gạch đầu dòng
                elif line.startswith('- ') or line.startswith('* '):
                    doc.add_paragraph(line[2:].replace('**', ''), style='List Bullet')
                else:
                    # Xóa các dấu ** in đậm của Markdown để văn bản Word sạch sẽ
                    doc.add_paragraph(line.replace('**', ''))
            
            # Lưu file Word vào bộ nhớ đệm (BytesIO) để Streamlit tải về
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            return bio

        # Chạy hàm tạo file Word
        docx_file = tao_file_word(st.session_state["ket_qua_giao_an"])

        # Nút tải xuống đã được nâng cấp thành file .docx
        st.download_button(
            "📥 Tải xuống Giáo án (.docx)", 
            data=docx_file, 
            file_name="Giao_An_Thong_Minh.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
