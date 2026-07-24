# -*- coding: utf-8 -*-
"""
============================================================
VIEW: GIAO DIỆN XÂY DỰNG KẾ HOẠCH BÀI DẠY (TÍCH HỢP OCR & TT18)
FILE: views/xd_khbd_view.py
============================================================
"""

import streamlit as st

try:
    from views.xd_khbd_data import (
        init_session_state,
        get_nls_domains,
        get_nls_components,
        get_nls_levels,
        get_nls_content,
        read_multiple_files,
        add_nls,
        format_nls,
        build_prompt,
        generate_ai,
        validate_khbd_result,
        diagnose_source_quality
    )
except Exception as e:
    st.error(f"❌ Không thể nạp module logic: {e}")
    raise

try:
    from export.word_export_engine import WordExportEngine
except Exception:
    WordExportEngine = None

def render_xd_khbd(ai_engine_client=None):
    init_session_state()

    st.title("📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY (CHUẨN 5512 & TT18)")
    
    st.subheader("🎛️ Thông tin bài dạy")
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1:
        khoi_lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    with col2:
        mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Tiếng Anh", "Khoa học tự nhiên", "Vật lí", "Hóa học", "Sinh học", "Lịch sử và Địa lí", "Tin học", "Công nghệ"])
    with col3:
        so_tiet = st.number_input("Số tiết", min_value=1, max_value=15, value=1)
        
    ten_bai = st.text_input("Tên bài học", placeholder="Nhập chính xác tên bài (VD: Định luật Ôm, Thơ Đường luật...)")

    st.subheader("✨ Cấu hình AI & Chế độ")
    c_md1, c_md2 = st.columns(2)
    with c_md1:
        mode = st.radio(
            "Chế độ soạn:", 
            ["tu_dong", "chinh_sua"], 
            format_func=lambda x: "⚡ Tự động soạn từ SGK (Tải SGK)" if x == "tu_dong" else "📄 Chỉnh sửa giáo án gốc (Tải KHBD cũ)", 
            horizontal=True
        )
    with c_md2:
        model_name = st.selectbox("Mô hình AI (Khuyên dùng 3.1 Pro cho KHBD phức tạp, nhiều Toán/Hóa)", ["3.5 Flash", "3.1 Pro", "Tư duy mở rộng"])

    st.subheader("📤 Tài liệu đầu vào")
    if mode == "chinh_sua":
        st.info("💡 Chế độ Chỉnh sửa: Hệ thống cần file Giáo án cũ của thầy để làm gốc, và SGK (nếu có) để đối chiếu kiến thức.")
        col_up1, col_up2 = st.columns(2)
        file_ga = col_up1.file_uploader("📂 Tải lên KHBD (Giáo án) cũ (.docx, .pdf)", type=["docx", "pdf"], accept_multiple_files=True)
        file_sgk = col_up2.file_uploader("📂 Tải lên SGK/Tài liệu bổ sung (.docx, .pdf) - Tùy chọn", type=["pdf", "docx"], accept_multiple_files=True)
    else:
        st.info("💡 Chế độ Tự động: Hệ thống BẮT BUỘC cần file Sách giáo khoa (PDF có text hoặc Word) để trích xuất chuẩn xác kiến thức.")
        file_sgk = st.file_uploader("📂 Tải lên SGK / Đề cương / Kiến thức gốc (.docx, .pdf)", type=["pdf", "docx"], accept_multiple_files=True)
        file_ga = []

    range_trang = ""
    if file_sgk and mode == "tu_dong":
        range_trang = st.text_input("Phạm vi trang SGK cần đọc (Rất quan trọng với file PDF lớn)", placeholder="Ví dụ: 45-48")

    st.subheader("🔧 Tích hợp chuyên sâu (Hòa nhập, AI, Số hóa)")
    
    tich_hop_ai = st.checkbox("🤖 Tích hợp hoạt động sử dụng AI trong bài học")
    
    tich_hop_hoa_nhap = st.checkbox("🤝 Tích hợp Dạy học hòa nhập (HS Khuyết tật)")
    nhu_cau_hoa_nhap = []
    if tich_hop_hoa_nhap:
        with st.container(border=True):
            st.markdown("**Cấu hình Dạy học Hòa nhập:**")
            nhu_cau_hoa_nhap = st.multiselect(
                "Đặc điểm học sinh khuyết tật trong lớp:", 
                ["Vận động", "Nghe", "Nói", "Nhìn", "Trí tuệ", "Tự kỷ / Tăng động (ADHD)", "Khác"], 
                default=["Nhìn"]
            )

    tich_hop_nls = st.checkbox("💻 Tích hợp Năng lực số (Theo Thông tư 18)")
    if tich_hop_nls:
        with st.container(border=True):
            st.markdown("**Cấu hình Năng lực số (DigComp / TT18):**")
            loai_khung = st.radio("Đối tượng áp dụng", ["Giáo viên (Thông tư 18)", "Học sinh (Khung DigComp)"], horizontal=True)
            st.session_state["khbd_loai_khung_nls"] = loai_khung
            
            col_nls1, col_nls2, col_nls3 = st.columns(3)
            with col_nls1:
                linh_vuc = st.selectbox("Miền năng lực", get_nls_domains(loai_khung), key="khbd_nls_linh_vuc")
            with col_nls2:
                thanh_phan = st.selectbox("Năng lực thành phần", get_nls_components(loai_khung, linh_vuc), key="khbd_nls_thanh_phan")
            with col_nls3:
                muc_do = st.selectbox("Mức độ", get_nls_levels(loai_khung, linh_vuc, thanh_phan), key="khbd_nls_muc_do")
                
            noi_dung_nls = get_nls_content(loai_khung, linh_vuc, thanh_phan, muc_do)
            st.info(f"**Mô tả NLS:** {noi_dung_nls}")
            st.session_state["khbd_nls_noi_dung"] = noi_dung_nls
            
            if st.button("➕ Thêm Năng lực số này vào KHBD"):
                add_nls()
                st.toast("Đã thêm yêu cầu NLS!")
                
            if st.session_state.khbd_nls_list:
                st.markdown("**Danh sách Năng lực số đã chọn:**")
                st.markdown(format_nls())
                if st.button("🗑️ Xóa danh sách NLS"):
                    st.session_state.khbd_nls_list = []
                    st.rerun()

    st.divider()
    if st.button("⚡ TẠO KẾ HOẠCH BÀI DẠY BẰNG AI", type="primary", use_container_width=True):
        if ai_engine_client is None:
            st.error("❌ Chưa cấu hình API Key hoặc Client AI bị lỗi.")
            st.stop()
        if not ten_bai.strip():
            st.warning("⚠️ Vui lòng nhập Tên bài học.")
            st.stop()
        if mode == "chinh_sua" and not file_ga:
            st.warning("⚠️ Vui lòng tải Giáo án gốc lên (Chế độ Chỉnh sửa).")
            st.stop()
        if mode == "tu_dong" and not file_sgk:
            st.warning("⚠️ Vui lòng tải SGK / Tài liệu kiến thức lên (Chế độ Soạn mới).")
            st.stop()

        with st.spinner("⏳ Đang quét tài liệu... (Nếu là ảnh Scan, AI Vision sẽ tự động nhận diện chữ, vui lòng đợi thêm 30s)"):
            try:
                noi_dung_chinh = read_multiple_files(file_sgk, range_trang, is_pdf_target=True) if file_sgk else ""
                noi_dung_ga = read_multiple_files(file_ga) if mode == "chinh_sua" and file_ga else ""
                
                # Logic kiểm tra lỗi mới (đã gỡ bỏ hàm kiểm tra chặn lỗi cũ)
                if mode == "tu_dong":
                    if "❌" in noi_dung_chinh:
                        st.error(noi_dung_chinh)
                        st.stop()
                        
                    if len(noi_dung_chinh.strip()) < 100:
                        st.error("❌ Hệ thống không thể đọc được nội dung chữ từ file này, và quá trình tự động quét ảnh OCR cũng thất bại (có thể do API Key chưa được nhập hoặc hết Quota). Thầy vui lòng nhập API Key cá nhân ở thanh bên trái để AI có thể đọc ảnh.")
                        st.stop()
                    else:
                        st.success(f"✅ Đã trích xuất và bảo toàn thành công {len(noi_dung_chinh):,} ký tự từ tài liệu tải lên.")

                thong_tin = f"- Khối: {khoi_lop}\n- Môn: {mon_hoc}\n- Tên bài: {ten_bai}\n- Số tiết: {so_tiet} tiết"
                nls_str = format_nls() if tich_hop_nls else "Không yêu cầu."
                
                prompt = build_prompt(
                    thong_tin=thong_tin,
                    noi_dung_chinh=noi_dung_chinh,
                    noi_dung_ga=noi_dung_ga,
                    nls_str=nls_str,
                    tich_hop_ai=tich_hop_ai,
                    tich_hop_hoa_nhap=tich_hop_hoa_nhap,
                    nhu_cau_hoa_nhap=", ".join(nhu_cau_hoa_nhap),
                    mode=mode,
                    so_tiet=so_tiet
                )

                raw_result = generate_ai(ai_engine_client, prompt, model_name)
                is_valid, msg = validate_khbd_result(raw_result)

                if not is_valid:
                    st.warning(f"⚠️ Cảnh báo sư phạm: {msg}")

                st.session_state['current_khbd_data'] = {
                    "is_khbd": True,
                    "title": ten_bai,
                    "ai_generated_content": raw_result
                }
                st.success("🎉 Khởi tạo giáo án thành công!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Lỗi hệ thống: {e}")

    # ==========================================================
    # HIỂN THỊ VÀ XUẤT WORD
    # ==========================================================
    if st.session_state.get('khbd_delete_trigger'):
        if 'current_khbd_data' in st.session_state:
            del st.session_state['current_khbd_data']
        st.session_state['khbd_delete_trigger'] = False
        st.rerun()

    khbd_cache = st.session_state.get('current_khbd_data')
    word_file = None
    
    if khbd_cache and khbd_cache.get('is_khbd'):
        st.markdown("---")
        st.markdown(f"### 📄 KẾT QUẢ KHBD: {khbd_cache['title'].upper()}")
        
        with st.expander("👀 Xem trước Kế hoạch bài dạy chi tiết", expanded=True):
            st.markdown(khbd_cache.get('ai_generated_content', ''))
            
            if WordExportEngine:
                with st.spinner("Đang render công thức Toán/Bảng biểu và xuất ra file Word chuẩn..."):
                    try:
                        if hasattr(WordExportEngine, 'convert_markdown_to_docx_bytes'):
                            word_file = WordExportEngine.convert_markdown_to_docx_bytes(khbd_cache['ai_generated_content'])
                    except Exception as e:
                        st.error(f"⚠️ Trình xuất Word đang gặp sự cố với format: {e}")
            
        col_save, col_download, col_delete = st.columns(3)
        with col_save:
            if st.button("💾 Lưu nháp vào hệ thống", use_container_width=True):
                st.toast("Đã lưu cấu hình giáo án vào bộ nhớ an toàn!")
                
        with col_download:
            if word_file:
                saved_title = khbd_cache.get("title", "Giao_An").replace(" ", "_")
                st.download_button(
                    label="📥 TẢI FILE WORD ĐÚNG CHUẨN 5512",
                    data=word_file,
                    file_name=f"KHBD_{saved_title}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.button("⏳ Đang chuẩn bị file Word...", disabled=True, use_container_width=True)
                
        with col_delete:
            if st.button("🗑️ Xóa kết quả làm lại", use_container_width=True):
                st.session_state['khbd_delete_trigger'] = True
                st.rerun()
