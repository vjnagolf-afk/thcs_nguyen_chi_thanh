# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def render_tkb(db):
    st.subheader("📅 Quản lý Thời Khóa Biểu Toàn Trường")
    
    # Kiểm tra client Supabase từ db connector có sẵn trong hệ thống
    supabase = db.client if hasattr(db, 'client') else db
    
    if not supabase:
        st.error("🚨 Không thể kết nối tới cơ sở dữ liệu Supabase. Vui lòng kiểm tra lại cấu hình `db_connector`.")
        return

    # 1. Lấy danh sách các đợt TKB đã lưu
    try:
        response = supabase.table("tkb_batches").select("*").order("created_at", desc=True).execute()
        batches = response.data if response.data else []
    except Exception as e:
        batches = []

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📤 Tải lên đợt TKB mới")
        with st.form("upload_tkb_form", clear_on_submit=True):
            batch_name_input = st.text_input("Tên đợt TKB:", placeholder="Ví dụ: TKB số 7 - Học kỳ 2 (2025-2026)")
            uploaded_file = st.file_uploader("Chọn file Excel Thời khóa biểu (.xlsx)", type=["xlsx", "xls"])
            submit_btn = st.form_submit_button("Xử lý & Lưu lên Supabase", use_container_width=True)

            if submit_btn:
                if not batch_name_input or not uploaded_file:
                    st.warning("⚠️ Vui lòng nhập tên đợt và chọn file Excel!")
                else:
                    with st.spinner("Đang đọc file và lưu dữ liệu..."):
                        try:
                            # Đọc file Excel chính xác theo sheet đầu tiên
                            xls = pd.ExcelFile(uploaded_file)
                            df = pd.read_excel(xls, sheet_name=0, header=None)
                            
                            # Lưu đợt vào bảng tkb_batches
                            batch_res = supabase.table("tkb_batches").insert({"batch_name": batch_name_input}).execute()
                            if not batch_res.data:
                                st.error("❌ Không thể tạo đợt TKB mới trên CSDL.")
                                return
                            batch_id = batch_res.data[0]["id"]

                            # Phân tích dữ liệu từ hàng thứ 5 (index 4) giống cấu trúc mẫu
                            headers = df.iloc[4].tolist() if len(df) > 4 else []
                            rows_to_insert = []
                            current_thu = "2"

                            for i in range(5, len(df)):
                                row = df.iloc[i].tolist()
                                if not row or all(pd.isna(x) for x in row):
                                    continue

                                if not pd.isna(row[0]):
                                    current_thu = str(row[0]).strip()
                                
                                tiet = row[1] if len(row) > 1 and not pd.isna(row[1]) else ""
                                if not tiet:
                                    continue

                                for col_index in range(2, len(headers)):
                                    raw_header = headers[col_index]
                                    if pd.isna(raw_header):
                                        continue
                                    
                                    lop = str(raw_header).split('\n')[0].strip()
                                    cell_value = row[col_index] if col_index < len(row) else None

                                    if not pd.isna(cell_value):
                                        cell_str = str(cell_value).strip()
                                        last_dash_index = cell_str.rfind('-')
                                        
                                        mon_hoc = cell_str
                                        giao_vien = "Chưa phân công"

                                        if last_dash_index != -1:
                                            mon_hoc = cell_str[:last_dash_index].strip()
                                            giao_vien = cell_str[last_dash_index + 1:].strip()

                                        rows_to_insert.append({
                                            "batch_id": batch_id,
                                            "thu": str(current_thu),
                                            "tiet": str(tiet),
                                            "lop": lop,
                                            "mon_hoc": mon_hoc,
                                            "giao_vien": giao_vien
                                        })

                            if rows_to_insert:
                                chunk_size = 500
                                for j in range(0, len(rows_to_insert), chunk_size):
                                    chunk = rows_to_insert[j:j + chunk_size]
                                    supabase.table("tkb_details").insert(chunk).execute()

                            st.success("✅ Tải lên và đồng bộ Thời khóa biểu thành công!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"❌ Lỗi xử lý file: {ex}")

    with col2:
        st.markdown("### 📂 Chọn đợt TKB quản lý")
        if batches:
            batch_options = {b["batch_name"] + f" (Ngày tạo: {b['created_at'][:10]})": b["id"] for b in batches}
            selected_batch_name = st.selectbox("Danh sách các đợt:", list(batch_options.keys()))
            selected_batch_id = batch_options[selected_batch_name]

            if st.button("🗑️ Xóa đợt TKB đang chọn", type="secondary", use_container_width=True):
                try:
                    supabase.table("tkb_batches").delete().eq("id", selected_batch_id).execute()
                    st.success("✅ Đã xóa đợt TKB thành công!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"❌ Lỗi khi xóa: {ex}")
        else:
            selected_batch_id = None
            st.info("Chưa có đợt TKB nào được tải lên hệ thống.")

    # 3. Hiển thị dữ liệu TKB
    if selected_batch_id:
        st.markdown("---")
        try:
            detail_res = supabase.table("tkb_details").select("*").eq("batch_id", selected_batch_id).execute()
            tkb_data = detail_res.data if detail_res.data else []
        except Exception:
            tkb_data = []

        if tkb_data:
            df_tkb = pd.DataFrame(tkb_data)

            tab_chung, tab_gv = st.tabs(["📚 TKB Chung Toàn Trường", "👩‍🏫 Xem Theo Giáo Viên"])

            # GIAO DIỆN TKB CHUNG TOÀN TRƯỜNG (Giống Hình 2)
            with tab_chung:
                st.markdown("### 🏫 Bảng Thời Khóa Biểu Chung Toàn Trường")
                try:
                    # Tạo bảng pivot với hàng là (Thứ, Tiết) và cột là Lớp
                    pivot_chung = df_tkb.pivot_table(
                        index=["thu", "tiet"], 
                        columns="lop", 
                        values="mon_hoc", 
                        aggfunc=lambda x: ' / '.join(x)
                    ).fillna("")
                    st.dataframe(pivot_chung, use_container_width=True)
                except Exception as e:
                    # Fallback hiển thị bảng chi tiết nếu cấu trúc pivot gặp lỗi
                    st.dataframe(df_tkb[["thu", "tiet", "lop", "mon_hoc", "giao_vien"]], use_container_width=True, hide_index=True)

            # GIAO DIỆN XEM THEO GIÁO VIÊN (Giống Hình 1)
            with tab_gv:
                st.markdown("### 👩‍🏫 Lịch Giảng Dạy Chi Tiết Theo Giáo Viên")
                danh_sach_gv = sorted(list(df_tkb["giao_vien"].dropna().unique()))
                selected_teacher = st.selectbox("Chọn giáo viên:", danh_sach_gv)

                if selected_teacher:
                    df_gv = df_tkb[df_tkb["giao_vien"] == selected_teacher]
                    st.markdown(f"**Giáo viên: {selected_teacher}** (Tổng số tiết: {len(df_gv)})")
                    
                    try:
                        # Ghép Môn học và Lớp để hiển thị trong ô dạng 'Môn - Lớp' giống ảnh mẫu
                        df_gv["noi_dung"] = df_gv["mon_hoc"] + " - " + df_gv["lop"]
                        
                        # Pivot table: Hàng là Tiết (1 đến 5), Cột là Thứ (2 đến 7)
                        pivot_gv = df_gv.pivot_table(
                            index="tiet", 
                            columns="thu", 
                            values="noi_dung", 
                            aggfunc=lambda x: ' / '.join(x)
                        ).fillna("")
                        
                        # Đảm bảo các cột thứ sắp xếp đúng thứ tự nếu có
                        standard_days = ["2", "3", "4", "5", "6", "7"]
                        existing_cols = [c for c in standard_days if c in pivot_gv.columns]
                        other_cols = [c for c in pivot_gv.columns if c not in standard_days]
                        pivot_gv = pivot_gv[existing_cols + other_cols]
                        
                        st.dataframe(pivot_gv, use_container_width=True)
                    except Exception as e:
                        # Fallback bảng danh sách chi tiết nếu không pivot được
                        st.dataframe(df_gv[["thu", "tiet", "lop", "mon_hoc"]], use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Đợt TKB này chưa có dữ liệu chi tiết.")
