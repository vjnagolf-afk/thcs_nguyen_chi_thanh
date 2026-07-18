import streamlit as st
import urllib.parse

def render_kiem_tra_nhanh(ai_engine):
    st.markdown("### ⚡ Hệ thống Kiểm tra Nhanh Trực tiếp")
    st.caption("Khởi tạo bài kiểm tra siêu tốc, học sinh quét mã QR và trả lời ngay trên điện thoại.")

    st.markdown("""
    <div style="background-color: #e8f4f8; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
        👨‍🏫 GV tạo câu hỏi ➔ 📱 Chiếu mã QR ➔ 📸 HS quét ➔ ✍️ Trả lời trên điện thoại ➔ 📊 Kết quả hiển thị trực tiếp
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        muc_dich = st.selectbox("Mục đích sử dụng:", ["Khởi động (Warm-up)", "Kiểm tra bài cũ", "Hình thành kiến thức", "Luyện tập", "Exit Ticket (Đánh giá cuối giờ)"])
    with col2:
        chu_de_kt = st.text_input("Chủ đề câu hỏi:", placeholder="Ví dụ: Công thức tính Vận tốc...")

    link_nhan_kq = st.text_input("🔗 Dán Link công cụ nhận câu trả lời (Google Form, Quizizz, Padlet...):", placeholder="https://...")

    if st.button("Tạo phiên Kiểm tra Live", type="primary"):
        if chu_de_kt.strip() and link_nhan_kq.strip():
            st.success(f"Đã mở phiên kiểm tra: {muc_dich} - {chu_de_kt}")
            
            # Chia 2 cột để hiển thị Mã QR và Gợi ý câu hỏi AI
            col_qr, col_cau_hoi = st.columns([1, 2])
            
            with col_qr:
                st.markdown("#### 📸 Mời học sinh quét mã:")
                # Sinh mã QR tự động từ link giáo viên nhập vào
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(link_nhan_kq)}"
                st.image(qr_url, use_container_width=True)
                st.caption(f"Link: {link_nhan_kq}")
                
            with col_cau_hoi:
                st.markdown("#### 🤖 AI Gợi ý câu hỏi:")
                with st.spinner("Đang biên soạn câu hỏi phù hợp..."):
                    prompt = f"Sinh nhanh 1 câu hỏi/tình huống siêu ngắn gọn nhằm mục đích '{muc_dich}' cho nội dung '{chu_de_kt}' để học sinh THCS trả lời ngay trên điện thoại."
                    try:
                        cau_hoi = ai_engine.generate_text(prompt)
                        st.info(cau_hoi)
                    except Exception as e:
                        st.error("Lỗi AI khi tạo câu hỏi.")
        else:
            st.warning("Vui lòng nhập chủ đề và dán Link nhận kết quả để tạo mã QR!")
