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
            
        with st.spinner("🧠 Hệ thống đang phân tích đa tầng (OCR), kiểm định chất lượng nguồn và biên soạn KHBD chi tiết theo số tiết..."):
            try:
                # Đọc tệp thông qua hệ thống kiểm định đa tầng mới
                noi_dung_chinh = read_multiple_files(file_sgk, range_trang, is_pdf_target=True) if mode != "chinh_sua" else ""
                noi_dung_ga = read_multiple_files(file_ga) if mode == "chinh_sua" else ""
                noi_dung_ppct = read_uploaded_file(file_ppct)
                noi_dung_ai = read_uploaded_file(file_ai)
                noi_dung_mau = read_uploaded_file(file_template) if file_template else read_template_local()
                    
                thong_tin = f"- Khối: {khoi_lop}\n- Môn: {mon_hoc}\n- Tên bài: {ten_bai or 'Theo nguồn'}\n- Số tiết: {so_tiet}\n- Ngôn ngữ: {'English' if tieng_anh else 'Tiếng Việt'}"
                hoat_dong = "\n".join(st.session_state.khbd_hoat_dong_list) or "Không có."
                
                # Gọi build_prompt (Hệ thống sẽ tự động validate chất lượng nguồn bên trong)
                prompt = build_prompt(
                    thong_tin=thong_tin, 
                    noi_dung_chinh=noi_dung_chinh, 
                    noi_dung_ga=noi_dung_ga, 
                    noi_dung_ppct=noi_dung_ppct,
                    noi_dung_ai=noi_dung_ai, 
                    noi_dung_mau=noi_dung_mau, 
                    nls=format_nls(),
                    tich_hop_ai=tich_hop_ai, 
                    tich_hop_hoa_nhap=tich_hop_hoa_nhap,
                    nhu_cau_hoa_nhap=", ".join(nhu_cau_hoa_nhap), 
                    hoat_dong=hoat_dong, 
                    mode=mode
                )
                
                raw_result = generate_ai(ai_engine, prompt)
                
                # Kiểm tra hợp lệ kết quả qua hàm validate mới
                is_valid, msg = validate_khbd_result(raw_result)
                if not is_valid:
                    st.warning(f"⚠️ Cảnh báo cấu trúc: {msg}")
                    
                st.session_state.khbd_result = raw_result
                st.success("🎉 Đã tạo giáo án chi tiết thành công!")
            except ValueError as ve:
                st.error(f"❌ Lỗi kiểm định dữ liệu nguồn: {str(ve)}")
            except Exception as e:
                st.error(f"❌ Lỗi hệ thống: {str(e)}")
