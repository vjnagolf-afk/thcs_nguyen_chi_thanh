import streamlit as st
import pandas as pd
from utils.db_connector import db

def render_user_management():
    st.markdown("### 🛡️ Trung tâm phê duyệt giáo viên (Admin Control)")
    
    # Lấy danh sách toàn bộ người dùng từ bảng profiles
    try:
        profiles = db.fetch_all("profiles")
        df = pd.DataFrame(profiles)
    except Exception as e:
        st.error(f"Không thể tải danh sách người dùng: {e}")
        return

    if df.empty:
        st.info("Chưa có giáo viên nào đăng ký tài khoản.")
        return

    # Hiển thị bảng danh sách
    st.dataframe(df[['email', 'status', 'role']], use_container_width=True)

    st.markdown("---")
    st.markdown("#### ⚙️ Thao tác duyệt nhanh")
    
    # Chọn giáo viên cần thao tác
    target_email = st.selectbox("Chọn email giáo viên:", df['email'].tolist())
    
    col1, col2, col3 = st.columns(3)
    
    if col1.button("✅ Duyệt (Active)"):
        db.client.table("profiles").update({"status": "active"}).eq("email", target_email).execute()
        st.success(f"Đã duyệt tài khoản: {target_email}")
        st.rerun()
        
    if col2.button("🚫 Khóa (Blocked)"):
        db.client.table("profiles").update({"status": "blocked"}).eq("email", target_email).execute()
        st.warning(f"Đã khóa tài khoản: {target_email}")
        st.rerun()
        
    if col3.button("🗑️ Xóa tài khoản"):
        # Lấy ID trước khi xóa
        user_id = df[df['email'] == target_email]['id'].values[0]
        db.client.table("profiles").delete().eq("id", user_id).execute()
        st.error(f"Đã xóa tài khoản: {target_email}")
        st.rerun()
