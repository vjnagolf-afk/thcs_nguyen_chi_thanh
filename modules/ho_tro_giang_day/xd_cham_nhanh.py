import streamlit as st
import pandas as pd
from pathlib import Path

def render_xd_cham_nhanh(ai_engine):
    st.markdown("### ⚡ Chấm bài nhanh hàng loạt (TN & TL)")
    
    # 1. Cấu hình bài kiểm tra
    c1, c2, c3 = st.columns(3)
    loai_bai = c1.selectbox("Loại bài:", ["Hỗn hợp (TN & TL)", "100% Trắc nghiệm", "100% Tự luận"])
    diem_tn = c2.number_input("Tổng điểm Trắc nghiệm:", value=5.0, step=0.1)
    diem_tl = c3.number_input("Tổng điểm Tự luận:", value=5.0, step=0.1)
    
    # Khu vực tải file (Hỗ trợ nhiều file cùng lúc)
    uploaded_files = st.file_uploader("Tải lên các file bài làm (PDF/DOCX/TXT):", accept_multiple_files=True, type=["pdf", "docx", "txt"])
    
    dap_an = st.text_area("Nhập Đáp án TN hoặc Tiêu chí chấm Tự luận:")
    
    if st.button("🚀 XỬ LÝ CHẤM LÔ (BATCH PROCESS)", type="primary"):
        if not uploaded_files or not dap_an:
            st.error("⚠️ Vui lòng tải file bài làm và nhập đáp án/tiêu chí!")
        else:
            ket_qua_list = []
            
            with st.spinner(f"⏳ Đang chấm {len(uploaded_files)} bài làm..."):
                for file in uploaded_files:
                    # Đọc nội dung (giả định dùng hàm extract_text_from_file đã có)
                    content = "Nội dung bài làm..." # Thầy sử dụng lại hàm extract_text_from_file ở các module trước
                    
                    prompt = f"""
                    Bạn là giáo viên. Hãy chấm bài làm này theo cấu trúc:
                    - Loại bài: {loai_bai}
                    - Đáp án/Tiêu chí: {dap_an}
                    - Trắc nghiệm: {diem_tn} điểm, Tự luận: {diem_tl} điểm.
                    
                    Trả về JSON duy nhất với keys: "diem_tn", "diem_tl", "tong_diem", "nhan_xet".
                    Bài làm: {content}
                    """
                    
                    # Gọi AI
                    try:
                        res = ai_engine.generate_text(prompt) # Cần xử lý parse JSON từ res
                        ket_qua_list.append({"Tên file": file.name, "Kết quả": res})
                    except Exception as e:
                        ket_qua_list.append({"Tên file": file.name, "Kết quả": f"Lỗi: {e}"})
            
            # 2. Hiển thị bảng tổng hợp
            st.markdown("### 📊 Kết quả chấm")
            df = pd.DataFrame(ket_qua_list)
            st.dataframe(df, use_container_width=True)
            
            # Xuất Excel
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Tải bảng điểm (CSV)", csv, "Bang_diem.csv", "text/csv")
