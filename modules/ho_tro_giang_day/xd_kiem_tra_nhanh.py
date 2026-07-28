# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_kiem_tra_nhanh.py
Nhiệm vụ: Trợ lý Tạo Bài Kiểm tra Nhanh Tương tác (Interactive Quiz).
Chức năng: AI tạo bộ câu hỏi trắc nghiệm JSON, hệ thống render giao diện làm bài, chấm điểm và giải thích tự động.
============================================================
"""

import json
import re
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Bắt buộc import AIEngine2
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

def clean_json_response(text):
    """Hàm dọn dẹp chuỗi trả về từ AI để bóc tách đúng phần JSON"""
    try:
        # Tìm phần bọc trong ngoặc vuông (mảng JSON)
        match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        # Nếu không có ngoặc vuông bọc ngoài, thử parse toàn bộ
        return json.loads(text)
    except Exception as e:
        logger.error(f"Lỗi parse JSON: {e}")
        return None

def render_xd_kiem_tra_nhanh(ai_engine_cu=None):
    # Khởi tạo bộ nhớ state cho bài kiểm tra
    if "ktn_quiz_data" not in st.session_state:
        st.session_state["ktn_quiz_data"] = None
    if "ktn_submitted" not in st.session_state:
        st.session_state["ktn_submitted"] = False
    if "ktn_score" not in st.session_state:
        st.session_state["ktn_score"] = 0

    st.markdown("### ⏱️ Bài Kiểm tra Nhanh Tương tác (Interactive Quiz)")
    st.info("💡 **Góc chuyên gia:** Tạo nhanh một bài trắc nghiệm ngay trên lớp để học sinh làm trực tiếp trên màn hình/máy tính bảng. Hệ thống tự động chấm điểm và đưa ra giải thích chi tiết.")

    # ========================================================
    # KHU VỰC 1: CẤU HÌNH BÀI KIỂM TRA
    # ========================================================
    with st.expander("⚙️ BẢNG ĐIỀU KHIỂN & TẠO ĐỀ (Dành cho Giáo viên)", expanded=(st.session_state["ktn_quiz_data"] is None)):
        col_cfg1, col_cfg2 = st.columns([2, 1])
        with col_cfg1:
            chu_de = st.text_input("Chủ đề bài kiểm tra:", placeholder="VD: Hiện tượng khúc xạ ánh sáng, Thì hiện tại hoàn thành, Lịch sử nhà Trần...")
            noi_dung_tham_khao = st.text_area("Văn bản tham khảo (Tuỳ chọn):", height=60, placeholder="Dán một đoạn văn bản ngắn vào đây nếu muốn AI ra đề bám sát văn bản này...")
        
        with col_cfg2:
            so_luong = st.number_input("Số câu hỏi:", min_value=3, max_value=20, value=5, step=1)
            muc_do = st.selectbox("Mức độ khó:", ["Nhận biết (Dễ)", "Thông hiểu (Vừa)", "Vận dụng (Khó)", "Hỗn hợp"])
            doi_tuong = st.selectbox("Cấp học:", ["Tiểu học", "THCS", "THPT"])

        if st.button("🚀 TẠO BÀI KIỂM TRA MỚI", type="primary", use_container_width=True):
            if not chu_de.strip() and not noi_dung_tham_khao.strip():
                st.warning("⚠️ Vui lòng nhập chủ đề hoặc nội dung tham khảo.")
            else:
                if AIEngine2 is None:
                    st.error("❌ Không tìm thấy hệ thống AIEngine2.")
                else:
                    with st.spinner("⏳ AI đang biên soạn và đóng gói dữ liệu câu hỏi (JSON)..."):
                        prompt = f"""
BẠN LÀ MỘT GIÁO VIÊN BIÊN SOẠN CÂU HỎI TRẮC NGHIỆM CHUYÊN NGHIỆP.
Hãy tạo {so_luong} câu hỏi trắc nghiệm (4 lựa chọn) về chủ đề: "{chu_de}".
Mức độ: {muc_do}. Phù hợp với đối tượng học sinh: {doi_tuong}.
Văn bản tham khảo (nếu có): {noi_dung_tham_khao}

