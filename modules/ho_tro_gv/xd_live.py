# ==========================================================
# MODULE: Trợ lý dạy học trực tuyến
# File: modules/ho_tro_gv/xd_live.py
# Version: 2.0
# ==========================================================

import streamlit as st
from datetime import datetime


# ==========================================================
# CSS
# ==========================================================

def load_css():
    st.markdown("""
    <style>

    .live-card{
        background:#ffffff;
        padding:16px;
        border-radius:12px;
        border:1px solid #E5E7EB;
        box-shadow:0 2px 8px rgba(0,0,0,0.05);
        margin-bottom:15px;
    }

    .live-title{
        font-size:28px;
        font-weight:bold;
        color:#D32F2F;
    }

    .live-sub{
        color:#555;
        font-size:15px;
    }

    .dashboard{
        background:#F8FAFC;
        border-radius:12px;
        padding:15px;
        border:1px solid #E2E8F0;
    }

    .section-title{
        font-size:20px;
        font-weight:700;
        color:#1565C0;
        margin-top:10px;
        margin-bottom:10px;
    }

    div.stButton > button{
        border-radius:10px;
        font-weight:600;
        height:44px;
    }

    textarea{
        border-radius:10px !important;
    }

    </style>
    """, unsafe_allow_html=True)


# ==========================================================
# KHỞI TẠO SESSION
# ==========================================================

