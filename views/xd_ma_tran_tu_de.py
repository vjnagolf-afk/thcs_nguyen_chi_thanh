# -*- coding: utf-8 -*-
import streamlit as st
import json
import re
import pandas as pd
from pathlib import Path
from io import BytesIO

# ============================================================
# KIỂM TRA THƯ VIỆN DOCXTPL / PYTHON-DOCX
# ============================================================
try:
    from docxtpl import DocxTemplate
except ImportError:
    DocxTemplate = None

# ============================================================
# SERVICE 1: ĐỌC VÀ TRÍCH XUẤT VĂN BẢN (ĐÃ TỐI ƯU CHỐNG TRÙNG)
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
            # XỬ LÝ FILE PDF
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
            # XỬ LÝ FILE DOCX (Tối ưu loại bỏ trùng lặp phần tử bảng)
            # ------------------------------------------------
            elif file_name.endswith(".docx"):
                from docx import Document
                doc = Document(BytesIO(file_bytes))
                result = []
                
                # Trích xuất văn bản trong bảng và đánh dấu lại để tránh trùng
                table_texts = set()
                for table in doc.tables:
                    for row in table.rows:
                        row_data = []
                        for cell in row.cells:
                            cell_text = cell.text.strip()
                            if cell_text:
                                # Lưu từng đoạn nhỏ nội bộ của ô để lọc ở bước sau
                                for p in cell.paragraphs:
                                    p_txt = p.text.strip()
                                    if p_txt:
                                        table_texts.add(p_txt)
                            cell_text_clean = cell_text.replace("\n", " ")
                            row_data.append(cell_text_clean)
                        
                        row_text = " | ".join(filter(None, row_data))
                        if row_text:
                            result.append(row_text)
                
                # Đọc các đoạn văn thông thường (Chỉ lấy đoạn KHÔNG nằm trong bảng)
                for paragraph in doc.paragraphs:
                    text = paragraph.text.strip()
                    if text and (text not in table_texts) and (text not in result):
                        result.append(text)
                
                return "\n".join(result)
            
            # ------------------------------------------------
            # XỬ LÝ FILE TXT
            # ------------------------------------------------
            elif file_name.endswith(".txt"):
                for encoding in ["utf-8", "utf-8-sig", "cp1258"]:
                    try:
                        return file_bytes.decode(encoding).strip()
                    except Exception:
                        continue
                raise ValueError("Không thể giải mã file TXT với các bảng mã phổ biến.")
                
        except Exception as e:
            # Ghi nhận lỗi nội bộ và đẩy lên tầng trên xử lý, tránh nuốt lỗi
            raise RuntimeError(f"Lỗi đọc định dạng file {file_name}: {str(e)}")
        return ""

    @staticmethod
    def normalize(text):
        if not text:
            return ""
        clean_text = re.sub(r"\s+", " ", text).strip()
        words = clean_text.split(" ")
        # Giới hạn 12,000 từ để tránh prompt vượt quá ngữ cảnh (Token Limit)
        return " ".join(words[:12000])
# ============================================================
# SERVICE 2: XỬ LÝ JSON VÀ TÍNH TOÁN MA TRẬN
# ============================================================
class MatrixCalculator:
    # ============================================================
# SERVICE 3: ĐỘNG CƠ XUẤT FILE WORD
# ============================================================

