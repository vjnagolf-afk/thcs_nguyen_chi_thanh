import streamlit as st
from pypdf import PdfReader
import re

def render_bien_ban(db): # Tham số db giữ nguyên để không lỗi app.py
    st.markdown("### 📝 Trợ lý Thư ký: Xây dựng Biên bản Sinh hoạt")
    st.caption("AI tự động soạn thảo biên bản họp bám sát cấu trúc dự thảo kế hoạch, hỗ trợ nhiều hình thức sinh hoạt chuyên môn khác nhau.")

    # Lấy danh sách GV từ bộ nhớ (nếu có) để làm menu chọn Chủ tọa/Thư ký
    ds_gv = st.session_state.get("danh_sach_gv", ["Chưa có dữ liệu (Hãy qua thẻ Danh sách)"])
    
    # Khởi tạo bộ nhớ tạm để không mất kết quả biên bản khi tải về
    if "ket_qua_bien_ban" not in st.session_state:
        st.session_state.ket_qua_bien_ban = None

    # 1. KHU VỰC THÔNG TIN CUỘC HỌP
    with st.expander("📌 Bước 1: Thông tin cơ bản", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            loai_cuoc_hop = st.selectbox("Loại hình sinh hoạt:", [
                "Sinh hoạt chuyên môn định kỳ",
                "Nghiên cứu bài học (Bước 2, 3)",
                "Xây dựng chuyên đề / STEM",
                "Phân tích kết quả kiểm tra",
                "Thống nhất ma trận, đặc tả đề",
                "Hình thức khác..."
            ])
        with col2:
            chu_toa = st.selectbox("👨‍🏫 Chủ tọa:", ds_gv, index=0)
        with col3:
            # Chọn thư ký (mặc định người thứ 2 trong danh sách nếu có)
            index_thu_ky = 1 if len(ds_gv) > 1 else 0
            thu_ky = st.selectbox("✍️ Thư ký:", ds_gv, index=index_thu_ky)

    # 2. KHU VỰC NẠP DỰ THẢO (Bám sát dàn ý)
    st.markdown("#### 📄 Bước 2: Nạp Dự thảo kế hoạch / Dàn ý")
    st.info("💡 AI sẽ dò tìm các đề mục lớn (I, II, III...) và mục nhỏ (1, 2, a, b...) trong văn bản này để tạo khung biên bản tương ứng.")
    
    tab_nhap, tab_file = st.tabs(["✍️ Dán văn bản Dự thảo", "📂 Tải file PDF Dự thảo"])
    noidung_du_thao = ""
    
    with tab_nhap:
        text_input = st.text_area("Dán nội dung dự thảo vào đây:", height=150, placeholder="Ví dụ:\nI. Đánh giá công tác tuần qua\n1. Ưu điểm\n2. Tồn tại\nII. Triển khai công tác tuần tới...")
        if text_input:
            noidung_du_thao = text_input
            
    with tab_file:
        uploaded_file = st.file_uploader("Tải lên file dự thảo (PDF)", type=["pdf"])
        if uploaded_file:
            try:
                reader = PdfReader(uploaded_file)
                extracted_text = ""
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
                noidung_du_thao = extracted_text
                st.success("✅ Đã đọc thành công nội dung file PDF!")
            except Exception as e:
                st.error(f"Lỗi đọc file PDF: {e}")

    # 3. NÚT XỬ LÝ AI
    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        if st.button("🪄 Viết Biên bản bằng AI", type="primary", use_container_width=True):
            if not noidung_du_thao.strip():
                st.warning("⚠️ Thầy vui lòng cung cấp nội dung hoặc file Dự thảo trước nhé!")
            else:
                with st.spinner("🧠 Thư ký AI đang tổng hợp và soạn thảo biên bản..."):
                    # Prompt ép AI tuân thủ cấu trúc
                    prompt = f"""
                    Bạn là Thư ký tổ chuyên môn trường THCS. Hãy viết một "Biên bản cuộc họp" chi tiết.
                    
                    THÔNG TIN CHUNG:
                    - Loại hình cuộc họp: {loai_cuoc_hop}
                    - Chủ tọa: {chu_toa}
                    - Thư ký: {thu_ky}
                    
                    NGUYÊN TẮC BẮT BUỘC (QUAN TRỌNG NHẤT):
                    Bên dưới là văn bản Dự thảo kế hoạch. Bạn PHẢI bám sát TUYỆT ĐỐI cấu trúc các đề mục của bản dự thảo này (Ví dụ: I, II, III... 1, 2, 3... a, b, c...). 
                    Không được tự ý bỏ sót bất kỳ mục nào có trong dự thảo.
                    
                    YÊU CẦU NỘI DUNG:
                    1. Mở đầu bằng Thời gian, Địa điểm, Thành phần tham dự.
                    2. Tại mỗi đề mục, hãy viết phần trình bày của Chủ tọa, sau đó TỰ ĐỘNG THÊM VÀO các ý kiến thảo luận giả định (hợp lý, logic mang tính sư phạm) của các thành viên trong tổ.
                    3. Cuối mỗi mục lớn phải có kết luận của Chủ tọa.
                    
                    DỰ THẢO KẾ HOẠCH:
                    '''{noidung_du_thao}'''
                    """
                    
                    try:
                        # Thay 'ai_engine.generate_text' bằng phương thức gọi AI thực tế của thầy (nếu được truyền qua db/session)
                        # Vì db không chứa ai_engine trong context này, em giả định thầy có ai_engine trong session hoặc import
                        if "ai_engine" in st.session_state:
                            bien_ban = st.session_state.ai_engine.generate_text(prompt)
                        else:
                            # Mockup nếu chưa kết nối AI để test giao diện
                            bien_ban = f"*(Đây là bản demo vì chưa truyền ai_engine vào hàm render_bien_ban)*\n\n**BIÊN BẢN {loai_cuoc_hop.upper()}**\n\nChủ tọa: {chu_toa}\nThư ký: {thu_ky}\n\n[Nội dung AI sinh ra dựa trên dự thảo sẽ hiện ở đây...]"
                            
                        st.session_state.ket_qua_bien_ban = bien_ban
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi gọi AI: {e}. Vui lòng kiểm tra lại kết nối AI Engine.")

    with col_btn2:
        if st.button("🗑️ Xóa / Làm lại", type="secondary", use_container_width=True):
            st.session_state.ket_qua_bien_ban = None
            st.rerun()

    # 4. HIỂN THỊ KẾT QUẢ VÀ TẢI VỀ
    st.markdown("---")
    if st.session_state.ket_qua_bien_ban:
        st.success("🎉 Biên bản đã hoàn thành! Thầy có thể đọc lại hoặc tải về máy.")
        
        # Nút xuất file Word/TXT
        st.download_button(
            label="⬇️ Tải Biên bản về máy (.txt)",
            data=st.session_state.ket_qua_bien_ban,
            file_name="Bien_Ban_SHCM.txt",
            mime="text/plain",
            type="primary"
        )
        
        st.markdown("#### 📜 Nội dung Biên bản")
        # Dùng một khung văn bản để giáo viên có thể chỉnh sửa tay được luôn trước khi copy
        st.text_area("Chỉnh sửa biên bản (nếu cần):", value=st.session_state.ket_qua_bien_ban, height=500)
