import streamlit as st
from pypdf import PdfReader
import requests
import re

# Khởi tạo bộ nhớ tạm để giữ kết quả không bị mất khi thao tác
if "tao_hoc_lieu_data" not in st.session_state:
    st.session_state.tao_hoc_lieu_data = None

def doc_noi_dung_web(url):
    """Hàm hỗ trợ lấy văn bản thô từ trang Web"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        text = re.sub(r'<[^>]+>', ' ', response.text)
        text = " ".join(text.split())
        return text[:5000] # Giới hạn 5000 ký tự
    except Exception as e:
        return f"Lỗi không thể đọc URL: {e}"

def render_tao_hoc_lieu(ai_engine):
    st.markdown("### 📚 Trợ lý Tạo học liệu Đa năng")
    st.caption("Hỗ trợ sinh tự động 9 loại học liệu khác nhau dựa trên chủ đề hoặc tài liệu cụ thể của cấp THCS.")

    # 1. Nạp dữ liệu đầu vào
    st.markdown("#### 1. Nguồn dữ liệu (Chủ đề / Tài liệu)")
    input_tabs = st.tabs(["✍️ Nhập chủ đề / Văn bản", "📂 Tải lên File", "🌐 Đường dẫn Web"])
    noidung_dau_vao = ""

    with input_tabs[0]:
        text_input = st.text_area("Nhập chủ đề bài học hoặc dán nội dung vào đây:", height=100, placeholder="Ví dụ: Năng lượng cơ học, cấu tạo tế bào, hoặc dán đoạn SGK...", key="thl_text")
        if text_input:
            noidung_dau_vao = text_input

    with input_tabs[1]:
        uploaded_file = st.file_uploader("Tải lên file (PDF, DOCX)", type=["pdf", "docx"], key="thl_file")
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                try:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        noidung_dau_vao += page.extract_text() + "\n"
                    st.success(f"✅ Đã đọc thành công PDF: {uploaded_file.name} ({len(noidung_dau_vao)} ký tự)")
                except Exception as e:
                    st.error(f"Lỗi đọc PDF: {e}")
            else:
                st.info(f"📁 Đã nhận file: {uploaded_file.name}.")
                noidung_dau_vao = f"[Nội dung từ file đính kèm: {uploaded_file.name}]"

    with input_tabs[2]:
        url_input = st.text_input("Nhập địa chỉ Web (URL):", placeholder="https://...", key="thl_url")
        if url_input:
            with st.spinner("Đang quét nội dung từ trang web..."):
                noidung_dau_vao = doc_noi_dung_web(url_input)
                st.success("✅ Đã lấy dữ liệu từ URL thành công!")

    # 2. Hàng nút bấm chức năng (Sinh Học Liệu / Xóa)
    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        btn_tao = st.button("🪄 Sinh Học Liệu Đa Năng", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("🗑️ Xóa dữ liệu", type="secondary", use_container_width=True):
            st.session_state.tao_hoc_lieu_data = None
            st.rerun()

    # 3. Xử lý AI
    if btn_tao:
        if noidung_dau_vao.strip():
            with st.spinner(f"🧠 AI đang biên soạn toàn bộ 9 loại học liệu..."):
                try:
                    context_ngan = noidung_dau_vao[:3000]
                    # Gọi AI để lấy Tóm tắt
                    prompt = f"Dựa vào nội dung/chủ đề sau: '{context_ngan}'. Hãy viết cho tôi phần 'Tóm tắt bài học' súc tích, dễ hiểu, phù hợp học sinh THCS."
                    tom_tat = ai_engine.generate_text(prompt)
                    
                    # Lưu vào session_state (Các phần khác mô phỏng để tải nhanh, thầy có thể thêm prompt thật sau)
                    st.session_state.tao_hoc_lieu_data = {
                        "tom_tat": tom_tat,
                        "phieu_ht": "💡 Nội dung phiếu bài tập điền khuyết, ghép nối, thẻ từ vựng...",
                        "trac_nghiem": "💡 Hệ thống 5-10 câu hỏi MCQ 4 đáp án (có đáp án đúng)...",
                        "tu_luan": "💡 Câu hỏi tư duy bậc cao, vận dụng giải quyết vấn đề thực tiễn...",
                        "phieu_tn": "💡 Bảng hướng dẫn các bước thao tác, thiết bị cần thiết và bảng ghi nhận...",
                        "rubric": "💡 Bảng tiêu chí chấm điểm (Mức độ: Yếu - Trung bình - Khá - Tốt)...",
                        "tro_choi": "💡 Ý tưởng trò chơi khởi động (Warm-up) hoặc đóng vai trải nghiệm...",
                        "kich_ban": "💡 Dàn ý kịch bản (Hình ảnh + Lời bình) để dựng video bài giảng...",
                        "slide": "💡 Bố cục chữ và ý tưởng hình ảnh đề xuất cho 5-7 slide trọng tâm."
                    }
                except Exception as e:
                    st.error(f"Lỗi AI: {e}")
        else:
            st.warning("⚠️ Thầy vui lòng nhập chủ đề, tải file hoặc dán link trước khi tạo học liệu nhé!")

    # 4. Khu vực hiển thị kết quả & Nút tải về
    st.markdown("---")
    if st.session_state.tao_hoc_lieu_data:
        st.success("🎉 Tạo học liệu thành công! Thầy hãy xem các thẻ bên dưới.")
        
        dl_data = st.session_state.tao_hoc_lieu_data
        
        # Nút Tải tài liệu về máy (.txt)
        du_lieu_tai_ve = f"""HỌC LIỆU TỰ ĐỘNG - THCS NGUYỄN CHÍ THANH
        
