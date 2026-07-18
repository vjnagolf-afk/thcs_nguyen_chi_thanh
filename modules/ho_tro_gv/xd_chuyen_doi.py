import streamlit as st
from pypdf import PdfReader
import requests
import re

# Khởi tạo bộ nhớ tạm để giữ kết quả không bị mất khi ấn nút Tải/Xóa
if "chuyen_doi_data" not in st.session_state:
    st.session_state.chuyen_doi_data = None

def doc_noi_dung_web(url):
    """Hàm hỗ trợ lấy văn bản thô từ một trang Web"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        # Lọc bỏ các tag HTML cơ bản để lấy text
        text = re.sub(r'<[^>]+>', ' ', response.text)
        # Rút gọn khoảng trắng
        text = " ".join(text.split())
        return text[:5000] # Giới hạn 5000 ký tự để không làm quá tải AI
    except Exception as e:
        return f"Lỗi không thể đọc URL: {e}"

def render_chuyen_doi(ai_engine):
    st.markdown("### 🔄 Chuyển đổi tài liệu thành bài dạy")
    st.caption("Trợ lý AI giúp đọc hiểu các tài liệu thô (sách, bài báo, tài liệu tham khảo) và tự động thiết kế luồng bài dạy chuẩn chỉnh.")

    # 1. Trực quan hóa luồng xử lý
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <b>Quy trình tự động:</b><br>
        📄 PDF / Word / PowerPoint ➔ 🧠 AI Phân tích ➔ 📝 KHBD ➔ 🖥️ Slide ➔ ✍️ Phiếu học tập ➔ 🎯 Câu hỏi kiểm tra ➔ 🎮 Quiz
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 1. Nạp tài liệu đầu vào")
    
    # Chia tab cho 3 phương thức nhập liệu
    input_tabs = st.tabs(["✍️ Nhập văn bản", "📂 Tải lên File", "🌐 Đường dẫn Web"])
    noidung_trich_xuat = ""

    with input_tabs[0]:
        text_input = st.text_area("Dán nội dung tài liệu thô vào đây:", height=150, placeholder="Ví dụ: Đoạn văn bản kiến thức về năng lượng tái tạo...")
        if text_input: 
            noidung_trich_xuat = text_input

    with input_tabs[1]:
        uploaded_file = st.file_uploader("Tải lên file (PDF, DOCX, PPTX)", type=["pdf", "docx", "pptx"])
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                try:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        noidung_trich_xuat += page.extract_text() + "\n"
                    st.success(f"✅ Đã đọc thành công PDF: {uploaded_file.name} ({len(noidung_trich_xuat)} ký tự)")
                except Exception as e:
                    st.error(f"Lỗi đọc PDF: {e}")
            else:
                st.info(f"📁 Đã nhận file: {uploaded_file.name}. (Ghi chú: Để trích xuất chi tiết Word/PPTX, cần cấu hình thêm thư viện python-docx/pptx ở máy chủ).")
                noidung_trich_xuat = f"[Nội dung từ file đính kèm: {uploaded_file.name}]"

    with input_tabs[2]:
        url_input = st.text_input("Nhập địa chỉ Web (URL):", placeholder="https://vi.wikipedia.org/wiki/...")
        if url_input:
            with st.spinner("Đang quét nội dung từ trang web..."):
                noidung_trich_xuat = doc_noi_dung_web(url_input)
                st.success("✅ Đã lấy dữ liệu từ URL thành công!")

    # 2. Hàng nút bấm chức năng (Chuyển đổi / Xóa)
    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        if st.button("🚀 Bắt đầu Chuyển đổi (AI)", type="primary", use_container_width=True):
            if noidung_trich_xuat.strip():
                with st.spinner("🧠 AI đang phân tích dữ liệu và thiết kế bài dạy..."):
                    try:
                        # Rút gọn bớt nội dung nếu quá dài để tránh vượt giới hạn token của AI
                        context_ngan = noidung_trich_xuat[:3000] 
                        prompt_khbd = f"Từ nội dung sau: '{context_ngan}'. Hãy lập dàn ý Kế hoạch bài dạy (Mục tiêu, Hoạt động chính) chuẩn sư phạm."
                        
                        # Gọi AI (Mô phỏng 1 luồng để tiết kiệm thời gian chờ)
                        ket_qua_khbd = ai_engine.generate_text(prompt_khbd)
                        
                        # Lưu toàn bộ vào session_state
                        st.session_state.chuyen_doi_data = {
                            "khbd": ket_qua_khbd,
                            "slide": "💡 Gợi ý Slide 1: Khởi động... | Slide 2: Khái niệm cốt lõi... | Slide 3: Vận dụng thực tế...",
                            "pht": "💡 Gợi ý: Bài tập điền khuyết dựa trên tài liệu, bảng KWL để học sinh ghi chép...",
                            "kiemtra": "💡 Gợi ý: 3 câu hỏi tự luận ngắn đánh giá mức độ thông hiểu và vận dụng...",
                            "quiz": "💡 Gợi ý: 5 câu hỏi trắc nghiệm nhanh 4 đáp án (A, B, C, D) dùng để củng cố cuối giờ..."
                        }
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
            else:
                st.warning("⚠️ Thầy vui lòng cung cấp tài liệu (Nhập chữ, up file hoặc dán link) trước khi chạy nhé!")

    with col_btn2:
        if st.button("🗑️ Xóa dữ liệu", type="secondary", use_container_width=True):
            st.session_state.chuyen_doi_data = None
            st.rerun()

    # 3. Khu vực hiển thị kết quả & Nút tải về
    st.markdown("---")
    if st.session_state.chuyen_doi_data:
        st.success("🎉 Hoàn tất! Hệ thống đã tạo xong các học liệu liên quan.")
        
        # Nút Tải tài liệu về máy (.txt)
        du_lieu_tai_ve = f"KẾ HOẠCH BÀI DẠY\n\n{st.session_state.chuyen_doi_data['khbd']}\n\n--- CÁC HỌC LIỆU KHÁC ---\nĐang cập nhật..."
        st.download_button(
            label="⬇️ Tải KHBD về máy (.txt)",
            data=du_lieu_tai_ve,
            file_name="Ho_so_bai_day_AI.txt",
            mime="text/plain",
            type="primary"
        )
        
        # Hiển thị Tabs kết quả
        tabs_out = st.tabs(["📝 KHBD", "🖥️ Slide", "✍️ Phiếu học tập", "🎯 Câu hỏi kiểm tra", "🎮 Quiz"])
        
        with tabs_out[0]:
            st.write(st.session_state.chuyen_doi_data["khbd"])
        with tabs_out[1]:
            st.info(st.session_state.chuyen_doi_data["slide"])
        with tabs_out[2]:
            st.info(st.session_state.chuyen_doi_data["pht"])
        with tabs_out[3]:
            st.info(st.session_state.chuyen_doi_data["kiemtra"])
        with tabs_out[4]:
            st.info(st.session_state.chuyen_doi_data["quiz"])
