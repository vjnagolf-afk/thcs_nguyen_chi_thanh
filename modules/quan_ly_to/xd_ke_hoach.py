import streamlit as st

def render_ke_hoach():
    # Thầy vẫn có thể để tên hàm/file cũ để khỏi sửa import, nhưng giao diện sẽ mang tên mới
    st.markdown("### 🎯 Quản lý và Xây dựng Chuyên đề Giáo dục")
    st.caption("Không gian chia sẻ, thiết kế và lưu trữ các chuyên đề chuyên môn sâu rộng, bám sát định hướng đổi mới giáo dục.")

    # 1. TRƯNG BÀY 6 MẢNG CHUYÊN ĐỀ BẰNG TABS
    st.markdown("#### 📚 Hệ thống Chuyên đề Trọng tâm")
    
    tabs_cd = st.tabs([
        "🛠️ PP & Kỹ thuật", 
        "📖 NC Bài học", 
        "📝 Kiểm tra ĐG", 
        "🎯 Phân hóa HS", 
        "💻 CNTT & Số hóa", 
        "🤝 Nghiệp vụ QL"
    ])

    with tabs_cd[0]:
        st.info("""
        **1. Phương pháp và Kỹ thuật dạy học**
        * **Đổi mới phương pháp:** Áp dụng các mô hình như Bàn tay nặn bột, Dạy học theo dự án, Giáo dục STEM/STEAM, phát huy tính tích cực, tự chủ của học sinh.
        * **Dạy học tích hợp và liên môn:** Xây dựng kế hoạch giảng dạy liên kết các kiến thức bộ môn gần gũi với thực tiễn.
        * **Phát triển năng lực:** Tập trung thiết kế bài giảng để phát triển phẩm chất, năng lực cốt lõi theo Chương trình GDPT.
        """)

    with tabs_cd[1]:
        st.success("""
        **2. Nghiên cứu bài học (Lesson Study)**
        * **Xây dựng kế hoạch bài dạy:** Giáo viên cùng nhau soạn, góp ý và hoàn thiện giáo án một chủ đề hoặc bài học khó.
        * **Dự giờ và phân tích bài học:** Tổ chức dạy thực nghiệm, quay phim, quan sát phản ứng, mức độ tiếp thu và khó khăn của học sinh, từ đó rút kinh nghiệm chung.
        """)

    with tabs_cd[2]:
        st.warning("""
        **3. Kiểm tra, đánh giá học sinh**
        * **Đổi mới đánh giá năng lực:** Xây dựng ngân hàng câu hỏi, đề kiểm tra thường xuyên và định kỳ theo hướng phát triển năng lực (tăng cường câu hỏi vận dụng, thực tiễn).
        * **Đánh giá quá trình:** Hướng dẫn cách chấm điểm, nhận xét và hỗ trợ học sinh tiến bộ thông qua các hoạt động trên lớp.
        """)

    with tabs_cd[3]:
        st.error("""
        **4. Hỗ trợ, phân hóa đối tượng**
        * **Phụ đạo học sinh chưa đạt:** Đưa ra các giải pháp cụ thể giúp học sinh lấy lại căn bản, cải thiện kết quả học tập.
        * **Bồi dưỡng học sinh giỏi:** Xây dựng chuyên đề chuyên sâu, các dạng bài tập nâng cao để ôn thi các cấp.
        """)

    with tabs_cd[4]:
        st.info("""
        **5. Ứng dụng CNTT và Chuyển đổi số**
        * **Ứng dụng AI trong giáo dục:** Sử dụng các công cụ Trí tuệ nhân tạo để hỗ trợ soạn giáo án, thiết kế bài tập và hỗ trợ quản lý lớp.
        * **Sử dụng phần mềm dạy học:** Hướng dẫn sử dụng phần mềm tạo bài giảng E-learning, trò chơi tương tác (Quizizz, Kahoot, Padlet), hoặc thí nghiệm ảo.
        """)

    with tabs_cd[5]:
        st.success("""
        **6. Nghiệp vụ và quản lý lớp học**
        * **Công tác chủ nhiệm lớp:** Giải quyết các tình huống sư phạm, giáo dục học sinh cá biệt, hoặc xây dựng tập thể lớp đoàn kết.
        * **Tư vấn tâm lý học đường:** Các phương pháp hỗ trợ học sinh có vấn đề về tâm lý, áp lực học tập.
        """)

    st.markdown("---")

    # 2. TRỢ LÝ AI: LẬP KẾ HOẠCH TRIỂN KHAI CHUYÊN ĐỀ
    st.markdown("#### 🤖 Trợ lý AI: Khởi tạo Khung Kế hoạch Chuyên đề")
    st.caption("Chọn một nhóm chuyên đề và cung cấp ý tưởng, AI sẽ lập ngay một khung kế hoạch chi tiết để tổ chuyên môn xét duyệt.")
    
    # Form yêu cầu AI
    with st.container(border=True):
        col_form1, col_form2 = st.columns([1, 2])
        with col_form1:
            nhom_cd = st.selectbox("Thuộc nhóm chuyên đề:", [
                "Phương pháp và Kỹ thuật dạy học",
                "Nghiên cứu bài học",
                "Kiểm tra, đánh giá học sinh",
                "Hỗ trợ, phân hóa đối tượng",
                "Ứng dụng CNTT và Chuyển đổi số",
                "Nghiệp vụ và quản lý lớp học"
            ])
            nguoi_bao_cao = st.text_input("Người báo cáo/Phụ trách:", placeholder="VD: Cô Huyền Trang")
        with col_form2:
            ten_chuyen_de = st.text_area("Tên chuyên đề & Ý tưởng trọng tâm:", height=110, placeholder="VD: Xây dựng chủ đề STEM 'Thuyền tự hành' để phát triển năng lực giải quyết vấn đề cho học sinh khối 8.")

        if st.button("🚀 Sinh Kế hoạch Chuyên đề", type="primary", use_container_width=True):
            if ten_chuyen_de.strip():
                with st.spinner("AI đang thiết kế khung kế hoạch chuyên đề..."):
                    prompt = f"""
                    Hãy đóng vai Tổ trưởng chuyên môn. Viết một 'Kế hoạch triển khai chuyên đề' thật chi tiết, khoa học, bám sát các tiêu chí của trường THCS.
                    
                    THÔNG TIN CHUYÊN ĐỀ:
                    - Nhóm chuyên đề: {nhom_cd}
                    - Tên chuyên đề/Ý tưởng: {ten_chuyen_de}
                    - Người phụ trách: {nguoi_bao_cao}
                    
                    CẤU TRÚC KẾ HOẠCH BẮT BUỘC:
                    I. Mục đích, yêu cầu (Phát triển năng lực gì? Giải quyết vấn đề gì?)
                    II. Đối tượng và thời gian thực hiện
                    III. Nội dung chi tiết của chuyên đề
                    IV. Tổ chức thực hiện (Phân công chuẩn bị, tiến trình báo cáo/dự giờ)
                    
                    Trình bày chuyên nghiệp, sử dụng bullet point rõ ràng.
                    """
                    try:
                        # Giả định ai_engine được lưu trong session_state hoặc truyền ngầm
                        if "ai_engine" in st.session_state:
                            khung_ke_hoach = st.session_state.ai_engine.generate_text(prompt)
                        else:
                            khung_ke_hoach = f"*(Demo - Chưa kết nối AI)*\n\n**KẾ HOẠCH TRIỂN KHAI CHUYÊN ĐỀ: {ten_chuyen_de.upper()}**\n\n- Nhóm: {nhom_cd}\n- Người phụ trách: {nguoi_bao_cao}\n\n[Nội dung chi tiết do AI sinh ra...]"
                        
                        st.session_state.ket_qua_chuyen_de = khung_ke_hoach
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
            else:
                st.warning("Thầy vui lòng nhập Tên chuyên đề hoặc Ý tưởng để AI có cơ sở lập kế hoạch nhé!")

    # 3. HIỂN THỊ VÀ TẢI KẾ HOẠCH
    if st.session_state.get("ket_qua_chuyen_de"):
        st.markdown("#### 📄 Khung Kế hoạch đề xuất")
        st.text_area("Chỉnh sửa Kế hoạch (nếu cần):", value=st.session_state.ket_qua_chuyen_de, height=400, key="edit_cd")
        
        st.download_button(
            label="⬇️ Tải Kế hoạch về máy (.txt)",
            data=st.session_state.ket_qua_chuyen_de,
            file_name="Ke_Hoach_Chuyen_De.txt",
            mime="text/plain",
            type="primary"
        )
