# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/quan_ly_to/sach_kn_so.py
Mô tả: Tủ sách Kỹ năng số cho Giáo viên & Lớp học trực tuyến.
Tính năng:
    - Trưng bày các chuyên mục cẩm nang AI, Công cụ tương tác, Quản trị lớp học.
    - Xem video bài giảng trực tiếp qua Streamlit.
    - Hỗ trợ thêm/xóa bài giảng video linh hoạt theo chuyên mục.
    - 💬 Khung chat trực tuyến tương tác giữa giáo viên và học sinh.
============================================================
"""

import streamlit as st
from datetime import datetime

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

    # Khởi tạo kho lưu trữ tin nhắn chat cho từng chuyên mục
    if "phong_chat" not in st.session_state:
        st.session_state.phong_chat = {
            "AI": [],
            "TuongTac": [],
            "QuanTri": []
        }

    st.markdown("### 📘 Tủ sách Kỹ năng số & Lớp học trực tuyến")
    st.caption("Kho tài liệu, cẩm nang hướng dẫn ứng dụng CNTT, AI và phòng học tương tác thời gian thực.")

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
    # MÀN HÌNH 2: BÊN TRONG LỚP HỌC (Video + Khung Chat Trực Tuyến)
    # ==========================================
    else:
        if st.button("⬅️ Quay lại Danh mục", type="secondary"):
            st.session_state.chuyen_muc_dang_mo = None
            st.rerun()
            
        st.markdown("---")
        cm = st.session_state.chuyen_muc_dang_mo
        
        if cm == "AI": st.markdown("#### 🤖 Lớp học Trực tuyến: Cẩm nang ứng dụng AI")
        elif cm == "TuongTac": st.markdown("#### 🖥️ Lớp học Trực tuyến: Công cụ Tương tác lớp học")
        elif cm == "QuanTri": st.markdown("#### 📊 Lớp học Trực tuyến: Quản trị Lớp học & Hồ sơ số")

        # Chia bố cục: Bên trái là Video bài giảng, Bên phải là Khung Chat thảo luận trực tiếp
        col_video, col_chat = st.columns([7, 4])

        with col_video:
            st.markdown("##### 📺 Bài giảng video")
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

            # 2. KHU VỰC NHÚNG THÊM VIDEO MỚI (Dành cho Giáo viên)
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

        with col_chat:
            st.markdown("##### 💬 Thảo luận & Chat trực tiếp")
            
            # Khung chứa lịch sử chat cuộn được
            chat_container = st.container(height=420)
            with chat_container:
                if len(st.session_state.phong_chat[cm]) == 0:
                    st.caption("Chưa có tin nhắn nào. Hãy là người đầu tiên đặt câu hỏi cho bài giảng!")
                else:
                    for chat in st.session_state.phong_chat[cm]:
                        st.markdown(f"**{chat['nguoi_gui']}** <span style='font-size:10px; color:gray;'>({chat['thoi_gian']})</span><br>{chat['noi_dung']}", unsafe_allow_html=True)
                        st.markdown("---")

            # Form gửi tin nhắn chat nhanh
            with st.form(f"form_chat_{cm}", clear_on_submit=True):
                ten_nguoi_gui = st.text_input("Tên của bạn (Học sinh / Giáo viên):", placeholder="VD: Nguyễn Văn A...")
                noi_dung_chat = st.text_area("Nội dung thảo luận / Đặt câu hỏi:", placeholder="Nhập câu hỏi tại đây...", height=70)
                btn_gui_chat = st.form_submit_button("📤 Gửi tin nhắn", type="primary", use_container_width=True)
                
                if btn_gui_chat:
                    if ten_nguoi_gui.strip() and noi_dung_chat.strip():
                        thoi_gian_hien_tai = datetime.now().strftime("%H:%M:%S")
                        st.session_state.phong_chat[cm].append({
                            "nguoi_gui": ten_nguoi_gui.strip(),
                            "noi_dung": noi_dung_chat.strip(),
                            "thoi_gian": thoi_gian_hien_tai
                        })
                        st.rerun()
                    else:
                        st.warning("⚠️ Vui lòng nhập đầy đủ Tên và Nội dung tin nhắn!")
