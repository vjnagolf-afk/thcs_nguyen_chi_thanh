# -*- coding: utf-8 -*-

import streamlit as st
import json
import re
import pandas as pd

from pathlib import Path
from io import BytesIO


# ============================================================
# KIỂM TRA THƯ VIỆN DOCXTPL
# ============================================================

try:
    from docxtpl import DocxTemplate

except ImportError:
    DocxTemplate = None


# ============================================================
# SERVICE 1: ĐỌC VÀ TRÍCH XUẤT VĂN BẢN
# ============================================================

class ExamTextExtractor:

    @staticmethod
    def extract(uploaded_file):

        if not uploaded_file:
            return ""

        try:

            file_name = uploaded_file.name.lower()
            file_bytes = uploaded_file.getvalue()

            # ------------------------------------------------
            # PDF
            # ------------------------------------------------

            if file_name.endswith(".pdf"):

                from pypdf import PdfReader

                reader = PdfReader(BytesIO(file_bytes))

                pages_text = []

                for page in reader.pages:

                    extracted = page.extract_text()

                    if extracted:
                        pages_text.append(extracted.strip())

                return "\n".join(pages_text)


            # ------------------------------------------------
            # DOCX
            # ------------------------------------------------

            elif file_name.endswith(".docx"):

                from docx import Document

                doc = Document(BytesIO(file_bytes))

                result = []

                seen_texts = set()


                # Đọc đoạn văn

                for paragraph in doc.paragraphs:

                    text = paragraph.text.strip()

                    if text and text not in seen_texts:

                        result.append(text)

                        seen_texts.add(text)


                # Đọc bảng

                for table in doc.tables:

                    for row in table.rows:

                        row_data = []

                        for cell in row.cells:

                            cell_text = cell.text.strip()

                            cell_text = cell_text.replace("\n", " ")

                            row_data.append(cell_text)


                        row_text = " | ".join(
                            filter(None, row_data)
                        )


                        if row_text and row_text not in seen_texts:

                            result.append(row_text)

                            seen_texts.add(row_text)


                return "\n".join(result)


            # ------------------------------------------------
            # TXT
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
                f"❌ Lỗi đọc file: {e}"
            )


        return ""


    @staticmethod
    def normalize(text):

        if not text:

            return ""


        clean_text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()


        words = clean_text.split(" ")


        # Giới hạn để tránh prompt quá dài

        return " ".join(
            words[:12000]
        )


# ============================================================
# SERVICE 2: XỬ LÝ JSON VÀ TÍNH TOÁN MA TRẬN
# ============================================================

