def render_xd_de_kt(ai_engine):

    import streamlit as st
    import sys
    import re
    from pathlib import Path
    from io import BytesIO

    # ============================================================
    # 1. ĐỌC NỘI DUNG FILE
    # ============================================================
    def extract_text_from_file(uploaded_file):

        if uploaded_file is None:
            return ""

        try:

            file_name = uploaded_file.name.lower()
            file_bytes = uploaded_file.getvalue()

            if not file_bytes:
                return ""

            # ----------------------------------------------------
            # PDF
            # ----------------------------------------------------
            if file_name.endswith(".pdf"):

                from pypdf import PdfReader

                reader = PdfReader(
                    BytesIO(file_bytes)
                )

                pages = []

                for page in reader.pages:

                    try:

                        text = page.extract_text()

                        if text and text.strip():

                            pages.append(
                                text.strip()
                            )

                    except Exception:

                        continue

                return "\n\n".join(
                    pages
                ).strip()

            # ----------------------------------------------------
            # DOCX
            # ----------------------------------------------------
            elif file_name.endswith(".docx"):

                from docx import Document

                document = Document(
                    BytesIO(file_bytes)
                )

                contents = []

                # Đoạn văn
                for paragraph in document.paragraphs:

                    text = paragraph.text.strip()

                    if text:

                        contents.append(
                            text
                        )

                # Bảng
                for table in document.tables:

                    for row in table.rows:

                        cells = []

                        for cell in row.cells:

                            text = (
                                cell.text
                                .strip()
                            )

                            cells.append(
                                text
                            )

                        row_text = (
                            " | ".join(
                                cells
                            )
                        )

                        if row_text.strip():

                            contents.append(
                                row_text
                            )

                return "\n".join(
                    contents
                ).strip()

            # ----------------------------------------------------
            # TXT
            # ----------------------------------------------------
            elif file_name.endswith(".txt"):

                for encoding in [
                    "utf-8",
                    "cp1258",
                    "latin-1"
                ]:

                    try:

                        return file_bytes.decode(
                            encoding
                        ).strip()

                    except UnicodeDecodeError:

                        continue

            return ""

        except Exception as e:

            st.error(
                f"❌ Lỗi đọc file: {e}"
            )

            return ""

    # ============================================================
    # 2. CHUẨN HÓA NỘI DUNG ĐỀ CƯƠNG
    # ============================================================
    def normalize_outline(text):

        if not text:

            return ""

        lines = []

        for line in text.splitlines():

            line = re.sub(
                r"\s+",
                " ",
                line.strip()
            )

            if line:

                lines.append(
                    line
                )

        result = "\n".join(
            lines
        )

        # Giới hạn để tránh prompt quá lớn
        MAX_CHARS = 80000

        if len(result) > MAX_CHARS:

            result = result[
                :MAX_CHARS
            ]

        return result

    # ============================================================
    # 3. XÂY DỰNG CẤU TRÚC ĐỀ ĐỘNG
    # ============================================================
    def build_exam_structure(
        n_nlc,
        d_nlc,
        n_ds,
        d_ds,
        n_dk,
        d_dk,
        n_ngan,
        d_ngan,
        tl_points
    ):

        sections = []

        current_question = 1

        # --------------------------------------------------------
        # HÀM THÊM NHÓM CÂU HỎI
        # --------------------------------------------------------
        def add_section(
            section_name,
            question_type,
            count,
            points_each
        ):

            nonlocal current_question

            count = int(count)

            points_each = float(
                points_each
            )

            if count <= 0:

                return

            start_question = (
                current_question
            )

            end_question = (
                current_question
                + count
                - 1
            )

            questions = list(
                range(
                    start_question,
                    end_question + 1
                )
            )

            total_points = (
                count
                * points_each
            )

            sections.append(
                {
                    "name": section_name,

                    "type": question_type,

                    "count": count,

                    "points_each":
                        points_each,

                    "total_points":
                        total_points,

                    "start_question":
                        start_question,

                    "end_question":
                        end_question,

                    "questions":
                        questions
                }
            )

            current_question = (
                end_question + 1
            )

        # --------------------------------------------------------
        # PHẦN KHÁCH QUAN
        # --------------------------------------------------------
        add_section(
            "Nhiều lựa chọn",
            "NLC",
            n_nlc,
            d_nlc
        )

        add_section(
            "Đúng/Sai",
            "DUNG_SAI",
            n_ds,
            d_ds
        )

        add_section(
            "Điền khuyết",
            "DIEN_KHUYET",
            n_dk,
            d_dk
        )

        add_section(
            "Trả lời ngắn",
            "TRA_LOI_NGAN",
            n_ngan,
            d_ngan
        )

        # --------------------------------------------------------
        # PHẦN TỰ LUẬN
        # --------------------------------------------------------
        for index, point in enumerate(
            tl_points,
            start=1
        ):

            point = float(
                point
            )

            if point <= 0:

                continue

            question_number = (
                current_question
            )

            sections.append(
                {
                    "name": "Tự luận",

                    "type": "TU_LUAN",

                    "count": 1,

                    "points_each": point,

                    "total_points": point,

                    "start_question":
                        question_number,

                    "end_question":
                        question_number,

                    "questions": [
                        question_number
                    ],

                    "tl_index": index
                }
            )

            current_question += 1

        total_questions = (
            current_question - 1
        )

        total_points = sum(
            section[
                "total_points"
            ]
            for section in sections
        )

        return {
            "sections": sections,

            "total_questions":
                total_questions,

            "total_points":
                total_points
        }

    # ============================================================
    # 4. TẠO HỢP ĐỒNG CẤU TRÚC ĐỀ ĐỘNG
    # ============================================================
    def build_structure_contract(
        exam_structure
    ):

        lines = []

        lines.append(
            "============================================================"
        )

        lines.append(
            "HỢP ĐỒNG CẤU TRÚC ĐỀ KIỂM TRA"
        )

        lines.append(
            "============================================================"
        )

        lines.append(
            f"TỔNG SỐ CÂU: "
            f"{exam_structure['total_questions']}"
        )

        lines.append(
            f"TỔNG ĐIỂM: "
            f"{exam_structure['total_points']:.2f}"
        )

        lines.append("")

        lines.append(
            "DANH SÁCH CÁC NHÓM CÂU HỎI:"
        )

        lines.append("")

        for index, section in enumerate(
            exam_structure[
                "sections"
            ],
            start=1
        ):

            start = (
                section[
                    "start_question"
                ]
            )

            end = (
                section[
                    "end_question"
                ]
            )

            if start == end:

                question_range = (
                    f"Câu {start}"
                )

            else:

                question_range = (
                    f"Câu {start} "
                    f"đến Câu {end}"
                )

            lines.append(
                f"{index}. "
                f"{section['name']}"
            )

            lines.append(
                f"   - Loại câu: "
                f"{section['type']}"
            )

            lines.append(
                f"   - Phạm vi: "
                f"{question_range}"
            )

            lines.append(
                f"   - Số câu: "
                f"{section['count']}"
            )

            lines.append(
                f"   - Điểm/câu: "
                f"{section['points_each']:.2f}"
            )

            lines.append(
                f"   - Tổng điểm: "
                f"{section['total_points']:.2f}"
            )

            lines.append("")

        lines.append(
            "DANH SÁCH SỐ CÂU ĐƯỢC PHÉP:"
        )

        question_numbers = []

        for section in (
            exam_structure[
                "sections"
            ]
        ):

            question_numbers.extend(
                section[
                    "questions"
                ]
            )

        lines.append(
            ", ".join(
                f"Câu {n}"
                for n in question_numbers
            )
        )

        lines.append("")

        lines.append(
            "QUY TẮC BẮT BUỘC:"
        )

        lines.append(
            "1. Không được tạo thêm câu ngoài danh sách trên."
        )

        lines.append(
            "2. Không được bỏ bớt câu trong danh sách trên."
        )

        lines.append(
            "3. Không được tự ý thay đổi số điểm."
        )

        lines.append(
            "4. Không được tự ý thay đổi dạng câu hỏi."
        )

        lines.append(
            "5. Số câu trong ma trận, đặc tả, đề "
            "và đáp án phải hoàn toàn giống nhau."
        )

        lines.append(
            "6. Các ý a), b), c), d) bên trong một câu "
            "không được tính thành câu hỏi mới."
        )

        lines.append(
            "7. Mỗi câu chính chỉ có một số thứ tự duy nhất."
        )

        lines.append(
            "8. Không được đánh số lại sau khi đã tạo đề."
        )

        return "\n".join(
            lines
        )

    # ============================================================
    # 5. HIỂN THỊ CẤU TRÚC ĐỀ
    # ============================================================
    def render_structure_summary(
        exam_structure
    ):

        st.markdown(
            "### 📊 Cấu trúc đề kiểm tra"
        )

        for section in (
            exam_structure[
                "sections"
            ]
        ):

            start = (
                section[
                    "start_question"
                ]
            )

            end = (
                section[
                    "end_question"
                ]
            )

            if start == end:

                question_range = (
                    f"Câu {start}"
                )

            else:

                question_range = (
                    f"Câu {start}–{end}"
                )

            st.write(
                f"**{section['name']}**: "
                f"{question_range} — "
                f"{section['count']} câu × "
                f"{section['points_each']:.2f} điểm = "
                f"{section['total_points']:.2f} điểm"
            )

        st.divider()

        st.write(
            f"**TỔNG: "
            f"{exam_structure['total_questions']} câu — "
            f"{exam_structure['total_points']:.2f} điểm**"
        )

    # ============================================================
    # 6. GIAO DIỆN CHÍNH
    # ============================================================
    st.markdown(
        "### 📝 Soạn thảo Ma trận, Đặc tả & Đề kiểm tra"
    )

    # ------------------------------------------------------------
    # THÔNG TIN CHUNG
    # ------------------------------------------------------------
    c1, c2, c3, c4, c5, c6 = st.columns(
        [1, 0.8, 1.2, 1, 2, 0.8]
    )

    mon_hoc = c1.selectbox(
        "Môn",
        [
            "Toán",
            "Ngữ văn",
            "Ngoại ngữ",
            "KHTN",
            "Lịch sử & Địa lý",
            "Tin học",
            "Khác"
        ],
        key="de_kt_mon_hoc"
    )

    lop = c2.selectbox(
        "Lớp",
        [
            "Lớp 6",
            "Lớp 7",
            "Lớp 8",
            "Lớp 9",
            "Lớp 10"
        ],
        index=2,
        key="de_kt_lop"
    )

    hinh_thuc = c3.selectbox(
        "Hình thức",
        [
            "Trắc nghiệm & Tự luận",
            "100% Trắc nghiệm",
            "100% Tự luận"
        ],
        key="de_kt_hinh_thuc"
    )

    thoi_gian = c4.selectbox(
        "Thời gian",
        [
            "15 phút",
            "45 phút",
            "60 phút",
            "90 phút",
            "120 phút"
        ],
        index=1,
        key="de_kt_thoi_gian"
    )

    ten_de = c5.text_input(
        "Tên bài kiểm tra",
        key="de_kt_ten_de"
    )

    with c6:

        st.markdown(
            "<div style='margin-top: 25px;'></div>",
            unsafe_allow_html=True
        )

        bam_sat = st.checkbox(
            "Bám sát đề cương",
            value=True,
            key="de_kt_bam_sat"
        )

    # ============================================================
    # 7. TẢI ĐỀ CƯƠNG
    # ============================================================
    file_de = st.file_uploader(
        "📚 Tải đề cương / tài liệu bám sát",
        type=[
            "pdf",
            "docx",
            "txt"
        ],
        key="de_kt_file_de_cuong"
    )

    if file_de:

        st.info(
            f"📄 Đã chọn: {file_de.name}"
        )

    # ============================================================
    # 8. CẤU HÌNH MỨC ĐỘ
    # ============================================================
    with st.expander(
        "⚙️ Cấu hình tỷ lệ mức độ nhận thức",
        expanded=True
    ):

        r1, r2, r3, r4 = st.columns(4)

        nb = r1.number_input(
            "Nhận biết (%)",
            min_value=0,
            max_value=100,
            value=40,
            step=5,
            key="de_kt_nb"
        )

        th = r2.number_input(
            "Thông hiểu (%)",
            min_value=0,
            max_value=100,
            value=30,
            step=5,
            key="de_kt_th"
        )

        vd = r3.number_input(
            "Vận dụng (%)",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            key="de_kt_vd"
        )

        vdc = r4.number_input(
            "Vận dụng cao (%)",
            min_value=0,
            max_value=100,
            value=10,
            step=5,
            key="de_kt_vdc"
        )

        total_percent = (
            nb
            + th
            + vd
            + vdc
        )

        if total_percent != 100:

            st.warning(
                f"⚠️ Tổng tỷ lệ hiện tại: "
                f"{total_percent}% "
                f"(phải bằng 100%)."
            )

    # ============================================================
    # 9. CẤU HÌNH CẤU TRÚC ĐỀ
    # ============================================================
    with st.expander(
        "📊 Cấu hình cấu trúc đề kiểm tra",
        expanded=True
    ):

        st.markdown(
            "#### PHẦN KHÁCH QUAN"
        )

        c1, c2, c3, c4 = st.columns(4)

        n_nlc = c1.number_input(
            "NLC - Số câu",
            min_value=0,
            max_value=100,
            value=10,
            step=1,
            key="de_kt_n_nlc"
        )

        d_nlc = c2.number_input(
            "NLC - Điểm/câu",
            min_value=0.0,
            max_value=10.0,
            value=0.25,
            step=0.25,
            key="de_kt_d_nlc"
        )

        n_ds = c3.number_input(
            "Đúng/Sai - Số câu",
            min_value=0,
            max_value=100,
            value=2,
            step=1,
            key="de_kt_n_ds"
        )

        d_ds = c4.number_input(
            "Đúng/Sai - Điểm/câu",
            min_value=0.0,
            max_value=10.0,
            value=0.25,
            step=0.25,
            key="de_kt_d_ds"
        )

        c5, c6, c7, c8 = st.columns(4)

        n_dk = c5.number_input(
            "Điền khuyết - Số câu",
            min_value=0,
            max_value=100,
            value=2,
            step=1,
            key="de_kt_n_dk"
        )

        d_dk = c6.number_input(
            "Điền khuyết - Điểm/câu",
            min_value=0.0,
            max_value=10.0,
            value=0.25,
            step=0.25,
            key="de_kt_d_dk"
        )

        n_ngan = c7.number_input(
            "Trả lời ngắn - Số câu",
            min_value=0,
            max_value=100,
            value=2,
            step=1,
            key="de_kt_n_ngan"
        )

        d_ngan = c8.number_input(
            "Trả lời ngắn - Điểm/câu",
            min_value=0.0,
            max_value=10.0,
            value=0.25,
            step=0.25,
            key="de_kt_d_ngan"
        )

        st.markdown(
            "#### PHẦN TỰ LUẬN"
        )

        num_tl = st.number_input(
            "Số câu tự luận",
            min_value=0,
            max_value=50,
            value=3,
            step=1,
            key="de_kt_num_tl"
        )

        tl_points = []

        if num_tl > 0:

            tl_cols = st.columns(
                min(
                    int(num_tl),
                    5
                )
            )

            for i in range(
                int(num_tl)
            ):

                col = tl_cols[
                    i % len(tl_cols)
                ]

                point = col.number_input(
                    f"Câu TL {i + 1} (điểm)",
                    min_value=0.0,
                    max_value=10.0,
                    value=2.0,
                    step=0.25,
                    key=f"de_kt_tl_{i}"
                )

                tl_points.append(
                    point
                )

        # --------------------------------------------------------
        # TẠO CẤU TRÚC ĐỀ
        # --------------------------------------------------------
        exam_structure = (
            build_exam_structure(
                n_nlc=n_nlc,
                d_nlc=d_nlc,
                n_ds=n_ds,
                d_ds=d_ds,
                n_dk=n_dk,
                d_dk=d_dk,
                n_ngan=n_ngan,
                d_ngan=d_ngan,
                tl_points=tl_points
            )
        )

        render_structure_summary(
            exam_structure
        )

    # ============================================================
    # 10. NÚT TẠO ĐỀ
    # ============================================================
    if st.button(
        "🚀 TẠO MA TRẬN & ĐỀ KIỂM TRA",
        type="primary",
        use_container_width=True
    ):

        # --------------------------------------------------------
        # KIỂM TRA TỶ LỆ
        # --------------------------------------------------------
        if total_percent != 100:

            st.error(
                "❌ Tổng tỷ lệ mức độ nhận thức "
                "phải bằng 100%."
            )

            st.stop()

        # --------------------------------------------------------
        # KIỂM TRA CẤU TRÚC
        # --------------------------------------------------------
        if (
            exam_structure[
                "total_questions"
            ] <= 0
        ):

            st.error(
                "❌ Đề phải có ít nhất một câu hỏi."
            )

            st.stop()

        if (
            exam_structure[
                "total_points"
            ] <= 0
        ):

            st.error(
                "❌ Tổng điểm đề phải lớn hơn 0."
            )

            st.stop()

        # --------------------------------------------------------
        # KIỂM TRA ĐỀ CƯƠNG
        # --------------------------------------------------------
        if bam_sat and not file_de:

            st.error(
                "❌ Thầy đã chọn "
                "'Bám sát đề cương' "
                "nhưng chưa tải tài liệu."
            )

            st.stop()

        # --------------------------------------------------------
        # ĐỌC ĐỀ CƯƠNG
        # --------------------------------------------------------
        with st.spinner(
            "📚 Đang đọc đề cương..."
        ):

            if bam_sat:

                raw_outline = (
                    extract_text_from_file(
                        file_de
                    )
                )

                outline_text = (
                    normalize_outline(
                        raw_outline
                    )
                )

                if not outline_text:

                    st.error(
                        "❌ Không đọc được nội dung "
                        "đề cương."
                    )

                    st.info(
                        "Nếu PDF là bản scan hình ảnh, "
                        "cần bổ sung OCR."
                    )

                    st.stop()

            else:

                outline_text = (
                    "Không sử dụng đề cương."
                )

        # ========================================================
        # TẠO HỢP ĐỒNG CẤU TRÚC
        # ========================================================
        structure_contract = (
            build_structure_contract(
                exam_structure
            )
        )

        # ========================================================
        # TẠO DANH SÁCH CÂU CHÍNH
        # ========================================================
        question_numbers = []

        for section in (
            exam_structure[
                "sections"
            ]
        ):

            question_numbers.extend(
                section[
                    "questions"
                ]
            )

        question_list = ", ".join(
            f"Câu {number}"
            for number in question_numbers
        )

        # ========================================================
        # PROMPT KIỂM SOÁT BÁM SÁT ĐỀ CƯƠNG
        # ========================================================
        scope_rules = f"""

============================================================
PHẠM VI KIẾN THỨC ĐƯỢC PHÉP
============================================================

Chỉ sử dụng kiến thức có căn cứ
trong đề cương/tài liệu dưới đây.

---------------- BẮT ĐẦU ĐỀ CƯƠNG ----------------

{outline_text}

---------------- KẾT THÚC ĐỀ CƯƠNG ----------------

QUY TẮC:

1. Không đưa nội dung ngoài đề cương.

2. Không tự ý mở rộng sang chủ đề khác.

3. Không tự ý thêm công thức ngoài phạm vi.

4. Có thể yêu cầu học sinh suy luận,
tính toán hoặc vận dụng kiến thức
đã có trong đề cương.

5. Mỗi câu hỏi phải xác định được
nội dung kiến thức tương ứng trong đề cương.

6. Ma trận, đặc tả, đề và đáp án
phải cùng bám một phạm vi kiến thức.
"""

        # ========================================================
        # QUY TẮC CÔNG THỨC
        # ========================================================
        formula_rules = """

============================================================
QUY TẮC TRÌNH BÀY CÔNG THỨC
============================================================

Nếu có công thức Toán/Vật lý/Hóa học:

- Công thức inline:
\\( ... \\)

- Công thức riêng:
\\[
...
\\]

Ví dụ:

\\[
v = \\frac{s}{t}
\\]

Không viết công thức dạng:

frac{s}{t}

sqrt{x}

Không tự ý thay đổi
ký hiệu, dữ kiện hoặc công thức
đã có trong đề cương.
"""

        # ========================================================
        # QUY TẮC MỨC ĐỘ
        # ========================================================
        level_rules = f"""

============================================================
TỶ LỆ MỨC ĐỘ NHẬN THỨC
============================================================

- Nhận biết: {nb}%
- Thông hiểu: {th}%
- Vận dụng: {vd}%
- Vận dụng cao: {vdc}%

Ma trận và đặc tả phải phân bố
theo các tỷ lệ trên trong phạm vi
số câu và điểm của đề.
"""

        # ========================================================
        # YÊU CẦU ĐẦU RA
        # ========================================================
        output_rules = f"""

============================================================
YÊU CẦU ĐẦU RA
============================================================

Tạo kết quả theo đúng thứ tự:

1. PHẠM VI KIẾN THỨC

2. MA TRẬN ĐỀ

3. BẢN ĐẶC TẢ

4. ĐỀ KIỂM TRA

5. ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM

6. BẢNG TỰ KIỂM TRA

============================================================
DANH SÁCH CÂU HỎI BẮT BUỘC
============================================================

{question_list}

Chỉ được sử dụng các số câu trên.

============================================================
YÊU CẦU ĐỒNG BỘ
============================================================

Ma trận phải khớp bản đặc tả.

Bản đặc tả phải khớp đề.

Đề phải khớp đáp án.

Số câu và điểm phải khớp
HỢP ĐỒNG CẤU TRÚC ĐỀ.

Các ý a), b), c), d)
bên trong một câu chỉ là ý thành phần,
không được tính thành câu hỏi mới.

============================================================
BẢNG TỰ KIỂM TRA
============================================================

[ ] Đủ toàn bộ các số câu được yêu cầu.

[ ] Không có câu ngoài danh sách.

[ ] Không có số câu bị trùng.

[ ] Tổng số câu đúng.

[ ] Tổng điểm đúng.

[ ] Mỗi dạng câu hỏi đúng số lượng.

[ ] Điểm từng dạng đúng.

[ ] Ma trận khớp đặc tả.

[ ] Đặc tả khớp đề.

[ ] Đề khớp đáp án.

[ ] Nội dung nằm trong phạm vi đề cương.
"""

        # ========================================================
        # PROMPT CUỐI
        # ========================================================
        final_prompt = f"""

Bạn là chuyên gia xây dựng
ma trận, bản đặc tả và đề kiểm tra
theo Chương trình GDPT 2018.

Môn học: {mon_hoc}

Lớp: {lop}

Tên bài kiểm tra: {ten_de}

Hình thức: {hinh_thuc}

Thời gian: {thoi_gian}

{structure_contract}

{scope_rules}

{formula_rules}

{level_rules}

{output_rules}

============================================================
NGUYÊN TẮC QUAN TRỌNG NHẤT
============================================================

HỢP ĐỒNG CẤU TRÚC ĐỀ là ràng buộc tuyệt đối.

Không được tự suy diễn lại số câu.

Không được tự ý thêm câu.

Không được tự ý bớt câu.

Không được tự ý thay đổi điểm.

Không được tự ý thay đổi dạng câu hỏi.

Không được biến ý nhỏ thành câu hỏi mới.

Trước khi trả kết quả,
hãy tự kiểm tra toàn bộ cấu trúc.

Chỉ trả về kết quả hoàn chỉnh.
"""

        # ========================================================
        # GỌI AI DUY NHẤT MỘT LẦN
        # ========================================================
        with st.spinner(
            "🤖 AI đang xây dựng ma trận, "
            "đặc tả, đề và đáp án..."
        ):

            try:

                result = (
                    ai_engine.generate_text(
                        final_prompt
                    )
                )

                if not result:

                    st.error(
                        "❌ AI trả về kết quả rỗng."
                    )

                    st.stop()

                # ------------------------------------------------
                # LƯU KẾT QUẢ
                # ------------------------------------------------
                st.session_state[
                    "de_kt_content"
                ] = result

                # ------------------------------------------------
                # LƯU CẤU HÌNH
                # ------------------------------------------------
                st.session_state[
                    "de_kt_config"
                ] = {

                    "mon_hoc":
                        mon_hoc,

                    "lop":
                        lop,

                    "ten_de":
                        ten_de,

                    "hinh_thuc":
                        hinh_thuc,

                    "thoi_gian":
                        thoi_gian,

                    "exam_structure":
                        exam_structure,

                    "total_questions":
                        exam_structure[
                            "total_questions"
                        ],

                    "total_points":
                        exam_structure[
                            "total_points"
                        ],

                    "file_name":
                        (
                            file_de.name
                            if file_de
                            else None
                        )
                }

                st.success(
                    "✅ Đã tạo xong đề kiểm tra."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"❌ Lỗi khi sinh đề: {e}"
                )

    # ============================================================
    # 11. HIỂN THỊ KẾT QUẢ
    # ============================================================
    if (
        "de_kt_content"
        in st.session_state
    ):

        st.divider()

        st.markdown(
            "## 📄 KẾT QUẢ ĐỀ KIỂM TRA"
        )

        config = (
            st.session_state.get(
                "de_kt_config",
                {}
            )
        )

        # --------------------------------------------------------
        # HIỂN THỊ CẤU TRÚC ĐÃ SINH
        # --------------------------------------------------------
        saved_structure = (
            config.get(
                "exam_structure"
            )
        )

        if saved_structure:

            with st.expander(
                "📊 Xem cấu trúc đề đã sử dụng",
                expanded=False
            ):

                render_structure_summary(
                    saved_structure
                )

        # --------------------------------------------------------
        # NÚT XÓA
        # --------------------------------------------------------
        if st.button(
            "🗑️ XÓA ĐỀ",
            key="de_kt_delete_result"
        ):

            st.session_state.pop(
                "de_kt_content",
                None
            )

            st.session_state.pop(
                "de_kt_config",
                None
            )

            st.rerun()

        # --------------------------------------------------------
        # HIỂN THỊ NỘI DUNG
        # --------------------------------------------------------
        st.markdown(
            st.session_state[
                "de_kt_content"
            ]
        )

        # ========================================================
        # XUẤT WORD
        # ========================================================
        try:

            root_path = str(
                Path(
                    __file__
                ).resolve().parents[2]
            )

            if (
                root_path
                not in sys.path
            ):

                sys.path.insert(
                    0,
                    root_path
                )

            from export.export_word import (
                WordExportEngine
            )

            word_bytes = (
                WordExportEngine.export_to_word(
                    {
                        "ai_generated_content":
                            st.session_state[
                                "de_kt_content"
                            ],

                        "is_de_kt":
                            True,

                        "title":
                            config.get(
                                "ten_de",
                                "Đề kiểm tra"
                            )
                    }
                )
            )

            st.download_button(
                "📥 TẢI FILE WORD",
                data=word_bytes,
                file_name="De_Thi.docx",
                use_container_width=True,
                key="de_kt_download_word"
            )

        except Exception as e:

            st.warning(
                f"⚠️ Lỗi xuất Word: {e}"
            )
