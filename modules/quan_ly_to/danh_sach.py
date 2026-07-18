import streamlit as st
import pandas as pd

def seed_data_to_supabase():
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
    # 2. Chuyển đổi thành bảng dữ liệu (DataFrame)
    df = pd.DataFrame(ds_thanh_vien)
    
    # 3. Hiển thị bảng lên giao diện (Ẩn cột index của Pandas cho đẹp)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 4. Lưu tên giáo viên vào Session State để các thẻ khác (Phân công, Biên bản) gọi ra dùng chung
    st.session_state.danh_sach_gv = df["Họ và tên"].tolist()
    
    st.markdown("---")
    st.caption("💡 Mẹo: Danh sách này đã được lưu vào bộ nhớ tạm. Khi thầy qua thẻ 'Phân công', hệ thống sẽ tự động lấy các tên này ra để thầy xếp lịch.")
