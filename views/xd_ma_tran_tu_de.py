# -*- coding: utf-8 -*-

import streamlit as st
import json
import re
from pathlib import Path
from io import BytesIO


# ============================================================
# KIỂM TRA THƯ VIỆN TEMPLATE WORD
# ============================================================

try:
    from docxtpl import DocxTemplate

except ImportError:
    st.error(
        "⚠️ Chưa cài đặt thư viện docxtpl. "
        "Vui lòng chạy: pip install docxtpl"
    )


# ============================================================
# SERVICE 1: ĐỌC VÀ TRÍCH XUẤT VĂN BẢN ĐỀ KIỂM TRA
# ============================================================

class ExamTextExtractor:

    @staticmethod
    def extract(uploaded_file):

        if uploaded_file is None:
            return ""

        try:

            file_name = uploaded_file.name.lower()
            file_bytes = uploaded_file.getvalue()

            # ------------------------------------------------
            # ĐỌC PDF
            # ------------------------------------------------

            if file_name.endswith(".pdf"):

                from pypdf import PdfReader

                reader = PdfReader(BytesIO(file_bytes))

                pages_text = []

                for page in reader.pages:

                    extracted = page.extract_text()

                    if extracted:
                        pages_text.append(
                            extracted.strip()
                        )

                return "\n".join(pages_text)


            # ------------------------------------------------
            # ĐỌC DOCX
            # ------------------------------------------------

            elif file_name.endswith(".docx"):

                from docx import Document

                doc = Document(
                    BytesIO(file_bytes)
                )

                result = []

                # Đọc đoạn văn
                for paragraph in doc.paragraphs:

                    text = paragraph.text.strip()

                    if text:

                        result.append(text)


                # Đọc bảng
                for table in doc.tables:

                    for row in table.rows:

                        row_data = []

                        for cell in row.cells:

                            cell_text = (
                                cell.text
                                .strip()
                                .replace("\n", " ")
                            )

                            row_data.append(
                                cell_text
                            )

                        row_text = " | ".join(
                            item
                            for item in row_data
                            if item
                        )

                        if row_text:

                            result.append(
                                row_text
                            )


                return "\n".join(result)


            # ------------------------------------------------
            # ĐỌC TXT
            # ------------------------------------------------

            elif file_name.endswith(".txt"):

                for encoding in [
                    "utf-8",
                    "utf-8-sig",
                    "cp1258"
                ]:

                    try:

                        return file_bytes.decode(
                            encoding
                        ).strip()

                    except Exception:

                        continue


        except Exception as e:

            st.error(
                f"❌ Lỗi đọc file đề kiểm tra: {e}"
            )


        return ""


    # --------------------------------------------------------
    # CHUẨN HÓA VĂN BẢN
    # --------------------------------------------------------

    @staticmethod
    def normalize(text):

        if not text:

            return ""

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        words = text.split(" ")

        # Giới hạn nội dung tránh quá dài
        return " ".join(
            words[:6000]
        )


# ============================================================
# SERVICE 2: XỬ LÝ JSON VÀ TÍNH TOÁN MA TRẬN
# ============================================================

