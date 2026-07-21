# -*- coding: utf-8 -*-
import streamlit as st

def render_ung_dung_khac():
    # Tiêu đề phân hệ đồng bộ giao diện hệ thống
    st.markdown("## 🛠️ Phân hệ: Ứng dụng khác")
    st.divider()

    # Danh sách 10 thẻ chức năng hiển thị dạng thanh tab ngang
    tab_titles = [
        "Thẻ 1", "Thẻ 2", "Thẻ 3", "Thẻ 4", "Thẻ 5", 
        "Thẻ 6", "Thẻ 7", "Thẻ 8", "Thẻ 9", "Thẻ 10"
    ]
    
    # Khởi tạo thanh tabs ngang
    tabs = st.tabs(tab_titles)

    # Xây dựng nội dung tương ứng cho từng thẻ khi giáo viên bấm vào
    for idx, tab in enumerate(tabs):
        the_id = idx + 1
        with tab:
            st.markdown(f"### 📝 Không gian làm việc: Thẻ chức năng số {the_id}")
            st.write(f"Thầy đang thao tác trên giao diện của **Thẻ {the_id}** trong phân hệ Ứng dụng khác.")
            
            # Khung vùng chứa tính năng riêng biệt cho từng thẻ
            with st.container(border=True):
                st.info(f"Khu vực nhập liệu và xử lý nghiệp vụ dành riêng cho Thẻ {the_id}.")
                
                # Ví dụ minh họa form/nút bấm tương tác trong thẻ
                col1, col2 = st.columns(2)
                col1.text_input(f"Nhập tham số cho Thẻ {the_id}", key=f"input_the_{the_id}")
                if col2.button(f"🚀 Thực thi Thẻ {the_id}", key=f"btn_exec_{the_id}", type="primary"):
                    st.success(f"Đã xử lý xong dữ liệu cho Thẻ {the_id}!")