class DocxTemplateEngine:

    @staticmethod
    def render_to_bytes(template_path, context_data):

        try:
            from docxtpl import DocxTemplate

            # Mở file Word mẫu
            doc = DocxTemplate(str(template_path))

            # Render dữ liệu vào template
            doc.render(context_data)

            # Lưu vào bộ nhớ RAM
            bio = BytesIO()
            doc.save(bio)

            return bio.getvalue()

        except Exception as e:
            raise RuntimeError(
                f"Lỗi khi kết xuất dữ liệu vào file Word: {str(e)}"
            )
    @staticmethod
    def parse_ai_json(result_text):
        if not result_text:
            raise ValueError("Hệ thống AI không trả về bất kỳ dữ liệu nào.")
        
        result_text = result_text.strip()
        # Xử lý bóc tách nếu AI vô tình bọc block code ```json ... ```
        match = re.search(r"```json\s*(.*?)\s*```", result_text, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1).strip()
        else:
            json_str = result_text
            
        # Cắt bỏ văn bản thừa nằm ngoài cặp dấu ngoặc nhọn { ... }
        if not json_str.startswith("{"):
            start = json_str.find("{")
            end = json_str.rfind("}")
            if start != -1 and end != -1:
                json_str = json_str[start:end + 1]
                
        return json.loads(json_str)

    @staticmethod
    def to_number(value):
        try:
            if value is None:
                return 0
            if isinstance(value, str):
                value = value.replace(",", ".")
                return float(value) if "." in value else int(value)
            return value
        except Exception:
            return 0

    @staticmethod
    def calculate_totals(parsed_data):
        if not isinstance(parsed_data, dict):
            raise ValueError("Dữ liệu AI phản hồi không đúng cấu trúc dạng cấu hình (JSON Object).")
        if "ma_tran" not in parsed_data:
            raise ValueError("Dữ liệu cấu trúc thiếu trường thông tin bắt buộc: 'ma_tran'.")
        if "dac_ta" not in parsed_data:
            raise ValueError("Dữ liệu cấu trúc thiếu trường thông tin bắt buộc: 'dac_ta'.")
            
        total = {
            "nb_tl": 0, "nb_tn": 0, "th_tl": 0, "th_tn": 0,
            "vd_tl": 0, "vd_tn": 0, "vdc_tl": 0, "vdc_tn": 0,
            "cau_tl": 0, "cau_tn": 0, "diem_tl": 0.0, "diem_tn": 0.0, "diem": 0.0
        }
        
        # Tính toán chuẩn hóa cho từng hàng trong bảng ma trận
        for item in parsed_data["ma_tran"]:
            tong_cau_tl = (MatrixCalculator.to_number(item.get("nb_tl", 0)) +
                           MatrixCalculator.to_number(item.get("th_tl", 0)) +
                           MatrixCalculator.to_number(item.get("vd_tl", 0)) +
                           MatrixCalculator.to_number(item.get("vdc_tl", 0)))
                           
            tong_cau_tn = (MatrixCalculator.to_number(item.get("nb_tn", 0)) +
                           MatrixCalculator.to_number(item.get("th_tn", 0)) +
                           MatrixCalculator.to_number(item.get("vd_tn", 0)) +
                           MatrixCalculator.to_number(item.get("vdc_tn", 0)))
            
            item["tong_cau_tl"] = tong_cau_tl
            item["tong_cau_tn"] = tong_cau_tn
            
            diem_tl = MatrixCalculator.to_number(item.get("tong_diem_tl", 0))
            diem_tn = MatrixCalculator.to_number(item.get("tong_diem_tn", 0))
            item["tong_diem_tl"] = diem_tl
            item["tong_diem_tn"] = diem_tn
            item["tong_diem"] = diem_tl + diem_tn
            
            # Tích lũy vào tổng số chung toàn đề
            for key in ["nb_tl", "nb_tn", "th_tl", "th_tn", "vd_tl", "vd_tn", "vdc_tl", "vdc_tn"]:
                total[key] += MatrixCalculator.to_number(item.get(key, 0))
                
            total["cau_tl"] += tong_cau_tl
            total["cau_tn"] += tong_cau_tn
            total["diem_tl"] += diem_tl
            total["diem_tn"] += diem_tn
            
        total["diem"] = total["diem_tl"] + total["diem_tn"]
        
        # Tính toán tỷ lệ phần trăm phân bố điểm số
        if total["diem"] > 0:
            total["phan_tram_tl"] = round(total["diem_tl"] / total["diem"] * 100, 1)
            total["phan_tram_tn"] = round(total["diem_tn"] / total["diem"] * 100, 1)
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
        cell.text = str(text if text is not None else "")

    @staticmethod
    def clear_table_body(table, start_row=1):
        while len(table.rows) > start_row:
            table._tbl.remove(table.rows[start_row]._tr)

    @staticmethod
    def render_to_bytes(template_path, data):
        from docx import Document
        doc = Document(str(template_path))
        if len(doc.tables) < 2:
            raise ValueError("Tệp tin template mẫu không hợp lệ. Yêu cầu tối thiểu có 2 bảng: Bảng 1 (Ma trận) và Bảng 2 (Đặc tả).")
            
        # --- XỬ LÝ ĐỔ DỮ LIỆU BẢNG 1: MA TRẬN ---
        table_matrix = doc.tables[0]
        ma_tran = data.get("ma_tran", [])
        MATRIX_DATA_START_ROW = 5  # Giữ lại 5 hàng tiêu đề mẫu
        WordMatrixEngine.clear_table_body(table_matrix, MATRIX_DATA_START_ROW)
        
        for item in ma_tran:
            row = table_matrix.add_row()
            values = [
                item.get("chu_de", ""), item.get("noi_dung", ""),
                item.get("nb_tl", 0), item.get("nb_tn", 0),
                item.get("th_tl", 0), item.get("th_tn", 0),
                item.get("vd_tl", 0), item.get("vd_tn", 0),
                item.get("vdc_tl", 0), item.get("vdc_tn", 0),
                item.get("tong_cau_tl", 0), item.get("tong_cau_tn", 0),
                item.get("tong_diem_tl", 0), item.get("tong_diem_tn", 0),
                item.get("tong_diem", 0)
            ]
            for idx, value in enumerate(values):
                if idx < len(row.cells):  # Phòng vệ nghiêm ngặt chống lỗi tràn chỉ mục cột
                    WordMatrixEngine.set_cell_text(row.cells[idx], value)
                    
        # --- XỬ LÝ ĐỔ DỮ LIỆU BẢNG 2: BẢN ĐẶC TẢ ---
        table_spec = doc.tables[1]
        dac_ta = data.get("dac_ta", [])
        SPEC_DATA_START_ROW = 4  # Giữ lại 4 hàng tiêu đề đặc tả mẫu
        WordMatrixEngine.clear_table_body(table_spec, SPEC_DATA_START_ROW)
        
        for item in dac_ta:
            row = table_spec.add_row()
            values = [
                item.get("stt", ""), item.get("chu_de", ""), item.get("noi_dung", ""), item.get("yccd", ""),
                item.get("cau_tn_nb", 0), item.get("cau_tn_th", 0), item.get("cau_tn_vd", 0), item.get("cau_tn_vdc", 0),
                item.get("cau_tl_nb", 0), item.get("cau_tl_th", 0), item.get("cau_tl_vd", 0), item.get("cau_tl_vdc", 0),
                item.get("ds_cau_hoi", ""), item.get("tong_diem_dt", 0)
            ]
            for idx, value in enumerate(values):
                if idx < len(row.cells):
                    WordMatrixEngine.set_cell_text(row.cells[idx], value)
                    
        # Xuất dữ liệu nhị phân ra bộ nhớ RAM
        bio = BytesIO()
        doc.save(bio)
        return bio.getvalue()
