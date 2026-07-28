# -*- coding: utf-8 -*-
r"""
============================================================
MODULE: modules/ho_tro_giang_day/xd_phan_tich.py
Nhiệm vụ: Trợ lý Phân tích Dữ liệu Học tập (Learning Analytics).
Chức năng: Đọc file Excel/CSV (Bảng điểm, chuyên cần), trực quan hóa dữ liệu cơ bản
và dùng AI để phân tích dự đoán, cảnh báo học sinh rủi ro, đưa ra khuyến nghị.
============================================================
"""

import io
import logging
import streamlit as st
import pandas as pd

logger = logging.getLogger(__name__)

# Kết nối bộ xuất Word
try:
    from export.export_word import export_word
except ImportError:
    export_word = None

# Bắt buộc import AIEngine2
try:
    from utils.ai_engine_2 import AIEngine2
except ImportError:
    AIEngine2 = None

def get_sample_data():
    """Tạo dữ liệu mẫu nếu giáo viên chưa có file Excel"""
    data = {
        "Họ và Tên": ["Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Phạm Thị D", "Hoàng Văn E", "Vũ Thị F", "Bùi Văn G"],
        "Điểm Giữa Kỳ": [6.5, 8.0, 4.0, 9.5, 5.0, 7.5, 3.5],
        "Điểm Chuyên Cần": [9.0, 10.0, 5.0, 10.0, 7.0, 9.0, 4.0],
        "Số buổi nghỉ": [1, 0, 5, 0, 3, 1, 6],
        "Tỷ lệ làm bài tập (%)": [75, 100, 40, 100, 60, 85, 30]
    }
    return pd.DataFrame(data)

def render_xd_phan_tich(ai_engine_cu=None):
    if "df_data" not in st.session_state:
        st.session_state["df_data"] = None
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None

    st.markdown("### 📊 Trợ lý Phân tích Dữ liệu & Cảnh báo Học tập")
    st.info("💡 **Góc chuyên gia:** Hệ thống đóng vai trò như một Data Scientist. Tải lên bảng điểm, điểm chuyên cần của lớp, AI sẽ phân tích xu hướng, cảnh báo học sinh có nguy cơ trượt/bỏ học và đề xuất lộ trình cải thiện.")

    # ========================================================
    # KHU VỰC 1: NẠP DỮ LIỆU
    # ========================================================
    with st.container(border=True):
        st.markdown("#### 1️⃣ Nhập Dữ liệu Đầu vào (Data Inputs)")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            uploaded_file = st.file_uploader("Tải lên Bảng điểm lớp học (CSV, Excel):", type=["csv", "xlsx", "xls"])
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📝 Tải Dữ liệu Mẫu (Để test)", use_container_width=True):
                st.session_state["df_data"] = get_sample_data()
                st.session_state["analysis_result"] = None
                
        # Xử lý file tải lên
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    st.session_state["df_data"] = pd.read_csv(uploaded_file)
                else:
                    st.session_state["df_data"] = pd.read_excel(uploaded_file)
                st.session_state["analysis_result"] = None
                st.success("✅ Đã tải dữ liệu thành công!")
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}. Vui lòng đảm bảo định dạng chuẩn.")

    # ========================================================
    # KHU VỰC 2: TRỰC QUAN HÓA & PHÂN TÍCH AI
    # ========================================================
    if st.session_state["df_data"] is not None:
        df = st.session_state["df_data"]
        
        st.markdown("---")
        st.markdown("#### 2️⃣ Tổng quan Dữ liệu Lớp học (Phân tích Mô tả)")
        
        # Hiển thị bảng
        st.dataframe(df, use_container_width=True, height=200)
        
        # Thống kê nhanh nếu có cột số
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if numeric_cols:
            st.markdown("**📉 Biểu đồ Phân phối Nhanh:**")
            selected_col = st.selectbox("Chọn cột điểm/chỉ số để xem biểu đồ:", numeric_cols)
            
            # Nếu có cột Tên thì dùng làm index để vẽ, nếu không vẽ cột bình thường
            name_cols = [col for col in df.columns if "tên" in col.lower() or "name" in col.lower()]
            if name_cols:
                chart_data = df.set_index(name_cols[0])[selected_col]
                st.bar_chart(chart_data)
            else:
                st.line_chart(df[selected_col])

        st.markdown("---")
        st.markdown("#### 3️⃣ Phân tích Dự đoán & Khuyến nghị bằng AI (Tương lai & Hành động)")
        
        yeu_cau_ai = st.text_input(
            "Mục tiêu phân tích (Tùy chọn):", 
            placeholder="VD: Hãy tìm ra những học sinh có nguy cơ hổng kiến thức nhất, tập trung vào điểm chuyên cần..."
        )
        
        if st.button("🧠 YÊU CẦU AI PHÂN TÍCH CHUYÊN SÂU", type="primary", use_container_width=True):
            if AIEngine2 is None:
                st.error("❌ Không tìm thấy hệ thống AIEngine2.")
                return
                
            with st.spinner("⏳ AI đang chạy thuật toán phân tích hành vi và dự đoán kết quả..."):
                # Đóng gói dữ liệu DataFrame thành chuỗi Markdown hoặc CSV thô để AI đọc
                csv_data = df.to_csv(index=False)
                
                prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA KHOA HỌC DỮ LIỆU GIÁO DỤC (EDUCATIONAL DATA SCIENTIST) VÀ CỐ VẤN HỌC TẬP.
