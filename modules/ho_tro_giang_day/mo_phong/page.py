# -*- coding: utf-8 -*-
"""
============================================================
MODULE: modules/ho_tro_giang_day/chuyen_gia_prompt.py
Mô tả: Chuyên gia Sinh Prompt Sư phạm & Tối ưu AI trong Giáo dục.
Tính năng:
    - Thư viện prompt mẫu theo môn học (Soạn KHBD, Sinh đề, Thảo luận, Tóm tắt...).
    - Prompt xử lý các tình huống sư phạm trong giảng dạy.
    - Prompt định hướng dành riêng cho học sinh.
    - Bộ prompt chuyên biệt dành riêng cho môn Tiếng Anh (Reading, Writing, Speaking...).
    - Bảng thông báo lưu ý đạo đức và nguyên tắc an toàn khi dùng AI.
============================================================
"""

import streamlit as st

def render_chuyen_gia_prompt():
    st.markdown("### 🎯 Chuyên gia Sinh Prompt Sư phạm & Tối ưu AI")
    st.caption("Thư viện câu lệnh (Prompt) chuẩn hóa, giúp thầy cô và học sinh tương tác với các công cụ AI (ChatGPT, Gemini, Claude,...) đạt hiệu quả cao nhất.")

    # ==========================================
    # BẢNG THÔNG BÁO LƯU Ý KHI DÙNG PROMPT AI TRONG GIÁO DỤC
    # ==========================================
    with st.expander("⚠️ QUY TẮC VÀ LƯU Ý QUAN TRỌNG KHI SỬ DỤNG AI TRONG GIÁO DỤC", expanded=False):
        st.markdown("""
        * **1. Xác thực thông tin (Fact-Checking):** AI có thể tạo ra thông tin không chính xác hoặc "ảo giác" (hallucination). Giáo viên bắt buộc phải kiểm duyệt kỹ lưỡng trước khi đưa vào bài giảng hoặc phát cho học sinh.
        * **2. Bảo mật dữ liệu cá nhân:** Không đưa thông tin mật, danh tính học sinh, hoặc dữ liệu nhạy cảm của nhà trường vào các nền tảng AI công cộng.
        * **3. Giữ vững vai trò chủ đạo của nhà giáo:** AI chỉ là công cụ hỗ trợ (co-pilot), tư duy sư phạm, cảm xúc và sự thấu hiểu học sinh của thầy cô là không thể thay thế.
        * **4. Định hướng học sinh sử dụng trung thực:** Khi cung cấp prompt cho học sinh, cần hướng dẫn các em dùng AI như một trợ lý gợi ý ý tưởng, tuyệt đối không sao chép nguyên văn để đối phó.
        """)

    st.markdown("---")

    # ==========================================
    # CÁC TAB CHỨC NĂNG CHÍNH
    # ==========================================
    tab_mon_hoc, tab_tinh_huong, tab_hoc_sinh, tab_tieng_anh = st.tabs([
        "📚 1. Prompt Theo Môn Học & Soạn Giảng", 
        "🧩 2. Prompt Tình Huống Giảng Dạy", 
        "🎓 3. Prompt Dành Cho Học Sinh", 
        "🇬🇧 4. Prompt Chuyên Biệt Môn Tiếng Anh"
    ])

    # ==========================================
    # TAB 1: PROMPT THEO MÔN HỌC & SOẠN GIẢNG
    # ==========================================
    with tab_mon_hoc:
        st.markdown("#### 📚 Thư viện Prompt hỗ trợ chuyên môn giáo viên")
        
        danh_muc_mon = st.selectbox(
            "Chọn mục đích sử dụng:",
            [
                "Soạn Kế hoạch bài dạy (KHBD chuẩn CV 5512)", 
                "Sinh Đề kiểm tra & Ma trận đề", 
                "Tạo Câu hỏi thảo luận / Khởi động", 
                "Làm Phiếu học tập phân hóa", 
                "Tóm tắt kiến thức cốt lõi"
            ],
            key="sel_muc_dich_mon"
        )

        if "KHBD" in danh_muc_mon:
            st.markdown("##### 📝 Prompt: Soạn Kế hoạch bài dạy chi tiết")
            prompt_content = """Vai trò: Bạn là Chuyên gia Giáo dục cấp cao, am hiểu sâu sắc Chương trình GDPT 2018 và Công văn 5512.
Nhiệm vụ: Hãy soạn một Kế hoạch bài dạy chi tiết cho bài học sau:
- Môn học: [Điền tên môn học]
- Khối lớp: [Điền khối lớp]
- Tên bài học: [Điền tên bài]
- Thời lượng: [Điền số tiết]

Yêu cầu cấu trúc bắt buộc:
1. Mục tiêu (Kiến thức, Năng lực chung/đặc thù, Phẩm chất).
2. Thiết bị dạy học và học liệu.
3. Tiến trình dạy học gồm 4 hoạt động: (1) Khởi động, (2) Hình thành kiến thức mới, (3) Luyện tập, (4) Vận dụng. Mỗi hoạt động phải trình bày rõ bảng 4 bước (Chuyển giao, Thực hiện, Báo cáo, Kết luận) và lồng ghép tích hợp Năng lực số."""
            st.code(prompt_content, language="markdown")
            st.info("💡 **Cách dùng:** Copy đoạn trên, điền thông tin bài học của thầy cô vào trong ngoặc vuông `[...]` rồi dán vào ChatGPT hoặc Gemini.")

        elif "Đề kiểm tra" in danh_muc_mon:
            st.markdown("##### 📝 Prompt: Sinh đề kiểm tra và ma trận")
            prompt_content = """Vai trò: Bạn là Chuyên gia khảo thí giáo dục phổ thông.
Nhiệm vụ: Hãy biên soạn một đề kiểm tra [15 phút / 1 tiết] môn [Điền tên môn], lớp [Điền lớp], chủ đề [Điền chủ đề].
Yêu cầu đầu ra bắt buộc:
1. Bảng Ma trận đề và Bản đặc tả (tỷ lệ: 40% Nhận biết, 30% Thông hiểu, 20% Vận dụng, 10% Vận dụng cao).
2. Đề kiểm tra gồm: Phần Trắc nghiệm (Nhiều lựa chọn, Đúng/Sai) và Phần Tự luận.
3. Đáp án chi tiết và Hướng dẫn chấm điểm cụ thể từng ý."""
            st.code(prompt_content, language="markdown")
            st.info("💡 **Cách dùng:** Copy đoạn trên, điều chỉnh thời lượng và môn học rồi gửi cho AI để nhận bộ đề hoàn chỉnh kèm hướng dẫn chấm.")

        elif "Thảo luận" in danh_muc_mon:
            st.markdown("##### 📝 Prompt: Thiết kế câu hỏi khởi động & thảo luận nhóm")
            prompt_content = """Vai trò: Bạn là giáo viên sáng tạo phương pháp dạy học tích cực.
Nhiệm vụ: Hãy thiết kế hệ thống câu hỏi khởi động (Warm-up) và câu hỏi thảo luận nhóm cho bài học: [Điền tên bài học], môn [Điền môn], lớp [Điền lớp].
Yêu cầu:
1. Câu hỏi khởi động dạng trò chơi hoặc tình huống có vấn đề kích thích tò mò.
2. 3 câu hỏi thảo luận theo kỹ thuật khăn phủ bàn hoặc mảnh ghép, có phân hóa mức độ từ dễ đến khó gắn liền với thực tiễn đời sống."""
            st.code(prompt_content, language="markdown")

        elif "Phiếu học tập" in danh_muc_mon:
            st.markdown("##### 📝 Prompt: Thiết kế Phiếu học tập phân hóa")
            prompt_content = """Vai trò: Bạn là nhà thiết kế học liệu sư phạm chuyên nghiệp.
Nhiệm vụ: Hãy thiết kế một Phiếu học tập sử dụng trong hoạt động [Điền tên hoạt động] của bài [Điền tên bài], môn [Điền môn].
Yêu cầu:
- Trình bày dạng bảng hoặc sơ đồ tư duy logic.
- Có phân hóa nhiệm vụ rõ ràng: Dành cho học sinh mức độ Đạt (Cơ bản) và mức độ Nâng cao (Vận dụng sáng tạo)."""
            st.code(prompt_content, language="markdown")

        else:
            st.markdown("##### 📝 Prompt: Tóm tắt kiến thức cốt lõi (Infographic / Sơ đồ)")
            prompt_content = """Vai trò: Bạn là chuyên gia sư phạm chuyên tối ưu hóa nội dung học tập.
Nhiệm vụ: Hãy cô đọng và tóm tắt toàn bộ kiến thức trọng tâm của bài: [Điền tên bài học], môn [Điền môn], lớp [Điền lớp].
Yêu cầu:
- Ngắn gọn, súc tích, dễ nhớ.
- Trình bày dưới dạng các từ khóa chính (Key terms), sơ đồ dạng text hoặc các bullet points mạch lạc giúp học sinh dễ dàng ghi nhớ nhanh trước khi kiểm tra."""
            st.code(prompt_content, language="markdown")

    # ==========================================
    # TAB 2: PROMPT TÌNH HUỐNG GIẢNG DẠY
    # ==========================================
    with tab_tinh_huong:
        st.markdown("#### 🧩 Gỡ rối các tình huống sư phạm phức tạp trong lớp học")
        
        tinh_huong_chon = st.selectbox(
            "Chọn tình huống cần hỗ trợ:",
            [
                "Học sinh mất tập trung, nói chuyện riêng trong giờ", 
                "Học sinh có năng lực tiếp thu chậm, chèn ép kiến thức", 
                "Xử lý mâu thuẫn/xích mích giữa các học sinh trong nhóm", 
                "Câu hỏi khó/bất ngờ của học sinh ngoài SGK"
            ],
            key="sel_tinh_huong"
        )

        if "mất tập trung" in tinh_huong_chon:
            prompt_th = """Vai trò: Bạn là chuyên gia tâm lý học đường và quản lý lớp học tích cực.
Nhiệm vụ: Tôi đang gặp tình trạng học sinh lớp [Điền lớp] thường xuyên lơ đễnh, nói chuyện riêng khi tôi giảng bài môn [Điền tên môn]. 
Hãy tư vấn cho tôi:
1. 3 nguyên nhân tâm lý phổ biến dẫn đến hành vi này ở lứa tuổi học sinh THCS.
2. Các giải pháp can thiệp nhẹ nhàng nhưng dứt điểm ngay tại lớp mà không làm ảnh hưởng đến tiến độ bài giảng."""
            st.code(prompt_th, language="markdown")

        elif "chậm" in tinh_huong_chon:
            prompt_th = """Vai trò: Bạn là chuyên gia giáo dục hòa nhập và phân hóa học sinh.
Nhiệm vụ: Trong lớp tôi có một số học sinh tiếp thu rất chậm, thường xuyên không theo kịp tiến độ của bài học môn [Điền môn]. 
Hãy giúp tôi thiết kế chiến lược hỗ trợ học sinh này:
- Cách điều chỉnh nhiệm vụ học tập nhỏ hơn (Scaffolding).
- Gợi ý phương pháp hỗ trợ trực quan giúp các em tự tin lấy lại động lực học tập."""
            st.code(prompt_th, language="markdown")

        elif "mâu thuẫn" in tinh_huong_chon:
            prompt_th = """Vai trò: Bạn là cố vấn công tác chủ nhiệm lớp học.
Nhiệm vụ: Khi tổ chức hoạt động nhóm môn [Điền môn], các em học sinh trong nhóm xảy ra tranh cãi, đùn đẩy công việc và không chịu hợp tác với nhau. 
Hãy đưa ra kịch bản giải quyết tình huống sư phạm này cho giáo viên chủ nhiệm/bộ môn nhằm xoa dịu tâm lý và hướng dẫn các em kỹ năng làm việc nhóm hiệu quả."""
            st.code(prompt_th, language="markdown")

        else:
            prompt_th = """Vai trò: Bạn là trợ lý chuyên môn khoa học đa ngành.
Nhiệm vụ: Trong giờ dạy môn [Điền môn], học sinh hỏi một câu hỏi khó ngoài chương trình SGK: "[Nhập câu hỏi của học sinh vào đây]".
Hãy cung cấp cho tôi:
1. Câu trả lời chính xác, khoa học và dễ hiểu nhất đối với lứa tuổi học sinh phổ thông.
2. Gợi ý cách dẫn dắt khéo léo để biến câu hỏi này thành một cơ hội mở rộng tư duy cho cả lớp."""
            st.code(prompt_th, language="markdown")

    # ==========================================
    # TAB 3: PROMPT DÀNH CHO HỌC SINH
    # ==========================================
    with tab_hoc_sinh:
        st.markdown("#### 🎓 Hướng dẫn học sinh sử dụng AI làm gia sư thông minh")
        st.info("💡 **Lời khuyên cho giáo viên:** Thầy cô có thể copy các prompt này dán lên bảng hoặc gửi vào nhóm lớp để định hướng các em dùng AI đúng cách, tránh việc học sinh nhờ AI làm hộ bài tập một cách thụ động.")

        muc_dich_hs = st.selectbox(
            "Chọn định hướng cho học sinh:",
            [
                "Đóng vai gia sư giải thích bài khó (Không làm hộ)", 
                "Tự tạo câu hỏi trắc nghiệm ôn tập trước kỳ thi", 
                "Luyện tập kỹ năng đặt câu hỏi phản biện (Critical Thinking)"
            ],
            key="sel_hs"
        )

        if "gia sư" in muc_dich_hs:
            prompt_hs = """Vai trò: Bạn là một người thầy/gia sư kiên nhẫn, thân thiện và giàu lòng khích lệ học sinh.
Nhiệm vụ: Tôi là học sinh lớp [Điền lớp] đang gặp khó khăn ở bài [Điền tên bài], môn [Điền môn]. 
Nguyên tắc làm việc của bạn:
- KHÔNG BAO GIỜ được đưa ra đáp án trực tiếp hay làm hộ bài tập cho tôi.
- Hãy dùng phương pháp gợi mở, đặt các câu hỏi nhỏ để dẫn dắt tôi tự suy luận ra vấn đề."""
            st.code(prompt_hs, language="markdown")

        elif "trắc nghiệm" in muc_dich_hs:
            prompt_hs = """Vai trò: Bạn là hệ thống trắc nghiệm ôn tập thông minh.
Nhiệm vụ: Hãy tạo cho tôi 5 câu hỏi trắc nghiệm khách quan về chủ đề [Điền chủ đề], môn [Điền môn].
Cách thức tương tác:
- Hãy đưa ra từng câu hỏi một. Khi tôi trả lời xong, bạn mới nhận xét đúng/sai, giải thích chi tiết rồi mới chuyển sang câu tiếp theo."""
            st.code(prompt_hs, language="markdown")

        else:
            prompt_hs = """Vai trò: Bạn là một nhà phản biện khoa học sắc sảo.
Nhiệm vụ: Tôi có một quan điểm về vấn đề [Điền vấn đề/hiện tượng]: "[Nhập quan điểm của học sinh]".
Hãy đặt cho tôi 2 câu hỏi phản biện góc nhìn đa chiều để giúp tôi kiểm tra lại tính logic và củng cố lập luận của mình một cách sâu sắc hơn."""
            st.code(prompt_hs, language="markdown")

    # ==========================================
    # TAB 4: PROMPT CHUYÊN BIỆT MÔN TIẾNG ANH
    # ==========================================
    with tab_tieng_anh:
        st.markdown("#### 🇬🇧 Bộ công cụ Prompt chuyên biệt hỗ trợ giáo viên Tiếng Anh")

        ky_nang_ta = st.selectbox(
            "Chọn kỹ năng / Hoạt động Tiếng Anh:",
            [
                "Tạo bài đọc hiểu (Reading Comprehension)", 
                "Luyện từ vựng theo chủ đề (Vocabulary)", 
                "Sửa lỗi ngữ pháp & Viết lại câu (Writing Correction)", 
                "Tạo hội thoại giao tiếp (Speaking / Listening Scripts)", 
                "Thiết kế trò chơi lớp học (Gamification)"
            ],
            key="sel_ta"
        )

        if "đọc hiểu" in ky_nang_ta:
            prompt_ta = """Role: You are an expert English Language Teaching (ELT) material developer.
Task: Create a Reading Comprehension passage and exercises for students at [Điền trình độ: A2 / B1], topic [Điền chủ đề].
Requirements:
1. A reading passage of about 150-200 words using appropriate vocabulary and grammar structures.
2. 5 Multiple-choice questions checking comprehension main ideas and details.
3. 3 Open-ended discussion questions.
4. Answer key included."""
            st.code(prompt_ta, language="markdown")

        elif "từ vựng" in ky_nang_ta:
            prompt_ta = """Role: You are an innovative English teacher.
Task: Create a vocabulary learning set for the topic [Điền chủ đề] suitable for grade [Điền khối lớp].
Requirements:
1. Provide 8-10 key words/phrases with phonetic transcriptions (IPA), word classes, Vietnamese meanings, and an illustrative example sentence for each.
2. Create a short gap-fill exercise using these words."""
            st.code(prompt_ta, language="markdown")

        elif "ngữ pháp" in ky_nang_ta:
            prompt_ta = """Role: You are an experienced English writing coach.
Task: Analyze the following paragraph written by a student, identify grammar/vocabulary errors, and provide feedback:
"[Dán đoạn văn tiếng Anh của học sinh vào đây]"
Requirements:
1. List the errors clearly in a table (Original sentence -> Correction -> Explanation in Vietnamese).
2. Rewrite an improved, natural version of the paragraph."""
            st.code(prompt_ta, language="markdown")

        elif "hội thoại" in ky_nang_ta:
            prompt_ta = """Role: You are a native English conversation partner and curriculum designer.
Task: Write a natural dialogue for a Speaking role-play activity in class.
- Topic: [Điền tình huống, ví dụ: At the airport / Ordering food]
- Level: [Điền trình độ]
- Characters: Person A and Person B.
- Include 3 suggested comprehension or follow-up questions for students to practice in pairs."""
            st.code(prompt_ta, language="markdown")

        else:
            prompt_ta = """Role: You are a gamification expert in education.
Task: Design a fun classroom game script to review grammar/vocabulary about [Điền chủ đề] for middle school students.
Requirements:
1. Game name and objectives.
2. Materials needed.
3. Step-by-step rules and instructions on how to play within 10-15 minutes."""
            st.code(prompt_ta, language="markdown")
