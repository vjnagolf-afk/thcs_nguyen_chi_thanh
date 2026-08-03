# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: views/xd_tao_prompt.py
Nhiệm vụ: Siêu Trung Tâm Tạo Prompt & Gợi ý Công cụ AI Đa Năng
Nâng cấp: "Zero-Edit" Meta-Templates cho KHBD, Đề, Slide, Video.
============================================================
"""

import streamlit as st

# ============================================================
# HỆ SINH THÁI CÁC NHÓM AI & GỢI Ý CÔNG CỤ
# ============================================================
AI_CATEGORIES = {
    "🤖 AI Đa Năng (LLM) & Viết Giáo án, Đề thi": {
        "desc": "Sinh giáo án, đề kiểm tra, lên ý tưởng kịch bản bằng văn bản.",
        "tools": "- **ChatGPT (GPT-4o) / Claude 3.5:** Copy Prompt dán vào đây để ra giáo án, đề kiểm tra chuẩn nhất."
    },
    "📊 AI Thuyết Trình (Làm Slide)": {
        "desc": "Thiết kế Slide bài giảng điện tử tự động, chuyên nghiệp.",
        "tools": "- **Gamma AI / Canva:** Copy Prompt dán vào tính năng 'Generate from Text' để AI tự dàn trang slide."
    },
    "🎬 AI Tạo Video Giáo Dục": {
        "desc": "Sinh video từ văn bản, hình ảnh kết hợp lời thoại.",
        "tools": "- **Veo / Sora / Kling (Hình ảnh):** Dùng phần Visual Prompt tiếng Anh.\n- **Vbee / ElevenLabs (Âm thanh):** Dùng phần Lời thoại tiếng Việt."
    },
    "👨‍🏫 AI Cho Giáo Viên (EdTech)": {
        "desc": "Các công cụ chuyên biệt tối ưu hóa nghiệp vụ sư phạm.",
        "tools": "- **MagicSchool AI:** Tối ưu hóa ma trận đề, rubric.\n- **NotebookLM:** Xây dựng kho tri thức (RAG) từ SGK."
    },
    "🎨 AI Tạo Hình Ảnh": {
        "desc": "Sinh hình ảnh minh họa, sơ đồ, nghệ thuật trực quan cho bài giảng.",
        "tools": "- **Midjourney / DALL·E 3 / Flux:** Dán Prompt vào để tạo ảnh minh họa SGK, tế bào, sự kiện lịch sử."
    },
    "📐 AI Chuyên Toán & Lập Trình": {
        "desc": "Giải toán, chứng minh định lý, vẽ đồ thị hàm số, viết code.",
        "tools": "- **DeepSeek / Claude 3.5 Sonnet:** Dán Prompt để giải toán, tạo mã HTML nhúng game học tập."
    },
    "📈 AI Phân Tích Dữ Liệu": {
        "desc": "Xử lý bảng điểm, thống kê kết quả học tập, vẽ biểu đồ.",
        "tools": "- **ChatGPT (Advanced Data Analysis):** Dán Prompt kèm file Excel bảng điểm để AI phân tích."
    }
}

# ============================================================
# HÀM GỌI AI THÔNG MINH (CROSS-ROUTING FALLBACK)
# ============================================================
def call_prompt_engineer(ai_engine, prompt, model_name="Gemini 1.5 Flash"):
    is_openai_preferred = "GPT" in model_name
    openai_model = "gpt-4o" if ("Pro" in model_name or "GPT-4o (" in model_name) else "gpt-4o-mini"
    
    def run_openai():
        api_key = None
        for key, val in st.session_state.items():
            if isinstance(val, str) and val.startswith("sk-"):
                api_key = val
                break
        if not api_key:
            for k in ["user_api_key", "api_key", "openai_api_key", "sk_key"]:
                if st.session_state.get(k) and str(st.session_state.get(k)).startswith("sk-"):
                    api_key = st.session_state.get(k)
                    break
        if not api_key and "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]

        if api_key:
            import openai
            client = openai.OpenAI(api_key=str(api_key).strip())
            response = client.chat.completions.create(
                model=openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        raise RuntimeError("Không có API Key OpenAI (sk-).")

    def run_gemini():
        try:
            from utils.ai_engine_2 import AIEngine2
            gemini_model = "gemini-2.5-pro" if "Pro" in model_name else "gemini-2.5-flash"
            engine_v2 = AIEngine2(default_model=gemini_model)
            res = engine_v2.generate_text(prompt)
            if res and not res.startswith("❌") and not res.startswith("⚠️") and "429" not in res and "RESOURCE_EXHAUSTED" not in res:
                return res
        except ImportError:
            if ai_engine and hasattr(ai_engine, "generate_text"):
                res = ai_engine.generate_text(prompt)
                if res and "429" not in res and "RESOURCE_EXHAUSTED" not in res and not res.startswith("❌"):
                    if isinstance(res, dict): 
                        return res.get("text", str(res))
                    elif hasattr(res, "text"): 
                        return res.text
                    return res
        raise RuntimeError("Gemini lỗi hoặc quá hạn mức 429.")

    if is_openai_preferred:
        try: return run_openai()
        except Exception: return run_gemini()
    else:
        try: return run_gemini()
        except Exception: return run_openai()

# ============================================================
# GIAO DIỆN CHÍNH
# ============================================================
def render_xd_tao_prompt(ai_engine=None):
    st.markdown("### 🧠 Máy Phát Sinh Prompt Sư Phạm Sẵn Sàng (Zero-Edit)")
    st.caption("Copy và Paste trực tiếp vào ChatGPT, Claude, Gamma hay Sora/Veo mà không cần chỉnh sửa thêm.")
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("#### 🎯 Lựa chọn nền tảng")
        nhom_ai = st.selectbox("Bạn đang muốn sử dụng nhóm AI nào?", list(AI_CATEGORIES.keys()))
        
        model_name = st.selectbox(
            "Động cơ sinh Prompt:", 
            ["Gemini 1.5 Flash (Tốc độ)", "Gemini 1.5 Pro (Sâu sắc)", "GPT-4o Mini", "GPT-4o (Cao cấp)"]
        )
        
        st.info(f"**💡 Chức năng:** {AI_CATEGORIES[nhom_ai]['desc']}\n\n**🚀 Nơi dán Prompt:**\n{AI_CATEGORIES[nhom_ai]['tools']}")

    with col2:
        st.markdown("#### ✍️ Trình bày ý tưởng ngắn gọn")
        chi_tiet = st.text_area(
            "Nhập chủ đề hoặc yêu cầu thô (AI sẽ tự động đắp khuôn mẫu chuyên nghiệp):", 
            height=180, 
            placeholder="- Nếu làm KHBD: Soạn giáo án bài Định lý Pytago lớp 8.\n- Nếu làm Slide: Slide bài Hệ tuần hoàn sinh học 8.\n- Nếu làm Đề: 20 câu trắc nghiệm Lịch sử 9 phong trào Cần Vương.\n- Nếu làm Video: Video về sự hình thành mưa."
        )
        
        btn_prompt = st.button("🪄 TẠO PROMPT COPY-PASTE NGAY", type="primary", use_container_width=True)

    if btn_prompt:
        if not chi_tiet.strip():
            st.warning("⚠️ Vui lòng nhập ý tưởng thô của bạn trước khi bấm tạo.")
        else:
            with st.spinner(f"Đang đúc khuôn Meta-Template cho {nhom_ai}..."):
                
                # SIÊU PROMPT ÉP KHUÔN SƯ PHẠM TRỰC TIẾP
                prompt_engineer_task = (
                    f'Bạn là "Master Prompt Engineer" chuyên phục vụ giáo viên Việt Nam.\n'
                    f'Giáo viên yêu cầu: "{chi_tiet}"\n'
                    f'Nhóm công cụ mục tiêu: {nhom_ai}\n\n'
                    f'NHIỆM VỤ: Sinh ra MỘT ĐOẠN PROMPT DUY NHẤT để giáo viên COPY và PASTE thẳng vào AI mục tiêu (ChatGPT, Gamma, Veo...) MÀ KHÔNG CẦN CHỈNH SỬA THÊM.\n\n'
                    f'BẮT BUỘC PHẢI NHÚNG CÁC LUẬT SAU VÀO TRONG PROMPT BẠN TẠO RA DỰA THEO LOẠI YÊU CẦU:\n\n'
                    f'1. NẾU LÀ VIẾT GIÁO ÁN (KẾ HOẠCH BÀI DẠY):\n'
                    f'Prompt tạo ra phải ép AI mục tiêu: Đóng vai chuyên gia giáo dục, tuân thủ tuyệt đối cấu trúc Công văn 5512 gồm 4 hoạt động: 1. Mở đầu, 2. Hình thành kiến thức mới, 3. Luyện tập, 4. Vận dụng. Mỗi hoạt động phải có đủ 4 mục (Mục tiêu, Nội dung, Sản phẩm, Tổ chức thực hiện).\n\n'
                    f'2. NẾU LÀ LÀM ĐỀ KIỂM TRA:\n'
                    f'Prompt tạo ra phải ép AI mục tiêu: Bám sát ma trận nhận thức (Nhận biết, Thông hiểu, Vận dụng). Câu hỏi trắc nghiệm phải có 4 đáp án A, B, C, D (không dùng số 1234), bôi đậm đáp án đúng và xuất kèm Bảng đáp án, giải thích chi tiết ở cuối.\n\n'
                    f'3. NẾU LÀ LÀM SLIDE BÀI GIẢNG (Cho Gamma AI / ChatGPT):\n'
                    f'Prompt tạo ra phải ép AI mục tiêu: Dàn dàn ý chi tiết cho 10-15 slide bằng Markdown. Mỗi slide phải ngắn gọn, chỉ dùng gạch đầu dòng (bullet points), không viết đoạn văn dài. Phải kèm theo dòng [Gợi ý hình ảnh: ...] bằng tiếng Anh để Gamma AI tự tìm ảnh.\n\n'
                    f'4. NẾU LÀ TẠO VIDEO GIÁO DỤC (Cho Veo/Sora + AI Lồng tiếng):\n'
                    f'Prompt tạo ra phải kẻ một BẢNG 3 CỘT. Cột 1: Thời gian (Giây). Cột 2: Visual Prompt (Mô tả hình ảnh bằng Tiếng Anh cực kỳ chi tiết, góc máy, ánh sáng để dán vào AI Video). Cột 3: Voiceover Script (Kịch bản lời thoại bằng Tiếng Việt, câu từ truyền cảm để dán vào AI Lồng tiếng).\n\n'
                    f'5. NẾU LÀ TẠO HÌNH ẢNH MINH HỌA:\n'
                    f'Prompt tạo ra phải 100% bằng TIẾNG ANH, cấu trúc theo thứ tự: Subject, Environment, Lighting, Color palette, Style, Camera angle.\n\n'
                    f'ĐẦU RA BẮT BUỘC THEO ĐÚNG CẤU TRÚC SAU:\n\n'
                    f'### 🛠️ NƠI SỬ DỤNG LỆNH NÀY\n'
                    f'(Chỉ định tên công cụ nên dán vào)\n\n'
                    f'### 📝 COPY TOÀN BỘ KHỐI BÊN DƯỚI DÁN VÀO AI\n'
                    f'```text\n'
                    f'(Nội dung Prompt siêu tối ưu của bạn)\n'
                    f'```'
                )
                
                try:
                    res = call_prompt_engineer(ai_engine, prompt_engineer_task, model_name)
                    st.markdown("---")
                    st.success("🎉 Đã tạo Prompt thành công! Thầy/cô chỉ việc copy khối text bên dưới và dán vào công cụ tương ứng.")
                    st.markdown(res)
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {e}")
