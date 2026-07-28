# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ung_dung_khac/the_02_embed_hub.py
Nhiệm vụ: Không gian Nhúng Tài nguyên (YouTube & Canva Embed).
Chức năng: Nhúng trực tiếp video bài giảng YouTube hoặc trò chơi, 
bài tập tương tác do Canva thiết kế vào hệ thống Streamlit.
============================================================
"""

import streamlit as st
import streamlit.components.v1 as components

def render_the_02(ai_engine=None):
    st.markdown("### 🌐 Không gian Nhúng Tài nguyên (YouTube & Canva Embed)")
    st.caption("Trợ giúp giáo viên nhúng trực tiếp video bài giảng YouTube hoặc các trò chơi, bài tập tương tác do Canva thiết kế vào hệ thống.")

    sub_tab1, sub_tab2 = st.tabs(["📺 Nhúng Video YouTube", "🎨 Nhúng Trò chơi / Thiết kế Canva"])

    # ============================================================
    # SUB-TAB 1: NHÙNG YOUTUBE
    # ============================================================
    with sub_tab1:
        st.markdown("#### Trình phát & Quản lý Video YouTube")
        yt_input = st.text_input(
            "Nhập Link YouTube hoặc Mã nhúng iframe",
            placeholder="Ví dụ: https://www.youtube.com/watch?v=... hoặc dán đoạn mã <iframe...> vào đây",
            key="the2_yt_input"
        )
        
        if yt_input:
            if "<iframe" in yt_input:
                st.markdown("**Bản xem trước từ mã nhúng:**")
                components.html(yt_input, height=450, scrolling=True)
            else:
                try:
                    st.markdown("**Bản xem trước trực tiếp:**")
                    st.video(yt_input)
                except Exception as e:
                    st.error(f"Không thể tải video từ liên kết này. Vui lòng kiểm tra lại URL. Lỗi: {e}")
        else:
            st.info("💡 Nhập đường dẫn YouTube hoặc dán đoạn mã iframe để hiển thị video trực tiếp tại đây.")

    # ============================================================
    # SUB-TAB 2: NHÙNG CANVA (TRÒ CHƠI / THUYẾT TRÌNH)
    # ============================================================
    with sub_tab2:
        st.markdown("#### Trình hiển thị Trò chơi / Thiết kế tương tác từ Canva")
        st.info(
            "💡 **Hướng dẫn lấy mã nhúng từ Canva:**\n"
            "1. Mở thiết kế hoặc trò chơi của thầy trên Canva.\n"
            "2. Bấm nút **Chia sẻ (Share)** ở góc trên bên phải.\n"
            "3. Chọn **Nhúng (Embed)** -> Copy đoạn **Mã nhúng HTML (Smart embed code)** có dạng `<iframe ...></iframe>` và dán vào ô bên dưới."
        )
        
        canva_input = st.text_area(
            "Dán mã nhúng iframe từ Canva vào đây",
            placeholder='Ví dụ: <iframe loading="lazy" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none;" src="..." allowfullscreen="allowfullscreen"></iframe>',
            height=150,
            key="the2_canva_input"
        )

        c1, c2 = st.columns(2)
        iframe_height = c1.slider("Độ cao khung hiển thị (Pixel)", min_value=400, max_value=900, value=550, step=50, key="the2_height")
        
        if st.button("🚀 Hiển thị nội dung Canva", type="primary", key="btn_render_canva"):
            if canva_input and "<iframe" in canva_input:
                st.success("🎉 Đã tải thành công thiết kế/trò chơi từ Canva lên hệ thống!")
                st.markdown("**Bản xem trước tương tác trực tiếp:**")
                components.html(canva_input, height=iframe_height, scrolling=True)
            else:
                st.warning("⚠️ Vui lòng dán đúng định dạng mã nhúng chứa thẻ `<iframe ...></iframe>` do Canva cung cấp.")
