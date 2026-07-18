import streamlit as st
import os.path
import base64
import json
from email.message import EmailMessage
import os
st.write("Thư mục hiện tại của app là: ", os.getcwd())
st.write("Các file đang thấy là: ", os.listdir())
# Thư viện của Google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Quyền truy cập: Chỉ đọc Email
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
def render_tom_tat_gmail(ai_engine):
    st.markdown("### 📧 Đọc và Tóm tắt Văn bản / Email")
    st.caption("Trợ lý AI giúp đọc các email/công văn từ nhà trường và trích xuất ý chính, lịch công tác quan trọng.")

    tab_nhap, tab_api = st.tabs(["✍️ Xử lý Email thủ công", "🔗 Kết nối tài khoản Gmail"])

    # --- TAB 1: NHẬP THỦ CÔNG (Giữ nguyên như cũ) ---
    with tab_nhap:
        col_input, col_options = st.columns([2, 1])
        with col_input:
            email_content = st.text_area("Dán nội dung Email / Công văn vào đây:", height=250)
        with col_options:
            st.markdown("**Mục tiêu phân tích:**")
            yeu_cau = st.radio("AI sẽ tập trung tìm kiếm:", [
                "📝 Tóm tắt gọn gàng ý chính",
                "⏰ Trích xuất Hạn chót (Deadlines)",
                "✅ Liệt kê công việc cần làm"
            ])
            btn_tom_tat = st.button("🪄 Phân tích bằng AI", type="primary", use_container_width=True)

        if btn_tom_tat and email_content:
            with st.spinner("AI đang đọc văn bản..."):
                prompt = f"Là thư ký Tổ chuyên môn, hãy đọc nội dung sau và {yeu_cau}. Trình bày ngắn gọn bằng gạch đầu dòng, bôi đậm hạn chót/nhiệm vụ.\n\nNội dung:\n{email_content}"
                try:
                    summary = ai_engine.generate_text(prompt)
                    st.success("✅ Đã xử lý xong!")
                    with st.container(border=True):
                        st.markdown(summary)
                except Exception as e:
                    st.error(f"Lỗi AI: {e}")

    # --- TAB 2: KẾT NỐI TRỰC TIẾP GMAIL ---
    with tab_api:
        st.markdown("#### 📥 Quét Hộp thư đến (Inbox)")
        st.info("Hệ thống sẽ kết nối với Gmail để lấy 5 email mới nhất và nhờ AI tổng hợp công việc.")
        
        if st.button("🚀 Kết nối & Tải Email mới nhất", type="primary"):
            service = get_gmail_service()
            if service:
                with st.spinner("Đang tải dữ liệu từ Gmail..."):
                    try:
                        # Gọi API lấy ID của 5 email mới nhất
                        results = service.users().messages().list(userId='me', maxResults=5).execute()
                        messages = results.get('messages', [])

                        if not messages:
                            st.warning("Hộp thư của thầy trống!")
                        else:
                            st.success("✅ Đã tải thành công 5 email mới nhất!")
                            
                            for idx, message in enumerate(messages):
                                # Lấy chi tiết từng email
                                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                                
                                # Lấy tiêu đề (Subject) và Người gửi (From)
                                headers = msg['payload'].get('headers', [])
                                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "Không có tiêu đề")
                                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Không rõ người gửi")
                                
                                # Bóc tách nội dung email (Snippet - Đoạn trích ngắn do Google tự tạo)
                                snippet = msg.get('snippet', '')

                                with st.expander(f"📧 Thư {idx + 1}: {subject}", expanded=False):
                                    st.markdown(f"**Từ:** `{sender}`")
                                    st.markdown(f"**Nội dung sơ lược:** {snippet}...")
                                    
                                    # Nút yêu cầu AI tóm tắt chính email này
                                    if st.button("🪄 Nhờ AI trích xuất nhiệm vụ email này", key=f"btn_ai_{idx}"):
                                        with st.spinner("AI đang phân tích..."):
                                            prompt_gmail = f"Hãy tóm tắt ngắn gọn và liệt kê các công việc/hạn chót cần làm từ email sau. Tiêu đề: {subject}. Người gửi: {sender}. Nội dung: {snippet}"
                                            kq_gmail = ai_engine.generate_text(prompt_gmail)
                                            st.markdown("---")
                                            st.markdown("🤖 **AI Phân tích:**")
                                            st.info(kq_gmail)
                    except Exception as e:
                        st.error(f"Lỗi khi tải thư: {e}")
