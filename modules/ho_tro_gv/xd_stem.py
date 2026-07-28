# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_stem.py
Nhiệm vụ: Trợ lý Thiết kế Kế hoạch Bài học STEM / STEAM.
Nâng cấp: Bám sát Quy trình 4 bước thiết kế, 3 hoạt động thực tế 
và 6 tiêu chí đánh giá chuẩn Bộ GD&ĐT. Tích hợp AIEngine2 & Xuất Word.
============================================================
"""

import logging
import streamlit as st

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

def render_xd_stem(ai_engine_cu=None):
    # Khởi tạo bộ nhớ tạm để giữ kết quả không bị mất khi thao tác tải file
    if "stem_result" not in st.session_state:
        st.session_state["stem_result"] = None
    if "stem_topic" not in st.session_state:
        st.session_state["stem_topic"] = "Ke_Hoach_STEM"

    st.markdown("### 🚀 Thiết kế Kế hoạch Bài học STEM / STEAM")
    st.info("💡 **Góc chuyên gia:** Trợ lý thiết kế bài giảng bám sát quy trình 4 bước, đảm bảo 3 hoạt động thực tiễn và tuân thủ 6 tiêu chí giáo dục STEM chuẩn mực (trong đó tôn trọng tính đa dạng đáp án và coi sự thất bại là một phần tất yếu của quá trình chế tạo).")
    
    with st.container(border=True):
        van_de_thuc_tien = st.text_area(
            "Bước 1+2: Xác định Vấn đề thực tiễn / Tên chủ đề STEM:", 
            height=100, 
            placeholder="VD: Thiết kế hệ thống tưới cây nhỏ giọt bằng chai nhựa để tiết kiệm nước, Chế tạo máy hút bụi mini, Làm nến thơm sinh học..."
        )
        
        c1, c2, c3 = st.columns(3)
        with c1:
            mon_chu_dao = st.text_input("Môn học chủ đạo & Lớp:", placeholder="VD: Vật lí 8, Khoa học tự nhiên 6...")
        with c2:
            thoi_luong = st.text_input("Thời lượng dự kiến:", placeholder="VD: 2 tiết (90 phút)")
        with c3:
            vat_lieu = st.text_input("Vật liệu (Tùy chọn):", placeholder="VD: Bìa carton, chai nhựa, keo nến...")
            
        btn_stem = st.button("🛠️ THIẾT KẾ TIẾN TRÌNH STEM CHUẨN MỰC", type="primary", use_container_width=True)

    # XỬ LÝ SỰ KIỆN NÚT BẤM
    if btn_stem:
        if AIEngine2 is None:
            st.error("❌ Không tìm thấy file `utils/ai_engine_2.py`. Vui lòng kiểm tra lại cấu trúc dự án.")
            return

        if not van_de_thuc_tien.strip() or not mon_chu_dao.strip():
            st.warning("⚠️ Vui lòng nhập Vấn đề thực tiễn và Môn học chủ đạo.")
        else:
            with st.spinner("⏳ AI đang phân tích tiêu chí, tích hợp kiến thức nền và xây dựng tiến trình STEM 5 bước..."):
                prompt = f"""
BẠN LÀ CHUYÊN GIA GIÁO DỤC STEM/STEAM CẤP QUỐC GIA.
Nhiệm vụ của bạn là thiết kế một Kế hoạch Bài học STEM bám sát hoàn toàn vào hệ thống lý luận sư phạm khắt khe dưới đây.
                
--- THÔNG TIN CƠ BẢN ---
- Chủ đề / Vấn đề thực tiễn: {van_de_thuc_tien}
- Môn học chủ đạo: {mon_chu_dao}
- Thời lượng: {thoi_luong if thoi_luong else 'Tuỳ chỉnh'}
- Vật liệu dự kiến: {vat_lieu if vat_lieu else 'Gợi ý các vật liệu tái chế, dễ tìm, chi phí thấp.'}

--- NỀN TẢNG LÝ LUẬN BẮT BUỘC ÁP DỤNG TRONG KỊCH BẢN ---
1. Kịch bản phải chứa đủ 3 hoạt động: (1) Tìm hiểu thực tiễn/phát hiện vấn đề, (2) Nghiên cứu kiến thức nền, (3) Giải quyết vấn đề.
2. Tuân thủ 6 tiêu chí: Tập trung vấn đề thực tiễn; Cấu trúc theo EDP; Học sinh kiến tạo; Làm việc nhóm; Kết nối Toán & Khoa học; Tiến trình mở (chấp nhận nhiều đáp án đúng và coi thất bại là một phần cần thiết của học tập).

