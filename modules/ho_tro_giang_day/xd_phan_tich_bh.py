import streamlit as st

def render_phan_tich_bh(ai_engine):
    st.markdown("### 📖 Phân tích bài học")
    st.caption("AI tự động 'bóc tách' nội dung để giúp giáo viên thiết kế chiến lược giảng dạy tối ưu nhất.")

    noi_dung = st.text_area("Nhập tên bài học hoặc nội dung trọng tâm:", height=100, placeholder="Ví dụ: Lực ma sát (Vật lý 6), Tế bào nhân thực...")
    
    if st.button("🧠 Bắt đầu Phân tích", type="primary"):
        if noi_dung.strip():
            with st.spinner("AI đang phân tích chuyên sâu bài học..."):
                prompt = f"""
                Hãy đóng vai một chuyên gia sư phạm. Phân tích bài học/chủ đề "{noi_dung}" cho học sinh cấp THCS theo đúng các mục sau:
                1. Yêu cầu cần đạt
                2. Kiến thức trọng tâm
                3. Kiến thức dễ nhầm lẫn (Misconceptions)
                4. Mức độ nhận thức (Theo thang Bloom)
                5. Khó khăn dự kiến của học sinh
                6. Gợi ý hoạt động dạy học
                7. Gợi ý thí nghiệm (Nếu có)
                8. Gợi ý công cụ/công nghệ AI hỗ trợ
                Trình bày dưới dạng Bullet point rõ ràng, súc tích.
                """
                try:
                    phan_tich = ai_engine.generate_text(prompt)
                    st.markdown("---")
                    st.write(phan_tich)
                except Exception as e:
                    st.error(f"Lỗi phân tích AI: {e}")
        else:
            st.warning("Thầy vui lòng nhập nội dung bài học cần phân tích!")
