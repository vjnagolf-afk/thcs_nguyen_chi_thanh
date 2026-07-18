import streamlit as st
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def get_gmail_service():
    """Hàm xác thực dùng Streamlit Secrets"""
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # 1. Lấy thông tin từ Secrets
    if "GOOGLE_CREDENTIALS" not in st.secrets:
        st.error("🚨 Không tìm thấy cấu hình Google trong Secrets!")
        return None
    
    # Chuyển đổi định dạng từ secrets sang dict
    client_config = dict(st.secrets["GOOGLE_CREDENTIALS"])
    
    # 2. Tạo flow xác thực từ config
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    # 3. Chạy xác thực
    creds = flow.run_local_server(port=0)

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        st.error(f"Lỗi kết nối Gmail API: {e}")
        return None
