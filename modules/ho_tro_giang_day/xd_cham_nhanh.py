import streamlit as st
import pandas as pd
import json
from pathlib import Path

# Hàm đọc file (thầy đảm bảo hàm này có trong module hoặc import từ utils)
def extract_text_from_file(uploaded_file):
    # Sử dụng logic đọc PDF/DOCX/TXT đã thiết kế trước đó
    return "Nội dung bài làm mẫu..." 

def render_xd_cham_nhanh(ai_engine):
    st.markdown("### ⚡ Chấm bài nhanh hàng loạt (TN & TL)")
    
    # 1. Cấu hình bảng điểm
    col_a, col_b = st.columns(2)
    with col_a:
        diem_tn = st.number_input("Tổng điểm TN (ví dụ: 5.0):", value=5.0, step=0.1)
        dap_an_tn = st.text_area("Nhập Đáp án Trắc nghiệm (ví dụ: 1A, 2B, 3C...):", height=100)
    with col_b:
        diem_tl = st.number_input("Tổng điểm TL (ví dụ: 5.0):", value=5.0, step=0.1)
        tieu_chi_tl = st.text_area("Nhập Tiêu chí/Đáp án Tự luận:", height=100)
    
    uploaded_files = st.file_uploader("Tải lên bài làm của HS (hàng loạt):", accept_multiple_files=True, type=["pdf", "docx", "txt"])
    
    if st.button("🚀 XỬ LÝ CHẤM LÔ (BATCH PROCESS)", type="primary", use_container_width=True):
        if not uploaded_files or not dap_an_tn or not tieu_chi_tl:
            st.error("⚠️ Vui lòng nhập đầy đủ đáp án cả 2 phần và tải file bài làm!")
        else:
            ket_qua_list = []
            with st.spinner(f"⏳ Đang chấm {len(uploaded_files)} bài làm..."):
                for file in uploaded_files:
                    content = extract_text_from_file(file)
                    
                    # Prompt ép AI trả về dữ liệu cấu trúc
                    prompt = f"""
                    Bạn là giáo viên. Hãy chấm bài làm này theo hai phần độc lập:
                    1. Phần Trắc nghiệm (Tổng {diem_tn}đ): So sánh với đáp án: {dap_an_tn}
                    2. Phần Tự luận (Tổng {diem_tl}đ): Chấm dựa trên tiêu chí: {tieu_chi_tl}
                    
                    Yêu cầu trả về JSON duy nhất có cấu trúc:
                    {{"diem_tn": (float), "diem_tl": (float), "tong_diem": (float), "nhan_xet": "..."}}
                    
                    Bài làm học sinh: {content}
                    """
                    
                    try:
                        res = ai_engine.generate_text(prompt)
                        # Trích xuất JSON từ phản hồi (giả định AI trả về chuỗi JSON)
                        data = json.loads(res.replace("```json", "").replace("```", "").strip())
                        ket_qua_list.append({
                            "Tên HS/File": file.name,
                            "Điểm TN": data["diem_tn"],
                            "Điểm TL": data["diem_tl"],
                            "Tổng điểm": data["diem_tn"] + data["diem_tl"],
                            "Nhận xét": data["nhan_xet"]
                        })
                    except Exception as e:
                        ket_qua_list.append({"Tên HS/File": file.name, "Điểm TN": 0, "Điểm TL": 0, "Tổng điểm": 0, "Nhận xét": "Lỗi xử lý AI"})
            
            # 2. Hiển thị bảng tổng hợp
            st.markdown("---")
            df = pd.DataFrame(ket_qua_list)
            st.dataframe(df, use_container_width=True)
            
            # Xuất Excel
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải bảng điểm tổng hợp (CSV)", csv, "Bang_diem_tong_hop.csv", "text/csv")
