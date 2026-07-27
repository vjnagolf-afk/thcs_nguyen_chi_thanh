# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: views/xd_ma_tran_tu_de_view.py
Nhiệm vụ: Giao diện Sinh Ma trận & Đặc tả từ Đề kiểm tra có sẵn.
Chuẩn MVC - Giao diện tinh gọn, đẩy việc xử lý cho Data & Export_Word.
============================================================
"""

import streamlit as st
from views.xd_ma_tran_tu_de_data import (
    init_session_state_mt,
    reset_mt_result,
    extract_exam_source,
    generate_matrix_ai
)

try:
    from export.export_word import export_word
except ImportError:
    export_word = None

def render_xd_ma_tran_tu_de(ai_engine=None):
    # Tham số ai_engine được giữ lại để app.py gọi không bị lỗi TypeError, 
    # nhưng ta sẽ không dùng nó để tránh lỗi xác thực (KeyError).
    
    init_session_state_mt()

    st.markdown("## 🧩 Sinh Ma trận & Đặc tả từ Đề kiểm tra có sẵn")
    st.info("💡 Tính năng phân tích ngược (Reverse Engineering): Tải lên một đề kiểm tra PDF/Word bất kỳ, AI sẽ tự động đọc, đếm số câu, phân loại mức độ (Biết/Hiểu/Vận dụng) và lập bảng Ma Trận, Đặc tả chuẩn Công văn 7991.")

    col1, col2 = st.columns(2)
    with col1:
        mon_hoc = st.selectbox(
            "Môn học",
            ["Khoa học tự nhiên", "Toán học", "Ngữ văn", "Ngoại ngữ", "Khác"],
            key="mt_mon"
        )
    with col2:
        lop = st.selectbox(
            "Lớp",
            ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"],
            index=3,
            key="mt_lop"
        )

    st.markdown("### 📂 Nguồn dữ liệu Đề kiểm tra")
    file_de = st.file_uploader(
        "Tải lên đề kiểm tra có sẵn (PDF, DOCX, TXT):",
        type=["pdf", "docx", "txt"],
        key="mt_file"
    )
    
    ai_model = st.selectbox(
        "Mô hình phân tích (Khuyên dùng Pro để phân tích chính xác):", 
        options=["Gemini 2.5 Pro (Chuyên sâu)", "Gemini 2.5 Flash (Tốc độ cao)", "GPT-4o (Cao cấp)", "GPT-4o Mini"],
        index=0
    )

    if st.button("🚀 PHÂN TÍCH ĐỀ & LẬP MA TRẬN", type="primary", use_container_width=True):
        if not file_de:
            st.warning("⚠️ Vui lòng tải lên đề kiểm tra có sẵn.")
            return

        st.session_state["mt_processing"] = True
        try:
            with st.spinner("⏳ Bước 1: Đang quét và trích xuất nội dung đề thi..."):
                exam_text = extract_exam_source(file_de)
                if not exam_text:
                    raise ValueError("Không đọc được nội dung từ file đề thi.")

            with st.spinner("🧠 Bước 2: AI đang phân tích từng câu hỏi và đối chiếu Công văn 7991..."):
                result_markdown = generate_matrix_ai(ai_model, mon_hoc, lop, exam_text)
                st.session_state["mt_result"] = result_markdown
                st.success("✅ Đã lập Ma trận và Bản đặc tả thành công!")
                
        except Exception as e:
            st.error(f"❌ Xảy ra lỗi: {e}")
        finally:
            st.session_state["mt_processing"] = False

    # ========================================================
    # HIỂN THỊ KẾT QUẢ VÀ XUẤT WORD
    # ========================================================
    if st.session_state.get("mt_result"):
        st.markdown("---")
        st.markdown("### 📑 KẾT QUẢ PHÂN TÍCH")
        
        # In Markdown thô ra giao diện để Giáo viên xem trước bảng
        st.markdown(st.session_state["mt_result"], unsafe_allow_html=True)

        st.markdown("### 📥 Xuất file Word")
        if export_word is None:
            st.error("Chưa cài đặt hoặc bị lỗi module export_word.")
        else:
            try:
                # Chuyển đổi Markdown thành Word Native (Căn lề, OMML, Kẻ bảng tự động)
                export_data = {
                    "ai_generated_content": st.session_state["mt_result"],
                    "mon": mon_hoc,
                    "lop": lop,
                    "is_dkt": False 
                }
                
                with st.spinner("Đang kết xuất bảng Word Native..."):
                    word_bytes = export_word(export_data)
                
                st.download_button(
                    label="📥 TẢI XUỐNG FILE WORD (MA TRẬN & ĐẶC TẢ)",
                    data=word_bytes,
                    file_name=f"Ma_Tran_Dac_Ta_Tu_De_{mon_hoc}_{lop}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Lỗi xuất file Word: {e}")
                
        if st.button("🔄 Phân tích đề khác", use_container_width=True):
            reset_mt_result()
            st.rerun()
