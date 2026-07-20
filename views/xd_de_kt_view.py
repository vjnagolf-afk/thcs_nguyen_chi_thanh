# -*- coding: utf-8 -*-
import streamlit as st
import sys
from pathlib import Path
from io import BytesIO
import re

# ============================================================
# 1. HÀM ĐỌC NỘI DUNG ĐỀ CƯƠNG
# ============================================================
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        file_name = uploaded_file.name.lower()
        file_bytes = uploaded_file.getvalue()
        if not file_bytes:
            return ""

        # PDF
        if file_name.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(file_bytes))
            pages = []
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    pages.append(f"\n--- TRANG {page_number} ---\n{text.strip()}")
            return "\n\n".join(pages).strip()

        # DOCX
        elif file_name.endswith(".docx"):
            from docx import Document
            document = Document(BytesIO(file_bytes))
            contents = []
            for paragraph in document.paragraphs:
                text = paragraph.text.strip()
                if text:
                    contents.append(text)
            for table in document.tables:
                for row in table.rows:
                    row_data = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    row_text = " | ".join(row_data)
                    if row_text.strip():
                        contents.append(row_text)
            return "\n".join(contents).strip()

        # TXT
        elif file_name.endswith(".txt"):
            for encoding in ["utf-8", "utf-8-sig", "cp1258", "latin-1"]:
                try:
                    return file_bytes.decode(encoding).strip()
                except Exception:
                    continue
            return ""
    except Exception as e:
        st.error(f"❌ Lỗi đọc tài liệu: {e}")
        return ""
    return ""

# ============================================================
# 2. HÀM CHUẨN HÓA ĐỀ CƯƠNG
# ============================================================
def normalize_outline(text):
    if not text:
        return ""
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"\s+", " ", line)
        lines.append(line)
    result = "\n".join(lines)
    return result[:60000] # Giới hạn ký tự để tránh vượt token AI

