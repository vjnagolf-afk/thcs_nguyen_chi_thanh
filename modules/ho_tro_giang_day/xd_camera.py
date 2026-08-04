# -*- coding: utf-8 -*-
import io
import logging
import streamlit as st
import base64
from PIL import Image

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2 để dùng tính năng Multimodal
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# Hàm chuyển đổi ảnh PIL sang Base64 chuẩn OpenAI
def get_base64_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# HÀM CROSS-ROUTING FALLBACK CHỐNG LỖI 429 CHO CAMERA (VISION)
def safe_generate_vision(ai_engine_cu, prompt, image_pil):
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
            raise RuntimeError("Chưa cấu hình API Key OpenAI (sk-) để dự phòng ảnh.")
        import openai
        client = openai.OpenAI(api_key=str(api_key).strip())
        
        # Chuyển ảnh sang dạng OpenAI đọc được
        base64_img = get_base64_image(image_pil)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_img}"
                            },
                        },
                    ],
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    def run_gemini():
        try:
            from utils.ai_engine_2 import AIEngine2
            engine_v2 = AIEngine2(default_model="gemini-1.5-flash")
            
            # Chuẩn bị dữ liệu cho Gemini
            buffered = io.BytesIO()
            image_pil.save(buffered, format="JPEG")
            img_bytes = buffered.getvalue()
            
            image_part = {
                "mime_type": "image/jpeg",
                "data": img_bytes
            }
            contents = [prompt, image_part]
            
            if hasattr(engine_v2, "generate_multimodal"):
                res = engine_v2.generate_multimodal(contents)
            else:
                raise RuntimeError("❌ File `utils/ai_engine_2.py` thiếu hàm `generate_multimodal`.")
                
            if res and not res.startswith("❌") and not res.startswith("⚠️") and "429" not in res and "RESOURCE_EXHAUSTED" not in res:
                return res
            raise RuntimeError("Hạn mức Gemini cạn kiệt.")
        except Exception as e:
            raise RuntimeError(f"Lỗi Gemini Vision: {str(e)}")

    error_msgs = []
    try:
        return run_gemini()
    except Exception as e1:
        error_msgs.append(f"Gemini: {e1}")
        try:
            return run_openai()
        except Exception as e2:
            error_msgs.append(f"OpenAI: {e2}")
            
    err_str = f"Hệ thống quá tải hoặc hết hạn mức:\n- {error_msgs[0]}\n- {error_msgs[1]}\n\n👉 Khắc phục: Chờ 1 phút để Gemini hồi phục, hoặc nạp Key OpenAI (sk-) vào hệ thống."
    raise RuntimeError(err_str)


