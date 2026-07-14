user_data = db.get_user_profile(user_id)
if user_data['status'] == 'pending':
    st.warning("Tài khoản đang chờ duyệt...")
    st.stop() # Dừng lại, không cho load các tab khác
