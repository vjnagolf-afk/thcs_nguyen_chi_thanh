import streamlit as st
import pandas as pd
import json

def render_xd_cham_nhanh(ai_engine):
    st.markdown("### ⚡ Chấm bài nhanh hàng loạt (Thiết lập linh hoạt)")
    
    # 1. Lựa chọn hình thức chấm
    hinh_thuc = st.selectbox("Chọn hình thức chấm bài:", ["Hỗn hợp (TN & TL)", "100% Trắc nghiệm", "100% Tự luận"])
    
    st.markdown("---")
    
    # 2. KHUNG NHẬP LIỆU LINH HOẠT
    dap_an_tn = ""
    diem_tn = 0
    tieu_chi_tl = ""
    diem_tl = 0
    file_tl_input = None

    if hinh_thuc == "Hỗn hợp (TN & TL)":
        c1, c2 = st.columns(2)
        with c1:
            diem_tn = st.number_input("Tổng điểm TN:", value=5.0, step=0.1)
            dap_an_tn = st.text_area("Đáp án Trắc nghiệm:")
        with c2:
            diem_tl = st.number_input("Tổng điểm TL:", value=5.0, step=0.1)
            tieu_chi_tl = st.text_area("Tiêu chí/Đáp án Tự luận:")
            file_tl_input = st.file_uploader("Tải file đáp án TL (Word/Ảnh):", type=["docx", "png", "jpg", "jpeg"])

    elif hinh_thuc == "100% Trắc nghiệm":
        diem_tn = st.number_input("Tổng điểm TN (100%):", value=10.0, step=0.1)
        dap_an_tn = st.text_area("Đáp án Trắc nghiệm:")

    elif hinh_thuc == "100% Tự luận":
        diem_tl = st.number_input("Tổng điểm TL (100%):", value=10.0, step=0.1)
        tieu_chi_tl = st.text_area("Tiêu chí/Đáp án Tự luận:")
        file_tl_input = st.file_uploader("Tải file đáp án TL (Word/Ảnh):", type=["docx", "png", "jpg", "jpeg"])

    uploaded_files = st.file_uploader("Tải bài làm của HS hàng loạt (PDF/DOCX/TXT):", accept_multiple_files=True, type=["pdf", "docx", "txt"])
    
    # 3. XỬ LÝ CHẤM BÀI
    if st.button("🚀 XỬ LÝ CHẤM LÔ (BATCH PROCESS)", type="primary"):
        if not uploaded_files:
            st.error("⚠️ Vui lòng tải bài làm của HS!")
        else:
            ket_qua_list = []
            with st.spinner("⏳ AI đang chấm bài..."):
                for file in uploaded_files:
                    # (Giả định hàm extract_text_from_file đã được import hoặc định nghĩa ở trên)
                    content = "Nội dung bài làm từ file..." 
                    
                    prompt = f"""
                    Chấm bài làm này theo hình thức: {hinh_thuc}.
                    - Đáp án TN: {dap_an_tn}
                    - Tiêu chí TL: {tieu_chi_tl}
                    - Điểm TN/TL: {diem_tn}/{diem_tl}
                    Trả về JSON: {{"diem_tn": 0.0, "diem_tl": 0.0, "tong_diem": 0.0, "nhan_xet": "..."}}
                    Bài làm: {content}
                    """
                    
                    try:
                        res = ai_engine.generate_text(prompt)
                        data = json.loads(res.replace("```json", "").replace("```", "").strip())
                        ket_qua_list.append({
                            "Tên HS": file.name,
                            "Điểm TN": data["diem_tn"],
                            "Điểm TL": data["diem_tl"],
                            "Tổng điểm": data["tong_diem"],
                            "Nhận xét": data["nhan_xet"]
                        })
                    except:
                        ket_qua_list.append({"Tên HS": file.name, "Tổng điểm": 0, "Nhận xét": "Lỗi"})
            
            st.dataframe(pd.DataFrame(ket_qua_list), use_container_width=True)
