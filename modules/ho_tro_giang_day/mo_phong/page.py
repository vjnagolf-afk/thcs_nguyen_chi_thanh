# -*- coding: utf-8 -*-

import streamlit as st
import streamlit.components.v1 as components
import re


# ==========================================
# HÀM HỖ TRỢ XỬ LÝ CHUỖI
# ==========================================

def _extract_html_code(text):

    if not text:
        return ""

    match = re.search(
        r"```(?:html)?\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        code = match.group(1).strip()
    else:
        code = text.strip()

    html_start = code.lower().find(
        "<!doctype html>"
    )

    if html_start == -1:

        html_start = code.lower().find(
            "<html"
        )

    if html_start >= 0:

        code = code[html_start:]

    return code.strip()


def _is_valid_html(code):

    if not code:
        return False

    code_lower = code.lower()

    return (
        "<html" in code_lower
        or "<!doctype html>" in code_lower
    )


# ==========================================
# HÀM RENDER CHÍNH
# ==========================================

def render_mo_phong(ai_engine):

    st.markdown(
        "### 📊 MÔ PHỎNG & THÍ NGHIỆM ẢO"
    )

    # ======================================
    # KHỞI TẠO SESSION STATE
    # ======================================

    if "kb_mp" not in st.session_state:

        st.session_state.kb_mp = ""

    if "code_mp" not in st.session_state:

        st.session_state.code_mp = ""

    if "link_yt_mp" not in st.session_state:

        st.session_state.link_yt_mp = ""

    if "ten_mp" not in st.session_state:

        st.session_state.ten_mp = ""

    # ======================================
    # 3 TAB CHÍNH
    # ======================================

    tab_ai, tab_phet, tab_kho = st.tabs(
        [
            "🤖 AI XÂY DỰNG MÔ PHỎNG",
            "🧪 PHÒNG THÍ NGHIỆM ẢO",
            "📚 KHO MÔ PHỎNG CỦA TÔI"
        ]
    )

    # ==========================================
    # TAB 1: AI XÂY DỰNG MÔ PHỎNG
    # ==========================================

    with tab_ai:

        st.markdown(
            "#### 🛠️ Khởi tạo Mô phỏng Mới"
        )

        ten_mp = st.text_input(
            "Tên mô phỏng:",
            placeholder=(
                "Ví dụ: Mô phỏng sự rơi tự do"
            )
        )

        mo_ta = st.text_area(
            "Mô tả mô phỏng cần xây dựng:",
            placeholder=(
                "Ví dụ: Tạo mô phỏng sự rơi tự do "
                "của một quả bóng. Cho phép điều chỉnh "
                "độ cao, khối lượng và gia tốc trọng trường..."
            ),
            height=150
        )

        col_mon, col_lop = st.columns(2)

        with col_mon:

            mon_hoc = st.selectbox(
                "Môn:",
                [
                    "KHTN",
                    "Vật lý",
                    "Hóa học",
                    "Sinh học",
                    "Toán"
                ]
            )

        with col_lop:

            lop = st.selectbox(
                "Lớp:",
                [
                    "6",
                    "7",
                    "8",
                    "9",
                    "Khác"
                ]
            )

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:

            btn_kb = st.button(
                "✨ TẠO KỊCH BẢN",
                use_container_width=True,
                type="primary"
            )

        with col_btn2:

            btn_code = st.button(
                "💻 SINH MÃ MÔ PHỎNG",
                use_container_width=True,
                type="primary"
            )

        # ======================================
        # TẠO KỊCH BẢN
        # ======================================

        if btn_kb:

            if not mo_ta.strip():

                st.warning(
                    "⚠️ Thầy vui lòng nhập mô tả mô phỏng trước!"
                )

            elif ai_engine is None:

                st.error(
                    "❌ AI Engine chưa được khởi tạo."
                )

            else:

                prompt_kb = f"""
Bạn là chuyên gia thiết kế mô phỏng
khoa học và giáo dục STEM cho học sinh THCS.

Hãy viết kịch bản chi tiết để lập trình
một mô phỏng tương tác.

Tên mô phỏng:
{ten_mp}

Môn học:
{mon_hoc}

Khối lớp:
{lop}

Mô tả:
{mo_ta}

Kịch bản cần bao gồm:

1. Mục tiêu học tập.
2. Hiện tượng khoa học.
3. Cơ sở lý thuyết.
4. Các đại lượng và biến số.
5. Các thanh trượt hoặc nút điều khiển.
6. Cách mô phỏng hoạt động.
7. Kết quả cần quan sát.
8. Câu hỏi khám phá.
9. Câu hỏi vận dụng.

Nội dung phải chính xác về khoa học
và phù hợp với học sinh THCS.
"""

                with st.spinner(
                    "🧠 AI đang xây dựng kịch bản..."
                ):

                    try:

                        scenario = (
                            ai_engine.generate_text(
                                prompt_kb
                            )
                        )

                        st.session_state.kb_mp = scenario

                        st.session_state.ten_mp = (
                            ten_mp
                        )

                        st.success(
                            "✅ Đã tạo kịch bản thành công!"
                        )

                    except Exception as e:

                        st.error(
                            f"Lỗi AI: {e}"
                        )

        # ======================================
        # SINH MÃ MÔ PHỎNG
        # ======================================

        if btn_code:

            if (
                not mo_ta.strip()
                and not st.session_state.kb_mp
            ):

                st.warning(
                    "⚠️ Thầy vui lòng nhập mô tả "
                    "hoặc tạo kịch bản trước!"
                )

            elif ai_engine is None:

                st.error(
                    "❌ AI Engine chưa được khởi tạo."
                )

            else:

                base_context = (

                    st.session_state.kb_mp

                    if st.session_state.kb_mp

                    else mo_ta
                )

                prompt_code = f"""
Bạn là lập trình viên Frontend chuyên nghiệp
và chuyên gia xây dựng mô phỏng khoa học
cho giáo dục THCS.

Hãy viết toàn bộ mã nguồn HTML, CSS và
JavaScript trong một file HTML duy nhất.

Tên mô phỏng:
{ten_mp}

Môn học:
{mon_hoc}

Khối lớp:
{lop}

Nội dung mô phỏng:
{base_context}

YÊU CẦU BẮT BUỘC:

1. Sử dụng HTML5 Canvas hoặc SVG.

2. Có giao diện trực quan.

3. Có thanh trượt input range.

4. Có các nút điều khiển.

5. Có hiển thị kết quả theo thời gian thực.

6. Có công thức khoa học.

7. Có phần giải thích hiện tượng.

8. Có thể chạy độc lập trên trình duyệt.

9. Không sử dụng backend.

10. Không sử dụng API Key.

11. Không phụ thuộc vào server bên ngoài.

12. Mã phải nằm trong một file HTML duy nhất.

CHỈ TRẢ VỀ MÃ HTML.
KHÔNG GIẢI THÍCH.
"""

                with st.spinner(
                    "🤖 AI đang lập trình mô phỏng..."
                ):

                    try:

                        raw_code = (
                            ai_engine.generate_text(
                                prompt_code
                            )
                        )

                        clean_code = (
                            _extract_html_code(
                                raw_code
                            )
                        )

                        if _is_valid_html(
                            clean_code
                        ):

                            st.session_state.code_mp = (
                                clean_code
                            )

                            st.success(
                                "✅ Đã lập trình xong!"
                            )

                        else:

                            st.error(
                                "❌ AI không trả về mã HTML hợp lệ."
                            )

                    except Exception as e:

                        st.error(
                            f"Lỗi AI: {e}"
                        )

        # ======================================
        # KẾT QUẢ
        # ======================================

        st.markdown("---")

        out_tab_kb, out_tab_code, out_tab_run = st.tabs(
            [
                "📋 KỊCH BẢN",
                "💻 MÃ NGUỒN",
                "▶️ CHẠY MÔ PHỎNG"
            ]
        )

        # ======================================
        # KỊCH BẢN
        # ======================================

        with out_tab_kb:

            if st.session_state.kb_mp:

                st.markdown(
                    st.session_state.kb_mp
                )

            else:

                st.info(
                    "Chưa có kịch bản."
                )

        # ======================================
        # MÃ NGUỒN
        # ======================================

        with out_tab_code:

            if st.session_state.code_mp:

                st.code(
                    st.session_state.code_mp,
                    language="html"
                )

                st.download_button(
                    label="📥 TẢI MÃ NGUỒN HTML",
                    data=st.session_state.code_mp,
                    file_name="mo_phong_ai.html",
                    mime="text/html",
                    use_container_width=True
                )

            else:

                st.info(
                    "Chưa có mã nguồn."
                )

        # ======================================
        # CHẠY MÔ PHỎNG
        # ======================================

        with out_tab_run:

            if st.session_state.code_mp:

                st.success(
                    "Tương tác trực tiếp với mô phỏng:"
                )

                components.html(
                    st.session_state.code_mp,
                    height=650,
                    scrolling=True
                )

                st.markdown("---")

                st.info(
                    "💡 Sau khi mô phỏng chạy ổn định, "
                    "thầy có thể quay màn hình và đăng "
                    "video lên YouTube để lưu trữ."
                )

            else:

                st.info(
                    "Nhấn 'Sinh mã mô phỏng' để chạy thử."
                )

    # ==========================================
    # TAB 2: PHÒNG THÍ NGHIỆM ẢO
    # ==========================================

    with tab_phet:

        st.markdown(
            "#### Khám phá kho học liệu chuẩn quốc tế"
        )

        st.info(
            "💡 Các nền tảng sẽ được mở trong tab mới."
        )

        col_phet, col_moza = st.columns(2)

        with col_phet:

            st.markdown(
                "### ⚛️ PhET Simulations"
            )

            st.markdown(
                "Kho mô phỏng tương tác Khoa học "
                "Tự nhiên và Toán học của Đại học "
                "Colorado Boulder."
            )

            st.link_button(
                "🚀 MỞ PHET TIẾNG VIỆT",
                "https://phet.colorado.edu/vi/",
                use_container_width=True
            )

        with col_moza:

            st.markdown(
                "### 🧬 MozaWeb 3D"
            )

            st.markdown(
                "Thư viện cảnh 3D tương tác "
                "và học liệu giáo dục."
            )

            st.link_button(
                "🌐 MỞ MOZAWEB 3D",
                "https://mozaweb.vn/vi/lexikon.php?cmd=getlist&let=3D&sid=BIO",
                use_container_width=True
            )

    # ==========================================
    # TAB 3: KHO MÔ PHỎNG
    # ==========================================

    with tab_kho:

        st.markdown(
            "#### 📚 Quản lý & Chia sẻ"
        )

        st.markdown(
            "### 🎥 Lưu mô phỏng bằng YouTube"
        )

        link_yt = st.text_input(
            "Dán link YouTube:",
            key="link_yt_mp"
        )

        if link_yt:

            st.video(
                link_yt
            )

            if st.button(
                "💾 LƯU VÀO KHO",
                use_container_width=True
            ):

                st.session_state[
                    "youtube_saved_mp"
                ] = link_yt

                st.success(
                    "✅ Đã lưu liên kết mô phỏng."
                )

        saved_link = st.session_state.get(
            "youtube_saved_mp",
            ""
        )

        if saved_link:

            st.markdown(
                "### 📌 Mô phỏng đã lưu"
            )

            st.video(
                saved_link
            )

        st.markdown("---")

        st.markdown(
            "### 💻 Mô phỏng HTML hiện tại"
        )

        if st.session_state.code_mp:

            st.success(
                "Đã có mô phỏng HTML trong phiên làm việc."
            )

            st.download_button(
                "📥 TẢI MÔ PHỎNG HTML",
                data=st.session_state.code_mp,
                file_name="mo_phong.html",
                mime="text/html",
                use_container_width=True
            )

        else:

            st.info(
                "Chưa có mô phỏng HTML."
            )
