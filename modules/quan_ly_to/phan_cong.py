# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import io

def render_phan_cong(db=None):
    st.markdown("### 🗓️ Phân công chuyên môn")
    
    # 1. Gọi danh sách giáo viên đã lưu từ thẻ "Danh sách"
    ds_gv = st.session_state.get("danh_sach_gv", [])
    
    if not ds_gv:
        st.warning("⚠️ Chưa có dữ liệu giáo viên. Thầy vui lòng nhấn sang thẻ 'Danh sách' một lần để hệ thống đồng bộ tên giáo viên trước nhé!")
        return
        
    st.caption("Tiện ích giao việc, phân công giảng dạy và kiêm nhiệm cho các thành viên trong tổ.")
    
    # Khởi tạo bộ nhớ tạm để lưu bảng phân công
    if "bang_phan_cong" not in st.session_state:
        st.session_state.bang_phan_cong = []

    # 2. KHU VỰC NHẬP LIỆU (CHIA 2 TABS)
    tab_thu_cong, tab_file = st.tabs(["✍️ Nhập thủ công", "📂 Tải lên từ File (Excel/CSV)"])
    
    # --- Tab 1: Nhập thủ công ---
    with tab_thu_cong:
        col1, col2, col3 = st.columns(3)
        with col1:
            gv_duoc_chon = st.selectbox("👨‍🏫 Chọn Giáo viên:", ds_gv)
        with col2:
            mon_day = st.selectbox("📚 Môn phụ trách chính:", [
                "KHTN 6", "KHTN 7", "KHTN 8", "KHTN 9", 
                "Tin học 6", "Tin học 7", "Tin học 8", "Tin học 9", 
                "Công nghệ 6", "Công nghệ 7", "Công nghệ 8", "Công nghệ 9",
                "GDTC", "Khác"
            ])
        with col3:
            so_tiet = st.number_input("⏱️ Số tiết/tuần:", min_value=1, max_value=30, value=4)
            
        nhiem_vu_khac = st.text_input("📌 Nhiệm vụ kiêm nhiệm (nếu có):", placeholder="VD: Chủ nhiệm 9A1, Bồi dưỡng HSG Lý 9...")
        
        if st.button("💾 Lưu phân công", type="primary", key="btn_luu_tc"):
            st.session_state.bang_phan_cong.append({
                "Giáo viên": gv_duoc_chon,
                "Môn giảng dạy": mon_day,
                "Số tiết": so_tiet,
                "Nhiệm vụ kiêm nhiệm": nhiem_vu_khac
            })
            st.success(f"✅ Đã thêm phân công cho giáo viên **{gv_duoc_chon}**!")
            st.rerun()

    # --- Tab 2: Upload File Hàng Loạt ---
    with tab_file:
        col_mau1, col_mau2 = st.columns([2, 1])
        with col_mau1:
            st.markdown("**Bước 1:** Tải file mẫu về máy, điền dữ liệu bằng Excel (Không đổi tên các cột).")
        with col_mau2:
            df_mau = pd.DataFrame({
                "Giáo viên": [ds_gv[0] if ds_gv else "Nguyễn Văn A"],
                "Môn giảng dạy": ["KHTN 9"],
                "Số tiết": [4],
                "Nhiệm vụ kiêm nhiệm": ["Tổ trưởng"]
            })
            csv_mau = df_mau.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ Tải File Mẫu (CSV)",
                data=csv_mau,
                file_name="File_Mau_Phan_Cong.csv",
                mime="text/csv",
                type="secondary",
                use_container_width=True
            )
            
        st.markdown("**Bước 2:** Tải file đã điền lên hệ thống (Hỗ trợ `.csv` hoặc `.xlsx`)")
        uploaded_file = st.file_uploader("Kéo thả file vào đây", type=["csv", "xlsx"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                
                cot_yeu_cau = ["Giáo viên", "Môn giảng dạy", "Số tiết", "Nhiệm vụ kiêm nhiệm"]
                if all(col in df_upload.columns for col in cot_yeu_cau):
                    st.success("✅ File hợp lệ! Xem trước dữ liệu bên dưới:")
                    st.dataframe(df_upload, use_container_width=True, hide_index=True)
                    
                    if st.button("🚀 Ghi đè dữ liệu lên hệ thống", type="primary", use_container_width=True):
                        st.session_state.bang_phan_cong = df_upload[cot_yeu_cau].to_dict('records')
                        st.rerun()
                else:
                    st.error(f"❌ File sai cấu trúc. Bắt buộc phải có các cột: {', '.join(cot_yeu_cau)}")
            except Exception as e:
                st.error(f"Có lỗi xảy ra khi đọc file: {e}. Vui lòng thử dùng định dạng .csv thay vì .xlsx nếu bị lỗi thư viện.")

    # 3. HIỂN THỊ BẢNG TỔNG HỢP
    st.markdown("---")
    if st.session_state.bang_phan_cong:
        st.markdown("#### 📋 Bảng tổng hợp Phân công hiện tại")
        
        df_pc = pd.DataFrame(st.session_state.bang_phan_cong)
        st.dataframe(df_pc, use_container_width=True, hide_index=True)
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            csv_export = df_pc.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ Tải bảng phân công về máy",
                data=csv_export,
                file_name='Bang_Phan_Cong_To_KHTN.csv',
                mime='text/csv',
                use_container_width=True
            )
        with col_btn2:
            if st.button("🗑️ Xóa toàn bộ dữ liệu", type="secondary", use_container_width=True, key="btn_xoa"):
                st.session_state.bang_phan_cong = []
                st.rerun()
    else:
        st.info("💡 Hiện chưa có dữ liệu phân công nào. Thầy hãy nhập thủ công hoặc tải file lên nhé!")
