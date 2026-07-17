import time
import streamlit as st
import random
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
from datetime import datetime, timedelta
def load_css():

    st.markdown("""
    <style>

    /* Tổng thể */

    .live-header {

        background: linear-gradient(
            135deg,
            #1565C0,
            #42A5F5
        );

        padding:25px;

        border-radius:18px;

        color:white;

        margin-bottom:20px;

    }


    .live-header h1 {

        font-size:32px;

        margin-bottom:5px;

    }


    .live-header p {

        font-size:16px;

        opacity:0.9;

    }



    /* Card */

    .live-card {

        background:white;

        padding:18px;

        border-radius:15px;

        border:1px solid #E5E7EB;

        box-shadow:
        0 4px 12px rgba(0,0,0,0.08);

        margin-bottom:15px;

    }



    /* Dashboard */

    .metric-card {

        padding:15px;

        border-radius:12px;

        background:#F8FAFC;

        border:1px solid #CBD5E1;

        text-align:center;

    }


    .metric-title {

        font-size:14px;

        color:#64748B;

    }


    .metric-value {

        font-size:25px;

        font-weight:bold;

        color:#1565C0;

    }



    /* Section */

    .section-title {

        font-size:21px;

        font-weight:700;

        color:#1565C0;

        margin-top:15px;

        margin-bottom:10px;

    }



    /* Button */

    div.stButton > button {

        border-radius:12px;

        height:45px;

        font-weight:600;

    }


    </style>
    """,
    unsafe_allow_html=True
    )
"lesson_duration":45,

"custom_duration":45,

"timer_running":False,

"timer_end":None,

"timer_start":None,

"timer_warning":""

def render_timer_setting():

    st.markdown(
        "<div class='section-title'>⏱ Cấu hình thời gian tiết học</div>",
        unsafe_allow_html=True
    )


    options = {

        "35 phút":35,

        "45 phút":45,

        "50 phút":50,

        "90 phút":90,

        "Tùy chỉnh":0

    }


    choice = st.selectbox(

        "Chọn thời lượng:",

        list(options.keys())

    )


    if choice == "Tùy chỉnh":

        duration = st.number_input(

            "Nhập số phút:",

            min_value=5,

            max_value=180,

            value=45

        )

        st.session_state.lesson_duration = duration


    else:

        st.session_state.lesson_duration = options[choice]


    st.info(
        f"⏰ Thời lượng đã chọn: "
        f"{st.session_state.lesson_duration} phút"
    )

# ==========================================================
# KHỞI TẠO TIMER LIVE
# ==========================================================

def start_live_timer():

    duration = st.session_state.lesson_duration

    st.session_state.timer_start = datetime.now()

    st.session_state.timer_end = (
        datetime.now()
        +
        timedelta(minutes=duration)
    )

    st.session_state.timer_running = True

    add_history(
        f"Bắt đầu tiết học ({duration} phút)"
    )
# ==========================================================
# TÍNH THỜI GIAN CÒN LẠI
# ==========================================================

def calculate_remaining_time():

    if not st.session_state.timer_running:

        return 0, "00:00"


    now = datetime.now()


    remaining = (
        st.session_state.timer_end
        -
        now
    )


    seconds = int(
        remaining.total_seconds()
    )


    if seconds <= 0:

        return 0, "00:00"


    minutes = seconds // 60

    sec = seconds % 60


    return seconds, f"{minutes:02d}:{sec:02d}"

# ==========================================================
# HIỂN THỊ TIMER
# ==========================================================

