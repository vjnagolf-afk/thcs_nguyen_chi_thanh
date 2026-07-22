# -*- coding: utf-8 -*-
"""
============================================================
VIEW: GIAO DIỆN XÂY DỰNG KẾ HOẠCH BÀI DẠY
FILE: views/xd_khbd_view.py
============================================================
"""
import streamlit as st
import os
import tempfile

# IMPORT LOGIC TỪ FILE DATA
from views.xd_khbd_data import (
    KHUNG_NLS_GV, KHUNG_NLS_HS, init_session_state,
    read_multiple_files, read_uploaded_file, read_template_local,
    add_nls, format_nls, add_activity, build_prompt, generate_ai
)

try:
    from export.word_export_engine import WordExportEngine
    from export.template_loader import TemplateLoader
except ImportError as e:
    WordExportEngine = None
    TemplateLoader = None
    EXPORT_WORD_IMPORT_ERROR = str(e)

# ============================================================
# GIAO DIỆN ĐIỀU KHIỂN CHÍNH (RENDER VIEW)
# ============================================================
def render_xd_khbd(ai_engine=None):
    init_session_state()
    st.title("📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY (CHUẨN 5512 & TT18)")
    
    st.subheader("🎛️ Thông tin bài dạy")
    col1, col2 = st.columns(2)
    with col1:
        khoi_lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], key="khbd_khoi_lop")
    with col2:
        mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Tiếng Anh", "Khoa học tự nhiên", "Vật lí", "Hóa học", "Sinh học", "Lịch sử và Địa lí", "Tin học", "Công nghệ", "Khác"], key="khbd_mon_hoc")
        
    st.subheader("✨ Chế độ soạn")
    mode = st.radio("Chọn chế độ", ["chinh_sua", "tu_dong"], format_func=lambda x: "📄 Chỉnh sửa giáo án gốc" if x == "chinh_sua" else "⚡ Tự động soạn từ SGK", key="khbd_mode", horizontal=True)
    
    range_trang = ""
    if mode == "tu_dong":
        st.info("💡 Nên giới hạn phạm vi trang để AI trích xuất siêu chi tiết.")
        range_trang = st.text_input("Phạm vi trang SGK cần soạn (Ví dụ: 45-48)", key="khbd_range_trang")

    st.subheader("📤 Tài liệu đầu vào")
    col_up1, col_up2, col_up3, col_up4 = st.columns(4)
    if mode == "chinh_sua":
        file_ga = col_up1.file_uploader("Giáo án gốc", type=["docx", "pdf"], accept_multiple_files=True, key="khbd_file_ga")
        file_sgk = []
    else:
        file_ga = []
        file_sgk = col_up1.file_uploader("SGK / Tài liệu", type=["pdf", "docx"], accept_multiple_files=True, key="khbd_file_sgk")
        
    file_ppct = col_up2.file_uploader("PPCT (Tùy chọn)", type=["pdf", "docx", "xlsx", "xls"], key="khbd_file_ppct")
    file_ai = col_up3.file_uploader("Bảng AI (Tùy chọn)", type=["pdf", "docx", "xlsx", "xls"], key="khbd_file_ai")
    file_template = col_up4.file_uploader("Mẫu KHBD trường", type=["docx"], key="khbd_file_template")

    st.subheader("📚 Thông tin chi tiết")
    col_td1, col_td2 = st.columns(2)
    with col_td1: ten_bai = st.text_input("Tên bài dạy", key="khbd_ten_bai")
    with col_td2: so_tiet = st.text_input("Thời lượng tiết học", value="1 tiết", key="khbd_so_tiet")

    st.subheader("🔧 Tích hợp chuyên sâu")
    c_th1, c_th2, c_th3 = st.columns(3)
    with c_th1: tich_hop_nls = st.checkbox("Năng lực số (TT18)", key="khbd_tich_hop_nls")
    with c_th2: tich_hop_ai = st.checkbox("Năng lực AI", key="khbd_tich_hop_ai")
    with c_th3: tich_hop_hoa_nhap = st.checkbox("Dạy học hòa nhập", key="khbd_tich_hop_hoa_nhap")

    nhu_cau_hoa_nhap = []
    if tich_hop_hoa_nhap:
        with st.container(border=True):
            st.markdown("##### 🫂 Lựa chọn loại khuyết tật/nhu cầu:")
            nhu_cau_hoa_nhap = st.multiselect("Chọn đối tượng", ["Vận động", "Nghe", "Nói", "Nhìn", "Thần kinh", "Tâm thần", "Trí tuệ", "Tự kỷ", "Khác"], default=["Nhìn"], key="khbd_nhu_cau_hoa_nhap")

    st.subheader("📌 Hoạt động giáo viên mong muốn thêm")
    c_hd1, c_hd2 = st.columns([5, 1])
    with c_hd1: st.text_input("Hoạt động", placeholder="VD: Thí nghiệm...", key="khbd_new_activity", label_visibility="collapsed", on_change=add_activity)
    with c_hd2: st.button("➕ Thêm", on_click=add_activity, use_container_width=True)
    
    for index, activity in enumerate(st.session_state.khbd_hoat_dong_list):
        c_i1, c_i2 = st.columns([10, 1])
        with c_i1: st.info(activity)
        with c_i2:
            if st.button("Xóa", key=f"khbd_del_activity_{index}"):
                st.session_state.khbd_hoat_dong_list.pop(index)
                st.rerun()

    # --------------------------------------------------------
    # ĐỒNG BỘ NĂNG LỰC SỐ PHẢN HỒI NHANH VÀ XỬ LÝ AI
    # --------------------------------------------------------
    if tich_hop_nls:
        with st.container(border=True):
            st.markdown("#### 🎯 Cấu hình Năng lực số")
            loai_khung = st.radio("Chuẩn:", ["Giáo viên (Thông tư 18)", "Học sinh (DigComp)"], horizontal=True, key="khbd_loai_khung_nls")
            current_khung = KHUNG_NLS_GV if loai_khung == "Giáo viên (Thông tư 18)" else KHUNG_NLS_HS
            
            col_lv, col_tp, col_md = st.columns([2, 2, 1])
            with col_lv: linh_vuc = st.selectbox("Lĩnh vực", list(current_khung.keys()), key="khbd_nls_linh_vuc")
            with col_tp: thanh_phan = st.selectbox("Thành phần", list(current_khung[linh_vuc].keys()), key="khbd_nls_thanh_phan")
            with col_md: muc_do = st.selectbox("Mức độ", list(current_khung[linh_vuc][thanh_phan].keys()), key="khbd_nls_muc_do")
            
            tu_dong_noi_dung = current_khung[linh_vuc][thanh_phan][muc_do]
            st.session_state.khbd_nls_noi_dung = tu_dong_noi_dung
            st.text_area("Yêu cầu cần đạt", value=tu_dong_noi_dung, height=100, disabled=True)
            st.button("➕ Thêm vào danh sách", on_click=add_nls, use_container_width=True)
            
            for index, item in enumerate(st.session_state.khbd_nls_list):
                with st.container(border=True):
                    st.markdown(f"**{index + 1}. {item['linh_vuc']}** ({item['muc_do']})\n\n{item['noi_dung']}")
                    if st.button("Xóa", key=f"khbd_del_nls_{index}"):
                        st.session_state.khbd_nls_list.pop(index)
                        st.rerun()

    tieng_anh = st.checkbox("Giáo án bằng Tiếng Anh", key="khbd_tieng_anh")

    st.divider()
    if st.button("⚡ KÍCH HOẠT XỬ LÝ AI", type="primary", use_container_width=True):
        if ai_engine is None:
            st.error("❌ Chưa cấu hình AI Core Engine.")
            st.stop()
        if mode == "chinh_sua" and not file_ga:
            st.error("⚠️ Vui lòng tải giáo án gốc.")
            st.stop()
        if mode == "tu_dong" and not file_sgk:
            st.error("⚠️ Vui lòng cung cấp tệp SGK.")
            st.stop()
            
        with st.spinner("🧠 AI đang phân tích dữ liệu nguồn và biên soạn KHBD chuẩn 5512..."):
            try:
                noi_dung_chinh = read_multiple_files(file_ga) if mode == "chinh_sua" else read_multiple_files(file_sgk, range_trang)
                noi_dung_ppct = read_uploaded_file(file_ppct)
                noi_dung_ai = read_uploaded_file(file_ai)
                noi_dung_mau = read_uploaded_file(file_template) if file_template else read_template_local()
                    
                thong_tin = f"- Khối: {khoi_lop}\n- Môn: {mon_hoc}\n- Tên bài: {ten_bai or 'Theo nguồn'}\n- Số tiết: {so_tiet}\n- Ngôn ngữ: {'English' if tieng_anh else 'Tiếng Việt'}"
                hoat_dong = "\n".join(st.session_state.khbd_hoat_dong_list) or "Không có."
                
                prompt = build_prompt(
                    thong_tin=thong_tin, noi_dung_chinh=noi_dung_chinh, noi_dung_ppct=noi_dung_ppct,
                    noi_dung_ai=noi_dung_ai, noi_dung_mau=noi_dung_mau, nls=format_nls(),
                    tich_hop_ai=tich_hop_ai, tich_hop_hoa_nhap=tich_hop_hoa_nhap,
                    nhu_cau_hoa_nhap=", ".join(nhu_cau_hoa_nhap), hoat_dong=hoat_dong, mode=mode
                )
                st.session_state.khbd_result = generate_ai(ai_engine, prompt)
                st.success("🎉 Đã tạo giáo án thành công!")
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")

    result = st.session_state.get("khbd_result")
    if result:
        st.subheader("📝 Kết quả Kế hoạch bài dạy")
        st.markdown(result)
        st.divider()
        st.subheader("📄 Xuất Word Chuẩn Định Dạng")
        
        if WordExportEngine is None:
            st.error("❌ Lỗi: Không kết nối được module `export.word_export_engine`.")
        else:
            try:
                template_path = "templates/KHBD_Mau.docx"
                uploaded_template = st.session_state.get("khbd_file_template")
                if uploaded_template:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                        tmp.write(uploaded_template.getvalue())
                        template_path = tmp.name
                
                try:
                    word_bytes = WordExportEngine.convert_markdown_to_docx_bytes(result, template_path=template_path)
                except TypeError:
                    word_bytes = WordExportEngine.convert_markdown_to_docx_bytes(result)
                        
                st.download_button("📥 TẢI KHBD WORD (Chuẩn 5512)", data=word_bytes, file_name="Giao_An_5512.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                if uploaded_template and template_path != "templates/KHBD_Mau.docx" and os.path.exists(template_path):
                    os.remove(template_path)
            except Exception as e:
                st.error(f"❌ Lỗi xuất Word: {str(e)}")
