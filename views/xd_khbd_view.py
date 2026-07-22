# -*- coding: utf-8 -*-

# """

VIEW: GIAO DIỆN XÂY DỰNG KẾ HOẠCH BÀI DẠY
KIẾN TRÚC: VIEW TÁCH BIỆT DATA/LOGIC
FILE: views/xd_khbd_view.py
===========================

"""

import streamlit as st
import os
import tempfile

# ============================================================

# IMPORT LOGIC TỪ FILE DATA

# ============================================================

try:
from views.xd_khbd_data import (
init_session_state,
get_nls_domains,
get_nls_components,
get_nls_levels,
get_nls_content,
read_multiple_files,
read_uploaded_file,
read_template_local,
add_nls,
format_nls,
add_activity,
build_prompt,
generate_ai,
validate_khbd_result,
)

except Exception as e:
st.error(
"❌ Không thể nạp module views.xd_khbd_data.\n\n"
f"Chi tiết lỗi: {e}"
)
raise

# ============================================================

# IMPORT MODULE XUẤT WORD

# ============================================================

try:
from export.word_export_engine import WordExportEngine
except Exception as e:
WordExportEngine = None
EXPORT_WORD_IMPORT_ERROR = str(e)

# ============================================================

# HÀM TIỆN ÍCH

# ============================================================

def _count_source_quality(text):
"""
Đánh giá nhanh chất lượng văn bản nguồn.
Không chặn cứng vì tài liệu ngắn vẫn có thể là nội dung hợp lệ.
"""

```
if not text:
    return {
        "chars": 0,
        "words": 0,
        "lines": 0,
        "status": "empty",
    }

chars = len(text)
words = len(text.split())
lines = len([x for x in text.splitlines() if x.strip()])

if chars < 500:
    status = "very_low"
elif chars < 1500:
    status = "low"
elif chars < 5000:
    status = "medium"
else:
    status = "good"

return {
    "chars": chars,
    "words": words,
    "lines": lines,
    "status": status,
}
```

def _show_source_quality(text, title="Nguồn kiến thức chính"):
"""
Hiển thị thống kê dữ liệu nguồn để giáo viên biết
AI thực sự nhận được bao nhiêu dữ liệu.
"""

```
quality = _count_source_quality(text)

st.markdown(f"#### 📊 Kiểm tra dữ liệu: {title}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Số ký tự", f"{quality['chars']:,}")

with col2:
    st.metric("Số từ", f"{quality['words']:,}")

with col3:
    st.metric("Số dòng", f"{quality['lines']:,}")

if quality["status"] == "empty":
    st.error(
        "❌ Không đọc được nội dung văn bản từ tài liệu nguồn."
    )

elif quality["status"] == "very_low":
    st.warning(
        "⚠️ Nội dung trích xuất được rất ít. "
        "PDF có thể là bản scan, ảnh hoặc file bị lỗi lớp văn bản."
    )

elif quality["status"] == "low":
    st.warning(
        "⚠️ Nội dung nguồn còn ngắn. "
        "Nên kiểm tra lại phạm vi trang hoặc khả năng trích xuất PDF."
    )

else:
    st.success(
        "✅ Dữ liệu nguồn đã được đọc và sẵn sàng đưa vào AI."
    )
```

# ============================================================

# RENDER VIEW CHÍNH

# ============================================================

def render_xd_khbd(ai_engine=None):

```
# --------------------------------------------------------
# KHỞI TẠO SESSION STATE
# --------------------------------------------------------
init_session_state()

st.title(
    "📘 XÂY DỰNG KẾ HOẠCH BÀI DẠY "
    "(CHUẨN 5512 & TT18)"
)

# ========================================================
# 1. THÔNG TIN BÀI DẠY
# ========================================================
st.subheader("🎛️ Thông tin bài dạy")

col1, col2 = st.columns(2)

with col1:
    khoi_lop = st.selectbox(
        "Khối lớp",
        [
            "Lớp 6",
            "Lớp 7",
            "Lớp 8",
            "Lớp 9",
            "Lớp 10",
            "Lớp 11",
            "Lớp 12",
        ],
        key="khbd_khoi_lop",
    )

with col2:
    mon_hoc = st.selectbox(
        "Môn học",
        [
            "Toán",
            "Ngữ văn",
            "Tiếng Anh",
            "Khoa học tự nhiên",
            "Vật lí",
            "Hóa học",
            "Sinh học",
            "Lịch sử và Địa lí",
            "Tin học",
            "Công nghệ",
            "Khác",
        ],
        key="khbd_mon_hoc",
    )

# ========================================================
# 2. CHẾ ĐỘ SOẠN
# ========================================================
st.subheader("✨ Chế độ soạn")

mode = st.radio(
    "Chọn chế độ",
    ["chinh_sua", "tu_dong"],
    format_func=lambda x: (
        "📄 Chỉnh sửa giáo án gốc"
        if x == "chinh_sua"
        else "⚡ Tự động soạn từ SGK"
    ),
    key="khbd_mode",
    horizontal=True,
)

range_trang = ""

if mode == "tu_dong":

    st.info(
        "💡 Nếu chỉ soạn một bài trong SGK, "
        "nên giới hạn phạm vi trang để AI tập trung phân tích nội dung."
    )

    range_trang = st.text_input(
        "Phạm vi trang SGK cần soạn",
        placeholder="Ví dụ: 45-48",
        key="khbd_range_trang",
    )

# ========================================================
# 3. TẢI TÀI LIỆU
# ========================================================
st.subheader("📤 Tài liệu đầu vào")

col_up1, col_up2, col_up3, col_up4 = st.columns(4)

if mode == "chinh_sua":

    file_ga = col_up1.file_uploader(
        "Giáo án gốc",
        type=["docx", "pdf"],
        accept_multiple_files=True,
        key="khbd_file_ga",
    )

    file_sgk = []

else:

    file_ga = []

    file_sgk = col_up1.file_uploader(
        "SGK / Tài liệu kiến thức",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="khbd_file_sgk",
    )

file_ppct = col_up2.file_uploader(
    "PPCT (Tùy chọn)",
    type=["pdf", "docx", "xlsx", "xls"],
    key="khbd_file_ppct",
)

file_ai = col_up3.file_uploader(
    "Bảng AI (Tùy chọn)",
    type=["pdf", "docx", "xlsx", "xls"],
    key="khbd_file_ai",
)

file_template = col_up4.file_uploader(
    "Mẫu KHBD trường",
    type=["docx"],
    key="khbd_file_template",
)

# ========================================================
# 4. THÔNG TIN CHI TIẾT
# ========================================================
st.subheader("📚 Thông tin chi tiết")

col_td1, col_td2 = st.columns(2)

with col_td1:

    ten_bai = st.text_input(
        "Tên bài dạy",
        key="khbd_ten_bai",
    )

with col_td2:

    so_tiet = st.text_input(
        "Thời lượng tiết học",
        value="1 tiết",
        key="khbd_so_tiet",
    )

# ========================================================
# 5. TÍCH HỢP CHUYÊN SÂU
# ========================================================
st.subheader("🔧 Tích hợp chuyên sâu")

c_th1, c_th2, c_th3 = st.columns(3)

with c_th1:

    tich_hop_nls = st.checkbox(
        "Năng lực số (TT18)",
        key="khbd_tich_hop_nls",
    )

with c_th2:

    tich_hop_ai = st.checkbox(
        "Năng lực AI",
        key="khbd_tich_hop_ai",
    )

with c_th3:

    tich_hop_hoa_nhap = st.checkbox(
        "Dạy học hòa nhập",
        key="khbd_tich_hop_hoa_nhap",
    )

# ========================================================
# 6. HÒA NHẬP
# ========================================================
nhu_cau_hoa_nhap = []

if tich_hop_hoa_nhap:

    with st.container(border=True):

        st.markdown(
            "##### 🫂 Lựa chọn loại khuyết tật / nhu cầu"
        )

        nhu_cau_hoa_nhap = st.multiselect(
            "Chọn đối tượng",
            [
                "Vận động",
                "Nghe",
                "Nói",
                "Nhìn",
                "Thần kinh",
                "Tâm thần",
                "Trí tuệ",
                "Tự kỷ",
                "Khác",
            ],
            default=["Nhìn"],
            key="khbd_nhu_cau_hoa_nhap",
        )

# ========================================================
# 7. HOẠT ĐỘNG BỔ SUNG
# ========================================================
st.subheader("📌 Hoạt động giáo viên mong muốn thêm")

c_hd1, c_hd2 = st.columns([5, 1])

with c_hd1:

    st.text_input(
        "Hoạt động",
        placeholder="VD: Thí nghiệm, trò chơi, mô phỏng...",
        key="khbd_new_activity",
        label_visibility="collapsed",
        on_change=add_activity,
    )

with c_hd2:

    st.button(
        "➕ Thêm",
        on_click=add_activity,
        use_container_width=True,
    )

for index, activity in enumerate(
    st.session_state.khbd_hoat_dong_list
):

    c_i1, c_i2 = st.columns([10, 1])

    with c_i1:

        st.info(activity)

    with c_i2:

        if st.button(
            "Xóa",
            key=f"khbd_del_activity_{index}",
        ):

            st.session_state.khbd_hoat_dong_list.pop(index)
            st.rerun()

# ========================================================
# 8. CẤU HÌNH NĂNG LỰC SỐ
# ========================================================
if tich_hop_nls:

    with st.container(border=True):

        st.markdown("#### 🎯 Cấu hình Năng lực số")

        loai_khung = st.radio(
            "Chuẩn",
            [
                "Giáo viên (Thông tư 18)",
                "Học sinh (DigComp)",
            ],
            horizontal=True,
            key="khbd_loai_khung_nls",
        )

        domains = get_nls_domains(loai_khung)

        col_lv, col_tp, col_md = st.columns(
            [2, 2, 1]
        )

        with col_lv:

            linh_vuc = st.selectbox(
                "Lĩnh vực",
                domains,
                key="khbd_nls_linh_vuc",
            )

        components = get_nls_components(
            loai_khung,
            linh_vuc,
        )

        with col_tp:

            thanh_phan = st.selectbox(
                "Thành phần",
                components,
                key="khbd_nls_thanh_phan",
            )

        levels = get_nls_levels(
            loai_khung,
            linh_vuc,
            thanh_phan,
        )

        with col_md:

            muc_do = st.selectbox(
                "Mức độ",
                levels,
                key="khbd_nls_muc_do",
            )

        tu_dong_noi_dung = get_nls_content(
            loai_khung,
            linh_vuc,
            thanh_phan,
            muc_do,
        )

        st.session_state.khbd_nls_noi_dung = (
            tu_dong_noi_dung
        )

        st.text_area(
            "Yêu cầu cần đạt",
            value=tu_dong_noi_dung,
            height=100,
            disabled=True,
        )

        st.button(
            "➕ Thêm vào danh sách",
            on_click=add_nls,
            use_container_width=True,
        )

        for index, item in enumerate(
            st.session_state.khbd_nls_list
        ):

            with st.container(border=True):

                st.markdown(
                    f"**{index + 1}. "
                    f"{item['linh_vuc']}** "
                    f"({item['muc_do']})\n\n"
                    f"{item['noi_dung']}"
                )

                if st.button(
                    "Xóa",
                    key=f"khbd_del_nls_{index}",
                ):

                    st.session_state.khbd_nls_list.pop(index)
                    st.rerun()

# ========================================================
# 9. NGÔN NGỮ
# ========================================================
tieng_anh = st.checkbox(
    "Giáo án bằng Tiếng Anh",
    key="khbd_tieng_anh",
)

st.divider()

# ========================================================
# 10. KÍCH HOẠT AI
# ========================================================
if st.button(
    "⚡ KÍCH HOẠT XỬ LÝ AI",
    type="primary",
    use_container_width=True,
):

    # ----------------------------------------------------
    # KIỂM TRA ENGINE
    # ----------------------------------------------------
    if ai_engine is None:

        st.error(
            "❌ Chưa cấu hình AI Core Engine."
        )

    # ----------------------------------------------------
    # KIỂM TRA TÀI LIỆU
    # ----------------------------------------------------
    elif mode == "chinh_sua" and not file_ga:

        st.error(
            "⚠️ Vui lòng tải giáo án gốc."
        )

    elif mode == "tu_dong" and not file_sgk:

        st.error(
            "⚠️ Vui lòng cung cấp tệp SGK."
        )

    else:

        with st.spinner(
            "🧠 Hệ thống đang phân tích tài liệu "
            "và biên soạn KHBD..."
        ):

            try:

                # ========================================
                # ĐỌC NGUỒN CHÍNH
                # ========================================
                if mode == "tu_dong":

                    noi_dung_chinh = read_multiple_files(
                        file_sgk,
                        range_trang,
                        is_pdf_target=True,
                    )

                else:

                    noi_dung_chinh = ""

                # ========================================
                # ĐỌC GIÁO ÁN GỐC
                # ========================================
                if mode == "chinh_sua":

                    noi_dung_ga = read_multiple_files(
                        file_ga
                    )

                else:

                    noi_dung_ga = ""

                # ========================================
                # ĐỌC TÀI LIỆU PHỤ
                # ========================================
                noi_dung_ppct = read_uploaded_file(
                    file_ppct
                )

                noi_dung_ai = read_uploaded_file(
                    file_ai
                )

                # ========================================
                # ĐỌC MẪU KHBD
                # ========================================
                if file_template:

                    noi_dung_mau = read_uploaded_file(
                        file_template
                    )

                else:

                    noi_dung_mau = read_template_local()

                # ========================================
                # KIỂM TRA CHẤT LƯỢNG NGUỒN
                # ========================================
                if mode == "tu_dong":

                    _show_source_quality(
                        noi_dung_chinh,
                        "SGK / Tài liệu kiến thức",
                    )

                    if not noi_dung_chinh.strip():

                        st.error(
                            "❌ Không đọc được nội dung SGK."
                        )

                        st.stop()

                # ========================================
                # THÔNG TIN BÀI DẠY
                # ========================================
                thong_tin = (
                    f"- Khối: {khoi_lop}\n"
                    f"- Môn: {mon_hoc}\n"
                    f"- Tên bài: "
                    f"{ten_bai or 'Theo nguồn'}\n"
                    f"- Số tiết: {so_tiet}\n"
                    f"- Ngôn ngữ: "
                    f"{'English' if tieng_anh else 'Tiếng Việt'}"
                )

                hoat_dong = (
                    "\n".join(
                        st.session_state.khbd_hoat_dong_list
                    )
                    or "Không có."
                )

                # ========================================
                # XÂY DỰNG PROMPT
                # ========================================
                prompt = build_prompt(
                    thong_tin=thong_tin,
                    noi_dung_chinh=noi_dung_chinh,
                    noi_dung_ga=noi_dung_ga,
                    noi_dung_ppct=noi_dung_ppct,
                    noi_dung_ai=noi_dung_ai,
                    noi_dung_mau=noi_dung_mau,
                    nls=format_nls(),
                    tich_hop_ai=tich_hop_ai,
                    tich_hop_hoa_nhap=tich_hop_hoa_nhap,
                    nhu_cau_hoa_nhap=", ".join(
                        nhu_cau_hoa_nhap
                    ),
                    hoat_dong=hoat_dong,
                    mode=mode,
                )

                # ========================================
                # GỌI AI
                # ========================================
                raw_result = generate_ai(
                    ai_engine,
                    prompt,
                )

                # ========================================
                # KIỂM TRA KẾT QUẢ
                # ========================================
                is_valid, msg = validate_khbd_result(
                    raw_result
                )

                if not is_valid:

                    st.warning(
                        f"⚠️ Cảnh báo cấu trúc: {msg}"
                    )

                # ========================================
                # LƯU KẾT QUẢ
                # ========================================
                st.session_state.khbd_result = raw_result

                st.success(
                    "🎉 Đã tạo giáo án thành công!"
                )

            except ValueError as ve:

                st.error(
                    f"❌ Lỗi kiểm định dữ liệu nguồn: {ve}"
                )

            except Exception as e:

                st.error(
                    f"❌ Lỗi hệ thống: {e}"
                )

# ========================================================
# 11. HIỂN THỊ KẾT QUẢ
# ========================================================
result = st.session_state.get(
    "khbd_result"
)

if result:

    st.subheader(
        "📝 Kết quả Kế hoạch bài dạy"
    )

    st.markdown(result)

    st.divider()

    st.subheader(
        "📄 Xuất Word Chuẩn Định Dạng"
    )

    if WordExportEngine is None:

        st.error(
            "❌ Không kết nối được module "
            "`export.word_export_engine`."
        )

    else:

        try:

            template_path = (
                "templates/KHBD_Mau.docx"
            )

            uploaded_template = file_template

            if uploaded_template:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".docx",
                ) as tmp:

                    tmp.write(
                        uploaded_template.getvalue()
                    )

                    template_path = tmp.name

            try:

                word_bytes = (
                    WordExportEngine
                    .convert_markdown_to_docx_bytes(
                        result,
                        template_path=template_path,
                    )
                )

            except TypeError:

                word_bytes = (
                    WordExportEngine
                    .convert_markdown_to_docx_bytes(
                        result
                    )
                )

            st.download_button(
                "📥 TẢI KHBD WORD (Chuẩn 5512)",
                data=word_bytes,
                file_name="Giao_An_5512.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )

            if (
                uploaded_template
                and template_path != "templates/KHBD_Mau.docx"
                and os.path.exists(template_path)
            ):

                os.remove(template_path)

        except Exception as e:

            st.error(
                f"❌ Lỗi xuất Word: {e}"
            )
```
