# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/quan_ly_to/bien_ban.py
Nhiệm vụ: Trợ lý Thư ký - Xây dựng Biên bản Sinh hoạt.
Chức năng: AI tự động soạn thảo biên bản họp bám sát cấu trúc 
dự thảo kế hoạch (hỗ trợ nhập text hoặc tải file PDF) kèm cơ chế 
gỡ lỗi chi tiết (Traceback).
============================================================
"""

import streamlit as st
from pypdf import PdfReader
import traceback

def render_bien_ban(ai_engine=None):
    st.markdown("### 📝 Trợ lý Thư ký: Xây dựng Biên bản Sinh hoạt")
    st.caption("AI tự động soạn thảo biên bản họp bám sát cấu trúc dự thảo kế hoạch, hỗ trợ nhiều hình thức sinh hoạt chuyên môn khác nhau.")

    # Lấy danh sách GV từ bộ nhớ (nếu có) để làm menu chọn Chủ tọa/Thư ký
    ds_gv = st.session_state.get("danh_sach_gv", ["Chưa có dữ liệu (Hãy qua thẻ Danh sách)"])
    
    if "ket_qua_bien_ban" not in st.session_state:
        st.session_state.ket_qua_bien_ban = None

    # 1. KHU VỰC THÔNG TIN CUỘC HỌP
    with st.expander("📌 Bước 1: Thông tin cơ bản", expanded=True):
        h1_c1, h1_c2, h1_c3 = st.columns([2, 1.5, 1.5])
        with h1_c1:
            loai_cuoc_hop = st.selectbox("📌 Loại hình sinh hoạt:", [
                "Sinh hoạt chuyên môn định kỳ",
                "Nghiên cứu bài học (Bước 2, 3)",
                "Xây dựng chuyên đề / STEM",
                "Phân tích kết quả kiểm tra",
                "Thống nhất ma trận, đặc tả đề",
                "Hình thức khác..."
            ])
        with h1_c2:
            thoi_gian = st.text_input("⏰ Thời gian:", placeholder="VD: 14h00, 18/07/2026")
        with h1_c3:
            dia_diem = st.text_input("📍 Địa điểm:", placeholder="VD: Văn phòng Trường")

        h2_c1, h2_c2, h2_c3, h2_c4 = st.columns(4)
        with h2_c1:
            chu_toa = st.selectbox("👨‍🏫 Chủ tọa:", ds_gv, index=0)
        with h2_c2:
            index_thu_ky = 1 if len(ds_gv) > 1 else 0
            thu_ky = st.selectbox("✍️ Thư ký:", ds_gv, index=index_thu_ky)
        with h2_c3:
            co_mat = st.text_input("👥 Có mặt:", placeholder="VD: 10/10")
        with h2_c4:
            vang_mat = st.text_input("🚫 Vắng mặt:", placeholder="VD: 0 (hoặc ghi tên)")

    # 2. KHU VỰC NẠP DỰ THẢO
    st.markdown("#### 📄 Bước 2: Nạp Dự thảo kế hoạch / Dàn ý")
    st.info("💡 AI sẽ dò tìm các đề mục lớn (I, II, III...) và mục nhỏ (1, 2, a, b...) trong văn bản này để tạo khung biên bản tương ứng.")
    
    tab_nhap, tab_file = st.tabs(["✍️ Dán văn bản Dự thảo", "📂 Tải file PDF Dự thảo"])
    noidung_du_thao = ""
    
    with tab_nhap:
        text_input = st.text_area("Dán nội dung dự thảo vào đây:", height=150, placeholder="Ví dụ:\nI. Đánh giá công tác tuần qua\n1. Ưu điểm\n2. Tồn tại\nII. Triển khai công tác tuần tới...")
        if text_input:
            noidung_du_thao = text_input
            
    with tab_file:
        uploaded_file = st.file_uploader("Tải lên file dự thảo (PDF)", type=["pdf"])
        if uploaded_file:
            try:
                reader = PdfReader(uploaded_file)
                extracted_text = ""
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
                noidung_du_thao = extracted_text
                st.success("✅ Đã đọc thành công nội dung file PDF!")
            except Exception as e:
                st.error(f"Lỗi đọc file PDF: {e}")

    # 3. NÚT XỬ LÝ AI
    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        if st.button("🪄 Viết Biên bản bằng AI", type="primary", use_container_width=True):
            if not noidung_du_thao.strip():
                st.warning("⚠️ Thầy vui lòng cung cấp nội dung hoặc file Dự thảo trước nhé!")
            else:
                with st.spinner("🧠 Thư ký AI đang tổng hợp và soạn thảo biên bản..."):
                    prompt = f"""
                    BẠN LÀ THƯ KÝ TỔ CHUYÊN MÔN TRƯỜNG THCS. HÃY VIẾT MỘT "BIÊN BẢN CUỘC HỌP" CHI TIẾT, MANG VĂN PHONG HÀNH CHÍNH TRANG TRỌNG.
                    
                    THÔNG TIN CHUNG:
                    - Loại hình cuộc họp: {loai_cuoc_hop}
                    - Thời gian: {thoi_gian}
                    - Địa điểm: {dia_diem}
                    - Thành phần: Có mặt {co_mat}, Vắng mặt {vang_mat}
                    - Chủ tọa: {chu_toa}
                    - Thư ký: {thu_ky}
                    
                    NGUYÊN TẮC BẮT BUỘC:
                    Bên dưới là văn bản Dự thảo kế hoạch. Bạn PHẢI bám sát TUYỆT ĐỐI cấu trúc các đề mục của bản dự thảo này (Ví dụ: I, II, III... 1, 2, 3... a, b, c...). Không được tự ý bỏ sót bất kỳ mục nào.
                    
                    YÊU CẦU NỘI DUNG:
                    1. Mở đầu biên bản chuẩn thể thức hành chính, bao gồm đầy đủ Thông tin chung.
                    2. Tại mỗi đề mục, trình bày nội dung của Chủ tọa, sau đó TỰ ĐỘNG THÊM VÀO các ý kiến thảo luận giả định mang tính sư phạm của các thành viên.
                    3. Cuối mỗi mục lớn phải có kết luận chốt lại vấn đề của Chủ tọa.
                    4. Phần cuối biên bản là thời gian kết thúc và chữ ký.
                    
                    DỰ THẢO KẾ HOẠCH:
                    '''{noidung_du_thao}'''
                    """
                    
                    bien_ban = None
                    try:
                        # Thử quét tất cả các nguồn ai_engine có thể có
                        engine_to_use = ai_engine
                        if not engine_to_use and "ai_engine" in st.session_state:
                            engine_to_use = st.session_state.ai_engine

                        if engine_to_use and hasattr(engine_to_use, "generate_text"):
                            bien_ban = engine_to_use.generate_text(prompt)
                        
                        # Nếu vẫn chưa có, tự gọi trực tiếp OpenAI bằng mọi khóa có trong session_state hoặc secrets
                        if not bien_ban:
                            api_key = None
                            for k in ["user_api_key", "api_key", "openai_api_key", "sk_key"]:
                                if st.session_state.get(k):
                                    api_key = st.session_state.get(k)
                                    break
                            
                            if not api_key and "OPENAI_API_KEY" in st.secrets:
                                api_key = st.secrets["OPENAI_API_KEY"]

                            if api_key and str(api_key).startswith("sk-"):
                                from openai import OpenAI
                                client = OpenAI(api_key=str(api_key).strip())
                                response = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[{"role": "user", "content": prompt}]
                                )
                                bien_ban = response.choices[0].message.content

                        if bien_ban:
                            st.session_state.ket_qua_bien_ban = bien_ban
                            st.rerun()
                        else:
                            st.error("❌ Không thể gọi AI do không tìm thấy đối tượng `ai_engine` hợp lệ hoặc khóa API chưa được thiết lập chính xác.")
                    except Exception as e:
                        st.error(f"❌ Phát hiện lỗi chi tiết khi gọi AI:")
                        st.code(traceback.format_exc())

    with col_btn2:
        if st.button("🗑️ Xóa / Làm lại", type="secondary", use_container_width=True):
            st.session_state.ket_qua_bien_ban = None
            st.rerun()

    # 4. HIỂN THỊ KẾT QUẢ VÀ TẢI VỀ
    st.markdown("---")
    if st.session_state.ket_qua_bien_ban:
        st.success("🎉 Biên bản đã hoàn thành! Thầy có thể đọc, chỉnh sửa trực tiếp hoặc tải về máy.")
        
        st.download_button(
            label="⬇️ Tải Biên bản về máy (.txt)",
            data=st.session_state.ket_qua_bien_ban,
            file_name="Bien_Ban_SHCM.txt",
            mime="text/plain",
            type="primary"
        )
        
        st.markdown("#### 📜 Nội dung Biên bản")
        st.text_area("Chỉnh sửa biên bản (nếu cần):", value=st.session_state.ket_qua_bien_ban, height=600, label_visibility="collapsed")
