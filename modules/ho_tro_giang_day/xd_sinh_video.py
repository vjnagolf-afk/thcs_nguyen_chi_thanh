# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_sinh_video.py
Nhiệm vụ: Trợ lý AI Sinh Video & Video Tương tác.
Chức năng: 
1. Lên kịch bản & viết Prompt tiếng Anh cho HeyGen/Runway.
2. Thiết kế Video Tương tác (Edpuzzle/H5P style) tự động chèn câu hỏi vào Timestamp.
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
    st.info("💡 **Góc chuyên gia:** Phân hệ gồm 2 công cụ cốt lõi: Tạo kịch bản cho các công cụ Sinh Video AI (HeyGen, Sora, Runway) và Thiết kế Video Tương tác (chèn câu hỏi tự động theo mốc thời gian như Edpuzzle, H5P).")

    # Tạo 2 Tabs cho 2 luồng công việc hoàn toàn khác biệt
    tab1, tab2 = st.tabs(["🎥 1. Lên Kịch bản & Prompt Sinh Video AI", "👆 2. Thiết kế Video Tương tác (Interactive Video)"])

    # ========================================================
    # TAB 1: NHÓM AI SINH VIDEO (AI VIDEO GENERATION)
    # ========================================================
    with tab1:
        st.markdown("#### Tạo Kịch bản cho Avatar AI hoặc Text-to-Video")
        with st.container(border=True):
            col_info, col_setting = st.columns([1, 1])
            
            with col_info:
                chu_de_video = st.text_input("Chủ đề Video:", placeholder="VD: Khủng hoảng kinh tế 1929, Sự hình thành lỗ đen...")
                đoi_tuong = st.selectbox("Khán giả mục tiêu:", ["Học sinh Tiểu học (Vui nhộn, đơn giản)", "Học sinh THCS (Trực quan, logic)", "Học sinh THPT (Chuyên sâu, học thuật)", "Giáo viên (Đào tạo chuyên môn/Lesson Study)"])
                
            with col_setting:
                cong_cu_ai = st.selectbox(
                    "Định hướng công cụ AI sẽ sử dụng:", 
                    [
                        "🤖 Giáo viên Ảo (HeyGen / Synthesia) - Tập trung vào kịch bản MC, biểu cảm.", 
                        "🌌 Cảnh phim chân thực (Runway Gen-3 / Sora / Luma) - Tập trung Prompt góc máy, chuyển động."
                    ]
                )
                thoi_luong = st.selectbox("Thời lượng dự kiến:", ["Short/Reel/TikTok (Dưới 1 phút)", "1 - 3 phút", "3 - 5 phút"])
                
            noi_dung_chinh = st.text_area("Các ý chính bắt buộc phải có trong video (Giáo án tóm tắt):", height=80, placeholder="1. Nguyên nhân, 2. Diễn biến, 3. Hậu quả...")
            
            btn_tao_script = st.button("📝 XÂY DỰNG KỊCH BẢN & PROMPT", type="primary", use_container_width=True)

        if btn_tao_script:
            if not chu_de_video.strip():
                st.warning("⚠️ Vui lòng nhập chủ đề video.")
            elif AIEngine2 is None:
                st.error("❌ Chưa kết nối AI Engine.")
            else:
                with st.spinner("⏳ AI đang phân cảnh và viết Prompt Tiếng Anh chuyên nghiệp..."):
                    prompt_script = f"""
BẠN LÀ MỘT ĐẠO DIỄN PHIM GIÁO DỤC VÀ CHUYÊN GIA PROMPT ENGINEERING.
Hãy viết một kịch bản chi tiết để sản xuất video học tập.
- Chủ đề: {chu_de_video}
- Khán giả: {đoi_tuong}
- Thời lượng: {thoi_luong}
- Công cụ AI dự kiến sử dụng: {cong_cu_ai}
- Nội dung cốt lõi: {noi_dung_chinh if noi_dung_chinh else 'Tự sáng tạo nội dung chuẩn kiến thức'}

YÊU CẦU TRÌNH BÀY (Dạng Bảng Markdown):
Trình bày Kịch bản dưới dạng BẢNG 4 cột:
1. **[Mốc Thời gian]**: Phân chia thời gian hợp lý (VD: 0:00 - 0:15).
2. **[Chỉ đạo Hình ảnh & Cảm xúc]**: Mô tả bằng Tiếng Việt hình ảnh hiển thị trên màn hình.
3. **[AI PROMPT Tiếng Anh]**: BẮT BUỘC có phần này. Viết câu lệnh Prompt chi tiết bằng Tiếng Anh (Camera angle, lighting, motion, character) để người dùng Copy và dán vào Midjourney/Runway/HeyGen.
4. **[Lời thoại / Voiceover]**: Lời thoại Tiếng Việt chi tiết của MC/Giáo viên.
"""
                    try:
                        engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                        res_script = engine_v2.generate_text(prompt_script, temperature=0.7)
                        if res_script.startswith("❌"):
                            st.error(res_script)
                        else:
                            st.session_state["vid_script_result"] = res_script
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {e}")

        # Hiển thị kết quả Tab 1
        if st.session_state["vid_script_result"]:
            st.markdown("---")
            st.markdown("### 🎞️ Kịch bản Video & AI Prompts")
            st.markdown(st.session_state["vid_script_result"], unsafe_allow_html=True)
            
            # Nút xuất file Tab 1
            if export_word:
                word_bytes = export_word({"ai_generated_content": st.session_state["vid_script_result"], "is_dkt": False})
                st.download_button(label="📘 Tải Kịch bản (.DOCX)", data=word_bytes, file_name="Kich_Ban_AI_Video.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="btn_down_script")

    # ========================================================
    # TAB 2: NHÓM VIDEO TƯƠNG TÁC (EDPUZZLE / H5P CLONE)
    # ========================================================
    with tab2:
        st.markdown("#### Trợ lý phân tích và chèn Câu hỏi (Hotspots) vào Video")
        st.caption("Ứng dụng thuật toán AI Đa phương tiện để tự động 'xem' video, xác định các điểm cao trào và tạo bộ câu hỏi tương tác khớp với từng giây của video.")
        
        with st.container(border=True):
            upl_interactive_vid = st.file_uploader("Tải lên Video Bài giảng hoặc Tiết học (MP4, MOV):", type=["mp4", "mov"], key="interactive_vid")
            
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
                
            # Nút xuất file Tab 2
            if export_word:
                word_bytes = export_word({"ai_generated_content": st.session_state["vid_interactive_result"], "is_dkt": False})
                st.download_button(label="📘 Tải Kế hoạch Tương tác (.DOCX)", data=word_bytes, file_name="Video_Tuong_Tac_H5P.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="btn_down_interactive")
