import streamlit as st
import pandas as pd

def render_phan_cong(db):
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
        
    # 2. Form phân công nhiệm vụ
    with st.expander("➕ Thêm phân công mới", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            # Menu dropdown tự động lấy tên từ thẻ Danh sách
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
            
        nhiem_vu_khac = st.text_input("📌 Nhiệm vụ kiêm nhiệm (nếu có):", placeholder="VD: Chủ nhiệm 9A1, Bồi dưỡng HSG Lý 9, Thư ký Hội đồng...")
        
        if st.button("💾 Lưu phân công", type="primary"):
            # Thêm thông tin vào bảng tạm
            st.session_state.bang_phan_cong.append({
                "Giáo viên": gv_duoc_chon,
                "Môn giảng dạy": mon_day,
                "Số tiết": so_tiet,
                "Nhiệm vụ kiêm nhiệm": nhiem_vu_khac
            })
            st.success(f"✅ Đã lưu phân công cho giáo viên **{gv_duoc_chon}** thành công!")
            st.rerun()
            
    # 3. Hiển thị bảng tổng hợp
    st.markdown("---")
    if st.session_state.bang_phan_cong:
        st.markdown("#### 📋 Bảng tổng hợp Phân công hiện tại")
        
        # Chuyển đổi dữ liệu thành DataFrame để hiển thị đẹp hơn
        df_pc = pd.DataFrame(st.session_state.bang_phan_cong)
        st.dataframe(df_pc, use_container_width=True, hide_index=True)
        
        # Các nút tiện ích xuất file và xóa
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            # Chuyển DataFrame thành định dạng CSV để tải về máy
            csv = df_pc.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ Tải bảng phân công về máy (Excel/CSV)",
                data=csv,
                file_name='Bang_Phan_Cong_To_KHTN.csv',
                mime='text/csv',
                use_container_width=True
            )
        with col_btn2:
            if st.button("🗑️ Xóa làm lại từ đầu", type="secondary", use_container_width=True):
                st.session_state.bang_phan_cong = []
                st.rerun()
    else:
        st.info("💡 Hiện chưa có dữ liệu phân công nào. Thầy hãy tạo mới ở form phía trên nhé!")
