# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_chu_nhiem.py
Nhiệm vụ: Trợ lý Công tác Chủ nhiệm & Tâm lý học đường.
Kết nối trực tiếp qua ai_engine_2.py.
Tích hợp tính năng Lưu kết quả (Session State) và Xuất file Word.
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

# ============================================================
# 1. HÀM GỌI AI ENGINE (TƯƠNG THÍCH ĐA PHIÊN BẢN SDK)
# ============================================================
def call_chu_nhiem_ai(ai_engine, prompt):
    """
    Giao tiếp với `ai_engine_2.py`.
    Thích ứng thông minh với các hàm có trong Engine của dự án.
    """
    if ai_engine is None:
        raise ValueError("Chưa kết nối AI Engine.")
        
    try:
        # Ưu tiên SDK Google GenAI mới nhất (nếu ai_engine_2.py đã cập nhật)
        if hasattr(ai_engine, "client") and hasattr(ai_engine.client, "models"):
            response = ai_engine.client.models.generate_content(
                model="gemini-2.5-pro", # Dùng Pro cho các bài toán suy luận tâm lý sâu
                contents=prompt
            )
            return response.text
        # Fallback về các hàm cũ
        elif hasattr(ai_engine, "generate_text"):
            return ai_engine.generate_text(prompt)
        elif hasattr(ai_engine, "generate"):
            return ai_engine.generate(prompt)
        else:
            raise AttributeError("Không tìm thấy hàm gọi AI hợp lệ trong ai_engine.")
            
    except Exception as e:
        logger.error(f"Lỗi AI Chủ nhiệm: {e}")
        raise RuntimeError(f"Sự cố khi gọi AI: {e}")

