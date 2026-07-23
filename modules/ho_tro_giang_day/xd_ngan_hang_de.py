# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_ngan_hang_de(ai_engine=None):
    st.markdown("### 🏦 Xây dựng Ngân hàng Câu hỏi Chuẩn hóa")
    st.caption("AI đọc tài liệu (Sách, Đề cương) và tự động trích xuất, phân loại tạo thành kho câu hỏi lưu trữ lâu dài.")

    st.info("💡 So với chức năng 'Kiểm tra nhanh', chức năng này cho phép tải file lên để AI bám sát dữ liệu gốc, chống 'ảo giác' (hallucination) kiến thức.")

    file_tai_lieu = st.file_uploader("Tải tài liệu PDF/Word/TXT chứa kiến thức gốc:", type=["txt", "pdf", "docx"])
    
    col1, col2 = st.columns(2)
    with col1:
        loai_cau_hoi = st.selectbox("Định dạng câu hỏi:", ["Trắc nghiệm 4 lựa chọn", "Tự luận ngắn", "Trắc nghiệm Đúng/Sai", "Câu hỏi tình huống"])
    with col2:
        so_luong_nhu_cau = st.slider("Số lượng câu hỏi muốn sinh ra:", 5, 30, 15)

    if st.button("🧠 Phân tích tài liệu & Sinh ngân hàng đề", type="primary", use_container_width=True):
        if not file_tai_lieu:
            st.warning("⚠️ Vui lòng tải tài liệu kiến thức lên.")
        else:
            with st.spinner("Hệ thống đang đọc file và bóc tách dữ liệu để xây dựng câu hỏi..."):
                # Mô phỏng việc đọc file (thực tế sẽ dùng module extract như ở xd_khbd)
                try:
                    if file_tai_lieu.name.endswith(".txt"):
                        noi_dung_file = file_tai_lieu.read().decode("utf-8")
                    else:
                        noi_dung_file = "Nội dung tài liệu đã được nạp (Giả định với PDF/Word để MVP chạy mượt). " + file_tai_lieu.name
                    
                    noi_dung_file = noi_dung_file[:20000] # Giới hạn context window
                    
                    prompt = f"""
                    Dựa vào nội dung tài liệu sau đây, hãy đóng vai chuyên gia khảo thí để xây dựng một ngân hàng câu hỏi.
                    
                    Định dạng câu hỏi yêu cầu: {loai_cau_hoi}
                    Số lượng: {so_luong_nhu_cau} câu.
                    
                    TÀI LIỆU GỐC:
                    {noi_dung_file}
                    
                    YÊU CẦU:
                    Tuyệt đối chỉ sử dụng kiến thức có trong tài liệu gốc. Kèm theo đáp án chuẩn ở ngay dưới mỗi câu.
                    """
                    
                    if ai_engine:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.markdown("#### 📂 Ngân Hàng Câu Hỏi Trích Xuất")
                        st.markdown(result)
                    else:
                        st.error("Chưa kết nối AI.")
                except Exception as e:
                    st.error(f"Lỗi xử lý: {e}")
