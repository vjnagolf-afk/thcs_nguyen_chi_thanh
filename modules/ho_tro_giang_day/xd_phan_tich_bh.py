# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_phan_tich_bh(ai_engine=None):
    st.markdown("### 🕵️‍♀️ Trợ lý Phân tích Bài học (Lesson Study)")
    st.caption("AI hỗ trợ phân tích dự giờ: Đánh giá kịch bản bài học, các hoạt động tương tác và thời lượng phân bổ dựa trên bản ghi chép/giáo án dự giờ.")

    with st.container(border=True):
        col_noidung, col_opt = st.columns([2, 1])
        
        with col_noidung:
            noidung_du_gio = st.text_area("Dán nội dung giáo án dự giờ hoặc ghi chép diễn biến lớp học:", height=250, placeholder="VD: Phút 0-5: GV ổn định lớp, Phút 5-15: Kiểm tra bài cũ, Phút 15-30: Hoạt động nhóm...")
        
        with col_opt:
            st.markdown("**Tiêu chí Phân tích:**")
            tieu_chi = st.radio("Chọn góc nhìn phân tích:", [
                "Phân tích Tỉ lệ thời gian (Giáo viên nói vs Học sinh hoạt động)",
                "Đánh giá mức độ phát triển Năng lực học sinh",
                "Phát hiện các điểm nghẽn/nhàm chán và đề xuất cải tiến"
            ])
            
            btn_phan_tich = st.button("🔍 Tiến hành Phân tích", type="primary", use_container_width=True)

    if btn_phan_tich:
        if not noidung_du_gio.strip():
            st.warning("⚠️ Vui lòng dán nội dung dự giờ/giáo án.")
        else:
            with st.spinner("AI đang nghiền ngẫm diễn biến bài học..."):
                prompt = f"""
                Bạn là một chuyên gia Sư phạm và Cố vấn chuyên môn giáo dục.
                Hãy đọc ghi chép diễn biến bài học dưới đây và tiến hành phân tích theo tiêu chí: {tieu_chi}.
                
                GHI CHÉP BÀI HỌC:
                {noidung_du_gio}
                
                YÊU CẦU:
                - Đưa ra những nhận định mang tính xây dựng, khách quan.
                - Trích dẫn cụ thể các hoạt động trong ghi chép để làm minh chứng cho nhận định.
                - Đề xuất ít nhất 2 giải pháp cụ thể để bài học hiệu quả hơn.
                """
                
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown("#### 📑 Báo cáo Phân tích Bài học")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
