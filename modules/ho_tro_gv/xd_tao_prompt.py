# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_tao_prompt(ai_engine=None):
    st.markdown("### 🧠 Thư viện & Công cụ Sinh Prompt Sư phạm")
    st.caption("AI đóng vai trò 'Prompt Engineer' để giúp bạn viết ra những câu lệnh giao tiếp hoàn hảo với các AI khác (ChatGPT, Claude, Midjourney...).")
    
    with st.container(border=True):
        muc_dich = st.selectbox("Mục đích sử dụng AI:", [
            "Viết giáo án / Kế hoạch giảng dạy", 
            "Soạn câu hỏi trắc nghiệm/Tự luận", 
            "Viết email gửi phụ huynh", 
            "Sinh ảnh minh họa (Text-to-Image)", 
            "Lập trình/Tạo mã nhúng HTML"
        ])
        chi_tiet = st.text_area("Trình bày ý tưởng thô của bạn (Càng chi tiết càng tốt):", height=100, placeholder="VD: Tôi muốn tạo 10 câu trắc nghiệm Sinh học lớp 9 bài ADN, mức độ vận dụng cao, có giải thích...")
        
        btn_prompt = st.button("⚙️ Tối ưu hóa Prompt", type="primary", use_container_width=True)

    if btn_prompt:
        if not chi_tiet.strip():
            st.warning("⚠️ Vui lòng trình bày ý tưởng thô của bạn.")
        else:
            with st.spinner("AI đang tái cấu trúc ý tưởng của bạn thành siêu prompt..."):
                prompt = f"""
                Bạn là một Chuyên gia Kỹ thuật Kích hoạt (Prompt Engineer) hàng đầu thế giới.
                Một giáo viên đang muốn sử dụng AI (ChatGPT/Claude/Midjourney) để làm việc sau:
                - Lĩnh vực: {muc_dich}
                - Ý tưởng thô của giáo viên: {chi_tiet}
                
                NHIỆM VỤ: Hãy viết lại ý tưởng thô đó thành một ĐOẠN PROMPT SIÊU HOÀN CHỈNH, CHUYÊN NGHIỆP, TỐI ƯU NHẤT để giáo viên có thể copy và dán vào các công cụ AI khác.
                
                CẤU TRÚC PROMPT CẦN VIẾT RA:
                1. Xác định Rõ Vai trò (Role).
                2. Mô tả nhiệm vụ chi tiết và bối cảnh (Task & Context).
                3. Định dạng đầu ra mong muốn (Format).
                4. Các ràng buộc/Quy tắc nghiêm ngặt (Constraints).
                
                Chỉ in ra đoạn Prompt hoàn chỉnh đặt trong khối ```text ... ``` để giáo viên dễ copy, kèm 1-2 lời khuyên nhỏ bên ngoài.
                """
                if ai_engine:
                    try:
                        res = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.success("✅ Đã sinh Prompt tối ưu! Thầy/cô có thể copy khối text dưới đây để dùng cho các AI khác.")
                        st.markdown(res)
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
