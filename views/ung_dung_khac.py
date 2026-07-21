# -*- coding: utf-8 -*-
import streamlit as st

def render_ung_dung_khac():
    st.markdown("## 🛠️ Phân hệ: Ứng dụng khác")
    st.markdown("Danh sách các thẻ chức năng tích hợp trong hệ thống:")
    st.divider()

    # Tạo danh sách 10 thẻ chức năng
    danh_sach_the = [
        {"id": 1, "ten": "Thẻ chức năng số 1", "mô_tả": "Mô tả ngắn gọn cho chức năng 1."},
        {"id": 2, "ten": "Thẻ chức năng số 2", "mô_tả": "Mô tả ngắn gọn cho chức năng 2."},
        {"id": 3, "ten": "Thẻ chức năng số 3", "mô_tả": "Mô tả ngắn gọn cho chức năng 3."},
        {"id": 4, "ten": "Thẻ chức năng số 4", "mô_tả": "Mô tả ngắn gọn cho chức năng 4."},
        {"id": 5, "ten": "Thẻ chức năng số 5", "mô_tả": "Mô tả ngắn gọn cho chức năng 5."},
        {"id": 6, "ten": "Thẻ chức năng số 6", "mô_tả": "Mô tả ngắn gọn cho chức năng 6."},
        {"id": 7, "ten": "Thẻ chức năng số 7", "mô_tả": "Mô tả ngắn gọn cho chức năng 7."},
        {"id": 8, "ten": "Thẻ chức năng số 8", "mô_tả": "Mô tả ngắn gọn cho chức năng 8."},
        {"id": 9, "ten": "Thẻ chức năng số 9", "mô_tả": "Mô tả ngắn gọn cho chức năng 9."},
        {"id": 10, "ten": "Thẻ chức năng số 10", "mô_tả": "Mô tả ngắn gọn cho chức năng 10."},
    ]

    # Hiển thị dạng lưới (Grid) 3 cột cho trực quan, đẹp mắt
    cols = st.columns(3)
    
    for index, the in enumerate(danh_sach_the):
        col = cols[index % 3]
        with col:
            with st.container(border=True):
                st.markdown(f"#### 📌 Thẻ {the['id']}")
                st.write(f"**{the['ten']}**")
                st.caption(the['mô_tả'])
                
                # Nút bấm tương tác cho từng thẻ
                if st.button(f"Truy cập #{the['id']}", key=f"btn_the_{the['id']}", use_container_width=True):
                    st.info(f"Thầy đang mở giao diện của **{the['ten']}**.")
