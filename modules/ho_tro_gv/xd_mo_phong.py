# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_gv/xd_mo_phong.py
Nhiệm vụ: Trợ lý Mô phỏng & Phòng Thí nghiệm Ảo.
ĐÃ FIX LỖI: Sửa hàm strip5 thành strip().
============================================================
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word của dự án
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2 để dùng Smart Router
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

def render_xd_mo_phong(ai_engine_cu=None):
    if "sim_result" not in st.session_state:
        st.session_state["sim_result"] = None
    if "sim_topic" not in st.session_state:
        st.session_state["sim_topic"] = "Kich_Ban_Mo_Phong"

    st.markdown("### 🧬 Trợ lý Mô phỏng & Phòng Thí nghiệm Ảo")
    st.info("💡 **Góc chuyên gia:** Hệ thống chia làm 2 phân vùng: Kho nguyên liệu thí nghiệm ảo trực tuyến (PhET, MozaWeb) và Trợ lý AI chuyên thiết kế kịch bản mô phỏng đa chiều (An toàn, Không gian/Thời gian, Trực quan hóa và Cá nhân hóa).")

    # TẠO 2 TAB PHÂN BIỆT RÕ RÀNG 2 NHÓM CHỨC NĂNG
    tab1, tab2 = st.tabs([
        "🌐 Nhóm 1: Kho Thí nghiệm Ảo (PhET & MozaWeb 3D)", 
        "🤖 Nhóm 2: Trợ lý AI Thiết kế Kịch bản Mô phỏng"
    ])

    # ========================================================
    # NHÓM 1: MÃ NHÚNG THÍ NGHIỆM ẢO PHET & MOZAWEB
    # ========================================================
    with tab1:
        st.markdown("#### 🧪 Kho Nguyên liệu & Phòng Thí nghiệm Ảo Trực tuyến")
        st.caption("Thầy/Cô có thể nhúng trực tiếp hoặc truy cập nhanh các nền tảng thí nghiệm ảo hàng đầu thế giới.")

        col_phet, col_moza = st.columns(2)

        with col_phet:
            with st.container(border=True):
                st.markdown("##### 🔬 PhET Interactive Simulations (University of Colorado)")
                st.markdown("Hơn 150 mô phỏng tương tác miễn phí về Vật lý, Hóa học, Sinh học, Toán học và Khoa học Trái Đất.")
                st.markdown("[🔗 Truy cập trang chủ PhET](https://phet.colorado.edu/)", unsafe_allow_html=True)
                
                if st.checkbox("💻 Nhúng trực tiếp PhET vào ứng dụng", value=False, key="embed_phet"):
                    st.components.v1.iframe("https://phet.colorado.edu/sims/html/density/latest/density_en.html", height=450, scrolling=True)

        with col_moza:
            with st.container(border=True):
                st.markdown("##### 🏛️ MozaWeb 3D & Khám phá Không gian ảo")
                st.markdown("Thư viện cảnh quay 3D, video giáo dục, hình ảnh trực quan sinh động cho mọi môn học.")
                moza_link = "https://mozaweb.vn/vi/lexikon.php?cmd=getlist&let=3D&active_menu=3d"
                st.markdown(f"[🔗 Truy cập Thư viện MozaWeb 3D]({moza_link})", unsafe_allow_html=True)
                
                if st.checkbox("💻 Nhúng trực tiếp MozaWeb 3D", value=False, key="embed_moza"):
                    st.components.v1.iframe(moza_link, height=450, scrolling=True)

    # ========================================================
    # NHÓM 2: TRỢ LÝ AI THIẾT KẾ KỊCH BẢN MÔ PHỎNG
    # ========================================================
    with tab2:
        st.markdown("#### 🎯 Thiết kế Kịch bản Mô phỏng & Tương tác Thông minh")
        
        with st.container(border=True):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                mon_hoc = st.text_input("Môn học:", placeholder="VD: Hóa học 9, Vật lý 10, Lịch sử 8...")
                chu_de = st.text_input("Chủ đề / Tên bài học:", placeholder="VD: Phản ứng hóa học, Cấu trúc tế bào, Trận Điện Biên Phủ...")
            with col_s2:
                nhom_tinh_nang = st.selectbox(
                    "Chọn trọng tâm mô phỏng:",
                    [
                        "🔬 Thí nghiệm & Thực hành An toàn (Hóa/Lý/Sinh không cháy nổ, thử nghiệm sai số, rủi ro cao)",
                        "🌍 Tương tác Không gian & Thời gian (Du hành thời gian, thay đổi quy mô, VR Field Trips, mô phỏng thời tiết)",
                        "📊 Thao tác Trực quan & Quản lý lớp học (Mô hình 3D, Dashboard theo dõi, Tùy chỉnh kịch bản, Chấm điểm tự động)",
                        "🤝 Tăng cường Tương tác & Cá nhân hóa (Không gian cộng tác nhóm, Gamification, Hỗ trợ học sinh đặc biệt)"
                    ]
                )
                do_tuoi = st.selectbox("Khối lớp / Đối tượng học sinh:", ["Lớp 6 - 7", "Lớp 8 - 9", "Lớp 10 - 12"])

            yeu_cau_chi_tiet = st.text_area("Yêu cầu cụ thể của giáo viên (Tuỳ chọn):", height=80, placeholder="VD: Cần thiết kế kịch bản cho phép học sinh thử sai 3 lần khi pha chế axit đặc...")
            
            btn_tao_sim = st.button("🚀 XÂY DỰNG KỊCH BẢN MÔ PHỎNG CHI TIẾT", type="primary", use_container_width=True)

        if btn_tao_sim:
            if AIEngine2 is None:
                st.error("❌ Không tìm thấy file `utils/ai_engine_2.py`. Vui lòng kiểm tra lại cấu trúc dự án.")
                return

            if not chu_de.strip() or not mon_hoc.strip():
                st.warning("⚠️ Vui lòng nhập đầy đủ Môn học và Chủ đề bài học.")
            else:
                with st.spinner("⏳ AI đang lập chiến lược mô phỏng, tích hợp các công nghệ ảo hóa tiên tiến..."):
                    
                    # Đã fix lỗi strip5 thành strip() ở đây
                    yeu_cau_str = yeu_cau_chi_tiet.strip() if yeu_cau_chi_tiet else 'Không có'

                    prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA CÔNG TRÌNH GIÁO DỤC (EDTECH EXPERT) VÀ KIẾN TRÚC SƯ THỰC TẾ ẢO (VR/AR/SIMULATION).
