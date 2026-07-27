# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_chuyen_doi.py
Nhiệm vụ: Trợ lý Xử lý, Làm sạch & Chuyển đổi Dữ liệu.
NÂNG CẤP: Kết nối AIEngine2, Chuẩn hóa công thức Toán học, Xuất file Word.
============================================================
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Tích hợp xuất Word để công thức Toán / Bảng biểu hiển thị chuẩn Native
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2 để dùng Smart Router
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

def render_xd_chuyen_doi(ai_engine_cu=None):
    # Khởi tạo session state để giữ kết quả không bị mất khi bấm tải file
    if "cd_result" not in st.session_state:
        st.session_state["cd_result"] = None
    if "cd_loai" not in st.session_state:
        st.session_state["cd_loai"] = ""

    st.markdown("### 🔄 Trợ lý Xử lý, Làm sạch & Chuyển đổi Dữ liệu")
    st.info("💡 **Góc chuyên gia:** Sử dụng AI để định dạng lại các văn bản lộn xộn, chuyển văn bản thành bảng biểu, viết lại câu chữ chuyên nghiệp hoặc **chuẩn hóa công thức Toán/Lý/Hóa bị lỗi copy từ ChatGPT**.")
    
    with st.container(border=True):
        loai_chuyen_doi = st.radio(
            "Chọn thao tác mong muốn:",
            [
                "Chuẩn hóa Công thức Toán học (Sửa lỗi copy từ ChatGPT về chuẩn $...$)", 
                "Chuyển đoạn văn thô thành Bảng dữ liệu (Markdown)", 
                "Làm sạch văn bản (Xóa khoảng trắng thừa, sửa lỗi gõ phím, lỗi font)", 
                "Chuyển đổi văn phong (Từ nôm na sang Hành chính/Sư phạm)"
            ]
        )
        
        van_ban_goc = st.text_area(
            "Dán văn bản gốc cần xử lý vào đây:", 
            height=250, 
            placeholder="Ví dụ: Dán một đoạn chứa công thức lỗi \\( x^2 + y^2 \\), hoặc văn bản lủng củng..."
        )
        
        btn_chuyen_doi = st.button("⚙️ THỰC THI CHUYỂN ĐỔI BẰNG AI", type="primary", use_container_width=True)

    if btn_chuyen_doi:
        if AIEngine2 is None:
            st.error("❌ Không tìm thấy file `utils/ai_engine_2.py`. Vui lòng kiểm tra lại cấu trúc dự án.")
            return

        if not van_ban_goc.strip():
            st.warning("⚠️ Vui lòng cung cấp văn bản gốc.")
        else:
            with st.spinner("⏳ AI đang xử lý và định dạng lại dữ liệu..."):
                
                # Cấu trúc Prompt tùy biến theo lựa chọn của người dùng
                if "Toán học" in loai_chuyen_doi:
                    prompt_task = r"""
BẠN LÀ CHUYÊN GIA BIÊN TẬP VÀ ĐỊNH DẠNG TOÁN HỌC.
Nhiệm vụ: Chuyển đổi toàn bộ các định dạng toán học bị lỗi trong văn bản dưới đây về chuẩn.
- Các công thức copy từ ChatGPT thường bị kẹp giữa `\( ... \)` hoặc `\[ ... \]`. Hãy biến TẤT CẢ chúng thành `$ ... $` (nếu trên cùng dòng) hoặc `$$ ... $$` (nếu đứng độc lập).
- Chỉnh sửa các công thức bị lỗi ký tự.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG DẤU NHÁY NGƯỢC (backtick `) ĐỂ BỌC CÔNG THỨC TOÁN.
- Giữ nguyên vẹn toàn bộ phần văn bản chữ (không làm thay đổi nội dung câu văn).
"""
                elif "Bảng dữ liệu" in loai_chuyen_doi:
                    prompt_task = """
Nhiệm vụ: Phân tích đoạn văn bản thô, nhận diện các trường thông tin và chuyển chúng thành một BẢNG (Markdown Table) thật khoa học, logic.
Chỉ xuất ra Bảng Markdown, không giải thích dông dài.
"""
                elif "Làm sạch" in loai_chuyen_doi:
                    prompt_task = """
Nhiệm vụ: Làm sạch đoạn văn bản sau. Xóa toàn bộ khoảng trắng thừa, sửa các lỗi dính chữ, lỗi gõ phím, ngắt nghỉ câu cho chuẩn ngữ pháp tiếng Việt. Giữ nguyên ý nghĩa gốc.
"""
                else:
                    prompt_task = """
Nhiệm vụ: Viết lại đoạn văn bản sau sang văn phong Hành chính / Sư phạm chuẩn mực, chuyên nghiệp, lịch sự nhưng vẫn giữ đúng thông điệp gốc.
"""

                prompt = f"""
{prompt_task}

--- VĂN BẢN GỐC CẦN XỬ LÝ ---
{van_ban_goc}
"""
                try:
                    # Khởi tạo AIEngine2 và chạy (Ưu tiên dùng Pro cho logic Toán học/Format)
                    engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                    result = engine_v2.generate_text(prompt)
                    
                    if result.startswith("❌") or result.startswith("⚠️"):
                        st.error(result)
                    else:
                        st.session_state["cd_result"] = result
                        st.session_state["cd_loai"] = loai_chuyen_doi.split("(")[0].strip()
                        st.success("✅ Dữ liệu đã được xử lý xong!")
                        
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {e}")

    # ========================================================
    # HIỂN THỊ KẾT QUẢ & XUẤT FILE
    # ========================================================
    if st.session_state.get("cd_result"):
        st.markdown("---")
        st.markdown("### 📑 KẾT QUẢ ĐÃ CHUYỂN ĐỔI")
        
        # Hiển thị kết quả ra giao diện
        st.markdown(st.session_state["cd_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Tải kết quả về máy")
        
        col_txt, col_word = st.columns(2)
        
        # Tải TXT (Nhanh, nguyên bản)
        with col_txt:
            st.download_button(
                label="📄 Tải kết quả (.TXT)",
                data=st.session_state["cd_result"],
                file_name="DuLieu_DaXuLy.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        # Tải WORD (Render OMML Toán học và Kẻ bảng)
        with col_word:
            if export_word is None:
                st.warning("⚠️ Module Word chưa sẵn sàng.")
            else:
                try:
                    export_data = {
                        "ai_generated_content": st.session_state["cd_result"],
                        "is_dkt": False
                    }
                    with st.spinner("Đang kết xuất Word (Native OMML)..."):
                        word_bytes = export_word(export_data)
                    
                    st.download_button(
                        label="📘 Tải kết quả (.DOCX)",
                        data=word_bytes,
                        file_name="DuLieu_DaXuLy.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Lỗi xuất Word: {e}")
                    
        if st.button("🔄 Làm sạch văn bản khác", use_container_width=True):
            st.session_state["cd_result"] = None
            st.rerun()