class MatrixCalculator:


    # --------------------------------------------------------
    # BÓC TÁCH JSON TỪ KẾT QUẢ AI
    # --------------------------------------------------------

    @staticmethod
    def parse_ai_json(result_text):

        if not result_text:

            raise ValueError(
                "AI không trả về dữ liệu."
            )


        result_text = result_text.strip()


        # Trường hợp AI trả về Markdown JSON
        json_match = re.search(
            r"```json\s*(.*?)\s*```",
            result_text,
            re.DOTALL | re.IGNORECASE
        )


        if json_match:

            json_str = json_match.group(1).strip()

        else:

            json_str = result_text


        # Tìm vùng JSON Object đầu tiên
        if not json_str.startswith("{"):

            start_index = json_str.find("{")

            end_index = json_str.rfind("}")

            if (
                start_index != -1
                and end_index != -1
                and end_index > start_index
            ):

                json_str = json_str[
                    start_index:
                    end_index + 1
                ]


        return json.loads(json_str)


    # --------------------------------------------------------
    # ÉP KIỂU SỐ AN TOÀN
    # --------------------------------------------------------

    @staticmethod
    def number(value, default=0):

        try:

            if value is None:

                return default

            if isinstance(value, str):

                value = value.replace(
                    ",",
                    "."
                )

            return float(value)

        except Exception:

            return default


    # --------------------------------------------------------
    # TÍNH LẠI TOÀN BỘ TỔNG
    # --------------------------------------------------------

    @staticmethod
    def calculate_totals(parsed_data):

        if not isinstance(
            parsed_data,
            dict
        ):

            raise ValueError(
                "Dữ liệu AI trả về phải là JSON Object."
            )


        if not isinstance(
            parsed_data.get(
                "ma_tran",
                []
            ),
            list
        ):

            raise ValueError(
                "Trường 'ma_tran' phải là một mảng JSON."
            )


        if not isinstance(
            parsed_data.get(
                "dac_ta",
                []
            ),
            list
        ):

            raise ValueError(
                "Trường 'dac_ta' phải là một mảng JSON."
            )


        # ----------------------------------------------------
        # TỔNG THEO MỨC ĐỘ NHẬN THỨC
        # ----------------------------------------------------

        total = {

            "nb_tl": 0,
            "nb_tn": 0,

            "th_tl": 0,
            "th_tn": 0,

            "vd_tl": 0,
            "vd_tn": 0,

            "vdc_tl": 0,
            "vdc_tn": 0,

            "cau_tl": 0,
            "cau_tn": 0,

            "diem_tl": 0.0,
            "diem_tn": 0.0,

            "diem": 0.0

        }


        # ----------------------------------------------------
        # CỘNG DỮ LIỆU TỪNG CHỦ ĐỀ
        # ----------------------------------------------------

        for item in parsed_data.get(
            "ma_tran",
            []
        ):

            # Số câu theo mức độ
            for key in [

                "nb_tl",
                "nb_tn",

                "th_tl",
                "th_tn",

                "vd_tl",
                "vd_tn",

                "vdc_tl",
                "vdc_tn"

            ]:

                total[key] += int(
                    MatrixCalculator.number(
                        item.get(
                            key,
                            0
                        )
                    )
                )


            # Tổng số câu tự luận
            total["cau_tl"] += int(
                MatrixCalculator.number(
                    item.get(
                        "tong_cau_tl",
                        0
                    )
                )
            )


            # Tổng số câu trắc nghiệm
            total["cau_tn"] += int(
                MatrixCalculator.number(
                    item.get(
                        "tong_cau_tn",
                        0
                    )
                )
            )


            # Tổng điểm tự luận
            total["diem_tl"] += MatrixCalculator.number(
                item.get(
                    "tong_diem_tl",
                    0
                )
            )


            # Tổng điểm trắc nghiệm
            total["diem_tn"] += MatrixCalculator.number(
                item.get(
                    "tong_diem_tn",
                    0
                )
            )


        # ----------------------------------------------------
        # TÍNH TỔNG ĐIỂM
        # ----------------------------------------------------

        total["diem"] = round(

            total["diem_tl"]
            +
            total["diem_tn"],

            2

        )


        # ----------------------------------------------------
        # TỶ LỆ ĐIỂM
        # ----------------------------------------------------

        if total["diem"] > 0:

            total["phan_tram_tl"] = round(

                total["diem_tl"]
                /
                total["diem"]
                *
                100,

                1

            )


            total["phan_tram_tn"] = round(

                total["diem_tn"]
                /
                total["diem"]
                *
                100,

                1

            )

        else:

            total["phan_tram_tl"] = 0

            total["phan_tram_tn"] = 0


        # ----------------------------------------------------
        # GẮN TỔNG VÀO JSON
        # ----------------------------------------------------

        parsed_data["tong"] = total


        return parsed_data


# ============================================================
# SERVICE 3: ĐỘNG CƠ XUẤT WORD
# ============================================================

class DocxTemplateEngine:


    @staticmethod
    def render_to_bytes(
        template_path,
        context_data
    ):

        doc = DocxTemplate(
            str(template_path)
        )


        # Đổ dữ liệu vào template
        doc.render(
            context_data
        )


        # Lưu vào bộ nhớ
        bio = BytesIO()


        doc.save(
            bio
        )


        return bio.getvalue()