Nhiệm vụ của bạn là thiết kế một Kịch bản Mô phỏng Giảng dạy hoàn chỉnh dựa trên các tiêu chí chuyên sâu.

--- THÔNG TIN CƠ BẢN ---
- Môn học: {mon_hoc}
- Chủ đề: {chu_de}
- Đối tượng: {do_tuoi}
- Trọng tâm mô phỏng được chọn: {nhom_tinh_nang}
- Yêu cầu riêng từ Giáo viên: {yeu_cau_str}

--- CẤU TRÚC KỊCH BẢN MÔ PHỎNG BẮT BUỘC ---

# 1. TỔNG QUAN & MỤC TIÊU HỌC TẬP TRỰC QUAN
(Xác định rõ học sinh đạt được kiến thức và kỹ năng gì thông qua mô phỏng này).

# 2. THIẾT LẬP MÔI TRƯỜNG & CÔNG CỤ ẢO
- **Loại hình mô phỏng:** (Ví dụ: Phòng lab hóa học an toàn, Không gian 3D, Bản đồ thời gian tương tác...).
- **Giải pháp thay thế chi phí/rủi ro:** (Khắc phục hạn chế thực tế như thế nào bằng kỹ thuật số).
- **Cơ chế thử nghiệm sai số:** (Cho phép học sinh thử lại, nhận cảnh báo lỗi ở bước nào).

# 3. KỊCH BẢN HOẠT ĐỘNG CHI TIẾT (STEP-BY-STEP)
- **Bước 1 (Khởi động / Phá băng):** ...
- **Bước 2 (Thực hành / Tương tác trực quan):** ...
- **Bước 3 (Thử thách & Xử lý tình huống rủi ro cao / Thay đổi biến số):** ...

# 4. QUẢN LÝ LỚP HỌC & ĐÁNH GIÁ TỰ ĐỘNG
- **Bảng điều khiển (Dashboard) của Giáo viên:** Theo dõi tiến độ thời gian thực ra sao.
- **Tiêu chí chấm điểm tự động:** Hệ thống ghi nhận kết quả dựa trên thông số nào.
- **Cá nhân hóa & Hỗ trợ học sinh đặc biệt:** Điều chỉnh tốc độ, phân loại nhiệm vụ cho học sinh yếu/giỏi.

# 5. TƯƠNG TÁC XÃ HỘI & GAMIFICATION
- **Không gian cộng tác nhóm từ xa:** Phân vai trò cho các thành viên trong nhóm ảo thế nào.
- **Yếu tố trò chơi hóa (Gamification):** Hệ thống điểm thưởng, huy hiệu khám phá.

[KỶ LUẬT ĐỊNH DẠNG]
- Trình bày rõ ràng bằng Markdown (Tiêu đề, danh sách, in đậm).
- NẾU có công thức Toán/Lý/Hóa, BẮT BUỘC bọc trong dấu `$ ... $`. Cấm dùng backtick (`).
"""
                    try:
                        engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                        result = engine_v2.generate_text(prompt, temperature=0.7)
                        
                        if result.startswith("❌") or result.startswith("⚠️"):
                            st.error(result)
                        else:
                            st.session_state["sim_result"] = result
                            st.session_state["sim_topic"] = chu_de.replace(" ", "_")
                    except Exception as e:
                        st.error(f"❌ Lỗi hệ thống: {e}")

        # Hiển thị kết quả và nút xuất Word
        if st.session_state.get("sim_result"):
            st.markdown("---")
            st.markdown("### 📑 KẾT QUẢ KỊCH BẢN MÔ PHỎNG")
            st.markdown(st.session_state["sim_result"], unsafe_allow_html=True)
            
            st.markdown("### 📥 Lưu trữ tài liệu")
            if export_word is None:
                st.warning("⚠️ Module Word chưa sẵn sàng.")
            else:
                try:
                    export_data = {
                        "ai_generated_content": st.session_state["sim_result"],
                        "is_dkt": False
                    }
                    with st.spinner("Đang kết xuất file Word chuẩn..."):
                        word_bytes = export_word(export_data)
                    
                    safe_topic = st.session_state.get("sim_topic", "Mo_Phong")[:30]
                    st.download_button(
                        label="📥 TẢI XUỐNG KỊCH BẢN MÔ PHỎNG (.DOCX)",
                        data=word_bytes,
                        file_name=f"Kich_Ban_Mo_Phong_{safe_topic}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Lỗi xuất Word: {e}")
                    
            if st.button("🔄 Thiết kế kịch bản mô phỏng khác", use_container_width=True):
                st.session_state["sim_result"] = None
                st.rerun()
