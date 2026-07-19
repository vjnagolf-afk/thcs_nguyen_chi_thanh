def render_cham_sang_kien(ai_engine):
    st.markdown("### 🔍 Chấm & Góp ý Sáng kiến")
    
    van_ban_sk = st.text_area("Dán nội dung sáng kiến của thầy/cô vào đây:", height=300)
    
    if st.button("⚖️ Chấm điểm & Phản biện"):
        # Prompt: Bạn là chuyên gia giáo dục. Hãy nhận xét sáng kiến dựa trên:
        # Tính mới, tính thực tiễn, bố cục sư phạm và văn phong học thuật.
        # Đưa ra các gợi ý chỉnh sửa cụ thể.
        st.write("Kết quả phản biện sẽ hiển thị ở đây...")
