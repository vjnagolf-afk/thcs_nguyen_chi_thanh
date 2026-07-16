import streamlit as st
from docxtpl import DocxTemplate
import io
import json
import PyPDF2
import os
import re
from loguru import logger

def clean_ai_json(response_text):
    """Trích xuất khối JSON sạch từ phản hồi của AI bằng Regex"""
    try:
        # Tìm khối nằm giữa ```json và ```
        match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if match:
            return match.group(1).strip()
        # Nếu không có khối markdown, tìm cặp dấu ngoặc nhọn đầu tiên và cuối cùng
        match_braces = re.search(r'(\{[\s\S]*\})', response_text)
        if match_braces:
            return match_braces.group(1).strip()
        return response_text.strip()
    except Exception as e:
        logger.error(f"Lỗi làm sạch JSON: {e}")
        return response_text

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    # Khởi tạo session state sạch sẽ
    if "khbd_docx" not in st.session_state:
        st.session_state.khbd_docx = None
    if "khbd_filename" not in st.session_state:
        st.session_state.khbd_filename = ""

    # 1. Giao diện cấu hình cấu trúc nhập liệu
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học Tự nhiên", "Tiếng Anh", "Tin học", "Công nghệ"])
    with col2:
        lop = st.selectbox("Lớp", [str(i) for i in range(6, 13)], index=3)
    with col3:
        hinh_thuc = st.selectbox("Chọn hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    with col4:
        thoi_luong = st.number_input("Số tiết", min_value=1, value=1)

    ten_bai = st.text_input("Tên bài dạy / Chủ đề", placeholder="Ví dụ: Phương trình bậc hai, Chí Phèo...")
    loai_ai = st.selectbox("🤖 Phiên bản AI", ["Flash (Nhanh, Mặc định)", "Pro (Thông minh, Suy luận sâu)"])
    
    model_chon = None
    if ai_engine:
        model_chon = ai_engine.MODELS["flash"] if "Flash" in loai_ai else ai_engine.MODELS["pro"]

    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=False)
    yeu_cau_them = st.text_area("Yêu cầu bổ sung", placeholder="Ví dụ: Thêm hoạt động trò chơi khởi động, tập trung phát triển năng lực tự học...")

    # Khu vực xử lý logic hành động
    tao_btn = st.button("🚀 Soạn KHBD", type="primary", use_container_width=True)

    if tao_btn:
        if not ten_bai:
            st.warning("Vui lòng nhập tên bài dạy!")
        elif not ai_engine or not model_chon:
            st.error("🔐 AI chưa kết nối! Vui lòng kiểm tra lại API Key.")
        else:
            with st.spinner("🤖 AI đang biên soạn và đóng gói file Word..."):
                try:
                    # 1. Xử lý file nâng cao (Tăng giới hạn ký tự lên 15,000 ~ 5-7 trang)
                    noi_dung_tham_khao = ""
                    if bam_sat and file_tai_len:
                        if file_tai_len.name.endswith('.pdf'):
                            reader = PyPDF2.PdfReader(file_tai_len)
                            for page in reader.pages:
                                text = page.extract_text()
                                if text: 
                                    noi_dung_tham_khao += text + "\n"
                                if len(noi_dung_tham_khao) > 15000: 
                                    break
                        elif file_tai_len.name.endswith('.txt'):
                            noi_dung_tham_khao = file_tai_len.read().decode("utf-8")[:15000]
                        
                        noi_dung_tham_khao = f"\n[TÀI LIỆU THAM KHẢO]:\n{noi_dung_tham_khao}"

                    # 2. Định nghĩa cấu trúc JSON mẫu gửi cho AI để ép format (Sửa theo các tag trong KHBD_Mau.docx của bạn)
                    json_structure = {
                        "ten_bai": ten_bai,
                        "mon_hoc": mon_hoc,
                        "lop": lop,
                        "thoi_luong": f"{thoi_luong} tiết",
                        "muc_tieu": {"kien_thuc": "...", "nang_luc": "...", "pham_chat": "..."},
                        "thiet_bi": "...",
                        "tien_trinh": [{"hoat_dong": "Khởi động", "muc_tieu_hd": "...", "noi_dung": "...", "san_pham": "...", "to_chuc": "..."}]
                    }

                    # 3. Kỹ thuật Prompt Engineering tối ưu
                    prompt = f"""
                    Bạn là một chuyên gia giáo dục. Hãy soạn Kế hoạch bài dạy (Giáo án) theo các thông tin sau:
                    - Môn học: {mon_hoc}
                    - Lớp: {lop}
                    - Tên bài: {ten_bai}
                    - Thời lượng: {thoi_luong} tiết
                    - Hình thức: {hinh_thuc}
                    - Yêu cầu đặc biệt: {yeu_cau_them if yeu_cau_them else "Theo chuẩn khung chương trình mới."}
                    {noi_dung_tham_khao}

                    YÊU CẦU BẮT BUỘC: 
                    Trả về dữ liệu dưới dạng JSON thuần túy khớp chính xác với cấu trúc key này để fill vào file Word:
                    {json.dumps(json_structure, ensure_ascii=False)}
                    Không giải thích gì thêm ngoài chuỗi JSON.
                    """

                    # 4. Gọi AI và bóc tách dữ liệu an toàn
                    response = ai_engine.generate_text(prompt, model_name=model_chon)
                    clean_json = clean_ai_json(response)
                    data_dict = json.loads(clean_json)

                    # 5. Khởi tạo và Render Word template
                    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates", "KHBD_Mau.docx")
                    if not os.path.exists(template_path):
                        st.error("Không tìm thấy file template KHBD_Mau.docx!")
                        return

                    doc = DocxTemplate(template_path)
                    doc.render(data_dict)
                    
                    # 6. Ghi vào bộ nhớ tạm session_state
                    bio = io.BytesIO()
                    doc.save(bio)
                    st.session_state.khbd_docx = bio.getvalue()
                    st.session_state.khbd_filename = f"KHBD_{ten_bai.replace(' ', '_')}.docx"
                    
                    st.success("🎉 Biên soạn thành công! Nhấp nút bên dưới để tải về.")
                    st.rerun()
                    
                except json.JSONDecodeError as json_err:
                    st.error("Lỗi cấu trúc phản hồi từ AI. Hãy thử bấm 'Soạn KHBD' lại lần nữa.")
                    logger.error(f"JSON Error. Raw Response: {response}")
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
                    logger.exception("Lỗi sinh KHBD")

    # Đưa nút Tải file xuống dưới cùng để cải thiện trải nghiệm người dùng (UX)
    if st.session_state.khbd_docx:
        st.markdown("---")
        st.download_button(
            label="📥 Tải file Giáo án (Word)", 
            data=st.session_state.khbd_docx, 
            file_name=st.session_state.khbd_filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
