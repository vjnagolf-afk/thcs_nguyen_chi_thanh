import streamlit as st
import sys
from pathlib import Path

def render_xd_chu_nhiem(ai_engine):
    st.markdown("### 👨‍🏫 Trợ lý Công tác Giáo viên Chủ nhiệm")

    # 1. BẢNG ĐIỀU KHIỂN CHÍNH
    c1, c2 = st.columns([3, 2])
    loai_cong_tac = c1.selectbox("Chọn công việc cần AI hỗ trợ:", [
        "Viết nhận xét học bạ / Sổ liên lạc", 
        "Xây dựng kịch bản họp Phụ huynh", 
        "Lên kế hoạch tiết sinh hoạt lớp", 
        "Tư vấn giải quyết tình huống sư phạm",
        "Viết thư ngỏ / Thông báo gửi Phụ huynh"
    ])
    giong_dieu = c2.selectbox("Văn phong / Giọng điệu:", [
        "Chuẩn mực, chuyên nghiệp",
        "Gần gũi, thấu cảm, động viên",
        "Nghiêm khắc, định hướng rõ ràng",
        "Khích lệ, truyền cảm hứng"
    ])

    st.markdown("---")
    
    # 2. KHU VỰC NHẬP LIỆU ĐỘNG (Thay đổi theo công việc)
    context = ""
    prompt_task = ""
    
    if loai_cong_tac == "Viết nhận xét học bạ / Sổ liên lạc":
        st.info("💡 Điền từ khóa ưu/nhược điểm, AI sẽ sinh ra các mẫu nhận xét mượt mà, chuẩn mực sư phạm.")
        col_hs1, col_hs2 = st.columns(2)
        ten_hs = col_hs1.text_input("Tên học sinh (Tùy chọn)")
        hoc_luc = col_hs2.selectbox("Mức độ Đạt / Năng lực", ["Tốt", "Khá", "Đạt", "Chưa đạt", "Có cố gắng nhưng cần nỗ lực thêm"])
        
        uu_diem = st.text_input("Ưu điểm nổi bật (Từ khóa)", placeholder="VD: Nhiệt tình, có năng khiếu vẽ, chữ đẹp, hăng hái...")
        han_che = st.text_input("Hạn chế cần khắc phục (Từ khóa)", placeholder="VD: Còn trầm, đôi khi chưa tập trung, ẩu môn Toán...")
        
        context = f"Học sinh: {ten_hs}\nMức độ: {hoc_luc}\nƯu điểm: {uu_diem}\nHạn chế: {han_che}"
        prompt_task = "Viết 5 mẫu nhận xét học bạ/sổ liên lạc khác nhau (từ ngắn gọn đến chi tiết) dành cho học sinh này. Lời lẽ cần khéo léo, mang tính xây dựng."
        
    elif loai_cong_tac == "Xây dựng kịch bản họp Phụ huynh":
        chu_de_hop = st.text_input("Chủ đề cuộc họp", placeholder="VD: Họp đầu năm học, Họp sơ kết HK1, Họp phổ biến ôn thi lớp 9...")
        thong_tin_lop = st.text_area("Tình hình chung của lớp", placeholder="VD: Sĩ số 45, các con ngoan, đoàn kết nhưng môn Toán còn yếu, hay nói chuyện riêng...")
        muc_tieu = st.text_area("Thông điệp/Mục tiêu muốn truyền tải", placeholder="VD: Mong phụ huynh phối hợp quản lý việc dùng điện thoại ở nhà, đôn đốc ôn thi...")
        
        context = f"Chủ đề họp: {chu_de_hop}\nTình hình lớp: {thong_tin_lop}\nThông điệp trọng tâm: {muc_tieu}"
        prompt_task = "Viết kịch bản chi tiết cho buổi họp phụ huynh, bao gồm: Lời chào mở đầu, Báo cáo tình hình, Phân tích vấn đề trọng tâm, Kêu gọi sự phối hợp từ gia đình, và Lời kết."
        
    elif loai_cong_tac == "Lên kế hoạch tiết sinh hoạt lớp":
        c_th, c_cd = st.columns(2)
        thoi_gian = c_th.text_input("Thời gian / Tuần thứ", placeholder="VD: Tuần 5, Tháng 10...")
        chu_diem = c_cd.text_input("Chủ điểm (Nếu có)", placeholder="VD: Tôn sư trọng đạo, Thanh niên với văn hóa giao thông...")
        noi_dung_chinh = st.text_area("Các nội dung/hoạt động chính dự kiến", placeholder="VD: Sơ kết thi đua tuần, phân công trực nhật, tổ chức trò chơi đố vui nhỏ...")
        
        context = f"Thời gian: {thoi_gian}\nChủ điểm: {chu_diem}\nHoạt động chính: {noi_dung_chinh}"
        prompt_task = "Lập kế hoạch chi tiết cho tiết sinh hoạt lớp (45 phút), bao gồm mục tiêu, chuẩn bị, và tiến trình các hoạt động (Khởi động, Sơ kết tuần, Sinh hoạt chủ điểm, Tổng kết/Giao việc)."
        
    else: # Tình huống sư phạm hoặc Thư ngỏ
        mo_ta_tinh_huong = st.text_area("Mô tả tình huống / Nội dung cần thông báo", placeholder="VD: Hai học sinh xích mích trong giờ ra chơi vì hiểu lầm trên mạng xã hội...", height=150)
        
        context = f"Nội dung/Tình huống: {mo_ta_tinh_huong}"
        if loai_cong_tac == "Tư vấn giải quyết tình huống sư phạm":
            prompt_task = "Phân tích tâm lý học sinh trong tình huống này và đề xuất 3 hướng xử lý thấu tình đạt lý, phân tích ưu nhược điểm của từng hướng để giáo viên chủ nhiệm lựa chọn."
        else:
            prompt_task = "Soạn thảo một bức thư ngỏ / thông báo chính thức gửi đến phụ huynh học sinh về vấn đề trên. Ngôn từ cần trang trọng, lịch sự và rõ ý."

    # 3. NÚT XỬ LÝ LOGIC
    st.write("")
    c_btn1, c_btn2 = st.columns([3, 1])
    if c_btn1.button("🚀 YÊU CẦU AI THỰC HIỆN", type="primary", use_container_width=True):
        if not context.strip() or len(context) < 15:
            st.warning("⚠️ Thầy cô vui lòng nhập thêm một chút thông tin/từ khóa để AI hiểu rõ ngữ cảnh hơn nhé!")
        else:
            with st.spinner("⏳ AI đang phân tích tâm lý giáo dục và biên soạn nội dung..."):
                prompt = f"""
                Bạn là một giáo viên chủ nhiệm tận tâm, xuất sắc và giàu kinh nghiệm sư phạm tại Việt Nam.
                Nhiệm vụ của bạn là: {prompt_task}
                
                THÔNG TIN CHI TIẾT TỪ GIÁO VIÊN:
                {context}
                
                YÊU CẦU:
                - Văn phong/Giọng điệu: {giong_dieu}.
                - Trình bày mạch lạc, sử dụng Markdown, chia đoạn rõ ràng. 
                - In đậm các ý chính hoặc tiêu đề. Dùng gạch đầu dòng cho các liệt kê.
                - Tính thực tiễn cao, có thể áp dụng trực tiếp vào môi trường học đường thực tế ở Việt Nam.
                """
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['chunhiem_content'] = content
                    st.session_state['chunhiem_meta'] = {"title": loai_cong_tac.replace("/", "_").replace(" ", "_")}
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")
                    
    if c_btn2.button("🗑️ Làm lại", use_container_width=True):
        st.session_state.pop('chunhiem_content', None)
        st.session_state.pop('chunhiem_meta', None)
        st.rerun()

    # 4. KHU VỰC KẾT QUẢ VÀ TẢI VỀ
    if st.session_state.get('chunhiem_content'):
        st.markdown("---")
        st.markdown(st.session_state['chunhiem_content'])
        
        try:
            # Lazy Import 
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = st.session_state['chunhiem_meta'].copy()
            data_export["ai_generated_content"] = st.session_state['chunhiem_content']
            data_export["is_rubric"] = True # Mượn cờ này để dùng template Word đơn giản không có bảng biểu phức tạp
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 TẢI FILE KẾT QUẢ (WORD)", 
                data=word_bytes, 
                file_name=f"CongTacChuNhiem_{st.session_state['chunhiem_meta']['title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")
