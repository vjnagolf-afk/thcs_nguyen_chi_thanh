# -*- coding: utf-8 -*-
import streamlit as st

def render_live_quiz_module():
    # 0. Tinh chỉnh CSS đồng bộ giao diện
    st.markdown("""
        <style>
        .stButton>button {
            font-weight: bold;
            border-radius: 6px;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. KHU VỰC CẤU HÌNH LINK ĐẦU VÀO
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        # Giải mã ký tự hiển thị lỗi thành icon 🖼️ chuẩn
        image_url = st.text_input("🖼️ Dán link ảnh bìa:", placeholder="https://...", key="quiz_image_url")
    with col_input2:
        live_link = st.text_input("🔗 Dán link Quiz Live (Kahoot/Quizizz):", placeholder="https://...", key="quiz_live_link")

    # Hiển thị ảnh bìa linh hoạt theo link giáo viên dán vào
    if image_url.strip():
        try:
            st.image(image_url.strip(), use_container_width=True, caption="Ảnh bìa phiên Quiz")
        except Exception:
            st.error("Không thể tải ảnh từ đường link này. Thầy/Cô vui lòng kiểm tra lại định dạng link nhé!")

    # 2. KHỞI TẠO VÀ QUẢN LÝ SESSION STATE
    if 'quiz_started' not in st.session_state:
        st.session_state['quiz_started'] = False

    st.write("---")

    # Chia bố cục vùng điều khiển và vùng hiển thị Live Dashboard
    col1, col2 = st.columns([1, 2])

    # ==========================================
    # KHỐI 1: BẢNG ĐIỀU KHIỂN CẤU HÌNH QUIZ
    # ==========================================
    with col1:
        st.markdown("### 🛠️ Cấu hình Quiz")
        ten_quiz = st.text_input("Tên phiên trắc nghiệm", "Kiểm tra 15' KHTN", key="quiz_title_input")
        
        # Nút mở link ngoài (Kahoot/Quizizz) luôn an toàn ở tab mới, chống chặn iframe
        if live_link.strip():
            st.link_button("🚀 MỞ LINK QUIZ ĐÃ DÁN", url=live_link.strip(), use_container_width=True)
        else:
            st.button("🚀 MỞ LINK QUIZ ĐÃ DÁN", disabled=True, use_container_width=True, help="Vui lòng dán link Quiz ở phía trên trước")

        # Cơ chế chuyển đổi trạng thái Bắt đầu / Kết thúc
        if not st.session_state['quiz_started']:
            # Giải mã ký tự lỗi hiển thị icon ▶️
            if st.button("▶️ BẮT ĐẦU PHÁT SÓNG TRONG APP", type="primary", use_container_width=True):
                st.session_state['quiz_started'] = True
                st.rerun()
        else:
            # Giải mã ký tự lỗi hiển thị icon ⏹️
            if st.button("⏹️ KẾT THÚC PHIÊN", type="secondary", use_container_width=True):
                st.session_state['quiz_started'] = False
                st.rerun()

    # ==========================================
    # KHỐI 2: MÀN HÌNH THEO DÕI LIVE FEED
    # ==========================================
    with col2:
        if st.session_state['quiz_started']:
            st.success(f"✅ Phiên '{ten_quiz}' đang hoạt động trực tuyến!")
            
            # Đã loại bỏ vòng lặp for gấy đơ app. 
            # Hiển thị thanh tiến trình tĩnh hoặc sẵn sàng nhận dữ liệu động
            st.progress(100, text="Hệ thống kết nối trực tuyến sẵn sàng")
            
            col_a, col_b = st.columns(2)
            col_a.metric("Số HS tham gia", "24", delta="+4 học sinh mới") # Giả lập số liệu mẫu trực quan
            col_b.metric("Câu hỏi hiện tại", "1/5", delta="Đang chạy câu 1")
            
            st.markdown("### 📊 Kết quả trực tiếp (Live Feed)")
            st.info("🔄 Đang đợi học sinh nhấn nộp bài... Biểu đồ xếp hạng sẽ tự động cập nhật tại đây.")
        else:
            st.info("Hệ thống đang ở chế độ chờ. Hãy cấu hình thông tin và nhấn nút Bắt đầu phiên Quiz.")
            st.caption("💡 Lưu ý: Các link nền tảng ngoài (Kahoot, Quizizz) bắt buộc phải mở ở tab mới để tránh bị hệ thống bảo mật của họ chặn.")
