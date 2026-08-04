# -*- coding: utf-8 -*-
import io
import time
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

# Bắt buộc import AIEngine2
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

# ========================================================
# CÁC HÀM TIỆN ÍCH
# ========================================================
def get_base64_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def simulate_stream(text):
    """Giả lập hiệu ứng gõ chữ (Streaming) cho các AI không hỗ trợ Stream native"""
    # Tách theo khoảng trắng để giữ nguyên từ
    words = text.split(" ")
    for i, word in enumerate(words):
        yield word + " "
        # Tốc độ gõ giả lập nhanh dần để không phải chờ lâu
        time.sleep(0.015)

def stream_openai(api_key, prompt, list_images):
    """Gọi OpenAI và lấy dữ liệu Stream thực tế từng chunk"""
    import openai
    client = openai.OpenAI(api_key=api_key.strip())
    
    content_array = [{"type": "text", "text": prompt}]
    for img in list_images:
        base64_img = get_base64_image(img)
        content_array.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
        })
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content_array}],
        temperature=0.7,
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

def run_gemini_sync(ai_engine_cu, prompt, list_images):
    """Gọi Gemini đồng bộ (Sync) bằng engine hiện tại"""
    try:
        engine_v2 = AIEngine2(default_model="gemini-1.5-flash")
        contents = [prompt]
        for img in list_images:
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            contents.append({
                "mime_type": "image/jpeg",
                "data": buffered.getvalue()
            })
            
        if hasattr(engine_v2, "generate_multimodal"):
            res = engine_v2.generate_multimodal(contents)
        else:
            raise RuntimeError("❌ File `utils/ai_engine_2.py` thiếu hàm `generate_multimodal`.")
            
        if res and not res.startswith("❌") and not res.startswith("⚠️") and "429" not in res and "RESOURCE_EXHAUSTED" not in res:
            return res
        raise RuntimeError("Hạn mức Gemini cạn kiệt (429).")
    except Exception as e:
        raise RuntimeError(f"Lỗi Gemini Vision: {str(e)}")