def render_xd_camera(ai_engine_cu=None):
    if "cam_result" not in st.session_state:
        st.session_state["cam_result"] = None
    if "cam_task" not in st.session_state:
        st.session_state["cam_task"] = ""

    st.markdown("### 📷 Trợ lý AI Camera Nhận diện (Vision AI)")
    st.info("💡 **Góc chuyên gia:** Sử dụng Webcam hoặc Camera trên thiết bị di động để chụp trực tiếp bài làm của học sinh, tài liệu giấy, hoặc không khí lớp học. AI sẽ phân tích hình ảnh và trả về kết quả số hóa ngay lập tức.")

    st.warning("⚠️ LƯU Ý: Tính năng yêu cầu cấp quyền sử dụng Webcam trên trình duyệt. Đã tích hợp chống sập bằng GPT-4o-mini Vision.")
    
    col_cam, col_result = st.columns([1, 1.2], gap="large")
    
    with col_cam:
        st.markdown("#### 📸 Khung thu nhận Hình ảnh")
        enable_cam = st.checkbox("Bật kết nối Camera", value=True)
        img_buffer = None
        
        if enable_cam:
            img_buffer = st.camera_input("Hướng camera vào tài liệu hoặc bài làm")
            
    with col_result:
        st.markdown("#### ⚙️ Trung tâm Xử lý AI")
        
        with st.container(border=True):
            tac_vu = st.radio(
                "Chọn tác vụ phân tích:", 
                [
                    "📝 Chấm điểm & Chữa bài làm (Tự luận/Trắc nghiệm)", 
                    "🖨️ Trích xuất văn bản & Số hóa (OCR)", 
                    "🤔 Phân tích trạng thái / Môi trường học tập"
                ]
            )
            
            yeu_cau_them = st.text_input("Ghi chú thêm cho AI (Tùy chọn):", placeholder="VD: Hãy chú ý vào công thức tính toán ở dòng thứ 2...")
            
            btn_phan_tich = st.button("🧠 PHÂN TÍCH HÌNH ẢNH NÀY", type="primary", use_container_width=True)

        if btn_phan_tich:
            if not img_buffer:
                st.error("❌ Chưa có dữ liệu hình ảnh. Vui lòng cấp quyền Camera và chụp ảnh trước!")
            else:
                with st.spinner("⏳ Khởi động Mắt Thần AI (Vision Model)... đang phân tích hình ảnh chi tiết..."):
                    try:
                        # 1. Chuyển đổi buffer thành đối tượng hình ảnh PIL
                        image = Image.open(img_buffer)
                        
                        # 2. Xây dựng Prompt tương ứng
                        if "Chấm điểm" in tac_vu:
                            prompt_text = f"""BẠN LÀ MỘT GIÁO VIÊN DÀY DẶN KINH NGHIỆM.
Nhiệm vụ của bạn là đọc hình ảnh bài làm của học sinh (viết tay hoặc in) được đính kèm và thực hiện các bước sau:
1. Đọc và phiên mã lại tóm tắt nội dung bài làm.
2. Chỉ ra các lỗi sai (nếu có) về mặt kiến thức, logic hoặc chính tả.
3. Giải thích cặn kẽ cách làm đúng.
4. Đưa ra một điểm số ước lượng và lời nhận xét động viên học sinh.
Ghi chú thêm từ giáo viên: {yeu_cau_them if yeu_cau_them else 'Không có'}
(Lưu ý: Nếu có Toán học, bắt buộc dùng LaTeX bọc trong dấu `$`)."""
                        elif "Trích xuất" in tac_vu:
                            prompt_text = f"""BẠN LÀ CHUYÊN GIA SỐ HÓA TÀI LIỆU CẤP CAO (OCR MASTER).
Hãy trích xuất TOÀN BỘ văn bản có trong hình ảnh này một cách chính xác tuyệt đối.
Yêu cầu:
1. Giữ nguyên tối đa cấu trúc đoạn văn, danh sách, bảng biểu.
2. BẮT BUỘC nhận diện và chuyển đổi mọi công thức Toán/Lý/Hóa thành mã LaTeX (bọc trong `$ ... $` cho trong dòng, `$$ ... $$` cho độc lập dòng).
3. Bỏ qua các vết mực nhòe hoặc chi tiết không phải văn bản.
Ghi chú thêm: {yeu_cau_them if yeu_cau_them else 'Trích xuất thô, chuẩn xác định dạng.'}"""
                        else:
                            prompt_text = f"""BẠN LÀ CHUYÊN GIA TÂM LÝ HỌC ĐƯỜNG VÀ QUẢN LÝ LỚP HỌC.
Hãy phân tích bức ảnh được đính kèm để đưa ra góc nhìn khách quan về bối cảnh:
1. Đánh giá sơ bộ trạng thái, không khí hoặc mức độ tập trung (nếu có người trong ảnh). Lưu ý: Phân tích theo nhóm, KHÔNG định danh cá nhân để bảo mật thông tin.
2. Mô tả các thiết bị, dụng cụ học tập hoặc tình huống giáo dục đang diễn ra.
3. Đưa ra lời khuyên sư phạm hoặc gợi ý tổ chức hoạt động tiếp theo dựa trên bối cảnh đó.
Ghi chú thêm: {yeu_cau_them if yeu_cau_them else 'Phân tích tổng quan không khí.'}"""

                        # 3. GỌI HÀM AN TOÀN ĐÃ CÓ FALLBACK CHỐNG SẬP
                        result = safe_generate_vision(ai_engine_cu, prompt_text, image)
                        
                        if result.startswith("❌") or result.startswith("⚠️"):
                            st.error(result)
                        else:
                            st.session_state["cam_result"] = result
                            st.session_state["cam_task"] = tac_vu.split(" ")[1] # Lấy từ khóa ngắn làm tên file
                            
                    except Exception as e:
                        st.error(f"❌ {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ KHI XỬ LÝ XONG
    # ========================================================
    if st.session_state.get("cam_result"):
        st.markdown("---")
        st.markdown("### 📊 KẾT QUẢ PHÂN TÍCH AI")
        st.markdown(st.session_state["cam_result"], unsafe_allow_html=True)
        
        st.markdown("#### 📥 Lưu trữ kết quả")
        col_txt, col_word = st.columns(2)
        
        with col_txt:
            st.download_button(
                label="📄 Tải kết quả (.TXT)",
                data=st.session_state["cam_result"],
                file_name=f"Vision_AI_{st.session_state['cam_task']}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        with col_word:
            if export_word is None:
                st.warning("⚠️ Module Word chưa sẵn sàng.")
            else:
                try:
                    export_data = {
                        "ai_generated_content": st.session_state["cam_result"],
                        "is_dkt": False
                    }
                    with st.spinner("Đang kết xuất Word..."):
                        word_bytes = export_word(export_data)
                    
                    st.download_button(
                        label="📘 Tải kết quả (.DOCX)",
                        data=word_bytes,
                        file_name=f"Vision_AI_{st.session_state['cam_task']}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Lỗi xuất Word: {e}")
                    
        if st.button("🔄 Xóa bộ nhớ và chụp ảnh mới", use_container_width=True):
            st.session_state["cam_result"] = None
            st.rerun()
