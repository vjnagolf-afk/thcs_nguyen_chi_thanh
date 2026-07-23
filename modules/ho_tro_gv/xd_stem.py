# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_stem(ai_engine=None):
    st.markdown("### 🚀 Thiết kế Kế hoạch Bài học STEM / STEAM")
    st.caption("AI hỗ trợ lên ý tưởng, thiết kế tiến trình 5 bước (EDP - Quy trình thiết kế kỹ thuật) cho các chủ đề giáo dục STEM.")
    
    with st.container(border=True):
        van_de_thuc_tien = st.text_area("Vấn đề thực tiễn / Tên chủ đề STEM:", height=100, placeholder="VD: Chế tạo thiết bị báo cháy đơn giản, Thiết kế hệ thống tưới cây nhỏ giọt, Làm nến thơm sinh học...")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            mon_chu_dao = st.text_input("Môn học chủ đạo:", placeholder="VD: Vật lí 8")
        with c2:
            thoi_luong = st.text_input("Thời lượng:", placeholder="VD: 2 tiết")
        with c3:
            vat_lieu = st.text_input("Vật liệu (Tùy chọn):", placeholder="Bìa carton, chai nhựa...")
            
        btn_stem = st.button("🛠️ Thiết kế Tiến trình STEM", type="primary", use_container_width=True)

    if btn_stem:
        if not van_de_thuc_tien.strip() or not mon_chu_dao.strip():
            st.warning("⚠️ Vui lòng nhập Vấn đề thực tiễn và Môn học chủ đạo.")
        else:
            with st.spinner("AI đang lên ý tưởng và thiết kế tiến trình STEM 5 bước..."):
                prompt = f"""
                Bạn là Chuyên gia Giáo dục STEM/STEAM cấp THCS.
                Hãy thiết kế một bản tóm tắt Kế hoạch Bài học STEM bám sát "Quy trình thiết kế kỹ thuật (EDP)".
                
                THÔNG TIN CHUNG:
                - Chủ đề/Vấn đề thực tiễn: {van_de_thuc_tien}
                - Môn chủ đạo: {mon_chu_dao}
                - Thời lượng: {thoi_luong}
                - Vật liệu dự kiến: {vat_lieu if vat_lieu else 'Đề xuất vật liệu tái chế, dễ tìm chi phí thấp.'}
                
                YÊU CẦU CẤU TRÚC (Sử dụng Markdown rõ ràng):
                I. TÓM TẮT MỤC TIÊU (Khoa học, Công nghệ, Kỹ thuật, Toán học).
                II. BỘ CÂU HỎI ĐỊNH HƯỚNG DÀNH CHO HỌC SINH (Gợi mở tư duy).
                III. TIẾN TRÌNH 5 BƯỚC:
                1. Xác định vấn đề.
                2. Nghiên cứu kiến thức nền & Đề xuất giải pháp.
                3. Lựa chọn giải pháp & Vẽ bản thiết kế.
                4. Chế tạo mô hình & Thử nghiệm.
                5. Chia sẻ, thảo luận & Điều chỉnh.
                (Mỗi bước mô tả ngắn gọn GV làm gì, HS làm gì).
                """
                if ai_engine:
                    try:
                        res = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown("#### 📐 Khung Kế hoạch Bài học STEM")
                        st.markdown(res)
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
