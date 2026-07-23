# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_hoc_lieu(ai_engine=None):
    st.markdown("### 📚 Trợ lý Tổng hợp & Thiết kế Học liệu")
    st.caption("Chuyển đổi văn bản thô, bài báo hoặc chương sách dài thành các định dạng học liệu ngắn gọn, dễ hiểu cho học sinh.")

    col_input, col_config = st.columns([2, 1])

    with col_input:
        van_ban_goc = st.text_area("Dán nội dung kiến thức thô vào đây (Tối đa 10.000 từ):", height=250, placeholder="Ví dụ: Đoạn văn bản dài về Lịch sử Việt Nam giai đoạn 1945-1954...")
    
    with col_config:
        st.markdown("**Cấu hình đầu ra:**")
        loai_hoc_lieu = st.selectbox(
            "Chọn định dạng học liệu:", 
            ["Tóm tắt Ý chính (Bullet points)", "Sơ đồ tư duy (Định dạng văn bản)", "Kịch bản Thuyết trình (Slides)", "Thẻ ghi nhớ (Flashcards Q&A)"]
        )
        doi_tuong = st.selectbox("Đối tượng học sinh:", ["Cấp THCS (Dễ hiểu, trực quan)", "Cấp THPT (Sâu sắc, phân tích)", "Giáo viên (Học thuật)"])
        
        btn_tao = st.button("🪄 Tạo Học liệu", type="primary", use_container_width=True)

    if btn_tao:
        if not van_ban_goc.strip():
            st.warning("⚠️ Vui lòng cung cấp văn bản gốc.")
        else:
            with st.spinner(f"AI đang chuyển đổi văn bản thành {loai_hoc_lieu}..."):
                prompt = f"""
                Bạn là một Chuyên gia thiết kế học liệu sư phạm xuất sắc.
                Dựa vào nội dung văn bản dưới đây, hãy chuyển đổi nó thành định dạng: {loai_hoc_lieu}.
                Đối tượng tiếp cận: {doi_tuong}.
                
                YÊU CẦU ĐẶC BIỆT TÙY THEO ĐỊNH DẠNG:
                - Nếu là Sơ đồ tư duy: Trình bày dạng cây phân cấp (Sử dụng các ký tự -, *, >, để thụt lề rõ ràng).
                - Nếu là Kịch bản Slides: Chia rõ Slide 1 (Tiêu đề, Nội dung chính, Hình ảnh gợi ý), Slide 2...
                - Nếu là Thẻ ghi nhớ: Liệt kê các cặp Mặt trước (Câu hỏi/Khái niệm) - Mặt sau (Trả lời/Định nghĩa).
                
                VĂN BẢN GỐC:
                {van_ban_goc}
                """
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown(f"#### 📄 Kết quả: {loai_hoc_lieu}")
                        st.markdown(result)
                        
                        st.download_button(
                            label="⬇️ Tải học liệu về máy (.txt)",
                            data=result,
                            file_name=f"HocLieu_{loai_hoc_lieu.replace(' ', '')}.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Lỗi khi gọi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
