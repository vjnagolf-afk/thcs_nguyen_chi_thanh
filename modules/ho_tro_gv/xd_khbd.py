import streamlit as st
from docxtpl import DocxTemplate
import io
import json
import PyPDF2

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # Khởi tạo bộ nhớ tạm để giữ file Word sau khi AI sinh xong (tránh bị mất khi bấm nút khác)
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
        lop = st.selectbox("Lớp", [str(i) for i in range(6, 13)], index=3) # Mặc định để Lớp 9
    with col3:
        hinh_thuc = st.selectbox("Chọn hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    with col4:
        thoi_luong = st.number_input("Số tiết", min_value=1, value=1)

    # HÀNG 2: Tên bài
    ten_bai = st.text_input("Tên bài dạy / Chủ đề")

    # HÀNG 3: Tích chọn và Tải file
    col_file, col_check = st.columns([3, 1])
    with col_file:
        file_tai_len = st.file_uploader("Tài liệu tham khảo (Tùy chọn - Hỗ trợ PDF, TXT)", type=["pdf", "txt"])
    with col_check:
        st.write("") # Tạo khoảng trống để căn giữa với ô upload
        st.write("")
        bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=False)

    # HÀNG 4: Yêu cầu bổ sung
    yeu_cau_them = st.text_area(
        "Yêu cầu bổ sung cho AI (Tùy chọn)", 
        placeholder="Ví dụ: Tích hợp giáo dục AI, sử dụng vi điều khiển, thêm trò chơi khởi động..."
    )

    # ==========================================
    # KHU VỰC NÚT BẤM (HÀNG 5)
    # ==========================================
    st.markdown("---")
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    
    tao_btn = btn_col1.button("🚀 Soạn KHBD", use_container_width=True, type="primary")
    luu_btn = btn_col2.button("💾 Lưu", use_container_width=True)
    xoa_btn = btn_col4.button("🗑️ Xóa form", use_container_width=True)

    # Nút Xóa: Khởi động lại giao diện và xóa bộ nhớ tạm
    if xoa_btn:
        st.session_state.khbd_docx = None
        st.session_state.khbd_filename = ""
        st.rerun()

    # Nút Lưu (Hiển thị thông báo, sẽ kết nối Database sau)
    if luu_btn:
        if st.session_state.khbd_docx:
            st.success("Đã lưu Kế hoạch bài dạy vào hệ thống (Giả lập)!")
        else:
            st.warning("Thầy cần tạo KHBD trước khi lưu nhé!")

    # Nút Tải File (Chỉ hiển thị nút TẢI khi đã có file trong session_state)
    if st.session_state.khbd_docx:
        btn_col3.download_button(
            label="📥 Tải file Word",
            data=st.session_state.khbd_docx,
            file_name=st.session_state.khbd_filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    else:
        # Nếu chưa có file thì hiển thị nút mờ (disabled)
        btn_col3.button("📥 Tải file Word", disabled=True, use_container_width=True)

    # ==========================================
    # LOGIC XỬ LÝ AI
    # ==========================================
    if tao_btn:
        if not ten_bai:
            st.warning("Thầy vui lòng nhập Tên bài dạy nhé!")
            return
            
        if not ai_engine:
            st.error("AI Engine chưa được kết nối. Vui lòng kiểm tra API Key.")
            return

        with st.spinner(f"🤖 Trợ lý AI đang tư duy và biên soạn KHBD theo hình thức {hinh_thuc}..."):
            
            # Xử lý nội dung file nếu thầy có đính kèm và tích chọn "Bám sát"
            noi_dung_tham_khao = ""
            if bam_sat and file_tai_len is not None:
                try:
                    if file_tai_len.name.endswith('.pdf'):
                        pdf_reader = PyPDF2.PdfReader(file_tai_len)
                        for page in pdf_reader.pages:
                            noi_dung_tham_khao += page.extract_text() + "\n"
                    elif file_tai_len.name.endswith('.txt'):
                        noi_dung_tham_khao = file_tai_len.getvalue().decode("utf-8")
                    
                    noi_dung_tham_khao = f"\n\n[TÀI LIỆU THAM KHẢO BẮT BUỘC BÁM SÁT]:\n{noi_dung_tham_khao[:3000]}" # Lấy 3000 ký tự đầu để tránh quá tải AI
                except Exception as e:
                    st.warning("Có lỗi khi đọc file, AI sẽ soạn theo dữ liệu mặc định.")
            
            # Kịch bản (Prompt) 
            prompt = f"""
            Đóng vai là một giáo viên {mon_hoc} cấp THCS xuất sắc.
            Hãy soạn Kế hoạch bài dạy cho bài: "{ten_bai}", Lớp {lop}, thời lượng {thoi_luong} tiết.
            Hình thức soạn: {hinh_thuc} (Hãy điều chỉnh nội dung chi tiết cho phù hợp với hình thức này).
            Yêu cầu chuyên môn bổ sung: {yeu_cau_them}
            {noi_dung_tham_khao}

            NHIỆM VỤ QUAN TRỌNG NHẤT:
            Dù soạn theo hình thức nào, bạn BẮT BUỘC phải trả về kết quả dưới định dạng JSON nguyên chuẩn (không có markdown). 
            Các Key trong JSON phải khớp chính xác 100% với cấu trúc dưới đây để tôi đổ vào khuôn Word (Nếu mục nào trong hình thức {hinh_thuc} không cần, hãy để chuỗi rỗng ""):
            {{
                "CHU_DE": "Tên chủ đề",
                "TEN_BAI_HOC": "{ten_bai}",
                "MON_HOC": "{mon_hoc}",
                "THOI_LUONG": "{thoi_luong}",
                "MUC_TIEU_KIEN_THUC": "Nội dung chi tiết mục tiêu kiến thức",
                "NANG_LUC_CHUNG": "Tự chủ tự học, giao tiếp, hợp tác...",
                "NANG_LUC_DAK_THU": "Năng lực đặc thù của môn học",
                "NANG_LUC_SO_VA_AI": "Ứng dụng công cụ số hoặc nhận thức cơ bản về AI trong bài học",
                "PHAM_CHAT": "Trung thực, trách nhiệm...",
                "GIAO_VIEN": "Máy chiếu, phiếu học tập, AI chatbot...",
                "HOC_SINH": "Sách vở, dụng cụ...",
                
                "HOAT_DONG_MO_DAU": "Tên hoạt động khởi động",
                "MUC_TIEU": "Mục tiêu HĐ 1",
                "NOI_DUNG": "Nội dung trò chơi/tình huống HĐ 1",
                "SAN_PHAM": "Câu trả lời dự kiến HĐ 1",
                "CHUYEN_GIAO_NHIEM_VU_HOC_TAP": "Cách GV giao nhiệm vụ HĐ 1",
                "THUC_HIEN_NHIEM_VU_HOC_TAP": "HS thực hiện HĐ 1",
                "BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo kết quả HĐ 1",
                "DANH_GIA_KET_QUA": "GV đánh giá HĐ 1",

                "TEN_HOAT_DONG": "Tên hoạt động khám phá 2.1",
                "HD1_MUC_TIEU": "Mục tiêu HĐ 2.1",
                "HD1_NOI_DUNG": "Nội dung HĐ 2.1",
                "HD1_SAN_PHAM": "Sản phẩm HĐ 2.1",
                "CHUYEN_GIAO_NHIEM_VU_HOC_TAP_1": "Cách giao nhiệm vụ HĐ 2.1",
                "THUC_HIEN_NHIEM_VU_HOC_TAP_1": "HS thực hiện HĐ 2.1",
                "BAO_CAO_KET_QUA_VA_THAO_LUAN_1": "Báo cáo HĐ 2.1",
                "KET_LUAN_1": "Chốt kiến thức HĐ 2.1",

                "HD2_MUC_TIEU": "Mục tiêu HĐ 2.2",
                "HD2_NOI_DUNG": "Nội dung HĐ 2.2",
                "HD2_SAN_PHAM": "Sản phẩm HĐ 2.2",
                "HD2_CHUYEN_GIAO_NHIEM_VU_HOC_TAP": "Cách giao nhiệm vụ HĐ 2.2",
                "HD2_THUC_HIEN_NHIEM_VU_HOC_TAP": "HS thực hiện HĐ 2.2",
                "HD2_BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ 2.2",
                "HD2_KET_LUAN": "Chốt kiến thức HĐ 2.2",

                "LT_MUC_TIEU": "Mục tiêu HĐ Luyện tập",
                "LT_NOI_DUNG": "Nội dung HĐ Luyện tập",
                "LT_SAN_PHAM": "Sản phẩm HĐ Luyện tập",
                "CHUYEN_GIAO_NHIEM_VU_HOC_TAP_LT": "Cách giao nhiệm vụ HĐ Luyện tập",
                "LT_THUC_HIEN_NHIEM_VU_HOC_TAP": "HS thực hiện HĐ Luyện tập",
                "LT_BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ Luyện tập",
                "LT_KET_LUAN": "Chốt kỹ năng HĐ Luyện tập",

                "VD_MUC_TIEU": "Mục tiêu HĐ Vận dụng",
                "VD_NOI_DUNG": "Nhiệm vụ thực tế HĐ Vận dụng",
                "VD_SAN_PHAM": "Sản phẩm thực hành HĐ Vận dụng",
                "TO_CHUC_THUC_HIEN": "Cách tổ chức thực hiện HĐ Vận dụng",
                "VD_CHUYEN_GIAO_NHIEM_VU_HOC_TAP": "Giao việc về nhà",
                "VD_THUC_HIEN_NHIEM_VU_HOC_TAP": "HS thực hiện HĐ Vận dụng",
                "VD_BAO_CAO_KET_QUA_VA_THAO_LUAN": "Báo cáo HĐ Vận dụng",
                "VD_KET_LUAN": "Đánh giá chung HĐ Vận dụng",

                "TIET_2": "Hướng dẫn hoặc nội dung chuyển tiếp sang Tiết 2",
                "PHU_LUC": "Ghi chú phụ lục",
                "PHIEU_HOC_TAP": "Nội dung chi tiết các câu hỏi trong Phiếu học tập"
            }}
            """

            try:
                response_text = ai_engine.generate_text(prompt)
                
                clean_json = response_text.replace("```json", "").replace("```", "").strip()
                data_dict = json.loads(clean_json)

                doc = DocxTemplate("templates/KHBD_Mau.docx")
                doc.render(data_dict)

                bio = io.BytesIO()
                doc.save(bio)
                
                # Lưu file vào bộ nhớ tạm của hệ thống để hiển thị nút Tải xuống
                st.session_state.khbd_docx = bio.getvalue()
                st.session_state.khbd_filename = f"KHBD_{ten_bai.replace(' ', '_')}.docx"
                
                st.success("🎉 Trợ lý AI đã soạn xong Kế hoạch bài dạy! Thầy hãy nhấn nút Tải file Word ở trên nhé.")
                # Tải lại UI để nút "Tải file Word" được kích hoạt
                st.rerun() 
                
            except json.JSONDecodeError:
                st.error("Lỗi: Trợ lý AI trả về sai định dạng. Thầy vui lòng nhấn Xóa và tạo lại nhé.")
            except Exception as e:
                st.error(f"Có lỗi hệ thống xảy ra: {e}")
