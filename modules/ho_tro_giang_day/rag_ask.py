# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/rag_ask.py
Nhiệm vụ: Trợ lý Chat & Hỏi đáp trên Tài liệu (RAG Ask).
Nâng cấp: Hỗ trợ đọc PDF, DOCX, TXT. Bộ nhớ hội thoại liền mạch.
============================================================
"""

import io
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Bắt buộc import AIEngine2 để dùng Smart Router
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# Hàm đọc file đa định dạng
def extract_text_from_file(uploaded_file):
    if not uploaded_file:
        return ""
    
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    extracted_text = ""

    try:
        if file_name.endswith('.docx'):
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            extracted_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
        elif file_name.endswith('.pdf'):
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_text = "\n".join([page.get_text("text") for page in doc])
        elif file_name.endswith(('.txt', '.md')):
            extracted_text = file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Lỗi đọc file {file_name}: {e}")
        st.error(f"Không thể đọc file {file_name}. Vui lòng kiểm tra lại định dạng.")
        
    return extracted_text

def render_rag_ask(ai_engine_cu=None):
    # ==========================================
    # KHỞI TẠO BỘ NHỚ SESSION STATE
    # ==========================================
    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = [{"role": "assistant", "content": "👋 Chào bạn! Hãy tải tài liệu lên (PDF, Word, TXT) và đặt câu hỏi nhé."}]
    if "rag_context" not in st.session_state:
        st.session_state.rag_context = ""
    if "rag_file_name" not in st.session_state:
        st.session_state.rag_file_name = ""

    st.markdown("### 📚 Trợ lý Chat & Hỏi đáp trên Tài liệu (RAG Ask)")
    st.caption("Tải lên sách giáo khoa, tài liệu bài giảng (PDF, Word, TXT). AI sẽ đọc, ghi nhớ và giải đáp mọi thắc mắc của học sinh chỉ dựa trên nội dung tài liệu đó.")

    # ==========================================
    # CHIA BỐ CỤC: TRÁI (NẠP DỮ LIỆU) - PHẢI (CHAT)
    # ==========================================
    col_left, col_right = st.columns([1, 2.5], gap="large")

    # --- CỘT TRÁI: QUẢN LÝ DỮ LIỆU ---
    with col_left:
        st.markdown("#### 📥 Nạp dữ liệu")
        
        uploaded_file = st.file_uploader(
            "Tải tài liệu (PDF, DOCX, TXT, MD)", 
            type=["pdf", "docx", "txt", "md"],
            help="Dung lượng tối đa tùy thuộc vào cấu hình Streamlit (thường là 200MB)."
        )
        
        # Xử lý khi có file mới tải lên
        if uploaded_file and uploaded_file.name != st.session_state.rag_file_name:
            with st.spinner("Đang đọc và phân tích tài liệu..."):
                extracted_text = extract_text_from_file(uploaded_file)
                if extracted_text.strip():
                    st.session_state.rag_context = extracted_text
                    st.session_state.rag_file_name = uploaded_file.name
                    # Thêm thông báo vào khung chat
                    st.session_state.rag_messages.append({"role": "assistant", "content": f"✅ Đã đọc xong tài liệu **{uploaded_file.name}**. Bạn muốn hỏi gì về tài liệu này?"})
                    st.rerun()
                else:
                    st.error("Tài liệu rỗng hoặc không thể trích xuất chữ.")

        # Hiển thị trạng thái bộ nhớ
        if st.session_state.rag_context:
            st.success(f"🧠 **Đang ghi nhớ:** {st.session_state.rag_file_name}")
            with st.expander("👁️ Xem trước nội dung (Trích xuất)"):
                st.text(st.session_state.rag_context[:1000] + "\n\n... (Đã cắt bớt hiển thị)")
        else:
            st.info("Chưa có tài liệu nào trong bộ nhớ.")

        if st.button("🗑️ Xóa bộ nhớ & Cuộc trò chuyện", use_container_width=True):
            st.session_state.rag_context = ""
            st.session_state.rag_file_name = ""
            st.session_state.rag_messages = [{"role": "assistant", "content": "👋 Chào bạn! Hãy tải tài liệu lên (PDF, Word, TXT) và đặt câu hỏi nhé."}]
            st.rerun()

    # --- CỘT PHẢI: KHUNG CHATBOT ---
    with col_right:
        st.markdown("#### 💬 Khung Chatbot")
        
        # Tạo khung chứa chat có viền và thanh cuộn (giả lập bằng container)
        chat_container = st.container(height=500, border=True)
        
        with chat_container:
            # Hiển thị lịch sử chat
            for message in st.session_state.rag_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Ô nhập liệu chat ở dưới cùng
        if prompt_text := st.chat_input("Hỏi AI về nội dung trong tài liệu..."):
            
            if AIEngine2 is None:
                st.error("❌ Chưa kết nối được AI Engine.")
                return

            # 1. Thêm câu hỏi của user vào giao diện
            st.session_state.rag_messages.append({"role": "user", "content": prompt_text})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt_text)
            
            # 2. Xây dựng Prompt RAG chuyên sâu
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("AI đang tìm kiếm trong tài liệu..."):
                        
                        # Lấy 4 tin nhắn gần nhất để làm ngữ cảnh hội thoại
                        history_text = ""
                        if len(st.session_state.rag_messages) > 2:
                            recent_msgs = st.session_state.rag_messages[-5:-1] # Bỏ câu hỏi hiện tại (nằm ở -1)
                            history_text = "\n".join([f"{'Học sinh' if m['role']=='user' else 'AI'}: {m['content']}" for m in recent_msgs])

                        rag_prompt = f"""
