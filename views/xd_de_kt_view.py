# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: views/xd_de_kt_view.py
Giao diện Xây dựng Đề kiểm tra, Ma trận, Bản đặc tả và Đáp án.
Tích hợp 2 chế độ: Chuẩn CV 7991 và Chế độ Tùy chọn (động form nhập liệu).
============================================================
"""

import streamlit as st
from views.xd_de_kt_data import (
    init_session_state_de_kt,
    reset_dkt_result,
    read_multiple_files_dkt,
    generate_dkt_ai
)

try:
    from export.export_word import export_word
except ImportError:
    export_word = None


def render_xd_de_kt(ai_engine=None):
    init_session_state_de_kt()

    st.markdown("## 📝 Xây dựng Đề kiểm tra (Ma trận - Đặc tả - Đề - Đáp án)")
    st.info("Hệ thống tự động bóc tách kiến thức từ tài liệu, thiết lập Ma trận, Bản đặc tả và sinh Đề kiểm tra chuẩn. Hỗ trợ xuất Word OMML sắc nét.")

    # TÙY CHỌN CHẾ ĐỘ TẠO ĐỀ
    mode_tao_de = st.radio(
        "Lựa chọn chế độ cấu hình đề:",
        ["Chuẩn Công văn 7991 (3 Mức độ, 4 Định dạng chuẩn)", "Tùy chọn tự do (4 Mức độ, Tùy chỉnh chi tiết số câu, điểm số)"],
        horizontal=True
    )

    config_data = {}

    with st.expander("⚙️ Thiết lập Cấu hình Đề kiểm tra", expanded=True):
        
        # CHẾ ĐỘ 1: CÔNG VĂN 7991 CŨ
        if "7991" in mode_tao_de:
            config_data["mode"] = "cv7991"
            col1, col2 = st.columns(2)
            with col1:
                config_data["mon_hoc"] = st.text_input("Môn học:", placeholder="VD: Khoa học tự nhiên")
                config_data["lop"] = st.text_input("Lớp:", placeholder="VD: Lớp 9")
            with col2:
                config_data["thoi_gian"] = st.number_input("Thời gian làm bài (phút):", min_value=15, max_value=180, value=45, step=5)
                config_data["ty_le"] = st.text_input("Tỉ lệ TN/TL:", value="70% Trắc nghiệm / 30% Tự luận")
            config_data["yeu_cau_dac_biet"] = st.text_area("Yêu cầu khác (Tuỳ chọn):", placeholder="VD: Tập trung vào chương...")

        # CHẾ ĐỘ 2: TÙY CHỌN TỰ DO
        else:
            config_data["mode"] = "tuy_chon"
            
            # Row 1: Môn, Lớp, Thời gian
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1: config_data["mon_hoc"] = st.text_input("MÔN HỌC", placeholder="Khoa học Tự nhiên")
            with c2: config_data["lop"] = st.text_input("LỚP", placeholder="Lớp 9")
            with c3: config_data["thoi_gian"] = st.number_input("THỜI GIAN", min_value=15, max_value=180, value=45, step=5)
            
            # Row 2: Tỷ lệ nhận thức
            st.markdown("**Tỷ lệ mức độ nhận thức (%):**")
            cnb, cth, cvd, cvdc = st.columns(4)
            pct_nb = cnb.number_input("Nhận biết", 0, 100, 40, step=5)
            pct_th = cth.number_input("Thông hiểu", 0, 100, 30, step=5)
            pct_vd = cvd.number_input("Vận dụng", 0, 100, 20, step=5)
            pct_vdc = cvdc.number_input("Vận dụng cao", 0, 100, 10, step=5)
            config_data["muc_do"] = {"nb": pct_nb, "th": pct_th, "vd": pct_vd, "vdc": pct_vdc}
            
            if (pct_nb + pct_th + pct_vd + pct_vdc) != 100:
                st.warning(f"⚠️ Tổng tỷ lệ mức độ nhận thức đang là {pct_nb + pct_th + pct_vd + pct_vdc}%. Vui lòng điều chỉnh lại cho đúng 100%.")

            config_data["ten_bai"] = st.text_input("Tên bài kiểm tra / Đề số:", placeholder="Ví dụ: Kiểm tra đánh giá giữa kì I")

            st.markdown("---")
            # Row 3: TRẮC NGHIỆM VÀ TỰ LUẬN
            col_tn, col_tl = st.columns(2)
            
            # ---- CỘT TRẮC NGHIỆM ----
            with col_tn:
                st.markdown("### TRẮC NGHIỆM")
                
                # Biến lưu trữ tổng điểm TN (Sẽ được cộng dồn)
                tong_tn = 0.0
                
                c_cau, c_diem = st.columns([1.5, 1])
                nlc_cau = c_cau.number_input("Số câu nhiều lựa chọn:", 0, 50, 12)
                nlc_diem = c_diem.number_input("Điểm/câu (NLC):", 0.0, 10.0, 0.25, step=0.25)
                tong_tn += (nlc_cau * nlc_diem)
                
                c_cau, c_diem = st.columns([1.5, 1])
                ds_cau = c_cau.number_input("Số câu đúng/sai:", 0, 20, 1)
                ds_diem = c_diem.number_input("Điểm/câu (Đ/S):", 0.0, 10.0, 0.25, step=0.25)
                tong_tn += (ds_cau * ds_diem)
                
                c_cau, c_diem = st.columns([1.5, 1])
                dk_cau = c_cau.number_input("Số câu điền khuyết:", 0, 20, 1)
                dk_diem = c_diem.number_input("Điểm/câu (ĐK):", 0.0, 10.0, 0.25, step=0.25)
                tong_tn += (dk_cau * dk_diem)
                
                c_cau, c_diem = st.columns([1.5, 1])
                tln_cau = c_cau.number_input("Số câu trả lời ngắn:", 0, 20, 2)
                tln_diem = c_diem.number_input("Điểm/câu (TLN):", 0.0, 10.0, 0.25, step=0.25)
                tong_tn += (tln_cau * tln_diem)
                
                st.info(f"👉 **TỔNG ĐIỂM TRẮC NGHIỆM: {tong_tn} Điểm**")
                
                config_data["trac_nghiem"] = {
                    "tong_diem": tong_tn,
                    "nlc_cau": nlc_cau, "nlc_diem": nlc_diem,
                    "ds_cau": ds_cau, "ds_diem": ds_diem,
                    "dk_cau": dk_cau, "dk_diem": dk_diem,
                    "tln_cau": tln_cau, "tln_diem": tln_diem
                }

            # ---- CỘT TỰ LUẬN ----
            with col_tl:
                st.markdown("### TỰ LUẬN")
                so_cau_tl = st.number_input("Số câu Tự luận (Điền để sinh ô nhập điểm):", min_value=0, max_value=15, value=4)
                
                diem_tl_list = []
                tong_tl = 0.0
                
                # Động (Dynamic) sinh số lượng ô nhập điểm tương ứng với số câu tự luận
                for i in range(int(so_cau_tl)):
                    c_label, c_diem = st.columns([1.5, 1])
                    c_label.markdown(f"<p style='padding-top: 10px; font-weight: bold;'>Câu {i+1}.</p>", unsafe_allow_html=True)
                    # Chú ý: Cần có key duy nhất cho mỗi ô để Streamlit không báo lỗi trùng lặp
                    diem_cau = c_diem.number_input(f"Điểm Câu {i+1}", min_value=0.0, max_value=10.0, value=1.0, step=0.25, key=f"diem_tl_cau_{i}", label_visibility="collapsed")
                    diem_tl_list.append(diem_cau)
                    tong_tl += diem_cau
                    
                st.info(f"👉 **TỔNG ĐIỂM TỰ LUẬN: {tong_tl} Điểm**")
                
                config_data["tu_luan"] = {
                    "so_cau": so_cau_tl,
                    "tong_diem": tong_tl,
                    "chi_tiet_diem": diem_tl_list
                }
                
            # Cảnh báo nếu tổng 2 phần không bằng 10
            if (tong_tn + tong_tl) != 10:
                st.warning(f"⚠️ Tổng điểm toàn bài hiện tại đang là {tong_tn + tong_tl} (Khác 10.0). Thầy/Cô vui lòng kiểm tra lại điểm thành phần.")

            st.markdown("---")
            config_data["yeu_cau_dac_biet"] = st.text_area("Yêu cầu khác:", placeholder="Ví dụ: Đề cương...")

    # UPLOAD TÀI LIỆU NGUỒN
    st.markdown("### 📂 Nguồn dữ liệu (File SGK / Đề cương)")
    uploaded_files = st.file_uploader(
        "Tải lên file PDF hoặc Word để làm kiến thức lõi:", 
        type=["pdf", "docx"], 
        accept_multiple_files=True
    )
    
    # CHỌN MÔ HÌNH VÀ TẠO ĐỀ
    st.markdown("### 🧠 Chọn Mô hình AI")
    ai_model = st.selectbox(
        "Mô hình xử lý:", 
        options=["Gemini 2.5 Flash (Tốc độ cao)", "Gemini 2.5 Pro (Chuyên sâu)", "GPT-4o Mini", "GPT-4o (Cao cấp)"],
        index=0
    )

    if st.button("🚀 XÂY DỰNG ĐỀ KIỂM TRA", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("⚠️ Thầy/Cô vui lòng tải lên ít nhất một tài liệu nguồn (PDF/DOCX).")
            return
        if not config_data.get("mon_hoc"):
            st.warning("⚠️ Thầy/Cô vui lòng nhập Môn học.")
            return
            
        st.session_state["dkt_processing"] = True
        try:
            with st.spinner("⏳ Bước 1: Đang bóc tách Văn bản, Hình ảnh và Bảng biểu từ tài liệu..."):
                source_text = read_multiple_files_dkt(uploaded_files)
                
            with st.spinner("🧠 Bước 2: AI đang tính toán Ma trận, lập Đặc tả và biên soạn Đề (Có thể mất 30-60 giây)..."):
                result_markdown = generate_dkt_ai(ai_model, config_data, source_text)
                st.session_state["dkt_result"] = result_markdown
                st.success("✅ Đã xây dựng Đề kiểm tra thành công!")
                
        except Exception as e:
            st.error(f"❌ Xảy ra lỗi: {e}")
        finally:
            st.session_state["dkt_processing"] = False

    # HIỂN THỊ KẾT QUẢ VÀ XUẤT WORD
    if st.session_state.get("dkt_result"):
        st.markdown("---")
        st.markdown("## 📑 KẾT QUẢ ĐỀ KIỂM TRA")
        st.markdown(st.session_state["dkt_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Xuất file Word")
        if export_word is None:
            st.error("Chưa cài đặt hoặc bị lỗi module export_word.")
        else:
            try:
                export_data = {
                    "ai_generated_content": st.session_state["dkt_result"],
                    "pages": st.session_state.get("current_dkt_metadata", {}).get("pages", []),
                    "mon": config_data.get("mon_hoc", ""),
                    "lop": config_data.get("lop", ""),
                    "is_dkt": True,
                    "template": "templates/dkt_mau.docx"
                }
                with st.spinner("Đang kết xuất file Word chuẩn (OMML Toán học, Hình ảnh...)..."):
                    word_bytes = export_word(export_data)
                
                st.download_button(
                    label="📥 TẢI XUỐNG FILE WORD (ĐÃ CĂN CHỈNH CHUẨN)",
                    data=word_bytes,
                    file_name=f"De_Kiem_Tra_{config_data.get('mon_hoc', '')}_{config_data.get('lop', '')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Lỗi xuất file Word: {e}")
                
        if st.button("🔄 Tạo lại đề khác", use_container_width=True):
            reset_dkt_result()
            st.rerun()