# ============================================================
# VIEW CHÍNH VÀ ĐIỀU HƯỚNG GIAO DIỆN
# ============================================================
def render_xd_ma_tran_tu_de(ai_engine):

    st.markdown("### 🧩 Sinh Ma trận & Đặc tả Đề kiểm tra")

    # ========================================================
    # 1. CẤU HÌNH ĐỀ
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
        "📥 Tải lên tệp đề kiểm tra hiện tại",
        type=["pdf", "docx", "txt"],
        key="mt_file"
    )

    # ========================================================
    # 2. NÚT PHÂN TÍCH
    # ========================================================
    if st.button(
        "🔍 PHÂN TÍCH ĐỀ & LẬP MA TRẬN",
        type="primary",
        use_container_width=True
    ):

        if not file_de:
            st.warning(
                "⚠️ Vui lòng đính kèm file đề kiểm tra trước khi phân tích."
            )
            return

        # ====================================================
        # 3. TÌM FILE WORD TEMPLATE
        # ====================================================
        template_path = (
            Path(__file__).resolve().parents[1]
            / "templates"
            / "ma_tran_dac_ta_mau.docx"
        )

        if not template_path.exists():
            st.error(
                f"❌ Không tìm thấy file mẫu Word:\n"
                f"{template_path}"
            )
            return

        # ====================================================
        # 4. TOÀN BỘ LUỒNG XỬ LÝ ĐƯỢC BỌC TRY-EXCEPT
        # ====================================================
        try:

            with st.spinner(
                "⏳ AI đang đọc đề, phân loại mức độ và xây dựng ma trận..."
            ):

                # ------------------------------------------------
                # FLOW 1: ĐỌC ĐỀ
                # ------------------------------------------------
                raw_text = ExamTextExtractor.extract(file_de)

                exam_text = ExamTextExtractor.normalize(
                    raw_text
                )

                if not exam_text:
                    raise ValueError(
                        "Không đọc được nội dung văn bản từ file đề."
                    )

                # ------------------------------------------------
                # FLOW 2: SCHEMA JSON
                # ------------------------------------------------
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

      "ds_cau_hoi": "Câu 1, Câu 2",

      "tong_diem_dt": 0.0
    }
  ]
}
"""

                # ------------------------------------------------
                # FLOW 3: PROMPT
                # ------------------------------------------------
                prompt = f"""
