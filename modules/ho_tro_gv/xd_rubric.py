# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_rubric.py
Nhiệm vụ: Trợ lý Xây dựng Rubric Đánh Giá theo hướng phát triển năng lực.
Tích hợp: Tiêu chí nội dung chuẩn, Phân bổ trọng số, Mô tả hành vi & Xuất Word.
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

def render_xd_rubric(ai_engine_cu=None):
    # Khởi tạo session state lưu kết quả
    if "rubric_result" not in st.session_state:
        st.session_state["rubric_result"] = None
    if "rubric_topic" not in st.session_state:
        st.session_state["rubric_topic"] = "Rubric_Danh_Gia"

    st.markdown("### 📊 Trợ lý Xây dựng Rubric Đánh Giá")
    st.info("💡 **Góc chuyên gia:** Thiết kế ma trận tiêu chí đánh giá (Rubric) chuẩn khoa học đo lường giáo dục: Bám sát mục tiêu, phân chia mức độ rõ ràng, mô tả hành vi định lượng được và phân bổ trọng số điểm hợp lý.")
    
    with st.container(border=True):
        loai_nhiem_vu = st.selectbox(
            "Loại nhiệm vụ đánh giá:", 
            ["Dự án học tập (Project)", "Bài thuyết trình", "Bài viết luận/Nghị luận", "Hoạt động thực hành/Thí nghiệm", "Làm việc nhóm"]
        )
        yeu_cau_can_dat = st.text_area(
            "Mục tiêu bài học / Yêu cầu cần đạt:", 
            height=100, 
            placeholder="VD: HS thiết kế được mô hình tế bào thực vật bằng vật liệu tái chế, thuyết trình rõ ràng chức năng các bào quan."
        )
        
        c1, c2 = st.columns(2)
        with c1:
            thang_diem = st.selectbox(
                "Thang đánh giá:", 
                ["4 mức (Chưa đạt, Đạt, Khá, Tốt)", "3 mức (Cần cố gắng, Đạt, Tốt)", "Thang điểm 10 chi tiết"]
            )
        with c2:
            kieu_trinh_bay = st.selectbox(
                "Góc nhìn đánh giá:", 
                ["Giáo viên chấm điểm", "Học sinh tự đánh giá (Self-assessment)", "Đánh giá đồng đẳng (Peer-assessment)"]
            )
        
        btn_rubric = st.button("✨ XÂY DỰNG RUBRIC CHUYÊN SÂU", type="primary", use_container_width=True)

    # XỬ LÝ SỰ KIỆN KHI BẤM NÚT
    if btn_rubric:
        if AIEngine2 is None:
            st.error("❌ Không tìm thấy file `utils/ai_engine_2.py`. Vui lòng kiểm tra lại cấu trúc dự án.")
            return

        if not yeu_cau_can_dat.strip():
            st.warning("⚠️ Vui lòng nhập Yêu cầu cần đạt.")
        else:
            with st.spinner("⏳ AI đang thiết kế ma trận tiêu chí đánh giá chuẩn đo lường giáo dục..."):
                prompt = f"""
BẠN LÀ CHUYÊN GIA ĐO LƯỜNG VÀ ĐÁNH GIÁ GIÁO DỤC CẤP CAO.
Hãy xây dựng một bảng Rubric cực kỳ chi tiết, khoa học và chuyên nghiệp để đánh giá nhiệm vụ: {loai_nhiem_vu}.

--- THÔNG TIN ĐẦU VÀO ---
- Mục tiêu / Yêu cầu cần đạt: {yeu_cau_can_dat}
- Thang đánh giá: {thang_diem}
- Đối tượng/Góc nhìn sử dụng rubric: {kieu_trinh_bay} (Điều chỉnh ngôn từ cho phù hợp: Nếu GV chấm dùng từ chuyên môn; nếu HS tự chấm dùng "Tôi...").

--- TIÊU CHÍ THIẾT KẾ BẮT BUỘC ---
1. **Tiêu chí nội dung:** Bám sát tuyệt đối mục tiêu bài học, chuẩn kiến thức, kỹ năng hoặc năng lực cốt lõi cần đo lường.
2. **Trọng số điểm:** Phân bổ tỷ lệ điểm hợp lý (hoặc phần trăm trọng số) cho từng tiêu chí lớn nhỏ tùy theo mức độ quan trọng (tổng trọng số các tiêu chí phải đạt 100% hoặc khớp thang điểm).
3. **Mức độ đạt được:** Phân chia thành các cấp rõ ràng theo đúng thang đánh giá ({thang_diem}).
4. **Mô tả chất lượng:** Diễn giải cụ thể hành động, sản phẩm hoặc năng lực tương ứng ở từng mức điểm (hành vi phải quan sát được, đo lường được, tuyệt đối không dùng từ ngữ mơ hồ).

--- YÊU CẦU ĐẦU RA ---
- Trình bày dưới dạng Bảng Markdown hoàn chỉnh. 
- Cột đầu tiên: "Tiêu chí đánh giá & Trọng số".
- Các cột tiếp theo: Các mức độ đạt được.
- Kèm theo Hướng dẫn quy đổi điểm số cụ thể cho giáo viên/học sinh.

[KỶ LUẬT ĐỊNH DẠNG]
- Sử dụng Markdown chuyên nghiệp.
- NẾU có công thức Toán/Lý/Hóa, BẮT BUỘC dùng chuẩn LaTeX bọc trong dấu `$ ... $`. Cấm dùng backtick (`).
"""
                try:
                    engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                    res = engine_v2.generate_text(prompt, temperature=0.7)
                    
                    if res.startswith("❌") or res.startswith("⚠️"):
                        st.error(res)
                    else:
                        st.session_state["rubric_result"] = res
                        st.session_state["rubric_topic"] = loai_nhiem_vu.replace(" ", "_")
                except Exception as e:
                    st.error(f"Lỗi AI: {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ & XUẤT FILE WORD
    # ========================================================
    if st.session_state.get("rubric_result"):
        st.markdown("---")
        st.markdown("#### 📑 Bảng Tiêu chí Đánh giá (Rubric)")
        st.markdown(st.session_state["rubric_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Lưu trữ Rubric")
        if export_word is None:
            st.warning("⚠️ Module Word chưa sẵn sàng.")
        else:
            try:
                export_data = {
                    "ai_generated_content": st.session_state["rubric_result"],
                    "is_dkt": False
                }
                with st.spinner("Đang kết xuất file Word..."):
                    word_bytes = export_word(export_data)
                
                safe_name = st.session_state.get("rubric_topic", "Rubric")[:30]
                st.download_button(
                    label="📥 TẢI XUỐNG RUBRIC (.DOCX)",
                    data=word_bytes,
                    file_name=f"Rubric_{safe_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Lỗi xuất Word: {e}")
                
        if st.button("🔄 Xóa bản nháp và tạo Rubric khác", use_container_width=True):
            st.session_state["rubric_result"] = None
            st.rerun()
