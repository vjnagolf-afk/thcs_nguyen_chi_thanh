# -*- coding: utf-8 -*-
r"""
============================================================
ỨNG DỤNG: Chatbot Giáo dục Trợ giảng AI
Công nghệ: Streamlit & Thư viện `google-genai` mới nhất
Tác giả: Chuyên gia AI & Lập trình viên Python
============================================================
"""

import streamlit as st

# Import thư viện google-genai mới nhất
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# ============================================================
# CẤU HÌNH GIAO DIỆN TRANG
# ============================================================
st.set_page_config(
    page_title="Trợ Giảng AI - Hỗ Trợ Học Tập Thông Minh",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🎓 Trợ Giảng AI - Đồng Hành Cùng Em Học Tập")
st.caption("Trợ lý ảo kiên nhẫn, khoa học luôn sẵn sàng giải đáp thắc mắc và hướng dẫn em tư duy mỗi ngày.")

# ============================================================
# THANH BÊN (SIDEBAR): CÀI ĐẶT & LỰA CHỌN SƯ PHẠM
# ============================================================
with st.sidebar:
    st.header("⚙️ Cài đặt hệ thống")
    
    # Nhập API Key cá nhân
    api_key_input = st.text_input(
        "Nhập Gemini API Key:", 
        type="password", 
        placeholder="AIzaSy...",
        help="Nhập API Key cá nhân của bạn để sử dụng mô hình."
    )
    
    st.markdown("---")
    st.subheader("🎯 Lựa chọn chế độ trợ giảng")
    
    # Hai lựa chọn theo yêu cầu
    che_do = st.radio(
        "Chọn phong cách phản hồi:",
        [
            "💡 Lựa chọn 1: Gợi ý từng bước (Không giải bài hộ hoàn toàn, kích thích tư duy)",
            "📚 Lựa chọn 2: Giải bài chi tiết & Phân tích đáp án (Cặn kẽ, rõ ràng bản chất)"
        ]
    )
    
    st.markdown("---")
    if st.button("🧹 Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.8em; font-style: italic; color: gray;'>"
        "Sử dụng Google GenAI SDK mới nhất.<br>Hỗ trợ đa lượt (Multi-turn Chat)."
        "</div>", 
        unsafe_allow_html=True
    )

# ============================================================
# CÀI ĐẶT VAI TRÒ (SYSTEM INSTRUCTION) DỰA TRÊN LỰA CHỌN
# ============================================================
if "Lựa chọn 1" in che_do:
    system_instruction = (
        "Bạn đóng vai là một Giáo viên trợ giảng vô cùng ân cần, kiên nhẫn và thấu hiểu tâm lý học sinh. "
        "Nhiệm vụ của bạn là giải thích các khái niệm học tập một cách dễ hiểu, khoa học, có ví dụ minh họa gần gũi. "
        "[QUY TẮC BẮT BUỘC]: Tuyệt đối không giải bài hộ hoàn toàn hoặc đưa ra đáp án trực tiếp. "
        "Hãy đóng vai trò người dẫn dắt, đặt các câu hỏi gợi mở, chia nhỏ vấn đề thành từng bước để học sinh tự suy luận và tìm ra kết quả."
    )
else:
    system_instruction = (
        "Bạn đóng vai là một Giáo viên trợ giảng vô cùng ân cần, kiên nhẫn và am hiểu chuyên môn sâu sắc. "
        "Nhiệm vụ của bạn là giải thích các khái niệm học tập một cách dễ hiểu, khoa học, có ví dụ minh họa. "
        "[QUY TẮC BẮT BUỘC]: Hãy hỗ trợ giải bài hộ học sinh hoàn toàn một cách chi tiết, rõ ràng từng bước. "
        "Đồng thời, tiến hành phân tích sâu sắc các lựa chọn/đáp án, chỉ ra bản chất vấn đề và mở rộng ví dụ tương tự để học sinh củng cố kiến thức."
    )

# ============================================================
# QUẢN LÝ LỊCH SỬ TRÒ CHUYỆN (SESSION STATE)
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "👋 Chào em! Thầy/Cô là Trợ giảng AI đây. Em đang gặp khó khăn ở bài tập hoặc khái niệm môn học nào? Hãy chia sẻ để chúng ta cùng trao đổi nhé!"
        }
    ]

# Hiển thị lịch sử trò chuyện lên giao diện
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================
# XỬ LÝ NHẬP LIỆU VÀ GỌI API GEMINI (GOOGLE-GENAI SDK)
# ============================================================
if prompt := st.chat_input("Nhập câu hỏi hoặc bài tập của em vào đây..."):
    # Lưu tin nhắn người dùng vào lịch sử
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Tiến hành sinh phản hồi từ AI
    with st.chat_message("assistant"):
        with st.spinner("Trợ giảng đang suy nghĩ và chuẩn bị câu trả lời..."):
            try:
                if genai is None:
                    st.error("❌ Thư viện `google-genai` chưa được cài đặt trong môi trường. Vui lòng chạy lệnh: `pip install google-genai`")
                else:
                    # Khởi tạo client google-genai (Lấy key từ sidebar nếu có, ngược lại lấy từ biến môi trường)
                    client_kwargs = {}
                    if api_key_input.strip():
                        client_kwargs["api_key"] = api_key_input.strip()
                    
                    client = genai.Client(**client_kwargs)
                    
                    # Sử dụng mô hình Gemini 2.5 Flash tối ưu cho tốc độ và chất lượng đối thoại
                    model_id = "gemini-2.5-flash"
                    
                    # Thiết lập cấu hình hệ thống và nhiệt độ
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                    )
                    
                    # Chuyển đổi toàn bộ lịch sử trò chuyện sang định dạng chuẩn `types.Content` của SDK mới
                    formatted_contents = []
                    for m in st.session_state.messages:
                        role_name = "user" if m["role"] == "user" else "model"
                        formatted_contents.append(
                            types.Content(
                                role=role_name,
                                parts=[types.Part.from_text(text=m["content"])]
                            )
                        )
                    
                    # Gọi API tạo nội dung đa lượt (Multi-turn)
                    response = client.models.generate_content(
                        model=model_id,
                        contents=formatted_contents,
                        config=config
                    )
                    
                    reply_text = response.text
                    st.markdown(reply_text)
                    
                    # Lưu phản hồi vào lịch sử phiên làm việc
                    st.session_state.messages.append({"role": "assistant", "content": reply_text})
                    
            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi khi kết nối với Google GenAI API: {e}")