BẠN LÀ HỆ THỐNG PHÂN TÍCH KHẢO THÍ.

NHIỆM VỤ:
Đọc đề kiểm tra được cung cấp.
Phân tích từng câu hỏi.
Xác định:
- Chủ đề
- Đơn vị kiến thức
- Mức độ nhận thức:
  + NB = Nhận biết
  + TH = Thông hiểu
  + VD = Vận dụng
  + VDC = Vận dụng cao
- Hình thức:
  + TN = Trắc nghiệm
  + TL = Tự luận

Sau đó trả về DUY NHẤT một JSON hợp lệ.

THÔNG TIN ĐỀ:
Môn học: {mon_hoc}
Lớp: {lop}

NỘI DUNG ĐỀ:
{exam_text}

==================================================
QUY TẮC TÍNH ĐIỂM BẮT BUỘC
==================================================

1. Phải phân tích đúng số lượng câu thực tế trong đề.

2. Không được tự ý thêm câu hỏi không tồn tại.

3. Không được bỏ sót câu hỏi.

4. Mỗi câu hỏi chỉ được phân loại vào một:
   - NB
   - TH
   - VD
   - VDC

5. Tổng số câu trong ma_tran phải khớp với đề thực tế.

6. Tổng số câu trong dac_ta phải khớp với ma_tran.

7. Với từng chủ đề:

   tong_cau_tl =
   nb_tl + th_tl + vd_tl + vdc_tl

   tong_cau_tn =
   nb_tn + th_tn + vd_tn + vdc_tn

8. Điểm tự luận:

   tong_diem_tl =
   tổng điểm các câu tự luận thuộc chủ đề.

9. Điểm trắc nghiệm:

   tong_diem_tn =
   tổng điểm các câu trắc nghiệm thuộc chủ đề.

10. Tổng điểm:

   tong_diem =
   tong_diem_tl + tong_diem_tn

11. Tất cả giá trị số phải là số thực hoặc số nguyên hợp lệ.

12. Không được dùng dấu phẩy trong số thập phân.
    Ví dụ đúng: 0.25
    Ví dụ sai: 0,25

13. Không được trả về Markdown.

14. Không được trả về giải thích.

15. CHỈ TRẢ VỀ JSON.

==================================================
CẤU TRÚC JSON BẮT BUỘC
==================================================

{json_schema}

==================================================
ĐỀ KIỂM TRA CẦN PHÂN TÍCH
==================================================