class MatrixCalculator:


    @staticmethod
    def parse_ai_json(result_text):

        if not result_text:

            raise ValueError(
                "AI không trả về dữ liệu."
            )


        result_text = result_text.strip()


        # ----------------------------------------------------
        # Trường hợp AI trả về Markdown JSON
        # ----------------------------------------------------

        match = re.search(
            r"```json\s*(.*?)\s*```",
            result_text,
            re.DOTALL | re.IGNORECASE
        )


        if match:

            json_str = match.group(1).strip()


        else:

            json_str = result_text


        # ----------------------------------------------------
        # Nếu AI trả thêm văn bản ngoài JSON
        # ----------------------------------------------------

        if not json_str.startswith("{"):

            start = json_str.find("{")

            end = json_str.rfind("}")

            if start != -1 and end != -1:

                json_str = json_str[
                    start:end + 1
                ]


        return json.loads(json_str)


    @staticmethod
    def to_number(value):

        try:

            if value is None:

                return 0


            if isinstance(value, str):

                value = value.replace(
                    ",",
                    "."
                )


            return float(value)


        except Exception:

            return 0


    @staticmethod
    def calculate_totals(parsed_data):


        if not isinstance(
            parsed_data,
            dict
        ):

            raise ValueError(
                "Dữ liệu AI trả về không phải JSON Object."
            )


        if "ma_tran" not in parsed_data:

            raise ValueError(
                "JSON không có trường ma_tran."
            )


        if "dac_ta" not in parsed_data:

            raise ValueError(
                "JSON không có trường dac_ta."
            )


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


        # ====================================================
        # TÍNH TOÁN LẠI MA TRẬN
        # ====================================================

        for item in parsed_data["ma_tran"]:


            # -----------------------------------------------
            # Tính tổng số câu TỰ LUẬN
            # -----------------------------------------------

            tong_cau_tl = (

                MatrixCalculator.to_number(
                    item.get("nb_tl", 0)
                )

                +

                MatrixCalculator.to_number(
                    item.get("th_tl", 0)
                )

                +

                MatrixCalculator.to_number(
                    item.get("vd_tl", 0)
                )

                +

                MatrixCalculator.to_number(
                    item.get("vdc_tl", 0)
                )

            )


            # -----------------------------------------------
            # Tính tổng số câu TRẮC NGHIỆM
            # -----------------------------------------------

            tong_cau_tn = (

                MatrixCalculator.to_number(
                    item.get("nb_tn", 0)
                )

                +

                MatrixCalculator.to_number(
                    item.get("th_tn", 0)
                )

                +

                MatrixCalculator.to_number(
                    item.get("vd_tn", 0)
                )

                +

                MatrixCalculator.to_number(
                    item.get("vdc_tn", 0)
                )

            )


            # -----------------------------------------------
            # Đảm bảo số câu đúng
            # -----------------------------------------------

            item["tong_cau_tl"] = tong_cau_tl

            item["tong_cau_tn"] = tong_cau_tn


            # -----------------------------------------------
            # ĐIỂM
            # -----------------------------------------------

            diem_tl = MatrixCalculator.to_number(
                item.get(
                    "tong_diem_tl",
                    0
                )
            )


            diem_tn = MatrixCalculator.to_number(
                item.get(
                    "tong_diem_tn",
                    0
                )
            )


            item["tong_diem_tl"] = diem_tl

            item["tong_diem_tn"] = diem_tn

            item["tong_diem"] = (
                diem_tl + diem_tn
            )


            # -----------------------------------------------
            # Cộng tổng
            # -----------------------------------------------

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

                total[key] += MatrixCalculator.to_number(
                    item.get(key, 0)
                )


            total["cau_tl"] += tong_cau_tl

            total["cau_tn"] += tong_cau_tn

            total["diem_tl"] += diem_tl

            total["diem_tn"] += diem_tn


        # ====================================================
        # TỔNG ĐIỂM
        # ====================================================

        total["diem"] = (

            total["diem_tl"]

            +

            total["diem_tn"]

        )


        # ====================================================
        # TỶ LỆ ĐIỂM
        # ====================================================

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


        parsed_data["tong"] = total


        return parsed_data


# ============================================================
# SERVICE 3: ĐỘNG CƠ GHI DỮ LIỆU TRỰC TIẾP VÀO BẢNG WORD
# ============================================================

