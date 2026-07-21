# -*- coding: utf-8 -*-

import streamlit as st
import json
import re
from pathlib import Path
from io import BytesIO


# ============================================================
# KIỂM TRA THƯ VIỆN TEMPLATE
# ============================================================

try:
    from docxtpl import DocxTemplate

except ImportError:

    st.error(
        "⚠️ Thư viện docxtpl chưa được cài đặt. "
        "Vui lòng chạy: pip install docxtpl"
    )


# ============================================================
# SERVICE 1: ĐỌC VÀ TRÍCH XUẤT VĂN BẢN
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
            # PDF
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

                return "\n".join(pages_text).strip()


            # ------------------------------------------------
            # DOCX
            # ------------------------------------------------

            elif file_name.endswith(".docx"):

                from docx import Document

                doc = Document(
                    BytesIO(file_bytes)
                )

                result = []

                # Đọc paragraph
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

                            row_data.append(cell_text)


                        row_text = " | ".join(
                            filter(None, row_data)
                        )

                        if row_text.strip():

                            result.append(row_text)


                return "\n".join(result).strip()


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


        # Giới hạn dữ liệu gửi AI
        words = clean_text.split(" ")

        return " ".join(
            words[:12000]
        )


# ============================================================
# SERVICE 2: XỬ LÝ JSON VÀ TÍNH TOÁN MA TRẬN
# ============================================================

