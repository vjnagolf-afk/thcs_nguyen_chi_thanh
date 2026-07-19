import streamlit as st
import streamlit.components.v1 as components
import re

# ==========================================
# CÁC HÀM HỖ TRỢ XỬ LÝ CHUỖI
# ==========================================
def _extract_html_code(text):
    if not text: return ""
    match = re.search(r"```(?:html)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        code = match.group(1).strip()
    else:
        code = text.strip()
    
    html_start = code.lower().find("<!doctype html>")
    if html_start == -1:
        html_start = code.lower().find("<html")
    if html_start >= 0:
        code = code[html_start:]
    return code.strip()

# ==========================================
# HÀM RENDER CHÍNH
# ==========================================
def render_mo_phong(ai_engine):
    st.markdown("### 🧪 Mô phỏng & Thí nghiệm ảo (AI Tích hợp)")
    st.caption("AI hỗ trợ xây dựng kịch bản, sinh mã HTML/JS mô phỏng trực tiếp và thư viện thí nghiệm ảo chuẩn quốc tế.")

    # Chia làm 2 khu vực: AI Sinh mô phỏng và Kho lưu trữ có sẵn
    tab_ai, tab_nhung = st.tabs(["🪄 Trợ lý AI Sinh Mô phỏng", "🌐 Kho Thí nghiệm ảo PhET & MozaWeb"])

    # ------------------------------------------
    # KHU VỰC 1: AI SINH KỊCH BẢN & MÃ NGUỒN
    # ------------------------------------------
    with tab_ai:
        st.markdown("#### 1. Khởi tạo Kịch bản & Lập trình")
        
        # Khởi tạo bộ nhớ tạm để giữ kết quả không bị mất khi thao tác
        if "kb_mo_phong" not in st.session_state: st.session_state.kb_mo_phong = ""
        if "code_mo_phong" not in st.session_state: st.session_state.code_mo_phong = ""

        # Form nhập liệu
        with st.form("form_tao_mo_phong"):
            col1, col2 = st.columns(2)
            with col1:
                ten_mp = st.text_input("Tên hiện tượng / Bài học:")
                mon_hoc = st.selectbox("Môn học:", ["Vật lý", "Hóa học", "Sinh học", "Toán học", "Khoa học Tự nhiên"])
            with col2:
                khoi_lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
                yeu_cau_them = st.text_input("Yêu cầu bổ sung:")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                btn_tao_kb = st.form_submit_button("📝 1. AI Viết Kịch Bản", use_container_width=True)
            with col_btn2:
                btn_tao_code = st.form_submit_button("💻 2. AI Sinh Mã HTML", use_container_width=True)

        if btn_tao_kb:
            if not ten_mp:
                st.warning("⚠️ Thầy vui lòng nhập Tên bài học / Hiện tượng cần mô phỏng!")
            else:
                with st.spinner("🧠 AI đang xây dựng kịch bản sư phạm..."):
                    prompt_kb = f"Viết kịch bản chi tiết để lập trình mô phỏng thí nghiệm ảo cho bài: {ten_mp}, môn {mon_hoc}, {khoi_lop}. Yêu cầu bổ sung: {yeu_cau_them}. Hãy liệt kê: 1. Mục tiêu, 2. Các thông số cần người dùng tương tác (như thanh trượt, nút bấm), 3. Hiện tượng khoa học sẽ xảy ra."
                    try:
                        st.session_state.kb_mo_phong = ai_engine.generate_text(prompt_kb)
                        st.success("✅ Đã tạo kịch bản thành công!")
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
        
        if st.session_state.kb_mo_phong:
            st.text_area("Kịch bản chi tiết:", value=st.session_state.kb_mo_phong, height=200)

        if btn_tao_code:
            if not st.session_state.kb_mo_phong:
                st.warning("⚠️ Thầy cần bấm 'AI Viết Kịch Bản' trước khi sinh mã code!")
            else:
                with st.spinner("🤖 AI đang lập trình mã HTML/CSS/JS (Có thể mất 15-30 giây)..."):
                    prompt_code = f"Đóng vai là một lập trình viên. Dựa vào kịch bản sau, hãy viết TOÀN BỘ MÃ HTML, CSS, JS (gộp chung vào 1 file HTML duy nhất) để tạo thành một mô phỏng tương tác chạy trực tiếp trên trình duyệt. Phải có giao diện đẹp, thanh điều khiển, trực quan sinh động. \n\nKịch bản:\n{st.session_state.kb_mo_phong}\n\nCHỈ TRẢ VỀ ĐOẠN MÃ HTML, không giải thích thêm."
                    try:
                        raw_code = ai_engine.generate_text(prompt_code)
                        st.session_state.code_mo_phong = _extract_html_code(raw_code)
                        st.success("✅ Đã lập trình xong mã Mô phỏng!")
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")

        if st.session_state.code_mo_phong:
            st.markdown("---")
            st.markdown("#### 2. Kết quả Thí nghiệm ảo")
            with st.expander("🛠️ Xem mã nguồn (HTML/JS)"):
                st.code(st.session_state.code_mo_phong, language='html')
            
            st.markdown("👇 **Khu vực chạy thử Mô phỏng trực tiếp:**")
            components.html(st.session_state.code_mo_phong, height=600, scrolling=True)

    # ------------------------------------------
    # KHU VỰC 2: NHÚNG PHET & MOZAWEB
    # ------------------------------------------
    with tab_nhung:
        st.markdown("#### Khám phá kho học liệu chuẩn quốc tế")
        st.info("💡 Lời khuyên: Để các mô phỏng chạy mượt mà, thầy cô nên ấn mở trong thẻ mới.")
        col_phet, col_moza = st.columns(2)
        with col_phet:
            st.markdown("### ⚛️ PhET Simulations")
            st.link_button("🚀 Mở PhET Tiếng Việt", "[https://phet.colorado.edu/vi/](https://phet.colorado.edu/vi/)", use_container_width=True)
        with col_moza:
            st.markdown("### 🧬 MozaWeb 3D")
            st.link_button("🌐 Mở MozaWeb 3D", "[https://mozaweb.vn/vi/lexikon.php?cmd=getlist&let=3D&sid=BIO](https://mozaweb.vn/vi/lexikon.php?cmd=getlist&let=3D&sid=BIO)", use_container_width=True)
