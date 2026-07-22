# -*- coding: utf-8 -*-
import streamlit as st

def init_session_state():
    if "hoat_dong_list" not in st.session_state:
        st.session_state.hoat_dong_list = []
    if "soan_mode" not in st.session_state:
        st.session_state.soan_mode = "chinh_sua" 
    if "nls_list" not in st.session_state:
        st.session_state.nls_list = []

def add_hoat_dong():
    new_hd = st.session_state.get("new_hoat_dong", "").strip()
    if new_hd and new_hd not in st.session_state.hoat_dong_list:
        st.session_state.hoat_dong_list.append(new_hd)
    st.session_state["new_hoat_dong"] = ""

def set_mode(mode):
    st.session_state.soan_mode = mode

def add_nls_item():
    tp = st.session_state.get("nls_tp", "")
    md = st.session_state.get("nls_md", "")
    nd = st.session_state.get("nls_nd", "").strip()
    if nd:
        st.session_state.nls_list.append({
            "thanh_phan": tp, 
            "muc_do": md, 
            "noi_dung": nd
        })
        st.session_state["nls_nd"] = "" # Reset textarea sau khi thêm

def render_xd_khbd(ai_engine=None):
    init_session_state()

    # Nhúng CSS tùy chỉnh
    st.markdown('''
        <style>
        .stButton button[kind="primary"] { background-color: #9333ea; color: white; border: none; border-radius: 8px; font-weight: bold; transition: 0.3s;}
        .stButton button[kind="primary"]:hover { background-color: #7e22ce; border: none; }
        .stButton button[kind="secondary"] { color: #6b7280; border: 1px solid #e5e7eb; border-radius: 8px; font-weight: 600; background-color: #f9fafb; transition: 0.3s;}
        .stButton button[kind="secondary"]:hover { border-color: #9333ea; color: #9333ea; background-color: #f3e8ff;}
        
        /* Cố gắng bôi hồng nút Thêm vào danh sách (CSS Hacking) */
        button:has(div:contains("Thêm vào danh sách")) { background-color: #e81e63 !important; border-color: #e81e63 !important; }
        button:has(div:contains("Thêm vào danh sách")):hover { background-color: #c2185b !important; }

        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .upload-card { text-align: center; padding: 10px; }
        .upload-icon { font-size: 2.5rem; color: #9333ea; margin-bottom: 10px; }
        .upload-title { font-weight: bold; font-size: 1.1rem; color: #1f2937; margin-bottom: 5px; }
        .upload-desc { font-size: 0.85rem; color: #6b7280; line-height: 1.4; }
        </style>
    ''', unsafe_allow_html=True)

    # Dữ liệu Năng lực số
    THANH_PHAN_NLS = [
        "1.1. Duyệt, tìm kiếm và lọc dữ liệu, thông tin và nội dung số",
        "1.2. Đánh giá dữ liệu, thông tin và nội dung số",
        "1.3. Quản lý dữ liệu, thông tin và nội dung số",
        "2.1. Tương tác thông qua công nghệ số",
        "2.2. Chia sẻ thông tin và nội dung thông qua công nghệ số",
        "2.3. Sử dụng công nghệ số để thực hiện trách nhiệm công dân",
        "2.4. Hợp tác thông qua công nghệ số",
        "2.5. Quy tắc ứng xử trên mạng",
        "2.6. Quản lý danh tính số",
        "3.1. Phát triển nội dung số",
        "3.2. Tích hợp và tạo lập lại nội dung số",
        "3.3. Thực thi bản quyền và giấy phép",
        "3.4. Lập trình",
        "4.1. Bảo vệ thiết bị",
        "4.2. Bảo vệ dữ liệu cá nhân và quyền riêng tư",
        "4.3. Bảo vệ sức khỏe và an sinh số",
        "4.4. Bảo vệ môi trường",
        "5.1. Giải quyết các vấn đề kỹ thuật",
        "5.2. Xác định nhu cầu và giải pháp công nghệ",
        "5.3. Sử dụng sáng tạo công nghệ số",
        "5.4. Xác định các vấn đề cần cải thiện về NLS",
        "6.1. Hiểu biết về trí tuệ nhân tạo",
        "6.2. Sử dụng trí tuệ nhân tạo",
        "6.3. Đánh giá trí tuệ nhân tạo"
    ]
    MUC_DO_NLS = ["-- Tự nhập --", "CB1a", "CB1b", "CB1c", "CB2a", "CB2b", "CB2c", "CB2d", "TC1a", "TC1b", "TC1c", "TC1d", "TC2a", "TC2b", "TC2c", "TC2d", "NC1a", "NC1b", "NC1c", "NC1d"]

    # =======================================================
    # 1. THÔNG TIN BÀI DẠY & CHẾ ĐỘ TÍCH HỢP
    # =======================================================
    st.markdown("### 🎛️ Thông tin bài dạy")
    c_khoi, c_mon = st.columns(2)
    with c_khoi:
        st.selectbox("KHỐI LỚP", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
    with c_mon:
        st.selectbox("MÔN HỌC", ["Khoa học tự nhiên", "Toán", "Ngữ văn", "Tin học", "Công nghệ"])

    st.write("")
    st.markdown("#### ✨ Chế độ tích hợp")
    c_th1, c_th2, c_th3 = st.columns(3)
    
    with c_th1:
        with st.container(border=True):
            tich_hop_nls = st.checkbox("**Tích hợp Năng lực số (NLS)**")
            st.caption("Lồng ghép NLS theo PPCT")
    with c_th2:
        with st.container(border=True):
            tich_hop_ai = st.checkbox("**Tích hợp Năng lực AI**")
            st.caption("Lồng ghép AI theo Bảng yêu cầu")
    with c_th3:
        with st.container(border=True):
            tich_hop_kt = st.checkbox("**Tích hợp Dạy học khuyết tật hòa nhập**")
            st.caption("Lồng ghép hỗ trợ HSKT")

    st.write("")
    
    # =======================================================
    # 2. NÚT CHUYỂN ĐỔI CHẾ ĐỘ (TOGGLE)
    # =======================================================
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        btn_chinh_sua = st.button("📄 CHỈNH SỬA GIÁO ÁN GỐC", 
                                  type="primary" if st.session_state.soan_mode == "chinh_sua" else "secondary", 
                                  use_container_width=True, 
                                  on_click=set_mode, args=("chinh_sua",))
    with c_btn2:
        btn_tu_dong = st.button("⚡ TỰ ĐỘNG SOẠN TỪ SGK", 
                                type="primary" if st.session_state.soan_mode == "tu_dong" else "secondary", 
                                use_container_width=True, 
                                on_click=set_mode, args=("tu_dong",))

    st.divider()

    # =======================================================
    # 3A. GIAO DIỆN: CHỈNH SỬA GIÁO ÁN GỐC 
    # =======================================================
    if st.session_state.soan_mode == "chinh_sua":
        with st.container(border=True):
            st.markdown("### 📤 Tài liệu đầu vào (Chỉ nên tải lên giáo án 1 tiết hoặc 1 bài)")
            
            c_up1, c_up2, c_up3 = st.columns(3)
            
            with c_up1:
                with st.container(border=True):
                    st.markdown('''
                        <div class="upload-card">
                            <div class="upload-icon">📄</div>
                            <div class="upload-title">Tải lên Giáo án gốc</div>
                            <div class="upload-desc">Hỗ trợ file Word (.docx), PDF, JPG, PNG. Bản đẹp, không phải bản scan.</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    # Hỗ trợ đa định dạng, cho phép tải nhiều file ảnh cùng lúc
                    st.file_uploader("Upload GA", type=["docx", "pdf", "jpg", "png", "jpeg"], accept_multiple_files=True, label_visibility="collapsed")
                st.markdown("<div style='text-align: center; color: #ef4444; font-size: 0.9em; margin-top: -10px;'>⚠️ Yêu cầu bắt buộc</div>", unsafe_allow_html=True)
                
            with c_up2:
                with st.container(border=True):
                    st.markdown('''
                        <div class="upload-card">
                            <div class="upload-icon" style="color: #6b7280;">📊</div>
                            <div class="upload-title">Tải lên PPCT</div>
                            <div class="upload-desc">Dùng để trích xuất chính xác năng lực số theo quy định nhà trường.</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    st.file_uploader("Upload PPCT", type=["pdf", "docx", "xlsx"], label_visibility="collapsed")
                    
            with c_up3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: right; margin-bottom: -15px;'><a href='#' style='font-size: 0.75rem; color: #9333ea; text-decoration: none; font-weight: 600; background: #f3e8ff; padding: 3px 8px; border-radius: 10px;'>Chuyển sang công cụ Tạo Bảng AI ↗</a></div>", unsafe_allow_html=True)
                    st.markdown('''
                        <div class="upload-card">
                            <div class="upload-icon" style="color: #6b7280;">📋</div>
                            <div class="upload-title">Tải lên Bảng tích hợp AI</div>
                            <div class="upload-desc">Nếu không tải, hệ thống sẽ tự động phân tích</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    st.file_uploader("Upload AI", type=["pdf", "docx", "xlsx"], label_visibility="collapsed")
                    
        st.warning("**Lời khuyên để tránh lỗi và tối ưu Quota:** Xin đừng đưa cả 1 kỳ học hoặc hàng chục trang giáo án vào cùng 1 lúc! Hãy tải **từng bài một (1 - 3 tiết)**. Việc tải khối lượng khổng lồ sẽ khiến AI bị ngợp sập bộ nhớ, làm hỏng bảng biểu và trừ một lúc sạch Quota sử dụng của bạn.", icon="⚠️")

    # =======================================================
    # 3B. GIAO DIỆN: TỰ ĐỘNG SOẠN TỪ SGK
    # =======================================================
    else:
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

        st.markdown("**Hình ảnh / PDF SGK cơ sở** *(Khuyến nghị chụp thật nét)*")
        with st.container(border=True):
            sgk_files = st.file_uploader("Kéo thả hoặc Nhấn để tải lên Sách Giáo Khoa", type=["pdf", "jpg", "png"], accept_multiple_files=True)

        st.markdown("**Kế hoạch Hoạt động (Tùy chọn)**")
        c_input, c_add = st.columns([4, 1])
        with c_input:
            st.text_input("Nhập hoạt động", placeholder="VD: Tìm hiểu cấu trúc máy tính...", key="new_hoat_dong", label_visibility="collapsed", on_change=add_hoat_dong)
        with c_add:
            st.button("Thêm", on_click=add_hoat_dong, type="primary", use_container_width=True)
        
        if st.session_state.hoat_dong_list:
            for i, hd in enumerate(st.session_state.hoat_dong_list):
                c_tag1, c_tag2 = st.columns([11, 1])
                with c_tag1: st.info(f"📍 {hd}")
                with c_tag2:
                    if st.button("❌", key=f"del_{i}", help="Xóa"):
                        st.session_state.hoat_dong_list.remove(hd)
                        st.rerun()

        if tich_hop_nls or tich_hop_ai:
            st.markdown("### 📤 Tài liệu tích hợp bổ sung")
            c_tl1, c_tl2 = st.columns(2)
            if tich_hop_nls:
                with c_tl1:
                    with st.container(border=True): st.file_uploader("📄 Tải lên PPCT (Năng lực số)", type=["pdf", "docx", "xlsx"])
            if tich_hop_ai:
                with c_tl2:
                    with st.container(border=True): st.file_uploader("📋 Tải lên Bảng tích hợp AI", type=["pdf", "docx", "xlsx"])

    # =======================================================
    # 4. CHỌN DẠNG KHUYẾT TẬT & YÊU CẦU NLS CHI TIẾT
    # =======================================================
    if tich_hop_kt:
        with st.container(border=True):
            st.markdown("#### 🎯 Chọn dạng khuyết tật hòa nhập")
            loai_kt = st.pills("Chọn khuyết tật", ["Khuyết tật vận động", "Khuyết tật nghe", "Khuyết tật nói", "Khuyết tật nhìn", "Khuyết tật thần kinh", "Khuyết tật tâm thần", "Khuyết tật trí tuệ", "Khuyết tật tự kỷ", "Khuyết tật khác", "Khuyết tật chung"], selection_mode="multi", default=["Khuyết tật chung"])

    # CHỨC NĂNG MỚI: YÊU CẦU NĂNG LỰC SỐ CỤ THỂ
    if tich_hop_nls:
        with st.container(border=True):
            co_yc_nls = st.checkbox("🎯 **Yêu cầu Năng lực số cụ thể (Tùy chọn)**", value=True) # Checkbox giống ảnh thiết kế
            if co_yc_nls:
                st.caption("Tích vào đây nếu bạn muốn chỉ định rõ thành phần và mức độ NLS cho AI")
                
                # Tạo 3 cột đúng tỷ lệ thiết kế
                c_tp, c_md, c_nd = st.columns([1.5, 1, 2.5])
                
                with c_tp:
                    st.selectbox("**1. THÀNH PHẦN**", THANH_PHAN_NLS, key="nls_tp")
                with c_md:
                    st.selectbox("**2. MỨC ĐỘ (TÙY CHỌN)**", MUC_DO_NLS, key="nls_md")
                with c_nd:
                    st.text_area("**3. NỘI DUNG YÊU CẦU**", placeholder="Mô tả năng lực hoặc hoạt động mong muốn...", key="nls_nd", height=70)
                
                c_space, c_btn_add = st.columns([3, 1])
                with c_btn_add:
                    st.button("➕ Thêm vào danh sách", type="primary", on_click=add_nls_item, use_container_width=True)
                
                # Hiển thị danh sách NLS đã thêm
                if st.session_state.nls_list:
                    st.markdown("---")
                    for i, item in enumerate(st.session_state.nls_list):
                        with st.container(border=True):
                            c_item_info, c_item_del = st.columns([11, 1])
                            with c_item_info:
                                st.markdown(f"**{item['thanh_phan']}** (Mức độ: `{item['muc_do']}`)")
                                st.write(f"👉 *{item['noi_dung']}*")
                            with c_item_del:
                                if st.button("❌", key=f"del_nls_{i}", help="Xóa yêu cầu này"):
                                    st.session_state.nls_list.pop(i)
                                    st.rerun()

    # =======================================================
    # 5. TÙY CHỌN NGÔN NGỮ & NÚT KÍCH HOẠT CHÍNH
    # =======================================================
    st.write("")
    with st.container(border=True):
        st.checkbox("Giáo án viết bằng ngôn ngữ Tiếng Anh")

    st.write("")
    if st.button("⚡ KÍCH HOẠT XỬ LÝ AI", type="primary", use_container_width=True):
        st.success(f"Hệ thống AI đang bắt đầu xử lý chế độ: **{'Chỉnh sửa giáo án' if st.session_state.soan_mode == 'chinh_sua' else 'Soạn tự động'}**!")
