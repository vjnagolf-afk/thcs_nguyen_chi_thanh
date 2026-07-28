# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_quizizz.py
Nhiệm vụ: Trợ lý Tạo tệp Import Quizizz / Kahoot / Blooket & Mã nhúng tương tác.
Hỗ trợ đa nguồn: Nhập chủ đề, File (PDF/Word/Ảnh), YouTube, Trang web.
Hỗ trợ 4 định dạng câu hỏi: Trắc nghiệm, Trả lời ngắn, Đúng/Sai, Bài luận.
============================================================
"""

import io
import os
import logging
import streamlit as st
from PIL import Image
from docx import Document

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word của dự án
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2 để dùng Smart Router
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# ============================================================
# HÀM TRÍCH XUẤT TÀI LIỆU ĐA NGUỒN (PDF, DOCX, ẢNH)
# ============================================================
def extract_content_from_source(uploaded_file):
    """Trích xuất text hoặc hình ảnh từ file tài liệu người dùng tải lên."""
    if not uploaded_file:
        return "", []
    
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    extracted_text = ""
    images = []

    try:
        if file_name.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            img = Image.open(io.BytesIO(file_bytes))
            images.append(img)
            extracted_text = "[Học sinh/Giáo viên tải lên hình ảnh tài liệu]"
            
        elif file_name.endswith('.docx'):
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
                        img = Image.open(io.BytesIO(base_image["image"]))
                        images.append(img)
                    except: pass
            extracted_text = "\n".join(texts)

        elif file_name.endswith('.txt'):
            extracted_text = file_bytes.decode('utf-8', errors='ignore')

    except Exception as e:
        logger.error(f"Lỗi trích xuất file {file_name}: {e}")
        
    return extracted_text, images

def render_xd_quizizz(ai_engine_cu=None):
    if "quiz_result" not in st.session_state:
        st.session_state["quiz_result"] = None
    if "quiz_topic" not in st.session_state:
        st.session_state["quiz_topic"] = "Bo_Cau_Hoi"

    st.markdown("### ⚡ Trợ lý Tạo tệp Import Quizizz / Kahoot / Blooket & Tương tác")
    st.info("💡 **Góc chuyên gia:** Tạo bộ câu hỏi trắc nghiệm, trả lời ngắn, đúng/sai và tự luận từ đa nguồn (Chủ đề, Tệp PDF/Word/Ảnh, YouTube, Website). Đồng thời hỗ trợ **nhúng trực tiếp** giao diện phòng quiz tương tác ngay trong ứng dụng.")

    # TẠO 2 TAB CHÍNH
    tab_tao_de, tab_nhung = st.tabs([
        "🛠️ 1. Soạn thảo & Tạo bộ câu hỏi (AI Builder)", 
        "🌐 2. Mã nhúng Giao diện Tương tác Trực tiếp"
    ])

    # ========================================================
    # TAB 1: SOẠN THẢO & TẠO BỘ CÂU HỎI
    # ========================================================
    with tab_tao_de:
        with st.container(border=True):
            st.markdown("#### 🎯 Chọn phương thức nạp dữ liệu (Nguồn AI)")
            
            # 4 Nút lựa chọn nguồn dữ liệu chuẩn giao diện Quiz AI
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

        # XỬ LÝ GỌI AI TẠO QUIZ
        if btn_tao_quiz:
            if AIEngine2 is None:
                st.error("❌ Không tìm thấy file `utils/ai_engine_2.py`.")
                return

            if not input_data_content.strip() and not uploaded_file:
                st.warning("⚠️ Vui lòng cung cấp nội dung chủ đề hoặc tải lên tệp tài liệu.")
            else:
                with st.spinner("⏳ AI đang phân tích tài liệu và biên soạn bộ câu hỏi tương tác chuẩn Quizizz/Kahoot..."):
                    
                    types_str = ", ".join(do_ut_cau_hoi)
                    prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA BIÊN SOẠN CÂU HỎI TRẮC NGHIỆM VÀ ĐÁNH GIÁ NĂNG LỰC HỌC SINH.
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
- NẾU có công thức Toán/Lý/Hóa, BẮT BUỘC bọc trong dấu `$ ... $`. Cấm dùng backtick (`).
"""
                    try:
                        # Gọi AI (Hỗ trợ cả ảnh nếu có tệp hình ảnh tải lên)
                        engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                        
                        if extracted_images:
                            contents = [prompt] + extracted_images
                            if hasattr(engine_v2, "generate_multimodal"):
                                result = engine_v2.generate_multimodal(contents)
                            else:
                                result = engine_v2.generate_text(prompt)
                        else:
                            result = engine_v2.generate_text(prompt, temperature=0.7)
                        
                        if result.startswith("❌") or result.startswith("⚠️"):
                            st.error(result)
                        else:
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
                    
            if st.button("🔄 Tạo bộ câu hỏi mới", use_container_width=True):
                st.session_state["quiz_result"] = None
                st.rerun()

    # ========================================================
    # TAB 2: MÃ NHÚNG GIAO DIỆN TƯƠNG TÁC TRỰC TIẾP
    # ========================================================
    with tab_nhung:
        st.markdown("#### 🌐 Nhúng Phòng Tương tác Quiz Trực tiếp")
        st.info("💡 **Hướng dẫn:** Thầy/Cô có thể dán đoạn mã nhúng (iframe code) hoặc đường dẫn liên kết công khai (Public Link) của phòng Quiz đã tạo trên nền tảng (như Quizizz, Kahoot, Zep, v.v.) để hiển thị và tương tác trực tiếp ngay tại đây.")

        embed_input = st.text_input(
            "Dán Link liên kết hoặc Mã nhúng (Iframe / URL):",
            placeholder="VD: https://quiz.zep.us/vi/join hoặc dán <iframe src=...></iframe>"
        )

        # Xử lý bóc tách URL nếu người dùng dán nguyên đoạn mã iframe html
        target_url = ""
        if embed_input.strip():
            if "src=" in embed_input:
                try:
                    import re
                    match = re.search(r'src=["\'](.*?)["\']', embed_input)
                    if match:
                        target_url = match.group(1)
                except:
                    target_url = embed_input.strip()
            else:
                target_url = embed_input.strip()

        if target_url:
            st.markdown(f"##### 🖥️ Đang hiển thị khung tương tác từ nguồn:")
            st.caption(target_url)
            try:
                st.components.v1.iframe(target_url, height=600, scrolling=True)
            except Exception as e:
                st.error(f"Không thể nhúng trang web này do chính sách bảo mật X-Frame-Options của bên thứ ba: {e}")
                st.markdown(f"[🔗 Bấm vào đây để mở trực tiếp trong tab mới]({target_url})", unsafe_allow_html=True)
        else:
            st.markdown("""
            > **Gợi ý sử dụng:**
            > 1. Truy cập vào trang web tạo Quiz của thầy (VD: `https://quiz.zep.us` hoặc `Quizizz`).
            > 2. Chọn tính năng **Chia sẻ (Share)** hoặc **Nhúng (Embed)** để lấy đường dẫn URL phòng học/bộ câu hỏi.
            > 3. Dán vào ô trống phía trên để học sinh hoặc giáo viên có thể thao tác trực tiếp trên giao diện Streamlit này mà không cần chuyển tab!
            """)
