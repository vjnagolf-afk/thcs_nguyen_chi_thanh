# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_live.py
Nhiệm vụ: Trợ lý Kịch bản Tương tác Trực tiếp (Live) - Cấp độ Bậc thầy.
Kết nối trực tiếp AIEngine2, có tính năng Xuất Word.
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

def render_xd_live(ai_engine_cu=None):
    # Khởi tạo bộ nhớ tạm để giữ kết quả kịch bản
    if "live_result" not in st.session_state:
        st.session_state["live_result"] = None
    if "live_topic" not in st.session_state:
        st.session_state["live_topic"] = "Kich_Ban_Live"

    st.markdown("### 🔴 Trợ lý Kịch bản Tương tác Trực tiếp (Live)")
    st.info("💡 **Góc chuyên gia:** Biến tiết dạy thành một show truyền hình thực tế! AI sẽ đóng vai trò là một Đạo diễn, MC và Giám khảo lão luyện để viết cho Thầy/Cô kịch bản từng lời dẫn, cách "rắc muối" và điều phối tranh biện đỉnh cao.")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            chu_de_live = st.text_input("Chủ đề bài học hôm nay:", placeholder="VD: Hiện tượng nhà kính, Văn tế nghĩa sĩ Cần Giuộc...")
            do_tuoi = st.selectbox("Đối tượng Học sinh:", ["Tiểu học (Cần năng lượng, vui nhộn)", "THCS (Cần giật gân, khơi gợi trí tò mò)", "THPT (Cần chiều sâu, tranh biện sắc bén)"])
        with col2:
            muc_dich = st.selectbox("Giai đoạn / Mục đích hoạt động:", [
                "Warm-up (Phá băng đầu giờ - Gây sốc/Tò mò)", 
                "Debate (Tranh biện giữa giờ - Chia phe/Phản biện)", 
                "Wrap-up (Củng cố cuối giờ - Game hóa/Neo cảm xúc)"
            ])
            phong_cach = st.selectbox("Phong cách dẫn dắt (Tone):", [
                "Hài hước, trending (Gen Z)", 
                "Nghiêm túc, kịch tính, bí ẩn", 
                "Cảm xúc, sâu lắng, truyền cảm hứng"
            ])
            
        boi_canh = st.text_area("Bối cảnh thêm hoặc Từ khóa cần nhấn mạnh (Tuỳ chọn):", height=80, placeholder="VD: HS đang khá buồn ngủ vì là tiết 5, cần game tương tác vật lý một chút...")
            
        btn_tao_live = st.button("🔥 TẠO KỊCH BẢN ĐIỀU PHỐI ĐỈNH CAO", type="primary", use_container_width=True)

    if btn_tao_live:
        if AIEngine2 is None:
            st.error("❌ Không tìm thấy file `utils/ai_engine_2.py`. Vui lòng kiểm tra lại cấu trúc dự án.")
            return

        if not chu_de_live.strip():
            st.warning("⚠️ Vui lòng nhập Chủ đề bài học để AI có chất liệu sáng tạo.")
        else:
            with st.spinner("⏳ AI đang hóa thân thành Đạo diễn sân khấu & Giám khảo quyền lực để viết kịch bản..."):
                prompt = f"""
BẠN LÀ MỘT BẬC THẦY VỀ NGHỆ THUẬT GIẢNG DẠY, MỘT GIÁM KHẢO SẮC BÉN VÀ LÀ MỘT MC ĐẦY LÔI CUỐN.
Nhiệm vụ của bạn là thiết kế một Kịch bản Tương tác Trực tiếp (Live Class) ĐỈNH CAO, biến tiết học thành một show diễn tri thức không thể rời mắt.

--- THÔNG TIN LỚP HỌC ---
- Chủ đề cốt lõi: {chu_de_live}
- Đối tượng: {do_tuoi}
- Mục đích hoạt động: {muc_dich}
- Phong cách dẫn dắt: {phong_cach}
- Bối cảnh/Yêu cầu thêm: {boi_canh if boi_canh.strip() else 'Tự do sáng tạo'}

--- CẤU TRÚC KỊCH BẢN BẮT BUỘC ---

# 1. SET-UP & BỐI CẢNH (Dành riêng cho GV)
(Gợi ý nhanh về đạo cụ, hình ảnh hiển thị trên Slide, nhạc nền cần bật, hoặc ánh mắt/thái độ cần thể hiện để tạo "vibe" ngay từ giây đầu tiên).

# 2. SCRIPT LỜI DẪN NHẬP (Mở mic lên là thu hút 100%)
(Viết chi tiết TỪNG CÂU TỪNG CHỮ để Giáo viên đọc. Lời thoại phải mang đậm phong cách "{phong_cach}". Mở bài bằng một câu hỏi sốc, một nghịch lý, hoặc một câu chuyện ngắn giật gân liên quan đến chủ đề).

# 3. KÍCH HOẠT TƯƠNG TÁC (Tâm điểm của hoạt động)
(Đưa ra 3 câu hỏi/tình huống/nhiệm vụ. 
HƯỚNG DẪN CỤ THỂ CÁCH YÊU CẦU HS TƯƠNG TÁC: VD "Các em gõ phím 1 nếu... phím 2 nếu...", "Ai phản đối hãy thả icon phẫn nộ", "Chia làm 2 phe chat tranh biện"... Đừng dùng cách hỏi đáp truyền thống nhàm chán).

# 4. GÓC NHÌN "GIÁM KHẢO" (Kỹ năng bẻ lái & Phản biện)
(Dự đoán các câu trả lời ngô nghê hoặc trái chiều của học sinh. Gợi ý cho Giáo viên các câu nói sắc bén để "chặt chém" (một cách hài hước/giáo dục), lật ngược vấn đề, ép học sinh phải tư duy sâu hơn. Giống như một giám khảo quyền lực nhận xét thí sinh).

# 5. CHỐT HẠ & NEO CẢM XÚC
(Câu nói chốt lại vấn đề, đúc kết kiến thức lõi thành một thông điệp ngắn gọn, sâu sắc khiến học sinh nổi da gà và nhớ mãi).

[KỶ LUẬT ĐỊNH DẠNG]
- Sử dụng Markdown chuyên nghiệp (Bullet points, in đậm từ khóa).
- NẾU có dính đến công thức Toán/Lý/Hóa, BẮT BUỘC dùng chuẩn LaTeX bọc trong dấu `$ ... $`.
- Tuyệt đối không dùng dấu backtick (`) cho công thức Toán.
"""
                try:
                    # Khởi tạo AIEngine2 (Dùng Pro để khả năng sáng tạo ngôn từ phong phú nhất)
                    engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                    result = engine_v2.generate_text(prompt, temperature=0.8) # Tăng temperature để tăng độ sáng tạo
                    
                    if result.startswith("❌") or result.startswith("⚠️"):
                        st.error(result)
                    else:
                        st.session_state["live_result"] = result
                        st.session_state["live_topic"] = chu_de_live.replace(" ", "_")
                        
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ & XUẤT FILE
    # ========================================================
    if st.session_state.get("live_result"):
        st.markdown("---")
        st.markdown("### 🎭 KỊCH BẢN ĐIỀU PHỐI ĐỈNH CAO")
        
        st.markdown(st.session_state["live_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Tải Kịch bản (In ra để dẫn chương trình)")
        if export_word is None:
            st.warning("⚠️ Module Word chưa sẵn sàng.")
        else:
            try:
                export_data = {
                    "ai_generated_content": st.session_state["live_result"],
                    "is_dkt": False
                }
                with st.spinner("Đang kết xuất Word..."):
                    word_bytes = export_word(export_data)
                
                safe_topic = st.session_state.get("live_topic", "Kich_Ban")[:30]
                
                st.download_button(
                    label="📘 TẢI KỊCH BẢN (.DOCX)",
                    data=word_bytes,
                    file_name=f"Live_Script_{safe_topic}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Lỗi xuất Word: {e}")
                
        if st.button("🔄 Lên kịch bản cho bài khác", use_container_width=True):
            st.session_state["live_result"] = None
            st.rerun()