# ============================================================
# 2. GIAO DIỆN VÀ LOGIC CHÍNH
# ============================================================
def render_xd_chu_nhiem(ai_engine=None):
    # Khởi tạo bộ nhớ tạm để giữ kết quả không bị mất khi thao tác
    if "cn_result" not in st.session_state:
        st.session_state["cn_result"] = None
    if "cn_chu_de" not in st.session_state:
        st.session_state["cn_chu_de"] = "Tư_vấn"

    st.markdown("### 👨‍👩‍👧‍👦 Trợ lý Công tác Chủ nhiệm & Tâm lý")
    st.info("💡 **Góc chuyên gia:** AI sẽ đóng vai trò là một chuyên gia tâm lý học đường, hỗ trợ phân tích nguyên nhân sâu xa, đưa ra từng bước xử lý sư phạm và gợi ý cả **kịch bản lời thoại** để Thầy/Cô giao tiếp với Phụ huynh/Học sinh.")
    
    with st.container(border=True):
        col_loai, col_do_tuoi = st.columns(2)
        with col_loai:
            chu_de = st.selectbox(
                "Chọn nhóm tình huống cần hỗ trợ:",
                [
                    "Xử lý học sinh vi phạm kỷ luật", 
                    "Tư vấn tâm lý (Trầm cảm, bạo lực học đường, cô lập)", 
                    "Xây dựng kịch bản họp Phụ huynh", 
                    "Hòa giải xung đột giữa Phụ huynh và Giáo viên",
                    "Động viên học sinh học tập sa sút"
                ]
            )
        with col_do_tuoi:
            do_tuoi = st.selectbox(
                "Khối lớp (Để AI dùng văn phong, tâm lý lứa tuổi phù hợp):", 
                [
                    "Lớp 6 (Chuyển cấp, bỡ ngỡ, nhạy cảm)", 
                    "Lớp 7 - 8 (Dậy thì, nổi loạn, thích thể hiện)", 
                    "Lớp 9 (Áp lực thi cử, định hướng tương lai)"
                ]
            )

        tinh_huong = st.text_area(
            "Mô tả chi tiết tình huống hiện tại:", 
            height=120, 
            placeholder="VD: Hai học sinh nữ đánh nhau vì mâu thuẫn trên mạng xã hội, phụ huynh một bên đang rất bức xúc gọi điện đòi làm lớn chuyện. Học sinh thì đang hoảng loạn khóc lóc..."
        )
        
        btn_tu_van = st.button("🧠 Phân tích tình huống & Đề xuất kịch bản", type="primary", use_container_width=True)

    # XỬ LÝ SỰ KIỆN NÚT BẤM
    if btn_tu_van:
        if not tinh_huong.strip():
            st.warning("⚠️ Vui lòng mô tả chi tiết tình huống để AI có cơ sở tư vấn.")
        else:
            with st.spinner("⏳ AI đang phân tích tâm lý lứa tuổi và soạn thảo kịch bản sư phạm khéo léo nhất..."):
                prompt = f"""
Bạn là một Chuyên gia Tâm lý học đường cấp cao và một Giáo viên chủ nhiệm vô cùng xuất sắc, khéo léo.
Hãy giúp giải quyết tình huống sư phạm sau đây một cách thấu tình đạt lý, mang tính giáo dục cao và đúng quy định của Bộ GD&ĐT.
                
--- THÔNG TIN TÌNH HUỐNG ---
- Đối tượng học sinh: {do_tuoi}
- Nhóm vấn đề: {chu_de}
- Tình huống thực tế đang diễn ra: {tinh_huong}
                
--- YÊU CẦU TRÌNH BÀY (DÙNG MARKDOWN) ---
# 1. PHÂN TÍCH TÂM LÝ & NGUYÊN NHÂN SÂU XA
(Đánh giá tâm lý của học sinh ở độ tuổi này, phân tích góc nhìn của phụ huynh và các yếu tố tác động).

# 2. CÁC BƯỚC XỬ LÝ SƯ PHẠM (QUY TRÌNH CHUẨN)
(Trình bày theo thứ tự: Ngay lập tức làm gì -> Tiếp theo làm gì -> Về lâu dài làm gì. Đảm bảo tính pháp lý và nhân văn).

# 3. KỊCH BẢN LỜI THOẠI THAM KHẢO
(Viết rõ dạng kịch bản đoạn hội thoại. Gợi ý Thầy/Cô nên nói câu gì để "hạ nhiệt", câu gì để thể hiện sự đồng cảm, và câu gì để chốt lại nguyên tắc. Phân chia rõ lời nói với Phụ huynh và lời nói với Học sinh).

# 4. LỜI KHUYÊN PHÒNG NGỪA
(Làm sao để lớp không lặp lại tình trạng này).
"""
                try:
                    result = call_chu_nhiem_ai(ai_engine, prompt)
                    # Lưu vào Session State để không bị mất khi tải lại trang
                    st.session_state["cn_result"] = result
                    # Lưu tên chủ đề để làm tên file Word
                    st.session_state["cn_chu_de"] = chu_de.split("(")[0].strip().replace(" ", "_")
                except Exception as e:
                    st.error(f"❌ {e}")

    # HIỂN THỊ KẾT QUẢ VÀ XUẤT WORD
    if st.session_state.get("cn_result"):
        st.markdown("---")
        st.markdown("### 🛡️ CẨM NANG XỬ LÝ TÌNH HUỐNG")
        
        # Hiển thị nội dung
        st.markdown(st.session_state["cn_result"], unsafe_allow_html=True)
        
        # Tính năng Xuất file Word
        st.markdown("### 📥 Lưu trữ Kịch bản")
        if export_word is None:
            st.error("Chưa cài đặt hoặc bị lỗi module export_word.")
        else:
            try:
                # Đóng gói dữ liệu gửi cho hàm export_word
                export_data = {
                    "ai_generated_content": st.session_state["cn_result"],
                    "is_dkt": False
                }
                
                with st.spinner("Đang kết xuất file Word..."):
                    word_bytes = export_word(export_data)
                
                safe_name = st.session_state.get("cn_chu_de", "Tu_van_Tam_ly")
                
                st.download_button(
                    label="📥 TẢI XUỐNG KỊCH BẢN (FILE WORD)",
                    data=word_bytes,
                    file_name=f"Kich_Ban_{safe_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Lỗi xuất file Word: {e}")
                
        if st.button("🔄 Xóa bản nháp và tư vấn tình huống mới", use_container_width=True):
            st.session_state["cn_result"] = None
            st.rerun()
