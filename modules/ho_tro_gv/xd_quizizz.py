# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_quizizz(ai_engine=None):
    st.markdown("### ⚡ Trợ lý Tạo tệp Import Quizizz / Kahoot / Blooket")
    st.caption("Chuyển đổi văn bản, đề cương ôn tập thành định dạng bảng chuẩn để copy/paste thẳng vào Excel import của các nền tảng trò chơi.")

    with st.container(border=True):
        de_cuong = st.text_area("Dán nội dung đề cương hoặc kiến thức vào đây:", height=200, placeholder="VD: Quang hợp là quá trình thực vật hấp thụ ánh sáng... Nước sôi ở 100 độ C...")
        
        col1, col2 = st.columns(2)
        with col1:
            nen_tang = st.selectbox("Nền tảng đích:", ["Quizizz", "Kahoot", "Blooket"])
        with col2:
            so_luong = st.number_input("Số lượng câu hỏi:", min_value=1, max_value=50, value=10)
        
        btn_chuyen = st.button("🚀 Tạo bộ câu hỏi Import", type="primary", use_container_width=True)

    if btn_chuyen:
        if not de_cuong.strip():
            st.warning("⚠️ Vui lòng cung cấp nội dung đề cương.")
        else:
            with st.spinner(f"AI đang soạn {so_luong} câu hỏi và định dạng chuẩn cho {nen_tang}..."):
                prompt = f"""
                Hãy soạn {so_luong} câu hỏi trắc nghiệm dựa trên nội dung sau:
                {de_cuong}
                
                YÊU CẦU ĐỊNH DẠNG CHO NỀN TẢNG {nen_tang}:
                Kẻ một bảng Markdown gồm các cột sau (Chuẩn để copy dán vào Excel):
                - Cột 1: Question Text (Nội dung câu hỏi)
                - Cột 2: Option 1 (Đáp án A)
                - Cột 3: Option 2 (Đáp án B)
                - Cột 4: Option 3 (Đáp án C)
                - Cột 5: Option 4 (Đáp án D)
                - Cột 6: Correct Answer (Ghi số 1, 2, 3 hoặc 4 tương ứng với đáp án đúng)
                - Cột 7: Time in seconds (Thời gian trả lời, mặc định 30)
                
                Chỉ trả về bảng, không giải thích dài dòng.
                """
                if ai_engine:
                    try:
                        res = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.success("✅ Đã tạo bảng câu hỏi! Thầy/cô bôi đen bảng này, copy và dán vào file Excel mẫu của nền tảng.")
                        st.markdown(res)
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
