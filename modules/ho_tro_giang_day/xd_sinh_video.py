# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_sinh_video.py
Nhiệm vụ: Trợ lý AI Sinh Video & Video Tương tác.
Nâng cấp: Tích hợp chuyên sâu 3 nhóm công cụ AI Video (Điện ảnh, Avatar, Tự động hóa)
và hệ thống Video Tương tác Timestamp thông minh.
============================================================
"""

import io
import json
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

def render_xd_sinh_video(ai_engine_cu=None):
    if "vid_script_result" not in st.session_state:
        st.session_state["vid_script_result"] = None
    if "vid_interactive_result" not in st.session_state:
        st.session_state["vid_interactive_result"] = None

    st.markdown("### 🎬 Trợ lý Sản xuất Video Học liệu & Tương tác")
    st.info("💡 **Góc chuyên gia:** Phân hệ chuyên nghiệp hỗ trợ xây dựng kịch bản, cấu trúc Prompt và chiến lược sản xuất video dựa trên 3 hệ sinh thái AI hàng đầu thế giới kết hợp công nghệ Video Tương tác.")

    # Tạo 2 Tabs cho 2 luồng công việc
    tab1, tab2 = st.tabs(["🎥 1. Sinh Kịch bản & Prompt theo Hệ sinh thái AI Video", "👆 2. Thiết kế Video Tương tác (Edpuzzle / H5P Style)"])

    # ========================================================
    # TAB 1: NHÓM AI SINH VIDEO (3 NHÓM CHUYÊN BIỆT)
    # ========================================================
    with tab1:
        st.markdown("#### Xây dựng Kịch bản tối ưu hóa cho từng Công cụ AI")
        
        with st.container(border=True):
            chu_de_video = st.text_input("Chủ đề bài học / Nội dung Video:", placeholder="VD: Khám phá hệ mặt trời, Sóng thần hình thành như thế nào, Đối thoại lịch sử...")
            
            col_nhom, col_doi_tuong = st.columns(2)
            with col_nhom:
                nhom_cong_cu = st.selectbox(
                    "Chọn Nhóm Công cụ AI mục tiêu:",
                    [
                        "1️⃣ Điện ảnh & Nghệ thuật (Runway Gen-3, Kling AI, Google Veo 3, Sora, Luma)",
                        "2️⃣ Thuyết trình & Đào tạo - Avatar AI (HeyGen, Synthesia, DeepBrain)",
                        "3️⃣ Tự động hóa & Kịch bản ngắn (InVideo AI, CapCut AI, Canva, Pictory)"
                    ]
                )
            with col_doi_tuong:
                doi_tuong_nhom1 = st.selectbox("Khán giả mục tiêu:", ["Học sinh Tiểu học (Trực quan, sinh động)", "Học sinh THCS (Logic, rõ ràng)", "Học sinh THPT (Học thuật, chuyên sâu)", "Đồng nghiệp / Tổ chuyên môn (Lesson Study)"])

            col_thoi_luong, col_phong_cach = st.columns(2)
            with col_thoi_luong:
                thoi_luong_nhom1 = st.selectbox("Thời lượng video:", ["Dưới 1 phút (Shorts/Reels/TikTok)", "1 - 3 phút (Video bài giảng ngắn)", "3 - 5 phút (Chuyên đề chi tiết)"])
            with col_phong_cach:
                phong_cach_nhom1 = st.selectbox("Phong cách hình ảnh:", ["Điện ảnh thực tế (Cinematic Photorealistic)", "Hoạt hình giáo dục 2D/3D (Animation)", "Tài liệu khoa học (Documentary)", "Bảng trắng / Đồ họa trực quan (Whiteboard/Infographic)"])

            noi_dung_chinh_nhom1 = st.text_area("Các ý chính bắt buộc phải có (Giáo án tóm tắt):", height=90, placeholder="1. Khái niệm, 2. Ví dụ thực tế, 3. Bài học rút ra...")
            
            btn_tao_script_chuyen_sau = st.button("🚀 SINH KỊCH BẢN & PROMPT CHUYÊN SÂU", type="primary", use_container_width=True)

        if btn_tao_script_chuyen_sau:
            if not chu_de_video.strip():
                st.warning("⚠️ Vui lòng nhập chủ đề video.")
            elif AIEngine2 is None:
                st.error("❌ Chưa kết nối AI Engine.")
            else:
                with st.spinner("⏳ AI đang phân tích và lập trình kịch bản tối ưu hóa riêng cho nhóm công cụ đã chọn..."):
                    
                    # Tùy biến prompt theo Nhóm công cụ
                    if "1️⃣ Điện ảnh" in nhom_cong_cu:
                        huong_dan_nhom = """
