import streamlit as st
from docxtpl import DocxTemplate
import io
import json
import pypdf  # Cập nhật từ PyPDF2 sang pypdf chuẩn theo requirements
import os
import re
from loguru import logger

def clean_ai_json(response_text):
    """Trích xuất khối JSON sạch từ phản hồi của AI bằng Regex"""
    try:
        match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if match:
            return match.group(1).strip()
        match_braces = re.search(r'(\{[\s\S]*\})', response_text)
        if match_braces:
            return match_braces.group(1).strip()
        return response_text.strip()
    except Exception as e:
        logger.error(f"Lỗi làm sạch JSON: {e}")
        return response_text

def render_xd_khbd(ai_engine):
    st.markdown("### 📝 Xây dựng Kế hoạch bài dạy (AI Hỗ trợ)")

    if "khbd_docx" not in st.session_state:
        st.session_state.khbd_docx = None
    if "khbd_filename" not in st.session_state:
        st.session_state.khbd_filename = ""

    # Giao diện nhập liệu nhanh
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mon_hoc = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Khoa học Tự nhiên", "Tiếng Anh", "Tin học", "Công nghệ"])
    with col2:
        lop = st.selectbox("Lớp", [str(i) for i in range(6, 13)], index=3)
    with col3:
        hinh_thuc = st.selectbox("Chọn hình thức", ["Chuẩn 5512", "KHBD thu gọn", "KHBD Stem"])
    with col4:
        thoi_luong = st.number_input("Số tiết", min_value=1, value=1)

    ten_bai = st.text_input("Tên bài dạy / Chủ đề", placeholder="Ví dụ: Câu cá mùa thu, Câu lệnh lặp...")
    loai_ai = st.selectbox("🤖 Phiên bản AI", ["Flash (Nhanh, Mặc định)", "Pro (Thông minh, Suy luận sâu)"])
    
    model_chon = None
    if ai_engine:
        model_chon = ai_engine.MODELS["flash"] if "Flash" in loai_ai else ai_engine.MODELS["pro"]

    file_tai_len = st.file_uploader("Tài liệu tham khảo (PDF, TXT)", type=["pdf", "txt"])
    bam_sat = st.checkbox("Bám sát nội dung file tải lên", value=False)
    yeu_cau_them = st.text_area("Yêu cầu bổ sung")

    tao_btn = st.button("🚀 Soạn KHBD", type="primary", use_container_width=True)

    if tao_btn:
        if not ten_bai:
            st.warning("Vui lòng nhập tên bài dạy!")
        elif not ai_engine or not model_chon:
            st.error("🔐 AI chưa kết nối!")
        else:
            with st.spinner("🤖 AI đang biên soạn giáo án..."):
                try:
                    # 1. Đọc file bằng thư viện pypdf mới
                    noi_dung_tham_khao = ""
                    if bam_sat and file_tai_len:
                        if file_tai_len.name.endswith('.pdf'):
                            # Cú pháp PdfReader viết thường của pypdf >= 5.0.0
                            reader = pypdf.PdfReader(file_tai_len)
                            for page in reader.pages:
                                text = page.extract_text()
                                if text: 
                                    noi_dung_tham_khao += text + "\n"
                                if len(noi_dung_tham_khao) > 15000: 
                                    break
                        elif file_tai_len.name.endswith('.txt'):
                            noi_dung_tham_khao = file_tai_len.read().decode("utf-8")[:15000]
                        
                        noi_dung_tham_khao = f"\n[TÀI LIỆU THAM KHẢO]:\n{noi_dung_tham_khao}"

                    # 2. Cấu trúc JSON giả định theo file KHBD_Mau.docx
                    json_structure = {
                        "ten_bai": ten_bai,
                        "mon_hoc": mon_hoc,
                        "lop": lop,
                        "thoi_luong": f"{thoi_luong} tiết",
                        "hinh_thuc": hinh_thuc,
                        "muc_tieu": {
                            "kien_thuc": "Các kiến thức trọng tâm bài học...",
                            "nang_luc": "Năng lực đặc thù môn học và năng lực chung...",
                            "pham_chat": "Các phẩm chất cần khơi gợi..."
                        },
                        "thiet_bi": "Thiết bị dạy học và học liệu sử dụng...",
                        "tien_trinh": [
                            {
                                "ten_hoat_dong": "Hoạt động 1: Xác định vấn đề/Nhiệm vụ học tập (Khởi động)",
                                "muc_tieu_hd": "Mục tiêu cụ thể của hoạt động...",
                                "noi_dung": "Nội dung giáo viên giao cho học sinh...",
                                "san_pham": "Sản phẩm dự kiến học sinh phải hoàn thành...",
                                "to_chuc": "Các bước tổ chức thực hiện (Chuyển giao - Thực hiện - Báo cáo - Kết luận)..."
                            }
                        ]
                    }

                    # 3. Prompt Engineering
                    prompt = f"""
                    Bạn là Chuyên gia Giáo dục thuộc Hệ sinh thái THCS Nguyễn Chí Thanh.
                    Hãy biên soạn Kế hoạch bài dạy chi tiết dựa trên thông tin sau:
                    - Môn: {mon_hoc} | Lớp: {lop} | Thời lượng: {thoi_luong} tiết.
                    - Tên bài: {ten_bai}
                    - Khung cấu trúc hình thức: {hinh_thuc}
                    - Yêu cầu thêm từ giáo viên: {yeu_cau_them if yeu_cau_them else "Chuẩn hóa theo đổi mới phương pháp dạy học."}
                    {noi_dung_tham_khao}

                    BẮT BUỘC TRẢ VỀ JSON theo đúng định dạng mẫu dưới đây (giữ nguyên tên các key để map vào Word template):
                    {json.dumps(json_structure, ensure_ascii=False)}
                    Chỉ trả về chuỗi JSON hợp lệ, không kèm lời thoại giải thích trước hoặc sau khối mã.
                    """

                    # 4. Gọi xử lý text từ AI Engine của bạn
                    response = ai_engine.generate_text(prompt, model_name=model_chon)
                    clean_json = clean_ai_json(response)
                    data_dict = json.loads(clean_json)

                    # 5. Đọc và Render Word Template bằng docxtpl
                    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates", "KHBD_Mau.docx")
                    if not os.path.exists(template_path):
                        st.error("Không tìm thấy file mẫu 'KHBD_Mau.docx' trong thư mục templates!")
                        return

                    doc = DocxTemplate(template_path)
                    doc.render(data_dict)
                    
                    # 6. Đóng gói lưu vào bộ nhớ tạm Session State
                    bio = io.BytesIO()
                    doc.save(bio)
                    st.session_state.khbd_docx = bio.getvalue()
                    st.session_state.khbd_filename = f"KHBD_{mon_hoc}_{lop}_{ten_bai.replace(' ', '_')}.docx"
                    
                    st.success("🎉 Đã biên soạn xong Kế hoạch bài dạy!")
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("Lỗi: AI phản hồi sai định dạng cấu trúc dữ liệu. Vui lòng thử bấm lại nút Soạn.")
                    logger.error(f"Lỗi phân tách JSON. Chuỗi gốc: {response}")
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi hệ thống: {e}")
                    logger.exception("Lỗi sinh KHBD")

    # Hiển thị khu vực tải file ở cuối trang sau khi UI Reload
    if st.session_state.khbd_docx:
        st.markdown("---")
        st.download_button(
            label="📥 Tải giáo án bản Word (.docx)", 
            data=st.session_state.khbd_docx, 
            file_name=st.session_state.khbd_filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