# ============================================================
# SERVICE 4: KIỂM TRA CẤU TRÚC JSON
# ============================================================

class MatrixValidator:


    @staticmethod
    def validate(data):

        if not isinstance(
            data,
            dict
        ):

            raise ValueError(
                "JSON phải là một Object."
            )


        if "ma_tran" not in data:

            raise ValueError(
                "JSON thiếu trường 'ma_tran'."
            )


        if "dac_ta" not in data:

            raise ValueError(
                "JSON thiếu trường 'dac_ta'."
            )


        if not isinstance(
            data["ma_tran"],
            list
        ):

            raise ValueError(
                "'ma_tran' phải là một mảng."
            )


        if not isinstance(
            data["dac_ta"],
            list
        ):

            raise ValueError(
                "'dac_ta' phải là một mảng."
            )


        if len(
            data["ma_tran"]
        ) == 0:

            raise ValueError(
                "Ma trận không có dữ liệu."
            )


        if len(
            data["dac_ta"]
        ) == 0:

            raise ValueError(
                "Bản đặc tả không có dữ liệu."
            )


        return True


# ============================================================
# VIEW CHÍNH
# ============================================================

def render_xd_ma_tran_tu_de(
    ai_engine
):


    st.markdown(
        "### 🧩 Sinh Ma trận & Đặc tả từ Đề kiểm tra"
    )


    # ========================================================
    # 1. CẤU HÌNH
    # ========================================================

    c1, c2 = st.columns(
        2
    )


    mon_hoc = c1.selectbox(

        "Môn học",

        [

            "Khoa học Tự nhiên",
            "Toán học",
            "Ngữ văn",
            "Ngoại ngữ",
            "Khác"

        ],

        key="mt_mon"

    )


    lop = c2.selectbox(

        "Lớp",

        [

            "Lớp 6",
            "Lớp 7",
            "Lớp 8",
            "Lớp 9",
            "Lớp 10",
            "Lớp 11",
            "Lớp 12"

        ],

        index=2,

        key="mt_lop"

    )


    file_de = st.file_uploader(

        "📥 Tải lên đề kiểm tra",

        type=[

            "pdf",
            "docx",
            "txt"

        ],

        key="mt_file"

    )


    # ========================================================
    # 2. NÚT XỬ LÝ
    # ========================================================

    if st.button(

        "🔍 PHÂN TÍCH ĐỀ & LẬP MA TRẬN",

        type="primary",

        use_container_width=True

    ):


        if not file_de:

            st.warning(

                "⚠️ Vui lòng tải lên file đề kiểm tra."

            )

            st.stop()


        # ----------------------------------------------------
        # ĐƯỜNG DẪN TEMPLATE
        # ----------------------------------------------------

        template_path = (

            Path(__file__)
            .resolve()
            .parents[1]
            /
            "templates"
            /
            "ma_tran_dac_ta_mau.docx"

        )


        if not template_path.exists():

            st.error(

                f"❌ Không tìm thấy file mẫu Word:\n"
                f"{template_path}"

            )

            st.stop()


        # ----------------------------------------------------
        # ĐỌC ĐỀ
        # ----------------------------------------------------

        with st.spinner(

            "⏳ Đang đọc và phân tích đề kiểm tra..."

        ):


            raw_text = ExamTextExtractor.extract(

                file_de

            )


            exam_text = ExamTextExtractor.normalize(

                raw_text

            )


            if not exam_text:

                st.error(

                    "❌ Không đọc được nội dung đề kiểm tra."

                )

                st.stop()


            # =================================================
            # SCHEMA JSON
            # =================================================

            json_schema = {

                "mon_hoc": mon_hoc,

                "lop": lop,

                "ma_tran": [

                    {

                        "chu_de": "Tên chủ đề",

                        "noi_dung": "Đơn vị kiến thức",

                        "nb_tl": 0,

                        "nb_tn": 8,

                        "th_tl": 0,

                        "th_tn": 4,

                        "vd_tl": 0,

                        "vd_tn": 0,

                        "vdc_tl": 0,

                        "vdc_tn": 0,

                        "tong_cau_tl": 0,

                        "tong_cau_tn": 12,

                        "tong_diem_tl": 0.0,

                        "tong_diem_tn": 3.0,

                        "tong_diem": 3.0

                    }

                ],

                "dac_ta": [

                    {

                        "stt": 1,

                        "chu_de": "Tên chủ đề",

                        "noi_dung": "Đơn vị kiến thức",

                        "yccd": (

                            "- YCCĐ 1.\n"

                            "- YCCĐ 2."

                        ),

                        "cau_tn_nb": 8,

                        "cau_tn_th": 4,

                        "cau_tn_vd": 0,

                        "cau_tn_vdc": 0,

                        "cau_tl_nb": 0,

                        "cau_tl_th": 0,

                        "cau_tl_vd": 0,

                        "cau_tl_vdc": 0,

                        "ds_cau_hoi": (

                            "Câu 1, 2, 3 (NB); "

                            "Câu 4, 5 (TH)"

                        ),

                        "tong_diem_dt": 3.0

                    }

                ]

            }


            # =================================================
            # PROMPT
            # =================================================

            prompt = f"""

BẠN LÀ HỆ THỐNG XỬ LÝ DỮ LIỆU KHẢO THÍ.

NHIỆM VỤ:

Đọc toàn bộ đề kiểm tra được cung cấp.

Phân tích từng câu hỏi.

Xác định:

- Chủ đề
- Đơn vị kiến thức
- Mức độ nhận thức:
  + NB = Nhận biết
  + TH = Thông hiểu
  + VD = Vận dụng
  + VDC = Vận dụng cao

Phân biệt chính xác:

- TN = Trắc nghiệm
- TL = Tự luận

TÍNH ĐIỂM:

- Không được tự ý thay đổi điểm của đề.
- Phải căn cứ vào cấu trúc thực tế của đề.
- Tổng điểm các câu phải khớp với tổng điểm bài kiểm tra.
- Tổng điểm theo các mức độ phải khớp với tổng điểm toàn bài.
- Số câu trong ma trận phải khớp với số câu thực tế.
- Không được tự ý tạo thêm câu hỏi.
- Không được bỏ sót câu hỏi.

QUY TẮC QUAN TRỌNG:

1. Chỉ trả về JSON hợp lệ.
2. Không được trả về Markdown.
3. Không được trả về ```json.
4. Không được thêm lời giải thích.
5. Tất cả key phải đúng chính xác như schema.
6. Các giá trị số phải là số JSON thực sự.
7. Không dùng dấu phẩy thập phân.
8. Dùng dấu chấm cho số thập phân.
9. Không được để giá trị số dưới dạng chuỗi.

THÔNG TIN ĐỀ:

Môn học: {mon_hoc}

Lớp: {lop}


NỘI DUNG ĐỀ KIỂM TRA:

{exam_text}


SCHEMA JSON BẮT BUỘC:

{json.dumps(
    json_schema,
    ensure_ascii=False,
    indent=2
)}


HÃY PHÂN TÍCH VÀ TRẢ VỀ DUY NHẤT MỘT JSON OBJECT.
"""


            try:

                # =================================================
                # FLOW 1: GỌI AI
                # =================================================

                result = ai_engine.generate_text(

                    prompt

                )


                if not result or not result.strip():

                    raise ValueError(

                        "AI không trả về dữ liệu."

                    )


                # =================================================
                # FLOW 2: PARSE JSON
                # =================================================

                parsed_data = MatrixCalculator.parse_ai_json(

                    result

                )


                # =================================================
                # FLOW 3: KIỂM TRA JSON
                # =================================================

                MatrixValidator.validate(

                    parsed_data

                )


                # =================================================
                # FLOW 4: TÍNH LẠI TỔNG BẰNG PYTHON
                # =================================================

                final_data = MatrixCalculator.calculate_totals(

                    parsed_data

                )


                # =================================================
                # KIỂM TRA TỔNG ĐIỂM
                # =================================================

                tong = final_data.get(

                    "tong",

                    {}

                )


                if tong.get(

                    "diem",

                    0

                ) <= 0:

                    raise ValueError(

                        "Tổng điểm của đề phải lớn hơn 0."

                    )


                # =================================================
                # FLOW 5: XUẤT WORD TEMPLATE
                # =================================================

                word_bytes = (

                    DocxTemplateEngine.render_to_bytes(

                        template_path,

                        final_data

                    )

                )


                # =================================================
                # FLOW 6: LƯU SESSION STATE
                # =================================================

                st.session_state[

                    "mt_word_bytes"

                ] = word_bytes


                st.session_state[

                    "mt_filename"

                ] = Path(

                    file_de.name

                ).stem


                st.session_state[

                    "mt_parsed_data"

                ] = final_data


                st.success(

                    "✅ Đã phân tích, tính toán và "
                    "đổ dữ liệu vào file Word mẫu thành công!"

                )


                st.rerun()


            except json.JSONDecodeError as e:

                st.error(

                    "❌ AI không trả về JSON hợp lệ.\n\n"

                    f"Chi tiết: {e}"

                )


            except ValueError as e:

                st.error(

                    f"❌ Dữ liệu không hợp lệ: {e}"

                )


            except Exception as e:

                st.error(

                    f"❌ Lỗi xử lý: {e}"

                )


