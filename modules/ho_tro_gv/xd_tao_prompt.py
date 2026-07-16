import streamlit as st
import sys
from pathlib import Path

def render_xd_tao_prompt(ai_engine):
    st.markdown("### 🧙‍♂️ Chuyên gia Thiết kế Câu lệnh (Prompt Engineering)")
    st.info("💡 Tính năng này giúp thầy cô chuyển đổi ý tưởng thô thành một câu lệnh (Prompt) chuẩn mực, tối ưu hóa để sử dụng trên bất kỳ nền tảng AI nào (ChatGPT, Claude, Gemini...).")

    # 1. BẢNG ĐIỀU KHIỂN
    c1, c2 = st.columns([1, 1])
    vai_tro = c1.selectbox("Bạn muốn AI đóng vai trò gì?", [
        "Chuyên gia Giáo dục & Thiết kế Sư phạm",
        "Chuyên gia Tích hợp Công nghệ & AI (STEM/IoT)",
        "Người thiết kế Trò chơi & Hoạt động tương tác",
        "Cố vấn Tâm lý học đường",
        "Nhà ngôn ngữ học / Chuyên gia viết lách"
    ])

    muc_tieu = c2.selectbox("Mục tiêu chính của câu lệnh", [
        "Lên ý tưởng / Sáng tạo nội dung bài giảng",
        "Viết kịch bản / Lập kế hoạch chi tiết",
        "Đơn giản hóa / Trực quan hóa kiến thức phức tạp",
        "Tạo ngân hàng câu hỏi / Bài tập vận dụng",
        "Giải quyết tình huống sư phạm cụ thể"
    ])

    doi_tuong = st.text_input("Đối tượng tiếp nhận (Học sinh/Phụ huynh/Đồng nghiệp)", value="Học sinh cấp THCS", placeholder="VD: Học sinh lớp 9, Phụ huynh học sinh, Ban giám hiệu...")
    
    yeu_cau = st.text_area(
        "Nội dung/Ý tưởng thô thầy cô muốn AI làm", 
        placeholder="Ví dụ: Tôi muốn tạo một hoạt động nhóm cho môn Khoa học, lồng ghép kiến thức về cảm biến và vi điều khiển để giảm lãng phí điện năng, các em sẽ trình bày bằng sơ đồ tư duy...",
        height=120
    )

    # 2. XỬ LÝ LOGIC
    st.write("")
    c_btn1, c_btn2 = st.columns([3, 1])
    
    if c_btn1.button("🚀 TỐI ƯU HÓA CÂU LỆNH (GENERATE PROMPT)", type="primary", use_container_width=True):
        if not yeu_cau.strip():
            st.error("⚠️ Thầy cô vui lòng nhập một chút ý tưởng thô vào ô 'Nội dung' nhé!")
        else:
            with st.spinner("⏳ AI đang cấu trúc lại ngôn ngữ và thiết kế Prompt chuyên nghiệp..."):
                prompt = f"""
                Bạn là một Kỹ sư Câu lệnh (Prompt Engineer) hàng đầu thế giới. Nhiệm vụ của bạn là giúp một giáo viên tạo ra một Prompt cực kỳ xuất sắc để họ có thể copy và dán vào ChatGPT/Claude/Gemini nhằm đạt được kết quả tốt nhất.

                THÔNG TIN Ý TƯỞNG TỪ GIÁO VIÊN:
                - Vai trò mong muốn AI đảm nhận: {vai_tro}
                - Mục tiêu cốt lõi: {muc_tieu}
                - Đối tượng hướng tới: {doi_tuong}
                - Ý tưởng thô/Yêu cầu: {yeu_cau}

                YÊU CẦU TRẢ VỀ:
                Hãy viết MỘT PROMPT HOÀN CHỈNH (bằng tiếng Việt) bao gồm đầy đủ các thành tố của một siêu câu lệnh (Mega-Prompt) theo cấu trúc:
                1. [BỐI CẢNH & VAI TRÒ]
                2. [NHIỆM VỤ CỤ THỂ]
                3. [RÀNG BUỘC & TIÊU CHÍ CHẤT LƯỢNG]
                4. [ĐỐI TƯỢNG MỤC TIÊU]
                5. [ĐỊNH DẠNG ĐẦU RA] (Bảng, Markdown, List...)

                Lưu ý: 
                - KHÔNG cần giải thích hay chào hỏi. Chỉ in ra nội dung của Prompt để người dùng có thể copy ngay.
                - Sử dụng văn phong rành mạch, ra lệnh rõ ràng, chia đoạn tốt bằng Markdown.
                - Đặt toàn bộ nội dung Prompt vừa tạo vào trong một khối trích dẫn hoặc format sao cho dễ nhìn nhất.
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['prompt_content'] = content
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    if c_btn2.button("🗑️ Xóa làm lại", use_container_width=True):
        st.session_state.pop('prompt_content', None)
        st.rerun()

    # 3. HIỂN THỊ KẾT QUẢ VÀ TÍNH NĂNG COPY NHANH
    if st.session_state.get('prompt_content'):
        st.markdown("---")
        st.success("🎉 **Đây là câu lệnh (Prompt) đã được tối ưu hóa. Thầy cô có thể nhấn nút Copy ở góc phải hộp dưới đây để sử dụng ngay!**")
        
        # Sử dụng st.code để Streamlit tự động tạo nút "Copy to clipboard" cực kỳ tiện lợi
        st.code(st.session_state['prompt_content'], language="markdown")
        
        try:
            # Lazy Import cho tính năng tải Word (dự phòng nếu GV muốn lưu lại)
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = {"title": "Prompt_Tu_Dong"}
            data_export["ai_generated_content"] = st.session_state['prompt_content']
            data_export["is_rubric"] = True # Dùng chung template tài liệu cơ bản
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 LƯU LẠI PROMPT (FILE WORD)", 
                data=word_bytes, 
                file_name="Prompt_Toi_Uu.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")
