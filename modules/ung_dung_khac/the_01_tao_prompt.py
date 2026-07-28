# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ung_dung_khac/the_01_tao_prompt.py
Nhiệm vụ: Công cụ Tạo Prompt Chuyên Sâu cho Trò Chơi Mô Phỏng Giáo Dục.
Tích hợp: Kết nối trực tiếp với AIEngine3 (`utils/ai_engine_3.py`).
============================================================
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Kết nối bộ xử lý AI từ utils/ai_engine_3.py
try:
    from utils.ai_engine_3 import AIEngine3
except ImportError:
    AIEngine3 = None

def render_the_01(ai_engine=None):
    st.markdown("### 🎮 Công cụ Tạo Prompt Chuyên Sâu cho Trò Chơi Mô Phỏng Giáo Dục")
    st.caption("Thiết kế prompt định hướng chính xác hành vi AI để tạo kịch bản/nguyên mẫu trò chơi phù hợp với từng nền tảng (Canva AI, HTML/JS, hoặc AI đa năng).")

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown("#### ⚙️ Cấu hình tham số thiết kế")
        
        mon_hoc = st.selectbox("Môn học", ["Khoa học Tự nhiên", "Toán học", "Lịch sử & Địa lí", "Công nghệ", "Tin học", "Môn khác"], key="tp_mon")
        lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"], index=2, key="tp_lop")
        chu_de = st.text_input("Tên chủ đề / Bài học", placeholder="Ví dụ: Định luật Ôm, Quang hợp, Hàm số bậc nhất...", key="tp_chude")
        
        muc_tieu = st.text_area("Mục tiêu bài học / Yêu cầu cần đạt", placeholder="Ví dụ: Học sinh hiểu được mối quan hệ giữa U, I, R và biết vận dụng giải bài toán thực tế.", key="tp_ductat")

        nen_tang = st.selectbox(
            "Nền tảng mục tiêu để sử dụng Prompt",
            [
                "Canva AI (Tập trung thiết kế slide tương tác, kịch bản lựa chọn tình huống, infographic bấm chọn)",
                "HTML / JavaScript (Tập trung viết mã nguyên mẫu chạy thanh trượt, tính toán số liệu thực tế)",
                "AI bất kỳ / Kịch bản sư phạm (Xây dựng Tài liệu thiết kế trò chơi GDD hoàn chỉnh)"
            ],
            key="tp_platform"
        )

        phuong_phap = st.selectbox(
            "Phương pháp sư phạm trò chơi",
            [
                "Trò chơi khám phá qua tình huống lựa chọn (Scenario-based / Branching)",
                "Mô phỏng thí nghiệm từng bước (Dự đoán – Thí nghiệm – Quan sát – Kết luận)",
                "Thử thách chinh phục cấp độ (Quiz tương tác kèm hệ thống điểm thưởng)"
            ],
            key="tp_pp"
        )

        btn_tao_prompt = st.button("✨ TẠO PROMPT CHUYÊN SÂU", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### 📋 Prompt cấu trúc tối ưu xuất ra")
        
        if btn_tao_prompt:
            if not chu_de.strip():
                st.warning("⚠️ Vui lòng nhập tên chủ đề hoặc bài học.")
            else:
                with st.spinner("🤖 Hệ thống đang tinh chỉnh prompt qua AIEngine3 theo đúng tiêu chuẩn sư phạm..."):
                    
                    if "Canva AI" in nen_tang:
                        platform_instructions = """
- Dành riêng cho Canva AI (Magic Design / Magic Write / Tạo bản thuyết trình tương tác):
- KHÔNG yêu cầu các tính năng code phức tạp, lập trình vật lý thời gian thực, hay đồ thị số học động mà Canva không hỗ trợ tốt.
- TẬP TRUNG vào: Thiết kế cấu trúc các Slide thuyết trình tương tác, dạng "Trò chơi lựa chọn tình huống" (nếu chọn A dẫn đến Slide X, nếu chọn B dẫn đến Slide Y), các thẻ lật (flip cards), câu hỏi trắc nghiệm nhánh, hoặc các điểm chạm (hotspots) trên infographic để học sinh khám phá kiến thức từng bước.
- Cung cấp rõ: Nội dung hiển thị trên từng slide, hình ảnh minh họa cần tìm kiếm, câu hỏi tương tác và phản hồi cho học sinh.
"""
                    elif "HTML / JavaScript" in nen_tang:
                        platform_instructions = """
- Dành cho AI lập trình (ChatGPT / Claude để xuất mã nguồn HTML/JS):
- Yêu cầu viết một tệp mã nguồn HTML hoàn chỉnh (gồm CSS bên trong và script JavaScript xử lý logic).
- Phải có các phần tử giao diện thực tế: Thanh trượt (slider), nút bấm (button), khung hiển thị kết quả số học động.
- Lập trình rõ quy luật tính toán khoa học chính xác (ví dụ công thức, biến số, hàm cập nhật trạng thái khi người dùng kéo thanh trượt).
"""
                    else:
                        platform_instructions = """
- Dành cho việc xây dựng Tài liệu Thiết kế Trò chơi (Game Design Document - GDD):
- Mô tả toàn bộ kịch bản sư phạm chi tiết: Tên game, cốt truyện/bối cảnh, nhiệm vụ, các biến số, luật chơi, hệ thống điểm số và phần thưởng, bảng câu hỏi và phản hồi chi tiết.
"""

                    prompt_chuyen_sau = f"""
BẠN LÀ CHUYÊN GIA THIẾT KẾ GIÁO DỤC SỐ VÀ KIẾN TẠO TRÒ CHƠI HỌC TẬP (EDTECH DESIGNER).
NHIỆM VỤ: Hãy viết một Prompt hoàn chỉnh, chi tiết và có cấu trúc rõ ràng để tôi copy/dán tiếp vào một AI khác hoặc Canva AI nhằm tạo ra trò chơi mô phỏng giáo dục chất lượng cao.

THÔNG TIN ĐẦU VÀO:
- Môn học & Khối lớp: {mon_hoc} - {lop}
- Chủ đề bài học: {chu_de}
- Mục tiêu cần đạt: {muc_tieu if muc_tieu else 'Khám phá và nắm vững kiến thức trọng tâm của chủ đề.'}
- Phương pháp sư phạm: {phuong_phap}
- Nền tảng thực thi dự kiến: {nen_tang}

QUY TẮC ĐẶC BIỆT CHO NỀN TẢNG NÀY:
{platform_instructions}

YÊU CẦU CẤU TRÚC PROMPT XUẤT RA:
Prompt bạn tạo ra phải có các phần rõ ràng sau để AI tiếp nhận thực hiện ngay lập tức:
1. Bối cảnh & Vai trò của AI thực thi.
2. Mục tiêu trò chơi & Đối tượng học sinh THCS.
3. Cơ chế hoạt động (Biến số, Nhiệm vụ, Thử thách).
4. Kịch bản chi tiết từng màn chơi / từng bước tương tác.
5. Hệ thống phản hồi (Feedback) và Đánh giá kết quả.

Hãy viết bằng tiếng Việt, văn phong chuyên nghiệp, định dạng Markdown rõ ràng.
"""

                    ket_qua_prompt = ""
                    try:
                        # Ưu tiên sử dụng AIEngine3 nếu có sẵn
                        if AIEngine3 is not None:
                            engine_v3 = AIEngine3()
                            if hasattr(engine_v3, "generate_text"):
                                ket_qua_prompt = engine_v3.generate_text(prompt_chuyen_sau)
                            else:
                                ket_qua_prompt = engine_v3.generate(prompt_chuyen_sau) # Dự phòng phương thức gọi khác
                        elif ai_engine is not None and hasattr(ai_engine, "generate_text"):
                            ket_qua_prompt = ai_engine.generate_text(prompt_chuyen_sau)
                        else:
                            raise Exception("Không tìm thấy engine AI hợp lệ.")
                    except Exception as e:
                        logger.error(f"Lỗi gọi AI3: {e}")
                        # Fallback mẫu chuẩn nếu AI chưa cấu hình key
                        ket_qua_prompt = f"""### MẪU PROMPT CHUYÊN SÂU TẠO TRÒ CHƠI CHO NỀN TẢNG: {nen_tang}

**Chủ đề:** {chu_de} ({mon_hoc} - {lop})
**Mục tiêu:** {muc_tieu}

*(Hệ thống sử dụng prompt mẫu tiêu chuẩn do chưa kết nối được API Key trực tiếp)*

---
**NỘI DUNG PROMPT CẦN COPY:**
Hãy đóng vai một chuyên gia thiết kế trò chơi giáo dục và giáo viên sáng tạo môn {mon_hoc} lớp {lop}. 
Hãy thiết kế một trò chơi mô phỏng dạng {phuong_phap} cho chủ đề: "{chu_de}".

Yêu cầu cụ thể:
1. **Nhiệm vụ học tập:** Thiết kế 3 thử thách từ dễ đến khó gắn liền với đời sống thực tế.
2. **Cơ chế tương tác:** Xác định rõ các bước học sinh tương tác (ví dụ: đọc tình huống -> đưa ra dự đoán -> chọn phương án/kéo thả -> nhận phản hồi giải thích).
3. **Phản hồi sư phạm:** Khi học sinh chọn đúng hoặc sai, hệ thống phải đưa ra lời giải thích ngắn gọn về bản chất khoa học.
4. **Trình bày:** Phù hợp hoàn hảo để tạo bản thuyết trình tương tác trên Canva (các slide phân nhánh, không yêu cầu code phức tạp).
"""

                    st.session_state["tp_ket_qua_prompt"] = ket_qua_prompt
                    st.success("🎉 Đã thiết kế thành công Prompt chuyên sâu qua AIEngine3!")

        if "tp_ket_qua_prompt" in st.session_state:
            st.text_area("Nội dung Prompt chuyên sâu:", value=st.session_state["tp_ket_qua_prompt"], height=400)
            st.download_button(
                "📥 Tải xuống tệp Prompt (.txt)",
                data=st.session_state["tp_ket_qua_prompt"],
                file_name=f"PromptChuyenSau_{chu_de.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("💡 Điền thông tin bên cột trái và bấm nút để khởi tạo Prompt tối ưu.")
