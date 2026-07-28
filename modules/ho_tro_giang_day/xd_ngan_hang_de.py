# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_ngan_hang_de.py
Nhiệm vụ: Trợ lý Tạo Ngân hàng Câu hỏi.
Chức năng: Sinh bộ câu hỏi nhanh từ tài liệu (có tùy chọn bám sát 100%) 
hoặc AI tự sinh dựa trên chủ đề mà không cần ma trận đặc tả.
============================================================
"""

import io
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word của dự án
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# Hàm đọc nội dung từ file
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
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_text = "\n".join([page.get_text("text") for page in doc])
        elif file_name.endswith(('.txt', '.md')):
            extracted_text = file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Lỗi đọc file: {e}")
        st.error(f"Không thể đọc file. Vui lòng kiểm tra định dạng.")
    return extracted_text

def render_xd_ngan_hang_de(ai_engine_cu=None):
    if "nhd_result" not in st.session_state:
        st.session_state["nhd_result"] = None
    if "nhd_topic" not in st.session_state:
        st.session_state["nhd_topic"] = "Ngan_Hang_De"

    st.markdown("### 🏦 Trợ lý Xây dựng Ngân Hàng Đề")
    st.info("💡 **Góc chuyên gia:** Tạo nhanh bộ câu hỏi ôn tập, kiểm tra (Trắc nghiệm, Tự luận, Đúng/Sai) mà không cần cấu trúc ma trận phức tạp. AI có thể tự nghĩ ra câu hỏi theo chủ đề, hoặc bám sát tuyệt đối vào tài liệu thầy/cô tải lên.")

    with st.container(border=True):
        st.markdown("#### 1️⃣ Cấu hình Nội dung (Tùy chọn)")
        
        chu_de = st.text_input("Chủ đề cốt lõi / Môn học:", placeholder="VD: Lịch sử 12 - Chiến dịch Điện Biên Phủ, Toán 9 - Hàm số bậc 2...")
        
        c1, c2 = st.columns(2)
        with c1:
            van_ban = st.text_area("Dán nội dung Đề cương/Tài liệu:", height=100, placeholder="Dán văn bản kiến thức vào đây (nếu có)...")
        with c2:
            uploaded_file = st.file_uploader("Hoặc tải lên File tài liệu (PDF, Word, TXT):", type=["pdf", "docx", "txt"])
            
        # NÚT GẠT QUAN TRỌNG
        bam_sat_100 = st.checkbox("🎯 Bám sát 100% tài liệu tải lên (Tuyệt đối không dùng kiến thức bên ngoài)", value=True, help="Nếu bật, AI sẽ chỉ ra câu hỏi có đáp án nằm trực tiếp trong văn bản của Thầy/Cô cung cấp.")

        st.markdown("---")
        st.markdown("#### 2️⃣ Cấu trúc Ngân hàng câu hỏi")
        
        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        with col_cfg1:
            so_luong_tn = st.number_input("Số câu Trắc nghiệm (4 đáp án):", min_value=0, max_value=50, value=10)
        with col_cfg2:
            so_luong_ds = st.number_input("Số câu Đúng/Sai:", min_value=0, max_value=50, value=0)
        with col_cfg3:
            so_luong_tl = st.number_input("Số câu Tự luận / Trả lời ngắn:", min_value=0, max_value=20, value=2)
            
        muc_do = st.selectbox("Mức độ câu hỏi:", ["Hỗn hợp mọi mức độ", "Chủ yếu Nhận biết - Thông hiểu (Dễ)", "Chủ yếu Vận dụng - Vận dụng cao (Khó)"])
        yeu_cau_them = st.text_input("Yêu cầu thêm:", placeholder="VD: Phải có giải thích chi tiết cho từng câu, tập trung vào bài tập tính toán...")

        btn_tao = st.button("🪄 TẠO NGÂN HÀNG ĐỀ NGAY", type="primary", use_container_width=True)

    # ========================================================
    # XỬ LÝ GỌI AI
    # ========================================================
    if btn_tao:
        if AIEngine2 is None:
            st.error("❌ Không tìm thấy hệ thống AIEngine2.")
            return

        if not chu_de.strip() and not van_ban.strip() and not uploaded_file:
            st.warning("⚠️ Vui lòng nhập Chủ đề hoặc cung cấp Tài liệu để AI có căn cứ ra đề.")
            return

        with st.spinner("⏳ AI đang biên soạn Ngân hàng câu hỏi. Quá trình này có thể mất ít phút tùy theo số lượng câu..."):
            
            # Xử lý gộp văn bản
            tai_lieu_tong_hop = van_ban.strip()
            if uploaded_file:
                tai_lieu_tong_hop += "\n" + extract_text_from_file(uploaded_file)
                
            # Xây dựng lệnh Ràng buộc Bám sát
            rang_buoc_bam_sat = ""
            if tai_lieu_tong_hop.strip():
                if bam_sat_100:
                    rang_buoc_bam_sat = """