def render_live_timer():

    st.markdown(
        "<div class='section-title'>⏱ Tiến trình tiết học</div>",
        unsafe_allow_html=True
    )


    total_seconds = (
        st.session_state.lesson_duration
        *
        60
    )


    remaining_seconds, display = (
        calculate_remaining_time()
    )


    if total_seconds > 0:

        elapsed = (
            total_seconds
            -
            remaining_seconds
        )


        progress = (
            elapsed
            /
            total_seconds
        )


        if progress > 1:

            progress = 1


    else:

        progress = 0



    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(

            "⏳ Đã dạy",

            f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"

        )


    with col2:

        st.metric(

            "⌛ Còn lại",

            display

        )


    with col3:

        if remaining_seconds <= 300 and remaining_seconds > 0:

            st.warning(
                "⚠️ Còn dưới 5 phút"
            )

        elif remaining_seconds <= 600:

            st.info(
                "🔔 Còn dưới 10 phút"
            )

        else:

            st.success(
                "🟢 Đang trong tiết học"
            )


    st.progress(progress)



    if remaining_seconds == 0 and st.session_state.timer_running:

        st.error(
            "🔴 Đã hết thời gian tiết học!"
        )


        add_history(
            "Hết thời gian tiết học"
        )


        st.session_state.timer_running = False

# ==========================================================
# ĐIỀU KHIỂN PHIÊN LIVE (V2 - CÓ TIMER)
# ==========================================================

