import streamlit as st
import pandas as pd
import io

def render_phan_cong(db):
    st.markdown("### 📋 Bảng Phân Công Chuyên Môn")
    
    # Đọc dữ liệu từ DB thông qua cổng db_connector
    try:
        data = db.fetch_all("phan_cong")
        df_pc = pd.DataFrame(data) if data else pd.DataFrame()
    except:
        df_pc = pd.DataFrame()

    if not df_pc.empty:
        st.dataframe(df_pc, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu phân công.")

    with st.expander("📤 CẬP NHẬT LỊCH TỪ EXCEL"):
        uploaded_pc = st.file_uploader("Upload bảng phân công (.xlsx)", type=["xlsx"])
        if uploaded_pc and st.button("💾 Lưu Bảng Phân Công"):
            df_new = pd.read_excel(uploaded_pc, dtype=str).fillna("")
            # Xóa cũ -> Lưu mới (qua db)
            db.client.table("phan_cong").delete().neq("ten_giao_vien", "XOA").execute()
            db.insert("phan_cong", df_new.to_dict(orient="records"))
            st.success("Đã đồng bộ!")
            st.rerun()