def init_session():

    defaults = {

        "live_running": False,

        "live_question": "",

        "live_answer": "",

        "live_poll": "",

        "live_quiz": "",

        "live_example": "",

        "live_notes": "",

        "live_history": [],

        "live_ai_count": 0,

        "live_poll_count": 0,

        "live_quiz_count": 0,

        "live_start_time": None,

        "live_class_name": "",

        "live_subject": "",

        "live_lesson": "",

        "meet_link": "",

        "quizizz_link": "",

        "kahoot_link": "",

        "teams_link": "",

        "zoom_link": ""

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


# ==========================================================
# GHI NHẬT KÝ
# ==========================================================

def add_history(action):

    now = datetime.now().strftime("%H:%M:%S")

    st.session_state.live_history.append(

        f"[{now}] {action}"

    )


# ==========================================================
# ĐỊNH DẠNG THỜI GIAN
# ==========================================================

def get_duration():

    if st.session_state.live_start_time is None:

        return "00:00"

    delta = datetime.now() - st.session_state.live_start_time

    total = int(delta.total_seconds())

    minute = total // 60

    second = total % 60

    return f"{minute:02d}:{second:02d}"


# ==========================================================
# RESET PHIÊN LIVE
# ==========================================================

def reset_live():

    st.session_state.live_running = False

    st.session_state.live_question = ""

    st.session_state.live_answer = ""

    st.session_state.live_poll = ""

    st.session_state.live_quiz = ""

    st.session_state.live_example = ""

    st.session_state.live_notes = ""

    st.session_state.live_ai_count = 0

    st.session_state.live_poll_count = 0

    st.session_state.live_quiz_count = 0

    st.session_state.live_history = []

    st.session_state.live_start_time = None


# ==========================================================
# HEADER
# ==========================================================

def render_header():

    st.markdown(
        """
        <div class='live-card'>

        <div class='live-title'>
        🔴 TRỢ LÝ DẠY HỌC TRỰC TUYẾN
        </div>

        <div class='live-sub'>
        AI hỗ trợ giáo viên trong suốt quá trình giảng dạy trực tuyến.
        Trả lời nhanh • Sinh Poll • Sinh Quiz • Gợi ý ví dụ • Nhật ký tiết học.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================================
# DASHBOARD
# ==========================================================

def render_dashboard():

    st.markdown("<div class='section-title'>📊 Dashboard</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Trạng thái",
            "🟢 Đang dạy" if st.session_state.live_running else "⚪ Chưa bắt đầu"
        )

    with c2:
        st.metric(
            "Thời lượng",
            get_duration()
        )

    with c3:
        st.metric(
            "AI hỗ trợ",
            st.session_state.live_ai_count
        )

    with c4:
        st.metric(
            "Poll / Quiz",
            f"{st.session_state.live_poll_count} / {st.session_state.live_quiz_count}"
        )


# ==========================================================
# THÔNG TIN LỚP HỌC
# ==========================================================

def render_class_info():

    st.markdown("<div class='section-title'>🏫 Thông tin lớp học</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.session_state.live_class_name = st.text_input(
            "Lớp",
            value=st.session_state.live_class_name,
            placeholder="Ví dụ: 7A"
        )

    with col2:
        st.session_state.live_subject = st.text_input(
            "Môn học",
            value=st.session_state.live_subject,
            placeholder="Ví dụ: KHTN"
        )

    with col3:
        st.session_state.live_lesson = st.text_input(
            "Bài học",
            value=st.session_state.live_lesson,
            placeholder="Ví dụ: Định luật Newton"
        )


# ==========================================================
# LINK DẠY HỌC
# ==========================================================

def render_links():

    st.markdown("<div class='section-title'>🔗 Liên kết dạy học</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.session_state.meet_link = st.text_input(
            "Google Meet",
            value=st.session_state.meet_link,
            placeholder="https://meet.google.com/..."
        )

        st.session_state.zoom_link = st.text_input(
            "Zoom",
            value=st.session_state.zoom_link,
            placeholder="https://zoom.us/..."
        )

        st.session_state.teams_link = st.text_input(
            "Microsoft Teams",
            value=st.session_state.teams_link,
            placeholder="https://teams.microsoft.com/..."
        )

    with c2:

        st.session_state.quizizz_link = st.text_input(
            "Quizizz",
            value=st.session_state.quizizz_link,
            placeholder="https://quizizz.com/..."
        )

        st.session_state.kahoot_link = st.text_input(
            "Kahoot",
            value=st.session_state.kahoot_link,
            placeholder="https://kahoot.it/..."
        )


# ==========================================================
# NÚT MỞ LINK
# ==========================================================

def render_link_buttons():

    st.markdown("#### 🚀 Mở nhanh")

    cols = st.columns(5)

    with cols[0]:
        if st.session_state.meet_link:
            st.link_button(
                "Meet",
                st.session_state.meet_link,
                use_container_width=True
            )

    with cols[1]:
        if st.session_state.zoom_link:
            st.link_button(
                "Zoom",
                st.session_state.zoom_link,
                use_container_width=True
            )

    with cols[2]:
        if st.session_state.teams_link:
            st.link_button(
                "Teams",
                st.session_state.teams_link,
                use_container_width=True
            )

    with cols[3]:
        if st.session_state.quizizz_link:
            st.link_button(
                "Quizizz",
                st.session_state.quizizz_link,
                use_container_width=True
            )

    with cols[4]:
        if st.session_state.kahoot_link:
            st.link_button(
                "Kahoot",
                st.session_state.kahoot_link,
                use_container_width=True
            )


# ==========================================================
# ĐIỀU KHIỂN PHIÊN LIVE
# ==========================================================

def render_live_control():

    st.markdown("<div class='section-title'>🎥 Điều khiển phiên học</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        if not st.session_state.live_running:

            if st.button(
                "▶️ BẮT ĐẦU PHIÊN",
                type="primary",
                use_container_width=True
            ):

                st.session_state.live_running = True
                st.session_state.live_start_time = datetime.now()

                add_history("Bắt đầu phiên học")

                st.rerun()

    with c2:

        if st.session_state.live_running:

            if st.button(
                "⏹️ KẾT THÚC PHIÊN",
                use_container_width=True
            ):

                add_history("Kết thúc phiên học")

                reset_live()

                st.rerun()
# ==========================================================
# AI PHẢN XẠ NHANH
# ==========================================================

def render_ai_quick_answer(ai_engine):

    st.markdown(
        "<div class='section-title'>⚡ AI Phản xạ nhanh</div>",
        unsafe_allow_html=True
    )

    st.caption(
        "Học sinh đặt câu hỏi → AI gợi ý câu trả lời ngắn gọn để giáo viên phản hồi ngay."
    )

    question = st.text_area(
        "Câu hỏi của học sinh",
        value=st.session_state.live_question,
        height=120,
        placeholder="Ví dụ: Thầy ơi, tại sao bầu trời có màu xanh?"
    )

    st.session_state.live_question = question

    col1, col2 = st.columns([1,1])

    with col1:

        if st.button(
            "🤖 AI Trả lời",
            use_container_width=True,
            type="primary"
        ):

            if question.strip() == "":

                st.warning("Vui lòng nhập câu hỏi.")

            elif ai_engine is None:

                st.error("Chưa khởi tạo AI Engine.")

            else:

                prompt = f"""
Bạn là trợ lý AI hỗ trợ giáo viên THCS.

Học sinh hỏi:

{question}

Hãy trả lời:

- Ngắn gọn
- Dễ hiểu
- Khoảng 4 câu
- Có ví dụ thực tế nếu phù hợp
- Phù hợp học sinh THCS.
"""

                with st.spinner("AI đang suy nghĩ..."):

                    try:

                        answer = ai_engine.generate_text(prompt)

                        st.session_state.live_answer = answer

                        st.session_state.live_ai_count += 1

                        add_history(
                            "AI trả lời câu hỏi học sinh"
                        )

                    except Exception as e:

                        st.error(e)

    with col2:

        if st.button(
            "🗑 Xóa",
            use_container_width=True
        ):

            st.session_state.live_question = ""

            st.session_state.live_answer = ""

            st.rerun()

    if st.session_state.live_answer:

        st.success(st.session_state.live_answer)

# ==========================================================
# AI GIẢI THÍCH - VÍ DỤ THỰC TẾ
# ==========================================================

def render_ai_explain(ai_engine):

    st.markdown(
        "<div class='section-title'>💡 AI Giải thích & Ví dụ</div>",
        unsafe_allow_html=True
    )

    if st.session_state.live_question.strip() == "":

        st.info("💬 Hãy nhập câu hỏi của học sinh ở mục 'AI Phản xạ nhanh' trước.")

        return

    muc_do = st.selectbox(
        "Mức độ giải thích",
        [
            "Lớp 6",
            "Lớp 7",
            "Lớp 8",
            "Lớp 9"
        ],
        key="live_level"
    )

    col1, col2 = st.columns(2)

    # =====================================================
    # Giải thích lại
    # =====================================================

    with col1:

        if st.button(
            "📖 Giải thích lại",
            use_container_width=True
        ):

            if ai_engine is None:

                st.error("Chưa khởi tạo AI Engine.")

            else:

                prompt = f"""
Bạn là giáo viên THCS.

Học sinh hỏi:

{st.session_state.live_question}

Hãy giải thích lại cho học sinh {muc_do}.

Yêu cầu:

- Ngắn gọn.

- Dễ hiểu.

- Không quá 6 câu.

- Dùng ngôn ngữ gần gũi.

- Không dùng thuật ngữ khó.
"""

                with st.spinner("AI đang giải thích..."):

                    try:

                        result = ai_engine.generate_text(prompt)

                        st.session_state.live_example = result

                        st.session_state.live_ai_count += 1

                        add_history(
                            "AI giải thích lại kiến thức"
                        )

                    except Exception as e:

                        st.error(e)

    # =====================================================
    # Ví dụ thực tế
    # =====================================================

    with col2:

        if st.button(
            "🌍 Ví dụ thực tế",
            use_container_width=True
        ):

            if ai_engine is None:

                st.error("Chưa khởi tạo AI Engine.")

            else:

                prompt = f"""
Bạn là giáo viên THCS.

Từ câu hỏi:

{st.session_state.live_question}

Hãy đưa ra:

- 03 ví dụ thực tế.

- Gần gũi với học sinh.

- Có thể xảy ra trong cuộc sống.

- Không dài quá 8 dòng.
"""

                with st.spinner("AI đang tìm ví dụ..."):

                    try:

                        result = ai_engine.generate_text(prompt)

                        st.session_state.live_example = result

                        st.session_state.live_ai_count += 1

                        add_history(
                            "AI tạo ví dụ thực tế"
                        )

                    except Exception as e:

                        st.error(e)

    # =====================================================
    # Hiển thị kết quả
    # =====================================================

    if st.session_state.live_example:

        st.info(st.session_state.live_example)
# ==========================================================
# AI TẠO TƯƠNG TÁC
# ==========================================================

def render_ai_interaction(ai_engine):

    st.markdown(
        "<div class='section-title'>🎯 AI Tạo tương tác lớp học</div>",
        unsafe_allow_html=True
    )

    if st.session_state.live_question.strip() == "":

        st.info("💬 Hãy nhập câu hỏi hoặc nội dung bài học trước.")

        return

    interaction_type = st.selectbox(
        "Loại tương tác",
        [
            "Câu hỏi trắc nghiệm",
            "Câu hỏi Đúng/Sai",
            "Câu hỏi thảo luận"
        ],
        key="live_interaction_type"
    )

    if st.button(
        "✨ Tạo tương tác",
        type="primary",
        use_container_width=True
    ):

        if ai_engine is None:

            st.error("Chưa khởi tạo AI Engine.")

        else:

            prompt = f"""
Bạn là giáo viên THCS.

Nội dung đang dạy:

{st.session_state.live_question}

Hãy tạo:

{interaction_type}

Yêu cầu:

- Phù hợp học sinh THCS.
- Ngắn gọn.
- Hấp dẫn.
- Có đáp án.
- Có gợi ý giáo viên dẫn dắt học sinh.
"""

            with st.spinner("AI đang tạo nội dung..."):

                try:

                    result = ai_engine.generate_text(prompt)

                    st.session_state.live_poll = result

                    st.session_state.live_poll_count += 1

                    st.session_state.live_ai_count += 1

                    add_history(
                        f"AI tạo {interaction_type}"
                    )

                except Exception as e:

                    st.error(e)

    if st.session_state.live_poll:

        st.success(st.session_state.live_poll)
# ==========================================================
# GHI CHÚ TIẾT DẠY
# ==========================================================

def render_note():

    st.markdown(
        "<div class='section-title'>📝 Ghi chú nhanh</div>",
        unsafe_allow_html=True
    )

    st.session_state.live_notes = st.text_area(
        "Ghi chú của giáo viên",
        value=st.session_state.live_notes,
        height=120,
        placeholder="Ví dụ:\n- HS còn nhầm khái niệm...\n- Tiết sau ôn lại..."
    )


# ==========================================================
# NHẬT KÝ HOẠT ĐỘNG
# ==========================================================

def render_history():

    st.markdown(
        "<div class='section-title'>📜 Nhật ký phiên học</div>",
        unsafe_allow_html=True
    )

    if len(st.session_state.live_history) == 0:

        st.info("Chưa có hoạt động nào.")

        return

    for item in reversed(st.session_state.live_history):

        st.write("•", item)


# ==========================================================
# HÀM CHÍNH
# ==========================================================

def render_xd_live(ai_engine):

    load_css()

    init_session()

    render_header()

    render_dashboard()

    st.divider()

    render_class_info()

    render_links()

    render_link_buttons()

    st.divider()

    render_live_control()

    st.divider()

    render_ai_quick_answer(ai_engine)

    st.divider()

    render_ai_explain(ai_engine)

    st.divider()

    render_ai_interaction(ai_engine)

    st.divider()

    col1, col2 = st.columns([2,1])

    with col1:

        render_note()

    with col2:

        render_history()

    st.divider()

    st.caption(
        "🔴 Trợ lý dạy học trực tuyến - AI Teacher Assistant"
    )
