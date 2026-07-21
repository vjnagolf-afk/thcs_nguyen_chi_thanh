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
    st.error(
        "⚠️ Thư viện docxtpl chưa được cài đặt. "
        "Vui lòng chạy lệnh: pip install docxtpl"
    )


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

            # -------------------------
            # ĐỌC PDF
            # -------------------------
            if file_name.endswith(".pdf"):

                from pypdf import PdfReader

                reader = PdfReader(BytesIO(file_bytes))
                pages_text = []

                for page in reader.pages:

                    extracted = page.extract_text()

                    if extracted:
                        pages_text.append(extracted.strip())

                return "\n".join(pages_text)

            # -------------------------
            # ĐỌC DOCX
            # -------------------------
            elif file_name.endswith(".docx"):

                from docx import Document

                doc = Document(BytesIO(file_bytes))

                result = []
                table_texts = set()

                # Đọc bảng
                for table in doc.tables:

                    for row in table.rows:

                        row_data = []

                        for cell in row.cells:

                            cell_text = cell.text.strip()

                            if cell_text:

                                for paragraph in cell.paragraphs:

                                    p_txt = paragraph.text.strip()

                                    if p_txt:
                                        table_texts.add(p_txt)

                            cell_text_clean = cell_text.replace(
                                "\n",
                                " "
                            )

                            row_data.append(cell_text_clean)

                        row_text = " | ".join(
                            filter(None, row_data)
                        )

                        if row_text:
                            result.append(row_text)

                # Đọc đoạn văn
                for paragraph in doc.paragraphs:

                    text = paragraph.text.strip()

                    if (
                        text
                        and text not in table_texts
                        and text not in result
                    ):
                        result.append(text)

                return "\n".join(result)

            # -------------------------
            # ĐỌC TXT
            # -------------------------
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

                raise ValueError(
                    "Không thể giải mã file TXT."
                )

        except Exception as e:

            raise RuntimeError(
                f"Lỗi đọc định dạng file "
                f"{file_name}: {str(e)}"
            )

        return ""

    # ========================================================
    # CHUẨN HÓA VĂN BẢN
    # ========================================================
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

        return " ".join(
            words[:12000]
        )


