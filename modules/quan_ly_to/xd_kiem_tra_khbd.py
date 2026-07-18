import streamlit as st
from pypdf import PdfReader

def render_kiem_tra_khbd(ai_engine):
    st.markdown("### 🔎 Kiểm tra, phê duyệt Kế hoạch bài dạy (Giáo án)")
    st.caption("AI đọc trực tiếp file KHBD tải lên, rà soát lỗi đa chiều và trích dẫn minh chứng thực tế từ văn bản.")

    # --- KHỞI TẠO BỘ NHỚ TẠM ---
    if "chat_history_khbd" not in st.session_state:
        st.session_state.chat_history_khbd = [{"role": "assistant", "content": "Chào thầy/cô! Hãy nạp file KHBD ở cột bên trái và nhấn **'Quét & Phân tích'** nhé!"}]
    
    if "noidung_khbd" not in st.session_state:
        st.session_state.noidung_khbd = ""
        
    if "ai_analysis_report" not in st.session_state:
        st.session_state.ai_analysis_report = ""

    # --- BỐ CỤC GIAO DIỆN CHÍNH ---
    col_left, col_right = st.columns([1, 2.2])

    # ==========================================
    # CỘT TRÁI: CONTROL PANEL 
    # ==========================================
    with col_left:
        with st.container(border=True):
            st.markdown("#### ⚙️ Cấu hình Kiểm tra")
            mon_hoc = st.selectbox("Môn học:", ["Khoa học Tự nhiên", "Toán học", "Ngữ Văn", "Tiếng Anh", "Tin học", "Khác"])
            khoi_lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
            
            st.markdown("**Tải file giáo án lên đây:**")
            file_khbd = st.file_uploader("Hỗ trợ định dạng PDF", type=["pdf"], label_visibility="collapsed")
            
            if st.button("🚀 Quét & Phân tích (Thực tế)", type="primary", use_container_width=True):
                if file_khbd:
                    with st.spinner("AI đang đọc file, tìm lỗi và lập bảng phân tích..."):
                        try:
                            # 1. Reset lại toàn bộ lịch sử và báo cáo cũ khi quét file mới
                            st.session_state.chat_history_khbd = []
                            st.session_state.ai_analysis_report = ""
                            st.session_state.noidung_khbd = ""
                            
                            # 2. Đọc nội dung file PDF thực tế
                            reader = PdfReader(file_khbd)
                            extracted_text = ""
                            for page in reader.pages:
                                extracted_text += page.extract_text() + "\n"
                            
                            # Cắt giới hạn ký tự (khoảng 15000 ký tự để không vượt giới hạn context của AI)
                            st.session_state.noidung_khbd = extracted_text[:15000] 
                            
                            # 3. Yêu cầu AI tự động lập Báo cáo chuyên sâu dựa trên text thật
                            prompt_scan = f"""
                            Bạn là chuyên gia thẩm định Kế hoạch bài dạy (KHBD) theo Công văn 5512. Hãy phân tích KHBD dưới đây và lập Báo cáo chi tiết theo 2 phần:

                            PHẦN 1: CẢNH BÁO LỖI & MÂU THUẪN (Kèm trích dẫn)
                            Chỉ ra các lỗi có thật trong văn bản theo 3 nhóm. BẮT BUỘC phải trích dẫn nguyên văn đoạn sai và chỉ rõ vị trí nằm ở mục nào. Nếu phần nào không có lỗi, ghi "Không phát hiện lỗi".
                            - 🔤 Lỗi chính tả & Câu từ
                            - 🧠 Lỗi kiến thức khoa học
                            - 🔗 Mâu thuẫn Logic & Hình thức (VD: Mục tiêu yêu cầu nhóm nhưng tổ chức cá nhân, ghi có video nhưng thiết bị không có máy chiếu...)

                            PHẦN 2: BẢNG ĐÁNH GIÁ 4 HOẠT ĐỘNG
                            Kẻ một bảng Markdown (gồm các cột: Hoạt động | Mục tiêu | Nội dung | Sản phẩm | Tổ chức thực hiện).
                            Đánh giá trạng thái thực tế của từng cột trong 4 hoạt động (Mở đầu, Hình thành KT, Luyện tập, Vận dụng) bằng các từ: Đạt / Cần sửa / Thiếu / Trống.

                            NỘI DUNG KHBD THỰC TẾ CẦN PHÂN TÍCH:
                            '''{st.session_state.noidung_khbd}'''
                            """
                            
                            # Gọi động cơ AI thật
                            report = ai_engine.generate_text(prompt_scan)
                            st.session_state.ai_analysis_report = report
                            
                            # 4. Ghi nhận thành công vào Chat
                            st.session_state.chat_history_khbd.append({"role": "assistant", "content": f"✅ Tôi đã đọc và phân tích xong giáo án **{mon_hoc} {khoi_lop}**. Mời thầy/cô xem **Báo cáo chi tiết** ở tab bên cạnh, hoặc đặt câu hỏi thảo luận thêm tại đây."})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi hệ thống hoặc lỗi kết nối AI: {e}")
                else:
                    st.warning("⚠️ Vui lòng tải file KHBD lên trước.")

    # ==========================================
    # CỘT PHẢI: KHUNG CHAT & DASHBOARD
    # ==========================================
    with col_right:
        tab_chat, tab_report = st.tabs(["💬 Trò chuyện với AI", "📊 Báo cáo AI phân tích (Thực tế)"])

        # --- TAB 1: KHUNG CHAT TƯƠNG TÁC ---
        with tab_chat:
            chat_container = st.container(height=450)
            with chat_container:
                for msg in st.session_state.chat_history_khbd:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            st.markdown("⚡ **Gợi ý kiểm tra nhanh:**")
            q1, q2 = st.columns(2)
            quick_prompt = None
            with q1:
                if st.button("🎯 Kiểm tra Mục tiêu (Bloom)", use_container_width=True): 
                    quick_prompt = "Hãy rà soát xem phần Mục tiêu đã dùng đúng động từ Bloom chưa? Nếu sai, hãy trích dẫn câu sai và gợi ý cách sửa lại."
                if st.button("🔄 Đề xuất lại HĐ Vận dụng", use_container_width=True): 
                    quick_prompt = "Dựa vào nội dung bài này, hãy đề xuất cho tôi một Hoạt động Vận dụng gắn với thực tiễn đời sống để bổ sung vào giáo án."
            with q2:
                if st.button("💻 Gợi ý Tích hợp Năng lực số", use_container_width=True): 
                    quick_prompt = "Với nội dung bài học này, tôi có thể lồng ghép công cụ số, AI hay thí nghiệm ảo nào vào các hoạt động? Hãy gợi ý chi tiết cách làm."
                if st.button("📝 Chỉnh lại văn phong", use_container_width=True): 
                    quick_prompt = "Hãy tìm các đoạn diễn đạt lủng củng, dài dòng trong giáo án và viết lại chúng sao cho chuẩn văn phong hành chính sư phạm."

            user_input = st.chat_input("Hỏi AI về nội dung giáo án đang tải lên...")
            
            prompt = user_input or quick_prompt
            if prompt:
                if not st.session_state.noidung_khbd:
                    st.warning("⚠️ Hãy tải file và Quét KHBD trước khi hỏi AI nhé!")
                else:
                    st.session_state.chat_history_khbd.append({"role": "user", "content": prompt})
                    with chat_container:
                        with st.chat_message("user"): st.markdown(prompt)
                        with st.chat_message("assistant"):
                            with st.spinner("AI đang đọc lại giáo án và trả lời..."):
                                try:
                                    # Gọi AI thật để trả lời câu hỏi dựa trên nội dung file
                                    chat_prompt = f"Dựa vào nội dung Kế hoạch bài dạy sau đây:\n\n{st.session_state.noidung_khbd}\n\nThực hiện yêu cầu sau của giáo viên: {prompt}"
                                    ai_response = ai_engine.generate_text(chat_prompt)
                                    st.markdown(ai_response)
                                    st.session_state.chat_history_khbd.append({"role": "assistant", "content": ai_response})
                                except Exception as e:
                                    st.error(f"Lỗi gọi AI: {e}")
                    st.rerun()

        # --- TAB 2: BÁO CÁO DASHBOARD ---
        with tab_report:
            if st.session_state.ai_analysis_report:
                st.success("Báo cáo dưới đây được AI tổng hợp TRỰC TIẾP từ dữ liệu file vừa tải lên.")
                # Hiển thị trực tiếp kết quả Markdown AI trả về (Thay thế hoàn toàn bảng giả)
                st.markdown(st.session_state.ai_analysis_report)
            else:
                st.info("💡 Bảng điều khiển đang trống. Vui lòng tải file giáo án lên và nhấn 'Quét & Phân tích (Thực tế)'.")
