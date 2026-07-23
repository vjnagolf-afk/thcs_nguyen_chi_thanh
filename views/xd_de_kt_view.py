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

try:
    from views.xd_khbd_data import (
        init_session_state,
        get_nls_domains,
        get_nls_components,
        get_nls_levels,
        get_nls_content,
        read_multiple_files,
        read_uploaded_file,
        read_template_local,
        add_nls,
        format_nls,
        add_activity,
        build_prompt,
        generate_ai,
        validate_khbd_result
    )
except Exception as e:
    st.error(f"❌ Không thể nạp module logic: {e}")
    raise

try:
    from export.word_export_engine import WordExportEngine
except Exception:
    WordExportEngine = None

def _show_source_quality(text, title="Tài liệu kiến thức"):
    chars = len(text)
    words = len(text.split())
    lines = len([x for x in text.splitlines() if x.strip()])

    st.markdown(f"#### 📊 Kiểm tra dữ liệu: {title}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Số ký tự", f"{chars:,}")
    c2.metric("Số từ", f"{words:,}")
    c3.metric("Số dòng", f"{lines:,}")

    if chars < 300:
        st.warning("⚠️ Nội dung trích xuất quá ít hoặc là file Scan rỗng. Nếu AI sinh lỗi, hãy copy chữ dán ra file Word (.docx) rồi tải lại!")
    else:
        st.success("✅ Dữ liệu đã được đọc thành công.")

