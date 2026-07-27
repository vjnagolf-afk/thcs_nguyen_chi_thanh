# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_live.py
Nhiệm vụ: Trợ lý Kịch bản Tương tác Trực tiếp (Live).
CẬP NHẬT TỐI THƯỢNG: Sinh MASTER PROMPT (Chỉ copy 1 lần duy nhất cho toàn bộ Video).
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
    # Khởi tạo bộ nhớ tạm
    if "live_result" not in st.session_state:
        st.session_state["live_result"] = None
    if "live_topic" not in st.session_state:
        st.session_state["live_topic"] = "Kich_Ban_Live"
    if "video_prompts" not in st.session_state:
        st.session_state["video_prompts"] = None

    st.markdown("### 🔴 Trợ lý Kịch bản Tương tác Trực tiếp (Live)")
    st.info('💡 **Góc chuyên gia:** Biến tiết dạy thành một show truyền hình thực tế! AI sẽ đóng vai trò là một Đạo diễn, MC và Giám khảo lão luyện để viết cho Thầy/Cô kịch bản từng lời dẫn, cách "rắc muối" và điều phối tranh biện đỉnh cao.')
    
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
            
        btn_tao_live = st.button("🔥 1. TẠO KỊCH BẢN ĐIỀU PHỐI ĐỈNH CAO", type="primary", use_container_width=True)

    # ========================================================
    # XỬ LÝ: TẠO KỊCH BẢN LIVE
    # ========================================================
    if btn_tao_live:
        if AIEngine2 is None:
            st.error("❌ Không tìm thấy file `utils/ai_engine_2.py`. Vui lòng kiểm tra lại cấu trúc dự án.")
            return

        if not chu_de_live.strip():
            st.warning("⚠️ Vui lòng nhập Chủ đề bài học để AI có chất liệu sáng tạo.")
        else:
            st.session_state["video_prompts"] = None 
            
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
(Gợi ý nhanh về đạo cụ, hình ảnh hiển thị trên Slide, nhạc nền cần bật).

# 2. SCRIPT LỜI DẪN NHẬP (Mở mic lên là thu hút 100%)
(Viết chi tiết TỪNG CÂU TỪNG CHỮ để Giáo viên đọc. Lời thoại phải mang đậm phong cách "{phong_cach}". Mở bài bằng một câu hỏi sốc, một nghịch lý, hoặc một câu chuyện ngắn giật gân).

# 3. KÍCH HOẠT TƯƠNG TÁC (Tâm điểm của hoạt động)
(Đưa ra 3 câu hỏi/tình huống/nhiệm vụ. HƯỚNG DẪN CỤ THỂ CÁCH YÊU CẦU HS TƯƠNG TÁC).

# 4. GÓC NHÌN "GIÁM KHẢO" (Kỹ năng bẻ lái & Phản biện)
(Dự đoán các câu trả lời ngô nghê hoặc trái chiều của học sinh. Gợi ý cho Giáo viên các câu nói sắc bén để "chặt chém" hoặc lật ngược vấn đề).

# 5. CHỐT HẠ & NEO CẢM XÚC
(Câu nói chốt lại vấn đề, đúc kết kiến thức lõi).