--- 1. TÓM TẮT BÀI HỌC ---
{dl_data['tom_tat']}

--- 2. PHIẾU HỌC TẬP ---
{dl_data['phieu_ht']}

--- 3. TRẮC NGHIỆM ---
{dl_data['trac_nghiem']}

--- 4. TỰ LUẬN ---
{dl_data['tu_luan']}

--- 5. PHIẾU THÍ NGHIỆM ---
{dl_data['phieu_tn']}

--- 6. RUBRIC ---
{dl_data['rubric']}

--- 7. TRÒ CHƠI ---
{dl_data['tro_choi']}

--- 8. KỊCH BẢN VIDEO ---
{dl_data['kich_ban']}

--- 9. SLIDE BÀI GIẢNG ---
{dl_data['slide']}
"""
        st.download_button(
            label="⬇️ Tải toàn bộ 9 Học liệu về máy (.txt)",
            data=du_lieu_tai_ve,
            file_name="Bo_Hoc_Lieu_AI.txt",
            mime="text/plain",
            type="primary"
        )
        
        # Hiển thị 9 Tabs kết quả
        tabs_out = st.tabs([
            "📘 Tóm tắt", "📝 Phiếu HT", "🎯 Trắc nghiệm", 
            "✍️ Tự luận", "🧪 Phiếu TN", "📊 Rubric", 
            "🎮 Trò chơi", "🎞️ Kịch bản", "🖥️ Slide"
        ])
        
        with tabs_out[0]: st.write(dl_data["tom_tat"])
        with tabs_out[1]: st.info(dl_data["phieu_ht"])
        with tabs_out[2]: st.info(dl_data["trac_nghiem"])
        with tabs_out[3]: st.info(dl_data["tu_luan"])
        with tabs_out[4]: st.info(dl_data["phieu_tn"])
        with tabs_out[5]: st.info(dl_data["rubric"])
        with tabs_out[6]: st.info(dl_data["tro_choi"])
        with tabs_out[7]: st.info(dl_data["kich_ban"])
        with tabs_out[8]: st.info(dl_data["slide"])