[ĐẶC THÙ NHÓM 1: ĐIỆN ẢNH & NGHỆ THUẬT - Runway, Kling, Veo, Sora, Luma]
- Tập trung vào cấu trúc phân cảnh (Scene-by-scene).
- Với mỗi cảnh, BẮT BUỘC cung cấp:
  + [Visual Description]: Mô tả hình ảnh điện ảnh bằng tiếng Việt.
  + [Camera & Physics Hint]: Gợi ý chuyển động camera (Pan, Zoom, Dolly) và mô phỏng vật lý (ánh sáng, khói, nước...).
  + [Prompt Tiếng Anh tối ưu]: Viết câu lệnh Prompt tiếng Anh cực kỳ chi tiết, chuẩn cú pháp cho Runway/Sora/Kling (bao gồm thông số khung hình, ánh sáng volumetric, chất lượng 4K).
"""
                    elif "2️⃣ Thuyết trình" in nhom_cong_cu:
                        huong_dan_nhom = """
[ĐẶC THÙ NHÓM 2: THUYẾT TRÌNH & ĐÀO TẠO AVATAR - HeyGen, Synthesia, DeepBrain]
- Tập trung vào kịch bản MC / Giáo viên ảo (Avatar AI).
- Cấu trúc trình bày:
  + [Slide / Slide Layout]: Gợi ý bố cục trên màn hình (vị trí đặt avatar, text, hình ảnh minh họa).
  + [Biểu cảm & Cử chỉ (Gesture)]: Gợi ý hướng dẫn Avatar mỉm cười, nhấn mạnh, hoặc đổi góc nhìn.
  + [Voiceover Script (Lời thoại chi tiết)]: Lời thoại tiếng Việt chuẩn văn phong sư phạm, ngắt nghỉ hợp lý để nạp vào HeyGen/Synthesia.
"""
                    else:
                        huong_dan_nhom = """
[ĐẶC THÙ NHÓM 3: TỰ ĐỘNG HÓA & KỊCH BẢN NGẮN - InVideo, CapCut, Canva, Pictory]
- Tập trung vào tối ưu hóa tốc độ tạo video ngắn (Shorts/Reels).
- Cấu trúc trình bày:
  + [Master Prompt cho InVideo AI]: Câu lệnh tổng quan dài 1 đoạn để dán thẳng vào ô tạo prompt của InVideo AI.
  + [Stock Footage Keywords (Từ khóa tìm kiếm video kho)] : Danh sách từ khóa tiếng Anh để tìm kiếm tư liệu (B-roll) chính xác.
  + [Auto-Caption & Voice Guidelines]: Gợi ý nhạc nền, phong cách phụ đề tự động (CapCut style) và giọng đọc.
"""

                    prompt_script_v2 = f"""
BẠN LÀ MỘT ĐẠO DIỄN SẢN XUẤT VIDEO GIÁO DỤC VÀ CHUYÊN GIA PROMPT ENGINEERING CẤP CAO.
Hãy thiết kế một kịch bản và hệ thống Prompt chuyên sâu dựa trên thông số sau:
- Chủ đề: {chu_de_video}
- Nhóm công cụ AI dự kiến sử dụng: {nhom_cong_cu}
- Khán giả mục tiêu: {doi_tuong_nhom1}
- Thời lượng: {thoi_luong_nhom1}
- Phong cách: {phong_cach_nhom1}
- Nội dung cốt lõi: {noi_dung_chinh_nhom1 if noi_dung_chinh_nhom1 else 'Tự sáng tạo chuẩn kiến thức sư phạm'}

{huong_dan_nhom}

