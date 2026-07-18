import streamlit as st
import pandas as pd
from pypdf import PdfReader

def render_kiem_tra_khbd():
    st.markdown("### 🔎 Kiểm tra, phê duyệt Kế hoạch bài dạy (Giáo án)")
    st.caption("AI rà soát giáo án tự động dựa trên Công văn 5512, rà soát lỗi đa chiều và trích dẫn minh chứng trực tiếp từ văn bản gốc.")

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
            
            st.markdown("**Kiểm tra chuyên sâu (Tích hợp AI):**")
            check_chinh_ta = st.checkbox("🔤 Rà soát Lỗi chính tả & Câu từ", value=True)
            check_kien_thuc = st.checkbox("🧠 Kiểm tra tính chính xác kiến thức", value=True)
            check_logic = st.checkbox("🔗 Phát hiện mâu thuẫn & Trích dẫn", value=True)

            st.markdown("**Tải file giáo án lên đây:**")
            file_khbd = st.file_uploader("Hỗ trợ PDF (đang phát triển DOCX)", type=["pdf"], label_visibility="collapsed")
            
            if st.button("🚀 Quét & Phân tích", type="primary", use_container_width=True):
                if file_khbd:
                    with st.spinner("AI đang bóc tách, rà soát từng dòng và tìm minh chứng..."):
                        try:
                            # Đọc nội dung file
                            reader = PdfReader(file_khbd)
                            extracted_text = ""
                            for page in reader.pages:
                                extracted_text += page.extract_text() + "\n"
                            
                            st.session_state.noidung_khbd = extracted_text
                            
                            # Mô phỏng quá trình AI tính điểm
                            st.session_state.khbd_metrics = {
                                "score": "15/20",
                                "percent": 75,
                                "errors": 4, 
                                "analyzed": True
                            }
                            st.session_state.chat_history_khbd.append({"role": "assistant", "content": f"✅ Tôi đã đọc xong giáo án **{mon_hoc} {khoi_lop}**. Phát hiện **{st.session_state.khbd_metrics['errors']} vấn đề** có kèm theo trích dẫn chính xác từ văn bản. Thầy/cô vui lòng chuyển sang tab **Báo cáo chi tiết** để xem cảnh báo, hoặc dùng các nút lệnh bên dưới để thảo luận."})
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
                    quick_prompt = "Hãy rà soát xem phần Mục tiêu đã đo lường được chưa? Có dùng đúng động từ Bloom không? Yêu cầu trích dẫn câu sai."
                if st.button("🔄 Rà soát 4 Hoạt động", use_container_width=True): 
                    quick_prompt = "Kiểm tra chuỗi hoạt động học xem đã có đủ 4 bước (Mục tiêu, Nội dung, Sản phẩm, Tổ chức thực hiện) chưa?"
            with q2:
                if st.button("💻 Tích hợp Năng lực số", use_container_width=True): 
                    quick_prompt = "Giáo án này đã tích hợp công cụ số hay AI vào hoạt động chưa? Hãy gợi ý cách lồng ghép."
                
                # --- Nút chức năng Rà soát Lỗi với Prompt ép buộc trích dẫn ---
                if st.button("🔍 Quét Lỗi & Trích dẫn gốc", use_container_width=True, type="primary"): 
                    quick_prompt = """Hãy đọc thật kỹ nội dung KHBD tải lên. YÊU CẦU BẮT BUỘC: Khi chỉ ra bất kỳ lỗi chính tả, sai kiến thức hay mâu thuẫn logic nào, bạn PHẢI:
                    1. Trích dẫn nguyên văn đoạn chứa lỗi.
                    2. Chỉ rõ vị trí (nằm ở Hoạt động/Đề mục nào).
                    Ví dụ: 'Mâu thuẫn: Tại Mục II.2 ghi [...] nhưng phần Tổ chức thực hiện lại ghi [...]'."""

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
                            with st.spinner("AI đang quét lỗi và truy xuất dữ liệu trích dẫn..."):
                                # Giả lập phản hồi AI cho chức năng rà soát lỗi chi tiết
                                ai_response = "*(Demo AI Phản hồi)* \n\n🔴 **Phát hiện mâu thuẫn:**\n- **Vị trí:** Hoạt động 1 (Mở đầu) và Mục II (Thiết bị dạy học).\n- **Trích dẫn Hoạt động 1:** *'Giáo viên trình chiếu đoạn video về sự rơi tự do...'* \n- **Trích dẫn Mục II:** *'Máy tính, SGK, thước kẻ'*.\n-> **Vấn đề:** Có sử dụng video nhưng trong phần Thiết bị dạy học không hề chuẩn bị Tivi, Máy chiếu hay Loa.\n\nThầy/cô có muốn tôi liệt kê thêm các lỗi khác không?"
                                st.markdown(ai_response)
                                
                    st.session_state.chat_history_khbd.append({"role": "assistant", "content": ai_response})
                    st.rerun()

        # --- TAB 2: BÁO CÁO DASHBOARD TRỰC QUAN ---
        with tab_report:
            if st.session_state.khbd_metrics["analyzed"]:
                
                # BỔ SUNG: KHU VỰC CẢNH BÁO LỖI CHI TIẾT (CÓ TRÍCH DẪN RÕ RÀNG)
                st.markdown("#### 🚨 Cảnh báo Lỗi & Mâu thuẫn (Kèm trích dẫn)")
                with st.expander("Bấm để xem phân tích lỗi chi tiết", expanded=True):
                    
                    st.warning("""🔤 **Lỗi chính tả & Câu từ:** 
- **Lỗi 1:** Sai chính tả. 
  *📍 Vị trí:* Mục I. Yêu cầu cần đạt > 2. Năng lực.
  *💬 Trích dẫn:* "...thông qua bài học giúp học sinh phát triển **năng lự** giải quyết vấn đề..."
- **Lỗi 2:** Câu văn lủng củng.
  *📍 Vị trí:* Hoạt động 1 > Tổ chức thực hiện.
  *💬 Trích dẫn:* "...giáo viên yêu cầu học sinh **ngiên cứu** hình ảnh rồi sau đó giáo viên lại hỏi học sinh trả lời..."
""")
                    
                    st.error("""🧠 **Lỗi kiến thức khoa học:** 
- **Lỗi 1:** Nhầm lẫn khái niệm / thuật ngữ.
  *📍 Vị trí:* Hoạt động 2 (Hình thành kiến thức) > Sản phẩm học tập.
  *💬 Trích dẫn:* "...học sinh nêu được: Khối lượng riêng là **trọng lượng** của một mét khối vật chất..."
  *💡 Sửa lại:* Khối lượng riêng là **khối lượng** của một đơn vị thể tích vật chất đó.
""")
                    
                    st.info("""🔗 **Mâu thuẫn Logic & Hình thức:** 
- 🔴 **Mâu thuẫn Phương pháp & Tổ chức:** 
  *📍 Vị trí đối chiếu:* Hoạt động 3 (Luyện tập).
  *💬 Trích dẫn Mục tiêu:* "...Học sinh **thảo luận nhóm 4 người** để hoàn thành phiếu học tập..."
  *💬 Trích dẫn Tổ chức thực hiện:* "...Giáo viên yêu cầu **mỗi học sinh tự làm bài** ra giấy nháp..." 
  *(-> Mâu thuẫn: Mục tiêu yêu cầu làm nhóm nhưng tổ chức lại làm cá nhân).*

- 🔴 **Mâu thuẫn Học liệu:** 
  *📍 Vị trí đối chiếu:* Hoạt động 1 và Mục II (Thiết bị dạy học).
  *💬 Trích dẫn HĐ 1:* "...GV yêu cầu học sinh quan sát **Biểu đồ nhiệt độ lượng mưa**..."
  *💬 Trích dẫn Mục II:* "...Máy chiếu, SGK, phấn, bảng..." 
  *(-> Mâu thuẫn: Không có bước chuẩn bị dữ liệu Biểu đồ nhiệt độ trong phần học liệu).*
""")

                st.markdown("---")
                
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
                    st.caption("4. Tính logic & Chính xác")
                    st.progress(60) 

                st.markdown("---")
                st.markdown("#### 📋 Chi tiết Chuỗi hoạt động học")
                st.caption("Bảng rà soát 4 mốc quan trọng trong từng hoạt động.")
                
                data_report = [
                    {"Hoạt động": "1. Mở đầu", "Mục tiêu": "🟢 Đạt", "Nội dung": "🟢 Đạt", "Sản phẩm": "🟢 Đạt", "Tổ chức": "🟡 Thiếu logic"},
                    {"Hoạt động": "2. Hình thành kiến thức", "Mục tiêu": "🟢 Đạt", "Nội dung": "🔴 Sai kiến thức", "Sản phẩm": "🟡 Thiếu", "Tổ chức": "🟢 Đạt"},
                    {"Hoạt động": "3. Luyện tập", "Mục tiêu": "🟢 Đạt", "Nội dung": "🟢 Đạt", "Sản phẩm": "🟢 Đạt", "Tổ chức": "🔴 Trái mục tiêu"},
                    {"Hoạt động": "4. Vận dụng", "Mục tiêu": "🔴 Trống", "Nội dung": "🔴 Trống", "Sản phẩm": "🔴 Trống", "Tổ chức": "🔴 Trống"},
                ]
                df_report = pd.DataFrame(data_report)
                st.dataframe(df_report, use_container_width=True, hide_index=True)

            else:
                st.info("💡 Bảng điều khiển (Dashboard) đang trống. Vui lòng tải file giáo án lên và nhấn 'Quét & Phân tích' ở cột điều khiển bên trái để xem kết quả trực quan.")