[KỶ LUẬT ĐẦU RA BẮT BUỘC]
Bạn CHỈ ĐƯỢC PHÉP trả về kết quả dưới định dạng MẢNG JSON (JSON Array). KHÔNG ĐƯỢC thêm bất kỳ lời chào, giải thích, hay ký tự nào bên ngoài mảng JSON này.
Cấu trúc mỗi Object trong mảng bắt buộc phải có các trường sau bằng tiếng Anh:
[
  {{
    "question": "Nội dung câu hỏi ở đây?",
    "options": ["A. Lựa chọn 1", "B. Lựa chọn 2", "C. Lựa chọn 3", "D. Lựa chọn 4"],
    "answer": "A. Lựa chọn 1", 
    "explanation": "Giải thích ngắn gọn tại sao đáp án này đúng."
  }}
]
(Lưu ý: Giá trị của "answer" phải giống hệt 100% một trong các giá trị nằm trong mảng "options").
Nếu có công thức toán/lý/hóa, hãy bọc trong $...$ để hiển thị LaTeX.
"""
                        try:
                            engine_v2 = AIEngine2(default_model="gemini-2.5-flash") # Flash sinh JSON rất nhanh
                            result_text = engine_v2.generate_text(prompt, temperature=0.5)
                            
                            quiz_data = clean_json_response(result_text)
                            if quiz_data and isinstance(quiz_data, list):
                                st.session_state["ktn_quiz_data"] = quiz_data
                                st.session_state["ktn_submitted"] = False # Reset trạng thái nộp bài
                                st.session_state["ktn_score"] = 0
                                st.rerun() # Tải lại trang để hiển thị khu vực làm bài
                            else:
                                st.error("❌ AI không trả về đúng định dạng JSON. Vui lòng thử lại.")
                                st.code(result_text)
                        except Exception as e:
                            st.error(f"❌ Lỗi khi gọi AI: {e}")

    # ========================================================
    # KHU VỰC 2: GIAO DIỆN LÀM BÀI TRỰC TIẾP
    # ========================================================
    if st.session_state["ktn_quiz_data"]:
        st.markdown("---")
        st.markdown(f"### 📝 BÀI KIỂM TRA: {st.session_state.get('ktn_topic', 'TRẮC NGHIỆM')}")
        
        quiz_data = st.session_state["ktn_quiz_data"]
        
        # Sử dụng form để học sinh chọn xong hết mới nộp bài (tránh load lại trang liên tục)
        with st.form("quiz_form"):
            user_answers = []
            
            for i, q in enumerate(quiz_data):
                st.markdown(f"**Câu {i+1}: {q.get('question', '')}**")
                
                # Render Radio buttons
                options = q.get('options', [])
                
                # Nếu đã nộp bài, vô hiệu hóa việc chọn lại
                choice = st.radio(
                    label=f"Chọn đáp án cho câu {i+1}",
                    options=options,
                    index=None,
                    key=f"q_{i}",
                    label_visibility="collapsed",
                    disabled=st.session_state["ktn_submitted"]
                )
                user_answers.append(choice)
                
                # NẾU ĐÃ NỘP BÀI -> HIỂN THỊ KẾT QUẢ TỪNG CÂU
                if st.session_state["ktn_submitted"]:
                    correct_answer = q.get('answer', '')
                    if choice == correct_answer:
                        st.success(f"✅ Chính xác! {q.get('explanation', '')}")
                    else:
                        st.error(f"❌ Sai rồi. Đáp án đúng là: **{correct_answer}**")
                        st.info(f"💡 Giải thích: {q.get('explanation', '')}")
                
                st.markdown("---")
                
            # Nút Nộp Bài
            submit_btn = st.form_submit_button("✅ NỘP BÀI & XEM ĐIỂM", disabled=st.session_state["ktn_submitted"])
            
            if submit_btn:
                # Tính điểm
                score = 0
                for i, ans in enumerate(user_answers):
                    if ans == quiz_data[i].get('answer', ''):
                        score += 1
                        
                st.session_state["ktn_score"] = score
                st.session_state["ktn_submitted"] = True
                st.rerun()

        # HIỂN THỊ TỔNG ĐIỂM SAU KHI NỘP BÀI
        if st.session_state["ktn_submitted"]:
            total_q = len(quiz_data)
            score = st.session_state["ktn_score"]
            percentage = (score / total_q) * 100
            
            st.markdown("### 🏆 KẾT QUẢ BÀI LÀM")
            col_score1, col_score2 = st.columns(2)
            
            with col_score1:
                st.metric(label="Số câu đúng", value=f"{score} / {total_q} câu")
            with col_score2:
                st.metric(label="Tỷ lệ hoàn thành", value=f"{percentage:.0f}%")
                
            if percentage >= 80:
                st.balloons()
                st.success("Tuyệt vời! Bạn nắm kiến thức rất vững!")
            elif percentage >= 50:
                st.warning("Khá tốt! Nhưng hãy xem lại các câu sai nhé.")
            else:
                st.error("Cần cố gắng hơn. Bạn hãy đọc kỹ phần giải thích bên trên để rút kinh nghiệm!")
                
            if st.button("🔄 Làm lại bài này", use_container_width=True):
                st.session_state["ktn_submitted"] = False
                st.rerun()
