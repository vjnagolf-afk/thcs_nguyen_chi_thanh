def render_xd_de_kt(ai_engine):

    import streamlit as st
    import sys
    import re
    from pathlib import Path
    from io import BytesIO

    # ============================================================
    # 1. HÀM ĐỌC FILE
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

                pdf_stream = BytesIO(file_bytes)

                reader = PdfReader(pdf_stream)

                pages_text = []

                for page in reader.pages:

                    try:

                        text = page.extract_text()

                        if text and text.strip():

                            pages_text.append(
                                text.strip()
                            )

                    except Exception:

                        continue

                return "\n\n".join(
                    pages_text
                ).strip()

            # ----------------------------------------------------
            # DOCX
            # ----------------------------------------------------
            elif file_name.endswith(".docx"):

                from docx import Document

                doc_stream = BytesIO(file_bytes)

                document = Document(
                    doc_stream
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

                            cell_text = (
                                cell.text
                                .strip()
                            )

                            cells.append(
                                cell_text
                            )

                        row_text = " | ".join(
                            cells
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

                try:

                    return file_bytes.decode(
                        "utf-8"
                    ).strip()

                except UnicodeDecodeError:

                    try:

                        return file_bytes.decode(
                            "cp1258"
                        ).strip()

                    except UnicodeDecodeError:

                        return file_bytes.decode(
                            "latin-1"
                        ).strip()

            return ""

        except Exception as e:

            st.error(
                f"❌ Lỗi đọc file: {e}"
            )

            return ""

    # ============================================================
    # 2. CHUẨN HÓA ĐỀ CƯƠNG
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

        # Giới hạn an toàn
        MAX_CHARS = 60000

        if len(result) > MAX_CHARS:

            result = result[
                :MAX_CHARS
            ]

        return result

    # ============================================================
    # 3. KIỂM TRA KẾT QUẢ AI
    # ============================================================
    def validate_generated_content(
        content
    ):

        if not content:

            return False, [
                "Kết quả AI rỗng."
            ]

        errors = []

        # --------------------------------------------------------
        # KIỂM TRA CÂU 1 → 19
        # --------------------------------------------------------
        question_numbers = re.findall(
            r"(?i)(?:^|\n)\s*(?:Câu|Cau)\s+(\d+)",
            content
        )

        numbers = []

        for number in question_numbers:

            try:

                number = int(
                    number
                )

                if number not in numbers:

                    numbers.append(
                        number
                    )

            except:

                pass

        # Không yêu cầu AI phải xuất hiện
        # đúng duy nhất 19 lần vì trong
        # ma trận/đặc tả có thể lặp mã câu.
        required_numbers = set(
            range(1, 20)
        )

        missing = sorted(
            required_numbers
            - set(numbers)
        )

        if missing:

            errors.append(
                "Thiếu câu: "
                + ", ".join(
                    f"Câu {n}"
                    for n in missing
                )
            )

        # --------------------------------------------------------
        # PHÁT HIỆN TỰ LUẬN SAI SỐ CÂU
        # --------------------------------------------------------
        tu_luan_match = re.search(
            r"(?is)"
            r"(?:PHẦN\s*II|PHAN\s*II)"
            r".{0,3000}?"
            r"(?:TỰ\s*LUẬN|TU\s*LUAN)"
            r".{0,5000}",
            content
        )

        if tu_luan_match:

            tu_luan_text = (
                tu_luan_match.group(
                    0
                )
            )

            # Các câu tự luận chính
            tl_numbers = set()

            for n in re.findall(
                r"(?i)(?:Câu|Cau)\s+"
                r"(17|18|19)\b",
                tu_luan_text
            ):

                tl_numbers.add(
                    int(n)
                )

            if tl_numbers != {
                17,
                18,
                19
            }:

                errors.append(
                    "Phần tự luận không đủ "
                    "Câu 17, Câu 18, Câu 19."
                )

        # --------------------------------------------------------
        # KIỂM TRA TỔNG ĐIỂM
        # --------------------------------------------------------
        if (
            "10,0 điểm" not in content
            and
            "10.0 điểm" not in content
            and
            "10 điểm" not in content
        ):

            errors.append(
                "Không phát hiện rõ tổng điểm 10."
            )

        if errors:

            return False, errors

        return True, []

    # ============================================================
    # 4. GIAO DIỆN
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
            "90 phút"
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
    # 5. TẢI ĐỀ CƯƠNG
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
            f"📄 Đã chọn: "
            f"{file_de.name}"
        )

    # ============================================================
    # 6. CẤU HÌNH MỨC ĐỘ
    # ============================================================
    with st.expander(
        "⚙️ Cấu hình mức độ nhận thức",
        expanded=True
    ):

        r1, r2, r3, r4 = st.columns(4)

        nb = r1.number_input(
            "Nhận biết (%)",
            min_value=0,
            max_value=100,
            value=40
        )

        th = r2.number_input(
            "Thông hiểu (%)",
            min_value=0,
            max_value=100,
            value=30
        )

        vd = r3.number_input(
            "Vận dụng (%)",
            min_value=0,
            max_value=100,
            value=20
        )

        vdc = r4.number_input(
            "Vận dụng cao (%)",
            min_value=0,
            max_value=100,
            value=10
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
    # 7. CẤU HÌNH CẤU TRÚC ĐỀ
    # ============================================================
    with st.expander(
        "📊 Cấu trúc đề kiểm tra",
        expanded=True
    ):

        st.markdown(
            """
            **PHẦN I. TRẮC NGHIỆM — 16 câu — 4,0 điểm**

            - Nhiều lựa chọn: 10 câu × 0,25 điểm
            - Đúng/Sai: 2 câu × 0,25 điểm
            - Điền khuyết: 2 câu × 0,25 điểm
            - Trả lời ngắn: 2 câu × 0,25 điểm

            **PHẦN II. TỰ LUẬN — 3 câu — 6,0 điểm**

            - Câu 17: 2,0 điểm
            - Câu 18: 2,0 điểm
            - Câu 19: 2,0 điểm

            **TỔNG: 19 CÂU — 10,0 ĐIỂM**
            """
        )

    # ============================================================
    # 8. NÚT TẠO ĐỀ
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
                "❌ Tổng tỷ lệ mức độ phải bằng 100%."
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
                        "văn bản từ đề cương."
                    )

                    st.info(
                        "Nếu PDF là bản scan hình ảnh, "
                        "cần bổ sung OCR."
                    )

                    st.stop()

            else:

                outline_text = (
                    "Không có đề cương."
                )

        # ========================================================
        # 9. HỢP ĐỒNG CẤU TRÚC
        # ========================================================
        structure_contract = """
============================================================
HỢP ĐỒNG CẤU TRÚC ĐỀ — BẮT BUỘC TUÂN THỦ
============================================================

TỔNG SỐ CÂU TOÀN ĐỀ: 19 CÂU
TỔNG ĐIỂM: 10,0 ĐIỂM

============================================================
PHẦN I. TRẮC NGHIỆM — 16 CÂU — 4,0 ĐIỂM
============================================================

A. NHIỀU LỰA CHỌN

Câu 1 đến Câu 10:
10 câu × 0,25 điểm = 2,50 điểm.

Mỗi câu có đúng 1 đáp án đúng.

------------------------------------------------------------

B. ĐÚNG / SAI

Câu 11 đến Câu 12:
2 câu × 0,25 điểm = 0,50 điểm.

Đây là 2 câu hỏi chính.

Các mệnh đề a), b), c), d)
chỉ là các ý/mệnh đề bên trong câu hỏi,
không được tính thành câu hỏi mới.

------------------------------------------------------------

C. ĐIỀN KHUYẾT

Câu 13 đến Câu 14:
2 câu × 0,25 điểm = 0,50 điểm.

------------------------------------------------------------

D. TRẢ LỜI NGẮN

Câu 15 đến Câu 16:
2 câu × 0,25 điểm = 0,50 điểm.

============================================================
PHẦN II. TỰ LUẬN — 3 CÂU — 6,0 ĐIỂM
============================================================

Câu 17: 2,0 điểm.

Câu 18: 2,0 điểm.

Câu 19: 2,0 điểm.

Các ý a), b), c) bên trong Câu 17, 18, 19
chỉ là các ý thành phần để chấm điểm.

KHÔNG ĐƯỢC tạo thêm Câu 20, Câu 21...
KHÔNG ĐƯỢC biến các ý a), b), c)
thành câu hỏi độc lập.

============================================================
DANH SÁCH SỐ CÂU DUY NHẤT
============================================================

Câu 1
Câu 2
Câu 3
Câu 4
Câu 5
Câu 6
Câu 7
Câu 8
Câu 9
Câu 10
Câu 11
Câu 12
Câu 13
Câu 14
Câu 15
Câu 16
Câu 17
Câu 18
Câu 19

Không được thiếu.
Không được thêm.
Không được đánh số lại.
============================================================
"""

        # ========================================================
        # 10. QUY TẮC CÔNG THỨC
        # ========================================================
        formula_rules = """

============================================================
QUY TẮC TRÌNH BÀY CÔNG THỨC TOÁN
============================================================

Đối với công thức Toán:

- Công thức inline dùng:
  \\( ... \\)

- Công thức riêng dùng:
  \\[
  ...
  \\]

Ví dụ:

\\(x^2 + 2x + 1\\)

\\[
x^2 + 2x + 1 = 0
\\]

Phân số:

\\[
\\frac{a}{b}
\\]

Căn:

\\[
\\sqrt{x}
\\]

Không dùng:

frac{a}{b}

sqrt{x}

Các công thức phải giữ nguyên ký hiệu toán học.
Không tự ý thay đổi dữ kiện hoặc công thức
có trong đề cương.
============================================================
"""

        # ========================================================
        # 11. QUY TẮC BÁM SÁT ĐỀ CƯƠNG
        # ========================================================
        scope_rules = f"""

============================================================
PHẠM VI KIẾN THỨC ĐƯỢC PHÉP
============================================================

CHỈ được sử dụng kiến thức trong tài liệu sau:

---------------- BẮT ĐẦU ĐỀ CƯƠNG ----------------

{outline_text}

---------------- KẾT THÚC ĐỀ CƯƠNG ----------------

QUY TẮC:

1. Không đưa kiến thức ngoài đề cương.

2. Không tự ý mở rộng sang bài học khác.

3. Không tự ý thêm công thức ngoài phạm vi.

4. Mọi câu hỏi phải có căn cứ trong đề cương.

5. Có thể yêu cầu học sinh suy luận,
   tính toán hoặc vận dụng kiến thức
   đã có trong đề cương.

6. Nếu một nội dung không có căn cứ
   trong đề cương thì không sử dụng.
============================================================
"""

        # ========================================================
        # 12. MỨC ĐỘ NHẬN THỨC
        # ========================================================
        level_rules = f"""

============================================================
TỶ LỆ MỨC ĐỘ NHẬN THỨC
============================================================

- Nhận biết: {nb}%
- Thông hiểu: {th}%
- Vận dụng: {vd}%
- Vận dụng cao: {vdc}%

Ma trận và đặc tả phải phản ánh đúng
các tỷ lệ này trong phạm vi cho phép
của tổng số câu và điểm.
============================================================
"""

        # ========================================================
        # 13. YÊU CẦU ĐẦU RA
        # ========================================================
        output_rules = """

============================================================
YÊU CẦU ĐẦU RA
============================================================

Tạo kết quả theo đúng thứ tự:

# PHẦN I. PHẠM VI KIẾN THỨC

Liệt kê các chủ đề/nội dung
được phép sử dụng từ đề cương.

------------------------------------------------------------

# PHẦN II. MA TRẬN ĐỀ

Ma trận phải thể hiện:

- Nội dung/chủ đề.
- Mức độ nhận thức.
- Số câu.
- Mã câu cụ thể.

Mã câu phải là:
C1, C2, ..., C19.

Không dùng mã câu ngoài C1 đến C19.

------------------------------------------------------------

# PHẦN III. BẢN ĐẶC TẢ

Mỗi yêu cầu cần đạt phải gắn với:

- Nội dung.
- Mức độ.
- Dạng câu hỏi.
- Mã câu cụ thể.

Mã câu trong đặc tả phải khớp với ma trận.

------------------------------------------------------------

# PHẦN IV. ĐỀ KIỂM TRA

Bắt buộc:

PHẦN I. TRẮC NGHIỆM

Câu 1 đến Câu 10:
Nhiều lựa chọn.

Câu 11 đến Câu 12:
Đúng/Sai.

Câu 13 đến Câu 14:
Điền khuyết.

Câu 15 đến Câu 16:
Trả lời ngắn.

PHẦN II. TỰ LUẬN

Câu 17: 2 điểm.

Câu 18: 2 điểm.

Câu 19: 2 điểm.

------------------------------------------------------------

# PHẦN V. ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM

Đáp án phải có:

Câu 1 → Câu 19.

Không được thiếu câu.

Điểm phải đúng:

Câu 1-16:
mỗi câu 0,25 điểm.

Câu 17:
2,0 điểm.

Câu 18:
2,0 điểm.

Câu 19:
2,0 điểm.

------------------------------------------------------------

# PHẦN VI. BẢNG TỰ KIỂM TRA

Bắt buộc xác nhận:

[✓] Có đủ Câu 1 đến Câu 19.

[✓] Không có Câu 20 trở lên.

[✓] Có đúng 16 câu phần trắc nghiệm.

[✓] Có đúng 3 câu tự luận.

[✓] Tổng điểm bằng 10,0.

[✓] Câu 17 = 2,0 điểm.

[✓] Câu 18 = 2,0 điểm.

[✓] Câu 19 = 2,0 điểm.

[✓] Ma trận khớp đặc tả.

[✓] Đặc tả khớp đề.

[✓] Đáp án khớp đề.

[✓] Không có câu ngoài phạm vi đề cương.

============================================================
"""

        # ========================================================
        # 14. PROMPT CUỐI
        # ========================================================
        final_prompt = f"""

Bạn là chuyên gia xây dựng ma trận,
bản đặc tả và đề kiểm tra.

Môn: {mon_hoc}

Lớp: {lop}

Tên bài kiểm tra: {ten_de}

Hình thức: {hinh_thuc}

Thời gian: {thoi_gian}

{structure_contract}

{formula_rules}

{scope_rules}

{level_rules}

{output_rules}

============================================================
YÊU CẦU QUAN TRỌNG NHẤT
============================================================

Không được tự suy diễn lại cấu trúc đề.

Không được tự tính lại số câu.

Không được thêm câu.

Không được bớt câu.

Không được đánh số lại.

Hãy coi HỢP ĐỒNG CẤU TRÚC ĐỀ
là ràng buộc tuyệt đối.

Trước khi trả kết quả,
hãy tự kiểm tra toàn bộ cấu trúc
theo BẢNG TỰ KIỂM TRA.

Chỉ trả về kết quả hoàn chỉnh.
"""

        # ========================================================
        # 15. GỌI AI DUY NHẤT 1 LẦN
        # ========================================================
        with st.spinner(
            "🤖 AI đang xây dựng ma trận, đặc tả và đề..."
        ):

            try:

                result = ai_engine.generate_text(
                    final_prompt
                )

                if not result:

                    st.error(
                        "❌ AI trả về kết quả rỗng."
                    )

                    st.stop()

                # ------------------------------------------------
                # KIỂM TRA CẤU TRÚC
                # ------------------------------------------------
                is_valid, errors = (
                    validate_generated_content(
                        result
                    )
                )

                if not is_valid:

                    st.warning(
                        "⚠️ AI đã trả kết quả "
                        "nhưng phát hiện vấn đề cấu trúc:"
                    )

                    for error in errors:

                        st.write(
                            f"- {error}"
                        )

                    st.info(
                        "Thầy có thể kiểm tra "
                        "nội dung trước khi xuất Word."
                    )

                # ------------------------------------------------
                # LƯU KẾT QUẢ
                # ------------------------------------------------
                st.session_state[
                    "de_kt_content"
                ] = result

                st.session_state[
                    "de_kt_config"
                ] = {

                    "mon_hoc": mon_hoc,

                    "lop": lop,

                    "ten_de": ten_de,

                    "hinh_thuc": hinh_thuc,

                    "thoi_gian": thoi_gian,

                    "total_questions": 19,

                    "total_points": 10.0,

                    "trac_nghiem_questions": 16,

                    "trac_nghiem_points": 4.0,

                    "tu_luan_questions": 3,

                    "tu_luan_points": 6.0,

                    "file_name": (
                        file_de.name
                        if file_de
                        else None
                    )
                }

                st.success(
                    "✅ Đã tạo xong kết quả."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"❌ Lỗi khi sinh đề: {e}"
                )

    # ============================================================
    # 16. HIỂN THỊ KẾT QUẢ
    # ============================================================
    if (
        "de_kt_content"
        in st.session_state
    ):

        st.divider()

        st.markdown(
            "## 📄 KẾT QUẢ"
        )

        col1, col2 = st.columns(
            [1, 5]
        )

        with col1:

            if st.button(
                "🗑️ XÓA ĐỀ"
            ):

                del st.session_state[
                    "de_kt_content"
                ]

                if (
                    "de_kt_config"
                    in st.session_state
                ):

                    del st.session_state[
                        "de_kt_config"
                    ]

                st.rerun()

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

            config = (
                st.session_state.get(
                    "de_kt_config",
                    {}
                )
            )

            word_bytes = (
                WordExportEngine.export_to_word(
                    {
                        "ai_generated_content":
                            st.session_state[
                                "de_kt_content"
                            ],

                        "is_de_kt": True,

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
                use_container_width=True
            )

        except Exception as e:

            st.warning(
                f"⚠️ Lỗi xuất Word: {e}"
            )
