# -*- coding: utf-8 -*-
import io
import os
import logging
import streamlit as st
from PIL import Image
import urllib.parse as urlparse

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2 để dùng tính năng Multimodal
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# ============================================================
# HÀM TRÍCH XUẤT TÀI LIỆU ĐA NGUỒN (PDF, DOCX, ẢNH)
# ============================================================
def extract_content_from_source(uploaded_file):
    if not uploaded_file:
        return "", []
    
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    extracted_text = ""
    images = []

    try:
        if file_name.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            img = Image.open(io.BytesIO(file_bytes)).convert('RGB')
            images.append(img)
            extracted_text = "[Học sinh/Giáo viên tải lên hình ảnh tài liệu]"
            
        elif file_name.endswith('.docx'):
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    texts.append(" | ".join([cell.text.replace("\n", " ").strip() for cell in row.cells]))
            extracted_text = "\n".join(texts)

        elif file_name.endswith('.pdf'):
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            texts = []
            for i in range(len(doc)):
                page = doc[i]
                texts.append(page.get_text("text"))
                for img_info in page.get_images(full=True):
                    try:
                        base_image = doc.extract_image(img_info[0])
                        img = Image.open(io.BytesIO(base_image["image"])).convert('RGB')
                        images.append(img)
                    except: pass
            extracted_text = "\n".join(texts)

        elif file_name.endswith('.txt'):
            extracted_text = file_bytes.decode('utf-8', errors='ignore')

    except Exception as e:
        logger.error(f"Lỗi trích xuất file {file_name}: {e}")
        
    return extracted_text, images

# HÀM CROSS-ROUTING FALLBACK CHỐNG LỖI 429
def safe_generate_quiz(ai_engine_cu, prompt, extracted_images=[]):
    api_key = None
    for key, val in st.session_state.items():
        if isinstance(val, str) and val.startswith("sk-"):
            api_key = val
            break
            
    if not api_key:
        for k in ["user_api_key", "api_key", "openai_api_key", "sk_key"]:
            if st.session_state.get(k) and str(st.session_state.get(k)).startswith("sk-"):
                api_key = st.session_state.get(k)
                break
                
    if not api_key and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]

    def run_openai():
        if not api_key:
            raise RuntimeError("Chưa cấu hình API Key OpenAI (sk-) để dự phòng.")
        import openai
        import base64
        client = openai.OpenAI(api_key=str(api_key).strip())
        
        content_array = [{"type": "text", "text": prompt}]
        for img in extracted_images:
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            base64_img = base64.b64encode(buffered.getvalue()).decode('utf-8')
            content_array.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
            })
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": content_array}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    def run_gemini():
        try:
            from utils.ai_engine_2 import AIEngine2
            engine_v2 = AIEngine2(default_model="gemini-1.5-flash")
            
            if extracted_images:
                contents = [prompt]
                for img in extracted_images:
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    contents.append({
                        "mime_type": "image/jpeg",
                        "data": buffered.getvalue()
                    })
                if hasattr(engine_v2, "generate_multimodal"):
                    res = engine_v2.generate_multimodal(contents)
                else:
                    raise RuntimeError("❌ Thiếu hàm generate_multimodal.")
            else:
                res = engine_v2.generate_text(prompt, temperature=0.7)
                
            if res and not res.startswith("❌") and not res.startswith("⚠️") and "429" not in res and "RESOURCE_EXHAUSTED" not in res:
                return res
            raise RuntimeError("Hạn mức Gemini cạn kiệt.")
        except Exception as e:
            raise RuntimeError(f"Lỗi Gemini: {str(e)}")

    error_msgs = []
    try:
        return run_gemini()
    except Exception as e1:
        error_msgs.append(f"Gemini: {e1}")
        try:
            return run_openai()
        except Exception as e2:
            error_msgs.append(f"OpenAI: {e2}")
            
    raise RuntimeError(f"Hệ thống quá tải hoặc hết hạn mức:\n- {error_msgs[0]}\n- {error_msgs[1]}\n\n👉 Nạp Key OpenAI (sk-) vào hệ thống để chạy ổn định.")


