# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_kiem_tra_nhanh(ai_engine=None):
    st.markdown("### ⏱️ Sinh Đề Kiểm tra Nhanh (Mini Test)")
    st.caption("Khởi tạo nhanh các bài kiểm tra 5 phút, 15 phút ngay trên lớp với các câu hỏi trắc nghiệm hoặc điền khuyết.")

    with st.form("form_kiem_tra_nhanh"):
        col1, col2, col3 = st.columns(3)
        with col1:
            mon_hoc = st.selectbox("Môn học:", ["Toán", "Ngữ Văn", "Tiếng Anh", "KHTN", "Vật lí", "Hóa học", "Sinh học", "Tin học"])
        with col2:
            khoi_lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
        with col3:
            so_luong = st.number_input("Số lượng câu hỏi:", min_value=1, max_value=50, value=10)
            
        chu_de = st.text_input("Chủ đề kiểm tra (Nhập chi tiết bài học):", placeholder="Ví dụ: Cấu tạo tế bào thực vật, Các thì trong Tiếng Anh...")
        muc_do = st.multiselect("Mức độ nhận thức:", ["Nhận biết", "Thông hiểu", "Vận dụng"], default=["Nhận biết", "Thông hiểu"])
        
        submitted = st.form_submit_button("🚀 Sinh Đề Kiểm Tra", type="primary", use_container_width=True)

    if submitted:
        if not chu_de.strip():
            st.warning("⚠️ Vui lòng nhập chủ đề kiểm tra.")
        else:
            with st.spinner("AI đang soạn câu hỏi trắc nghiệm và trộn đề..."):
                prompt = f"""
                Bạn là một giáo viên {mon_hoc} {khoi_lop} giàu kinh nghiệm.
                Hãy soạn một bài kiểm tra nhanh gồm {so_luong} câu hỏi trắc nghiệm (có 4 đáp án A, B, C, D).
                Chủ đề: {chu_de}.
                Mức độ tập trung vào: {", ".join(muc_do)}.
                
                YÊU CẦU:
                1. Các câu hỏi phải chính xác về mặt khoa học, không có đáp án gây tranh cãi.
                2. Đánh số thứ tự từ Câu 1 đến Câu {so_luong}.
                3. BẮT BUỘC: Ở phần cuối cùng của kết quả, hãy cung cấp một [BẢNG ĐÁP ÁN ĐÚNG] và giải thích ngắn gọn cho các câu hỏi Khó/Vận dụng.
                """
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.success("✅ Đã sinh đề thành công!")
                        st.markdown("---")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Lỗi khi gọi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