BẠN LÀ MỘT TRỢ LÝ HỌC THUẬT AI TẬN TÂM, THÔNG MINH VÀ KỶ LUẬT.
Nhiệm vụ của bạn là trả lời câu hỏi của người dùng, NHƯNG BẮT BUỘC PHẢI DỰA TRÊN TÀI LIỆU CUNG CẤP DƯỚI ĐÂY.

--- NỘI DUNG TÀI LIỆU CỦA GIÁO VIÊN ---
{st.session_state.rag_context if st.session_state.rag_context else "(Người dùng chưa tải lên tài liệu nào. Hãy nhắc họ tải lên)."}

--- LỊCH SỬ TRÒ CHUYỆN GẦN ĐÂY ---
{history_text}

--- CÂU HỎI MỚI CỦA NGƯỜI DÙNG ---
{prompt_text}

[KỶ LUẬT TRẢ LỜI SỐNG CÒN]
1. Nếu câu hỏi liên quan đến Tài liệu: Hãy trích xuất thông tin, tổng hợp và trả lời dễ hiểu, có thể trích dẫn đoạn liên quan.
2. NẾU CÂU HỎI KHÔNG NẰM TRONG TÀI LIỆU: BẮT BUỘC phải trả lời: "Xin lỗi, thông tin này không có trong tài liệu bài giảng. Em có muốn hỏi thêm gì về nội dung tài liệu không?". TUYỆT ĐỐI KHÔNG tự bịa ra kiến thức bên ngoài để trả lời.
3. Trình bày bằng Markdown rõ ràng, thân thiện với học sinh.
"""
                        try:
                            engine_v2 = AIEngine2(default_model="gemini-2.5-flash") # Dùng Flash cho tốc độ phản hồi Chat siêu nhanh
                            response = engine_v2.generate_text(rag_prompt)
                            
                            if response.startswith("❌"):
                                st.error(response)
                            else:
                                st.markdown(response)
                                st.session_state.rag_messages.append({"role": "assistant", "content": response})
                        except Exception as e:
                            st.error(f"Lỗi truy vấn AI: {e}")