--- YÊU CẦU TRÌNH BÀY (DÙNG MARKDOWN) ---

# PHẦN I: TỔNG QUAN CHỦ ĐỀ & YÊU CẦU KỸ THUẬT (Quy trình 4 bước thiết kế)
- **1. Chủ đề & Vấn đề cần giải quyết:** Mô tả bối cảnh thực tiễn.
- **2. Phân tích Kiến thức STEM:** S (Khoa học), T (Công nghệ), E (Kỹ thuật), M (Toán học) trong bài là gì?
- **3. Xây dựng tiêu chí sản phẩm/giải pháp:** (Cực kỳ quan trọng: Tiêu chí phải định lượng được, ví dụ: chịu được tải trọng bao nhiêu, kích thước tối đa bao nhiêu, hoạt động ổn định trong bao lâu...).
- **4. Đề xuất danh mục Vật liệu.**

# PHẦN II: TIẾN TRÌNH DẠY HỌC 5 BƯỚC (Quy trình Thiết kế Kỹ thuật - EDP)
(Ở mỗi bước, hãy trình bày rõ Hoạt động của GV, Hoạt động của HS, và nhấn mạnh vào việc làm việc nhóm).
- **Bước 1: Xác định vấn đề & Đặt tiêu chí (Tìm hiểu thực tiễn):** Giao nhiệm vụ thế nào để lôi cuốn học sinh?
- **Bước 2: Nghiên cứu kiến thức nền & Đề xuất giải pháp:** Học sinh vận dụng kiến thức Toán/Khoa học gì đang học để giải quyết?
- **Bước 3: Lựa chọn giải pháp & Bản vẽ thiết kế:** (Nhấn mạnh hoạt động nhóm kiến tạo).
- **Bước 4: Chế tạo mô hình & Thử nghiệm:** (Bắt buộc phải có kịch bản học sinh làm thử nghiệm bị thất bại/sai số, GV hướng dẫn HS coi sự thất bại là cần thiết để cải tiến).
- **Bước 5: Trình bày, Thảo luận & Điều chỉnh:** (GV tổ chức đánh giá sao cho tôn trọng việc có nhiều đáp án/giải pháp đúng khác nhau).

[KỶ LUẬT ĐỊNH DẠNG SỐNG CÒN]
- Trình bày mạch lạc bằng Markdown.
- Nếu có xuất hiện công thức Toán/Lý/Hóa, TUYỆT ĐỐI dùng chuẩn LaTeX bọc trong dấu `$ ... $`. Không bao giờ được dùng dấu nháy ngược (`) để bọc công thức Toán học.
"""
                try:
                    engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                    res = engine_v2.generate_text(prompt, temperature=0.7)
                    
                    if res.startswith("❌") or res.startswith("⚠️"):
                        st.error(res)
                    else:
                        st.session_state["stem_result"] = res
                        st.session_state["stem_topic"] = van_de_thuc_tien[:30].strip().replace(" ", "_")
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ & XUẤT FILE WORD
    # ========================================================
    if st.session_state.get("stem_result"):
        st.markdown("---")
        st.markdown("#### 📐 Khung Kế hoạch Bài học STEM (Chuẩn EDP)")
        st.markdown(st.session_state["stem_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Tải Giáo án / Kế hoạch")
        if export_word is None:
            st.warning("⚠️ Module Word chưa sẵn sàng.")
        else:
            try:
                export_data = {
                    "ai_generated_content": st.session_state["stem_result"],
                    "is_dkt": False
                }
                with st.spinner("Đang kết xuất file Word chuẩn mực..."):
                    word_bytes = export_word(export_data)
                
                safe_name = st.session_state.get("stem_topic", "STEM")
                
                st.download_button(
                    label="📘 TẢI KẾ HOẠCH BÀI HỌC (.DOCX)",
                    data=word_bytes,
                    file_name=f"KHBD_STEM_{safe_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Lỗi xuất Word: {e}")
                
        if st.button("🔄 Xóa bản nháp và thiết kế chủ đề mới", use_container_width=True):
            st.session_state["stem_result"] = None
            st.rerun()
