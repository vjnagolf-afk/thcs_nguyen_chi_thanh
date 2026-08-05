# -*- coding: utf-8 -*-
"""
============================================================
MODULE: modules/ho_tro_giang_day/mo_phong/page.py
Mô tả: Chuyên gia Sinh Prompt Sư phạm & Tối ưu AI trong Giáo dục.
(Thay thế cho chức năng Mô phỏng trùng lặp)
============================================================
"""

import streamlit as st

def render_xd_mo_phong(ai_engine=None):
    st.markdown("### 🎯 Chuyên gia Sinh Prompt Sư phạm & Tối ưu AI")
    st.caption("Thư viện câu lệnh (Prompt) chuẩn hóa, giúp thầy cô và học sinh tương tác với các công cụ AI (ChatGPT, Gemini, Claude,...) đạt hiệu quả cao nhất. Thầy cô chỉ cần bấm biểu tượng 'Copy' ở góc phải mỗi ô mã để dán vào AI.")

    # ==========================================
    # BẢNG THÔNG BÁO LƯU Ý KHI DÙNG PROMPT AI TRONG GIÁO DỤC
    # ==========================================
    st.warning("**⚠️ QUY TẮC VÀ LƯU Ý QUAN TRỌNG KHI SỬ DỤNG AI TRONG GIÁO DỤC**\n"
               "1. **Xác thực thông tin:** AI có thể tạo ra thông tin không chính xác. Giáo viên bắt buộc phải kiểm duyệt kỹ lưỡng trước khi đưa vào bài giảng.\n"
               "2. **Bảo mật dữ liệu:** Không đưa danh tính học sinh, điểm số hoặc dữ liệu nhạy cảm của trường lên AI công cộng.\n"
               "3. **Vai trò chủ đạo:** AI chỉ là trợ lý. Tư duy sư phạm và sự thấu hiểu học sinh của thầy cô là không thể thay thế.\n"
               "4. **Hướng dẫn học sinh:** Dạy các em dùng AI để gợi mở ý tưởng, tuyệt đối không lạm dụng sao chép đối phó.")
    st.markdown("---")

    # ==========================================
    # CÁC TAB CHỨC NĂNG CHÍNH
    # ==========================================
    tab_khbd, tab_khao_thi, tab_tinh_huong, tab_hs, tab_ta = st.tabs([
        "📚 1. Kế hoạch bài dạy & Slide", 
        "📝 2. Đề kiểm tra", 
        "🧩 3. Tình huống & PHT", 
        "🎓 4. Dành cho Học sinh", 
        "🇬🇧 5. Tiếng Anh"
    ])

    # ------------------------------------------
    # TAB 1: KẾ HOẠCH BÀI DẠY (KHBD) & SLIDE
    # ------------------------------------------
    with tab_khbd:
        st.markdown("#### 📚 Prompt Soạn Kế hoạch bài dạy & Thiết kế Slide")
        loai_khbd = st.radio("Chọn mẫu Prompt:", [
            "KHBD Chuẩn CV 5512 & GDPT 2018 (Chi tiết)", 
            "KHBD Tích hợp Năng lực số (Eduaide/MagicSchool)", 
            "Thẩm định Kế hoạch bài dạy (Tổ trưởng chuyên môn)",
            "Thiết kế Slide bài giảng (Dùng cho Gamma.app, Canva AI)"
        ], horizontal=True)

        if "Chuẩn CV 5512" in loai_khbd:
            st.info("Mẫu Prompt yêu cầu AI đóng vai chuyên gia, xây dựng tiến trình 4 hoạt động chi tiết, tích hợp STEM, AI và Phân hóa.")
            prompt_khbd_chuan = """# 1. VAI TRÒ
Bạn là Chuyên gia Giáo dục cấp cao của Việt Nam, có nhiều năm kinh nghiệm biên soạn Kế hoạch bài dạy (KHBD) theo Chương trình Giáo dục phổ thông 2018.
Bạn am hiểu sâu về Công văn 5512/BGDĐT, Yêu cầu cần đạt, Giáo dục STEM, Khung năng lực số (Thông tư 02/2024/BGDĐT) và các phương pháp dạy học tích cực.

# 2. THÔNG TIN ĐẦU VÀO
* Môn học: [Nhập môn học]
* Lớp: [Nhập khối lớp]
* Bộ sách: [Nhập tên bộ sách]
* Bài học: [Nhập tên bài]
* Thời lượng: [Số tiết]
* Yêu cầu cần đạt: [Dán YCCĐ vào đây]

# 3. YÊU CẦU CẤU TRÚC (BẮT BUỘC DẠNG BẢNG)
I. Thông tin chung
II. Mục tiêu (Kiến thức, Năng lực đặc thù, Năng lực chung, Phẩm chất đo lường được).
III. Thiết bị dạy học và học liệu.
IV. Tiến trình dạy học (Gồm 4 HĐ: Khởi động, Hình thành kiến thức, Luyện tập, Vận dụng).
Mỗi hoạt động BẮT BUỘC trình bày 4 bước: (1) Chuyển giao nhiệm vụ, (2) Thực hiện nhiệm vụ, (3) Báo cáo thảo luận, (4) Kết luận nhận định.
Viết rõ lời nói của giáo viên và hành động của học sinh.

# 4. TÍCH HỢP BẮT BUỘC
- Cuối mỗi hoạt động có mục: Tích hợp AI (Gợi ý công cụ, Prompt mẫu, vai trò).
- Đánh giá năng lực số học sinh theo TT 02/2024 (Khai thác TT, Giao tiếp, Hợp tác...).
- Giáo dục STEM (nếu phù hợp).
- Phân hóa học sinh (Chậm, trung bình, khá giỏi).
- Các Phụ lục (Bảng tổng hợp AI, Học liệu số, Rubric, Câu hỏi đánh giá, Bài tập về nhà)."""
            st.code(prompt_khbd_chuan, language="markdown")
            
        elif "Năng lực số" in loai_khbd:
            st.info("Mẫu Prompt tập trung mạnh vào việc thiết kế hoạt động phát triển Năng lực số và AI cho học sinh.")
            prompt_magicschool = """Hãy soạn giáo án hoàn toàn bằng tiếng Việt và bắt buộc phải tuân theo cấu trúc chuẩn của Công văn 5512/BGDĐT-GDTrH bao gồm đầy đủ các phần sau:
I. MỤC TIÊU: 
1. Về kiến thức; 
2. Về năng lực; (Phải có đầy đủ 3 nhóm năng lực: a) Năng lực chung; b) Năng lực đặc thù; c) Năng lực số và AI). 
(Phần Năng lực số và AI phải thực hiện đúng các mảng năng lực số và các chỉ báo mức độ theo thông tư 02/2025 của bộ giáo dục và đào tạo)
3. Về phẩm chất.

II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU.
III. TIẾN TRÌNH DẠY HỌC: 
Thiết kế đủ 4 hoạt động học tập (Khởi động, Hình thành kiến thức, Luyện tập, Vận dụng). Mỗi hoạt động chia rõ 4 mục: a) Mục tiêu; b) Nội dung; c) Sản phẩm; d) Tổ chức thực hiện (Chuyển giao, Thực hiện, Báo cáo, Kết luận).

# TÍCH HỢP NĂNG LỰC SỐ
Mỗi hoạt động cần chỉ rõ học sinh được hình thành:
- Khai thác thông tin số
- Giao tiếp số
- Hợp tác số
- Sáng tạo nội dung số
- An toàn số
- Giải quyết vấn đề bằng công nghệ số
Đánh dấu mức độ (Có/Không) và mô tả cụ thể."""
            st.code(prompt_magicschool, language="markdown")

        elif "Thiết kế Slide" in loai_khbd:
            st.info("💡 **Cách dùng:** Copy đoạn prompt dưới đây, điền nội dung bài học rồi dán vào Gemini. Sau đó, copy kết quả dàn ý từ Gemini dán thẳng vào [Gamma.app](https://gamma.app) hoặc Canva (Magic Design) để AI tự động tạo hình ảnh và slide trong 1 phút.")
            prompt_slide = """# VAI TRÒ
Bạn là chuyên gia thiết kế bài giảng điện tử (E-learning), chuyên gia Presentation Design (PowerPoint, Canva, Gamma) và là giáo viên dày dặn kinh nghiệm giảng dạy theo Chương trình GDPT 2018 của Việt Nam. Khả năng đặc biệt của bạn là chuyển hóa kiến thức học thuật thành nội dung trực quan, tối giản, dễ hiểu và hấp dẫn học sinh THCS.

# THÔNG TIN ĐẦU VÀO
- Môn học: [Điền môn học]
- Lớp: [Điền lớp]
- Tên bài học: [Điền tên bài]
- Thời lượng: [Điền thời lượng, ví dụ: 45 phút]
- Mục tiêu bài học: [Điền mục tiêu]
- Nội dung tóm tắt/SGK: [Copy/paste nội dung SGK hoặc tóm tắt vào đây]

# MỤC TIÊU & QUY TẮC THIẾT KẾ (RẤT QUAN TRỌNG)
Tạo kịch bản slide bài giảng hoàn chỉnh tuân thủ TUYỆT ĐỐI các quy tắc sau:

1. Nguyên tắc Đa phương tiện (Multimedia Learning - Richard Mayer):
   - Coherence: Loại bỏ hoàn toàn thông tin, hình ảnh, từ ngữ thừa.
   - Signaling: Dùng các dấu hiệu (in đậm, màu sắc) để làm nổi bật ý chính.
   - Redundancy: Không lặp lại nguyên văn chữ trên slide vào lời giảng.
   - Spatial Contiguity: Sắp xếp chữ phải đặt sát ngay cạnh hình ảnh liên quan.
   - Temporal Contiguity: Lời giảng và hình ảnh/hiệu ứng phải xuất hiện đồng thời.
   - Segmenting: Chia nhỏ nội dung phức tạp thành các slide/bước nhỏ dễ tiêu hóa.
   - Personalization: Sử dụng ngôn ngữ xưng hô gần gũi, phù hợp học sinh THCS.

2. Phong cách & Màu sắc:
   - Thiết kế Tối giản (Minimalism), nhiều khoảng trắng, font Sans Serif dễ đọc.
   - Tối đa 3 màu: 1 màu chính, 1 màu nhấn, 1 màu trung tính. Tuyệt đối không dùng quá nhiều màu lòe loẹt.

3. Giới hạn Text (Quy tắc thép):
   - 1 Slide = 1 Thông điệp.
   - Tiêu đề: Ngắn gọn, nổi bật, TỐI ĐA 10 TỪ.
   - Nội dung chữ: Dạng bullet point. TỐI ĐA 3-5 ý/slide. TỐI ĐA 12 từ/ý. KHÔNG viết đoạn văn.

4. Trực quan hóa (Visual First): 
   - BẮT BUỘC: Mỗi slide phải có ít nhất một thành phần trực quan (icon, infographic, sơ đồ, timeline, bảng, hình minh họa, ảnh thực tế, mô hình 3D, biểu đồ).
   - Không được phép tạo slide toàn chữ.

5. Hiệu ứng (Animation/Transition):
   - Chỉ sử dụng các hiệu ứng chuyên nghiệp: Fade, Appear, Wipe, hoặc Morph.
   - Tuyệt đối KHÔNG đề xuất các hiệu ứng gây rối mắt (Bounce, Fly, Spin...).

6. Tương tác & Đánh giá: 
   - Lồng ghép linh hoạt (Câu hỏi, Mini game, Thí nghiệm, QR Code, Video...).
   - Xác định rõ mức độ nhận thức theo Thang Bloom cho từng slide.

# ĐẦU RA YÊU CẦU
Hãy thiết kế lần lượt TOÀN BỘ bài học, không rút gọn, không bỏ sót phần nào. Nếu quá dài, hãy dừng lại ở slide hợp lý và đợi tôi gõ "Tiếp tục". 

Trình bày MỖI SLIDE theo đúng định dạng Template dưới đây:

---
### Slide [Số thứ tự]: [Tên Slide - Tối đa 10 từ]
- **Mục tiêu Slide:** [1 câu ngắn gọn]
- **Mức tư duy Bloom:** [Remember / Understand / Apply / Analyze / Evaluate / Create]
- **Bố cục thiết kế:** [Đề xuất: Left text + Right image / 3 columns / Mindmap / Timeline / Table / Full image...]
- **Nội dung trên Slide (Text hiển thị):**
  + Ý 1: [Tối đa 12 từ]
  + Ý 2: [Tối đa 12 từ]
  + Ý 3: [Tối đa 12 từ]
- **Thành phần Trực quan & Hình ảnh:**
  + Mô tả: [Ghi rõ loại thành phần (VD: Sơ đồ, Icon, Ảnh thực tế) và mô tả chi tiết]
  + Prompt tạo ảnh AI: "[Viết 1 prompt tiếng Anh chi tiết. VD: A realistic illustration of...]"
- **Hiệu ứng & Tương tác (Nếu có):** [Chỉ định Fade/Appear/Wipe/Morph và Hoạt động tương tác]
- **Ghi chú cho Giáo viên (Speaker Notes):**
  + Gợi ý lời giảng: [2-4 câu diễn giải tự nhiên, cuốn hút, không đọc lại chữ trên slide]
  + Thời lượng dự kiến: [X phút]
---"""
            st.code(prompt_slide, language="markdown")
            
        else:
            st.info("Mẫu Prompt để nhờ AI duyệt và chấm điểm giáo án như một Tổ trưởng chuyên môn.")
            prompt_thamdinh = """Đóng vai là một Tổ trưởng chuyên môn cấp THCS có chuyên môn sâu về sư phạm, công nghệ thông tin và ứng dụng AI trong giáo dục. 
Nhiệm vụ của bạn là đọc, phân tích và thẩm định Kế hoạch bài dạy (KHBD) dưới đây dựa trên 5 tiêu chí:
1. Sư phạm (Theo CV 5512).
2. Ứng dụng CNTT.
3. Tích hợp Năng lực số.
4. Năng lực AI.
5. Kiểm tra, Đánh giá.

# YÊU CẦU ĐẦU RA:
Trình bày kết quả dưới dạng "PHIẾU THẨM ĐỊNH KẾ HOẠCH BÀI DẠY":
I. NHẬN XÉT TỔNG QUAN (2 điểm sáng, 1 lỗ hổng lớn nhất).
II. PHÂN TÍCH 5 TIÊU CHÍ (Chấm thang Đạt/Cần cải thiện/Xuất sắc. BẮT BUỘC trích dẫn minh chứng từ giáo án).
III. YÊU CẦU ĐIỀU CHỈNH (3 gợi ý chỉnh sửa trực tiếp, thực tế).

Nội dung giáo án cần thẩm định:
[DÁN GIÁO ÁN CỦA BẠN VÀO ĐÂY]"""
            st.code(prompt_thamdinh, language="markdown")

    # ------------------------------------------
    # TAB 2: ĐỀ KIỂM TRA & KHẢO THÍ
    # ------------------------------------------
    with tab_khao_thi:
        st.markdown("#### 📝 Prompt Xây dựng Đề kiểm tra & Khảo thí")
        loai_de = st.radio("Chọn chức năng:", ["Xây dựng toàn bộ Ma trận & Đề kiểm tra", "Cấu hình AI Khảo thí chuyên sâu"], horizontal=True)
        
        if "toàn bộ" in loai_de:
            st.info("Lệnh tổng hợp tạo từ A-Z một bài kiểm tra kèm Ma trận, Đặc tả, Đề, Đáp án và Hướng dẫn chấm.")
            prompt_de_kt = """NHIỆM VỤ
Hãy xây dựng đầy đủ một Bộ đề kiểm tra môn [Nhập môn học], lớp [Nhập lớp], chủ đề [Nhập chủ đề].

Quy trình:
Bước 1: Phân tích yêu cầu giáo viên.
Bước 2: Sử dụng CT GDPT 2018 (hoặc tài liệu đính kèm nếu có).
Bước 3: Tạo đầy đủ các phần bằng Markdown chuẩn:
I. Ma trận
II. Bản đặc tả
III. Đề kiểm tra (Trắc nghiệm & Tự luận)
IV. Đáp án
V. Hướng dẫn chấm

Bước 4: Tự kiểm tra:
✓ Đủ số câu
✓ Đủ số điểm
✓ Tổng điểm = 10
✓ Đúng tỉ lệ mức độ (Nhận biết, Thông hiểu, Vận dụng, VDC)
✓ Không thiếu phần nào. (Các công thức Toán/Lý/Hóa/Sinh phải dùng LaTeX)."""
            st.code(prompt_de_kt, language="markdown")
        else:
            st.info("System Prompt giúp thiết lập cấu hình chuyên gia cho các AI tạo đề tự động.")
            prompt_sys = """Bạn là Chuyên gia khảo thí cao cấp của Bộ Giáo dục và Đào tạo Việt Nam.
NHIỆM VỤ
- Xây dựng đề kiểm tra theo Chương trình GDPT 2018.
- Đánh giá phẩm chất và năng lực học sinh.
- Tuân thủ Công văn 5512 và các hướng dẫn hiện hành.

QUY TẮC BẮT BUỘC
1. Luôn trả lời bằng Markdown chuẩn.
2. Công thức Toán, Lý, Hóa, Sinh bắt buộc dùng LaTeX (VD: $$x^2+y^2=1$$).
3. Bảng Markdown phải đúng chuẩn. Không dùng HTML.
4. Không sinh dữ liệu giả. Không dừng giữa chừng.
5. Chỉ trả về đúng nội dung đề kiểm tra."""
            st.code(prompt_sys, language="markdown")

    # ------------------------------------------
    # TAB 3: TÌNH HUỐNG SƯ PHẠM & PHIẾU HỌC TẬP
    # ------------------------------------------
    with tab_tinh_huong:
        st.markdown("#### 🧩 Gỡ rối tình huống giảng dạy & Công cụ hỗ trợ")
        th_chon = st.selectbox("Chọn nhu cầu của bạn:", [
            "Tạo Phiếu học tập & Hoạt động Thảo luận",
            "Tóm tắt kiến thức cốt lõi",
            "Xử lý tình huống học sinh lơ đễnh/mất tập trung",
            "Xử lý tình huống học sinh mâu thuẫn khi làm việc nhóm"
        ])

        if "Phiếu học tập" in th_chon:
            st.code("""Vai trò: Bạn là chuyên gia thiết kế học liệu sư phạm tích cực.
Nhiệm vụ: Hãy thiết kế một Phiếu học tập và 3 câu hỏi thảo luận nhóm (theo kỹ thuật Khăn phủ bàn) cho bài [Điền tên bài], môn [Điền môn].
Yêu cầu:
- Phiếu học tập có phân hóa mức độ: Cơ bản (Đạt) và Nâng cao (Vận dụng sáng tạo).
- Câu hỏi thảo luận gắn liền với tình huống thực tiễn đời sống.""", language="markdown")
        elif "Tóm tắt" in th_chon:
            st.code("""Vai trò: Bạn là chuyên gia sơ đồ hóa tư duy.
Nhiệm vụ: Hãy cô đọng kiến thức trọng tâm bài [Điền tên bài], môn [Điền môn], lớp [Điền lớp].
Yêu cầu: Trình bày dạng bullet points mạch lạc, sử dụng các từ khóa chính (Key terms) giúp học sinh dễ dàng ghi nhớ nhanh để ôn thi.""", language="markdown")
        elif "lơ đễnh" in th_chon:
            st.code("""Vai trò: Bạn là chuyên gia tâm lý học đường.
Nhiệm vụ: Học sinh lớp [Điền lớp] thường lơ đễnh, nói chuyện riêng trong giờ môn [Điền môn]. 
Hãy tư vấn: 3 nguyên nhân tâm lý cốt lõi và kịch bản 3 bước xử lý nhẹ nhàng, dứt điểm ngay tại lớp mà không làm gián đoạn bài giảng.""", language="markdown")
        else:
            st.code("""Vai trò: Bạn là chuyên gia công tác chủ nhiệm.
Nhiệm vụ: Khi hoạt động nhóm bài [Điền bài], các em xảy ra tranh cãi, không hợp tác. 
Hãy cung cấp kịch bản giải quyết mâu thuẫn tại chỗ và cách thức chia lại vai trò để rèn luyện kỹ năng hợp tác cho học sinh.""", language="markdown")

    # ------------------------------------------
    # TAB 4: DÀNH CHO HỌC SINH
    # ------------------------------------------
    with tab_hs:
        st.markdown("#### 🎓 Hướng dẫn Học sinh sử dụng AI (Tự học & Phản biện)")
        st.info("Giáo viên copy prompt này gửi cho học sinh để rèn khả năng tự học, cam kết AI không làm hộ bài.")
        
        hs_chon = st.selectbox("Mục tiêu tự học của học sinh:", [
            "AI đóng vai Gia sư giải thích bài khó (Không giải hộ)",
            "AI đóng vai Người tạo câu hỏi ôn tập tương tác",
            "AI đóng vai Chuyên gia phản biện (Critical Thinking)"
        ])
        
        if "Gia sư" in hs_chon:
            st.code("""Vai trò: Bạn là một gia sư kiên nhẫn, thân thiện.
Nhiệm vụ: Tôi là học sinh lớp [Điền lớp]. Tôi đang không hiểu phần [Điền kiến thức] của môn [Điền môn].
Nguyên tắc: KHÔNG BAO GIỜ được giải hộ bài tập hay đưa đáp án trực tiếp. Hãy đặt các câu hỏi gợi mở nhỏ để dẫn dắt tôi tự suy luận ra vấn đề.""", language="markdown")
        elif "ôn tập" in hs_chon:
            st.code("""Vai trò: Bạn là hệ thống trắc nghiệm thông minh.
Nhiệm vụ: Tạo cho tôi 5 câu hỏi ôn tập chủ đề [Điền chủ đề].
Cách thức: Đưa ra TỪNG CÂU HỎI MỘT. Tôi trả lời xong, bạn nhận xét đúng/sai, giải thích chi tiết rồi mới chuyển sang câu tiếp theo.""", language="markdown")
        else:
            st.code("""Vai trò: Bạn là một nhà tư duy phản biện sắc sảo.
Nhiệm vụ: Tôi có một góc nhìn về vấn đề: "[Nhập quan điểm của học sinh]".
Hãy đặt cho tôi 2-3 câu hỏi phản biện lật lại vấn đề để giúp tôi kiểm tra lại tính logic và củng cố lập luận của mình.""", language="markdown")

    # ------------------------------------------
    # TAB 5: TIẾNG ANH (ENGLISH ELT)
    # ------------------------------------------
    with tab_ta:
        st.markdown("#### 🇬🇧 Bộ Prompt Chuyên biệt cho Giáo viên Tiếng Anh")
        ta_chon = st.selectbox("Kỹ năng / Hoạt động:", [
            "Tạo bài đọc hiểu (Reading Comprehension)",
            "Luyện từ vựng (Vocabulary Set)",
            "Sửa lỗi ngữ pháp & Viết (Writing Correction)",
            "Kịch bản hội thoại (Speaking Role-play)",
            "Trò chơi lớp học (Gamification)"
        ])
        
        if "đọc hiểu" in ta_chon:
            st.code("""Role: You are an expert ELT material developer.
Task: Create a Reading Comprehension passage for [Trình độ: A2/B1] students about [Chủ đề].
Requirements:
1. A passage of 150-200 words.
2. 5 Multiple-choice questions (main idea & details).
3. 3 Open-ended discussion questions.
4. Include the Answer Key.""", language="markdown")
        elif "từ vựng" in ta_chon:
            st.code("""Role: You are an innovative English teacher.
Task: Create a vocabulary learning set for the topic [Chủ đề] suitable for Grade [Lớp].
Requirements: Provide 8-10 key words/phrases with IPA phonetic transcriptions, word classes, Vietnamese meanings, and 1 example sentence for each. Then create a short gap-fill exercise.""", language="markdown")
        elif "ngữ pháp" in ta_chon:
            st.code("""Role: You are an experienced English writing coach.
Task: Analyze the following paragraph written by a student: "[Dán đoạn văn tiếng Anh]".
Requirements: 
1. Create a table listing errors (Original -> Correction -> Explanation in Vietnamese).
2. Rewrite an improved, natural version of the paragraph.""", language="markdown")
        elif "hội thoại" in ta_chon:
            st.code("""Role: You are a native conversation partner.
Task: Write a natural dialogue for a Speaking role-play activity in class.
Topic: [Tình huống, VD: At a restaurant]. Level: [Trình độ].
Include Person A and Person B. Add 3 follow-up questions for pair practice.""", language="markdown")
        else:
            st.code("""Role: You are an ELT gamification expert.
Task: Design a fun, fast-paced classroom game script to review [Chủ đề từ vựng/ngữ pháp] for [Độ tuổi] students.
Requirements: Name of the game, Objectives, Materials needed, and Step-by-step instructions to play within 10-15 minutes.""", language="markdown")
