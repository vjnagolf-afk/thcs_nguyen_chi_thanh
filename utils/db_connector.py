import streamlit as st
from supabase import create_client

class DBConnector:
    def __init__(self):
        self.url = st.secrets["SUPABASE_URL"]
        self.key = st.secrets["SUPABASE_KEY"]
        self.client = create_client(self.url, self.key)

    def get_table(self, table_name):
        return self.client.table(table_name)

    # Hàm tiện ích dùng chung cho toàn dự án
    def fetch_all(self, table_name):
        try:
            return self.client.table(table_name).select("*").execute().data
        except Exception as e:
            st.error(f"Lỗi truy xuất bảng {table_name}: {e}")
            return []

    def insert(self, table_name, data):
        return self.client.table(table_name).insert(data).execute()

    def delete(self, table_name, column, value):
        return self.client.table(table_name).delete().eq(column, value).execute()

# Khởi tạo singleton để dùng chung
db = DBConnector()
