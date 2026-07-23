# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_chu_nhiem(ai_engine=None):
    st.markdown("### 👨‍👩‍👧‍👦 Trợ lý Công tác Chủ nhiệm & Tâm lý")
    st.caption("AI hỗ trợ phân tích tâm lý học sinh, đề xuất kịch bản họp phụ huynh và xử lý các tình huống sư phạm khó.")
    
    with st.container(border=True):
        col_loai, col_do_tuoi = st.columns(2)
        with col_loai:
            chu_de = st.selectbox(
                "Chọn nhóm tình huống cần hỗ trợ:",
                ["Xử lý học sinh vi phạm kỷ luật", "Tư vấn tâm lý (Trầm cảm, bạo lực học đường, cô lập)", "Xây dựng kịch bản họp Phụ huynh", "Hòa giải xung đột giữa Phụ huynh và Giáo viên"]
            )
        with col_do_tuoi:
            do_tuoi = st.selectbox("Khối lớp (Để AI dùng văn phong, tâm lý lứa tuổi phù hợp):", ["Lớp 6 (Chuyển cấp, bỡ ngỡ)", "Lớp 7 - 8 (Dậy thì, nổi loạn)", "Lớp 9 (Áp lực thi cử)"])

        tinh_huong = st.text_area("Mô tả chi tiết tình huống hiện tại:", height=120, placeholder="VD: Hai học sinh nữ đánh nhau vì mâu thuẫn trên mạng xã hội, phụ huynh một bên đang rất bức xúc đòi làm lớn chuyện...")
        
        btn_tu_van = st.button("🧠 AI Phân tích & Đề xuất hướng giải quyết", type="primary", use_container_width=True)

    if btn_tu_van:
        if not tinh_huong.strip():
            st.warning("⚠️ Vui lòng mô tả chi tiết tình huống để AI có cơ sở tư vấn.")
        else:
            with st.spinner("AI đang phân tích tâm lý và soạn thảo kịch bản xử lý..."):
                prompt = f"""
                Bạn là một Chuyên gia Tâm lý học đường và một Hiệu trưởng/Giáo viên chủ nhiệm xuất sắc.
                Hãy giúp giải quyết tình huống sư phạm sau đây một cách khéo léo, thấu tình đạt lý và đúng quy định của Bộ GD&ĐT.
                
                THÔNG TIN:
                - Đối tượng học sinh: {do_tuoi}
                - Nhóm vấn đề: {chu_de}
                - Tình huống thực tế: {tinh_huong}
                
                YÊU CẦU TRÌNH BÀY:
                1. Phân tích nguyên nhân sâu xa / Tâm lý của các bên liên quan.
                2. Các bước xử lý cụ thể (Bước 1 làm gì, Bước 2 làm gì...).
                3. Gợi ý Kịch bản lời thoại (Cách GVCN nói chuyện với Học sinh / Phụ huynh để hạ nhiệt và đồng thuận).
                """
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown("#### 🛡️ Cẩm nang xử lý tình huống")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
