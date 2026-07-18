import streamlit as st

def render_sach_kn_so():
    # --- KHỞI TẠO BỘ NHỚ TẠM ---
    # 1. Biến theo dõi xem thầy đang mở chuyên mục nào (Mặc định là None - Tức là đang ở màn hình chính)
    if "chuyen_muc_dang_mo" not in st.session_state:
        st.session_state.chuyen_muc_dang_mo = None

    # 2. Kho dữ liệu video (Thầy dán link vào đây, nó sẽ lưu tạm. Về sau có thể kết nối CSDL thật)
    if "kho_video" not in st.session_state:
        st.session_state.kho_video = {
            "AI": ["https://www.youtube.com/watch?v=yW6K2ZtO-X4"], # Link ví dụ
            "TuongTac": [],
            "QuanTri": []
        }

    st.markdown("### 📘 Tủ sách Kỹ năng số cho Giáo viên")
    st.caption("Kho tài liệu, cẩm nang hướng dẫn ứng dụng công nghệ thông tin và AI vào công tác giảng dạy.")

    # ==========================================
    # MÀN HÌNH 1: DANH MỤC CHÍNH (Hiển thị khi chưa chọn mục nào)
    # ==========================================
    if st.session_state.chuyen_muc_dang_mo is None:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🤖 Cẩm nang AI")
            st.info("""
            - Hướng dẫn cơ bản sử dụng ChatGPT
            - Kỹ năng viết Prompt sư phạm
            - Ứng dụng Gemini trong soạn giảng
            """)
            if st.button("📖 Vào lớp học AI", key="doc_ai", type="primary", use_container_width=True):
                st.session_state.chuyen_muc_dang_mo = "AI"
                st.rerun()
            
        with col2:
            st.markdown("#### 🖥️ Công cụ Tương tác")
            st.success("""
            - Hướng dẫn tạo Quizizz / Kahoot
            - Tổ chức lớp học với Padlet
            - Sử dụng phòng thí nghiệm ảo (PhET)
            """)
            if st.button("📖 Vào lớp Tương tác", key="doc_tt", type="primary", use_container_width=True):
                st.session_state.chuyen_muc_dang_mo = "TuongTac"
                st.rerun()
            
        with col3:
            st.markdown("#### 📊 Quản trị Lớp học")
            st.warning("""
            - Quản lý điểm số nâng cao với Excel
            - Xây dựng hồ sơ số, Google Classroom
            - Bảo mật thông tin học sinh
            """)
            if st.button("📖 Vào lớp Quản trị", key="doc_ql", type="primary", use_container_width=True):
                st.session_state.chuyen_muc_dang_mo = "QuanTri"
                st.rerun()
            
        st.markdown("---")
        st.markdown("#### 🔍 Tìm kiếm tài liệu khác")
        tim_kiem = st.text_input("Nhập từ khóa tài liệu bạn muốn tìm (VD: Canva, PowerPoint...):")
        if tim_kiem:
            st.write(f"Đang tìm kiếm tài liệu liên quan đến: **{tim_kiem}**... (Tính năng kết nối kho lưu trữ đang hoàn thiện)")

    # ==========================================
    # MÀN HÌNH 2: BÊN TRONG LỚP HỌC (Hiển thị Video và Form)
    # ==========================================
    else:
        # Nút Quay lại
        if st.button("⬅️ Quay lại Danh mục", type="secondary"):
            st.session_state.chuyen_muc_dang_mo = None
            st.rerun()
            
        st.markdown("---")
        
        # Lấy ID chuyên mục đang mở
        cm = st.session_state.chuyen_muc_dang_mo
        
        # Đặt Tiêu đề tương ứng
        if cm == "AI": st.markdown("#### 🤖 Kho Video: Cẩm nang ứng dụng AI")
        elif cm == "TuongTac": st.markdown("#### 🖥️ Kho Video: Công cụ Tương tác lớp học")
        elif cm == "QuanTri": st.markdown("#### 📊 Kho Video: Quản trị Lớp học & Hồ sơ số")

        # 1. KHU VỰC HIỂN THỊ VIDEO
        if len(st.session_state.kho_video[cm]) == 0:
            st.info("💡 Chuyên mục này hiện chưa có video nào. Thầy hãy dùng form bên dưới để thêm mới nhé!")
        else:
            # Hiển thị từng video có trong danh sách
            for idx, link_video in enumerate(st.session_state.kho_video[cm]):
                st.markdown(f"**Bài học {idx + 1}:**")
                try:
                    st.video(link_video) # Streamlit tự động nhận diện và nhúng link YouTube/MP4
                except:
                    st.error(f"Không thể tải video từ link: {link_video}")
                st.markdown("<br>", unsafe_allow_html=True) # Tạo khoảng cách

        # 2. KHU VỰC NHÚNG THÊM VIDEO MỚI (FORM)
        st.markdown("---")
        with st.expander("➕ Dành cho Quản trị viên: Thêm bài giảng Video mới", expanded=True):
            with st.form("form_nhung_video", clear_on_submit=True):
                st.caption("Dán đường link YouTube của bài giảng vào đây để đưa lên hệ thống.")
                link_moi = st.text_input("🔗 Nhập link YouTube (Ví dụ: https://www.youtube.com/watch?v=...):")
                
                submitted = st.form_submit_button("Lưu Video", type="primary")
                if submitted:
                    if link_moi.strip():
                        # Thêm link mới vào kho dữ liệu của chuyên mục hiện tại
                        st.session_state.kho_video[cm].append(link_moi.strip())
                        st.success("✅ Đã thêm video thành công!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Thầy chưa nhập link video!")
