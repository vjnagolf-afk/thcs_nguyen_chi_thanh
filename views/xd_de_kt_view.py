# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: views/xd_de_kt_view.py
Giao diện Xây dựng Đề kiểm tra, Ma trận, Bản đặc tả và Đáp án.
Hỗ trợ tích hợp Metadata (Ảnh/Bảng) cho file xuất Word.
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


def render_xd_de_kt():
    init_session_state_de_kt()

    st.markdown("## 📝 Xây dựng Đề kiểm tra (Ma trận - Đặc tả - Đề - Đáp án)")
    st.info("Hệ thống sử dụng AI để tự động bóc tách kiến thức từ tài liệu SGK/Chuyên đề, thiết lập Ma trận 4 mức độ, Bản đặc tả chi tiết và sinh Đề kiểm tra chuẩn.")

    # 1. THIẾT LẬP CẤU HÌNH
    with st.expander("⚙️ Thiết lập Cấu hình Đề kiểm tra", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            mon_hoc = st.text_input("Môn học:", placeholder="VD: Khoa học tự nhiên, Toán...")
            lop = st.text_input("Lớp:", placeholder="VD: Lớp 9")
        with col2:
            thoi_gian = st.number_input("Thời gian làm bài (phút):", min_value=15, max_value=180, value=45, step=5)
            ty_le = st.text_input("Tỉ lệ Trắc nghiệm / Tự luận (Điểm):", value="70% Trắc nghiệm (7 điểm) / 30% Tự luận (3 điểm)")
            
        yeu_cau_dac_biet = st.text_area("Yêu cầu đặc biệt (Tuỳ chọn):", placeholder="VD: Tập trung nhiều vào phần Khúc xạ ánh sáng, mức độ Vận dụng cao đặt vào Tự luận...")

    # 2. UPLOAD TÀI LIỆU NGUỒN
    st.markdown("### 📂 Nguồn dữ liệu (File SGK / Bài giảng)")
    uploaded_files = st.file_uploader(
        "Tải lên file PDF hoặc Word (Khuyên dùng file có chứa hình ảnh, bài tập):", 
        type=["pdf", "docx"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"Đã tải lên {len(uploaded_files)} file. Hệ thống sẽ trích xuất cả Văn bản, Hình ảnh và Bảng biểu.")

    # 3. CHỌN MÔ HÌNH VÀ TẠO ĐỀ
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
        if not mon_hoc or not lop:
            st.warning("⚠️ Thầy/Cô vui lòng nhập Môn học và Lớp.")
            return
            
        st.session_state["dkt_processing"] = True
        
        try:
            with st.spinner("⏳ Bước 1: Đang bóc tách Văn bản, Hình ảnh và Bảng biểu từ tài liệu..."):
                source_text = read_multiple_files_dkt(uploaded_files)
                
            with st.spinner("🧠 Bước 2: AI đang tính toán Ma trận, lập Đặc tả và biên soạn Đề (Có thể mất 30-60 giây)..."):
                config = {
                    "mon_hoc": mon_hoc,
                    "lop": lop,
                    "thoi_gian": thoi_gian,
                    "ty_le": ty_le,
                    "yeu_cau_dac_biet": yeu_cau_dac_biet
                }
                result_markdown = generate_dkt_ai(ai_model, config, source_text)
                st.session_state["dkt_result"] = result_markdown
                st.success("✅ Đã xây dựng Đề kiểm tra thành công!")
                
        except Exception as e:
            st.error(f"❌ Xảy ra lỗi: {e}")
        finally:
            st.session_state["dkt_processing"] = False

    # 4. HIỂN THỊ KẾT QUẢ VÀ XUẤT WORD
    if st.session_state.get("dkt_result"):
        st.markdown("---")
        st.markdown("## 📑 KẾT QUẢ ĐỀ KIỂM TRA")
        st.markdown(st.session_state["dkt_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Xuất file Word")
        if export_word is None:
            st.error("Chưa cài đặt hoặc bị lỗi module export_word.")
        else:
            try:
                # Đóng gói dữ liệu + Truyền template mẫu cho file Đề Kiểm Tra nếu cần
                export_data = {
                    "ai_generated_content": st.session_state["dkt_result"],
                    # Lấy metadata ảnh/bảng từ session_state (đã lưu ở bước read_multiple_files_dkt)
                    "pages": st.session_state.get("current_dkt_metadata", {}).get("pages", []),
                    "mon": mon_hoc,
                    "lop": lop,
                    "is_dkt": True,  # Flag báo cho export_word biết đây là đề kiểm tra
                    "template": "templates/dkt_mau.docx" # Định hướng template nếu export_word hỗ trợ sau này
                }
                
                with st.spinner("Đang kết xuất file Word chuẩn (OMML Toán học, Hình ảnh...)..."):
                    word_bytes = export_word(export_data)
                
                st.download_button(
                    label="📥 TẢI XUỐNG FILE WORD (ĐÃ CĂN CHỈNH CHUẨN)",
                    data=word_bytes,
                    file_name=f"De_Kiem_Tra_{mon_hoc}_{lop}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Lỗi xuất file Word: {e}")
                
        if st.button("🔄 Tạo lại đề khác", use_container_width=True):
            reset_dkt_result()
            st.rerun()
