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
# VIEW CHÍNH VÀ ĐIỀU HƯỚNG GIAO DIỆN (TƯƠNG THÍCH EXAMAIENGINE)
# ============================================================
def render_xd_ma_tran_tu_de(ai_engine):
    """
    ai_engine: là một thực thể (instance) của lớp ExamAIEngine đã được khởi tạo
               ví dụ: ai_engine = ExamAIEngine(gemini_api_key="...")
    """
    st.markdown("### Sinh Ma trận & Đặc tả Đề kiểm tra")
    
    # Cấu hình thanh chọn thông tin đề bài từ giáo viên
    c1, c2 = st.columns(2)
    mon_hoc = c1.selectbox("Môn học", ["Khoa học Tự nhiên", "Toán học", "Ngữ văn", "Ngoại ngữ", "Khác"], key="mt_mon")
    lop = c2.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"], index=2, key="mt_lop")
    
    file_de = st.file_uploader("Tải lên tệp đề kiểm tra hiện tại", type=["pdf", "docx", "txt"], key="mt_file")
    
    if st.button("PHÂN TÍCH ĐỀ & LẬP MA TRẬN", type="primary", use_container_width=True):
        if not file_de:
            st.warning("Vui lòng đính kèm và tải lên file đề kiểm tra trước khi thực hiện phân tích.")
            return
            
        # Tìm đường dẫn file mẫu Word trong thư mục templates
        template_path = Path(__file__).resolve().parents[1] / "templates" / "ma_tran_dac_ta_mau.docx"
        if not template_path.exists():
            st.error(f"Hệ thống thiếu file cấu trúc mẫu tại đường dẫn: {template_path}")
            return
            
        # --- BẮT ĐẦU VÒNG XỬ LÝ AN TOÀN CHỐNG SẬP (CRASH-PROOF) ---
        try:
            with st.spinner("Hệ thống AI đang đọc dữ liệu tệp và phân tích cấu trúc đề..."):
                # 1. Đọc và chuẩn hóa nội dung văn bản đề bài từ File gửi lên
                raw_text = ExamTextExtractor.extract(file_de)
                exam_text = ExamTextExtractor.normalize(raw_text)
                
                if not exam_text:
                    st.error("Không thể đọc được dữ liệu chữ từ tệp tin này. Hãy thử kiểm tra lại tệp tin.")
                    return
                
                # 2. Xây dựng cấu trúc Exam Contract theo đúng định dạng nghiệp vụ yêu cầu (Trang 7)
                # Hệ thống yêu cầu: subject, grade, duration, total_score, question_blueprint
                # Lưu ý: Cần điều chỉnh blueprint động dựa theo đề, đoạn này tạo khung hợp đồng mẫu
                exam_contract = {
                    "subject": mon_hoc,
                    "grade": lop,
                    "duration": 90,  # Thời gian làm bài mặc định (phút)
                    "total_score": 10.0,  # Tổng điểm bắt buộc bằng 10.0 theo luật thẩm định hệ thống
                    "question_blueprint": [
                        # Khung blueprint mẫu để AI bám theo sinh và ánh xạ số câu
                        {"question_no": 1, "question_type": "NLC", "points": 0.25},
                        {"question_no": 2, "question_type": "NLC", "points": 0.25},
                        {"question_no": 3, "question_type": "TL", "points": 1.0}
                    ]
                }
                
                # 3. GỌI CHÍNH XÁC HÀM ĐIỀU PHỐI CỦA EXAMAIENGINE (Đã sửa lỗi attribute)
                # Truyền exam_contract và nội dung văn bản đề bài (đóng vai trò outline_text)
                validated_data = ai_engine.generate_exam(
                    exam_contract=exam_contract,
                    outline_text=exam_text,
                    additional_materials="Yêu cầu trích xuất cấu trúc ma trận và đặc tả từ đề bài trên."
                )
                
                # 4. Đổ dữ liệu đã được AI xử lý và hậu kiểm xong xuôi vào file Word template
                word_bytes = WordMatrixEngine.render_to_bytes(template_path, validated_data)
                
                # Lưu thông tin tạm vào session_state để hiển thị bản trực quan lên giao diện
                st.session_state["processed_matrix_data"] = validated_data
                st.session_state["download_word_bytes"] = word_bytes
                st.success("🎉 Phân tích đề bài và tự động thiết lập ma trận thành công!")

        except Exception as err:
            # Bọc giữ lỗi an toàn, hiển thị thông báo nghiệp vụ rõ ràng (ExamContractError, ExamOutputError,...)
            st.error(f"❌ Quá trình phân tích thất bại do lỗi hệ thống: {str(err)}")
            
    # --- PHẦN TỐI ƯU UX: HIỂN THỊ XEM TRƯỚC VÀ NÚT TẢI XUỐNG ---
    if "processed_matrix_data" in st.session_state:
        st.markdown("#### Đã phân tích - Xem trước bảng dữ liệu ma trận sơ bộ")
        
        # Nếu AI trả về cấu trúc gồm trường 'matrix', hiển thị trực quan lên Streamlit
        matrix_data = st.session_state["processed_matrix_data"].get("matrix", [])
        if matrix_data:
            df_preview = pd.DataFrame(matrix_data)
            st.dataframe(df_preview, use_container_width=True)
        else:
            st.info("Hệ thống đã lưu tệp dữ liệu, sẵn sàng tải xuống.")
        
        st.download_button(
            label="📥 TẢI XUỐNG FILE WORD MA TRẬN & ĐẶC TẢ (.DOCX)",
            data=st.session_state["download_word_bytes"],
            file_name=f"Ma_tran_Dac_ta_{mon_hoc}_{lop}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

