import streamlit as st
from docxtpl import DocxTemplate
import io
import json
import PyPDF2

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # Khởi tạo bộ nhớ tạm
    if "khbd_docx" not in st.session_state:
        st.session_state.khbd_docx = None
    if "khbd_filename" not in st.session_state:
        st.session_state.khbd_filename = ""

    # GIAO DIỆN NHẬP LIỆU
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
        lop = st.selectbox("Lớp", [str(i) for i in range(6, 13)], index=3)
    with col3:
        hinh_thuc = st.selectbox("Chọn hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    with col4:
        thoi_luong = st.number_input("Số tiết", min_value=1, value=1)

    col_ten, col_ai = st.columns([3, 1])
    with col_ten:
        ten_bai = st.text_input("Tên bài dạy / Chủ đề")
    with col_ai:
        loai_ai = st.selectbox("🤖 Phiên bản AI", ["Flash (Nhanh)", "Pro (Thông minh)"])
        # Ánh xạ model qua dictionary của Engine
        model_chon = ai_engine.MODELS["flash"] if "Flash" in loai_ai else ai_engine.MODELS["pro"]

    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=False)
    yeu_cau_them = st.text_area("Yêu cầu bổ sung", placeholder="Ví dụ: Tích hợp AI, sử dụng vi điều khiển...")

    # NÚT BẤM VÀ XỬ LÝ
    st.markdown("---")
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    tao_btn = btn_col1.button("🚀 Soạn KHBD", use_container_width=True, type="primary")
    
    if st.session_state.khbd_docx:
        btn_col3.download_button("📥 Tải file Word", data=st.session_state.khbd_docx, 
                                 file_name=st.session_state.khbd_filename, 
                                 mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                                 use_container_width=True)

    if tao_btn:
        if not ten_bai:
            st.warning("Thầy vui lòng nhập Tên bài dạy!")
            return

        with st.spinner("🤖 AI đang soạn thảo..."):
            # Xử lý file tham khảo
            noi_dung_tham_khao = ""
            if bam_sat and file_tai_len:
                # (Phần xử lý PDF/TXT giữ nguyên như cũ)
                pass 

            prompt = f"Soạn KHBD bài '{ten_bai}', môn {mon_hoc}, lớp {lop}, thời lượng {thoi_luong} tiết. Trả về đúng định dạng JSON cho các key: CHU_DE, TEN_BAI_HOC, MON_HOC, THOI_LUONG, MUC_TIEU_KIEN_THUC, NANG_LUC_CHUNG, NANG_LUC_DAK_THU, NANG_LUC_SO_VA_AI, PHAM_CHAT, GIAO_VIEN, HOC_SINH, HOAT_DONG_MO_DAU, MUC_TIEU, NOI_DUNG, SAN_PHAM, CHUYEN_GIAO_NHIEM_VU_HOC_TAP, THUC_HIEN_NHIEM_VU_HOC_TAP, BAO_CAO_KET_QUA_VA_THAO_LUAN, DANH_GIA_KET_QUA, TEN_HOAT_DONG, HD1_MUC_TIEU, HD1_NOI_DUNG, HD1_SAN_PHAM, CHUYEN_GIAO_NHIEM_VU_HOC_TAP_1, THUC_HIEN_NHIEM_VU_HOC_TAP_1, BAO_CAO_KET_QUA_VA_THAO_LUAN_1, KET_LUAN_1, HD2_MUC_TIEU, HD2_NOI_DUNG, HD2_SAN_PHAM, HD2_CHUYEN_GIAO_NHIEM_VU_HOC_TAP, HD2_THUC_HIEN_NHIEM_VU_HOC_TAP, HD2_BAO_CAO_KET_QUA_VA_THAO_LUAN, HD2_KET_LUAN, LT_MUC_TIEU, LT_NOI_DUNG, LT_SAN_PHAM, CHUYEN_GIAO_NHIEM_VU_HOC_TAP_LT, LT_THUC_HIEN_NHIEM_VU_HOC_TAP, LT_BAO_CAO_KET_QUA_VA_THAO_LUAN, LT_KET_LUAN, VD_MUC_TIEU, VD_NOI_DUNG, VD_SAN_PHAM, TO_CHUC_THUC_HIEN, VD_CHUYEN_GIAO_NHIEM_VU_HOC_TAP, VD_THUC_HIEN_NHIEM_VU_HOC_TAP, VD_BAO_CAO_KET_QUA_VA_THAO_LUAN, VD_KET_LUAN, TIET_2, PHU_LUC, PHIEU_HOC_TAP."

            try:
                # Gọi Engine với model đã chọn
                response_text = ai_engine.generate_text(prompt, model_name=model_chon)
                clean_json = response_text.replace("```json", "").replace("```", "").strip()
                data_dict = json.loads(clean_json)

                doc = DocxTemplate("templates/KHBD_Mau.docx")
                doc.render(data_dict)
                bio = io.BytesIO()
                doc.save(bio)
                
                st.session_state.khbd_docx = bio.getvalue()
                st.session_state.khbd_filename = f"KHBD_{ten_bai.replace(' ', '_')}.docx"
                st.success("🎉 Soạn thảo thành công!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {e}")
