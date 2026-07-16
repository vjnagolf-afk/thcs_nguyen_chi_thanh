import streamlit as st
from docxtpl import DocxTemplate
import io
import json
import PyPDF2
import os

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # Khởi tạo bộ nhớ tạm để giữ file Word sau khi AI sinh xong
    if "khbd_docx" not in st.session_state:
        st.session_state.khbd_docx = None
    if "khbd_filename" not in st.session_state:
        st.session_state.khbd_filename = ""

    # ==========================================
    # KHU VỰC GIAO DIỆN (UI)
    # ==========================================
    
    # HÀNG 1: 4 Tùy chọn inline
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        danh_sach_mon = [
            "Khoa học Tự nhiên", "Toán", "Ngữ văn", "Tiếng Anh", 
            "Lịch sử và Địa lí", "Tin học", "Công nghệ", "Giáo dục công dân", 
            "Âm nhạc", "Mĩ thuật", "Giáo dục thể chất", "Hoạt động trải nghiệm",
            "Vật lí", "Hóa học", "Sinh học", "Lịch sử", "Địa lí"
        ]
        mon_hoc = st.selectbox("Môn học", danh_sach_mon)
    with col2:
        lop = st.selectbox("Lớp", [str(i) for i in range(6, 13)], index=3) # Mặc định Lớp 9
    with col3:
        hinh_thuc = st.selectbox("Chọn hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    with col4:
        thoi_luong = st.number_input("Số tiết", min_value=1, value=1)

    # HÀNG 2: Tên bài và Chọn phiên bản AI
    col_ten, col_ai = st.columns([3, 1])
    with col_ten:
        ten_bai = st.text_input("Tên bài dạy / Chủ đề")
    with col_ai:
        loai_ai = st.selectbox(
            "🤖 Phiên bản AI", 
            ["Flash (Nhanh, Mặc định)", "Pro (Thông minh, Suy luận sâu)"]
        )
        # Sửa lỗi AttributeError khi ai_engine bị rỗng (chưa nhập Key)
        model_chon = None
        if ai_engine:
            model_chon = ai_engine.MODELS["flash"] if "Flash" in loai_ai else ai_engine.MODELS["pro"]
    # HÀNG 3: Tích chọn và Tải file
    col_file, col_check = st.columns([3, 1])
    with col_file:
        file_tai_len = st.file_uploader("Tài liệu tham khảo (Tùy chọn - Hỗ trợ PDF, TXT)", type=["pdf", "txt"])
    with col_check:
        st.write("") 
        st.write("")
        bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=False)

    # HÀNG 4: Yêu cầu bổ sung
    yeu_cau_them = st.text_area(
        "Yêu cầu bổ sung cho AI (Tùy chọn)", 
        placeholder="Ví dụ: Tích hợp giáo dục AI, sử dụng vi điều khiển, thêm trò chơi khởi động..."
    )

    # ==========================================
    # KHU VỰC NÚT BẤM
    # ==========================================
    st.markdown("---")
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    
    tao_btn = btn_col1.button("🚀 Soạn KHBD", use_container_width=True, type="primary")
    luu_btn = btn_col2.button("💾 Lưu", use_container_width=True)
    
    # Nút Tải File (Chỉ hiển thị khi đã có file trong session_state)
    if st.session_state.khbd_docx:
        btn_col3.download_button(
            label="📥 Tải file Word",
            data=st.session_state.khbd_docx,
            file_name=st.session_state.khbd_filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    else:
        btn_col3.button("📥 Tải file Word", disabled=True, use_container_width=True)

    xoa_btn = btn_col4.button("🗑️ Xóa form", use_container_width=True)

    # ==========================================
    # LOGIC XỬ LÝ SỰ KIỆN
    # ==========================================
    if xoa_btn:
        st.session_state.khbd_docx = None
        st.session_state.khbd_filename = ""
        st.rerun()

    if luu_btn:
        if st.session_state.khbd_docx:
            st.success("Đã lưu Kế hoạch bài dạy vào hệ thống (Giả lập)!")
        else:
            st.warning("Thầy cần tạo KHBD trước khi lưu nhé!")

    if tao_btn:
        if not ten_bai:
            st.warning("Thầy vui lòng nhập Tên bài dạy nhé!")
        elif not ai_engine or not model_chon:
            st.error("🔐 AI Engine chưa kết nối. Vui lòng kiểm tra lại API Key.")
        else:
            with st.spinner(f"🤖 Trợ lý AI đang tư duy..."):
                # 1. Xử lý nội dung file tham khảo
                noi_dung_tham_khao = ""
                if bam_sat and file_tai_len is not None:
                    try:
                        if file_tai_len.name.endswith('.pdf'):
                            pdf_reader = PyPDF2.PdfReader(file_tai_len)
                            for page in pdf_reader.pages:
                                text = page.extract_text()
                                if text:
                                    noi_dung_tham_khao += text + "\n"
                                if len(noi_dung_tham_khao) > 3000: break
                        elif file_tai_len.name.endswith('.txt'):
                            noi_dung_tham_khao = file_tai_len.getvalue().decode("utf-8")[:3000]
                        noi_dung_tham_khao = f"\n\n[TÀI LIỆU]:\n{noi_dung_tham_khao}"
                    except Exception as e:
                        st.warning(f"Lỗi đọc file: {e}")

                # 2. Xây dựng Prompt
                prompt = f"""
                Đóng vai giáo viên {mon_hoc} THCS. Soạn Kế hoạch bài dạy: "{ten_bai}", lớp {lop}, {thoi_luong} tiết.
                Hình thức: {hinh_thuc}. Yêu cầu: {yeu_cau_them}. {noi_dung_tham_khao}
                Trả về JSON chuẩn với các key: CHU_DE, TEN_BAI_HOC, MON_HOC, THOI_LUONG, MUC_TIEU_KIEN_THUC, NANG_LUC_CHUNG, NANG_LUC_DAC_THU, NANG_LUC_SO_VA_AI, PHAM_CHAT, GIAO_VIEN, HOC_SINH, MUC_TIEU, NOI_DUNG, SAN_PHAM, CHUYEN_GIAO_NHIEM_VU_HOC_TAP, THUC_HIEN_NHIEM_VU_HOC_TAP, BAO_CAO_KET_QUA_VA_THAO_LUAN, DANH_GIA_KET_QUA, TEN_HOAT_DONG, HD1_MUC_TIEU, HD1_NOI_DUNG, HD1_SAN_PHAM, CHUYEN_GIAO_NHIEM_VU_HOC_TAP_1, THUC_HIEN_NHIEM_VU_HOC_TAP_1, BAO_CAO_KET_QUA_VA_THAO_LUAN_1, KET_LUAN_1, HD2_MUC_TIEU, HD2_NOI_DUNG, HD2_SAN_PHAM, HD2_CHUYEN_GIAO_NHIEM_VU_HOC_TAP, HD2_THUC_HIEN_NHIEM_VU_HOC_TAP, HD2_BAO_CAO_KET_QUA_VA_THAO_LUAN, HD2_KET_LUAN, LT_MUC_TIEU, LT_NOI_DUNG, LT_SAN_PHAM, CHUYEN_GIAO_NHIEM_VU_HOC_TAP_LT, LT_THUC_HIEN_NHIEM_VU_HOC_TAP, LT_BAO_CAO_KET_QUA_VA_THAO_LUAN, LT_KET_LUAN, VD_MUC_TIEU, VD_NOI_DUNG, VD_SAN_PHAM, TO_CHUC_THUC_HIEN, VD_CHUYEN_GIAO_NHIEM_VU_HOC_TAP, VD_THUC_HIEN_NHIEM_VU_HOC_TAP, VD_BAO_CAO_KET_QUA_VA_THAO_LUAN, VD_KET_LUAN, PHIEU_HOC_TAP.
                """

                # 3. Gọi AI và Render
                try:
                    response_text = ai_engine.generate_text(prompt, model_name=model_chon)
                    clean_json = response_text.replace("```json", "").replace("```", "").strip()
                    data_dict = json.loads(clean_json)

                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    template_path = os.path.join(current_dir, "..", "..", "templates", "KHBD_Mau.docx")
                    
                    doc = DocxTemplate(template_path)
                    doc.render(data_dict)

                    bio = io.BytesIO()
                    doc.save(bio)
                    st.session_state.khbd_docx = bio.getvalue()
                    st.session_state.khbd_filename = f"KHBD_{ten_bai.replace(' ', '_')}.docx"
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")

    # 1. Gọi AI Engine bằng dòng lệnh mới
            try:
                response_text = ai_engine.generate_text(prompt, model_name=model_chon)
                clean_json = response_text.replace("```json", "").replace("```", "").strip()
                data_dict = json.loads(clean_json)
                doc = DocxTemplate(template_path)
                doc.render(data_dict)     
            except Exception as e:
                st.error(f"⚠️ Lỗi trong quá trình AI biên soạn: {e}")
                logger.exception("AI Generation Failed")
            
            # Kịch bản JSON chuẩn (đã fix toàn bộ lỗi ngoặc)
            prompt = f"""
            Đóng vai là một giáo viên {mon_hoc} cấp THCS xuất sắc.
            Hãy soạn Kế hoạch bài dạy cho bài: "{ten_bai}", Lớp {lop}, thời lượng {thoi_luong} tiết.
            Hình thức soạn: {hinh_thuc}
            Yêu cầu chuyên môn bổ sung: {yeu_cau_them}
            {noi_dung_tham_khao}

            NHIỆM VỤ QUAN TRỌNG NHẤT:
            BẮT BUỘC trả về kết quả dưới định dạng JSON nguyên chuẩn. 
            Không viết thêm bất kỳ lời dẫn nào ở đầu hoặc cuối.
            Các Key trong JSON phải khớp chính xác 100% với cấu trúc dưới đây:
            {{
                "CHU_DE": "Tên chủ đề",
                "TEN_BAI_HOC": "{ten_bai}",
                "MON_HOC": "{mon_hoc}",
                "THOI_LUONG": "{thoi_luong}",
                "MUC_TIEU_KIEN_THUC": "Nội dung chi tiết mục tiêu kiến thức",
                "NANG_LUC_CHUNG": "Tự chủ tự học, giao tiếp, hợp tác...",
                "NANG_LUC_DAC_THU": "Năng lực đặc thù",
                "NANG_LUC_SO_VA_AI": "Ứng dụng công cụ số hoặc AI",
                "PHAM_CHAT": "Trung thực, trách nhiệm...",
                "GIAO_VIEN": "Thiết bị của GV",
                "HOC_SINH": "Thiết bị của HS",
                
                "MUC_TIEU": "Mục tiêu HĐ Mở đầu",
                "NOI_DUNG": "Nội dung HĐ Mở đầu",
                "SAN_PHAM": "Sản phẩm dự kiến HĐ Mở đầu",
                "CHUYEN_GIAO_NHIEM_VU_HOC_TAP": "Cách giao nhiệm vụ HĐ Mở đầu",
                "THUC_HIEN_NHIEM_VU_HOC_TAP": "Thực hiện HĐ Mở đầu",
                "BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ Mở đầu",
                "DANH_GIA_KET_QUA": "Đánh giá HĐ Mở đầu",

                "TEN_HOAT_DONG": "Tên hoạt động khám phá",
                "HD1_MUC_TIEU": "Mục tiêu HĐ 2.1",
                "HD1_NOI_DUNG": "Nội dung HĐ 2.1",
                "HD1_SAN_PHAM": "Sản phẩm HĐ 2.1",
                "CHUYEN_GIAO_NHIEM_VU_HOC_TAP_1": "Giao nhiệm vụ HĐ 2.1",
                "THUC_HIEN_NHIEM_VU_HOC_TAP_1": "Thực hiện HĐ 2.1",
                "BAO_CAO_KET_QUA_VA_THAO_LUAN_1": "Báo cáo HĐ 2.1",
                "KET_LUAN_1": "Kết luận HĐ 2.1",

                "HD2_MUC_TIEU": "Mục tiêu HĐ 2.2",
                "HD2_NOI_DUNG": "Nội dung HĐ 2.2",
                "HD2_SAN_PHAM": "Sản phẩm HĐ 2.2",
                "HD2_CHUYEN_GIAO_NHIEM_VU_HOC_TAP": "Giao nhiệm vụ HĐ 2.2",
                "HD2_THUC_HIEN_NHIEM_VU_HOC_TAP": "Thực hiện HĐ 2.2",
                "HD2_BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ 2.2",
                "HD2_KET_LUAN": "Kết luận HĐ 2.2",

                "LT_MUC_TIEU": "Mục tiêu HĐ Luyện tập",
                "LT_NOI_DUNG": "Nội dung HĐ Luyện tập",
                "LT_SAN_PHAM": "Sản phẩm HĐ Luyện tập",
                "CHUYEN_GIAO_NHIEM_VU_HOC_TAP_LT": "Giao nhiệm vụ HĐ Luyện tập",
                "LT_THUC_HIEN_NHIEM_VU_HOC_TAP": "Thực hiện HĐ Luyện tập",
                "LT_BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ Luyện tập",
                "LT_KET_LUAN": "Kết luận HĐ Luyện tập",

                "VD_MUC_TIEU": "Mục tiêu HĐ Vận dụng",
                "VD_NOI_DUNG": "Nội dung HĐ Vận dụng",
                "VD_SAN_PHAM": "Sản phẩm HĐ Vận dụng",
                "TO_CHUC_THUC_HIEN": "Tổ chức thực hiện HĐ Vận dụng",
                "VD_CHUYEN_GIAO_NHIEM_VU_HOC_TAP": "Giao nhiệm vụ HĐ Vận dụng",
                "VD_THUC_HIEN_NHIEM_VU_HOC_TAP": "Thực hiện HĐ Vận dụng",
                "VD_BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ Vận dụng",
                "VD_KET_LUAN": "Kết luận HĐ Vận dụng",

                "PHIEU_HOC_TAP": "Nội dung chi tiết các câu hỏi trong Phiếu học tập"
            }}
            """

            try:
                # Gọi AI 
                response_text = ai_engine.generate_text(prompt, model_name=model_chon)
                
                # Làm sạch dữ liệu rác quanh JSON
                clean_json = response_text.replace("```json", "").replace("```", "").strip()
                data_dict = json.loads(clean_json)

                # ==========================================
                # XỬ LÝ ĐƯỜNG DẪN TỰ ĐỘNG ĐỂ TRÁNH LỖI NOT FOUND
                # ==========================================
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
                template_path = os.path.join(project_root, "templates", "KHBD_Mau.docx")

                # Render vào file mẫu Word
                doc = DocxTemplate(template_path)
                doc.render(data_dict)

                # Lưu vào bộ nhớ ảo
                bio = io.BytesIO()
                doc.save(bio)
                
                st.session_state.khbd_docx = bio.getvalue()
                st.session_state.khbd_filename = f"KHBD_{ten_bai.replace(' ', '_')}.docx"
                
                st.success("🎉 Trợ lý AI đã soạn xong Kế hoạch bài dạy! Thầy hãy nhấn nút Tải file Word ở trên nhé.")
                st.rerun() 
                
            except json.JSONDecodeError:
                st.error("Lỗi: Trợ lý AI trả về sai định dạng. Thầy vui lòng nhấn Xóa form và tạo lại nhé.")
            except Exception as e:
                st.error(f"Có lỗi hệ thống xảy ra: {e}")
