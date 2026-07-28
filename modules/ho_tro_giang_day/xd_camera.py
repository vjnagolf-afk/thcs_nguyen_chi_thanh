# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_camera.py
Nhiệm vụ: Trợ lý AI Camera Nhận diện (Vision AI).
Chức năng: Chụp ảnh bài làm, số hóa tài liệu, hoặc đánh giá trạng thái 
thông qua mô hình Đa phương tiện (Multimodal) của AIEngine2.
============================================================
"""

import io
import logging
import streamlit as st
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

def render_xd_camera(ai_engine_cu=None):
    # Khởi tạo bộ nhớ tạm để giữ kết quả phân tích
    if "cam_result" not in st.session_state:
        st.session_state["cam_result"] = None
    if "cam_task" not in st.session_state:
        st.session_state["cam_task"] = ""

    st.markdown("### 📷 Trợ lý AI Camera Nhận diện (Vision AI)")
    st.info("💡 **Góc chuyên gia:** Sử dụng Webcam hoặc Camera trên thiết bị di động để chụp trực tiếp bài làm của học sinh, tài liệu giấy, hoặc không khí lớp học. AI sẽ phân tích hình ảnh và trả về kết quả số hóa ngay lập tức.")

    st.warning("⚠️ LƯU Ý: Tính năng yêu cầu cấp quyền sử dụng Webcam trên trình duyệt. Để chạy trên mạng LAN hoặc Internet, máy chủ cần được cấu hình SSL/HTTPS.")
    
    col_cam, col_result = st.columns([1, 1.2], gap="large")
    
    with col_cam:
        st.markdown("#### 📸 Khung thu nhận Hình ảnh")
        enable_cam = st.checkbox("Bật kết nối Camera", value=True)
        img_buffer = None
        
        if enable_cam:
            # Widget thu ảnh từ Camera
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

        # XỬ LÝ GỌI AI ĐA PHƯƠNG TIỆN
        if btn_phan_tich:
            if not img_buffer:
                st.error("❌ Chưa có dữ liệu hình ảnh. Vui lòng cấp quyền Camera và chụp ảnh trước!")
            elif AIEngine2 is None:
                st.error("❌ Không tìm thấy hệ thống AIEngine2.")
            else:
                with st.spinner("⏳ Khởi động Mắt Thần AI (Vision Model)... đang phân tích hình ảnh chi tiết..."):
                    try:
                        # 1. Chuyển đổi buffer thành đối tượng hình ảnh PIL
                        image = Image.open(img_buffer)
                        
                        # 2. Xây dựng Prompt tương ứng
                        if "Chấm điểm" in tac_vu:
                            prompt_text = f"""
BẠN LÀ MỘT GIÁO VIÊN DÀY DẶN KINH NGHIỆM.
Nhiệm vụ của bạn là đọc hình ảnh bài làm của học sinh (viết tay hoặc in) được đính kèm và thực hiện các bước sau:
1. Đọc và phiên mã lại tóm tắt nội dung bài làm.
2. Chỉ ra các lỗi sai (nếu có) về mặt kiến thức, logic hoặc chính tả.
3. Giải thích cặn kẽ cách làm đúng.
4. Đưa ra một điểm số ước lượng và lời nhận xét động viên học sinh.
Ghi chú thêm từ giáo viên: {yeu_cau_them if yeu_cau_them else 'Không có'}
(Lưu ý: Nếu có Toán học, bắt buộc dùng LaTeX bọc trong dấu `$`).
"""
                        elif "Trích xuất" in tac_vu:
                            prompt_text = f"""
BẠN LÀ CHUYÊN GIA SỐ HÓA TÀI LIỆU CẤP CAO (OCR MASTER).
Hãy trích xuất TOÀN BỘ văn bản có trong hình ảnh này một cách chính xác tuyệt đối.
Yêu cầu:
1. Giữ nguyên tối đa cấu trúc đoạn văn, danh sách, bảng biểu.
2. BẮT BUỘC nhận diện và chuyển đổi mọi công thức Toán/Lý/Hóa thành mã LaTeX (bọc trong `$ ... $` cho trong dòng, `$$ ... $$` cho độc lập dòng).
3. Bỏ qua các vết mực nhòe hoặc chi tiết không phải văn bản.
Ghi chú thêm: {yeu_cau_them if yeu_cau_them else 'Trích xuất thô, chuẩn xác định dạng.'}
"""
                        else:
                            prompt_text = f"""
BẠN LÀ CHUYÊN GIA TÂM LÝ HỌC ĐƯỜNG VÀ QUẢN LÝ LỚP HỌC.
Hãy phân tích bức ảnh được đính kèm để đưa ra góc nhìn khách quan về bối cảnh:
1. Đánh giá sơ bộ trạng thái, không khí hoặc mức độ tập trung (nếu có người trong ảnh). Lưu ý: Phân tích theo nhóm, KHÔNG định danh cá nhân để bảo mật thông tin.
2. Mô tả các thiết bị, dụng cụ học tập hoặc tình huống giáo dục đang diễn ra.
3. Đưa ra lời khuyên sư phạm hoặc gợi ý tổ chức hoạt động tiếp theo dựa trên bối cảnh đó.
Ghi chú thêm: {yeu_cau_them if yeu_cau_them else 'Phân tích tổng quan không khí.'}
"""

                        # 3. Đóng gói dữ liệu Multimodal (Text + Image)
                        contents = [prompt_text, image]
                        
                        # 4. Gọi API
                        engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                        if hasattr(engine_v2, "generate_multimodal"):
                            result = engine_v2.generate_multimodal(contents)
                        else:
                            # Fallback nếu class chưa cập nhật method
                            result = "❌ Cần cập nhật hàm generate_multimodal trong AIEngine2."
                            
                        if result.startswith("❌") or result.startswith("⚠️"):
                            st.error(result)
                        else:
                            st.session_state["cam_result"] = result
                            st.session_state["cam_task"] = tac_vu.split(" ")[1] # Lấy từ khóa ngắn làm tên file
                            
                    except Exception as e:
                        st.error(f"❌ Lỗi xử lý hình ảnh: {e}")

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
