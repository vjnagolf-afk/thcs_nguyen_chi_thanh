import streamlit as st
import pandas as pd
from pypdf import PdfReader

def render_kiem_tra_khbd():
    st.markdown("### 🔎 Kiểm tra, phê duyệt Kế hoạch bài dạy (Giáo án)")
    st.caption("AI rà soát giáo án tự động dựa trên Công văn 5512, đồng thời kiểm tra lỗi chính tả, kiến thức, và tính logic của bài soạn.")

    # --- KHỞI TẠO BỘ NHỚ TẠM (SESSION STATE) ---
    if "chat_history_khbd" not in st.session_state:
        st.session_state.chat_history_khbd = [{"role": "assistant", "content": "Chào thầy/cô! Hãy nạp file KHBD ở cột bên trái, chọn các tùy chọn rà soát chuyên sâu và nhấn **'Quét & Phân tích'** nhé!"}]
    
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
            
            # Tùy chọn kiểm tra chuyên sâu mới
            st.markdown("**Kiểm tra chuyên sâu (Tích hợp AI):**")
            check_chinh_ta = st.checkbox("🔤 Rà soát Lỗi chính tả & Câu từ", value=True)
            check_kien_thuc = st.checkbox("🧠 Kiểm tra tính chính xác kiến thức", value=True)
            check_logic = st.checkbox("🔗 Phát hiện mâu thuẫn logic & Hình ảnh", value=True)

            st.markdown("**Tải file giáo án lên đây:**")
            file_khbd = st.file_uploader("Hỗ trợ PDF (đang phát triển DOCX)", type=["pdf"], label_visibility="collapsed")
            
            if st.button("🚀 Quét & Phân tích", type="primary", use_container_width=True):
                if file_khbd:
                    with st.spinner("AI đang bóc tách nội dung, quét lỗi chính tả và đối chiếu logic..."):
                        try:
                            # Đọc nội dung file
                            reader = PdfReader(file_khbd)
                            extracted_text = ""
                            for page in reader.pages:
                                extracted_text += page.extract_text() + "\n"
                            
                            st.session_state.noidung_khbd = extracted_text
                            
                            # Mô phỏng quá trình AI tính điểm
                            st.session_state.khbd_metrics = {
                                "score": "16/20",
                                "percent": 80,
                                "errors": 5, # Tăng số lỗi vì có thêm tính năng quét sâu
                                "analyzed": True
                            }
                            st.session_state.chat_history_khbd.append({"role": "assistant", "content": f"✅ Tôi đã đọc xong giáo án **{mon_hoc} {khoi_lop}**. Phát hiện **{st.session_state.khbd_metrics['errors']} vấn đề** liên quan đến cấu trúc, chính tả và logic. Thầy/cô vui lòng chuyển sang tab **Báo cáo chi tiết** để xem cảnh báo, hoặc dùng các nút lệnh bên dưới để thảo luận chuyên sâu."})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi đọc file: {e}")
                else:
                    st.warning("⚠️ Vui lòng tải file KHBD lên trước.")

        st.markdown("#### 📊 Chỉ số đánh giá tổng quan")
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Điểm số", st.session_state.khbd_metrics["score"])
        with m2: st.metric("Cấu trúc", f"{st.session_state.khbd_metrics['percent']}%")
        with m3: st.metric("Cần sửa", f'{st.session_state.khbd_metrics["errors"]} lỗi', delta="-Cảnh báo", delta_color="inverse")

    # ==========================================
    # CỘT PHẢI: KHUNG CHAT & DASHBOARD
    # ==========================================
    with col_right:
        tab_chat, tab_report = st.tabs(["💬 Trò chuyện với AI", "📊 Báo cáo chi tiết (Dashboard)"])

        # --- TAB 1: KHUNG CHAT TƯƠNG TÁC ---
        with tab_chat:
            chat_container = st.container(height=400)
            with chat_container:
                for msg in st.session_state.chat_history_khbd:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            # Hàng nút "Gợi ý nhanh" chia làm 2 hàng cho gọn gàng
            st.markdown("⚡ **Gợi ý kiểm tra nhanh:**")
            q1, q2 = st.columns(2)
            quick_prompt = None
            with q1:
                if st.button("🎯 Kiểm tra Mục tiêu (Bloom)", use_container_width=True): 
                    quick_prompt = "Hãy rà soát xem phần Mục tiêu đã đo lường được chưa? Có dùng đúng động từ Bloom không?"
                if st.button("🔄 Rà soát 4 Hoạt động", use_container_width=True): 
                    quick_prompt = "Kiểm tra chuỗi hoạt động học xem đã có đủ 4 bước (Mục tiêu, Nội dung, Sản phẩm, Tổ chức thực hiện) chưa?"
            with q2:
                if st.button("💻 Tích hợp Năng lực số", use_container_width=True): 
                    quick_prompt = "Giáo án này đã tích hợp công cụ số hay AI vào hoạt động của học sinh chưa? Hãy gợi ý cách lồng ghép."
                # --- Nút chức năng Rà soát Lỗi mới ---
                if st.button("🔍 Quét Lỗi & Mâu thuẫn logic", use_container_width=True, type="primary"): 
                    quick_prompt = "Hãy đọc thật kỹ nội dung và liệt kê chi tiết: 1. Các lỗi chính tả/diễn đạt. 2. Các sai sót về mặt kiến thức bộ môn. 3. Các mâu thuẫn logic (Ví dụ: mục tiêu yêu cầu làm nhóm nhưng thực hiện lại làm cá nhân, nội dung hỏi biểu đồ nhưng không có biểu đồ...)."

            user_input = st.chat_input("Nhập câu hỏi để yêu cầu AI phân tích, sửa lỗi KHBD...")
            
            prompt = user_input or quick_prompt
            if prompt:
                if not st.session_state.noidung_khbd:
                    st.warning("⚠️ Hãy tải file và Quét KHBD trước khi hỏi AI nhé!")
                else:
                    st.session_state.chat_history_khbd.append({"role": "user", "content": prompt})
                    with chat_container:
                        with st.chat_message("user"): st.markdown(prompt)
                        with st.chat_message("assistant"):
                            with st.spinner("AI đang phân tích ngữ nghĩa và đối chiếu logic..."):
                                # Giả lập phản hồi AI cho chức năng rà soát lỗi
                                ai_response = "*(Demo AI Phản hồi)* Dựa trên phân tích nội dung, tôi phát hiện ra một số mâu thuẫn: \n\n- **Về logic:** Ở Hoạt động 3, mục tiêu yêu cầu 'học sinh phân tích biểu đồ nhiệt độ', nhưng trong phần 'Nội dung' lại không hề nhắc đến việc trình chiếu hay phát tài liệu có biểu đồ này.\n- **Về diễn đạt:** Từ 'năng lự' (thiếu chữ c), 'sắp sếp' (sai chính tả) lặp lại 2 lần ở trang 3.\n\nThầy/cô có muốn tôi tự động sửa và viết lại đoạn văn này không?"
                                st.markdown(ai_response)
                                
                    st.session_state.chat_history_khbd.append({"role": "assistant", "content": ai_response})
                    st.rerun()

        # --- TAB 2: BÁO CÁO DASHBOARD TRỰC QUAN ---
        with tab_report:
            if st.session_state.khbd_metrics["analyzed"]:
                
                # BỔ SUNG: KHU VỰC CẢNH BÁO LỖI CHI TIẾT
                st.markdown("#### 🚨 Cảnh báo Lỗi & Mâu thuẫn (AI Phát hiện)")
                with st.expander("Bấm để xem phân tích lỗi chi tiết", expanded=True):
                    st.warning("🔤 **Lỗi chính tả & Câu từ:** \n- Phát hiện 3 lỗi chính tả (VD: 'Năng lự' -> 'Năng lực', 'ngiên cứu' -> 'nghiên cứu'). \n- Câu văn ở phần Mở đầu hơi dài và lủng củng, nên ngắt thành 2 ý rõ ràng.")
                    st.error("🧠 **Lỗi kiến thức khoa học:** \n- Tại Hoạt động 2 (Hình thành kiến thức mới): Công thức hoặc định nghĩa đang cung cấp có dấu hiệu nhầm lẫn (cần kiểm tra lại đại lượng vật lý/thuật ngữ chuyên ngành).")
                    st.info("🔗 **Mâu thuẫn Logic & Hình thức:** \n- 🔴 **Mâu thuẫn phương pháp:** Mục tiêu yêu cầu *'Thảo luận nhóm'* nhưng phần Tổ chức thực hiện lại ghi *'Học sinh tự làm bài ra giấy nháp'*.\n- 🔴 **Mâu thuẫn học liệu:** Có đặt câu hỏi phân tích dữ liệu bảng biểu, nhưng phần *'Thiết bị dạy học'* không chuẩn bị bảng biểu này.")

                st.markdown("---")
                
                # Phần đánh giá 5512 (Giữ nguyên cấu trúc)
                st.markdown("#### 📈 Mức độ hoàn thiện theo cấu trúc 5512")
                c_prog1, c_prog2 = st.columns(2)
                with c_prog1:
                    st.caption("1. Mục tiêu & Yêu cầu cần đạt")
                    st.progress(90)
                    st.caption("2. Chuỗi hoạt động (4 bước)")
                    st.progress(70)
                with c_prog2:
                    st.caption("3. Phương pháp & Đánh giá")
                    st.progress(85)
                    st.caption("4. Tính logic & Chính xác (Nội dung)")
                    st.progress(60) # Chỉ số mới phản ánh độ chính xác nội dung

                st.markdown("---")
                st.markdown("#### 📋 Chi tiết Chuỗi hoạt động học")
                st.caption("Bảng rà soát 4 mốc quan trọng trong từng hoạt động.")
                
                data_report = [
                    {"Hoạt động": "1. Mở đầu / Xác định vấn đề", "Mục tiêu": "🟢 Đạt", "Nội dung": "🟢 Đạt", "Sản phẩm": "🟢 Đạt", "Tổ chức": "🟡 Thiếu logic"},
                    {"Hoạt động": "2. Hình thành kiến thức mới", "Mục tiêu": "🟢 Đạt", "Nội dung": "🔴 Sai kiến thức", "Sản phẩm": "🟡 Thiếu", "Tổ chức": "🟢 Đạt"},
                    {"Hoạt động": "3. Luyện tập", "Mục tiêu": "🟢 Đạt", "Nội dung": "🟢 Đạt", "Sản phẩm": "🟢 Đạt", "Tổ chức": "🟢 Đạt"},
                    {"Hoạt động": "4. Vận dụng", "Mục tiêu": "🔴 Trống", "Nội dung": "🔴 Trống", "Sản phẩm": "🔴 Trống", "Tổ chức": "🔴 Trống"},
                ]
                df_report = pd.DataFrame(data_report)
                st.dataframe(df_report, use_container_width=True, hide_index=True)

            else:
                st.info("💡 Bảng điều khiển (Dashboard) đang trống. Vui lòng tải file giáo án lên và nhấn 'Quét & Phân tích' ở cột điều khiển bên trái để xem kết quả trực quan.")