class WordMatrixEngine:

    @staticmethod
    def set_cell_text(cell, text):
        """
        Ghi nội dung vào ô Word nhưng giữ lại định dạng cơ bản của ô.
        """
        cell.text = str(text if text is not None else "")

    @staticmethod
    def clear_table_body(table, start_row=1):
        """
        Xóa các hàng dữ liệu cũ, giữ nguyên hàng tiêu đề.
        """
        while len(table.rows) > start_row:
            table._tbl.remove(table.rows[start_row]._tr)

    @staticmethod
    def render_to_bytes(template_path, data):

        from docx import Document

        doc = Document(str(template_path))

        if len(doc.tables) < 2:
            raise ValueError(
                "File mẫu phải có ít nhất 2 bảng: "
                "Bảng 1 - Ma trận; Bảng 2 - Đặc tả."
            )

        # =====================================================
        # BẢNG 1: MA TRẬN
        # =====================================================

        table_matrix = doc.tables[0]

        ma_tran = data.get("ma_tran", [])

        # Giữ nguyên các hàng tiêu đề của mẫu.
        # Nếu bảng mẫu có 5 hàng tiêu đề thì đổi thành 5.
        MATRIX_DATA_START_ROW = 5

        # Xóa các dòng dữ liệu cũ
        WordMatrixEngine.clear_table_body(
            table_matrix,
            MATRIX_DATA_START_ROW
        )

        for item in ma_tran:

            row = table_matrix.add_row()

            values = [
                item.get("chu_de", ""),
                item.get("noi_dung", ""),

                item.get("nb_tl", 0),
                item.get("nb_tn", 0),

                item.get("th_tl", 0),
                item.get("th_tn", 0),

                item.get("vd_tl", 0),
                item.get("vd_tn", 0),

                item.get("vdc_tl", 0),
                item.get("vdc_tn", 0),

                item.get("tong_cau_tl", 0),
                item.get("tong_cau_tn", 0),

                item.get("tong_diem_tl", 0),
                item.get("tong_diem_tn", 0),

                item.get("tong_diem", 0)
            ]

            for idx, value in enumerate(values):

                if idx < len(row.cells):

                    WordMatrixEngine.set_cell_text(
                        row.cells[idx],
                        value
                    )

        # =====================================================
        # BẢNG 2: BẢN ĐẶC TẢ
        # =====================================================

        table_spec = doc.tables[1]

        dac_ta = data.get("dac_ta", [])

        # Số dòng tiêu đề của bảng đặc tả
        SPEC_DATA_START_ROW = 4

        WordMatrixEngine.clear_table_body(
            table_spec,
            SPEC_DATA_START_ROW
        )

        for item in dac_ta:

            row = table_spec.add_row()

            values = [

                item.get("stt", ""),

                item.get("chu_de", ""),

                item.get("noi_dung", ""),

                item.get("yccd", ""),

                item.get("cau_tn_nb", 0),

                item.get("cau_tn_th", 0),

                item.get("cau_tn_vd", 0),

                item.get("cau_tn_vdc", 0),

                item.get("cau_tl_nb", 0),

                item.get("cau_tl_th", 0),

                item.get("cau_tl_vd", 0),

                item.get("cau_tl_vdc", 0),

                item.get("ds_cau_hoi", ""),

                item.get("tong_diem_dt", 0)

            ]

            for idx, value in enumerate(values):

                if idx < len(row.cells):

                    WordMatrixEngine.set_cell_text(
                        row.cells[idx],
                        value
                    )

        # =====================================================
        # LƯU FILE WORD
        # =====================================================

        bio = BytesIO()

        doc.save(bio)

        return bio.getvalue()

# ============================================================
# VIEW CHÍNH
# ============================================================

