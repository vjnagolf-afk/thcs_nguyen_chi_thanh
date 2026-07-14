import streamlit as st
import pandas as pd

def render_danh_sach():
    st.markdown("### 👥 Danh sách thành viên")
    # Tạm thời hiển thị dữ liệu mẫu
    data = {"Họ và tên": ["Nguyễn Văn A", "Trần Thị B"], "Chức vụ": ["Tổ trưởng", "Thư ký"]}
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
