# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_chatbot.py
Nhiệm vụ: Trợ lý Chatbot Giáo dục (Trợ giảng AI Sư phạm).
Công nghệ: Thư viện `google-genai` mới nhất của Google.
Tính năng: 
- Cấu hình API Key trên Sidebar.
- Lưu trữ lịch sử trò chuyện (Chat history).
- 2 Chế độ sư phạm: (1) Socratic - Gợi ý từng bước, (2) Giải thích chi tiết.
============================================================
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Thử import thư viện google-genai mới nhất
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

def render_xd_chatbot(ai_engine_cu=None):
    st.markdown("### 🤖 Trợ lý Chatbot Giáo dục (Trợ giảng Sư phạm AI)")
    st.info("💡 **Góc chuyên gia:** Trợ lý ảo kiên nhẫn đồng hành cùng học sinh. Hệ thống áp dụng phương pháp Sư phạm Socratic (gợi mở tư duy) hoặc Giải thích chi tiết tùy theo lựa chọn của người học.")

    # ========================================================
    # 1. THANH BÊN (SIDEBAR) CẤU HÌNH API KEY & CHẾ ĐỘ SƯ PHẠM
    # ========================================================
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Cài đặt Trợ giảng AI")
        
        # Nhập API Key tùy chọn
        api_key_input = st.text_input("Nhập Gemini API Key (Tùy chọn):", type="password", placeholder="AIzaSy...", help="Nếu để trống, hệ thống sẽ tự động dùng API Key mặc định của ứng dụng.")
        
        st.markdown("---")
        st.markdown("### 🎓 Chế độ Hỗ trợ Sư phạm")
        che_do_su_pham = st.radio(
            "Chọn phong cách phản hồi của Trợ giảng:",
            [
                "💡 Lựa chọn 1: Phương pháp Gợi mở (Socratic) - Không giải hộ hoàn toàn, đưa ra gợi ý từng bước để học sinh tự tư duy.",
                "📚 Lựa chọn 2: Giải bài chi tiết & Phân tích đáp án - Hỗ trợ giải thích cặn kẽ, rõ ràng từng bước kèm ví dụ."
            ]
        )
        
        st.markdown("---")
        if st.button("🧹 Xóa lịch sử trò chuyện", use_container_width=True):
            st.session_state["chatbot_messages"] = []
            st.rerun()

    # ========================================================
    # 2. KHỞI TẠO LỊCH SỬ TRÒ CHUYỆN (SESSION STATE)
    # ========================================================
    if "chatbot_messages" not in st.session_state:
        st.session_state["chatbot_messages"] = [
            {
                "role": "assistant", 
                "content": "👋 Chào bạn! Mình là Trợ giảng AI. Bạn đang gặp khó khăn ở bài tập hoặc khái niệm môn học nào? Hãy chia sẻ để chúng ta cùng giải quyết nhé!"
            }
        ]

    # Xác định System Instruction dựa trên lựa chọn của giáo viên/học sinh
    if "Lựa chọn 1" in che_do_su_pham:
        system_instruction = """
Bạn là một Giáo viên trợ giảng vô cùng ân cần, kiên nhẫn và am hiểu tâm lý học sinh.
[QUY TẮC PHẢN HỒI BẮT BUỘC - SƯ PHẠM SOCRATIC]:
1. TUYỆT ĐỐI KHÔNG giải bài tập hộ học sinh từ A-Z hoặc đưa ra đáp án trực tiếp ngay từ đầu.
2. Hãy đóng vai trò là người dẫn dắt: Đặt các câu hỏi gợi mở, chia nhỏ vấn đề thành các bước dễ hiểu, và động viên học sinh tự suy luận ra kết quả.
3. Giải thích khái niệm bằng các ví dụ thực tế gần gũi, sinh động. Khuyến khích tư duy phản biện.
"""
    else:
        system_instruction = """
Bạn là một Chuyên gia Giáo dục và Gia sư giỏi chuyên môn, tận tâm.
[QUY TẮC PHẢN HỒI BẮT BUỘC - GIẢI THÍCH CHI TIẾT]:
1. Khi học sinh đưa ra một bài toán hoặc câu hỏi, hãy tiến hành giải bài hộ một cách hoàn chỉnh, rõ ràng.
2. Trình bày lời giải thành các bước logic (Bước 1, Bước 2, Kết luận).
3. Có phần phân tích sâu tại sao lại chọn hướng giải quyết đó, lưu ý các bẫy thường gặp và mở rộng thêm ví dụ tương tự để học sinh củng cố kiến thức.
"""

    # ========================================================
    # 3. HIỂN THỊ KHUNG CHAT (UI)
    # ========================================================
    chat_container = st.container(height=500, border=True)
    
    with chat_container:
        for message in st.session_state["chatbot_messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # ========================================================
    # 4. XỬ LÝ GỬI TIN NHẮN & KẾT NỐI SDK `google-genai`
    # ========================================================
    if prompt := st.chat_input("Nhập câu hỏi hoặc bài tập của bạn vào đây..."):
        # Thêm tin nhắn của người dùng vào lịch sử
        st.session_state["chatbot_messages"].append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Tiến hành gọi API
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Trợ giảng AI đang suy nghĩ..."):
                    try:
                        if genai is None:
                            st.error("❌ Thư viện `google-genai` chưa được cài đặt trong môi trường Python.")
                            return

                        # Khởi tạo client google-genai (Sử dụng key tùy chỉnh nếu có, ngược lại lấy mặc định tự động)
                        client_kwargs = {}
                        if api_key_input.strip():
                            client_kwargs["api_key"] = api_key_input.strip()
                        
                        client = genai.Client(**client_kwargs)
                        
                        # Sử dụng mô hình Gemini 2.5 Flash (hoặc 2.5 Pro) tối ưu cho chat
                        model_id = "gemini-2.5-flash"
                        
                        # Chuyển đổi lịch sử chat của Streamlit sang định dạng chuẩn của google-genai SDK nếu cần,
                        # Hoặc sử dụng client.chats.create với system_instruction
                        config = types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.7,
                        )
                        
                        # Xây dựng danh sách contents bao gồm toàn bộ lịch sử để duy trì đa lượt (multi-turn)
                        formatted_contents = []
                        for m in st.session_state["chatbot_messages"]:
                            role_name = "user" if m["role"] == "user" else "model"
                            formatted_contents.append(
                                types.Content(
                                    role=role_name,
                                    parts=[types.Part.from_text(text=m["content"])]
                                )
                            )
                        
                        # Gọi generate_content với lịch sử đầy đủ
                        response = client.models.generate_content(
                            model=model_id,
                            contents=formatted_contents,
                            config=config
                        )
                        
                        reply_text = response.text
                        st.markdown(reply_text)
                        
                        # Lưu phản hồi vào lịch sử
                        st.session_state["chatbot_messages"].append({"role": "assistant", "content": reply_text})
                        
                    except Exception as e:
                        error_msg = f"❌ Đã xảy ra lỗi kết nối với Google GenAI SDK: {e}"
                        st.error(error_msg)