def render_xd_ma_tran_tu_de(
    ai_engine
):


    st.markdown(
        "### 🧩 Sinh Ma trận & Đặc tả"
    )


    # ========================================================
    # CẤU HÌNH
    # ========================================================

    c1, c2 = st.columns(2)


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
    # NÚT PHÂN TÍCH
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

            return


        # ----------------------------------------------------
        # TÌM TEMPLATE
        # ----------------------------------------------------

        template_path = (

            Path(__file__).resolve().parents[1]

            /

            "templates"

            /

            "ma_tran_dac_ta_mau.docx"

        )


        if not template_path.exists():

            st.error(

                f"❌ Không tìm thấy file mẫu:\n"
                f"{template_path}"

            )

            return


        with st.spinner(

            "⏳ AI đang phân tích đề..."

        ):


            try:


                # =================================================
                # 1. ĐỌC ĐỀ
                # =================================================

                raw_text = (

                    ExamTextExtractor.extract(
                        file_de
                    )

                )


                exam_text = (

                    ExamTextExtractor.normalize(
                        raw_text
                    )

                )


                if not exam_text:

                    raise ValueError(

                        "Không đọc được nội dung đề kiểm tra."

                    )


                # =================================================
                # 2. JSON SCHEMA
                # =================================================

                json_schema = {

                    "mon_hoc": mon_hoc,

                    "lop": lop,

                    "ma_tran": [

                        {

                            "chu_de": "Tên chủ đề",

                            "noi_dung": "Đơn vị kiến thức",

                            "nb_tl": 0,

                            "nb_tn": 0,

                            "th_tl": 0,

                            "th_tn": 0,

                            "vd_tl": 0,

                            "vd_tn": 0,

                            "vdc_tl": 0,

                            "vdc_tn": 0,

                            "tong_cau_tl": 0,

                            "tong_cau_tn": 0,

                            "tong_diem_tl": 0.0,

                            "tong_diem_tn": 0.0,

                            "tong_diem": 0.0

                        }

                    ],

                    "dac_ta": [

                        {

                            "stt": 1,

                            "chu_de": "Tên chủ đề",

                            "noi_dung": "Đơn vị kiến thức",

                            "yccd": "- YCCĐ 1.\n- YCCĐ 2.",

                            "cau_tn_nb": 0,

                            "cau_tn_th": 0,

                            "cau_tn_vd": 0,

                            "cau_tn_vdc": 0,

                            "cau_tl_nb": 0,

                            "cau_tl_th": 0,

                            "cau_tl_vd": 0,

                            "cau_tl_vdc": 0,

                            "ds_cau_hoi": "",

                            "tong_diem_dt": 0.0

                        }

                    ]

                }


                schema_text = json.dumps(

                    json_schema,

                    ensure_ascii=False,

                    indent=2

                )


                # =================================================
                # 3. PROMPT
                # =================================================

                prompt = f"""

BẠN LÀ HỆ THỐNG XỬ LÝ DỮ LIỆU KHẢO THÍ.

NHIỆM VỤ:

Phân tích ĐỀ KIỂM TRA đã có.

Phân loại từng câu hỏi theo:

- NB: Nhận biết
- TH: Thông hiểu
- VD: Vận dụng
- VDC: Vận dụng cao

Xác định chủ đề và đơn vị kiến thức.

Tính điểm chính xác.

CHỈ TRẢ VỀ DUY NHẤT JSON HỢP LỆ.

KHÔNG ĐƯỢC TRẢ VỀ MARKDOWN.

KHÔNG ĐƯỢC DÙNG ```json.

KHÔNG ĐƯỢC GIẢI THÍCH.

==================================================
THÔNG TIN ĐỀ
==================================================

MÔN: {mon_hoc}

LỚP: {lop}

==================================================
NỘI DUNG ĐỀ
==================================================

{exam_text}

==================================================
SCHEMA JSON BẮT BUỘC
==================================================

{schema_text}

==================================================
QUY TẮC TÍNH ĐIỂM
==================================================

1. Không được tự ý tạo thêm câu hỏi.

2. Mỗi câu hỏi trong đề chỉ được tính một lần.

3. Tổng số câu trong ma_tran phải khớp với đề.

4. Tổng điểm phải khớp với thang điểm của đề.

5. tong_cau_tl =
nb_tl + th_tl + vd_tl + vdc_tl.

6. tong_cau_tn =
nb_tn + th_tn + vd_tn + vdc_tn.

7. tong_diem =
tong_diem_tl + tong_diem_tn.

8. Không được làm tròn sai số điểm.

9. Chỉ trả về JSON hợp lệ.
"""


                # =================================================
                # FLOW 1: GỌI AI
                # =================================================

                result = ai_engine.generate_text(
                    prompt
                )


                if not result:

                    raise ValueError(

                        "AI không trả về dữ liệu."

                    )


                # =================================================
                # FLOW 2: PARSE JSON
                # =================================================

                parsed_data = (

                    MatrixCalculator.parse_ai_json(
                        result
                    )

                )


                # =================================================
                # KIỂM TRA CẤU TRÚC
                # =================================================

                if not isinstance(

                    parsed_data,

                    dict

                ):

                    raise ValueError(

                        "JSON AI trả về không phải Object."

                    )


                if not isinstance(

                    parsed_data.get(
                        "ma_tran"
                    ),

                    list

                ):

                    raise ValueError(

                        "ma_tran phải là một mảng."

                    )


                if not isinstance(

                    parsed_data.get(
                        "dac_ta"
                    ),

                    list

                ):

                    raise ValueError(

                        "dac_ta phải là một mảng."

                    )


                # =================================================
                # FLOW 3: TÍNH TOÁN BẰNG PYTHON
                # =================================================

                final_data = (

                    MatrixCalculator.calculate_totals(

                        parsed_data

                    )

                )


                # =================================================
                # KIỂM TRA TỔNG ĐIỂM
                # =================================================

                if (

                    final_data
                    .get(
                        "tong",
                        {}
                    )
                    .get(
                        "diem",
                        0
                    )

                    <= 0

                ):

                    raise ValueError(

                        "Tổng điểm của đề bằng 0."

                    )


                # =================================================
                # FLOW 4: XUẤT WORD
                # =================================================

                word_bytes = (

                    DocxTemplateEngine.render_to_bytes(

                        template_path,

                        final_data

                    )

                )


                if not word_bytes:

                    raise ValueError(

                        "Không tạo được file Word."

                    )


                # =================================================
                # LƯU SESSION STATE
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


                # KHÔNG st.rerun()
                # Kết quả sẽ hiển thị ngay bên dưới


                st.success(

                    "✅ Đã phân tích và tạo file Word thành công!"

                )


            except json.JSONDecodeError as e:


                st.error(

                    "❌ AI trả về JSON không hợp lệ."

                )


                with st.expander(

                    "Xem phản hồi thô của AI"

                ):

                    st.code(

                        result if "result" in locals()
                        else "Không có dữ liệu"

                    )


            except Exception as e:


                st.error(

                    f"❌ Lỗi xử lý: {e}"

                )


    # ========================================================
    # HIỂN THỊ KẾT QUẢ
    # ========================================================

    if "mt_parsed_data" not in st.session_state:

        return


    st.divider()


    st.markdown(

        "### 🎉 KẾT QUẢ XỬ LÝ"

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


    if data.get("ma_tran"):


        df_mt = pd.DataFrame(

            data["ma_tran"]

        )


        st.dataframe(

            df_mt,

            use_container_width=True,

            hide_index=True

        )


    else:


        st.warning(

            "Không có dữ liệu ma trận."

        )


    # ========================================================
    # XEM TRƯỚC ĐẶC TẢ
    # ========================================================

    st.markdown(

        "#### 📝 2. BẢN ĐẶC TẢ"

    )


    if data.get("dac_ta"):


        df_dt = pd.DataFrame(

            data["dac_ta"]

        )


        st.dataframe(

            df_dt,

            use_container_width=True,

            hide_index=True

        )


    else:


        st.warning(

            "Không có dữ liệu đặc tả."

        )


    # ========================================================
    # NÚT TẢI FILE
    # ========================================================

    st.divider()


    c1, c2 = st.columns(2)


    safe_filename = st.session_state.get(

        "mt_filename",

        "HoanChinh"

    )


    with c1:


        st.download_button(

            "📥 TẢI MA TRẬN & ĐẶC TẢ (.DOCX)",

            data=st.session_state[
                "mt_word_bytes"
            ],

            file_name=(

                f"MaTran_DacTa_"
                f"{safe_filename}.docx"

            ),

            mime=(

                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"

            ),

            use_container_width=True,

            type="primary"

        )


    with c2:


        if st.button(

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

        "🛠️ KIỂM TRA JSON"

    ):


        st.json(

            data

        )
