import streamlit as st
import sys
from pathlib import Path

def render_xd_mo_phong(ai_engine):
    st.markdown("### 🔬 Kịch bản Mô phỏng & Thực hành")
    st.info("💡 Hỗ trợ giáo viên xây dựng kịch bản Thí nghiệm thực tế, Hướng dẫn dùng Thí nghiệm ảo (PhET, Olabs...) hoặc Kịch bản nhập vai (Roleplay).")

    # 1. BẢNG ĐIỀU KHIỂN
    c1, c2, c3 = st.columns([2, 1, 2])
    mon_hoc = c1.selectbox("Môn học (Thực hành)", [
        "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", 
        "Tin học", "Công nghệ", "Lịch sử", "Địa lý", "Ngữ văn", "Ngoại ngữ"
    ])
    lop = c2.selectbox("Lớp (Thực hành)", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2)
    loai_hinh = c3.selectbox("Loại hình thực hành", [
        "Thí nghiệm thực tế (Hands-on Lab)", 
        "Thí nghiệm ảo / Phần mềm (Virtual Lab)", 
        "Mô phỏng nhập vai / Tình huống (Roleplay)"
    ])

    st.write("")
    
    ten_bai = st.text_input("Tên bài thực hành / Mô phỏng", placeholder="Ví dụ: Quan sát tế bào biểu bì vảy hành, Khảo sát con lắc lò xo trên PhET, Hội nghị Diên Hồng...")
    
    yeu_cau_them = st.text_area(
        "Yêu cầu cụ thể (Tùy chọn)", 
        placeholder="VD: Cần có bảng mẫu báo cáo thu hoạch, nhấn mạnh quy tắc an toàn cháy nổ, tập trung vào kỹ năng sử dụng kính hiển vi..."
    )

    # 2. XỬ LÝ LOGIC
    st.write("")
    c_btn1, c_btn2 = st.columns([3, 1])
    
    # Bổ sung key="tao_mo_phong" và key="xoa_mo_phong" để chống lỗi trùng lặp nút bấm
    if c_btn1.button("🚀 XÂY DỰNG KỊCH BẢN THỰC HÀNH", key="tao_mo_phong", type="primary", use_container_width=True):
        if not ten_bai.strip():
            st.error("⚠️ Vui lòng nhập Tên bài thực hành / Mô phỏng!")
        else:
            with st.spinner("⏳ AI đang thiết kế các bước thao tác và mẫu báo cáo..."):
                
                # Cấu trúc prompt linh hoạt theo loại hình
                dk_loai_hinh = ""
                if "Thí nghiệm thực tế" in loai_hinh:
                    dk_loai_hinh = """
                    1. Mục tiêu (Kiến thức, Kỹ năng).
                    2. Chuẩn bị (Dụng cụ, hóa chất, vật liệu).
                    3. Lưu ý an toàn phòng thí nghiệm CỰC KỲ QUAN TRỌNG.
                    4. Các bước tiến hành (Chi tiết từng bước thao tác).
                    5. Hiện tượng quan sát được & Giải thích khoa học.
                    6. Mẫu phiếu báo cáo kết quả thực hành (dành cho học sinh điền).
                    """
                elif "Thí nghiệm ảo" in loai_hinh:
                    dk_loai_hinh = """
                    1. Mục tiêu thực hành.
                    2. Nền tảng đề xuất (Gợi ý dùng PhET Interactive Simulations, Olabs, Tinkercad... phù hợp với bài).
                    3. Hướng dẫn truy cập và các thông số cần cài đặt ban đầu trên phần mềm.
                    4. Các bước thao tác trên giao diện (Kéo thả gì, quan sát đồng hồ đo nào...).
                    5. Bảng ghi chép số liệu mô phỏng.
                    6. Câu hỏi phân tích dữ liệu rút ra từ mô phỏng.
                    """
                else:
                    dk_loai_hinh = """
                    1. Mục tiêu của hoạt động nhập vai (Giúp HS thấu cảm/hiểu sâu vấn đề gì).
                    2. Bối cảnh tình huống (Không gian, thời gian).
                    3. Hệ thống nhân vật và Đặc điểm/Nhiệm vụ của từng nhân vật.
                    4. Tiến trình hoạt động (Mở đầu, Đỉnh điểm, Tháo gỡ).
                    5. Câu hỏi định hướng thảo luận sau khi diễn xong.
                    6. Tiêu chí đánh giá diễn xuất/sự hiểu bài của các nhóm.
                    """

                prompt = f"""
                Bạn là một chuyên gia phương pháp giảng dạy, đặc biệt xuất sắc trong việc thiết kế các hoạt động thực hành, thí nghiệm và mô phỏng.
                Hãy soạn một kịch bản/giáo án thực hành chi tiết theo yêu cầu sau:

                THÔNG TIN:
                - Môn: {mon_hoc}, Cấp độ: {lop}
                - Tên bài/Chủ đề: {ten_bai}
                - Loại hình: {loai_hinh}
                - Yêu cầu thêm từ giáo viên: {yeu_cau_them}

                CẤU TRÚC BẮT BUỘC:
                {dk_loai_hinh}

                LƯU Ý KỸ THUẬT:
                - Sử dụng Markdown để trình bày. Kẻ bảng rõ ràng nếu có mẫu báo cáo.
                - Sử dụng LaTeX ($...$) cho các công thức hóa học/vật lý để hiển thị đẹp mắt.
                - Tuyệt đối KHÔNG dùng ký tự ">" ở đầu các dòng.
                - Trình bày sư phạm, dễ hiểu, học sinh có thể đọc và tự làm theo được.
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['mophong_content'] = content
                    st.session_state['mophong_meta'] = {
                        "title": ten_bai.replace(" ", "_"),
                        "mon": mon_hoc
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    if c_btn2.button("🗑️ Xóa làm lại", key="xoa_mo_phong", use_container_width=True):
        st.session_state.pop('mophong_content', None)
        st.session_state.pop('mophong_meta', None)
        st.rerun()

    # 3. HIỂN THỊ KẾT QUẢ VÀ TẢI VỀ
    if st.session_state.get('mophong_content'):
        st.markdown("---")
        st.markdown(st.session_state['mophong_content'])
        
        try:
            # Lazy Import
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = {"title": st.session_state['mophong_meta']['title']}
            data_export["ai_generated_content"] = st.session_state['mophong_content']
            data_export["is_rubric"] = True # Mượn template có hỗ trợ bảng biểu
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 TẢI KỊCH BẢN THỰC HÀNH (WORD)", 
                data=word_bytes, 
                file_name=f"MoPhong_ThucHanh_{st.session_state['mophong_meta']['title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")