class MatrixCalculator:


    @staticmethod
    def to_number(value, default=0):

        """
        Chuyển mọi dữ liệu số về dạng số an toàn.
        Ví dụ:
        '4' -> 4
        '4.0' -> 4.0
        None -> 0
        """

        if value is None:

            return default


        if isinstance(
            value,
            bool
        ):

            return int(value)


        if isinstance(
            value,
            (int, float)
        ):

            return value


        if isinstance(
            value,
            str
        ):

            value = value.strip()

            if not value:

                return default


            value = value.replace(
                ",",
                "."
            )


            try:

                number = float(value)

                if number.is_integer():

                    return int(number)

                return number


            except Exception:

                return default


        return default


    @staticmethod
    def parse_ai_json(result_text):

        """
        Bóc tách JSON an toàn từ kết quả AI.

        Hỗ trợ:
        1. JSON thuần
        2. ```json ... ```
        3. AI có thêm văn bản trước/sau JSON
        """

        if not result_text:

            raise json.JSONDecodeError(
                "AI không trả về dữ liệu",
                "",
                0
            )


        text = result_text.strip()


        # ----------------------------------------------------
        # Trường hợp 1: Có code block ```json
        # ----------------------------------------------------

        match = re.search(
            r"```json\s*(.*?)\s*```",
            text,
            re.IGNORECASE | re.DOTALL
        )


        if match:

            json_text = match.group(1).strip()


        else:

            # ------------------------------------------------
            # Trường hợp 2: Tìm JSON Object đầu tiên
            # ------------------------------------------------

            start = text.find("{")
            end = text.rfind("}")


            if start == -1 or end == -1:

                raise json.JSONDecodeError(
                    "Không tìm thấy JSON Object",
                    text,
                    0
                )


            json_text = text[start:end + 1]


        return json.loads(
            json_text
        )


    @staticmethod
    def calculate_totals(parsed_data):

        """
        Tính lại toàn bộ tổng bằng Python.

        AI chỉ phân loại câu hỏi.
        Python chịu trách nhiệm tính toán.
        """


        # ----------------------------------------------------
        # Tổng toàn bài
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

            "diem": 0.0,

            "phan_tram_tl": 0.0,
            "phan_tram_tn": 0.0
        }


        # ----------------------------------------------------
        # Tính lại từng dòng ma trận
        # ----------------------------------------------------

        for item in parsed_data.get(
            "ma_tran",
            []
        ):

            # --------------------------------------------
            # Chuẩn hóa các trường số
            # --------------------------------------------

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

                item[key] = MatrixCalculator.to_number(
                    item.get(key, 0)
                )


            # --------------------------------------------
            # Tính tổng câu tự luận
            # --------------------------------------------

            item["tong_cau_tl"] = (

                item["nb_tl"]
                + item["th_tl"]
                + item["vd_tl"]
                + item["vdc_tl"]

            )


            # --------------------------------------------
            # Tính tổng câu trắc nghiệm
            # --------------------------------------------

            item["tong_cau_tn"] = (

                item["nb_tn"]
                + item["th_tn"]
                + item["vd_tn"]
                + item["vdc_tn"]

            )


            # --------------------------------------------
            # Chuẩn hóa điểm
            # --------------------------------------------

            item["tong_diem_tl"] = round(

                MatrixCalculator.to_number(
                    item.get(
                        "tong_diem_tl",
                        0
                    )
                ),

                2
            )


            item["tong_diem_tn"] = round(

                MatrixCalculator.to_number(
                    item.get(
                        "tong_diem_tn",
                        0
                    )
                ),

                2
            )


            item["tong_diem"] = round(

                item["tong_diem_tl"]
                + item["tong_diem_tn"],

                2
            )


            # --------------------------------------------
            # Cộng vào tổng
            # --------------------------------------------

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

                total[key] += item[key]


            total["cau_tl"] += (
                item["tong_cau_tl"]
            )


            total["cau_tn"] += (
                item["tong_cau_tn"]
            )


            total["diem_tl"] += (
                item["tong_diem_tl"]
            )


            total["diem_tn"] += (
                item["tong_diem_tn"]
            )


        # ----------------------------------------------------
        # TỔNG ĐIỂM CUỐI CÙNG
        # ----------------------------------------------------

        total["diem"] = round(

            total["diem_tl"]
            + total["diem_tn"],

            2
        )


        # ----------------------------------------------------
        # TỶ LỆ ĐIỂM
        # ----------------------------------------------------

        if total["diem"] > 0:

            total["phan_tram_tl"] = round(

                total["diem_tl"]
                / total["diem"]
                * 100,

                1
            )


            total["phan_tram_tn"] = round(

                total["diem_tn"]
                / total["diem"]
                * 100,

                1
            )


        # ----------------------------------------------------
        # Gắn tổng vào dữ liệu
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


        doc.render(
            context_data
        )


        bio = BytesIO()


        doc.save(
            bio
        )


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
    # 1. CẤU HÌNH
    # ========================================================

    c1, c2 = st.columns(
        [1, 1]
    )


    mon_hoc = c1.selectbox(

        "Môn",

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
        # TÌM FILE TEMPLATE
        # ----------------------------------------------------

        template_path = (

            Path(__file__).resolve().parents[1]

            / "templates"

            / "ma_tran_dac_ta_mau.docx"

        )


        if not template_path.exists():

            st.error(

                f"❌ Không tìm thấy file mẫu tại:\n"
                f"{template_path}"

            )

            st.stop()


        with st.spinner(

            "⏳ AI đang phân tích từng câu hỏi..."

        ):


            # =================================================
            # ĐỌC ĐỀ
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

                st.error(

                    "❌ Không đọc được nội dung đề kiểm tra."

                )

                st.stop()


            # =================================================
            # JSON SCHEMA
            # =================================================

            json_schema = """

{
  "mon_hoc": "Tên môn học",
  "lop": "Lớp",
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

      "yccd": "- YCCĐ 1.\\n- YCCĐ 2.",

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

"""


            # =================================================
            # PROMPT
            # KHÔNG DÙNG F-STRING CHO JSON SCHEMA
            # =================================================

            prompt = (

                """

BẠN LÀ HỆ THỐNG XỬ LÝ DỮ LIỆU KHẢO THÍ.

NHIỆM VỤ:

Đọc toàn bộ đề kiểm tra được cung cấp.

Phân tích từng câu hỏi.

Xác định:

- Chủ đề
- Đơn vị kiến thức
- Hình thức trắc nghiệm hoặc tự luận
- Mức độ Nhận biết (NB)
- Mức độ Thông hiểu (TH)
- Mức độ Vận dụng (VD)
- Mức độ Vận dụng cao (VDC)

Sau đó trả về đúng một JSON Object.

TUYỆT ĐỐI KHÔNG:

- Không viết lời giải thích.
- Không viết Markdown.
- Không dùng ```json.
- Không thêm văn bản trước JSON.
- Không thêm văn bản sau JSON.

============================================================
THÔNG TIN ĐỀ
============================================================

MÔN HỌC:
"""
                + mon_hoc
                + """

LỚP:
"""
                + lop
                + """

============================================================
NỘI DUNG ĐỀ KIỂM TRA
============================================================

"""
                + exam_text
                + """

============================================================
QUY TẮC TÍNH ĐIỂM
============================================================

1. Phải phân loại từng câu hỏi.

2. Không được đếm một câu hỏi hai lần.

3. Tổng số câu trong ma_tran phải khớp với đề.

4. Tổng số câu trắc nghiệm phải khớp với số câu trắc nghiệm thực tế.

5. Tổng số câu tự luận phải khớp với số câu tự luận thực tế.

6. Tổng điểm phải khớp với tổng điểm của đề.

7. Nếu đề có điểm cho từng câu hoặc từng ý, phải căn cứ đúng vào đề.

8. Không được tự ý tạo thêm câu hỏi.

9. Không được bỏ sót câu hỏi.

10. Các trường số phải là NUMBER JSON thực sự.

Ví dụ đúng:

"nb_tn": 4

Ví dụ sai:

"nb_tn": "4"

11. Các trường điểm phải là số.

Ví dụ:

"tong_diem_tn": 4.0

12. Các tổng câu trong từng dòng ma_tran phải được tính đúng.

13. Các tổng điểm trong từng dòng ma_tran phải được tính đúng.

14. Các trường tổng cuối cùng sẽ được Python tính lại.

============================================================
CẤU TRÚC JSON BẮT BUỘC
============================================================

"""
                + json_schema
                + """

============================================================
ĐỀ KIỂM TRA CẦN PHÂN TÍCH
============================================================

"""
                + exam_text

            )


            # =================================================
            # FLOW 1: GỌI AI SINH JSON
            # =================================================

            try:

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

                parsed_data = (

                    MatrixCalculator.parse_ai_json(
                        result
                    )

                )


                if not isinstance(
                    parsed_data,
                    dict
                ):

                    raise ValueError(

                        "Dữ liệu AI trả về không phải JSON Object."

                    )


                # =================================================
                # KIỂM TRA CẤU TRÚC
                # =================================================

                if "ma_tran" not in parsed_data:

                    raise ValueError(

                        "JSON thiếu trường: ma_tran"

                    )


                if "dac_ta" not in parsed_data:

                    raise ValueError(

                        "JSON thiếu trường: dac_ta"

                    )


                if not isinstance(
                    parsed_data["ma_tran"],
                    list
                ):

                    raise ValueError(

                        "Trường ma_tran phải là một mảng."

                    )


                if not isinstance(
                    parsed_data["dac_ta"],
                    list
                ):

                    raise ValueError(

                        "Trường dac_ta phải là một mảng."

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

                tong = final_data.get(
                    "tong",
                    {}
                )


                tong_diem = (

                    tong.get(
                        "diem",
                        0
                    )

                )


                if tong_diem <= 0:

                    raise ValueError(

                        "Tổng điểm của đề phải lớn hơn 0."

                    )


                # =================================================
                # FLOW 4: XUẤT WORD TEMPLATE
                # =================================================

                word_bytes = (

                    DocxTemplateEngine.render_to_bytes(

                        template_path,

                        final_data

                    )

                )


                # =================================================
                # FLOW 5: LƯU SESSION STATE
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

                    "✅ Hệ thống đã phân tích, "
                    "tính toán và xuất Word thành công!"

                )


                st.rerun()


            # =================================================
            # LỖI JSON
            # =================================================

            except json.JSONDecodeError:

                st.error(

                    "❌ AI không trả về đúng định dạng JSON hợp lệ."

                )


            # =================================================
            # LỖI DỮ LIỆU
            # =================================================

            except ValueError as e:

                st.error(

                    f"❌ Dữ liệu không hợp lệ: {e}"

                )


            # =================================================
            # LỖI HỆ THỐNG
            # =================================================

            except Exception as e:

                st.error(

                    f"❌ Lỗi xử lý: {e}"

                )


    # ========================================================
    # 3. HIỂN THỊ KẾT QUẢ
    # ========================================================

    if "mt_word_bytes" in st.session_state:


        st.divider()


        st.markdown(

            "### 🎉 KẾT QUẢ XỬ LÝ"

        )


        c_btn1, c_btn2 = st.columns(
            2
        )


        safe_filename = (

            st.session_state.get(

                "mt_filename",

                "HoanChinh"

            )

        )


        # ----------------------------------------------------
        # DOWNLOAD WORD
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # XÓA KẾT QUẢ
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # HIỂN THỊ JSON
        # ----------------------------------------------------

        with st.expander(

            "👁️ KIỂM TRA DỮ LIỆU JSON "
            "(GIÁO VIÊN SOÁT LỖI AI)"

        ):


            st.json(

                st.session_state[
                    "mt_parsed_data"
                ]

            )
