# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/quan_ly_to/sach_kn_so.py
Mô tả: Tủ sách Kỹ năng số cho Giáo viên.
Tính năng:
    - Trưng bày các chuyên mục cẩm nang AI, Công cụ tương tác, Quản trị lớp học.
    - Xem video bài giảng trực tiếp qua Streamlit.
    - Hỗ trợ thêm/xóa bài giảng video linh hoạt theo chuyên mục.
============================================================
"""

import streamlit as st

def render_sach_kn_so():
    # --- KHỞI TẠO BỘ NHỚ TẠM ---
    if "chuyen_muc_dang_mo" not in st.session_state:
        st.session_state.chuyen_muc_dang_mo = None

    if "kho_video" not in st.session_state:
        st.session_state.kho_video = {
            "AI": ["https://www.youtube.com/watch?v=yW6K2ZtO-X4"], 
            "TuongTac": [],
            "QuanTri": []
        }

    st.markdown("### 📘 Tủ sách Kỹ năng số cho Giáo viên")
    st.caption("Kho tài liệu, cẩm nang hướng dẫn ứng dụng công nghệ thông tin và AI vào công tác giảng dạy.")

    # ==========================================
    # MÀN HÌNH 1: DANH MỤC CHÍNH
    # ==========================================
    if st.session_state.chuyen_muc_dang_mo is None:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🤖 Cẩm nang AI")
            st.info("- Hướng dẫn cơ bản sử dụng ChatGPT\n- Kỹ năng viết Prompt sư phạm\n- Ứng dụng Gemini trong soạn giảng")
            if st.button("📖 Vào lớp học AI", key="doc_ai", type="primary", use_container_width=True):
                st.session_state.chuyen_muc_dang_mo = "AI"
                st.rerun()
            
        with col2:
            st.markdown("#### 🖥️ Công cụ Tương tác")
            st.success("- Hướng dẫn tạo Quizizz / Kahoot\n- Tổ chức lớp học với Padlet\n- Sử dụng phòng thí nghiệm ảo (PhET)")
            if st.button("📖 Vào lớp Tương tác", key="doc_tt", type="primary", use_container_width=True):
                st.session_state.chuyen_muc_dang_mo = "TuongTac"
                st.rerun()
            
        with col3:
            st.markdown("#### 📊 Quản trị Lớp học")
            st.warning("- Quản lý điểm số nâng cao với Excel\n- Xây dựng hồ sơ số, Google Classroom\n- Bảo mật thông tin học sinh")
            if st.button("📖 Vào lớp Quản trị", key="doc_ql", type="primary", use_container_width=True):
                st.session_state.chuyen_muc_dang_mo = "QuanTri"
                st.rerun()
            
        st.markdown("---")
        st.markdown("#### 🔍 Tìm kiếm tài liệu khác")
        tim_kiem = st.text_input("Nhập từ khóa tài liệu bạn muốn tìm (VD: Canva, PowerPoint...):")
        if tim_kiem:
            st.write(f"Đang tìm kiếm tài liệu liên quan đến: **{tim_kiem}**... (Tính năng kết nối kho lưu trữ đang hoàn thiện)")

    # ==========================================
    # MÀN HÌNH 2: BÊN TRONG LỚP HỌC (Hiển thị Video và Form)
    # ==========================================
    else:
        if st.button("⬅️ Quay lại Danh mục", type="secondary"):
            st.session_state.chuyen_muc_dang_mo = None
            st.rerun()
            
        st.markdown("---")
        cm = st.session_state.chuyen_muc_dang_mo
        
        if cm == "AI": st.markdown("#### 🤖 Kho Video: Cẩm nang ứng dụng AI")
        elif cm == "TuongTac": st.markdown("#### 🖥️ Kho Video: Công cụ Tương tác lớp học")
        elif cm == "QuanTri": st.markdown("#### 📊 Kho Video: Quản trị Lớp học & Hồ sơ số")

        # 1. KHU VỰC HIỂN THỊ VÀ XÓA VIDEO
        if len(st.session_state.kho_video[cm]) == 0:
            st.info("💡 Chuyên mục này hiện chưa có video nào. Thầy hãy dùng form bên dưới để thêm mới nhé!")
        else:
            for idx, link_video in enumerate(st.session_state.kho_video[cm]):
                col_title, col_del = st.columns([5, 1])
                with col_title:
                    st.markdown(f"**Bài học {idx + 1}:**")
                with col_del:
                    if st.button("🗑️ Xóa", key=f"del_{cm}_{idx}", type="secondary", use_container_width=True):
                        st.session_state.kho_video[cm].pop(idx)
                        st.rerun()
                try:
                    st.video(link_video)
                except Exception:
                    st.error(f"Không thể tải video từ link: {link_video}")
                st.markdown("<br>", unsafe_allow_html=True)

        # 2. KHU VỰC NHÚNG THÊM VIDEO MỚI
        st.markdown("---")
        with st.expander("➕ Dành cho Quản trị viên: Thêm bài giảng Video mới", expanded=False):
            with st.form(f"form_nhung_video_{cm}", clear_on_submit=True):
                st.caption("Dán đường link YouTube của bài giảng vào đây để đưa lên hệ thống.")
                link_moi = st.text_input("https://youtu.be/eKprZGSi3ro")
                
                submitted = st.form_submit_button("Lưu Video", type="primary")
                if submitted:
                    if link_moi.strip():
                        st.session_state.kho_video[cm].append(link_moi.strip())
                        st.success("✅ Đã thêm video thành công!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Thầy chưa nhập link video!")
