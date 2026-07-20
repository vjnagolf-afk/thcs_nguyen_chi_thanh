import streamlit as st
import sys
import os
from pathlib import Path
from string import Template

def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.pdf'):
            from pypdf import PdfReader
            return "\n".join([p.extract_text() for p in PdfReader(uploaded_file).pages if p.extract_text()])
        elif uploaded_file.name.endswith('.docx'):
            import docx
            return "\n".join([para.text for para in docx.Document(uploaded_file).paragraphs])
        elif uploaded_file.name.endswith('.txt'):
            return uploaded_file.read().decode("utf-8")
    except: return ""
    return ""

def load_prompt(filename):
    # Đường dẫn trỏ đúng thư mục prompts/ trong thư mục gốc
    root_path = Path(__file__).resolve().parents[2]
    file_path = root_path / "prompts" / filename
    if not file_path.exists():
        return f"Lỗi: Không tìm thấy file {filename} tại {file_path}"
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def render_xd_de_kt(ai_engine):

    import streamlit as st
    import sys
    from pathlib import Path
    from io import BytesIO

    # ============================================================
    # HÀM ĐỌC NỘI DUNG FILE
    # ============================================================
    def extract_text_from_file(uploaded_file):

        if uploaded_file is None:
            return ""

        try:

            file_name = uploaded_file.name.lower()

            # ====================================================
            # ĐỌC PDF
            # ====================================================
            if file_name.endswith(".pdf"):

                from pypdf import PdfReader

                # Đọc dữ liệu file vào bộ nhớ
                file_bytes = uploaded_file.getvalue()

                if not file_bytes:
                    raise ValueError(
                        "File PDF không có dữ liệu."
                    )

                pdf_stream = BytesIO(file_bytes)

                reader = PdfReader(pdf_stream)

                texts = []

                for page_number, page in enumerate(
                    reader.pages,
                    start=1
                ):

                    try:

                        text = page.extract_text()

                        if text and text.strip():

                            texts.append(
                                f"\n--- TRANG {page_number} ---\n"
                                f"{text.strip()}"
                            )

                    except Exception as page_error:

                        st.warning(
                            f"⚠️ Không đọc được trang "
                            f"{page_number}: {page_error}"
                        )

                result = "\n".join(texts)

                return result.strip()

            # ====================================================
            # ĐỌC DOCX
            # ====================================================
            elif file_name.endswith(".docx"):

                from docx import Document

                file_bytes = uploaded_file.getvalue()

                if not file_bytes:
                    raise ValueError(
                        "File DOCX không có dữ liệu."
                    )

                doc_stream = BytesIO(file_bytes)

                document = Document(doc_stream)

                texts = []

                # ------------------------------------------------
                # ĐỌC CÁC ĐOẠN VĂN
                # ------------------------------------------------
                for paragraph in document.paragraphs:

                    text = paragraph.text.strip()

                    if text:

                        texts.append(text)

                # ------------------------------------------------
                # ĐỌC CÁC BẢNG
                # ------------------------------------------------
                for table_index, table in enumerate(
                    document.tables,
                    start=1
                ):

                    texts.append(
                        f"\n--- BẢNG {table_index} ---"
                    )

                    for row in table.rows:

                        row_values = []

                        for cell in row.cells:

                            cell_text = cell.text.strip()

                            row_values.append(
                                cell_text
                            )

                        row_text = " | ".join(
                            row_values
                        )

                        if row_text.strip():

                            texts.append(
                                row_text
                            )

                result = "\n".join(texts)

                return result.strip()

            # ====================================================
            # ĐỌC TXT
            # ====================================================
            elif file_name.endswith(".txt"):

                file_bytes = uploaded_file.getvalue()

                if not file_bytes:
                    raise ValueError(
                        "File TXT không có dữ liệu."
                    )

                # Thử UTF-8 trước
                try:

                    result = file_bytes.decode(
                        "utf-8"
                    )

                except UnicodeDecodeError:

                    # Nếu không phải UTF-8,
                    # thử Windows-1258
                    try:

                        result = file_bytes.decode(
                            "cp1258"
                        )

                    except UnicodeDecodeError:

                        result = file_bytes.decode(
                            "latin-1"
                        )

                return result.strip()

            else:

                raise ValueError(
                    "Định dạng file không được hỗ trợ."
                )

        except Exception as e:

            st.error(
                f"❌ Lỗi đọc file "
                f"'{uploaded_file.name}': {e}"
            )

            return ""

    # ============================================================
    # CHUẨN HÓA NỘI DUNG ĐỀ CƯƠNG
    # ============================================================
    def normalize_outline(text):

        if not text:
            return ""

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if line:

                lines.append(line)

        result = "\n".join(lines)

        # Giới hạn để tránh prompt quá lớn
        MAX_CHARS = 60000

        if len(result) > MAX_CHARS:

            st.warning(
                f"⚠️ Đề cương có "
                f"{len(result):,} ký tự. "
                f"Hệ thống sử dụng "
                f"{MAX_CHARS:,} ký tự đầu tiên."
            )

            result = result[:MAX_CHARS]

        return result

    # ============================================================
    # GIAO DIỆN
    # ============================================================
    st.markdown(
        "### 📝 Soạn thảo Ma trận, Đặc tả & Đề KT "
        "(Chuẩn 5512)"
    )

    # ============================================================
    # THÔNG TIN CHUNG
    # ============================================================
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
    # TẢI ĐỀ CƯƠNG
    # ============================================================
    file_de = st.file_uploader(
        "📚 Tải đề cương / tài liệu làm căn cứ sinh đề",
        type=[
            "pdf",
            "docx",
            "txt"
        ],
        key="de_kt_file_de_cuong"
    )

    # ============================================================
    # HIỂN THỊ TRẠNG THÁI FILE
    # ============================================================
    if file_de is not None:

        st.info(
            f"📄 Đã tải lên: "
            f"**{file_de.name}** "
            f"({file_de.size:,} bytes)"
        )

    # ============================================================
    # CẤU HÌNH TỶ LỆ
    # ============================================================
    with st.expander(
        "⚙️ Cấu hình Tỷ lệ & Số câu",
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

        tong_ty_le = nb + th + vd + vdc

        if tong_ty_le != 100:

            st.warning(
                f"⚠️ Tổng tỷ lệ hiện tại: "
                f"{tong_ty_le}%. "
                f"Phải bằng 100%."
            )

        st.markdown(
            "#### 📌 Cấu trúc các dạng câu hỏi"
        )

        cols = st.columns(8)

        n_nlc = cols[0].number_input(
            "NLC",
            min_value=0,
            value=10
        )

        d_nlc = cols[1].number_input(
            "Đ.NLC",
            min_value=0.0,
            value=0.25,
            step=0.25
        )

        n_ds = cols[2].number_input(
            "Đ/S",
            min_value=0,
            value=2
        )

        d_ds = cols[3].number_input(
            "Đ.Đ/S",
            min_value=0.0,
            value=0.25,
            step=0.25
        )

        n_dk = cols[4].number_input(
            "Điền K",
            min_value=0,
            value=2
        )

        d_dk = cols[5].number_input(
            "Đ.DK",
            min_value=0.0,
            value=0.25,
            step=0.25
        )

        n_ngan = cols[6].number_input(
            "TL Ngắn",
            min_value=0,
            value=2
        )

        d_ngan = cols[7].number_input(
            "Đ.TLN",
            min_value=0.0,
            value=0.50,
            step=0.25
        )

        total_diem_tn = (
            n_nlc * d_nlc
            + n_ds * d_ds
            + n_dk * d_dk
            + n_ngan * d_ngan
        )

        tl_cols = st.columns(4)

        num_tl = tl_cols[0].number_input(
            "Số câu Tự luận",
            min_value=1,
            max_value=10,
            value=2
        )

        tl_points = []

        for i in range(num_tl):

            p = tl_cols[1].number_input(
                f"Câu {i + 1} (đ)",
                min_value=0.0,
                value=1.0,
                step=0.25,
                key=f"tl_p_{i}"
            )

            tl_points.append(p)

        total_diem_tl = sum(tl_points)

        total_diem = (
            total_diem_tn
            + total_diem_tl
        )

        tl_cols[2].metric(
            "Tổng điểm TN",
            f"{total_diem_tn:.2f}"
        )

        tl_cols[3].metric(
            "Tổng điểm TL",
            f"{total_diem_tl:.2f}"
        )

        st.metric(
            "TỔNG ĐIỂM",
            f"{total_diem:.2f} / 10"
        )

    # ============================================================
    # NÚT TẠO ĐỀ
    # ============================================================
    if st.button(
        "🚀 TẠO MA TRẬN & ĐỀ THI",
        type="primary",
        use_container_width=True
    ):

        # --------------------------------------------------------
        # KIỂM TRA TỶ LỆ
        # --------------------------------------------------------
        if tong_ty_le != 100:

            st.error(
                "❌ Tổng tỷ lệ mức độ phải bằng 100%."
            )

            st.stop()

        # --------------------------------------------------------
        # KIỂM TRA FILE
        # --------------------------------------------------------
        if bam_sat and file_de is None:

            st.error(
                "❌ Thầy đã chọn bám sát đề cương "
                "nhưng chưa tải file."
            )

            st.stop()

        # --------------------------------------------------------
        # KIỂM TRA TỔNG ĐIỂM
        # --------------------------------------------------------
        if abs(total_diem - 10.0) > 0.01:

            st.error(
                f"❌ Tổng điểm hiện tại là "
                f"{total_diem:.2f}/10."
            )

            st.stop()

        # ========================================================
        # ĐỌC ĐỀ CƯƠNG
        # ========================================================
        with st.spinner(
            "📚 Đang đọc nội dung đề cương..."
        ):

            if bam_sat and file_de:

                raw_outline = extract_text_from_file(
                    file_de
                )

                if not raw_outline:

                    st.error(
                        "❌ Không đọc được nội dung đề cương."
                    )

                    st.stop()

                outline_text = normalize_outline(
                    raw_outline
                )

                if not outline_text:

                    st.error(
                        "❌ Đề cương không có nội dung văn bản."
                    )

                    st.stop()

            else:

                outline_text = (
                    "Không sử dụng đề cương tải lên."
                )

        # ========================================================
        # PHẠM VI KIẾN THỨC ĐƯỢC PHÉP
        # ========================================================
        allowed_scope = f"""
============================================================
PHẠM VI KIẾN THỨC ĐƯỢC PHÉP SỬ DỤNG
============================================================

Đây là nguồn kiến thức chính thức duy nhất:

---------------- BẮT ĐẦU ĐỀ CƯƠNG ----------------

{outline_text}

----------------- KẾT THÚC ĐỀ CƯƠNG -----------------

QUY TẮC BẮT BUỘC:

1. Chỉ sử dụng kiến thức có trong đề cương.

2. Không được tự ý bổ sung kiến thức ngoài đề cương.

3. Không được mở rộng sang bài học khác.

4. Mỗi câu hỏi phải có căn cứ cụ thể trong đề cương.

5. Nếu không xác định được căn cứ trong đề cương,
   không được sử dụng nội dung đó.

6. Không được đưa kiến thức ngoài phạm vi
   chỉ vì kiến thức đó phù hợp với môn học.

7. Có thể yêu cầu học sinh suy luận hoặc tính toán
   dựa trên kiến thức trong đề cương.

8. Sau khi tạo đề phải tự kiểm tra từng câu hỏi.

============================================================
"""

        # ========================================================
        # CẤU HÌNH ĐỀ
        # ========================================================
        exam_configuration = f"""
============================================================
CẤU HÌNH ĐỀ KIỂM TRA
============================================================

Môn: {mon_hoc}

Lớp: {lop}

Tên đề: {ten_de}

Hình thức: {hinh_thuc}

Thời gian: {thoi_gian}

Tổng điểm: 10 điểm.

Mức độ:

- Nhận biết: {nb}%
- Thông hiểu: {th}%
- Vận dụng: {vd}%
- Vận dụng cao: {vdc}%

Cấu trúc:

- NLC: {n_nlc} câu × {d_nlc} điểm
- Đúng/Sai: {n_ds} câu × {d_ds} điểm
- Điền khuyết: {n_dk} câu × {d_dk} điểm
- Trả lời ngắn: {n_ngan} câu × {d_ngan} điểm
- Tự luận: {num_tl} câu
- Tổng điểm TN: {total_diem_tn:.2f}
- Tổng điểm TL: {total_diem_tl:.2f}

============================================================
"""

        # ========================================================
        # YÊU CẦU KIỂM SOÁT
        # ========================================================
        strict_instruction = """
============================================================
YÊU CẦU TẠO ĐỀ
============================================================

Hãy tạo đầy đủ:

1. PHẠM VI KIẾN THỨC ĐƯỢC SỬ DỤNG.

2. MA TRẬN ĐỀ.

3. BẢN ĐẶC TẢ.

4. ĐỀ KIỂM TRA.

5. ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM.

6. BẢNG TỰ KIỂM TRA.

------------------------------------------------------------
KIỂM SOÁT BẮT BUỘC
------------------------------------------------------------

Mỗi câu hỏi phải:

- Nằm trong phạm vi đề cương.
- Phù hợp môn và lớp.
- Đúng mức độ nhận thức.
- Đúng dạng câu hỏi.
- Đúng số điểm.

Không được:

- Tự ý thêm bài học.
- Tự ý thêm chủ đề.
- Tự ý thêm công thức ngoài đề cương.
- Tự ý thay đổi số câu.
- Tự ý thay đổi tổng điểm.

------------------------------------------------------------
TỰ KIỂM TRA TRƯỚC KHI TRẢ KẾT QUẢ
------------------------------------------------------------

Phải kiểm tra:

1. Có câu hỏi ngoài đề cương không?
2. Có đúng số câu không?
3. Có đúng tổng 10 điểm không?
4. Ma trận có khớp đặc tả không?
5. Đặc tả có khớp đề không?
6. Đề có khớp đáp án không?

Nếu phát hiện câu hỏi ngoài phạm vi,
phải thay thế câu hỏi đó trước khi trả kết quả.

------------------------------------------------------------
CẤU TRÚC KẾT QUẢ
------------------------------------------------------------

# PHẦN I. PHẠM VI KIẾN THỨC

# PHẦN II. MA TRẬN

# PHẦN III. BẢN ĐẶC TẢ

# PHẦN IV. ĐỀ KIỂM TRA

# PHẦN V. ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM

# PHẦN VI. BẢNG TỰ KIỂM TRA

============================================================
"""

        # ========================================================
        # PROMPT CUỐI
        # ========================================================
        final_prompt = f"""
{strict_instruction}

{exam_configuration}

{allowed_scope}

Hãy thực hiện nhiệm vụ ngay.
Ưu tiên tuyệt đối việc bám sát đề cương.
"""

        # ========================================================
        # GỌI AI ĐÚNG 1 LẦN
        # ========================================================
        with st.spinner(
            "🤖 AI đang tạo đề kiểm tra..."
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

                # LƯU KẾT QUẢ
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
                    "bam_sat": bam_sat,
                    "file_name": (
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
    # HIỂN THỊ KẾT QUẢ
    # ============================================================
    if "de_kt_content" in st.session_state:

        st.divider()

        st.markdown(
            "## 📄 KẾT QUẢ ĐỀ KIỂM TRA"
        )

        if st.button(
            "🗑️ XÓA ĐỀ"
        ):

            del st.session_state[
                "de_kt_content"
            ]

            if "de_kt_config" in st.session_state:

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
                Path(__file__).resolve().parents[2]
            )

            if root_path not in sys.path:

                sys.path.insert(
                    0,
                    root_path
                )

            from export.export_word import (
                WordExportEngine
            )

            config = st.session_state.get(
                "de_kt_config",
                {}
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
