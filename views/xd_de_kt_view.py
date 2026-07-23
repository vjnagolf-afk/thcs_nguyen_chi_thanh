# -*- coding: utf-8 -*-
"""
============================================================
VIEW: GIAO DIỆN XÂY DỰNG ĐỀ KIỂM TRA & MA TRẬN
FILE: views/xd_de_kt_view.py
============================================================
"""

import streamlit as st

try:
    from views.xd_de_kt_data import init_session_state_de_kt, generate_de_kt_ai, build_prompt_de_kt
except ImportError:
    def init_session_state_de_kt(): pass
    def generate_de_kt_ai(c, p, m="3.5 Flash"): return ""
    def build_prompt_de_kt(t, m, n): return ""

def render_xd_de_kt(ai_engine=None):
    """
    Khớp chính xác tham số truyền vào từ app.py
    """
    init_session_state_de_kt()

    st.title("📝 XÂY DỰNG ĐỀ KIỂM TRA & MA TRẬN (CHUẨN GDPT 2018)")
    
    st.subheader("🎛️ Thông tin chung")
    col1, col2, col3 = st.columns(3)
    with col1:
        khoi = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], key="de_kt_khoi")
    with col2:
        mon = st.selectbox("Môn học", ["Toán", "Ngữ văn", "Tiếng Anh", "Khoa học tự nhiên", "Vật lí", "Hóa học", "Sinh học", "Lịch sử và Địa lí", "Tin học", "Công nghệ"], key="de_kt_mon")
    with col3:
        hinh_thuc = st.selectbox("Hình thức", ["15 phút", "Giữa kỳ", "Cuối kỳ"], key="de_kt_hinh_thuc")

    st.subheader("⚙️ Cấu trúc đề & Tỷ lệ điểm")
    c_t1, c_t2, c_t3 = st.columns(3)
    with c_t1: pt_nhan_biet = st.number_input("Tỷ lệ Nhận biết (%)", value=40, step=5, key="de_nb")
    with c_t2: pt_thong_hieu = st.number_input("Tỷ lệ Thông hiểu (%)", value=30, step=5, key="de_th")
    with c_t3: pt_van_dung = st.number_input("Tỷ lệ Vận dụng (%)", value=30, step=5, key="de_vd")

    noi_dung_on = st.text_area("Nội dung / Chủ đề cần kiểm tra", placeholder="Nhập các bài học hoặc nội dung trọng tâm...", key="de_kt_noidung")

    st.divider()
    if st.button("⚡ TẠO ĐỀ KIỂM TRA & MA TRẬN", type="primary", use_container_width=True):
        if ai_engine is None:
            st.error("❌ Chưa cấu hình AI Engine.")
        elif not noi_dung_on.strip():
            st.warning("⚠️ Vui lòng nhập nội dung ôn tập/kiểm tra.")
        else:
            with st.spinner("⏳ Trợ lý AI đang biên soạn ma trận, đặc tả và đề kiểm tra..."):
                try:
                    thong_tin = f"- Khối: {khoi}\n- Môn: {mon}\n- Hình thức: {hinh_thuc}"
                    ma_trận = f"- Nhận biết: {pt_nhan_biet}%\n- Thông hiểu: {pt_thong_hieu}%\n- Vận dụng: {pt_van_dung}%"
                    
                    prompt = build_prompt_de_kt(thong_tin, ma_trận, noi_dung_on)
                    result = generate_de_kt_ai(ai_engine, prompt)
                    
                    st.session_state['de_kt_result'] = result
                    st.success("🎉 Đã tạo đề kiểm tra thành công!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Lỗi hệ thống: {e}")

    ket_qua = st.session_state.get("de_kt_result")
    if ket_qua:
        st.subheader("📄 Kết quả Đề kiểm tra & Ma trận")
        st.markdown(ket_qua)
