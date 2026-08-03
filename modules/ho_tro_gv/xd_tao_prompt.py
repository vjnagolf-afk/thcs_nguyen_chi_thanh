# -*- coding: utf-8 -*-
import streamlit as st

# ============================================================
# HỆ SINH THÁI CÁC NHÓM AI & GỢI Ý CÔNG CỤ
# ============================================================
AI_CATEGORIES = {
    "🤖 AI Đa Năng (LLM)": {
        "desc": "Các trợ lý ngôn ngữ lớn điều phối chính, xử lý văn bản, giải quyết vấn đề đa lĩnh vực.",
        "tools": "- **ChatGPT (GPT-4o/5.5):** Trợ lý điều phối chính, lập kế hoạch, phân tích yêu cầu xuất sắc.\n- **Claude 3.5 Sonnet:** Bá chủ về lập luận, viết lách tự nhiên và lập trình.\n- **Gemini 1.5 Pro:** Tích hợp sâu Google Drive, Docs, Sheets, tra cứu thông tin siêu tốc."
    },
    "👨‍🏫 AI Cho Giáo Viên (EdTech)": {
        "desc": "Các công cụ chuyên biệt tối ưu hóa nghiệp vụ sư phạm.",
        "tools": "- **MagicSchool AI:** Số 1 về Lập kế hoạch bài học, ma trận đề, rubric.\n- **Quizizz AI:** Tạo trò chơi kiểm tra bài cũ nhanh chóng.\n- **NotebookLM:** Xây dựng kho tri thức (RAG) từ SGK, trả lời chính xác theo tài liệu nhà trường."
    },
    "🎨 AI Tạo Hình Ảnh": {
        "desc": "Sinh hình ảnh minh họa, sơ đồ, nghệ thuật trực quan cho bài giảng.",
        "tools": "- **Midjourney:** Đỉnh cao tạo ảnh nghệ thuật, siêu thực.\n- **DALL·E 3 / Flux:** Xuất sắc trong việc tạo hình minh họa, sơ đồ bám sát ngữ cảnh."
    },
    "📊 AI Thuyết Trình": {
        "desc": "Thiết kế Slide bài giảng điện tử tự động, chuyên nghiệp.",
        "tools": "- **Gamma AI:** Tạo slide siêu tốc, bố cục hiện đại.\n- **Tome / Canva AI:** Trực quan, dễ dàng tùy biến cho giáo viên."
    },
    "📚 AI Nghiên Cứu": {
        "desc": "Hỗ trợ tra cứu tài liệu học thuật, tổng hợp luận văn, sáng kiến.",
        "tools": "- **NotebookLM:** Hỏi đáp trực tiếp trên kho tài liệu PDF/Word tải lên.\n- **Perplexity / Consensus:** Cỗ máy tìm kiếm có trích dẫn nguồn học thuật rõ ràng."
    },
    "📐 AI Chuyên Toán": {
        "desc": "Giải toán, chứng minh định lý, vẽ đồ thị hàm số.",
        "tools": "- **DeepSeek:** Đỉnh cao giải toán logic, tối ưu chi phí xử lý mảng lớn.\n- **ChatGPT (GPT-4o) / Mathway:** Hỗ trợ từng bước giải chi tiết."
    },
    "💻 AI Lập Trình": {
        "desc": "Sinh mã nguồn, gỡ lỗi (debug), viết script hỗ trợ giảng dạy.",
        "tools": "- **DeepSeek Coder:** Viết code cực chuẩn, giải quyết thuật toán tốt.\n- **Claude 3.5 Sonnet / GitHub Copilot:** Tạo game học tập, ứng dụng web nhỏ cho lớp học."
    },
    "📈 AI Phân Tích Dữ Liệu": {
        "desc": "Xử lý bảng điểm, thống kê kết quả học tập, vẽ biểu đồ.",
        "tools": "- **ChatGPT (Advanced Data Analysis):** Xử lý file Excel/CSV bảng điểm xuất sắc.\n- **Gemini Advanced:** Liên kết trực tiếp với Google Sheets."
    },
    "🎬 AI Tạo Video": {
        "desc": "Sinh video từ văn bản, hình ảnh để minh họa bài giảng sinh động.",
        "tools": "- **Sora / Kling AI:** Sinh video chân thực từ văn bản.\n- **Runway Gen-3 / Pika:** Tạo hiệu ứng, minh họa hiện tượng Vật lý/Hóa học."
    },
    "🎵 AI Tạo Âm Thanh": {
        "desc": "Tạo nhạc nền, bài hát học tập, chuyển văn bản thành giọng nói.",
        "tools": "- **Suno / Udio:** Sáng tác bài hát theo chủ đề môn học.\n- **ElevenLabs:** Lồng tiếng (Voiceover) siêu thực cho video bài giảng."
    },
    "🌍 AI Dịch Thuật": {
        "desc": "Dịch thuật tài liệu ngoại văn, bản ngữ hóa chuyên ngành.",
        "tools": "- **DeepL:** Dịch ngữ cảnh chuyên sâu, mượt mà.\n- **Claude 3.5 Sonnet:** Dịch và giữ nguyên định dạng văn bản học thuật."
    },
    "🖌️ AI Thiết Kế": {
        "desc": "Làm poster, infographic, banner lớp học.",
        "tools": "- **Canva AI / Adobe Firefly:** Thiết kế nhanh, có sẵn template giáo dục."
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
        try: 
            return run_openai()
        except Exception: 
            return run_gemini()
    else:
        try: 
            return run_gemini()
        except Exception: 
            return run_openai()

# ============================================================
# GIAO DIỆN CHÍNH
# ============================================================
def render_xd_tao_prompt(ai_engine=None):
    st.markdown("### 🧠 Siêu Trung Tâm AI & Khởi tạo Prompt Sư phạm")
    st.caption("AI đóng vai trò 'Prompt Engineer' để giúp bạn viết ra những câu lệnh giao tiếp hoàn hảo với các nền tảng AI khác trên thế giới.")
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("#### 🎯 Lựa chọn nền tảng")
        nhom_ai = st.selectbox("Bạn đang muốn sử dụng nhóm AI nào?", list(AI_CATEGORIES.keys()))
        
        model_name = st.selectbox(
            "Động cơ sinh Prompt:", 
            ["Gemini 1.5 Flash (Tốc độ)", "Gemini 1.5 Pro (Sâu sắc)", "GPT-4o Mini", "GPT-4o (Cao cấp)"]
        )
        
        st.info(f"**💡 Chức năng:** {AI_CATEGORIES[nhom_ai]['desc']}\n\n**🚀 Công cụ khuyến nghị:**\n{AI_CATEGORIES[nhom_ai]['tools']}")

    with col2:
        st.markdown("#### ✍️ Trình bày ý tưởng")
        chi_tiet = st.text_area(
            "Ý tưởng thô của bạn (Nói nôm na, càng nhiều chi tiết càng tốt):", 
            height=180, 
            placeholder="VD: Tôi muốn dùng Midjourney tạo hình ảnh một tế bào thực vật 3D, phong cách Pixar, nhìn sinh động để làm slide..."
        )
        
        btn_prompt = st.button("🪄 Tối Ưu Hóa & Sinh Prompt Chuẩn", type="primary", use_container_width=True)

    if btn_prompt:
        if not chi_tiet.strip():
            st.warning("⚠️ Vui lòng trình bày ý tưởng thô của bạn trước khi bấm tạo.")
        else:
            with st.spinner(f"Đang biến ý tưởng thành Siêu Prompt chuyên dụng cho {nhom_ai}..."):
                lang_instruction = "Viết bằng TIẾNG VIỆT rõ ràng, chuẩn sư phạm."
                if "Hình Ảnh" in nhom_ai or "Video" in nhom_ai or "Âm Thanh" in nhom_ai:
                    lang_instruction = "Viết bằng TIẾNG ANH (Vì các AI tạo Ảnh/Video/Âm thanh chỉ hiểu tốt tiếng Anh)."
                
                # Nối chuỗi để an toàn tuyệt đối khi biên dịch Python
                prompt_engineer_task = (
                    f'Bạn là một "Siêu Chuyên gia Kỹ thuật Kích hoạt" (Master Prompt Engineer) cấp thế giới.\n'
                    f'Một giáo viên đang muốn sử dụng công cụ thuộc nhóm: {nhom_ai}\n'
                    f'Ý tưởng thô của giáo viên: "{chi_tiet}"\n\n'
                    f'NHIỆM VỤ CỦA BẠN:\n'
                    f'1. Xác định công cụ phù hợp nhất trong nhóm này để thực hiện ý tưởng.\n'
                    f'2. Viết lại ý tưởng thô thành MỘT ĐOẠN PROMPT HOÀN CHỈNH, TUYỆT HẢO NHẤT để giáo viên copy và dán vào công cụ đó.\n'
                    f'3. {lang_instruction}\n\n'
                    f'CẤU TRÚC ĐẦU RA BẮT BUỘC:\n\n'
                    f'### 🛠️ GỢI Ý CÔNG CỤ SỬ DỤNG\n'
                    f'(Chỉ đích danh công cụ tốt nhất. Ví dụ: Bạn nên copy lệnh này dán vào ChatGPT / Midjourney / Gamma AI...)\n\n'
                    f'### 📝 PROMPT ĐÃ TỐI ƯU (Bấm nút Copy ở góc phải)\n'
                    f'```text\n'
                    f'(Viết toàn bộ nội dung Prompt vào đây. \n'
                    f'Nếu là LLM Text: Phải có Role, Context, Task, Format, Constraints.\n'
                    f'Nếu là Midjourney/Tạo ảnh: Phải có Subject, Environment, Lighting, Style, Parameters như --ar 16:9 --v 6.0)\n'
                    f'```\n\n'
                    f'### 💡 HƯỚNG DẪN THÊM\n'
                    f'(Giải thích ngắn gọn 1-2 câu vì sao Prompt này hiệu quả, hoặc cần thay đổi tham số nào nếu giáo viên muốn tùy biến).'
                )
                
                try:
                    res = call_prompt_engineer(ai_engine, prompt_engineer_task, model_name)
                    st.markdown("---")
                    st.success("🎉 Đã thiết kế xong Siêu Prompt!")
                    st.markdown(res)
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {e}")