Trình bày kết quả thật mạch lạc bằng Markdown, sử dụng bảng hoặc tiêu đề nổi bật để giáo viên dễ dàng copy sử dụng ngay.
"""
                    try:
                        engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                        res_script = engine_v2.generate_text(prompt_script_v2, temperature=0.7)
                        if res_script.startswith("❌"):
                            st.error(res_script)
                        else:
                            st.session_state["vid_script_result"] = res_script
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {e}")

        # Hiển thị kết quả Tab 1
        if st.session_state["vid_script_result"]:
            st.markdown("---")
            st.markdown("### 🎞️ Kịch bản & Prompt Chuyên sâu theo Công cụ")
            st.markdown(st.session_state["vid_script_result"], unsafe_allow_html=True)
            
            if export_word:
                word_bytes = export_word({"ai_generated_content": st.session_state["vid_script_result"], "is_dkt": False})
                st.download_button(label="📘 Tải Kịch bản & Prompt (.DOCX)", data=word_bytes, file_name="Kich_Ban_Va_Prompt_AI_Video.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="btn_down_script_v2")

    # ========================================================
    # TAB 2: NHÓM VIDEO TƯƠNG TÁC (EDPUZZLE / H5P CLONE)
    # ========================================================
    with tab2:
        st.markdown("#### Trợ lý phân tích và chèn Câu hỏi (Hotspots) vào Video")
        st.caption("Sử dụng thuật toán AI Đa phương tiện để tự động 'xem' video, xác định các điểm cao trào và tạo bộ câu hỏi tương tác khớp với từng giây của video.")
        
        with st.container(border=True):
            upl_interactive_vid = st.file_uploader("Tải lên Video Bài giảng hoặc Tiết học (MP4, MOV):", type=["mp4", "mov"], key="interactive_vid_v2")
            
            if upl_interactive_vid:
                st.video(upl_interactive_vid)
                
            so_diem_tuong_tac = st.slider("Số lượng câu hỏi tương tác muốn chèn:", min_value=2, max_value=10, value=3)
            muc_tieu = st.text_input("Mục tiêu tương tác:", placeholder="VD: Kiểm tra mức độ hiểu bài của học sinh, hoặc Phân tích tình huống sư phạm (cho giáo viên)...")
            
            btn_tao_interactive = st.button("👆 TỰ ĐỘNG PHÂN TÍCH & TẠO ĐIỂM TƯƠNG TÁC (TIMESTAMPS)", type="primary", use_container_width=True)

        if btn_tao_interactive:
            if not upl_interactive_vid:
                st.warning("⚠️ Vui lòng tải Video lên để AI phân tích.")
            elif AIEngine2 is None:
                st.error("❌ Chưa kết nối AI Engine.")
            else:
                with st.spinner(f"⏳ AI (Mắt Thần) đang trực tiếp xem video để tìm ra {so_diem_tuong_tac} vị trí chèn câu hỏi hoàn hảo nhất..."):
                    prompt_interactive = f"""
BẠN LÀ MỘT CHUYÊN GIA CÔNG NGHỆ GIÁO DỤC (EDTECH EXPERT).
Nhiệm vụ của bạn là XEM và NGHE trực tiếp file video đính kèm. 
Hãy xác định chính xác {so_diem_tuong_tac} vị trí (thời điểm - Timestamp) thích hợp nhất để tạm dừng video và chèn một câu hỏi tương tác (Quiz). Mục tiêu: {muc_tieu if muc_tieu else 'Kiểm tra độ tập trung và hiểu nội dung'}.

YÊU CẦU TRÌNH BÀY BÁO CÁO (Trình bày rõ ràng bằng Markdown):
Với mỗi điểm tương tác, hãy định dạng chính xác như sau:

🕒 **Mốc thời gian (Timestamp): [MM:SS]**
- **Sự kiện trong Video lúc này:** (Mô tả ngắn gọn chuyện gì đang xảy ra trên màn hình hoặc người nói vừa nói câu gì).
- **Loại tương tác:** (Trắc nghiệm / Tự luận ngắn / Suy ngẫm).
- **Nội dung Câu hỏi (Pop-up Quiz):** (Đặt câu hỏi dựa đúng vào nội dung vừa trôi qua).
- **Đáp án / Hướng dẫn giải:** (Cung cấp đáp án hoặc gợi ý cho giáo viên).

[KỶ LUẬT]: Thời gian Timestamp BẮT BUỘC phải khớp với diễn biến thực tế của video đính kèm.
"""
                    try:
                        engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                        contents = [prompt_interactive]
                        
                        video_part = {
                            "mime_type": upl_interactive_vid.type,
                            "data": upl_interactive_vid.getvalue()
                        }
                        contents.append(video_part)
                        
                        if hasattr(engine_v2, "generate_multimodal"):
                            res_interactive = engine_v2.generate_multimodal(contents)
                        else:
                            res_interactive = "❌ Cần cập nhật hàm `generate_multimodal` trong `AIEngine2` để nhận file Video."
                            
                        if res_interactive.startswith("❌"):
                            st.error(res_interactive)
                        else:
                            st.session_state["vid_interactive_result"] = res_interactive
                    except Exception as e:
                        st.error(f"Lỗi AI xử lý video: {e}")

        # Hiển thị kết quả Tab 2
        if st.session_state["vid_interactive_result"]:
            st.markdown("---")
            st.markdown("### 👆 Kế hoạch Video Tương tác (Hotspots Timeline)")
            st.success("Tổ IT/Chuyên môn có thể sử dụng cấu trúc Timestamp dưới đây để nạp vào hệ thống Edpuzzle, H5P hoặc Video.js của trường.")
            
            with st.container(border=True):
                st.markdown(st.session_state["vid_interactive_result"], unsafe_allow_html=True)
                
            if export_word:
                word_bytes = export_word({"ai_generated_content": st.session_state["vid_interactive_result"], "is_dkt": False})
                st.download_button(label="📘 Tải Kế hoạch Tương tác (.DOCX)", data=word_bytes, file_name="Video_Tuong_Tac_H5P.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="btn_down_interactive_v2")
