import streamlit as st
import sys
from pathlib import Path

def render_xd_tro_choi(ai_engine):
    st.markdown("### 🎮 Trợ lý Thiết kế Trò chơi Học tập")
    
    # 1. BẢNG ĐIỀU KHIỂN
    c1, c2 = st.columns([2, 1])
    loai_tro_choi = c1.selectbox("Loại trò chơi:", [
        "Ô chữ (Crossword)", 
        "Đố vui (Quiz Show)", 
        "Giải cứu đại dương / Phiêu lưu", 
        "Trò chơi nhập vai (Roleplay Game)",
        "Trò chơi phản xạ nhanh"
    ])
    doi_tuong = c2.selectbox("Đối tượng:", ["Cá nhân", "Nhóm nhỏ", "Cả lớp"])
    
    chu_de = st.text_input("Nội dung/Chủ đề kiến thức:", placeholder="VD: Bảng tuần hoàn hóa học, Các thì trong tiếng Anh...")
    muc_tieu = st.text_area("Mục tiêu hoặc yêu cầu đặc biệt:", placeholder="VD: Trò chơi cần sôi nổi, không quá 10 phút, HS cần vận động nhẹ...")

    # 2. XỬ LÝ LOGIC
    if st.button("🚀 THIẾT KẾ TRÒ CHƠI", type="primary", use_container_width=True):
        if not chu_de.strip():
            st.error("⚠️ Vui lòng nhập Chủ đề kiến thức!")
        else:
            with st.spinner("⏳ AI đang xây dựng luật chơi và kịch bản..."):
                prompt = f"""
                Bạn là một chuyên gia sáng tạo trò chơi giáo dục (Gamification). Hãy thiết kế một trò chơi học tập dựa trên thông tin sau:
                - Loại trò chơi: {loai_tro_choi}
                - Chủ đề: {chu_de}
                - Đối tượng: {doi_tuong}
                - Mục tiêu: {muc_tieu}

                YÊU CẦU TRẢ VỀ:
                1. Tên trò chơi (Gây tò mò, hấp dẫn).
                2. Luật chơi (Chi tiết, dễ hiểu, có cách tính điểm).
                3. Các bước triển khai (Chuẩn bị gì, thực hiện trong bao lâu).
                4. Nội dung câu hỏi/thử thách (Nếu là đố vui/ô chữ thì liệt kê cụ thể các câu hỏi và đáp án).
                5. Lời dẫn cho giáo viên (Để quản trò khuấy động không khí).
                
                Lưu ý: Ngôn ngữ gần gũi, phù hợp với học sinh THCS, không sử dụng ký tự '>' đầu dòng.
                """
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['trochoi_content'] = content
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi AI: {e}")

    if st.session_state.get('trochoi_content'):
        st.markdown("---")
        st.markdown(st.session_state['trochoi_content'])
        
        if st.button("🗑️ Xóa"):
            st.session_state.pop('trochoi_content', None)
            st.rerun()
