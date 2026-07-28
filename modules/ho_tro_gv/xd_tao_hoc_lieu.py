# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_tao_hoc_lieu.py
Nhiệm vụ: Trợ lý Kỹ sư Câu lệnh (Prompt Engineering) & Tạo Học Liệu.
Chức năng: Sinh ra các siêu câu lệnh (Meta Prompt) dựa trên lý luận chuẩn:
Zero-shot, Few-shot, Chain-of-Thought, Multimodal...
ĐÃ FIX TÊN HÀM ĐỂ KHỚP VỚI HỆ THỐNG APP.PY GỐC.
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

def render_xd_tao_hoc_lieu(ai_engine_cu=None):
    if "prompt_result" not in st.session_state:
        st.session_state["prompt_result"] = None
    if "prompt_topic" not in st.session_state:
        st.session_state["prompt_topic"] = "Sieu_Prompt"

    st.markdown("### 🧠 Lò Luyện Siêu Câu Lệnh (Prompt Engineering)")
    st.info("💡 **Góc chuyên gia (Meta-Prompting):** Đây là nơi Thầy/Cô tạo ra những câu lệnh (Prompt) đỉnh cao nhất để điều khiển bất kỳ AI nào (ChatGPT, Midjourney, Claude...). Hãy thiết lập kỹ thuật và AI sẽ đúc kết thành một câu lệnh hoàn hảo cho Thầy/Cô copy.")

    with st.container(border=True):
        st.markdown("#### 1. Định hình Kiến trúc Câu lệnh")
        col1, col2 = st.columns(2)
        with col1:
            linh_vuc = st.selectbox("Lĩnh vực / Mục đích:", [
                "Soạn thảo Văn bản / Kế hoạch / Sáng kiến",
                "Thiết kế Bài giảng (KHBD) / Đề kiểm tra",
                "Sáng tạo Kịch bản / Kể chuyện / MC",
                "Thiết kế Hình ảnh / Video (Midjourney, Veo, Sora)",
                "Lập trình / Phân tích Dữ liệu",
                "Khác (Tự do sáng tạo)"
            ])
            
            ky_thuat = st.selectbox("Kỹ thuật Prompting (Độ phức tạp):", [
                "Zero-shot (Yêu cầu trực tiếp, không cần mẫu)",
                "One-shot (Cung cấp 1 ví dụ chuẩn để AI bắt chước)",
                "Few-shot / Multi-shot (Đưa nhiều mẫu, định dạng phức tạp)",
                "Chain-of-Thought (Bắt AI tư duy logic từng bước một)"
            ])
            
        with col2:
            the_thuc = st.selectbox("Định dạng dữ liệu (Modality):", [
                "Text Prompt (Thuần văn bản tiếng Việt/Anh)",
                "Image Prompt (Lệnh vẽ ảnh tĩnh bằng tiếng Anh)",
                "Video/Audio Prompt (Lệnh tạo chuyển động, lồng tiếng)",
                "Multimodal (Kết hợp phân tích ảnh và sinh văn bản)"
            ])
            
            vai_tro = st.text_input(
                "Đóng vai (System Prompt):", 
                placeholder="VD: Một chuyên gia giáo dục 20 năm kinh nghiệm, Đạo diễn Hollywood..."
            )

        st.markdown("#### 2. Cốt lõi Yêu cầu")
        yeu_cau = st.text_area(
            "Thầy/Cô muốn AI làm công việc gì cụ thể?", 
            height=120, 
            placeholder="VD: Viết một sáng kiến kinh nghiệm về chuyển đổi số trong giáo dục, cấu trúc 3 chương. Hoặc: Tạo một bức ảnh 1 lớp học tương lai phong cách Cyberpunk..."
        )
        
        btn_tao = st.button("🪄 ĐÚC KẾT SIÊU CÂU LỆNH (META PROMPT)", type="primary", use_container_width=True)

    # XỬ LÝ SỰ KIỆN NÚT BẤM
    if btn_tao:
        if AIEngine2 is None:
            st.error("❌ Không tìm thấy file `utils/ai_engine_2.py`.")
            return

        if not yeu_cau.strip():
            st.warning("⚠️ Vui lòng nhập cốt lõi yêu cầu để AI có chất liệu đúc kết câu lệnh.")
        else:
            with st.spinner("⏳ AI đang vận dụng các kỹ thuật Prompt Engineering để tối ưu hóa câu lệnh của Thầy/Cô..."):
                bq = "```" # Thủ thuật tránh lỗi markdown xé toạc giao diện
                
                prompt = f"""
BẠN LÀ MỘT KỸ SƯ CÂU LỆNH (PROMPT ENGINEER) HÀNG ĐẦU THẾ GIỚI.
Nhiệm vụ của bạn là lấy ý tưởng thô của người dùng và viết ra một SIÊU CÂU LỆNH (MASTER PROMPT) hoàn chỉnh, sắc bén nhất để người dùng copy và dán vào các AI khác (ChatGPT, Midjourney, Claude...).

--- THÔNG SỐ KIẾN TRÚC ---
- Lĩnh vực: {linh_vuc}
- Vai trò AI cần nhập (System Role): {vai_tro if vai_tro.strip() else 'Một chuyên gia xuất sắc nhất trong lĩnh vực này'}
- Định dạng đích: {the_thuc}
- Kỹ thuật ép buộc: {ky_thuat}
- Ý tưởng cốt lõi của người dùng: {yeu_cau}

--- QUY TẮC THIẾT KẾ PROMPT ---
1. Nếu là **Zero-shot**: Lệnh phải cực kỳ rõ ràng, súc tích, quy định đủ tone giọng và đầu ra.
2. Nếu là **One-shot/Few-shot**: BẮT BUỘC bạn phải tự sáng tác ra 1 hoặc vài Ví dụ (Examples) chuẩn mực chèn vào prompt để làm mẫu cho AI kia học theo.
3. Nếu là **Chain-of-Thought (CoT)**: Trong câu lệnh BẮT BUỘC phải chứa các câu thần chú ép AI tư duy, ví dụ: "Hãy suy nghĩ từng bước một (Let's think step by step)", hoặc "Phân tích nguyên nhân trước khi đưa ra kết luận".
4. Nếu là **Image/Video Prompt**: BẮT BUỘC phải viết bằng Tiếng Anh (chuẩn cú pháp Midjourney/Sora với các thông số như --ar 16:9, --v 6.0, lighting, camera angle).

--- CẤU TRÚC ĐẦU RA ---
Hãy trình bày ĐÚNG theo định dạng sau:

### 🌟 PHÂN TÍCH KỸ THUẬT (Dành cho Giáo viên)
(Giải thích nhanh trong 2-3 câu tại sao câu lệnh bạn sắp viết lại hiệu quả với kỹ thuật {ky_thuat}).

### 📋 SIÊU CÂU LỆNH CỦA BẠN (Sẵn sàng Copy)
(Sử dụng Code Block {bq}text và {bq} để bọc câu lệnh lại cho dễ Copy).
{bq}text
[Viết toàn bộ nội dung Prompt hoàn chỉnh vào đây. Đã bao gồm System Prompt thiết lập vai trò, các ràng buộc kỹ thuật, ví dụ mẫu (nếu có) và yêu cầu thực thi].
{bq}
"""
                try:
                    engine_v2 = AIEngine2(default_model="gemini-2.5-pro") 
                    res = engine_v2.generate_text(prompt, temperature=0.6)
                    
                    if res.startswith("❌") or res.startswith("⚠️"):
                        st.error(res)
                    else:
                        st.session_state["prompt_result"] = res
                        st.session_state["prompt_topic"] = linh_vuc.split("/")[0].strip().replace(" ", "_")
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ & XUẤT FILE WORD
    # ========================================================
    if st.session_state.get("prompt_result"):
        st.markdown("---")
        st.success("✅ Đã đúc kết thành công! Thầy/Cô chỉ cần bấm nút Copy ở góc viền xám để lấy câu lệnh.")
        
        st.markdown(st.session_state["prompt_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Lưu trữ Bộ Prompt")
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 TẢI FILE TEXT (.TXT)",
                data=st.session_state["prompt_result"],
                file_name=f"Sieu_Prompt_{st.session_state['prompt_topic']}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        with col2:
            if export_word is None:
                st.warning("⚠️ Module Word chưa sẵn sàng.")
            else:
                try:
                    export_data = {
                        "ai_generated_content": st.session_state["prompt_result"],
                        "is_dkt": False
                    }
                    with st.spinner("Đang kết xuất file Word..."):
                        word_bytes = export_word(export_data)
                    
                    safe_name = st.session_state.get("prompt_topic", "Sieu_Prompt")
                    st.download_button(
                        label="📘 TẢI FILE WORD (.DOCX)",
                        data=word_bytes,
                        file_name=f"Sieu_Prompt_{safe_name}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Lỗi xuất Word: {e}")
                    
        if st.button("🔄 Xóa bản nháp và tạo Prompt mới", use_container_width=True):
            st.session_state["prompt_result"] = None
            st.rerun()
