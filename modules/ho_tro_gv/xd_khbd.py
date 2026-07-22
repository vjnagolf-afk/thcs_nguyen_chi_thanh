# -*- coding: utf-8 -*-
import streamlit as st

def init_session_state():
    if "hoat_dong_list" not in st.session_state:
        st.session_state.hoat_dong_list = []

def add_hoat_dong():
    new_hd = st.session_state.get("new_hoat_dong", "").strip()
    if new_hd and new_hd not in st.session_state.hoat_dong_list:
        st.session_state.hoat_dong_list.append(new_hd)
    st.session_state["new_hoat_dong"] = "" # Xóa trắng input sau khi thêm

def render_giao_an_ui(ai_engine=None):
    init_session_state()

    # Nhúng CSS tùy chỉnh để làm nút bấm màu tím và tinh chỉnh khoảng cách
    st.markdown("""
        <style>
        /* Tùy chỉnh màu sắc nút bấm chính (Primary Button) thành màu tím */
        .stButton button[kind="primary"] {
            background-color: #9333ea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #7e22ce;
            border: none;
        }
        
        /* Tùy chỉnh màu sắc nút outline */
        .stButton button[kind="secondary"] {
            color: #4b5563;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-weight: 600;
        }
        .stButton button[kind="secondary"]:hover {
            border-color: #9333ea;
            color: #9333ea;
        }
        
        /* Giảm khoảng cách giữa các phần tử để UI gọn gàng như bản thiết kế */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # =======================================================
    # 1. THÔNG TIN BÀI DẠY
    # =======================================================
    st.markdown("### 🎛️ Thông tin bài dạy")
    c_khoi, c_mon = st.columns(2)
    with c_khoi:
        st.selectbox("KHỐI LỚP", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
    with c_mon:
        st.selectbox("MÔN HỌC", ["Khoa học tự nhiên", "Toán", "Ngữ văn", "Tin học", "Công nghệ"])

    st.write("") # Dòng trống tạo khoảng cách

    # =======================================================
    # 2. CHẾ ĐỘ TÍCH HỢP (CARDS)
    # =======================================================
    st.markdown("#### ✨ Chế độ tích hợp")
    c_th1, c_th2, c_th3 = st.columns(3)
    
    with c_th1:
        with st.container(border=True):
            tich_hop_nls = st.checkbox("**Tích hợp Năng lực số (NLS)**", help="Lồng ghép NLS theo PPCT")
            st.caption("Lồng ghép NLS theo PPCT")
            
    with c_th2:
        with st.container(border=True):
            tich_hop_ai = st.checkbox("**Tích hợp Năng lực AI**", help="Lồng ghép AI theo Bảng yêu cầu")
            st.caption("Lồng ghép AI theo Bảng yêu cầu")
            
    with c_th3:
        with st.container(border=True):
            tich_hop_kt = st.checkbox("**Tích hợp Dạy học khuyết tật hòa nhập**", help="Lồng ghép hỗ trợ HSKT")
            st.caption("Lồng ghép hỗ trợ HSKT")

    st.write("")
    
    # 2 NÚT THAO TÁC CHÍNH (Nằm giữa màn hình)
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        st.button("📄 CHỈNH SỬA GIÁO ÁN GỐC", use_container_width=True)
    with c_btn2:
        st.button("⚡ TỰ ĐỘNG SOẠN TỪ SGK", type="primary", use_container_width=True)

    st.divider()

    # =======================================================
    # 3. THÔNG TIN GIÁO ÁN SOẠN MỚI
    # =======================================================
    st.markdown("### 📄 Thông tin giáo án soạn mới")
    
    c_cap, c_mau = st.columns(2)
    with c_cap:
        st.selectbox("Cấp học", ["THCS", "Tiểu học", "THPT"])
    with c_mau:
        st.selectbox("Mẫu giáo án", ["Công văn 5512 (Chuẩn Bộ)", "Mẫu rút gọn", "Mẫu tư duy"])

    c_ten, c_tg = st.columns(2)
    with c_ten:
        st.text_input("Tên bài dạy", placeholder="VD: Định dạng văn bản")
    with c_tg:
        st.text_input("Thời lượng (Số tiết)", placeholder="VD: 2 tiết")

    # =======================================================
    # 4. TẢI LÊN TÀI LIỆU
    # =======================================================
    st.markdown("**Hình ảnh / PDF SGK cơ sở** *(Khuyến nghị chụp thật nét)*")
    with st.container(border=True):
        sgk_files = st.file_uploader(
            "Kéo thả hoặc Nhấn để tải lên Sách Giáo Khoa", 
            type=["pdf", "jpg", "png"],
            accept_multiple_files=True,
            help="Hỗ trợ định dạng PDF, JPG, PNG (Tối đa 50MB)"
        )

    # =======================================================
    # 5. KẾ HOẠCH HOẠT ĐỘNG
    # =======================================================
    st.markdown("**Kế hoạch Hoạt động (Tùy chọn)**")
    st.caption("Nhập các hoạt động cần thiết, AI sẽ tự động phân rã nếu để trống.")
    
    c_input, c_add = st.columns([4, 1])
    with c_input:
        st.text_input(
            "Nhập hoạt động", 
            placeholder="VD: Tìm hiểu cấu trúc máy tính...", 
            key="new_hoat_dong", 
            label_visibility="collapsed",
            on_change=add_hoat_dong # Hỗ trợ nhấn Enter để thêm
        )
    with c_add:
        st.button("Thêm", on_click=add_hoat_dong, type="primary", use_container_width=True)
    
    # Hiển thị danh sách hoạt động đã thêm dưới dạng Tags
    if st.session_state.hoat_dong_list:
        for i, hd in enumerate(st.session_state.hoat_dong_list):
            c_tag1, c_tag2 = st.columns([11, 1])
            with c_tag1:
                st.info(f"📍 {hd}")
            with c_tag2:
                if st.button("❌", key=f"del_{i}", help="Xóa"):
                    st.session_state.hoat_dong_list.remove(hd)
                    st.rerun()

    st.write("")

    # =======================================================
    # 6. KHỐI HIỂN THỊ CÓ ĐIỀU KIỆN (Dựa vào Chế độ Tích hợp)
    # =======================================================
    
    # Nếu chọn Tích hợp NLS hoặc AI -> Hiển thị khối Tải tài liệu bổ sung
    if tich_hop_nls or tich_hop_ai:
        st.markdown("### 📤 Tài liệu tích hợp bổ sung")
        c_tl1, c_tl2 = st.columns(2)
        
        if tich_hop_nls:
            with c_tl1:
                with st.container(border=True):
                    st.file_uploader("📄 Tải lên PPCT (Năng lực số)", type=["pdf", "docx", "xlsx"])
                    
        if tich_hop_ai:
            with c_tl2:
                with st.container(border=True):
                    # Dòng này mô phỏng nút badge "Chuyển sang công cụ Tạo Bảng AI"
                    st.markdown("[Chuyển sang công cụ Tạo Bảng AI ↗](#)", unsafe_allow_html=True) 
                    st.file_uploader("📋 Tải lên Bảng tích hợp AI", type=["pdf", "docx", "xlsx"])

    # Nếu chọn Khuyết tật -> Hiển thị Pills chọn loại khuyết tật (Streamlit 1.40+)
    if tich_hop_kt:
        with st.container(border=True):
            st.markdown("#### 🎯 Chọn dạng khuyết tật hòa nhập")
            st.caption("Giáo án sẽ được điều chỉnh cho phù hợp (chọn nhiều nếu cần)")
            
            danh_sach_kt = [
                "Khuyết tật vận động", "Khuyết tật nghe", "Khuyết tật nói", 
                "Khuyết tật nhìn", "Khuyết tật thần kinh", "Khuyết tật tâm thần", 
                "Khuyết tật trí tuệ", "Khuyết tật tự kỷ", "Khuyết tật khác", 
                "Khuyết tật chung"
            ]
            
            loai_kt = st.pills(
                "Chọn khuyết tật", 
                danh_sach_kt, 
                selection_mode="multi", 
                label_visibility="collapsed",
                default=["Khuyết tật chung"]
            )

    # Nếu chọn Năng lực số -> Hiển thị Yêu cầu cụ thể
    if tich_hop_nls:
        with st.container(border=True):
            co_yc_nls = st.checkbox("🎯 **Yêu cầu Năng lực số cụ thể (Tùy chọn)**")
            if co_yc_nls:
                st.text_area("Chỉ định rõ thành phần và mức độ NLS cho AI", placeholder="Nhập yêu cầu tại đây...")

    # =======================================================
    # 7. TÙY CHỌN NGÔN NGỮ & NÚT KÍCH HOẠT CHÍNH
    # =======================================================
    st.write("")
    with st.container(border=True):
        giao_an_ta = st.checkbox("Giáo án viết bằng ngôn ngữ Tiếng Anh")

    st.write("")
    btn_kich_hoat = st.button("⚡ KÍCH HOẠT XỬ LÝ AI", type="primary", use_container_width=True)
    
    if btn_kich_hoat:
        st.success("Hệ thống AI đang bắt đầu xử lý theo cấu hình của thầy!")

# Để chạy thử nghiệm, gọi hàm:
# render_giao_an_ui()