def render_xd_khbd(ai_engine_client=None):
    """
    Nhận tham số ai_engine_client từ app.py (thường là client lấy từ get_ai_client)
    """
    init_session_state()

    st.title("📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY (CHUẨN 5512 & TT18)")
    
    st.subheader("🎛️ Thông tin bài dạy")
    col1, col2 = st.columns(2)
    with col1:
        khoi_lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    with col2:
        mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Tiếng Anh", "Khoa học tự nhiên", "Vật lí", "Hóa học", "Sinh học", "Lịch sử và Địa lí", "Tin học", "Công nghệ", "Khác"])
        
    st.subheader("✨ Cấu hình AI & Chế độ")
    c_md1, c_md2 = st.columns(2)
    with c_md1:
        mode = st.radio("Chế độ soạn", ["tu_dong", "chinh_sua"], format_func=lambda x: "⚡ Tự động soạn từ SGK" if x == "tu_dong" else "📄 Chỉnh sửa giáo án gốc", horizontal=True)
    with c_md2:
        model_name = st.selectbox("Mô hình AI xử lý", ["3.5 Flash", "3.1 Flash-Lite", "3.1 Pro", "Tư duy mở rộng"])

    range_trang = ""
    if mode == "tu_dong":
        st.info("💡 Nên giới hạn trang để trích xuất chuẩn. Ví dụ: 45-48")
        range_trang = st.text_input("Phạm vi trang SGK", placeholder="Ví dụ: 45-48")

    st.subheader("📤 Tài liệu đầu vào")
    col_up1, col_up2, col_up3, col_up4 = st.columns(4)
    if mode == "chinh_sua":
        file_ga = col_up1.file_uploader("Giáo án gốc", type=["docx", "pdf"], accept_multiple_files=True)
        file_sgk = []
    else:
        file_ga = []
        file_sgk = col_up1.file_uploader("SGK / Tài liệu (.docx, .pdf)", type=["pdf", "docx"], accept_multiple_files=True)
        
    file_ppct = col_up2.file_uploader("PPCT (Tùy chọn)", type=["pdf", "docx", "xlsx", "xls"])
    file_ai = col_up3.file_uploader("Bảng AI (Tùy chọn)", type=["pdf", "docx", "xlsx", "xls"])
    file_template = col_up4.file_uploader("Mẫu KHBD trường", type=["docx"])

    st.subheader("📚 Chi tiết bài học")
    col_td1, col_td2 = st.columns(2)
    with col_td1: ten_bai = st.text_input("Tên bài dạy")
    with col_td2: so_tiet = st.number_input("Thời lượng tiết học", min_value=1, max_value=10, value=1)

    st.subheader("🔧 Tích hợp chuyên sâu")
    c_th1, c_th2, c_th3 = st.columns(3)
    with c_th1: tich_hop_nls = st.checkbox("Năng lực số (TT18)")
    with c_th2: tich_hop_ai = st.checkbox("Năng lực AI")
    with c_th3: tich_hop_hoa_nhap = st.checkbox("Dạy học hòa nhập")

    nhu_cau_hoa_nhap = []
    if tich_hop_hoa_nhap:
        nhu_cau_hoa_nhap = st.multiselect("Chọn loại khuyết tật/nhu cầu", ["Vận động", "Nghe", "Nói", "Nhìn", "Trí tuệ", "Khác"], default=["Nhìn"])

    # Xử lý nút KÍCH HOẠT
    st.divider()
    if st.button("⚡ KÍCH HOẠT TIẾN TRÌNH AI", type="primary", use_container_width=True):
        if ai_engine_client is None:
            st.error("❌ Chưa cấu hình API Key hoặc Client AI bị lỗi.")
            st.stop()
        if mode == "chinh_sua" and not file_ga:
            st.warning("⚠️ Vui lòng tải giáo án gốc lên.")
            st.stop()
        if mode == "tu_dong" and not file_sgk:
            st.warning("⚠️ Vui lòng tải SGK / Tài liệu kiến thức lên.")
            st.stop()

        with st.spinner("⏳ Trợ lý AI đang bóc tách tài liệu và thiết kế tiến trình..."):
            try:
                # Trích xuất dữ liệu
                noi_dung_chinh = read_multiple_files(file_sgk, range_trang, is_pdf_target=True) if mode == "tu_dong" and file_sgk else ""
                
                if mode == "tu_dong":
                    _show_source_quality(noi_dung_chinh)
                    if len(noi_dung_chinh.strip()) < 50:
                        st.error("❌ Dữ liệu đọc được quá ít, dừng xử lý.")
                        st.stop()

                noi_dung_ga = read_multiple_files(file_ga) if mode == "chinh_sua" and file_ga else ""
                noi_dung_ppct = read_uploaded_file(file_ppct) if file_ppct else ""
                noi_dung_ai = read_uploaded_file(file_ai) if file_ai else ""
                noi_dung_mau = read_uploaded_file(file_template) if file_template else read_template_local()

                thong_tin = f"- Khối: {khoi_lop}\n- Môn: {mon_hoc}\n- Tên bài: {ten_bai}\n- Số tiết: {so_tiet} tiết"
                
                prompt = build_prompt(
                    thong_tin=thong_tin,
                    noi_dung_chinh=noi_dung_chinh,
                    noi_dung_ga=noi_dung_ga,
                    noi_dung_ppct=noi_dung_ppct,
                    noi_dung_ai=noi_dung_ai,
                    noi_dung_mau=noi_dung_mau,
                    nls="Có",
                    tich_hop_ai=tich_hop_ai,
                    tich_hop_hoa_nhap=tich_hop_hoa_nhap,
                    nhu_cau_hoa_nhap=", ".join(nhu_cau_hoa_nhap),
                    hoat_dong="",
                    mode=mode
                )

                # Gọi AI ổn định
                raw_result = generate_ai(ai_engine_client, prompt, model_name)
                is_valid, msg = validate_khbd_result(raw_result)

                if not is_valid:
                    st.warning(f"⚠️ Cảnh báo sư phạm: {msg}")

                # Lưu vào cache ổn định
                st.session_state['current_khbd_data'] = {
                    "is_khbd": True,
                    "title": ten_bai if ten_bai else "Giáo án AI",
                    "ai_generated_content": raw_result
                }
                st.success("🎉 Khởi tạo giáo án thành công!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Lỗi hệ thống: {e}")

    # =====================================================================
    # HIỂN THỊ VÀ KẾT XUẤT HỒ SƠ WORD TỰ ĐỘNG
    # =====================================================================
    if st.session_state.get('khbd_delete_trigger'):
        if 'current_khbd_data' in st.session_state:
            del st.session_state['current_khbd_data']
        st.session_state['khbd_delete_trigger'] = False
        st.rerun()

    khbd_cache = st.session_state.get('current_khbd_data')
    word_file = None
    
    if khbd_cache and khbd_cache.get('is_khbd'):
        st.markdown("---")
        st.markdown(f"### 📄 KẾT QUẢ: {khbd_cache['title']}")
        
        with st.expander("👀 Xem trước Kế hoạch bài dạy chi tiết", expanded=True):
            st.markdown(khbd_cache.get('ai_generated_content', ''))
            
            # Xuất Word
            if WordExportEngine:
                try:
                    template_path = "templates/KHBD_Mau.docx"
                    # Nếu đang xài hàm cũ `convert_markdown_to_docx_bytes`:
                    if hasattr(WordExportEngine, 'convert_markdown_to_docx_bytes'):
                        word_file = WordExportEngine.convert_markdown_to_docx_bytes(khbd_cache['ai_generated_content'], template_path=template_path)
                    # Hoặc nếu dùng hàm mới `export_to_word`:
                    elif hasattr(WordExportEngine, 'export_to_word'):
                        word_file = WordExportEngine.export_to_word(khbd_cache)
                except Exception as e:
                    st.error(f"⚠️ Trình xuất Word đang gặp sự cố: {e}")
            
        col_save, col_download, col_delete = st.columns(3)
        with col_save:
            if st.button("💾 Lưu file tạm thời", use_container_width=True):
                st.toast("Đã lưu cấu hình giáo án vào bộ nhớ an toàn!")
                
        with col_download:
            if word_file:
                saved_title = khbd_cache.get("title", "Giao_An").replace(" ", "_")
                st.download_button(
                    label="📥 Tải file Word về máy",
                    data=word_file,
                    file_name=f"KHBD_{saved_title}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            else:
                st.button("⏳ Trình xuất đang lỗi...", disabled=True, use_container_width=True)
                
        with col_delete:
            if st.button("🗑️ Xóa kết quả", use_container_width=True):
                st.session_state['khbd_delete_trigger'] = True
                st.rerun()
