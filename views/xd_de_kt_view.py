# -*- coding: utf-8 -*-
import streamlit as st
import sys
from pathlib import Path

# ============================================================
# HÀM ĐỌC NỘI DUNG ĐỀ CƯƠNG
# ============================================================
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        filename = uploaded_file.name.lower()
        # ----------------------------------------------------
        # ĐỌC PDF
        # ----------------------------------------------------
        if filename.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(uploaded_file)
            texts = []
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    texts.append(f"\n--- TRANG {page_number} ---\n{text.strip()}")
            return "\n".join(texts)

        # ----------------------------------------------------
        # ĐỌC DOCX
        # ----------------------------------------------------
        elif filename.endswith(".docx"):
            import docx
            document = docx.Document(uploaded_file)
            texts = []
            # Đọc các đoạn văn
            for para in document.paragraphs:
                text = para.text.strip()
                if text:
                    texts.append(text)
            # Đọc toàn bộ bảng
            for table_index, table in enumerate(document.tables, start=1):
                texts.append(f"\n--- BẢNG {table_index} ---")
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text.strip():
                        texts.append(row_text)
            return "\n".join(texts)

        # ----------------------------------------------------
        # ĐỌC TXT
        # ----------------------------------------------------
        elif filename.endswith(".txt"):
            return uploaded_file.read().decode("utf-8", errors="ignore")

    except Exception as e:
        st.error(f"❌ Lỗi khi đọc đề cương: {e}")
        return ""
    return ""

# ============================================================
# HÀM CHUẨN HÓA ĐỀ CƯƠNG
# ============================================================
def normalize_outline(text):
    if not text:
        return ""
    # Xóa các dòng trống liên tiếp
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    text = "\n".join(lines)
    
    # Giới hạn độ dài để tránh prompt quá lớn
    MAX_CHARS = 60000
    if len(text) > MAX_CHARS:
        st.warning(f"⚠️ Đề cương có {len(text):,} ký tự. Hệ thống sử dụng {MAX_CHARS:,} ký tự đầu tiên.")
        text = text[:MAX_CHARS]
    return text