[RÀNG BUỘC SỐNG CÒN]: BẠN PHẢI BÁM SÁT 100% VÀO TÀI LIỆU ĐƯỢC CUNG CẤP DƯỚI ĐÂY. 
TUYỆT ĐỐI KHÔNG SỬ DỤNG KIẾN THỨC BÊN NGOÀI ĐỂ ĐẶT CÂU HỎI. Mọi câu hỏi và đáp án phải có căn cứ rõ ràng từ nội dung tài liệu. Nếu tài liệu không đủ dữ kiện, hãy báo cáo.
"""
                else:
                    rang_buoc_bam_sat = """
Bạn có thể kết hợp tài liệu cung cấp và kiến thức học thuật chuyên sâu của bản thân để làm phong phú bộ câu hỏi, miễn là đáp ứng đúng chủ đề.
"""
            else:
                rang_buoc_bam_sat = "Người dùng không cung cấp tài liệu. Hãy sử dụng kiến thức bách khoa của bạn để tự sáng tác bộ câu hỏi chuyên nghiệp nhất."

            prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA KHẢO THÍ VÀ GIÁO VIÊN KINH NGHIỆM.
Nhiệm vụ: Biên soạn một "Ngân Hàng Câu Hỏi" chuẩn mực theo yêu cầu sau:

--- CẤU HÌNH ---
- Chủ đề môn học: {chu_de}
- Số lượng: {so_luong_tn} câu Trắc nghiệm, {so_luong_ds} câu Đúng/Sai, {so_luong_tl} câu Tự luận.
- Mức độ: {muc_do}
- Yêu cầu bổ sung: {yeu_cau_them if yeu_cau_them else 'Trình bày rõ ràng, đáp án chính xác.'}

--- TÀI LIỆU GỐC & RÀNG BUỘC ---
{rang_buoc_bam_sat}
Nội dung tài liệu (nếu có): {tai_lieu_tong_hop[:15000]}

--- YÊU CẦU TRÌNH BÀY ĐẦU RA ---
Hãy trình bày bằng Markdown thật đẹp, chia thành các phần rõ ràng:
1. PHẦN I: TRẮC NGHIỆM
(Mỗi câu Trắc nghiệm phải có 4 đáp án A, B, C, D. Bên dưới mỗi câu hoặc cuối phần có Bôi đậm Đáp án đúng và Giải thích ngắn gọn).
2. PHẦN II: ĐÚNG / SAI (Nếu có)
3. PHẦN III: TỰ LUẬN (Nếu có)
(Đi kèm Gợi ý trả lời hoặc Bareme chấm điểm tóm tắt).

*Lưu ý: Nếu có công thức Toán/Lý/Hóa, BẮT BUỘC bọc trong dấu `$ ... $`.*
"""
            try:
                engine_v2 = AIEngine2(default_model="gemini-2.5-pro") # Dùng Pro để sinh câu hỏi chất lượng cao và tuân thủ Grounding tốt nhất
                result = engine_v2.generate_text(prompt, temperature=0.6)
                
                if result.startswith("❌") or result.startswith("⚠️"):
                    st.error(result)
                else:
                    st.session_state["nhd_result"] = result
                    st.session_state["nhd_topic"] = chu_de[:30].strip().replace(" ", "_") if chu_de else "Tu_Sinh"
            except Exception as e:
                st.error(f"❌ Lỗi khi gọi AI: {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ & XUẤT FILE
    # ========================================================
    if st.session_state.get("nhd_result"):
        st.markdown("---")
        st.markdown("### 📑 KẾT QUẢ NGÂN HÀNG ĐỀ")
        st.markdown(st.session_state["nhd_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Tải xuống Bộ câu hỏi")
        col_txt, col_word = st.columns(2)
        
        with col_txt:
            st.download_button(
                label="📄 Tải bộ đề (.TXT)",
                data=st.session_state["nhd_result"],
                file_name=f"Ngan_Hang_De_{st.session_state['nhd_topic']}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        with col_word:
            if export_word is None:
                st.warning("⚠️ Module Word chưa sẵn sàng.")
            else:
                try:
                    export_data = {
                        "ai_generated_content": st.session_state["nhd_result"],
                        "is_dkt": False
                    }
                    with st.spinner("Đang kết xuất file Word..."):
                        word_bytes = export_word(export_data)
                    
                    st.download_button(
                        label="📘 Tải bộ đề (.DOCX)",
                        data=word_bytes,
                        file_name=f"Ngan_Hang_De_{st.session_state['nhd_topic']}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Lỗi xuất Word: {e}")
                    
        if st.button("🔄 Xóa và Tạo Ngân hàng đề mới", use_container_width=True):
            st.session_state["nhd_result"] = None
            st.rerun()