def render_live_control():

    st.markdown(
        "<div class='section-title'>🎥 Điều khiển phiên học</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)


    # ------------------------------------------------------
    # BẮT ĐẦU PHIÊN
    # ------------------------------------------------------

    with col1:

        if not st.session_state.live_running:

            if st.button(
                "▶️ BẮT ĐẦU PHIÊN",
                type="primary",
                use_container_width=True
            ):

                # Trạng thái phiên học
                st.session_state.live_running = True


                # Thời gian cũ của phiên
                st.session_state.live_start_time = datetime.now()


                # Khởi động bộ đếm mới
                start_live_timer()


                add_history(
                    "Bắt đầu phiên dạy trực tuyến"
                )


                st.rerun()



    # ------------------------------------------------------
    # KẾT THÚC PHIÊN
    # ------------------------------------------------------

    with col2:

        if st.session_state.live_running:

            if st.button(
                "⏹️ KẾT THÚC PHIÊN",
                type="secondary",
                use_container_width=True
            ):

                add_history(
                    "Kết thúc phiên dạy trực tuyến"
                )


                # Dừng timer

                st.session_state.timer_running = False


                # Xóa trạng thái phiên

                st.session_state.live_running = False


                st.session_state.timer_start = None

                st.session_state.timer_end = None


                st.rerun()

# ==========================================================
# CAMERA LIVE PROCESSOR
# ==========================================================

class VideoProcessor(VideoProcessorBase):

    def recv(self, frame):

        img = frame.to_ndarray(
            format="bgr24"
        )

        return av.VideoFrame.from_ndarray(
            img,
            format="bgr24"
        )
# ==========================================================
# CAMERA LIVE
# ==========================================================

def render_camera_live():

    st.markdown(
        "<div class='section-title'>📷 Camera trực tiếp</div>",
        unsafe_allow_html=True
    )


    st.caption(
        "Camera giáo viên / camera thí nghiệm"
    )


    webrtc_streamer(

        key="teacher-camera",

        video_processor_factory=VideoProcessor,

        media_stream_constraints={

            "video": True,

            "audio": False

        },

        async_processing=True

    )

def render_xd_live(ai_engine):

    load_css()

    init_session()

    render_header()

    render_dashboard()

def init_session():

"live_ai_quiz":"",
"live_exit_ticket":"",
"live_activity":"",
"live_quick_check":""

# ==========================================================
# AI MINI QUIZ LIVE
# ==========================================================

def render_ai_mini_quiz(ai_engine):

    st.markdown(
        "<div class='section-title'>🎯 AI Mini Quiz Live</div>",
        unsafe_allow_html=True
    )


    content = st.text_area(
        "Nội dung đang giảng:",
        placeholder="Ví dụ: Định luật phản xạ ánh sáng..."
    )


    col1, col2 = st.columns(2)


    with col1:

        number = st.selectbox(
            "Số câu:",
            [1,3,5]
        )


    with col2:

        level = st.selectbox(
            "Mức độ:",
            [
                "Nhận biết",
                "Thông hiểu",
                "Vận dụng"
            ]
        )


    if st.button(
        "✨ Sinh Quiz",
        use_container_width=True
    ):


        if not content.strip():

            st.warning(
                "Nhập nội dung bài học."
            )

        elif ai_engine is None:

            st.error(
                "AI chưa sẵn sàng."
            )

        else:


            prompt=f"""

Bạn là giáo viên THCS.

Tạo {number} câu hỏi trắc nghiệm.

Chủ đề:

{content}


Mức độ:

{level}


Yêu cầu:

- Có 4 phương án A,B,C,D.
- Có đáp án.
- Có giải thích ngắn.

"""


            with st.spinner(
                "AI đang tạo câu hỏi..."
            ):

                result = ai_engine.generate_text(
                    prompt
                )

                st.session_state.live_ai_quiz = result


    if st.session_state.live_ai_quiz:

        st.success(
            st.session_state.live_ai_quiz
        )
# ==========================================================
# AI EXIT TICKET
# ==========================================================

def render_exit_ticket(ai_engine):

    st.markdown(
        "<div class='section-title'>📝 Exit Ticket cuối giờ</div>",
        unsafe_allow_html=True
    )


    lesson = st.text_input(
        "Tên bài học:",
        placeholder="Ví dụ: Nam châm điện"
    )


    if st.button(
        "Tạo Exit Ticket"
    ):


        prompt=f"""

Bạn là giáo viên THCS.

Tạo Exit Ticket cho bài:

{lesson}


Gồm:

1. Điều em hiểu nhất?
2. Một điều còn chưa rõ?
3. Một câu hỏi vận dụng thực tế?

Ngôn ngữ phù hợp học sinh THCS.

"""


        with st.spinner(
            "Đang tạo..."
        ):

            result = ai_engine.generate_text(
                prompt
            )

            st.session_state.live_exit_ticket = result



    if st.session_state.live_exit_ticket:

        st.info(
            st.session_state.live_exit_ticket
        )
# ==========================================================
# AI GỢI Ý HOẠT ĐỘNG
# ==========================================================

def render_ai_activity(ai_engine):

    st.markdown(
        "<div class='section-title'>💡 AI gợi ý hoạt động</div>",
        unsafe_allow_html=True
    )


    situation = st.text_area(
        "Tình trạng lớp:",
        placeholder=
        "Ví dụ: Học sinh mất tập trung sau 20 phút"
    )


    if st.button(
        "AI đề xuất"
    ):


        prompt=f"""

Bạn là chuyên gia phương pháp dạy học.

Tình trạng lớp:

{situation}


Hãy đề xuất:

- Một hoạt động kéo dài 3-5 phút.
- Cách tổ chức.
- Mục tiêu.
- Cách đánh giá nhanh.

"""


        with st.spinner(
            "AI đang phân tích..."
        ):


            result = ai_engine.generate_text(
                prompt
            )


            st.session_state.live_activity=result



    if st.session_state.live_activity:

        st.success(
            st.session_state.live_activity
        )

render_ai_mini_quiz(ai_engine)

render_exit_ticket(ai_engine)

render_ai_activity(ai_engine)
"student_list": [],
"selected_student": "",
"group_timer_seconds": 0,
"group_timer_running": False,
"quick_scores": {},
# ==========================================================
# RANDOM HỌC SINH
# ==========================================================

def render_student_picker():

    st.markdown(
        "<div class='section-title'>🎲 Vòng quay học sinh</div>",
        unsafe_allow_html=True
    )

    students = st.text_area(
        "Danh sách học sinh (mỗi dòng một tên):",
        height=120
    )


    if students.strip():

        st.session_state.student_list = [
            x.strip()
            for x in students.split("\n")
            if x.strip()
        ]


    if st.button(
        "🎯 Chọn ngẫu nhiên",
        use_container_width=True
    ):

        if st.session_state.student_list:

            st.session_state.selected_student = random.choice(
                st.session_state.student_list
            )

        else:

            st.warning(
                "Chưa có danh sách học sinh"
            )


    if st.session_state.selected_student:

        st.success(
            f"👤 Học sinh được chọn: {st.session_state.selected_student}"
        )

# ==========================================================
# GROUP TIMER
# ==========================================================

def render_group_timer():

    st.markdown(
        "<div class='section-title'>⏱ Đồng hồ hoạt động nhóm</div>",
        unsafe_allow_html=True
    )


    minutes = st.number_input(
        "Thời gian (phút)",
        min_value=1,
        max_value=60,
        value=5
    )


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "▶️ Bắt đầu nhóm",
            use_container_width=True
        ):

            st.session_state.group_timer_seconds = minutes * 60

            st.session_state.group_timer_running = True



    with col2:

        if st.button(
            "⏹ Dừng",
            use_container_width=True
        ):

            st.session_state.group_timer_running = False



    if st.session_state.group_timer_running:

        sec = st.session_state.group_timer_seconds


        st.metric(
            "Còn lại",
            f"{sec//60:02d}:{sec%60:02d}"
        )


        if sec > 0:

            time.sleep(1)

            st.session_state.group_timer_seconds -= 1

            st.rerun()

        else:

            st.warning(
                "⏰ Hết thời gian hoạt động!"
            )

            st.session_state.group_timer_running = False

