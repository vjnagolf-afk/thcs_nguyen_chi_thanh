import streamlit as st
import pandas as pd
from pypdf import PdfReader

def render_kiem_tra_khbd():
    st.markdown("### 🔎 Kiểm tra, phê duyệt Kế hoạch bài dạy (Giáo án)")
    st.caption("AI rà soát giáo án tự động dựa trên Công văn 5512 và định hướng phát triển phẩm chất, năng lực học sinh.")

    # --- KHỞI TẠO BỘ NHỚ TẠM (SESSION STATE) ---
    if "chat_history_khbd" not in st.session_state:
        st.session_state.chat_history_khbd = [{"role": "assistant", "content": "Chào thầy/cô! Hãy nạp file KHBD ở cột bên trái, sau đó nhấn **'Quét & Phân tích'** để tôi bắt đầu rà soát nhé!"}]
    
    if "khbd_metrics" not in st.session_state:
        st.session_state.khbd_metrics = {"score": "0/20", "percent": 0, "errors": 0, "analyzed": False}
        
    if "noidung_khbd" not in st.session_state:
        st.session_state.noidung_khbd = ""

    # --- BỐ CỤC GIAO DIỆN CHÍNH (CỘT 1: 30% | CỘT 2: 70%) ---
    col_left, col_right = st.columns([1, 2.2])

    # ==========================================
    # CỘT TRÁI: CONTROL PANEL & CHỈ SỐ NHANH
    # ==========================================
    with col_left:
        with st.container(border=True):
            st.markdown("#### ⚙️ Cấu hình Kiểm tra")
            mon_hoc = st.selectbox("Môn học:", ["Khoa học Tự nhiên", "Toán học", "Ngữ Văn", "Tiếng Anh", "Tin học", "Khác"])
            khoi_lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
            tieu_chi = st.selectbox("Bộ tiêu chí đánh giá:", ["Chuẩn CV 5512 + Năng lực", "Tích hợp Năng lực số & AI", "Kiểm tra ngắn (Khởi động)"])

            st.markdown("**Tải file giáo án lên đây:**")
            file_khbd = st.file_uploader("Hỗ trợ PDF (đang phát triển DOCX)", type=["pdf"], label_visibility="collapsed")
            
            if st.button("🚀 Quét & Phân tích", type="primary", use_container_width=True):
                if file_khbd:
                    with st.spinner("AI đang bóc tách 4 hoạt động và đối chiếu tiêu chí..."):
                        try:
                            # Đọc nội dung file PDF
                            reader = PdfReader(file_khbd)
                            extracted_text = ""
                            for page in reader.pages:
                                extracted_text += page.extract_text() + "\n"
                            
                            st.session_state.noidung_khbd = extracted_text
                            
                            # Mô phỏng quá trình AI chấm điểm (Thầy có thể thay bằng Logic gọi AI thật sau này)
                            st.session_state.khbd_metrics = {
                                "score": "16/20",
                                "percent": 80,
                                "errors": 3,
                                "analyzed": True
                            }
                            # Thêm câu chào của AI vào chat
                            st.session_state.chat_history_khbd.append({"role": "assistant", "content": f"✅ Tôi đã đọc xong giáo án môn **{mon_hoc} {khoi_lop}**. Tổng quan đạt **{st.session_state.khbd_metrics['percent']}%** chuẩn 5512. Thầy/cô có thể xem chi tiết ở tab **Báo cáo Dashboard** hoặc bấm vào các nút Gợi ý bên dưới để tôi phân tích sâu hơn."})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi đọc file: {e}")
                else:
                    st.warning("⚠️ Vui lòng tải file KHBD lên trước.")

        st.markdown("#### 📊 Chỉ số đánh giá tổng quan")
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Điểm số", st.session_state.khbd_metrics["score"])
        with m2: st.metric("Đạt chuẩn", f"{st.session_state.khbd_metrics['percent']}%")
        with m3: st.metric("Cần sửa", st.session_state.khbd_metrics["errors"])

    # ==========================================
    # CỘT PHẢI: KHUNG CHAT & DASHBOARD
    # ==========================================
    with col_right:
        tab_chat, tab_report = st.tabs(["💬 Trò chuyện với AI", "📊 Báo cáo chi tiết (Dashboard)"])

        # --- TAB 1: KHUNG CHAT TƯƠNG TÁC ---
        with tab_chat:
            # Vùng hiển thị tin nhắn (cố định chiều cao, tự động cuộn)
            chat_container = st.container(height=450)
            with chat_container:
                for msg in st.session_state.chat_history_khbd:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            # Hàng nút "Gợi ý nhanh" (Quick Replies)
            st.markdown("⚡ **Gợi ý kiểm tra nhanh:**")
            q1, q2, q3 = st.columns(3)
            quick_prompt = None
            if q1.button("🎯 Kiểm tra Mục tiêu", use_container_width=True): 
                quick_prompt = "Hãy rà soát xem phần Mục tiêu (Kiến thức, Năng lực, Phẩm chất) đã đo lường được chưa? Có dùng đúng động từ Bloom không?"
            if q2.button("🔄 Check 4 Hoạt động", use_container_width=True): 
                quick_prompt = "Kiểm tra chuỗi hoạt động học (Mở đầu, Hình thành KT, Luyện tập, Vận dụng) xem đã có đủ 4 bước (Mục tiêu, Nội dung, Sản phẩm, Tổ chức thực hiện) chưa?"
            if q3.button("💻 Năng lực số & AI", use_container_width=True): 
                quick_prompt = "Giáo án này đã tích hợp công cụ số hay AI vào hoạt động của học sinh chưa? Hãy gợi ý cách lồng ghép."

            # Ô nhập liệu tự do
            user_input = st.chat_input("Nhập câu hỏi để yêu cầu AI phân tích, sửa lỗi KHBD...")
            
            # Xử lý khi người dùng nhập hoặc bấm nút gợi ý
            prompt = user_input or quick_prompt
            if prompt:
                if not st.session_state.noidung_khbd:
                    st.warning("⚠️ Hãy tải file và Quét KHBD trước khi hỏi AI nhé!")
                else:
                    # Lưu câu hỏi của User
                    st.session_state.chat_history_khbd.append({"role": "user", "content": prompt})
                    
                    # Gọi AI (Mô phỏng hoặc gọi thật)
                    with chat_container:
                        with st.chat_message("user"): st.markdown(prompt)
                        with st.chat_message("assistant"):
                            with st.spinner("AI đang đối chiếu tiêu chí sư phạm..."):
                                # NẾU THẦY ĐÃ NỐI AI ENGINE, THAY ĐOẠN NÀY BẰNG: 
                                # ai_response = st.session_state.ai_engine.generate_text(f"Dựa trên KHBD sau: {st.session_state.noidung_khbd}. Hãy trả lời: {prompt}")
                                ai_response = f"*(Đây là phản hồi AI)* Dựa trên dữ liệu, tôi nhận thấy phần Tổ chức thực hiện ở Hoạt động Vận dụng đang thiếu bước **'Chuyển giao nhiệm vụ'**. Ngoài ra, mục tiêu đưa ra chưa gắn với sản phẩm học tập cụ thể. Thầy/cô nên điều chỉnh..."
                                st.markdown(ai_response)
                                
                    # Lưu câu trả lời của AI
                    st.session_state.chat_history_khbd.append({"role": "assistant", "content": ai_response})
                    st.rerun()

        # --- TAB 2: BÁO CÁO DASHBOARD TRỰC QUAN ---
        with tab_report:
            if st.session_state.khbd_metrics["analyzed"]:
                st.markdown("#### 📈 Mức độ hoàn thiện theo Tiêu chí 5512")
                
                c_prog1, c_prog2 = st.columns(2)
                with c_prog1:
                    st.caption("1. Mục tiêu & Yêu cầu cần đạt")
                    st.progress(90) # Mô phỏng số liệu
                    st.caption("2. Chuỗi hoạt động (4 bước)")
                    st.progress(70)
                with c_prog2:
                    st.caption("3. Phương pháp & Đánh giá")
                    st.progress(85)
                    st.caption("4. Tích hợp Năng lực số / AI")
                    st.progress(40)

                st.markdown("---")
                st.markdown("#### 📋 Chi tiết Cấu trúc Hoạt động học")
                st.caption("Bảng rà soát 4 mốc quan trọng trong từng hoạt động.")
                
                # Bảng trạng thái (Đạt/Chưa đạt)
                data_report = [
                    {"Hoạt động": "1. Mở đầu / Xác định vấn đề", "Mục tiêu": "🟢 Đạt", "Nội dung": "🟢 Đạt", "Sản phẩm": "🟢 Đạt", "Tổ chức thực hiện": "🟡 Cần sửa"},
                    {"Hoạt động": "2. Hình thành kiến thức mới", "Mục tiêu": "🟢 Đạt", "Nội dung": "🟢 Đạt", "Sản phẩm": "🟡 Thiếu", "Tổ chức thực hiện": "🟢 Đạt"},
                    {"Hoạt động": "3. Luyện tập", "Mục tiêu": "🟢 Đạt", "Nội dung": "🟢 Đạt", "Sản phẩm": "🟢 Đạt", "Tổ chức thực hiện": "🟢 Đạt"},
                    {"Hoạt động": "4. Vận dụng", "Mục tiêu": "🔴 Trống", "Nội dung": "🔴 Trống", "Sản phẩm": "🔴 Trống", "Tổ chức thực hiện": "🔴 Trống"},
                ]
                df_report = pd.DataFrame(data_report)
                st.dataframe(df_report, use_container_width=True, hide_index=True)

                st.error("🚨 **Cảnh báo lỗi nghiêm trọng:** Hoạt động Vận dụng bị thiếu hoàn toàn. Trong Hoạt động Mở đầu, phần 'Tổ chức thực hiện' chưa nêu rõ cách thức Báo cáo, thảo luận của học sinh.")
            else:
                st.info("💡 Bảng điều khiển (Dashboard) đang trống. Vui lòng tải file giáo án lên và nhấn 'Quét & Phân tích' ở cột điều khiển bên trái để xem kết quả trực quan.")
