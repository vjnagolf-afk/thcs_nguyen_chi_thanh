# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import re

# ==========================================
# HÀM HỖ TRỢ XỬ LÝ CHUỖI
# ==========================================
def _extract_html_code(text):
    """Trích xuất mã HTML sạch từ câu trả lời của AI"""
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
    st.markdown("### 📊 MÔ PHỎNG & THÍ NGHIỆM ẢO")
    
    # Khởi tạo bộ nhớ session_state
    if "kb_mp" not in st.session_state: st.session_state.kb_mp = ""
    if "code_mp" not in st.session_state: st.session_state.code_mp = ""

    # Chia 3 Tab theo đúng sơ đồ của thầy
    tab_ai, tab_phet, tab_kho = st.tabs(["🤖 AI XÂY DỰNG MÔ PHỎNG", "🧪 PHÒNG THÍ NGHIỆM ẢO", "📚 KHO MÔ PHỎNG CỦA TÔI"])

    # ==========================================
    # TAB 1: 🤖 AI XÂY DỰNG MÔ PHỎNG
    # ==========================================
    with tab_ai:
        st.markdown("#### 🛠️ Khởi tạo Mô phỏng Mới")
        
        # Giao diện nhập liệu giống thiết kế của thầy
        mo_ta = st.text_area(
            "Mô tả mô phỏng cần xây dựng:", 
            placeholder="Ví dụ: Tạo mô phỏng sự rơi tự do của một quả bóng. Cho phép điều chỉnh độ cao, khối lượng và gia tốc trọng trường..."
        )
        
        col_mon, col_lop = st.columns(2)
        with col_mon:
            mon_hoc = st.selectbox("Môn:", ["KHTN", "Vật lý", "Hóa học", "Sinh học", "Toán"])
        with col_lop:
            lop = st.selectbox("Lớp:", ["6", "7", "8", "9", "Khác"])
            
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            btn_kb = st.button("✨ Tạo kịch bản", use_container_width=True, type="primary")
        with col_btn2:
            btn_code = st.button("💻 Sinh mã mô phỏng", use_container_width=True, type="primary")

        # Xử lý: Tạo Kịch bản
        if btn_kb:
            if not mo_ta:
                st.warning("⚠️ Thầy vui lòng nhập mô tả mô phỏng trước!")
            else:
                with st.spinner("🧠 AI đang xây dựng kịch bản..."):
                    prompt_kb = f"Viết kịch bản chi tiết để lập trình mô phỏng tương tác cho môn {mon_hoc} lớp {lop}. Mô tả: {mo_ta}. Kịch bản cần bao gồm: Mục tiêu, Các biến số điều chỉnh (như thanh trượt slider, nút bấm), Hiện tượng xảy ra, Câu hỏi khám phá."
                    try:
                        st.session_state.kb_mp = ai_engine.generate_text(prompt_kb)
                        st.success("✅ Đã tạo kịch bản thành công!")
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")

        # Xử lý: Sinh mã HTML/JS
        if btn_code:
            if not mo_ta and not st.session_state.kb_mp:
                st.warning("⚠️ Thầy vui lòng nhập mô tả hoặc tạo kịch bản trước khi sinh mã!")
            else:
                with st.spinner("🤖 AI đang lập trình mã HTML/JavaScript/Canvas (Có thể mất 20-40 giây)..."):
                    base_context = st.session_state.kb_mp if st.session_state.kb_mp else mo_ta
                    prompt_code = f"Đóng vai lập trình viên Frontend chuyên nghiệp. Viết toàn bộ mã nguồn (HTML, CSS, JavaScript) gom chung vào 1 file HTML duy nhất để chạy mô phỏng sau:\n\n{base_context}\n\nYêu cầu kỹ thuật BẮT BUỘC:\n- Sử dụng công nghệ HTML5 Canvas hoặc SVG để vẽ hình động trực quan.\n- Cung cấp các thanh trượt (<input type='range'>) và giao diện điều khiển (UI) đẹp mắt.\n- Mã phản hồi liên tục và chạy được ngay trên trình duyệt mà không cần cài đặt.\n- Chỉ xuất ra đoạn mã code nằm trong cặp ```html, không giải thích gì thêm."
                    try:
                        raw_code = ai_engine.generate_text(prompt_code)
                        st.session_state.code_mp = _extract_html_code(raw_code)
                        st.success("✅ Đã lập trình xong mã Mô phỏng!")
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")

        # Khu vực hiển thị kết quả (Các Tab phụ)
        st.markdown("---")
        out_tab_kb, out_tab_code, out_tab_run = st.tabs(["📋 Kịch bản", "💻 Mã nguồn", "▶️ Chạy mô phỏng"])
        
        with out_tab_kb:
            if st.session_state.kb_mp:
                st.write(st.session_state.kb_mp)
            else:
                st.info("Chưa có kịch bản.")
                
        with out_tab_code:
            if st.session_state.code_mp:
                st.code(st.session_state.code_mp, language='html')
                # Nút tải mã nguồn về máy (.html)
                st.download_button(
                    label="📥 Tải mã nguồn (.html)",
                    data=st.session_state.code_mp,
                    file_name="mo_phong_ai.html",
                    mime="text/html"
                )
            else:
                st.info("Chưa có mã nguồn.")
                
        with out_tab_run:
            if st.session_state.code_mp:
                st.success("Tương tác trực tiếp với mô phỏng bên dưới:")
                # Chạy HTML/JS ngay trên Streamlit
                components.html(st.session_state.code_mp, height=600, scrolling=True)
                
                st.markdown("---")
                st.markdown("**Hướng dẫn lưu trữ:**")
                st.caption("Sau khi mô phỏng chạy chuẩn, thầy có thể dùng phần mềm quay màn hình (OBS/Zalo) để quay lại quá trình tương tác mô phỏng ➔ Đăng lên YouTube ➔ Lưu vào *Kho mô phỏng của tôi*.")
            else:
                st.info("Nhấn 'Sinh mã mô phỏng' để có giao diện chạy thử.")

    # ==========================================
    # TAB 2: 🧪 PHÒNG THÍ NGHIỆM ẢO
    # ==========================================
    with tab_phet:
        st.markdown("#### Khám phá kho học liệu chuẩn quốc tế")
        st.info("💡 Mở trong Tab mới (An toàn nhất để không bị chặn bởi các quy định bảo mật của nền tảng).")
        
        col_phet, col_moza = st.columns(2)
        
        with col_phet:
            st.markdown("### ⚛️ PhET Simulations")
            st.markdown("Kho mô phỏng tương tác Khoa học Tự nhiên và Toán học của Đại học Colorado Boulder.")
            st.link_button("🚀 Mở PhET Tiếng Việt", "[https://phet.colorado.edu/vi/](https://phet.colorado.edu/vi/)", use_container_width=True)

        with col_moza:
            st.markdown("### 🧬 MozaWeb 3D")
            st.markdown("Thư viện cảnh 3D tương tác sắc nét, video giáo dục (Sinh học, Hóa học, Lịch sử...).")
            st.link_button("🌐 Mở MozaWeb 3D", "[https://mozaweb.vn/vi/lexikon.php?cmd=getlist&let=3D&sid=BIO](https://mozaweb.vn/vi/lexikon.php?cmd=getlist&let=3D&sid=BIO)", use_container_width=True)

    # ==========================================
    # TAB 3: 📚 KHO MÔ PHỎNG CỦA TÔI
    # ==========================================
    with tab_kho:
        st.markdown("#### Quản lý & Chia sẻ")
        
        col_kho1, col_kho2 = st.columns(2)
        with col_kho1:
            st.markdown("**Danh sách mô phỏng đã tạo:**")
            st.info("Dữ liệu đang trống. (Tính năng kết nối cơ sở dữ liệu để lưu trữ lâu dài đang được phát triển).")
            
        with col_kho2:
            st.markdown("**Đăng mô phỏng bằng Video (YouTube):**")
            link_yt = st.text_input("Dán link YouTube (đã quay từ Tab 1):")
            if link_yt:
                st.video(link_yt)
                st.button("💾 Lưu vào kho")
