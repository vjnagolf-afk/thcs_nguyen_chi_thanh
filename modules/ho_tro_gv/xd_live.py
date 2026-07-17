import time
import random
import av
from datetime import datetime, timedelta
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# ==========================================================
# CẤU HÌNH GIAO DIỆN (CSS TÙY CHỈNH)
# ==========================================================
def load_css():
    st.markdown("""
    <style>
    /* Tổng thể */
    .live-header {
        background: linear-gradient(135deg, #1565C0, #42A5F5);
        padding: 25px;
        border-radius: 18px;
        color: white;
        margin-bottom: 20px;
    }
    .live-header h1 {
        font-size: 32px;
        margin-bottom: 5px;
    }
    .live-header p {
        font-size: 16px;
        opacity: 0.9;
    }
    /* Card thông tin */
    .live-card {
        background: white;
        padding: 18px;
        border-radius: 15px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }
    /* Dashboard thẻ chỉ số */
    .metric-card {
        padding: 15px;
        border-radius: 12px;
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        text-align: center;
    }
    .metric-title {
        font-size: 14px;
        color: #64748B;
    }
    .metric-value {
        font-size: 25px;
        font-weight: bold;
        color: #1565C0;
    }
    /* Tiêu đề phân đoạn */
    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #1565C0;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    /* Nút bấm mặc định */
    div.stButton > button {
        border-radius: 12px;
        height: 45px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================================
# ĐỊNH NGHĨA HEADER & DASHBOARD
# ==========================================================
def render_header():
    st.markdown("""
    <div class="live-header">
        <h1>Trợ lý Dạy học Trực tuyến AI</h1>
        <p>AI Teacher Assistant - THCS Nguyễn Chí Thanh</p>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard():
    st.markdown("<div class='section-title'>📊 Dashboard Live</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_text = "LIVE" if st.session_state.get("live_running", False) else "OFF"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Trạng thái</div>
            <div class="metric-value">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        duration = st.session_state.get("lesson_duration", 45)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Thời lượng</div>
            <div class="metric-value">{duration} phút</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        ai_count = st.session_state.get("live_ai_count", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">AI hỗ trợ</div>
            <div class="metric-value">{ai_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        poll_count = st.session_state.get("live_poll_count", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Tương tác</div>
            <div class="metric-value">{poll_count}</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# XỬ LÝ CAMERA TRỰC TIẾP
# ==========================================================
class VideoProcessor(VideoProcessorBase):
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def render_camera_live():
    st.markdown("<div class='section-title'>📹 Camera trực tiếp</div>", unsafe_allow_html=True)
    st.caption("Camera giáo viên / camera thí nghiệm")
    webrtc_streamer(
        key="teacher-camera",
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )
# ==========================================================
# HỆ THỐNG QUẢN LÝ THỜI GIAN (TIMER)
# ==========================================================
def render_timer_setting():
    st.markdown("<div class='section-title'>⏱ Cấu hình thời gian tiết học</div>", unsafe_allow_html=True)
    options = {"35 phút": 35, "45 phút": 45, "50 phút": 50, "90 phút": 90, "Tùy chỉnh": 0}
    choice = st.selectbox("Chọn thời lượng:", list(options.keys()))
    
    if choice == "Tùy chỉnh":
        duration = st.number_input("Nhập số phút:", min_value=5, max_value=180, value=45)
    else:
        duration = options[choice]
        
    st.session_state.lesson_duration = duration
    st.info(f"⏱ Thời lượng đã chọn: {st.session_state.lesson_duration} phút")

def start_live_timer():
    duration = st.session_state.lesson_duration
    st.session_state.timer_start = datetime.now()
    st.session_state.timer_end = datetime.now() + timedelta(minutes=duration)
    st.session_state.timer_running = True
    if "add_history" in globals():
        add_history(f"Bắt đầu tiết học ({duration} phút)")

def calculate_remaining_time():
    if not st.session_state.get("timer_running", False):
        return 0, "00:00"
    now = datetime.now()
    remaining = st.session_state.timer_end - now
    seconds = int(remaining.total_seconds())
    if seconds <= 0:
        return 0, "00:00"
    minutes = seconds // 60
    sec = seconds % 60
    return seconds, f"{minutes:02d}:{sec:02d}"

def render_live_timer():
    st.markdown("<div class='section-title'>⏱ Tiến trình tiết học</div>", unsafe_allow_html=True)
    total_seconds = st.session_state.get("lesson_duration", 45) * 60
    remaining_seconds, display = calculate_remaining_time()
    
    if total_seconds > 0:
        elapsed = total_seconds - remaining_seconds
        progress = elapsed / total_seconds
        progress = min(max(progress, 0.0), 1.0)
    else:
        elapsed = 0
        progress = 0.0
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏳ Đã dạy", f"{int(elapsed//60):02d}:{int(elapsed%60):02d}")
    with col2:
        st.metric("⏳ Còn lại", display)
    with col3:
        if 0 < remaining_seconds <= 300:
            st.warning("⚠️ Còn dưới 5 phút")
        elif remaining_seconds <= 600 and remaining_seconds > 0:
            st.info("ℹ️ Còn dưới 10 phút")
        else:
            st.success("✅ Đang trong tiết học")
            
    st.progress(progress)
    
    if remaining_seconds == 0 and st.session_state.get("timer_running", False):
        st.error("🚨 Đã hết thời gian tiết học!")
        if "add_history" in globals():
            add_history("Hết thời gian tiết học")
        st.session_state.timer_running = False

def render_live_control():
    st.markdown("<div class='section-title'>🎮 Điều khiển phiên học</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.get("live_running", False):
            if st.button("▶️ BẮT ĐẦU PHIÊN", type="primary", use_container_width=True):
                st.session_state.live_running = True
                st.session_state.live_start_time = datetime.now()
                start_live_timer()
                if "add_history" in globals():
                    add_history("Bắt đầu phiên dạy trực tuyến")
                st.rerun()
                
    with col2:
        if st.session_state.get("live_running", False):
            if st.button("⏹ KẾT THÚC PHIÊN", type="secondary", use_container_width=True):
                if "add_history" in globals():
                    add_history("Kết thúc phiên dạy trực tuyến")
                st.session_state.timer_running = False
                st.session_state.live_running = False
                st.session_state.timer_start = None
                st.session_state.timer_end = None
                st.rerun()

# ==========================================================
# CÁC CHỨC NĂNG TÍCH HỢP TRÍ TUỆ NHÂN TẠO (AI)
# ==========================================================
def render_ai_mini_quiz(ai_engine):
    st.markdown("<div class='section-title'>🤖 AI Mini Quiz Live</div>", unsafe_allow_html=True)
    content = st.text_area("Nội dung đang giảng:", placeholder="Ví dụ: Định luật phản xạ ánh sáng...", key="quiz_content")
    col1, col2 = st.columns(2)
    with col1:
        number = st.selectbox("Số câu:", [1, 3, 5])
    with col2:
        level = st.selectbox("Mức độ:", ["Nhận biết", "Thông hiểu", "Vận dụng"])
        
    if st.button("✨ Sinh Quiz", use_container_width=True):
        if not content.strip():
            st.warning("⚠️ Nhập nội dung bài học.")
        elif ai_engine is None:
            st.error("❌ AI chưa sẵn sàng.")
        else:
            prompt = f"Bạn là giáo viên THCS. Tạo {number} câu hỏi trắc nghiệm.\nChủ đề:\n{content}\nMức độ:\n{level}\nYêu cầu:\n- Có 4 phương án A,B,C,D.\n- Có đáp án.\n- Có giải thích ngắn."
            with st.spinner("AI đang tạo câu hỏi..."):
                st.session_state.live_ai_quiz = ai_engine.generate_text(prompt)
                
    if st.session_state.get("live_ai_quiz"):
        st.success(st.session_state.live_ai_quiz)

def render_exit_ticket(ai_engine):
    st.markdown("<div class='section-title'>🎟️ Exit Ticket cuối giờ</div>", unsafe_allow_html=True)
    lesson = st.text_input("Tên bài học:", placeholder="Ví dụ: Nam châm điện", key="exit_lesson")
    
    if st.button("📐 Tạo Exit Ticket"):
        if ai_engine is None:
            st.error("❌ AI chưa sẵn sàng.")
        else:
            prompt = f"Bạn là giáo viên THCS.\nTạo Exit Ticket cho bài:\n{lesson}\nGồm:\n1. Điều em hiểu nhất?\n2. Một điều còn chưa rõ?\n3. Một câu hỏi vận dụng thực tế?\nNgôn ngữ phù hợp học sinh THCS."
            with st.spinner("Đang tạo..."):
                st.session_state.live_exit_ticket = ai_engine.generate_text(prompt)
                
    if st.session_state.get("live_exit_ticket"):
        st.info(st.session_state.live_exit_ticket)

def render_ai_activity(ai_engine):
    st.markdown("<div class='section-title'>💡 AI gợi ý hoạt động</div>", unsafe_allow_html=True)
    situation = st.text_area("Tình trạng lớp:", placeholder="Ví dụ: Học sinh mất tập trung sau 20 phút", key="class_situation")
    
    if st.button("🔍 AI đề xuất"):
        if ai_engine is None:
            st.error("❌ AI chưa sẵn sàng.")
        else:
            prompt = f"Bạn là chuyên gia phương pháp dạy học.\nTình trạng lớp:\n{situation}\nHãy đề xuất:\n- Một hoạt động kéo dài 3-5 phút.\n- Cách tổ chức.\n- Mục tiêu.\n- Cách đánh giá nhanh."
            with st.spinner("AI đang phân tích..."):
                st.session_state.live_activity = ai_engine.generate_text(prompt)
                
    if st.session_state.get("live_activity"):
        st.success(st.session_state.live_activity)
# ==========================================================
# CÁC TIỆN ÍCH LỚP HỌC TRỰC TIẾP
# ==========================================================
def render_student_picker():
    st.markdown("<div class='section-title'>🎯 Vòng quay học sinh</div>", unsafe_allow_html=True)
    students = st.text_area("Danh sách học sinh (mỗi dòng một tên):", height=120, key="students_input")
    
    if students.strip():
        st.session_state.student_list = [x.strip() for x in students.split("\n") if x.strip()]
        
    if st.button("🎲 Chọn ngẫu nhiên", use_container_width=True):
        if st.session_state.get("student_list"):
            st.session_state.selected_student = random.choice(st.session_state.student_list)
        else:
            st.warning("⚠️ Chưa có danh sách học sinh")
            
    selected = st.session_state.get("selected_student", "")
    if selected:
        st.success(f"🎉 Học sinh được chọn: **{selected}**")

def render_group_timer():
    st.markdown("<div class='section-title'>⏱ Đồng hồ hoạt động nhóm</div>", unsafe_allow_html=True)
    minutes = st.number_input("Thời gian (phút)", min_value=1, max_value=60, value=5, key="group_timer_input")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Bắt đầu nhóm", use_container_width=True):
            st.session_state.group_timer_seconds = minutes * 60
            st.session_state.group_timer_running = True
    with col2:
        if st.button("⏱ Dừng đếm", use_container_width=True):
            st.session_state.group_timer_running = False
            
    if st.session_state.get("group_timer_running", False):
        sec = st.session_state.group_timer_seconds
        st.metric("⏳ Nhóm còn lại", f"{sec//60:02d}:{sec%60:02d}")
        if sec > 0:
            time.sleep(1)
            st.session_state.group_timer_seconds -= 1
            st.rerun()
        else:
            st.warning("🚨 Hết thời gian hoạt động nhóm!")
            st.session_state.group_timer_running = False

def render_quick_score():
    st.markdown("<div class='section-title'>📝 Bảng điểm nhanh</div>", unsafe_allow_html=True)
    name = st.text_input("Tên học sinh", key="score_student_name")
    score = st.number_input("Điểm", min_value=0.0, max_value=10.0, step=0.5, key="score_student_value")
    
    if st.button("💾 Lưu điểm"):
        if name:
            if "quick_scores" not in st.session_state:
                st.session_state.quick_scores = {}
            st.session_state.quick_scores[name] = score
            st.toast(f"Đã lưu {score} điểm cho {name}!")
            
    scores = st.session_state.get("quick_scores", {})
    if scores:
        st.write(scores)

# ==========================================================
# KHỞI TẠO VÀ ĐIỀU KHUYỂN LUỒNG GIAO DIỆN CHÍNH
# ==========================================================
def init_session():
    defaults = {
        "live_running": False,
        "lesson_duration": 45,
        "timer_running": False,
        "timer_start": None,
        "timer_end": None,
        "live_ai_count": 0,
        "live_poll_count": 0,
        "live_ai_quiz": "",
        "live_exit_ticket": "",
        "live_activity": "",
        "student_list": [],
        "selected_student": "",
        "group_timer_seconds": 0,
        "group_timer_running": False,
        "quick_scores": {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def add_history(action_text):
    if "history_log" not in st.session_state:
        st.session_state.history_log = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.history_log.append(f"[{timestamp}] {action_text}")

def render_history():
    st.markdown("<div class='section-title'>📜 Nhật ký phiên</div>", unsafe_allow_html=True)
    logs = st.session_state.get("history_log", [])
    if logs:
        for log in reversed(logs):
            st.text(log)
    else:
        st.caption("Chưa có ghi nhận nào.")

# Các hàm giả lập bổ sung để tránh lỗi gọi hàm chưa định nghĩa
def render_class_info(): st.info("🏫 Lớp: 8A1 | Sĩ số: 40 | Phòng học trực tuyến")
def render_links(): st.caption("🔗 [Link tài liệu bài giảng](#) | [Link phòng hỗ trợ](#)")
def render_note(): st.text_area("📝 Ghi chú nhanh của giáo viên:", height=100)
def render_ai_quick_answer(ai_engine): pass
def render_ai_explain(ai_engine): pass
def render_ai_interaction(ai_engine): pass

# ==========================================================
# HÀM KẾT NỐI TOÀN BỘ GIAO DIỆN X-LIVE
# ==========================================================
def render_xd_live(ai_engine):
    load_css()
    init_session()
    render_header()
    render_dashboard()
    
    st.divider()
    col1, col2 = st.columns([1, 1])
    with col1:
        render_class_info()
        render_links()
    with col2:
        render_camera_live()
        
    st.divider()
    render_timer_setting()
    render_live_control()
    render_live_timer()
    
    st.divider()
    render_ai_quick_answer(ai_engine)
    render_ai_explain(ai_engine)
    render_ai_interaction(ai_engine)
    render_ai_mini_quiz(ai_engine)
    render_exit_ticket(ai_engine)
    render_ai_activity(ai_engine)
    
    st.divider()
    render_student_picker()
    render_group_timer()
    render_quick_score()
    
    st.divider()
    col3, col4 = st.columns([2, 1])
    with col3:
        render_note()
    with col4:
        render_history()
        
    st.caption("🤖 AI Teacher Assistant - Live Classroom Control Center")
