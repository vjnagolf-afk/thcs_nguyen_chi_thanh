# -*- coding: utf-8 -*-
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word của dự án
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

def safe_generate(ai_engine_cu, prompt):
    """
    Hàm gọi AI thông minh: Thử Gemini Flash -> Tự động chuyển sang OpenAI (sk-) nếu hết hạn mức (429).
    """
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

    def run_openai():
        if not api_key:
            raise RuntimeError("Hệ thống chưa được cấu hình API Key OpenAI (sk-).")
        import openai
        client = openai.OpenAI(api_key=str(api_key).strip())
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    def run_gemini():
        try:
            from utils.ai_engine_2 import AIEngine2
            engine_v2 = AIEngine2(default_model="gemini-1.5-flash")
            res = engine_v2.generate_text(prompt, temperature=0.7)
            if res and not res.startswith("❌") and not res.startswith("⚠️") and "429" not in res and "RESOURCE_EXHAUSTED" not in res:
                return res
            raise RuntimeError("Hạn mức Gemini cạn kiệt.")
        except ImportError:
            if ai_engine_cu and hasattr(ai_engine_cu, "generate_text"):
                res = ai_engine_cu.generate_text(prompt)
                if res and not res.startswith("❌") and not res.startswith("⚠️") and "429" not in res and "RESOURCE_EXHAUSTED" not in res:
                    if isinstance(res, dict): return res.get("text", str(res))
                    elif hasattr(res, "text"): return res.text
                    return res
                raise RuntimeError("Hạn mức Gemini cạn kiệt.")
        except Exception as e:
            raise RuntimeError(f"Lỗi máy chủ Google: {str(e)}")
        raise RuntimeError("Google Gemini từ chối kết nối.")

    error_msgs = []
    try:
        return run_gemini()
    except Exception as e1:
        error_msgs.append(f"Gemini: {e1}")
        try:
            return run_openai()
        except Exception as e2:
            error_msgs.append(f"OpenAI: {e2}")
            
    err_str = f"Cả 2 nền tảng AI đều gặp sự cố:\n- {error_msgs[0]}\n- {error_msgs[1]}\n\n👉 Khắc phục: Vui lòng chờ 1 phút để Gemini hồi phục, hoặc thêm khóa `sk-` của OpenAI để hệ thống chạy ổn định 100%."
    raise RuntimeError(err_str)


def render_xd_rubric(ai_engine_cu=None):
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
        if not yeu_cau_can_dat.strip():
            st.warning("⚠️ Vui lòng nhập Yêu cầu cần đạt.")
        else:
            with st.spinner("⏳ AI đang thiết kế ma trận tiêu chí đánh giá chuẩn đo lường giáo dục..."):
                prompt = f"""BẠN LÀ CHUYÊN GIA ĐO LƯỜNG VÀ ĐÁNH GIÁ GIÁO DỤC CẤP CAO.
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
- NẾU có công thức Toán/Lý/Hóa, BẮT BUỘC dùng chuẩn LaTeX bọc trong dấu `$ ... $`. Cấm dùng backtick (`)."""
                
                try:
                    # GỌI HÀM AN TOÀN ĐÃ CÓ FALLBACK
                    res = safe_generate(ai_engine_cu, prompt)
                    st.session_state["rubric_result"] = res
                    st.session_state["rubric_topic"] = loai_nhiem_vu.replace(" ", "_")
                except Exception as e:
                    st.error(f"❌ {e}")

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