# ============================================================
# SERVICE 2: XỬ LÝ JSON VÀ TÍNH TOÁN
# ============================================================
class MatrixCalculator:

    # ========================================================
    # PHÂN TÍCH JSON AI
    # ========================================================
    @staticmethod
    def parse_ai_json(result_text):

        if not result_text:

            raise ValueError(
                "Hệ thống AI không trả về bất kỳ dữ liệu nào."
            )

        result_text = result_text.strip()

        # Trường hợp AI trả về ```json ... ```
        match = re.search(
            r"```json\s*(.*?)\s*```",
            result_text,
            re.DOTALL | re.IGNORECASE
        )

        if match:

            json_str = match.group(1).strip()

        else:

            json_str = result_text

        # Nếu còn văn bản bên ngoài JSON
        if not json_str.startswith("{"):

            start = json_str.find("{")
            end = json_str.rfind("}")

            if start != -1 and end != -1:

                json_str = json_str[
                    start:end + 1
                ]

        return json.loads(json_str)

    # ========================================================
    # CHUYỂN SỐ
    # ========================================================
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

                return (
                    float(value)
                    if "." in value
                    else int(value)
                )

            return value

        except Exception:

            return 0

    # ========================================================
    # CHUẨN BỊ DỮ LIỆU CHO TEMPLATE WORD
    # ========================================================
    @staticmethod
    def prepare_template_context(
        parsed_data,
        mon_hoc
    ):

        if not isinstance(
            parsed_data,
            dict
        ):

            raise ValueError(
                "Dữ liệu AI phản hồi "
                "không đúng cấu trúc."
            )

        ma_tran_raw = parsed_data.get(
            "ma_tran",
            []
        )

        dac_ta_raw = parsed_data.get(
            "dac_ta",
            []
        )

        # ====================================================
        # MA TRẬN
        # ====================================================
        ma_tran_data = []

        for item in ma_tran_raw:

            nb = MatrixCalculator.to_number(
                item.get("nb", 0)
            )

            th = MatrixCalculator.to_number(
                item.get("th", 0)
            )

            vd = MatrixCalculator.to_number(
                item.get("vd", 0)
            )

            vdc = MatrixCalculator.to_number(
                item.get("vdc", 0)
            )

            tong_so_cau = (
                nb
                + th
                + vd
                + vdc
            )

            tong_diem = MatrixCalculator.to_number(
                item.get("tong_diem", 0)
            )

            ma_tran_data.append({

                "chu_de": item.get(
                    "chu_de",
                    ""
                ),

                "noi_dung": item.get(
                    "noi_dung",
                    ""
                ),

                "nb": nb,

                "th": th,

                "vd": vd,

                "vdc": vdc,

                "tong_so_cau": tong_so_cau,

                "tong_diem": tong_diem

            })

        # ====================================================
        # ĐẶC TẢ
        # ====================================================
        dac_ta_data = []

        for item in dac_ta_raw:

            dac_ta_data.append({

                "stt": item.get(
                    "stt",
                    1
                ),

                "chu_de": item.get(
                    "chu_de",
                    ""
                ),

                "bai_hoc": item.get(
                    "bai_hoc",
                    item.get(
                        "noi_dung",
                        ""
                    )
                ),

                "yccd": item.get(
                    "yccd",
                    ""
                ),

                "tn_nb": MatrixCalculator.to_number(
                    item.get(
                        "tn_nb",
                        0
                    )
                ),

                "tn_hieu": MatrixCalculator.to_number(
                    item.get(
                        "tn_hieu",
                        0
                    )
                ),

                "tn_vd": MatrixCalculator.to_number(
                    item.get(
                        "tn_vd",
                        0
                    )
                ),

                "ds_nb": MatrixCalculator.to_number(
                    item.get(
                        "ds_nb",
                        0
                    )
                ),

                "ds_hieu": MatrixCalculator.to_number(
                    item.get(
                        "ds_hieu",
                        0
                    )
                ),

                "ds_vd": MatrixCalculator.to_number(
                    item.get(
                        "ds_vd",
                        0
                    )
                ),

                "tl_biet": MatrixCalculator.to_number(
                    item.get(
                        "tl_biet",
                        0
                    )
                ),

                "tl_hieu": MatrixCalculator.to_number(
                    item.get(
                        "tl_hieu",
                        0
                    )
                ),

                "tl_vd": MatrixCalculator.to_number(
                    item.get(
                        "tl_vd",
                        0
                    )
                ),

                "tong_diem": MatrixCalculator.to_number(
                    item.get(
                        "tong_diem",
                        0
                    )
                )

            })

        return {

            "MON_HOC": mon_hoc,

            "ma_tran_data": ma_tran_data,

            "dac_ta_data": dac_ta_data

        }


# ============================================================
# SERVICE 3: KẾT XUẤT WORD
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

        doc.save(bio)

        return bio.getvalue()


