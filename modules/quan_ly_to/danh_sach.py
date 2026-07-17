import streamlit as st
import pandas as pd
import time

def load_danh_sach_data(db):
    """Hàm lấy dữ liệu từ bảng quan_ly_tcm trên Supabase"""
    try:
        response = db.table("quan_ly_tcm").select("*").order("id").execute()
        if not response.data:
            return pd.DataFrame()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Lỗi kết nối CSDL Supabase: {e}")
        return pd.DataFrame()

def seed_data_to_supabase(db):
    """Hàm đẩy danh sách 10 giáo viên mặc định lên Supabase"""
    data = [
        {"ten": "Lê Hồng Dưỡng", "ngay_sinh": "1976", "bang_cap": "ĐH", "chu_the": "KHTN (Lý) - CN", "vai_tro": "Tổ trưởng", "email": "vjnagolf@gmail.com", "dien_thoai": "0984331178"},
        {"ten": "Nguyễn Thị Huyền Trang", "ngay_sinh": "1983", "bang_cap": "Thạc sĩ", "chu_the": "KHTN (Lý) - CN", "vai_tro": "Giáo viên", "email": "nguyenvana@gmail.com", "dien_thoai": "0909123457"},
        {"ten": "Lý Nguyễn Thu Nhi", "ngay_sinh": "1979", "bang_cap": "ĐH", "chu_the": "KHTN (Lý) - CN", "vai_tro": "Giáo viên", "email": "nguyenvana@gmail.com", "dien_thoai": "0909123458"},
        {"ten": "Khương Thị Thúy Vân", "ngay_sinh": "1979", "bang_cap": "ĐH", "chu_the": "KHTN (Sinh)", "vai_tro": "Giáo viên", "email": "nguyenvana@gmail.com", "dien_thoai": "0909123460"},
        {"ten": "Trần Xuân Hạnh", "ngay_sinh": "1985", "bang_cap": "ĐH", "chu_the": "GDTC", "vai_tro": "Giáo viên", "email": "nguyenvana@gmail.com", "dien_thoai": "0909123461"},
        {"ten": "Trương Vĩnh Văn", "ngay_sinh": "1981", "bang_cap": "ĐH", "chu_the": "KHTN (Sinh) - GDTC", "vai_tro": "Giáo viên", "email": "nguyenvana@gmail.com", "dien_thoai": "0909123462"},
        {"ten": "Phạm Xuân Thọ", "ngay_sinh": "1979", "bang_cap": "ĐH", "chu_the": "KHTN (Sinh) - GDTC", "vai_tro": "Giáo viên", "email": "nguyenvana@gmail.com", "dien_thoai": "0909123463"},
        {"ten": "Lê Hùng Cường", "ngay_sinh": "1988", "bang_cap": "ĐH", "chu_the": "KHTN (Lý) - CN", "vai_tro": "Giáo viên", "email": "nguyenvana@gmail.com", "dien_thoai": "0909123464"},
        {"ten": "Phạm Thùy Ngoan", "ngay_sinh": "1980", "bang_cap": "ĐH", "chu_the": "KHTN (Hóa)", "vai_tro": "Giáo viên", "email": "nguyenvana@gmail.com", "dien_thoai": "0909123465"},
        {"ten": "Phạm Thị Minh Anh", "ngay_sinh": "2002", "bang_cap": "ĐH", "chu_the": "KHTN (Hóa-Sinh)", "vai_tro": "Giáo viên", "email": "nguyenvana@gmail.com", "dien_thoai": "0909123466"},
    ]
    try:
        db.table("quan_ly_tcm").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Lỗi khi đẩy dữ liệu: {e}")
        return False

def render_danh_sach(db):
    st.markdown("### 👥 Danh sách thành viên")
    st.info("📌 Dữ liệu thành viên được đồng bộ trực tiếp với Cơ sở dữ liệu đám mây (Supabase).")
    
    # Kéo dữ liệu từ Supabase về
    df_team = load_danh_sach_data(db)
    
    if not df_team.empty:
        # Nếu có dữ liệu thì hiển thị bảng
        st.dataframe(
            df_team, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "id": None, # Ẩn cột ID của hệ thống
                "created_at": None,
                "ten": "Họ và tên", 
                "ngay_sinh": "Năm sinh", 
                "bang_cap": "Bằng cấp", 
                "chu_the": "Môn dạy", 
                "vai_tro": "Vai trò", 
                "email": "Email", 
                "dien_thoai": "SĐT"
            }
        )
    else:
        # Nếu bảng trống (chưa có gì trên Supabase)
        st.warning("⚠️ Bảng dữ liệu quan_ly_tcm trên Supabase hiện đang trống!")
        if st.button("🚀 Đồng bộ 10 thành viên mặc định lên Supabase", type="primary"):
            with st.spinner("⏳ Đang lưu dữ liệu lên hệ thống..."):
                if seed_data_to_supabase(db):
                    st.success("🎉 Đã lưu thành công! Đang tải lại dữ liệu...")
                    time.sleep(1.5)
                    st.rerun()