# ========================================================
# GIAO DIỆN CHÍNH
# ========================================================
def render_xd_camera(ai_engine_cu=None):
    if "cam_result" not in st.session_state:
        st.session_state["cam_result"] = None
    if "cam_task" not in st.session_state:
        st.session_state["cam_task"] = ""

    st.markdown("### 📷 Trợ lý AI Vision: Chấm Điểm & Số Hóa")
    st.info("💡 **Tính năng mới Nâng cấp (V2):** Hỗ trợ chấm **Nhiều ảnh cùng lúc** (bài thi nhiều trang), tích hợp **Bareme/Rubric điểm**, và hiển thị kết quả **Thời gian thực (Streaming)**.")

    col_cam, col_result = st.columns([1, 1.2], gap="large")
    
    # ----------------------------------------------------
    # CỘT TRÁI: THU THẬP HÌNH ẢNH (CAMERA + UPLOAD)
    # ----------------------------------------------------
    with col_cam:
        st.markdown("#### 📸 Khung thu nhận Hình ảnh")
        st.caption("Thầy/cô có thể vừa chụp Webcam, vừa tải thêm nhiều ảnh từ máy tính.")
        
        # 1. Chụp từ Camera
        enable_cam = st.checkbox("Bật kết nối Webcam/Camera", value=False)
        img_buffer = None
        if enable_cam:
            img_buffer = st.camera_input("Chụp ảnh tài liệu/bài làm")
            
        # 2. Tải nhiều ảnh từ máy
        st.markdown("---")
        uploaded_files = st.file_uploader("Hoặc tải lên bài làm (hỗ trợ nhiều ảnh):", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)
        
        # Gom tất cả ảnh lại
        images_to_process = []
        if img_buffer:
            images_to_process.append(Image.open(img_buffer).convert('RGB'))
        if uploaded_files:
            for f in uploaded_files:
                images_to_process.append(Image.open(f).convert('RGB'))
                
        if len(images_to_process) > 0:
            st.success(f"✅ Đã thu nhận tổng cộng **{len(images_to_process)}** hình ảnh sẵn sàng phân tích.")

    # ----------------------------------------------------
    # CỘT PHẢI: CẤU HÌNH TÁC VỤ VÀ GỌI AI
    # ----------------------------------------------------
    with col_result:
        st.markdown("#### ⚙️ Trung tâm Xử lý AI")
        
        with st.container(border=True):
            tac_vu = st.radio(
                "Chọn tác vụ phân tích:", 
                [
                    "📝 Chấm điểm & Chữa bài làm", 
                    "🖨️ Trích xuất văn bản & Số hóa (OCR)", 
                    "🤔 Phân tích trạng thái / Môi trường học tập"
                ]
            )
            
            # GIAO DIỆN RUBRIC CHỈ HIỆN KHI CHỌN CHẤM ĐIỂM
            rubric_text = ""
            if "Chấm điểm" in tac_vu:
                rubric_text = st.text_area(
                    "📌 Bareme / Rubric / Đáp án chấm (Khuyên dùng):", 
                    height=100,
                    placeholder="VD: Ý 1: Phân tích được tác giả (1đ). Ý 2: Nêu được nghệ thuật (2đ)..."
                )
            
            yeu_cau_them = st.text_input("Ghi chú thêm cho AI (Tùy chọn):", placeholder="VD: Hãy chú ý vào công thức tính toán ở dòng thứ 2...")
            
            btn_phan_tich = st.button("🧠 TIẾN HÀNH PHÂN TÍCH", type="primary", use_container_width=True)

        if btn_phan_tich:
            if len(images_to_process) == 0:
                st.error("❌ Chưa có dữ liệu hình ảnh. Vui lòng chụp hoặc tải ảnh lên trước!")
            else:
                st.markdown("---")
                st.markdown("#### ⏳ Đang phân tích (Streaming)...")
                
                # Vùng chứa kết quả Streaming
                result_container = st.empty()
                
                # 1. Tạo Prompt
                if "Chấm điểm" in tac_vu:
                    prompt_text = f"""BẠN LÀ MỘT GIÁO VIÊN VÀ CHUYÊN GIA KHẢO THÍ DÀY DẶN KINH NGHIỆM.
Nhiệm vụ của bạn là đọc các hình ảnh bài làm của học sinh (viết tay hoặc in) và thực hiện phân tích/chấm điểm.
{f"BẮT BUỘC SỬ DỤNG BAREME/RUBRIC SAU ĐỂ CHẤM ĐIỂM TỪNG Ý:\n{rubric_text}" if rubric_text.strip() else "Phân tích và đưa ra điểm số ước lượng dựa trên chuyên môn của bạn."}

CÁC BƯỚC THỰC HIỆN:
1. Đọc và phiên mã sơ lược nội dung học sinh đã làm.
2. Chỉ ra các lỗi sai (nếu có) về mặt kiến thức, logic hoặc chính tả.
3. Chấm điểm chi tiết từng phần dựa vào Bareme (nếu có).
4. Đưa ra tổng điểm và một lời nhận xét ngắn gọn, động viên.

Ghi chú thêm từ giáo viên: {yeu_cau_them if yeu_cau_them else 'Không có'}
(Lưu ý định dạng: Trình bày Markdown sạch sẽ. Nếu có Toán học, dùng LaTeX bọc trong dấu `$`)."""

                elif "Trích xuất" in tac_vu:
                    prompt_text = f"""BẠN LÀ CHUYÊN GIA SỐ HÓA TÀI LIỆU CẤP CAO (OCR MASTER).
Hãy trích xuất TOÀN BỘ văn bản có trong (các) hình ảnh này một cách chính xác tuyệt đối.
Yêu cầu:
1. Giữ nguyên tối đa cấu trúc đoạn văn, danh sách, bảng biểu.
2. BẮT BUỘC nhận diện và chuyển đổi mọi công thức Toán/Lý/Hóa thành mã LaTeX (bọc trong `$ ... $` cho trong dòng, `$$ ... $$` cho độc lập dòng).
3. Nối liền mạch nội dung nếu ảnh bị cắt trang.
Ghi chú thêm: {yeu_cau_them if yeu_cau_them else 'Trích xuất thô, chuẩn xác định dạng.'}"""

                else:
                    prompt_text = f"""BẠN LÀ CHUYÊN GIA TÂM LÝ HỌC ĐƯỜNG VÀ QUẢN LÝ LỚP HỌC.
Hãy phân tích (các) bức ảnh được đính kèm để đưa ra góc nhìn khách quan về bối cảnh:
1. Đánh giá sơ bộ trạng thái, không khí hoặc mức độ tập trung (nếu có người). Phân tích theo nhóm, KHÔNG định danh cá nhân.
2. Mô tả các thiết bị, dụng cụ học tập hoặc tình huống giáo dục đang diễn ra.
3. Đưa ra lời khuyên sư phạm.
Ghi chú thêm: {yeu_cau_them if yeu_cau_them else 'Phân tích tổng quan không khí.'}"""

                # 2. Xử lý logic gọi AI + Streaming
                full_response = ""
                error_msgs = []
                
                # Lấy API Key để fallback
                api_key = None
                for k in ["user_api_key", "api_key", "openai_api_key", "sk_key"]:
                    if st.session_state.get(k) and str(st.session_state.get(k)).startswith("sk-"):
                        api_key = str(st.session_state.get(k))
                        break
                if not api_key and "OPENAI_API_KEY" in st.secrets:
                    api_key = st.secrets["OPENAI_API_KEY"]

                # CỐ GẮNG GỌI GEMINI TRƯỚC (GIẢ LẬP STREAM)
                try:
                    sync_result = run_gemini_sync(ai_engine_cu, prompt_text, images_to_process)
                    # Giả lập streaming cho UI mượt mà
                    full_response = result_container.write_stream(simulate_stream(sync_result))
                    
                except Exception as e_gemini:
                    error_msgs.append(f"Gemini: {str(e_gemini)}")
                    
                    # NẾU GEMINI LỖI 429 -> GỌI OPENAI VÀ STREAM THỰC TẾ
                    if api_key:
                        try:
                            full_response = result_container.write_stream(stream_openai(api_key, prompt_text, images_to_process))
                        except Exception as e_openai:
                            st.error(f"❌ OpenAI cũng gặp lỗi: {e_openai}")
                    else:
                        st.error(f"❌ Gemini bị từ chối truy cập (Hết hạn mức). Vui lòng thêm khóa `sk-` của OpenAI để hệ thống tự động bẻ lái!\nChi tiết: {e_gemini}")

                # 3. Lưu kết quả
                if full_response:
                    st.session_state["cam_result"] = full_response
                    st.session_state["cam_task"] = tac_vu.split(" ")[1] # Lấy từ khóa làm tên file
                    st.success("✅ Phân tích hoàn tất!")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ KHI XỬ LÝ XONG (VÙNG LƯU TRỮ)
    # ========================================================
    if st.session_state.get("cam_result"):
        st.markdown("---")
        st.markdown("#### 📥 Quản lý Kết quả")
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
                    
        if st.button("🔄 Xóa bộ nhớ và tải ảnh mới", use_container_width=True):
            st.session_state["cam_result"] = None
            st.rerun()