# ============================================================
# VIEW CHÍNH
# ============================================================
def render_xd_ma_tran_tu_de(ai_engine):

    st.markdown(
        "### 🧩 Sinh Ma trận & Đặc tả Đề kiểm tra "
        "(Chuẩn Template Word)"
    )

    # ========================================================
    # THÔNG TIN MÔN - LỚP
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

    # ========================================================
    # UPLOAD ĐỀ
    # ========================================================
    file_de = st.file_uploader(

        "Tải lên tệp đề kiểm tra hiện tại",

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

        "PHÂN TÍCH ĐỀ & LẬP MA TRẬN",

        type="primary",

        use_container_width=True

    ):

        if not file_de:

            st.warning(

                "Vui lòng đính kèm và tải lên "
                "file đề kiểm tra trước khi "
                "thực hiện phân tích."

            )

            return

        # ====================================================
        # XÁC ĐỊNH TEMPLATE
        # ====================================================
        template_path = (

            Path(__file__)
            .resolve()
            .parents[1]
            / "templates"
            / "ma_tran_dac_ta_mau.docx"

        )

        if not template_path.exists():

            st.error(

                "Hệ thống thiếu file cấu trúc mẫu tại đường dẫn: "
                f"{template_path}"

            )

            return

        try:

            with st.spinner(

                "Hệ thống AI đang đọc dữ liệu "
                "tệp và phân tích cấu trúc chi tiết..."

            ):

                # ====================================================
                # ĐỌC ĐỀ
                # ====================================================
                raw_text = ExamTextExtractor.extract(
                    file_de
                )

                exam_text = ExamTextExtractor.normalize(
                    raw_text
                )

                if not exam_text:

                    st.error(

                        "Không thể đọc được dữ liệu chữ "
                        "từ tệp tin này."

                    )

                    return

                # ====================================================
                # SCHEMA JSON
                # ====================================================
                json_schema = """
{
  "ma_tran": [
    {
      "chu_de": "Tên chủ đề",
      "noi_dung": "Tên bài học",
      "nb": 2,
      "th": 1,
      "vd": 1,
      "vdc": 0,
      "tong_diem": 1.5
    }
  ],
  "dac_ta": [
    {
      "stt": 1,
      "chu_de": "Tên chủ đề",
      "bai_hoc": "Tên bài học",
      "yccd": "- Nêu được định nghĩa...\\n- Giải thích được hiện tượng...",
      "tn_nb": 2,
      "tn_hieu": 1,
      "tn_vd": 0,
      "ds_nb": 0,
      "ds_hieu": 0,
      "ds_vd": 0,
      "tl_biet": 0,
      "tl_hieu": 0,
      "tl_vd": 1,
      "tong_diem": 1.5
    }
  ]
}
"""

                # ====================================================
                # PROMPT
                # ====================================================
                prompt = f"""

BẠN LÀ CHUYÊN GIA KHẢO THÍ
VÀ BIÊN SOẠN CHƯƠNG TRÌNH GDPT 2018.

NHIỆM VỤ:

Phân tích đề kiểm tra môn {mon_hoc},
lớp {lop} được cung cấp dưới đây.

Hãy bóc tách từng câu hỏi để xây dựng:

1. MA TRẬN ĐỀ KIỂM TRA.
2. BẢN ĐẶC TẢ ĐỀ KIỂM TRA.

==================================================
NGUYÊN TẮC PHÂN TÍCH
==================================================

- Chỉ sử dụng thông tin thực sự xuất hiện trong đề.
- Không tự ý thêm bài học hoặc kiến thức ngoài đề.
- Phải phân tích từng câu hỏi.
- Phải xác định đúng nội dung kiến thức.
- Phải xác định đúng mức độ nhận thức.
- Không được bỏ sót câu hỏi.
- Không được tạo dữ liệu không có căn cứ từ đề.

==================================================
YÊU CẦU MA TRẬN
==================================================

Các mức độ:

- nb: Nhận biết.
- th: Thông hiểu.
- vd: Vận dụng.
- vdc: Vận dụng cao.

Mỗi dòng tương ứng với một chủ đề hoặc nội dung
kiến thức thực sự xuất hiện trong đề.

tong_so_cau phải bằng:

nb + th + vd + vdc

tong_diem phải phản ánh tổng điểm của các câu
thuộc nội dung đó.

==================================================
YÊU CẦU BẢN ĐẶC TẢ
==================================================

Cột yccd phải viết cụ thể, rõ ràng,
bám sát nội dung câu hỏi trong đề.

Không viết chung chung.

Ví dụ:

- Nêu được...
- Trình bày được...
- Nhận biết được...
- Giải thích được...
- So sánh được...
- Phân tích được...
- Tính được...
- Vận dụng được kiến thức để giải quyết...

Mỗi yêu cầu cần đạt phải thể hiện đúng
mức độ nhận thức của câu hỏi.

==================================================
NỘI DUNG ĐỀ KIỂM TRA
==================================================

{exam_text}

==================================================
CẤU TRÚC JSON BẮT BUỘC
==================================================

Chỉ được trả về JSON thuần túy.

Không được có:

- Markdown.
- ```json.
- ```.
- Lời giải thích.
- Nhận xét.
- Văn bản bên ngoài JSON.

JSON phải đúng cấu trúc sau:

{json_schema}

==================================================
KIỂM TRA TRƯỚC KHI TRẢ KẾT QUẢ
==================================================

Trước khi trả về JSON, hãy tự kiểm tra:

1. JSON hợp lệ.
2. Có đầy đủ hai khóa:
   - ma_tran
   - dac_ta
3. Không bỏ sót câu hỏi.
4. Các số liệu là số.
5. tong_so_cau được tính đúng.
6. Nội dung bám sát đề.
7. Không thêm kiến thức ngoài đề.

CHỈ TRẢ VỀ JSON.
"""

                # ====================================================
                # GỌI AI
                # ====================================================
                result = ai_engine.generate_text(
                    prompt
                )

                # ====================================================
                # PHÂN TÍCH JSON
                # ====================================================
                parsed_json = MatrixCalculator.parse_ai_json(
                    result
                )

                # ====================================================
                # CHUẨN BỊ CONTEXT
                # ====================================================
                template_context = (

                    MatrixCalculator.prepare_template_context(

                        parsed_json,

                        mon_hoc

                    )

                )

                # ====================================================
                # KẾT XUẤT WORD
                # ====================================================
                word_bytes = (

                    DocxTemplateEngine.render_to_bytes(

                        template_path,

                        template_context

                    )

                )

                # ====================================================
                # LƯU SESSION STATE
                # ====================================================
                st.session_state[
                    "processed_matrix_data"
                ] = template_context

                st.session_state[
                    "download_word_bytes"
                ] = word_bytes

                st.session_state[
                    "mt_mon_hoc_file"
                ] = mon_hoc

                st.session_state[
                    "mt_lop_file"
                ] = lop

                st.success(

                    "🎉 Phân tích đề bài và thiết lập "
                    "file Word mẫu thành công!"

                )

        except json.JSONDecodeError:

            st.error(

                "❌ AI trả về dữ liệu không đúng "
                "chuẩn định dạng JSON. "
                "Vui lòng bấm thử lại."

            )

        except Exception as err:

            st.error(

                "❌ Quá trình phân tích thất bại: "
                f"{str(err)}"

            )

    # ========================================================
    # HIỂN THỊ KẾT QUẢ
    # ========================================================
    if "processed_matrix_data" in st.session_state:

        st.divider()

        st.markdown(
            "#### 👁️ Xem trước dữ liệu cấu trúc"
        )

        data = st.session_state[
            "processed_matrix_data"
        ]

        # ====================================================
        # BẢNG MA TRẬN
        # ====================================================
        if data.get("ma_tran_data"):

            st.markdown(
                "**1. Bảng Ma Trận**"
            )

            st.dataframe(

                pd.DataFrame(
                    data["ma_tran_data"]
                ),

                use_container_width=True

            )

        # ====================================================
        # BẢN ĐẶC TẢ
        # ====================================================
        if data.get("dac_ta_data"):

            st.markdown(
                "**2. Bản Đặc Tả**"
            )

            st.dataframe(

                pd.DataFrame(
                    data["dac_ta_data"]
                ),

                use_container_width=True

            )

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        # ====================================================
        # TÊN FILE
        # ====================================================
        safe_mon = st.session_state.get(

            "mt_mon_hoc_file",

            "Mon"

        )

        safe_lop = st.session_state.get(

            "mt_lop_file",

            "Lop"

        )

        # ====================================================
        # DOWNLOAD WORD
        # ====================================================
        st.download_button(

            label=(
                "📥 TẢI XUỐNG FILE WORD "
                "MA TRẬN & ĐẶC TẢ (.DOCX)"
            ),

            data=st.session_state[
                "download_word_bytes"
            ],

            file_name=(

                f"Ma_tran_Dac_ta_"
                f"{safe_mon}_"
                f"{safe_lop}.docx"

            ),

            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),

            use_container_width=True,

            type="primary"

        )