Dưới đây là tập dữ liệu về điểm số, chuyên cần và hành vi học tập của một lớp học (định dạng CSV).

--- TẬP DỮ LIỆU ---
{csv_data}

--- YÊU CẦU CỦA GIÁO VIÊN ---
{yeu_cau_ai if yeu_cau_ai else 'Phân tích toàn diện chất lượng lớp học.'}

--- NHIỆM VỤ CỦA BẠN ---
Dựa trên dữ liệu trên, hãy lập một báo cáo phân tích sâu sắc, chia thành 3 phần rõ ràng:

### 📊 1. Phân tích Mô tả (Tổng quan)
- Nhận xét về phổ điểm, điểm trung bình chung, mức độ đồng đều của lớp.
- Chỉ ra các xu hướng nổi bật (ví dụ: điểm chuyên cần có tỷ lệ thuận với tỷ lệ làm bài không).

### ⚠️ 2. Phân tích Dự đoán & Cảnh báo (Cần hành động ngay)
- **Gắn cờ ĐỎ:** Liệt kê đích danh những học sinh có nguy cơ rủi ro cao nhất (trượt môn, bỏ học, hoặc điểm quá thấp so với mặt bằng chung). Nêu rõ lý do (do nghỉ nhiều hay do năng lực).
- **Gắn cờ VÀNG:** Những học sinh có dấu hiệu sa sút cần chú ý.
- **Gắn cờ XANH:** Những cá nhân xuất sắc có khả năng bứt phá.

### 💡 3. Khuyến nghị Cá nhân hóa (Hành động Sư phạm)
- Gợi ý lộ trình can thiệp cho nhóm rủi ro (Nên gặp mặt riêng? Nhắc nhở phụ huynh? Giao bài tập bù?).
- Gợi ý cách điều chỉnh phương pháp giảng dạy chung cho toàn lớp dựa trên phổ điểm này.

[KỶ LUẬT ĐỊNH DẠNG SỐNG CÒN]
- Trình bày mạch lạc bằng Markdown, sử dụng bảng nếu cần thiết để tóm tắt danh sách học sinh.
- Văn phong khách quan, đồng cảm nhưng thẳng thắn, bám sát 100% vào số liệu được cung cấp.
"""
                try:
                    engine_v2 = AIEngine2(default_model="gemini-2.5-pro")
                    result = engine_v2.generate_text(prompt, temperature=0.3) # Temperature thấp để phân tích số liệu chính xác
                    
                    if result.startswith("❌"):
                        st.error(result)
                    else:
                        st.session_state["analysis_result"] = result
                except Exception as e:
                    st.error(f"❌ Lỗi khi gọi AI: {e}")

    # ========================================================
    # KHU VỰC 4: KẾT QUẢ VÀ XUẤT BÁO CÁO
    # ========================================================
    if st.session_state.get("analysis_result"):
        st.markdown("---")
        st.markdown("### 📑 BÁO CÁO PHÂN TÍCH CHẤT LƯỢNG HỌC TẬP")
        st.markdown(st.session_state["analysis_result"], unsafe_allow_html=True)
        
        st.markdown("### 📥 Lưu trữ Báo cáo")
        if export_word is None:
            st.warning("⚠️ Module Word chưa sẵn sàng.")
        else:
            try:
                export_data = {
                    "ai_generated_content": st.session_state["analysis_result"],
                    "is_dkt": False
                }
                with st.spinner("Đang kết xuất file Word..."):
                    word_bytes = export_word(export_data)
                
                st.download_button(
                    label="📘 TẢI BÁO CÁO (.DOCX)",
                    data=word_bytes,
                    file_name="Bao_Cao_Phan_Tich_Lop_Hoc.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Lỗi xuất Word: {e}")
