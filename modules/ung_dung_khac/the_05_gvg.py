# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ung_dung_khac/the_05_gvg.py
Nhiệm vụ: Công cụ Xây dựng Biện pháp thi GVG & GVCN Giỏi.
Chức năng: Lập dàn ý, viết đề cương báo cáo biện pháp nâng cao 
chất lượng giảng dạy/chủ nhiệm cho các cấp thi.
============================================================
"""

import streamlit as st

def init_state():
    if "gvg_result" not in st.session_state:
        st.session_state["gvg_result"] = None
    if "gvg_goi_y" not in st.session_state:
        st.session_state["gvg_goi_y"] = None

def render_the_05(ai_engine=None):
    init_state()
    st.markdown("### 🏆 Công cụ Xây dựng Biện pháp thi GVG & GVCN Giỏi")
    st.caption("Hỗ trợ giáo viên xây dựng đề cương, dàn ý chi tiết báo cáo biện pháp nâng cao chất lượng giáo dục và công tác chủ nhiệm lớp.")

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown("#### 📝 Thông tin & Cấu hình Biện pháp")
        
        # Hàng 1: Cấp học, Môn, Cấp thi
        c1, c2, c3 = st.columns(3)
        with c1:
            cap_hoc = st.selectbox("Cấp học", ["Trung học cơ sở", "Tiểu học", "Trung học phổ thông", "Mầm non"], key="gvg_caphoc")
        with c2:
            mon_linh_vuc = st.selectbox(
                "Môn / Lĩnh vực", 
                [
                    "Công tác Chủ nhiệm lớp", "Toán", "Ngữ văn", "Khoa học tự nhiên (Lý, Hóa, Sinh)", 
                    "Lịch sử và Địa lý", "Giáo dục công dân", "Tiếng Anh", "Tin học", 
                    "Công nghệ", "Nghệ thuật", "Giáo dục thể chất", "HĐ trải nghiệm, hướng nghiệp"
                ], 
                key="gvg_mon"
            )
        with c3:
            cap_thi = st.selectbox("Cấp thi", ["Cấp Trường", "Cấp Xã/Phường", "Cấp Huyện/Quận", "Cấp Tỉnh"], key="gvg_capthi")

        # Hàng 2: Tên biện pháp và Nút Gợi ý
        st.markdown("**Tên biện pháp / Đề tài** <span style='color:red;'>*</span>", unsafe_allow_html=True)
        c_name, c_btn = st.columns([4, 1])
        with c_name:
            ten_bien_phap = st.text_input(
                "Nhập tên biện pháp", 
                placeholder="Ví dụ: Một số biện pháp giúp học sinh tự học môn Toán...", 
                label_visibility="collapsed",
                key="gvg_ten"
            )
        with c_btn:
            btn_goi_y = st.button("💡 Gợi ý", use_container_width=True)

        if btn_goi_y:
            if not ai_engine:
                st.error("❌ Chưa kết nối AI.")
            else:
                with st.spinner("Đang tìm ý tưởng..."):
                    prompt_goiy = f"Bạn là chuyên gia giáo dục. Hãy gợi ý 5 tên đề tài/biện pháp dự thi Giáo viên giỏi/Chủ nhiệm giỏi cấp {cap_thi} cho môn/lĩnh vực: {mon_linh_vuc} ({cap_hoc}). Yêu cầu: Tên đề tài mang tính thực tiễn, đổi mới sáng tạo theo chương trình GDPT 2018. Chỉ in ra danh sách 5 tên, không giải thích dài dòng."
                    try:
                        res_goiy = ai_engine.generate_text(prompt_goiy)
                        st.session_state["gvg_goi_y"] = res_goiy
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
        
        if st.session_state["gvg_goi_y"]:
            st.info(f"**Gợi ý cho thầy/cô:**\n{st.session_state['gvg_goi_y']}")

        # Hàng 3: Thực trạng
        thuc_trang = st.text_area(
            "Thực trạng & Vấn đề (Không bắt buộc)", 
            placeholder="Mô tả khó khăn, vướng mắc hiện tại của học sinh/lớp học. (Nếu để trống, AI sẽ tự động đề xuất thực trạng phổ biến)",
            height=100,
            key="gvg_thuctrang"
        )

        # Hàng 4: Đối tượng & Dự kiến
        c_dt, c_dk = st.columns(2)
        with c_dt:
            doi_tuong = st.text_input("Đối tượng áp dụng", placeholder="VD: Học sinh lớp 8A trường...", key="gvg_doituong")
        with c_dk:
            du_kien_bp = st.text_area("Dự kiến các biện pháp chính (Nếu có)", placeholder="Mỗi dòng một ý chính...", height=80, key="gvg_dukien")

        btn_lap_dan_y = st.button("🚀 LẬP DÀN Ý TỰ ĐỘNG", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### 📋 Kết quả Xây dựng Biện pháp")
        
        if btn_lap_dan_y:
            if not ten_bien_phap.strip():
                st.warning("⚠️ Vui lòng nhập Tên biện pháp/Đề tài trước khi lập dàn ý (Thầy/cô có thể dùng nút Gợi ý).")
                st.stop()
            
            if not ai_engine:
                st.error("❌ Hệ thống chưa kết nối AI Engine. Vui lòng nhập API Key ở thanh bên.")
                st.stop()

            prompt_build = f"""
            BẠN LÀ CHUYÊN GIA GIÁO DỤC, THÀNH VIÊN BAN GIÁM KHẢO HỘI THI GIÁO VIÊN DẠY GIỎI / GIÁO VIÊN CHỦ NHIỆM GIỎI.
            
            Yêu cầu: Hãy viết một Đề cương / Dàn ý Báo cáo biện pháp thật chi tiết, khoa học và mang tính thực tiễn cao dựa trên các thông tin sau:
            - Cấp học: {cap_hoc}
            - Môn / Lĩnh vực: {mon_linh_vuc}
            - Cấp dự thi: {cap_thi}
            - Tên biện pháp: {ten_bien_phap}
            - Đối tượng áp dụng: {doi_tuong if doi_tuong else 'Học sinh phù hợp với cấp học'}
            - Thực trạng (do giáo viên cung cấp): {thuc_trang if thuc_trang else 'Tự động phân tích các khó khăn phổ biến phù hợp với tên đề tài.'}
            - Các biện pháp cốt lõi dự kiến: {du_kien_bp if du_kien_bp else 'Tự động đề xuất 3-4 biện pháp sáng tạo, bám sát Chương trình GDPT 2018.'}

            Cấu trúc dàn ý chuẩn quy định báo cáo GVG/GVCNG:
            I. ĐẶT VẤN ĐỀ (Lý do chọn biện pháp, tính cấp thiết).
            II. THỰC TRẠNG (Thuận lợi, khó khăn, nguyên nhân).
            III. CÁC BIỆN PHÁP THỰC HIỆN (Trình bày chi tiết từng biện pháp, cách thức triển khai cụ thể).
            IV. KẾT QUẢ ĐẠT ĐƯỢC (Định tính và định lượng minh chứng).
            V. KẾT LUẬN VÀ KIẾN NGHỊ.
            
            Viết bằng ngôn ngữ sư phạm chuẩn mực, định dạng Markdown rõ ràng, làm nổi bật các từ khóa quan trọng.
            """

            with st.spinner("🤖 Trợ lý AI đang soạn thảo dàn ý chi tiết..."):
                try:
                    result_text = ai_engine.generate_text(prompt_build)
                    st.session_state["gvg_result"] = result_text
                    st.success("🎉 Đã hoàn thành Dàn ý báo cáo biện pháp!")
                except Exception as e:
                    st.error(f"❌ Lỗi xử lý AI: {str(e)}")

        if st.session_state["gvg_result"]:
            st.markdown(
                f"<div style='border: 1px solid #ddd; padding: 15px; border-radius: 8px; background-color: #f9f9f9; height: 500px; overflow-y: auto;'>"
                f"{st.session_state['gvg_result']}</div>", 
                unsafe_allow_html=True
            )
            
            st.write("") # Tạo khoảng trống
            
            c_download, c_delete = st.columns(2)
            with c_download:
                st.download_button(
                    label="📥 Tải xuống Dàn ý (.txt)",
                    data=st.session_state["gvg_result"],
                    file_name=f"BienPhap_{cap_thi.replace(' ', '')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with c_delete:
                if st.button("🗑️ Xóa kết quả", use_container_width=True):
                    st.session_state["gvg_result"] = None
                    st.rerun()
        else:
            st.info("💡 Kết quả dàn ý và đề cương chi tiết sẽ hiển thị tại đây sau khi thầy/cô bấm nút Lập Dàn ý.")