[KỶ LUẬT ĐỊNH DẠNG]
- Sử dụng Markdown chuyên nghiệp.
- NẾU có dính đến công thức Toán/Lý/Hóa, BẮT BUỘC dùng chuẩn LaTeX bọc trong dấu `$...$`.
- Tuyệt đối không dùng dấu backtick (`) cho công thức Toán.
"""
                try:
                    engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                    result = engine_v2.generate_text(prompt, temperature=0.8)
                    
                    if result.startswith("❌") or result.startswith("⚠️"):
                        st.error(result)
                    else:
                        st.session_state["live_result"] = result
                        st.session_state["live_topic"] = chu_de_live.replace(" ", "_")
                        
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ & CÁC NÚT TÍNH NĂNG MỞ RỘNG
    # ========================================================
    if st.session_state.get("live_result"):
        st.markdown("---")
        st.markdown("### 🎭 KỊCH BẢN ĐIỀU PHỐI ĐỈNH CAO")
        st.markdown(st.session_state["live_result"], unsafe_allow_html=True)
        
        col_down, col_video = st.columns([1, 1])
        with col_down:
            st.markdown("#### 📥 Tải Kịch bản (Bản in)")
            if export_word:
                try:
                    export_data = {"ai_generated_content": st.session_state["live_result"], "is_dkt": False}
                    word_bytes = export_word(export_data)
                    safe_topic = st.session_state.get("live_topic", "Kich_Ban")[:30]
                    st.download_button(
                        label="📄 TẢI KỊCH BẢN (.DOCX)",
                        data=word_bytes,
                        file_name=f"Live_Script_{safe_topic}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Lỗi xuất Word: {e}")
            else:
                st.warning("⚠️ Module Word chưa sẵn sàng.")

        with col_video:
            st.markdown("#### 🎬 Chuyển hóa thành Video Tương tác")
            btn_tao_video = st.button("🪄 2. Sinh MASTER PROMPT (Tạo AI Video 1 chạm)", use_container_width=True, type="secondary")

        # ========================================================
        # XỬ LÝ: SINH MASTER PROMPT (1 COPY-PASTE)
        # ========================================================
        if btn_tao_video:
            with st.spinner("⏳ AI đang nén toàn bộ kịch bản thành 1 Master Prompt duy nhất..."):
                bq = "```"
                video_prompt = f"""
Bạn là một Đạo diễn Phim & Chuyên gia AI Video (Google Veo, Sora, HeyGen).
YÊU CẦU ĐẶC BIỆT: Người dùng muốn chỉ cần COPY 1 LẦN DUY NHẤT để dán vào công cụ tạo Video. Do đó, bạn KHÔNG ĐƯỢC chia nhỏ prompt theo từng cảnh nữa. Hãy gộp tất cả thành các MASTER BLOCK.

Hãy thiết lập ĐÚNG cấu trúc sau bằng Markdown:

## 🎥 1. MASTER VIDEO PROMPT (TIẾNG ANH - TẠO HÌNH ẢNH/VIDEO)
(Gộp toàn bộ thông tin về nhân vật MC, bối cảnh, và chuỗi hành động xuyên suốt từ đầu đến cuối kịch bản vào MỘT đoạn văn bản tiếng Anh duy nhất. Sử dụng các từ khóa chuyển cảnh mượt mà. Đảm bảo mô tả ngoại hình MC xuất hiện rõ ràng để AI giữ tính nhất quán).
{bq}text
[Viết Master Prompt Tiếng Anh vào đây - Chỉ một đoạn văn bản dài duy nhất, liên tục]
{bq}

## 🗣️ 2. MASTER SCRIPT (TIẾNG VIỆT - TẠO GIỌNG ĐỌC MC ẢO)
(Trích xuất toàn bộ lời thoại của MC từ đầu đến cuối kịch bản. Loại bỏ các chỉ dẫn hành động, chỉ giữ lại LỜI NÓI. Có thể dùng các thẻ [Pause 2s] để ngắt nhịp nếu cần).
{bq}text
[Viết Master Script Tiếng Việt vào đây - Liền mạch từ đầu đến cuối]
{bq}

## 🖱️ 3. KỊCH BẢN ĐIỂM CHẠM (EDPUZZLE/H5P)
(Chỉ dẫn nhanh cho giáo viên biết nên dừng video ở đoạn nào để chèn câu hỏi tương tác).
[Liệt kê ngắn gọn]

--- KỊCH BẢN GỐC ---
{st.session_state["live_result"]}
"""
                try:
                    engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                    video_result = engine_v2.generate_text(video_prompt, temperature=0.5)
                    
                    if video_result.startswith("❌") or video_result.startswith("⚠️"):
                        st.error(video_result)
                    else:
                        st.session_state["video_prompts"] = video_result
                        
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống khi sinh Prompt Video: {e}")

        # Hiển thị bộ Prompt Video nếu đã tạo
        if st.session_state.get("video_prompts"):
            st.markdown("---")
            st.success("✅ Đã nén thành công Master Prompt! Giờ đây Thầy/Cô chỉ cần 1 thao tác Copy-Paste.")
            st.info("💡 **Hướng dẫn:** Bấm Copy ở khung Tiếng Anh dán vào Veo/Sora. Bấm Copy ở khung Tiếng Việt dán vào HeyGen/V-hub.")
            
            with st.expander("🎞️ MASTER PROMPT AI VIDEO (Bấm để xem & Copy)", expanded=True):
                st.markdown(st.session_state["video_prompts"], unsafe_allow_html=True)
                
                st.download_button(
                    label="📋 Tải file Master Prompt (.TXT)",
                    data=st.session_state["video_prompts"],
                    file_name="Master_Video_Prompts.txt",
                    mime="text/plain",
                    use_container_width=True
                )