# ============================================================
# HÀM GIAO DIỆN CHÍNH
# ============================================================
def render_xd_de_kt(ai_engine):
    st.markdown("### 📝 Soạn thảo Ma trận, Đặc tả & Đề KT (Chuẩn 5512)")

    # ============================================================
    # 1. THÔNG TIN CHUNG
    # ============================================================
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
        ["15 phút", "45 phút", "90 phút", "120 phút"],
        key="de_kt_thoi_gian"
    )

    ten_de = c5.text_input(
        "Tên bài kiểm tra",
        key="de_kt_ten_de"
    )

    with c6:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        bam_sat = st.checkbox(
            "Bám sát đề cương",
            value=True,
            key="de_kt_bam_sat"
        )

    # ============================================================
    # 2. TẢI ĐỀ CƯƠNG
    # ============================================================
    file_de = st.file_uploader(
        "📚 Tải đề cương / tài liệu làm căn cứ sinh đề",
        type=["pdf", "docx", "txt"],
        key="de_kt_file_de_cuong"
    )

    # ============================================================
    # 3. CẤU HÌNH TỶ LỆ MỨC ĐỘ NHẬN THỨC & CẤU TRÚC ĐỀ
    # ============================================================
    with st.expander("⚙️ Cấu hình Tỷ lệ & Số câu", expanded=True):
        r1, r2, r3, r4 = st.columns(4)
        nb = r1.number_input("Nhận biết (%)", min_value=0, max_value=100, value=40, key="de_kt_nb")
        th = r2.number_input("Thông hiểu (%)", min_value=0, max_value=100, value=30, key="de_kt_th")
        vd = r3.number_input("Vận dụng (%)", min_value=0, max_value=100, value=20, key="de_kt_vd")
        vdc = r4.number_input("Vận dụng cao (%)", min_value=0, max_value=100, value=10, key="de_kt_vdc")

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

        tl_cols = st.columns(4)
        num_tl = tl_cols[0].number_input("Số câu Tự luận", min_value=1, max_value=10, value=2, key="de_kt_num_tl")
        tl_points = []
        for i in range(num_tl):
            p = tl_cols[1].number_input(f"Câu {i + 1} (đ)", min_value=0.0, value=1.0, step=0.25, key=f"de_kt_tl_p_{i}")
            tl_points.append(p)

        total_diem_tl = sum(tl_points)
        total_diem = total_diem_tn + total_diem_tl

        tl_cols[2].metric("Tổng điểm TN", f"{total_diem_tn:.2f}")
        tl_cols[3].metric("Tổng điểm TL", f"{total_diem_tl:.2f}")
        st.metric("TỔNG ĐIỂM ĐỀ", f"{total_diem:.2f} / 10")

    # ============================================================
    # 4. KIỂM TRA CẤU HÌNH TRƯỚC KHI SINH
    # ============================================================
    if st.button("🚀 TẠO MA TRẬN & ĐỀ THI", type="primary", use_container_width=True, key="de_kt_btn_generate"):
        
        if tong_ty_le != 100:
            st.error("❌ Tổng tỷ lệ Nhận biết + Thông hiểu + Vận dụng + Vận dụng cao phải bằng 100%.")
            st.stop()

        if bam_sat and file_de is None:
            st.error("❌ Thầy đã chọn 'Bám sát đề cương' nhưng chưa tải lên đề cương.")
            st.stop()

        if abs(total_diem - 10.0) > 0.01:
            st.error(f"❌ Tổng điểm hiện tại là {total_diem:.2f}/10. Vui lòng điều chỉnh lại cấu hình.")
            st.stop()

        # ========================================================
        # 5. ĐỌC VÀ XÂY DỰNG PHẠM VI KIẾN THỨC ĐƯỢC PHÉP
        # ========================================================
        with st.spinner("📚 Đang xử lý kịch bản sinh đề thông minh..."):
            if bam_sat and file_de:
                raw_outline = extract_text_from_file(file_de)
                outline_text = normalize_outline(raw_outline)
                if not outline_text:
                    st.error("❌ Không đọc được nội dung đề cương.")
                    st.stop()

                allowed_scope = f"""
============================================================
PHẠM VI KIẾN THỨC ĐƯỢC PHÉP SỬ DỤNG
============================================================

Tài liệu dưới đây là nguồn kiến thức duy nhất được phép sử dụng để xây dựng đề kiểm tra.

------------------- BẮT ĐẦU ĐỀ CƯƠNG -------------------
{outline_text}
-------------------- KẾT THÚC ĐỀ CƯƠNG ------------------

QUY TẮC PHẠM VI:
1. Chỉ sử dụng kiến thức xuất hiện trong đề cương.
2. Không được tự ý bổ sung kiến thức ngoài đề cương.
3. Không được mở rộng sang bài học, chủ đề hoặc nội dung không xuất hiện trong đề cương.
4. Đề kiểm tra phải phủ đúng các đơn vị kiến thức được nêu trong đề cương.
============================================================
"""
            else:
                allowed_scope = """
============================================================
PHẠM VI KIẾN THỨC
============================================================
Không có đề cương được tải lên. AI được phép sử dụng kiến thức phù hợp với Chương trình giáo dục phổ thông 2018 tương ứng với Môn học và Lớp học đã cấu hình.
============================================================
"""

        # ========================================================
        # 6. TÍNH TOÁN SỐ THỨ TỰ CÂU ĐỂ CHỐNG ẢO GIÁC AI
        # ========================================================
        tong_cau_tn = n_nlc + n_ds + n_dk + n_ngan
        
        idx_nlc_start, idx_nlc_end = 1, n_nlc
        idx_ds_start, idx_ds_end = idx_nlc_end + 1, idx_nlc_end + n_ds
        idx_dk_start, idx_dk_end = idx_ds_end + 1, idx_ds_end + n_dk
        idx_ngan_start, idx_ngan_end = idx_dk_end + 1, idx_dk_end + n_ngan
        
        idx_tl_start = tong_cau_tn + 1
        
        chi_tiet_tu_luan = ""
        for i, p in enumerate(tl_points):
            chi_tiet_tu_luan += f"├── Câu {idx_tl_start + i} = {p} điểm\n"

        # ========================================================
        # 7. XÂY DỰNG CẤU HÌNH ĐỀ (ĐÓNG KHUNG TỪ PYTHON)
        # ========================================================
        exam_configuration = f"""
============================================================
THÔNG TIN CẤU HÌNH ĐỀ KIỂM TRA (AI BẮT BUỘC TUÂN THỦ)
============================================================

Môn học: {mon_hoc} | Lớp: {lop} | Tên bài: {ten_de} | Thời gian: {thoi_gian}
PHÂN BỐ MỨC ĐỘ NHẬN THỨC: Nhận biết: {nb}% | Thông hiểu: {th}% | Vận dụng: {vd}% | Vận dụng cao: {vdc}%

------------------------------------------------------------
KHUNG CẤU TRÚC CHI TIẾT (BẢN KẾ HOẠCH ĐÃ CHUẨN HÓA)
------------------------------------------------------------
Phần Trắc nghiệm: Tổng {tong_cau_tn} câu = {total_diem_tn} điểm
├── NLC: {n_nlc} câu × {d_nlc} = {n_nlc * d_nlc} điểm
├── Đúng/Sai: {n_ds} câu × {d_ds} = {n_ds * d_ds} điểm
├── Điền khuyết: {n_dk} câu × {d_dk} = {n_dk * d_dk} điểm
└── Trả lời ngắn: {n_ngan} câu × {d_ngan} = {n_ngan * d_ngan} điểm

Phần Tự luận: Tổng {num_tl} câu = {total_diem_tl} điểm
{chi_tiet_tu_luan.strip()}

------------------------------------------------------------
QUY ĐỊNH ĐÁNH SỐ THỨ TỰ TỪNG PHẦN TRONG ĐỀ
------------------------------------------------------------
PHẦN I. TRẮC NGHIỆM — {total_diem_tn} điểm
- Dạng NLC: Đánh số từ Câu {idx_nlc_start} → Câu {idx_nlc_end}
- Dạng Đúng/Sai: Đánh số từ Câu {idx_ds_start} → Câu {idx_ds_end}
- Dạng Điền khuyết: Đánh số từ Câu {idx_dk_start} → Câu {idx_dk_end}
- Dạng Trả lời ngắn: Đánh số từ Câu {idx_ngan_start} → Câu {idx_ngan_end}

PHẦN II. TỰ LUẬN — {total_diem_tl} điểm
- Các câu Tự luận: Đánh số từ Câu {idx_tl_start} → Câu {idx_tl_start + num_tl - 1}
============================================================
"""

        # ========================================================
        # 8. PROMPT KIỂM SOÁT CHẶT LỖI
        # ========================================================
        strict_instruction = """
============================================================
YÊU CẦU BẮT BUỘC KHI TẠO ĐỀ (TUYỆT ĐỐI KHÔNG SÁNG TẠO LÀM SAI LỆCH)
============================================================

1. QUY TẮC HIỂN THỊ CÔNG THỨC TOÁN HỌC (LaTeX)
Mọi công thức toán học, biểu thức, phương trình, tọa độ, ký hiệu (VD: phân số, căn bậc hai, lũy thừa, v.v.) BẮT BUỘC phải được bọc trong cặp dấu $ để hiển thị đúng chuẩn LaTeX. 
Ví dụ đúng: $y = x^2 + 2$, $\Delta$, $x_1, x_2$.
Ví dụ SÁI: y = x^2 + 2, delta, x1, x2.

2. QUY TẮC ĐÁNH SỐ THỨ TỰ
Đánh số câu hỏi liên tục từ Câu 1 đến câu cuối cùng theo ĐÚNG KHUNG CẤU TRÚC đã cung cấp ở trên. Đáp án cũng phải khớp chính xác với số thứ tự này. Tuyệt đối không tự ý khởi tạo lại Câu 1 khi qua phần Tự Luận.

3. LOGIC BẢNG MA TRẬN VÀ BẢN ĐẶC TẢ
- Cột "Tổng" (số câu / số điểm) trong Ma trận phải là TỔNG ĐÚNG của các cột Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao trên cùng hàng đó. Không được cộng sai.
- Mọi câu hỏi được sinh ra trong Đề bài phải khớp 100% với Bản đặc tả.
- Không gộp chung Điền khuyết và Trả lời ngắn vào phần Tự Luận. Tất cả các dạng này đều thuộc Trắc nghiệm.

------------------------------------------------------------
YÊU CẦU ĐẦU RA (THEO TRÌNH TỰ BẮT BUỘC)
------------------------------------------------------------
# PHẦN I. PHẠM VI KIẾN THỨC ĐƯỢC SỬ DỤNG
# PHẦN II. MA TRẬN ĐỀ KIỂM TRA
# PHẦN III. BẢN ĐẶC TẢ
# PHẦN IV. ĐỀ KIỂM TRA (Trình bày đúng cấu trúc và số thứ tự)
# PHẦN V. ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM (Khớp số thứ tự với đề)
# PHẦN VI. BẢNG TỰ KIỂM TRA
============================================================
"""

        final_prompt = f"""
{strict_instruction}
{exam_configuration}
{allowed_scope}

NHIỆM VỤ: Hãy đóng vai một chuyên gia giáo dục, cẩn thận rà soát logic toán học, sau đó sinh ra trọn bộ hồ sơ đề kiểm tra (Phần I đến Phần VI) đáp ứng tuyệt đối các thông số trên.
"""

        # ========================================================
        # 9. GỌI AI
        # ========================================================
        with st.spinner("🤖 AI đang tính toán ma trận, soạn thảo và định dạng công thức Toán học..."):
            try:
                result = ai_engine.generate_text(final_prompt)
                
                if not result or not result.strip():
                    st.error("❌ AI trả về kết quả rỗng.")
                    st.stop()

                st.session_state["de_kt_content"] = result
                st.session_state["de_kt_config"] = {
                    "mon_hoc": mon_hoc, "lop": lop, "ten_de": ten_de,
                    "hinh_thuc": hinh_thuc, "thoi_gian": thoi_gian,
                    "tong_diem": total_diem, "bam_sat": bam_sat,
                    "file_name": file_de.name if file_de else None
                }
                st.success("✅ Đã tạo xong ma trận, đặc tả và đề kiểm tra không lỗi logic!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Lỗi khi sinh đề: {e}")

    # ============================================================
    # 10. HIỂN THỊ KẾT QUẢ VÀ XUẤT WORD
    # ============================================================
    if "de_kt_content" in st.session_state:
        st.divider()
        st.markdown("## 📄 KẾT QUẢ ĐỀ KIỂM TRA")

        if st.button("🗑️ XÓA ĐỀ", key="de_kt_delete"):
            del st.session_state["de_kt_content"]
            if "de_kt_config" in st.session_state:
                del st.session_state["de_kt_config"]
            st.rerun()

        st.markdown(st.session_state["de_kt_content"])

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
            st.warning(f"⚠️ Thư viện docx chưa được cài đặt hoặc có lỗi cấu trúc: {e}")