# ==========================================================
# QUICK SCORE
# ==========================================================

def render_quick_score():

    st.markdown(
        "<div class='section-title'>📊 Bảng điểm nhanh</div>",
        unsafe_allow_html=True
    )


    name = st.text_input(
        "Tên học sinh"
    )


    score = st.number_input(
        "Điểm",
        min_value=0.0,
        max_value=10.0,
        step=0.5
    )


    if st.button(
        "➕ Lưu điểm"
    ):

        if name:

            st.session_state.quick_scores[name] = score



    if st.session_state.quick_scores:

        st.write(
            st.session_state.quick_scores
        )
render_student_picker()

render_group_timer()

render_quick_score()

# ==========================================================
# HEADER V2
# ==========================================================

def render_header():

    st.markdown(
        """
        <div class="live-header">

        <h1>
        🔴 Trợ lý Dạy học Trực tuyến AI
        </h1>

        <p>
        AI Teacher Assistant - THCS Nguyễn Chí Thanh
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================================
# DASHBOARD V2
# ==========================================================

def render_dashboard():

    st.markdown(
        "<div class='section-title'>📊 Dashboard Live</div>",
        unsafe_allow_html=True
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.markdown(
            f"""
            <div class="metric-card">

            <div class="metric-title">
            Trạng thái
            </div>

            <div class="metric-value">
            {"🟢 LIVE" if st.session_state.live_running else "⚪ OFF"}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="metric-card">

            <div class="metric-title">
            Thời lượng
            </div>

            <div class="metric-value">
            {st.session_state.lesson_duration} phút
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            f"""
            <div class="metric-card">

            <div class="metric-title">
            AI hỗ trợ
            </div>

            <div class="metric-value">
            {st.session_state.live_ai_count}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col4:

        st.markdown(
            f"""
            <div class="metric-card">

            <div class="metric-title">
            Tương tác
            </div>

            <div class="metric-value">
            {st.session_state.live_poll_count}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

def render_xd_live(ai_engine):

    load_css()

    init_session()

    render_header()


    # Dashboard

    render_dashboard()


    st.divider()


    # Thông tin lớp

    col1, col2 = st.columns(
        [1,1]
    )


    with col1:

        render_class_info()

        render_links()


    with col2:

        render_camera_live()



    st.divider()


    # Timer

    render_timer_setting()

    render_live_control()

    render_live_timer()



    st.divider()



    # AI

    render_ai_quick_answer(ai_engine)

    render_ai_explain(ai_engine)

    render_ai_interaction(ai_engine)

    render_ai_mini_quiz(ai_engine)

    render_exit_ticket(ai_engine)

    render_ai_activity(ai_engine)



    st.divider()



    # Công cụ lớp học

    render_student_picker()

    render_group_timer()

    render_quick_score()



    st.divider()



    # Ghi chú

    col3, col4 = st.columns(
        [2,1]
    )


    with col3:

        render_note()


    with col4:

        render_history()



    st.caption(
        "🔴 AI Teacher Assistant - Live Classroom Control Center"
    )

from modules.ho_tro_gv.xd_live import render_xd_live