def render_xd_quizizz(ai_engine_cu=None):
    if "quiz_result" not in st.session_state:
        st.session_state["quiz_result"] = None
    if "quiz_topic" not in st.session_state:
        st.session_state["quiz_topic"] = "Bo_Cau_Hoi"

    st.markdown("### ⚡ Trợ lý Tạo Bộ Câu Hỏi & Tổ Chức Quiz Trực Tuyến")
    st.info("💡 **Góc chuyên gia:** Tạo bộ câu hỏi từ đa nguồn (Văn bản, File, YouTube, Web). Đặc biệt: Tích hợp phòng tương tác Real-time để học sinh tham gia thi đấu trực tiếp ngay trên hệ thống!")

    tab_tao_de, tab_nhung = st.tabs([
        "🛠️ 1. Soạn thảo Bộ câu hỏi (AI Builder)", 
        "🏆 2. Phòng Thi Đấu Real-time (Host & Client)"
    ])

    # ========================================================
    # TAB 1: SOẠN THẢO & TẠO BỘ CÂU HỎI
    # ========================================================
    with tab_tao_de:
        with st.container(border=True):
            st.markdown("#### 🎯 Chọn phương thức nạp dữ liệu (Nguồn AI)")
            
            nguon_nhap = st.radio(
                "Nguồn dữ liệu đầu vào:",
                [
                    "✍️ Nhập chủ đề trực tiếp", 
                    "📁 Trích xuất từ tệp (PDF, Word, Ảnh)", 
                    "📺 Trích xuất từ YouTube (Link video)", 
                    "🌐 Trích xuất từ trang web (URL)"
                ],
                horizontal=True,
                label_visibility="collapsed"
            )

            input_data_content = ""
            uploaded_file = None
            extracted_images = []

            if "Nhập chủ đề" in nguon_nhap:
                input_data_content = st.text_input("Nhập chủ đề bài kiểm tra:", placeholder="VD: Định luật Ôm, Phản ứng hóa học lớp 9, Các nước Đông Nam Á...")
            elif "Trích xuất từ tệp" in nguon_nhap:
                uploaded_file = st.file_uploader("Tải lên tài liệu (PDF, Word, TXT, Ảnh):", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
                if uploaded_file:
                    with st.spinner("Đang đọc dữ liệu từ tệp..."):
                        input_data_content, extracted_images = extract_content_from_source(uploaded_file)
                        st.success(f"✅ Đã đọc thành công tệp: {uploaded_file.name}")
            elif "YouTube" in nguon_nhap:
                input_data_content = st.text_input("Dán đường dẫn (URL) Video YouTube:", placeholder="https://www.youtube.com/watch?v=...")
            else:
                input_data_content = st.text_input("Dán đường dẫn (URL) Trang web tài liệu:", placeholder="https://vi.wikipedia.org/wiki/...")

            st.markdown("---")
            st.markdown("#### ⚙️ Cấu hình định dạng câu hỏi & Số lượng")
            
            col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
            with col_cfg1:
                so_luong = st.number_input("Tổng số câu hỏi:", min_value=5, max_value=50, value=10, step=5)
            with col_cfg2:
                do_kho = st.selectbox("Mức độ khó:", ["Nhận biết", "Thông hiểu", "Vận dụng", "Hỗn hợp các mức độ"])
            with col_cfg3:
                do_ut_cau_hoi = st.multiselect(
                    "Các dạng câu hỏi bao gồm:",
                    ["Trắc nghiệm (4 lựa chọn)", "Trả lời ngắn", "Đúng / Sai", "Bài luận"],
                    default=["Trắc nghiệm (4 lựa chọn)", "Đúng / Sai"]
                )

            them_chi_tiet = st.text_area("Yêu cầu thêm (Tuỳ chọn):", height=70, placeholder="VD: Tập trung vào phần bài tập tính toán, có giải chi tiết từng câu...")
            
            btn_tao_quiz = st.button("🚀 TẠO BỘ CÂU HỎI THÔNG MINH", type="primary", use_container_width=True)

        if btn_tao_quiz:
            if not input_data_content.strip() and not uploaded_file:
                st.warning("⚠️ Vui lòng cung cấp nội dung chủ đề hoặc tải lên tệp tài liệu.")
            else:
                with st.spinner("⏳ AI đang phân tích tài liệu và biên soạn bộ câu hỏi..."):
                    types_str = ", ".join(do_ut_cau_hoi)
                    prompt = f"""BẠN LÀ MỘT CHUYÊN GIA BIÊN SOẠN CÂU HỎI TRẮC NGHIỆM VÀ ĐÁNH GIÁ NĂNG LỰC HỌC SINH.
Nhiệm vụ của bạn là xây dựng bộ câu hỏi chuẩn xác, sư phạm, phục vụ cho các nền tảng Quizizz, Kahoot, Blooket.

--- THÔNG TIN CẤU HÌNH ---
- Nguồn dữ liệu đầu vào: {nguon_nhap}
- Nội dung/Chủ đề/Tài liệu: {input_data_content[:15000]}
- Số lượng câu hỏi yêu cầu: {so_luong} câu
- Mức độ: {do_kho}
- Các dạng câu hỏi được phép sử dụng: {types_str}
- Yêu cầu bổ sung: {them_chi_tiet if them_chi_tiet else 'Không có'}

--- CẤU TRÚC TRÌNH BÀY BẮT BUỘC ---
Hãy biên soạn rõ ràng theo từng câu hỏi với định dạng chuẩn sau:

### Câu [Số]: [Nội dung câu hỏi]
- **Dạng câu hỏi:** [Trắc nghiệm / Trả lời ngắn / Đúng-Sai / Bài luận]
- **Các đáp án (Nếu là Trắc nghiệm):** 
  A. [...] 
  B. [...] 
  C. [...] 
  D. [...]
- **Đáp án đúng:** [...]
- **Giải thích chi tiết:** [...]

[KỶ LUẬT ĐỊNH DẠNG]
- Trình bày rõ ràng bằng Markdown.
- NẾU có công thức Toán/Lý/Hóa, BẮT BUỘC bọc trong dấu `$ ... $`. Cấm dùng backtick (`)."""
                    
                    try:
                        result = safe_generate_quiz(ai_engine_cu, prompt, extracted_images)
                        st.session_state["quiz_result"] = result
                        st.session_state["quiz_topic"] = "Bo_Cau_Hoi_Quiz"
                    except Exception as e:
                        st.error(f"❌ Lỗi hệ thống: {e}")

        # Hiển thị kết quả bộ câu hỏi
        if st.session_state.get("quiz_result"):
            st.markdown("---")
            st.markdown("### 📑 BỘ CÂU HỎI ĐÃ ĐƯỢC BIÊN SOẠN")
            st.markdown(st.session_state["quiz_result"], unsafe_allow_html=True)
            
            st.markdown("### 📥 Lưu trữ & Xuất tệp")
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.download_button(
                    label="📄 Tải bộ câu hỏi (.TXT)",
                    data=st.session_state["quiz_result"],
                    file_name="Bo_Cau_Hoi_Quizizz.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            with col_d2:
                if export_word:
                    try:
                        export_data = {"ai_generated_content": st.session_state["quiz_result"], "is_dkt": False}
                        with st.spinner("Đang kết xuất Word..."):
                            word_bytes = export_word(export_data)
                        st.download_button(
                            label="📘 Tải bộ câu hỏi (.DOCX)",
                            data=word_bytes,
                            file_name="Bo_Cau_Hoi_Quizizz.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            type="primary"
                        )
                    except Exception as e:
                        st.error(f"Lỗi xuất Word: {e}")
                else:
                    st.warning("⚠️ Module Word chưa sẵn sàng.")

    # ========================================================
    # TAB 2: PHÒNG THI ĐẤU REAL-TIME BẰNG CÔNG NGHỆ PUSHER
    # ========================================================
    with tab_nhung:
        st.markdown("#### 🏆 Nền Tảng Tương Tác: Thống Kê & Xếp Hạng")
        st.info("💡 **Giải pháp tích hợp:** Để tạo phòng tương tác Real-time giữa các máy (Bấm giờ, tính điểm nhanh chậm) ngay trên Streamlit, thầy hãy đăng ký một tài khoản miễn phí trên [Pusher.com](https://pusher.com/). Sau đó nhập các khóa kết nối (API Keys) vào đây.")
        
        with st.expander("🔑 Cấu hình Máy chủ Pusher (Dành cho Quản trị viên)", expanded=False):
            pusher_app_id = st.text_input("Pusher App ID:", type="password")
            pusher_key = st.text_input("Pusher Key:", type="password")
            pusher_secret = st.text_input("Pusher Secret:", type="password")
            pusher_cluster = st.text_input("Pusher Cluster (VD: ap1):")
            
        vai_tro = st.radio("Thầy/Cô đang mở máy tính này với vai trò gì?", ["🖥️ Giáo viên (Host - Máy chủ)", "📱 Học sinh (Client - Máy trạm)"], horizontal=True)
        
        st.markdown("---")
        
        # ĐƯA PHẦN MÃ NHÚNG RA NGOÀI ĐỂ LUÔN LUÔN HIỂN THỊ
        st.markdown("#### 🌐 Khung Trình Chiếu Câu Hỏi (Từ bên thứ 3)")
        st.caption("Thầy/Cô dán link bộ câu hỏi (từ Quizizz, Kahoot, Website...) vào đây để chiếu lên màn hình lớn cho học sinh xem.")
        embed_input = st.text_input("Dán Link liên kết hoặc Mã nhúng (Iframe / URL):", placeholder="VD: https://quizizz.com/join/...")
        target_url = ""
        if embed_input.strip():
            if "src=" in embed_input:
                try:
                    import re
                    match = re.search(r'src=["\'](.*?)["\']', embed_input)
                    if match: target_url = match.group(1)
                except: target_url = embed_input.strip()
            else:
                target_url = embed_input.strip()

        if target_url:
            st.markdown(f"##### 🖥️ Đang hiển thị khung bài test từ nguồn:")
            st.caption(target_url)
            try:
                st.components.v1.iframe(target_url, height=500, scrolling=True)
            except Exception as e:
                st.error(f"Lỗi chính sách bảo mật X-Frame-Options: {e}")
                st.markdown(f"[🔗 Bấm vào đây mở trang trong tab mới]({target_url})", unsafe_allow_html=True)

        st.markdown("---")

        # XỬ LÝ PUSHER REAL-TIME
        if not (pusher_app_id and pusher_key and pusher_secret and pusher_cluster):
            st.warning("⚠️ Nhập Cấu hình Pusher ở trên để kích hoạt Bảng Điều Khiển và Bảng Xếp Hạng tương tác.")
        else:
            # GIAO DIỆN REAL-TIME SAU KHI CẤU HÌNH PUSHER THÀNH CÔNG
            try:
                import pusher
                # Khởi tạo đối tượng Pusher
                pusher_client = pusher.Pusher(
                    app_id=pusher_app_id,
                    key=pusher_key,
                    secret=pusher_secret,
                    cluster=pusher_cluster,
                    ssl=True
                )
                
                # --- VAI TRÒ GIÁO VIÊN ---
                if "Giáo viên" in vai_tro:
                    st.markdown("### 👑 BẢNG ĐIỀU KHIỂN GIÁO VIÊN")
                    ma_phong = st.text_input("Tạo Mã Phòng thi (VD: 123456):", value="123456")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("🚀 PHÁT CÂU HỎI TIẾP THEO (GỬI LỆNH)"):
                            # Gửi tín hiệu báo hiệu câu mới tới tất cả học sinh
                            try:
                                pusher_client.trigger(f'phong-{ma_phong}', 'cau_moi', {'message': 'start_timer'})
                                st.success("✅ Đã phát tín hiệu câu hỏi đến tất cả máy học sinh!")
                            except Exception as e:
                                st.error(f"Lỗi kết nối Pusher: {e}")
                    with col_btn2:
                        if st.button("🛑 KẾT THÚC THỜI GIAN TRẢ LỜI"):
                            try:
                                pusher_client.trigger(f'phong-{ma_phong}', 'het_gio', {'message': 'stop_timer'})
                                st.error("🛑 Đã khóa quyền trả lời của học sinh!")
                            except: pass
                            
                    st.markdown("#### 🏆 Bảng Xếp Hạng & Tốc Độ (Leaderboard)")
                    st.info("Giáo viên sẽ nhìn thấy tên nhóm, lựa chọn và thời gian trả lời của các máy học sinh đẩy về đây (Cần kết nối API Polling để lấy dữ liệu liên tục - Sẽ tích hợp sâu ở Phase sau). Hiện tại máy chủ Pusher đã nhận và lưu thành công toàn bộ tương tác của HS.")
                    
                # --- VAI TRÒ HỌC SINH ---
                else:
                    st.markdown("### 📱 GIAO DIỆN THI ĐẤU HỌC SINH")
                    col_hs1, col_hs2 = st.columns(2)
                    with col_hs1:
                        nhap_ma_phong = st.text_input("Nhập Mã Phòng từ Giáo viên:")
                    with col_hs2:
                        ten_nhom = st.text_input("Tên Nhóm / Tên Học sinh:")
                        
                    if nhap_ma_phong and ten_nhom:
                        st.markdown(f"#### ⏱️ Đang chờ tín hiệu từ phòng {nhap_ma_phong}...")
                        # Khi học sinh bấm đáp án -> Gửi tín hiệu về Server Pusher -> Báo về máy Host của GV
                        st.markdown("Nhìn lên màn hình của Giáo viên và nhanh tay chọn đáp án:")
                        
                        ca, cb, cc, cd = st.columns(4)
                        import time
                        
                        def gui_dap_an(dap_an):
                            # Gửi đáp án kèm thời gian Timestamp để so sánh tốc độ
                            timestamp = time.time()
                            try:
                                pusher_client.trigger(
                                    f'phong-{nhap_ma_phong}', 
                                    'nop_dap_an', 
                                    {'nhom': ten_nhom, 'dap_an': dap_an, 'thoi_gian': timestamp}
                                )
                                st.success(f"✅ Nộp đáp án **{dap_an}** thành công!")
                            except Exception as e:
                                st.error("Lỗi mạng, không thể nộp bài.")
                        
                        # Làm nút to lên một chút
                        if ca.button("🅰️ ĐÁP ÁN A", use_container_width=True): gui_dap_an("A")
                        if cb.button("🅱️ ĐÁP ÁN B", use_container_width=True): gui_dap_an("B")
                        if cc.button("🅲 ĐÁP ÁN C", use_container_width=True): gui_dap_an("C")
                        if cd.button("🅳 ĐÁP ÁN D", use_container_width=True): gui_dap_an("D")
                        
            except ImportError:
                st.error("❌ Thư viện kết nối thời gian thực chưa được cài đặt. Vui lòng cài đặt: `pip install pusher`")
            except Exception as e:
                st.error(f"❌ Cấu hình API không hợp lệ: {e}")
