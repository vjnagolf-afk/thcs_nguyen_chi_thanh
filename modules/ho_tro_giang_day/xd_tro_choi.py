import streamlit as st
import streamlit.components.v1 as components

def render_xd_tro_choi(ai_engine):
    st.markdown("### 🎮 Cổng Trò chơi Giáo dục Tương tác")
    st.caption("Kho lưu trữ các trò chơi và phòng thí nghiệm ảo do các thầy cô tâm huyết xây dựng, giúp khởi động tiết học và củng cố kiến thức sinh động.")

    # 1. Danh mục trò chơi đã được phân loại và lọc trùng lặp
    danh_muc_game = {
        "Toán học": {
            "Trò chơi Toán cô Vân (Hàm số)": "https://trochoitoancovanhsmu.netlify.app/",
            "Trò chơi Toán cô Vân (Đạo hàm)": "https://trochoitoancovandaoham1.netlify.app/",
            "Trò chơi Toán CLB Toán 22": "https://trochoicovanclbtoan22.netlify.app/",
            "Math 2 Word": "https://math-2-word.vercel.app/"
        },
        "Ngữ văn": {
            "Đấu trường Văn học": "https://dautruongvanhoc.netlify.app/"
        },
        "Tiếng Anh": {
            "English Grammar Arena": "https://englishgrammararena.netlify.app/"
        },
        "Vật lý / KHTN": {
            "Thử tài Vật lý": "https://thutaivatly.netlify.app/",
            "Thí nghiệm Vật lý": "http://thinghiemvatly.studyai.id.vn/"
        },
        "Tin học / Trò chơi chung": {
            "Lập trình cô Đức": "https://laptrinhcoduc.netlify.app/",
            "Game cô Thi Thi": "https://gamecothithi.netlify.app/",
            "Game Thuận 1B": "https://gamethuan1b.netlify.app/",
            "Mối liên hệ UI (Vy Thi)": "https://vythiviethals.github.io/moi_lien_he_UI/",
            "Game Bích Phương": "https://gamebbichphuong1.netlify.app/",
            "Game Nghiêng đầu": "https://gamenghiengdau.netlify.app/",
            "Trò chơi 01": "https://trochoi01.netlify.app/"
        }
    }

    # 2. Giao diện chọn trò chơi
    col1, col2 = st.columns([1, 2])
    with col1:
        nhom_mon = st.selectbox("📚 Chọn nhóm môn / chủ đề:", list(danh_muc_game.keys()))
    with col2:
        ten_game = st.selectbox("🎯 Chọn trò chơi:", list(danh_muc_game[nhom_mon].keys()))
    
    url_game_dang_chon = danh_muc_game[nhom_mon][ten_game]

    st.markdown("---")

    # 3. Trợ lý AI Gợi ý tổ chức (Tích hợp AI Engine)
    with st.expander("🤖 Gợi ý cách tổ chức trò chơi này từ AI", expanded=False):
        muc_dich = st.radio("Thầy muốn dùng trò chơi này để làm gì?", ["Khởi động vào bài", "Kiểm tra bài cũ", "Củng cố cuối giờ"], horizontal=True)
        if st.button("Tạo kịch bản tổ chức", type="secondary"):
            with st.spinner("AI đang soạn kịch bản..."):
                prompt = f"Tôi sắp cho học sinh THCS chơi trò '{ten_game}' (Link: {url_game_dang_chon}) trong mục đích '{muc_dich}'. Hãy gợi ý cho tôi một kịch bản tổ chức lớp học thật nhanh gọn, hấp dẫn, có cách chia đội và thưởng điểm."
                try:
                    kich_ban = ai_engine.generate_text(prompt)
                    st.success("Kịch bản đề xuất:")
                    st.write(kich_ban)
                except Exception as e:
                    st.error(f"Lỗi kết nối AI: {e}")

    # 4. Khu vực hiển thị Game (Iframe)
    col_btn1, col_btn2 = st.columns([4, 1])
    with col_btn1:
        st.markdown(f"**Đang hiển thị:** `{ten_game}`")
    with col_btn2:
        # Nút dự phòng trường hợp web gốc chặn iframe hoặc thầy muốn mở to ra
        st.link_button("Mở to ở Tab mới 🌐", url=url_game_dang_chon, use_container_width=True)

    st.markdown(
        """
        <style>
        .game-container {
            border: 2px solid #e6e6e6;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    st.markdown('<div class="game-container">', unsafe_allow_html=True)
    # Nhúng game vào màn hình (chiều cao 650px)
    components.iframe(url_game_dang_chon, width=None, height=650, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)