{exam_text}
"""

                # =================================================
                # FLOW 4: GỌI AI
                # =================================================
                result = ai_engine.generate_text(prompt)

                if not result:
                    raise ValueError(
                        "AI không trả về dữ liệu."
                    )

                # =================================================
                # FLOW 5: PARSE JSON
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

                if "ma_tran" not in parsed_data:
                    raise ValueError(
                        "JSON thiếu trường ma_tran."
                    )

                if "dac_ta" not in parsed_data:
                    raise ValueError(
                        "JSON thiếu trường dac_ta."
                    )

                # =================================================
                # FLOW 6: TÍNH TOÁN LẠI BẰNG PYTHON
                # =================================================
                final_data = (
                    MatrixCalculator.calculate_totals(
                        parsed_data
                    )
                )

                # =================================================
                # FLOW 7: XUẤT WORD TEMPLATE
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
                # FLOW 8: LƯU SESSION STATE
                # =================================================
                st.session_state[
                    "processed_matrix_data"
                ] = final_data

                st.session_state[
                    "download_word_bytes"
                ] = word_bytes

                st.session_state[
                    "mt_mon_hoc_file"
                ] = mon_hoc

                st.session_state[
                    "mt_lop_file"
                ] = lop

                st.session_state[
                    "mt_filename"
                ] = Path(
                    file_de.name
                ).stem

                st.success(
                    "🎉 Phân tích đề và tạo dữ liệu ma trận thành công!"
                )

        except json.JSONDecodeError:

            st.error(
                "❌ AI trả về dữ liệu không đúng chuẩn JSON."
            )

        except ValueError as err:

            st.error(
                f"⚠️ Dữ liệu không hợp lệ: {err}"
            )

        except Exception as err:

            st.error(
                f"❌ Quá trình xử lý thất bại: {err}"
            )

    # ============================================================
    # 5. HIỂN THỊ KẾT QUẢ
    # ============================================================
    if "processed_matrix_data" in st.session_state:

        st.divider()

        st.markdown(
            "## 🎉 KẾT QUẢ PHÂN TÍCH"
        )

        data = (
            st.session_state[
                "processed_matrix_data"
            ]
        )

        # ========================================================
        # XEM TRƯỚC MA TRẬN
        # ========================================================
        st.markdown(
            "### 📊 1. MA TRẬN ĐỀ KIỂM TRA"
        )

        if data.get("ma_tran"):

            df_mt = pd.DataFrame(
                data["ma_tran"]
            )

            st.dataframe(
                df_mt,
                use_container_width=True,
                height=500
            )

        # ========================================================
        # XEM TRƯỚC ĐẶC TẢ
        # ========================================================
        st.markdown(
            "### 📝 2. BẢN ĐẶC TẢ"
        )

        if data.get("dac_ta"):

            df_dt = pd.DataFrame(
                data["dac_ta"]
            )

            st.dataframe(
                df_dt,
                use_container_width=True,
                height=600
            )

        # ========================================================
        # TỔNG HỢP
        # ========================================================
        if data.get("tong"):

            st.markdown(
                "### 🧮 3. TỔNG HỢP ĐIỂM"
            )

            tong = data["tong"]

            col1, col2, col3, col4 = st.columns(4)

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
        # NÚT TẢI FILE WORD
        # ========================================================
        st.divider()

        safe_mon = (
            st.session_state.get(
                "mt_mon_hoc_file",
                "Mon"
            )
        )

        safe_lop = (
            st.session_state.get(
                "mt_lop_file",
                "Lop"
            )
        )

        safe_filename = (
            st.session_state.get(
                "mt_filename",
                "HoanChinh"
            )
        )

        c_btn1, c_btn2 = st.columns(2)

        c_btn1.download_button(
            label=(
                "📥 TẢI FILE WORD "
                "MA TRẬN & ĐẶC TẢ"
            ),

            data=(
                st.session_state[
                    "download_word_bytes"
                ]
            ),

            file_name=(
                f"Ma_tran_Dac_ta_"
                f"{safe_mon}_"
                f"{safe_lop}_"
                f"{safe_filename}.docx"
            ),

            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
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

            for key in [
                "processed_matrix_data",
                "download_word_bytes",
                "mt_mon_hoc_file",
                "mt_lop_file",
                "mt_filename"
            ]:

                st.session_state.pop(
                    key,
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
