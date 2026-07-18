import streamlit as st
import pandas as pd

def render_danh_sach():
    st.markdown("### 👥 Danh sách thành viên Tổ chuyên môn")
    st.success("📌 Dữ liệu thành viên được đồng bộ 1 chiều từ mã nguồn hệ thống.")

    # 1. Khai báo danh sách giáo viên (Đã đổi key tiếng Việt để hiển thị lên bảng đẹp hơn)
    ds_thanh_vien = [
        {"Họ và tên": "Lê Hồng Dưỡng", "Năm sinh": "1976", "Bằng cấp": "ĐH", "Chuyên môn": "KHTN (Lý) - CN", "Nhiệm vụ": "Tổ trưởng", "Email": "vjnagolf@gmail.com", "Điện thoại": "0984331178"},
        {"Họ và tên": "Nguyễn Thị Huyền Trang", "Năm sinh": "1983", "Bằng cấp": "Thạc sĩ", "Chuyên môn": "KHTN (Lý) - CN", "Nhiệm vụ": "Giáo viên", "Email": "nguyenvana@gmail.com", "Điện thoại": "0909123457"},
        {"Họ và tên": "Lý Nguyễn Thu Nhi", "Năm sinh": "1979", "Bằng cấp": "ĐH", "Chuyên môn": "KHTN (Lý) - CN", "Nhiệm vụ": "Giáo viên", "Email": "nguyenvana@gmail.com", "Điện thoại": "0909123458"},
        {"Họ và tên": "Khương Thị Thúy Vân", "Năm sinh": "1979", "Bằng cấp": "ĐH", "Chuyên môn": "KHTN (Sinh)", "Nhiệm vụ": "Giáo viên", "Email": "nguyenvana@gmail.com", "Điện thoại": "0909123460"},
        {"Họ và tên": "Trần Xuân Hạnh", "Năm sinh": "1985", "Bằng cấp": "ĐH", "Chuyên môn": "GDTC", "Nhiệm vụ": "Giáo viên", "Email": "nguyenvana@gmail.com", "Điện thoại": "0909123461"},
        {"Họ và tên": "Trương Vĩnh Văn", "Năm sinh": "1981", "Bằng cấp": "ĐH", "Chuyên môn": "KHTN (Sinh) - GDTC", "Nhiệm vụ": "Giáo viên", "Email": "nguyenvana@gmail.com", "Điện thoại": "0909123462"},
        {"Họ và tên": "Phạm Xuân Thọ", "Năm sinh": "1979", "Bằng cấp": "ĐH", "Chuyên môn": "KHTN (Sinh) - GDTC", "Nhiệm vụ": "Giáo viên", "Email": "nguyenvana@gmail.com", "Điện thoại": "0909123463"},
        {"Họ và tên": "Lê Hùng Cường", "Năm sinh": "1988", "Bằng cấp": "ĐH", "Chuyên môn": "KHTN (Lý) - CN", "Nhiệm vụ": "Giáo viên", "Email": "nguyenvana@gmail.com", "Điện thoại": "0909123464"},
        {"Họ và tên": "Phạm Thùy Ngoan", "Năm sinh": "1980", "Bằng cấp": "ĐH", "Chuyên môn": "KHTN (Hóa)", "Nhiệm vụ": "Giáo viên", "Email": "nguyenvana@gmail.com", "Điện thoại": "0909123465"},
        {"Họ và tên": "Phạm Thị Minh Anh", "Năm sinh": "2002", "Bằng cấp": "ĐH", "Chuyên môn": "KHTN (Hóa-Sinh)", "Nhiệm vụ": "Giáo viên", "Email": "nguyenvana@gmail.com", "Điện thoại": "0909123466"},
    ]    
    
    # 2. Chuyển đổi thành bảng dữ liệu (DataFrame)
    df = pd.DataFrame(ds_thanh_vien)
    
    # 3. Hiển thị bảng lên giao diện (Ẩn cột index của Pandas cho đẹp)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 4. Lưu tên giáo viên vào Session State để các thẻ khác (Phân công, Biên bản) gọi ra dùng chung
    st.session_state.danh_sach_gv = df["Họ và tên"].tolist()
    
    st.markdown("---")
    st.caption("💡Danh sách được cập nhật thường xuyên.")
