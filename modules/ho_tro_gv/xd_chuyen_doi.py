# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_chuyen_doi.py
Nhiệm vụ: Trợ lý Xử lý, Làm sạch & Chuyển đổi Dữ liệu.
NÂNG CẤP: Tích hợp cơ chế tự động dự phòng sang OpenAI (sk-) 
khi Gemini Pro bị cạn hạn mức (429 Resource Exhausted).
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

def safe_generate(prompt):
    """
    Hàm gọi AI thông minh: Thử Gemini Pro -> Gemini Flash -> Tự động chuyển sang OpenAI (sk-) nếu hết hạn mức (429).
    """
    # 1. Thử gọi qua AIEngine2 với model Pro
    if AIEngine2 is not None:
        try:
            engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
            res = engine_v2.generate_text(prompt)
            if res and not res.startswith("❌") and not res.startswith("⚠️") and "429" not in res and "RESOURCE_EXHAUSTED" not in res:
                return res
        except Exception:
            pass
        
        # 2. Nếu Pro lỗi, thử sang Flash
        try:
            engine_flash = AIEngine2(default_model="gemini-2.5-flash")
            res = engine_flash.generate_text(prompt)
            if res and not res.startswith("❌") and not res.startswith("⚠️") and "429" not in res and "RESOURCE_EXHAUSTED" not in res:
                return res
        except Exception:
            pass

    # 3. Dự phòng tự động gọi trực tiếp OpenAI bằng khóa sk- đang có sẵn trong hệ thống
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
        try:
            from openai import OpenAI
            client = OpenAI(api_key=str(api_key).strip())
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as open_err:
            raise RuntimeError(f"Cả Gemini và OpenAI đều gặp sự cố: {open_err}")

    raise RuntimeError("Hạn mức Gemini đã cạn (429 Resource Exhausted) và không tìm thấy khóa API OpenAI dự phòng trong hệ thống.")

def render_xd_chuyen_doi(ai_engine_cu=None):
    # Khởi tạo session state để giữ kết quả không bị mất khi bấm tải file
    if "cd_result" not in st.session_state:
        st.session_state["cd_result"] = None
    if "cd_loai" not in st.session_state:
        st.session_state["cd_loai"] = ""

    st.markdown("### 🔄 Trợ lý Xử lý, Làm sạch & Chuyển đổi Dữ liệu")
    st.info("💡 **Góc chuyên gia:** Sử dụng AI để định dạng lại các văn bản lộn xộn, chuyển văn bản thành bảng biểu, viết lại câu chữ chuyên nghiệp hoặc **phục hồi và chuẩn hóa công thức Toán/Lý/Hóa bị dập nát khi copy từ ChatGPT**.")
    
    with st.container(border=True):
        loai_chuyen_doi = st.radio(
            "Chọn thao tác mong muốn:",
            [
                "Chuẩn hóa và Phục hồi Công thức Toán học (Lỗi copy từ ChatGPT)", 
                "Chuyển đoạn văn thô thành Bảng dữ liệu (Markdown)", 
                "Làm sạch văn bản (Xóa khoảng trắng thừa, sửa lỗi gõ phím, lỗi font)", 
                "Chuyển đổi văn phong (Từ nôm na sang Hành chính/Sư phạm)"
            ]
        )
        
        van_ban_goc = st.text_area(
            "Dán văn bản gốc cần xử lý vào đây:", 
            height=250, 
            placeholder="Ví dụ dán đoạn toán bị lỗi: x = -b ± b2 - 4ac2a ..."
        )
        
        btn_chuyen_doi = st.button("⚙️ THỰC THI CHUYỂN ĐỔI BẰNG AI", type="primary", use_container_width=True)

    if btn_chuyen_doi:
        if not van_ban_goc.strip():
            st.warning("⚠️ Vui lòng cung cấp văn bản gốc.")
        else:
            with st.spinner("⏳ AI đang xử lý và định dạng lại dữ liệu..."):
                
                # Cấu trúc Prompt tùy biến theo lựa chọn của người dùng
                if "Toán học" in loai_chuyen_doi:
                    prompt_task = r"""
BẠN LÀ CHUYÊN GIA TOÁN HỌC VÀ LATEX SIÊU VIỆT.
Nhiệm vụ: Chuyển đổi và PHỤC HỒI toàn bộ các công thức toán học bị lỗi định dạng (do copy/paste từ ChatGPT dạng plain-text) về chuẩn LaTeX hoàn chỉnh.

[CÁC LỖI THƯỜNG GẶP CẦN PHỤC HỒI BẮT BUỘC]:
1. Lỗi mất số mũ/chỉ số: `b2` phải sửa thành `b^2`, `x1` thành `x_1`, `x2` thành `x_2`.
2. Lỗi mất phân số: `-b/2a` hoặc `-b2a` phải sửa thành `\frac{-b}{2a}`. Phải có cặp ngoặc nhọn `{}` bao bọc tử và mẫu.
3. Lỗi mất dấu căn: `b2-4ac` trong công thức nghiệm phải có căn, sửa thành `\sqrt{b^2-4ac}`.
4. Lỗi ký hiệu Unicode thô: Thay `Δ` bằng `\Delta`, thay `±` bằng `\pm`, thay `·` bằng `\cdot`.

[QUY TẮC ĐÓNG GÓI - KỶ LUẬT THÉP ĐỂ XUẤT FILE WORD]:
1. MỌI công thức và BIẾN SỐ ĐƠN LẺ (như a, b, c, \Delta, x, y...) ĐỀU PHẢI được bọc trong dấu `$ ... $` (nếu nằm trong dòng) hoặc `$$ ... $$` (nếu đứng độc lập).
2. LƯU Ý SỐNG CÒN: Cấm tuyệt đối việc ngắt dòng khi sử dụng `$$ ... $$`. Dấu `$$` và công thức BẮT BUỘC phải nằm liền nhau trên 1 dòng duy nhất.
   - ❌ SAI (Word sẽ bị lỗi phân mảnh):
   $$
   ax^2 + bx + c = 0
   $$
   - ✅ ĐÚNG (Word hiển thị hoàn hảo):
   $$ ax^2 + bx + c = 0 $$
3. TUYỆT ĐỐI KHÔNG dùng dấu ngoặc `\( ... \)` hay `\[ ... \]`.
4. TUYỆT ĐỐI KHÔNG dùng dấu nháy ngược (`) để bọc công thức.
5. KHÔNG giải thích dông dài, chỉ xuất ra nội dung đã được xử lý hoàn chỉnh.

Hãy viết lại toàn bộ văn bản dưới đây, giữ nguyên lời văn, nhưng phục hồi 100% công thức Toán học theo đúng cú pháp LaTeX và LUẬT TRÊN 1 DÒNG DUY NHẤT.
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
                    # Gọi hàm an toàn có tích hợp cơ chế tự động dự phòng (Fallback)
                    result = safe_generate(prompt)
                    
                    if result.startswith("❌") or result.startswith("⚠️"):
                        st.error(result)
                    else:
                        st.session_state["cd_result"] = result
                        st.session_state["cd_loai"] = loai_chuyen_doi.split("(")[0].strip()
                        st.success("✅ Dữ liệu đã được phục hồi và xử lý xong!")
                        
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
                    
        if st.button("🔄 Xử lý văn bản khác", use_container_width=True):
            st.session_state["cd_result"] = None
            st.rerun()