# ============================================================
# HIỂN THỊ KẾT QUẢ
# ============================================================

if (

    "mt_parsed_data"

    in st.session_state

):


    st.divider()


    st.success(

        "🎉 AI ĐÃ PHÂN TÍCH THÀNH CÔNG!"

    )


    data = st.session_state[

        "mt_parsed_data"

    ]


    # ========================================================
    # XEM TRƯỚC MA TRẬN
    # ========================================================

    st.markdown(

        "#### 📊 1. MA TRẬN"

    )


    for index, item in enumerate(

        data.get(

            "ma_tran",

            []

        ),

        start=1

    ):

        with st.expander(

            f"📌 Chủ đề {index}: "
            f"{item.get('chu_de', '')}"

        ):

            st.json(

                item

            )


    # ========================================================
    # XEM TRƯỚC ĐẶC TẢ
    # ========================================================

    st.markdown(

        "#### 📝 2. BẢN ĐẶC TẢ"

    )


    for index, item in enumerate(

        data.get(

            "dac_ta",

            []

        ),

        start=1

    ):

        with st.expander(

            f"📌 Mục {index}: "
            f"{item.get('chu_de', '')}"

        ):

            st.json(

                item

            )


    # ========================================================
    # TỔNG HỢP
    # ========================================================

    st.markdown(

        "#### 📈 3. TỔNG HỢP ĐIỂM"

    )


    tong = data.get(

        "tong",

        {}

    )


    col1, col2, col3, col4 = st.columns(

        4

    )


    col1.metric(

        "Câu TN",

        tong.get(

            "cau_tn",

            0

        )

    )


    col2.metric(

        "Câu TL",

        tong.get(

            "cau_tl",

            0

        )

    )


    col3.metric(

        "Điểm TN",

        tong.get(

            "diem_tn",

            0

        )

    )


    col4.metric(

        "Điểm TL",

        tong.get(

            "diem_tl",

            0

        )

    )


    # ========================================================
    # NÚT TẢI WORD
    # ========================================================

    st.divider()


    c_btn1, c_btn2 = st.columns(

        2

    )


    safe_filename = st.session_state.get(

        "mt_filename",

        "HoanChinh"

    )


    c_btn1.download_button(

        "📥 TẢI MA TRẬN & ĐẶC TẢ (.DOCX)",

        data=st.session_state[

            "mt_word_bytes"

        ],

        file_name=(

            f"MaTran_DacTa_"

            f"{safe_filename}.docx"

        ),

        use_container_width=True,

        type="primary"

    )


    # ========================================================
    # XÓA KẾT QUẢ
    # ========================================================

    if c_btn2.button(

        "🗑️ ĐÓNG & LÀM LẠI",

        use_container_width=True

    ):


        st.session_state.pop(

            "mt_word_bytes",

            None

        )


        st.session_state.pop(

            "mt_filename",

            None

        )


        st.session_state.pop(

            "mt_parsed_data",

            None

        )


        st.rerun()


    # ========================================================
    # RAW JSON
    # ========================================================

    with st.expander(

        "🛠️ XEM DỮ LIỆU JSON GỐC"

    ):

        st.json(

            data

        )
