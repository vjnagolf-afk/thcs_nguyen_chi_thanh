# -*- coding: utf-8 -*-
import streamlit as st

def render_the_01(ai_engine=None):
    st.markdown("### 🎮 Công cụ Sinh Prompt & Nguyên mẫu Trò chơi Mô phỏng")
    st.caption("Hỗ trợ giáo viên thiết kế prompt chuyên sâu hoặc mã nguồn nguyên mẫu tương tác cho các môn học THCS.")

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown("#### ⚙️ Cấu hình thông số trò chơi")
        mon_hoc = st.selectbox("Môn học", ["Khoa học Tự nhiên", "Toán học", "Lịch sử & Địa lí", "Công nghệ", "Tin học", "Môn khác"], key="tg_mon")
        lop = st.selectbox("Khối lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"], index=2, key="tg_lop")
        chu_de = st.text_input("Tên chủ đề / Bài học", placeholder="Ví dụ: Định luật Ôm, Quang hợp, Hàm số bậc nhất...", key="tg_chude")
        
        phuong_phap = st.selectbox(
            "Phương pháp / Phong cách mô phỏng",
            [
                "Mô phỏng tổng quát (Thanh trượt, thay đổi thông số trực quan)",
                "Phòng thí nghiệm ảo chuyên biệt (Mạch điện, dụng cụ đo, đồ thị)",
                "Phương pháp KHKT: Dự đoán – Thí nghiệm – Quan sát – Giải thích – Kết luận"
            ],
            key="tg_pp"
        )

        dang_dau_ra = st.radio(
            "Hình thức đầu ra mong muốn",
            ["Prompt chuyên sâu cho AI", "Mã nguồn nguyên mẫu tương tác (HTML/JS)"],
            key="tg_output"
        )

        btn_tao = st.button("✨ TẠO PROMPT & KỊCH BẢN TRÒ CHƠI", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### 📋 Kết quả đầu ra")
        
        if btn_tao:
            if not chu_de.strip():
                st.warning("⚠️ Vui lòng nhập tên chủ đề hoặc bài học.")
            else:
                with st.spinner("🤖 Hệ thống AI đang tổng hợp và kiến tạo kịch bản trò chơi..."):
                    prompt_xay_dung = f"""
BẠN LÀ CHUYÊN GIA THIẾT KẾ GIÁO DỤC SỐ VÀ LẬP TRÌNH GAME MÔ PHỎNG (EDTECH).
NHIỆM VỤ: Hãy tạo ra một {"bản Prompt chuyên sâu" if "Prompt" in dang_dau_ra else "mã nguồn nguyên mẫu HTML/CSS/JavaScript hoàn chỉnh"} cho trò chơi mô phỏng giáo dục môn {mon_hoc} - {lop}.

THÔNG TIN CHI TIẾT:
- Chủ đề: {chu_de}
- Phong cách mô phỏng: {phuong_phap}
- Đối tượng học sinh: Học sinh THCS (11-15 tuổi).

YÊU CẦU THIẾT KẾ:
1. Tính khoa học và chính xác cao, bám sát chương trình GDPT 2018.
2. Có cơ chế tương tác thực tế (thanh trượt điều chỉnh thông số, nút bấm, tính toán công thức động).
3. Cấu trúc rõ ràng gồm: Màn hình bắt đầu, Mô phỏng tương tác, Thử thách/Nhiệm vụ học tập, Hệ thống tính điểm/phản hồi, và Tổng kết kiến thức.
4. Giao diện hiện đại, trực quan, phù hợp lứa tuổi THCS.

Hãy trình bày rõ ràng bằng tiếng Việt.
"""
                    if ai_engine:
                        try:
                            ket_qua_ai = ai_engine.generate_text(prompt_xay_dung)
                        except Exception as e:
                            ket_qua_ai = f"Lỗi gọi AI: {str(e)}"
                    else:
                        ket_qua_ai = f"""### MẪU PROMPT CHUYÊN SÂU CHO CHỦ ĐỀ: {chu_de} ({mon_hoc} - {lop})

Tạo một trò chơi mô phỏng giáo dục tương tác bằng tiếng Việt dành cho học sinh THCS về chủ đề: {chu_de}.

**Thiết kế mô phỏng:**
- Cho phép học sinh thay đổi các biến số thông qua thanh trượt (slider) và nút bấm trực quan.
- Các giá trị thay đổi theo quy luật khoa học chính xác của môn {mon_hoc}.
- Hiển thị kết quả đo lường và đồ thị trực quan (nếu có).

**Cấu trúc nhiệm vụ:**
1. Tình huống thực tế và câu hỏi dự đoán.
2. Khu vực thí nghiệm ảo cho học sinh thao tác.
3. Phản hồi tức thì (Đúng/Sai) kèm giải thích bản chất kiến thức.
4. Hệ thống chấm điểm, tích lũy huy hiệu và tổng kết kiến thức cần ghi nhớ.
"""

                    st.session_state["ung_dung_khac_ket_qua"] = ket_qua_ai
                    st.success("🎉 Đã tạo thành công kịch bản và prompt trò chơi!")

        if "ung_dung_khac_ket_qua" in st.session_state:
            st.text_area("Nội dung kết xuất:", value=st.session_state["ung_dung_khac_ket_qua"], height=350)
            st.download_button(
                "📥 Tải xuống kịch bản (.txt)",
                data=st.session_state["ung_dung_khac_ket_qua"],
                file_name=f"Prompt_TroChoi_{chu_de.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("💡 Vui lòng cấu hình thông số bên cột trái và bấm nút để hệ thống sinh nội dung.")