# ============================================================
# 3. GIAO DIỆN CHÍNH
# ============================================================
def render_xd_de_kt(ai_engine):
    st.markdown("### 📝 Soạn thảo Ma trận, Đặc tả & Đề KT (Chuẩn 5512)")

    # ------------------------------------------------------------
    # THÔNG TIN CHUNG
    # ------------------------------------------------------------
    c1, c2, c3, c4, c5, c6 = st.columns([1, 0.8, 1.2, 1, 2, 0.8])

    mon_hoc = c1.selectbox(
        "Môn",
        [
            "Toán học", "Ngữ văn", "Ngoại ngữ", "Khoa học Tự nhiên", 
            "Lịch sử và Địa lý", "Lịch sử", "Địa lý", "Vật lý", "Hóa học", 
            "Sinh học", "Giáo dục công dân", "Giáo dục kinh tế và pháp luật", 
            "Tin học", "Công nghệ", "Giáo dục thể chất", 
            "Nghệ thuật (Âm nhạc, Mĩ thuật)", "Hoạt động trải nghiệm, hướng nghiệp", 
            "Nội dung giáo dục của địa phương", "Giáo dục quốc phòng và an ninh", "Khác"
        ],
        key="de_kt_mon_hoc"
    )

    lop = c2.selectbox(
        "Lớp",
        ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"],
        index=2,
        key="de_kt_lop"
    )

    hinh_thuc = c3.selectbox(
        "Hình thức",
        ["Trắc nghiệm & Tự luận", "100% Trắc nghiệm", "100% Tự luận"],
        key="de_kt_hinh_thuc"
    )

    thoi_gian = c4.selectbox(
        "Thời gian",
        ["15 phút", "45 phút", "60 phút", "90 phút", "120 phút"],
        index=3,
        key="de_kt_thoi_gian"
    )

    ten_de = c5.text_input("Tên bài kiểm tra", key="de_kt_ten_de")

    with c6:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        bam_sat = st.checkbox("Bám sát đề cương", value=True, key="de_kt_bam_sat")

    # ------------------------------------------------------------
    # UPLOAD ĐỀ CƯƠNG
    # ------------------------------------------------------------
    file_de = st.file_uploader(
        "📚 Tải đề cương / tài liệu làm căn cứ sinh đề",
        type=["pdf", "docx", "txt"],
        key="de_kt_file_de_cuong"
    )

    # ------------------------------------------------------------
    # CẤU HÌNH TỶ LỆ & CẤU TRÚC ĐỀ
    # ------------------------------------------------------------
    with st.expander("⚙️ Cấu hình Tỷ lệ & Số câu", expanded=True):
        r1, r2, r3, r4 = st.columns(4)
        nb = r1.number_input("Nhận biết (%)", min_value=0, max_value=100, value=40, step=5, key="de_kt_nb")
        th = r2.number_input("Thông hiểu (%)", min_value=0, max_value=100, value=30, step=5, key="de_kt_th")
        vd = r3.number_input("Vận dụng (%)", min_value=0, max_value=100, value=20, step=5, key="de_kt_vd")
        vdc = r4.number_input("Vận dụng cao (%)", min_value=0, max_value=100, value=10, step=5, key="de_kt_vdc")

        tong_ty_le = nb + th + vd + vdc
        if tong_ty_le != 100:
            st.warning(f"⚠️ Tổng tỷ lệ mức độ hiện tại là {tong_ty_le}%. Phải bằng 100%.")

        st.markdown("#### 📌 Cấu trúc các dạng câu hỏi")
        cols = st.columns(8)
        n_nlc = cols[0].number_input("NLC", min_value=0, value=10, key="de_kt_n_nlc")
        d_nlc = cols[1].number_input("Đ.NLC", min_value=0.0, value=0.25, step=0.25, key="de_kt_d_nlc")
        n_ds = cols[2].number_input("Đ/S", min_value=0, value=2, key="de_kt_n_ds")
        d_ds = cols[3].number_input("Đ.Đ/S", min_value=0.0, value=0.25, step=0.25, key="de_kt_d_ds")
        n_dk = cols[4].number_input("Điền K", min_value=0, value=2, key="de_kt_n_dk")
        d_dk = cols[5].number_input("Đ.DK", min_value=0.0, value=0.25, step=0.25, key="de_kt_d_dk")
        n_ngan = cols[6].number_input("TL Ngắn", min_value=0, value=2, key="de_kt_n_ngan")
        d_ngan = cols[7].number_input("Đ.TLN", min_value=0.0, value=0.50, step=0.25, key="de_kt_d_ngan")

        total_diem_tn = (n_nlc * d_nlc) + (n_ds * d_ds) + (n_dk * d_dk) + (n_ngan * d_ngan)

        st.markdown("#### PHẦN TỰ LUẬN")
        tl_cols = st.columns(6)
        num_tl = tl_cols[0].number_input("Số câu Tự luận", min_value=0, max_value=10, value=3, key="de_kt_num_tl")
        
        tl_points = []
        for i in range(num_tl):
            # Giới hạn hiển thị cột để giao diện không bị tràn
            p = tl_cols[(i % 5) + 1].number_input(f"Câu {i + 1} (đ)", min_value=0.0, value=2.0, step=0.25, key=f"de_kt_tl_p_{i}")
            tl_points.append(p)

        total_diem_tl = sum(tl_points)
        total_diem = total_diem_tn + total_diem_tl

        st.markdown("---")
        res_cols = st.columns(3)
        res_cols[0].metric("Tổng điểm Trắc nghiệm", f"{total_diem_tn:.2f}")
        res_cols[1].metric("Tổng điểm Tự luận", f"{total_diem_tl:.2f}")
        res_cols[2].metric("TỔNG ĐIỂM ĐỀ", f"{total_diem:.2f} / 10")

    # ============================================================
    # 4. KIỂM TRA CẤU HÌNH & TẠO ĐỀ
    # ============================================================
    if st.button("🚀 TẠO MA TRẬN & ĐỀ KIỂM TRA", type="primary", use_container_width=True, key="de_kt_btn_generate"):
        
        if tong_ty_le != 100:
            st.error("❌ Tổng tỷ lệ Nhận biết + Thông hiểu + Vận dụng + Vận dụng cao phải bằng 100%.")
            st.stop()

        if bam_sat and file_de is None:
            st.error("❌ Thầy đã chọn 'Bám sát đề cương' nhưng chưa tải lên đề cương.")
            st.stop()

        if abs(total_diem - 10.0) > 0.01:
            st.error(f"❌ Tổng điểm hiện tại là {total_diem:.2f}/10. Vui lòng điều chỉnh lại cấu hình.")
            st.stop()

        with st.spinner("📚 Đang xử lý kịch bản sinh đề thông minh..."):
            if bam_sat and file_de:
                raw_outline = extract_text_from_file(file_de)
                outline_text = normalize_outline(raw_outline)
                if not outline_text:
                    st.error("❌ Không đọc được nội dung đề cương.")
                    st.stop()
            else:
                outline_text = "Không cung cấp đề cương. AI tự động bám sát CT GDPT 2018 theo Môn học và Lớp."

        # --------------------------------------------------------
        # TÍNH TOÁN LOGIC SỐ THỨ TỰ CÂU BẰNG PYTHON (CHỐNG ẢO GIÁC AI)
        # --------------------------------------------------------
        tong_cau_tn = n_nlc + n_ds + n_dk + n_ngan
        
        # Chỉ số Trắc nghiệm
        idx_nlc_start, idx_nlc_end = 1, n_nlc
        idx_ds_start, idx_ds_end = idx_nlc_end + 1, idx_nlc_end + n_ds
        idx_dk_start, idx_dk_end = idx_ds_end + 1, idx_ds_end + n_dk
        idx_ngan_start, idx_ngan_end = idx_dk_end + 1, idx_dk_end + n_ngan
        
        # Chỉ số Tự luận
        idx_tl_start = tong_cau_tn + 1
        chi_tiet_tu_luan = ""
        for i, p in enumerate(tl_points):
            chi_tiet_tu_luan += f"├── Câu {idx_tl_start + i} = {p} điểm\n"

        # --------------------------------------------------------
        # KHUNG RÀNG BUỘC CHO AI
        # --------------------------------------------------------
        strict_prompt = f"""
BẠN LÀ CHUYÊN GIA BIÊN SOẠN ĐỀ KIỂM TRA THEO CHUẨN GDPT 2018.
NHIỆM VỤ: Soạn thảo Ma trận, Đặc tả, Đề kiểm tra và Đáp án tuân thủ TUYỆT ĐỐI các ràng buộc sau.

============================================================
THÔNG TIN CHUNG & PHẠM VI KIẾN THỨC
============================================================
Môn: {mon_hoc} | Lớp: {lop} | Tên bài: {ten_de} | Thời gian: {thoi_gian}
ĐỀ CƯƠNG KIẾN THỨC DUY NHẤT ĐƯỢC DÙNG:
{outline_text}

============================================================
KHUNG CẤU TRÚC ĐỀ BÀI (KHÔNG ĐƯỢC PHÉP THAY ĐỔI)
============================================================
TỶ LỆ: Nhận biết: {nb}% | Thông hiểu: {th}% | Vận dụng: {vd}% | Vận dụng cao: {vdc}%

PHẦN I. TRẮC NGHIỆM ({tong_cau_tn} câu, {total_diem_tn} điểm)
- Nhiều lựa chọn (NLC): {n_nlc} câu ({d_nlc}đ/câu) -> BẮT BUỘC Đánh số từ Câu {idx_nlc_start} đến Câu {idx_nlc_end}
- Đúng/Sai: {n_ds} câu ({d_ds}đ/câu) -> BẮT BUỘC Đánh số từ Câu {idx_ds_start} đến Câu {idx_ds_end}
- Điền khuyết: {n_dk} câu ({d_dk}đ/câu) -> BẮT BUỘC Đánh số từ Câu {idx_dk_start} đến Câu {idx_dk_end}
- Trả lời ngắn: {n_ngan} câu ({d_ngan}đ/câu) -> BẮT BUỘC Đánh số từ Câu {idx_ngan_start} đến Câu {idx_ngan_end}

PHẦN II. TỰ LUẬN ({num_tl} câu, {total_diem_tl} điểm)
{chi_tiet_tu_luan.strip()}

============================================================
QUY TẮC NGHIÊM NGẶT (NẾU VI PHẠM SẼ BỊ LỖI HỆ THỐNG)
============================================================
1. SỐ THỨ TỰ CÂU HỎI: Phải nối tiếp nhau từ Câu 1 đến Câu {idx_tl_start + num_tl - 1} theo đúng Khung Cấu Trúc ở trên. Tuyệt đối KHÔNG đánh số lại từ Câu 1 khi chuyển sang phần Tự luận.
2. CÔNG THỨC TOÁN HỌC (LaTeX): Mọi số liệu, biểu thức, phương trình, ký hiệu toán học (kể cả số đơn giản) BẮT BUỘC phải được bọc trong dấu $. (Ví dụ đúng: $y = x^2 + 2$. Sai: y = x^2 + 2).
3. ĐÁP ÁN NLC: Bắt buộc cung cấp đủ 4 phương án A, B, C, D cho mỗi câu NLC.
4. TÍNH TOÁN MA TRẬN: Trong bảng Ma trận, cột "Tổng số câu" phải bằng chính xác phép cộng của các số lượng câu Nhận biết, Thông hiểu, Vận dụng, VDC trên cùng một hàng. Tổng điểm phải đúng 10.0.

TRÌNH BÀY ĐẦU RA THEO THỨ TỰ:
# PHẦN I. PHẠM VI KIẾN THỨC SỬ DỤNG
# PHẦN II. MA TRẬN ĐỀ KIỂM TRA
# PHẦN III. BẢN ĐẶC TẢ
# PHẦN IV. ĐỀ KIỂM TRA
# PHẦN V. ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM
"""
        with st.spinner("🤖 AI đang soạn thảo ma trận, đề thi và định dạng công thức..."):
            try:
                result = ai_engine.generate_text(strict_prompt)
                
                if not result or not result.strip():
                    st.error("❌ AI trả về kết quả rỗng.")
                    st.stop()

                # Lưu kết quả
                st.session_state["de_kt_content"] = result
                st.session_state["de_kt_config"] = {
                    "mon_hoc": mon_hoc, "lop": lop, "ten_de": ten_de,
                    "hinh_thuc": hinh_thuc, "thoi_gian": thoi_gian,
                    "tong_diem": total_diem, "bam_sat": bam_sat
                }

                st.success("✅ Đã tạo thành công! Khung cấu trúc và số thứ tự đã được bảo đảm.")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Lỗi sinh đề: {e}")

    # ============================================================
    # 5. HIỂN THỊ KẾT QUẢ VÀ XUẤT WORD
    # ============================================================
    if "de_kt_content" in st.session_state:
        st.divider()
        st.markdown("## 📄 KẾT QUẢ ĐỀ KIỂM TRA")

        if st.button("🗑️ XÓA ĐỀ", key="de_kt_delete"):
            st.session_state.pop("de_kt_content", None)
            st.session_state.pop("de_kt_config", None)
            st.rerun()

        st.markdown(st.session_state["de_kt_content"])

        # Xuất Word
        try:
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            
            from export.export_word import WordExportEngine
            config = st.session_state.get("de_kt_config", {})
            word_bytes = WordExportEngine.export_to_word({
                "ai_generated_content": st.session_state["de_kt_content"],
                "is_de_kt": True,
                "title": config.get("ten_de", "Đề kiểm tra")
            })

            st.download_button(
                "📥 TẢI FILE WORD",
                data=word_bytes,
                file_name="De_Thi.docx",
                use_container_width=True,
                key="de_kt_download_word"
            )
        except Exception as e:
            st.warning(f"⚠️ Tính năng xuất Word đang lỗi hoặc chưa cấu hình thư viện export_word: {e}")
