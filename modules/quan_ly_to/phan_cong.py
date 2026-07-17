import streamlit as st
import pandas as pd
import io
import time

@st.cache_data
def get_phan_cong_template():
    """Hàm tạo file Excel mẫu ngay trong bộ nhớ để người dùng tải về"""
    df_mau = pd.DataFrame({
        "ten_giao_vien": ["Lê Hồng Dưỡng", "Nguyễn Thị Huyền Trang"],
        "mon_day": ["KHTN (Lý) - CN", "KHTN (Lý) - CN"],
        "lop_day": ["9A1, 9A2", "9A3, 9A4"],
        "so_tiet_tuan": [10, 12],
        "nhiem_vu_kiem_nhiem": ["Bồi dưỡng HSG", "CN Lớp 9A3"]
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_mau.to_excel(writer, index=False, sheet_name='Phan_Cong')
    return buffer.getvalue()

def load_phan_cong_data(db):
    """Hàm lấy dữ liệu từ bảng phan_cong trên Supabase"""
    try:
        response = db.table("phan_cong").select("*").execute()
        if not response.data:
            return pd.DataFrame()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Lỗi kết nối Cơ sở dữ liệu Supabase: {e}")
        return pd.DataFrame()

def render_phan_cong(db):
    st.markdown("### 📋 Bảng Phân Công Chuyên Môn")
    st.info("💡 Dữ liệu phân công được đồng bộ trực tiếp với Cơ sở dữ liệu đám mây (Supabase).")

    # 1. TẢI VÀ HIỂN THỊ DỮ LIỆU HIỆN TẠI
    df_pc_current = load_phan_cong_data(db)
    
    if not df_pc_current.empty:
        st.dataframe(
            df_pc_current, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "id": None,           # Ẩn cột id của hệ thống Supabase
                "created_at": None,   # Ẩn cột thời gian tạo
                "ten_giao_vien": "Giáo viên", 
                "mon_day": "Môn dạy", 
                "lop_day": "Lớp dạy", 
                "so_tiet_tuan": "Số tiết/tuần", 
                "nhiem_vu_kiem_nhiem": "Kiêm nhiệm"
            }
        )
    else:
        st.warning("⚠️ Chưa có dữ liệu phân công. Vui lòng cập nhật từ file Excel ở phía dưới.")

    st.markdown("---")

    # 2. KHU VỰC CẬP NHẬT TỪ EXCEL
    with st.expander("📤 CẬP NHẬT BẢNG PHÂN CÔNG (TỪ FILE EXCEL)", expanded=False):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**Bước 1: Tải file mẫu**")
            st.download_button(
                label="📥 Tải file Phân Công Mẫu (.xlsx)", 
                data=get_phan_cong_template(), 
                file_name="Mau_Phan_Cong.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        with col2:
            st.markdown("**Bước 2: Upload file đã điền**")
            uploaded_pc = st.file_uploader("Upload bảng phân công", type=["xlsx"], key="file_pc", label_visibility="collapsed")

        if uploaded_pc is not None:
            try:
                # Đọc file Excel người dùng tải lên
                df_pc = pd.read_excel(uploaded_pc, dtype=str).fillna("")
                cols_chuan = ["ten_giao_vien", "mon_day", "lop_day", "so_tiet_tuan", "nhiem_vu_kiem_nhiem"]
                
                # Kiểm tra xem file tải lên có đủ các cột chuẩn không
                if set(cols_chuan).issubset(df_pc.columns):
                    df_pc = df_pc[cols_chuan]
                    st.markdown("**Bản xem trước dữ liệu:**")
                    st.dataframe(df_pc, use_container_width=True)
                    
                    if st.button("💾 Lưu Lên Hệ Thống Supabase", type="primary"):
                        import_data = df_pc.to_dict(orient="records")
                        try:
                            with st.spinner("⏳ Đang đồng bộ lên Supabase..."):
                                # Xóa dữ liệu cũ (Dùng trick .neq() để xóa toàn bộ dữ liệu trong bảng)
                                db.table("phan_cong").delete().neq("ten_giao_vien", "XOA_DU_LIEU_CU").execute()
                                
                                # Thêm dữ liệu mới
                                db.table("phan_cong").insert(import_data).execute()
                            
                            st.success("🎉 Đã lưu thành công! Đang tải lại dữ liệu...")
                            time.sleep(1.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi khi lưu dữ liệu lên Supabase: {e}")
                else:
                    st.error(f"File Excel bị thiếu cột. Vui lòng đảm bảo có đủ 5 cột: {', '.join(cols_chuan)}")
            except Exception as e:
                st.error(f"Lỗi đọc file Excel: {e}")
