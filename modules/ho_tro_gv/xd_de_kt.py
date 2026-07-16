import streamlit as st
import sys
from pathlib import Path
from pypdf import PdfReader

# KHÔNG IMPORT WordExportEngine Ở ĐÂY ĐỂ CHỐNG LỖI KEYERROR

def render_xd_de_kt(ai_engine):
    st.markdown("### 📝 Xây dựng Đề kiểm tra & Ma trận (AI Hỗ trợ)")

    # 1. Bảng điều khiển (Control Panel)
    ds_mon = [
        "Ngữ văn", "Toán", "Ngoại ngữ", "Giáo dục công dân", "Lịch sử và Địa lý", 
        "Khoa học tự nhiên", "Vật lí", "Hoá học", "Sinh học", "Công nghệ", 
        "Tin học", "Giáo dục thể chất", "Nghệ thuật", "Giáo dục địa phương"
    ]

    col1, col2, col3, col4 = st.columns(4)
    mon_hoc = col1.selectbox("Môn học (Đề KT)", ds_mon)
    lop = col2.selectbox("Lớp (Đề KT)", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    thoi_gian = col3.selectbox("Thời gian làm bài", ["15 phút", "45 phút", "60 phút", "90 phút", "120 phút"], index=1)
    hinh_thuc = col4.selectbox("Hình thức", ["Trắc nghiệm & Tự luận", "100% Trắc nghiệm", "100% Tự luận"])
    
    c_tn, c_tl = st.columns(2)
    so_cau_tn = c_tn.number_input("Số câu Trắc nghiệm", min_value=0, max_value=100, value=12 if "Trắc nghiệm" in hinh_thuc else 0)
    so_cau_tl = c_tl.number_input("Số câu Tự luận", min_value=0, max_value=20, value=3 if "Tự luận" in hinh_thuc else 0)

    chu_de = st.text_input("Phạm vi kiến thức / Tên chủ đề cần kiểm tra", placeholder="VD: Định lý Thales, Lịch sử Việt Nam thế kỉ X...")
    yeu_cau_ma_tran = st.text_area(
        "Yêu cầu cụ thể & Mức độ (Tùy chọn)", 
        placeholder="VD: Ma trận 40% Nhận biết, 30% Thông hiểu, 20% Vận dụng, 10% Vận dụng cao. Có bảng ma trận đề..."
    )
    
    bam_sat = st.checkbox("Bám sát kiến thức từ file tài liệu tải lên", value=True)
    file_tai_len = st.file_uploader("Tài liệu tham khảo (Đề cương, bài học) - PDF/TXT", type=["pdf", "txt"], key="file_de_kt")

    # 2. Xử lý logic và Prompt
    c1, c2 = st.columns(2)
    if c1.button("🚀 SINH ĐỀ KIỂM TRA", type="primary"):
        if not chu_de.strip():
            st.error("⚠️ Vui lòng nhập Phạm vi kiến thức hoặc Chủ đề!")
        elif so_cau_tn == 0 and so_cau_tl == 0:
            st.error("⚠️ Vui lòng cấu hình số câu hỏi lớn hơn 0!")
        else:
            with st.spinner("⏳ AI đang phân tích ma trận và trộn đề..."):
                file_context = ""
                if file_tai_len and bam_sat:
                    try:
                        if file_tai_len.name.endswith('.pdf'):
                            reader = PdfReader(file_tai_len)
                            file_context = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                        elif file_tai_len.name.endswith('.txt'):
                            file_context = file_tai_len.read().decode("utf-8")
                    except Exception as e:
                        st.warning(f"Không thể đọc tài liệu: {e}")

                prompt = f"""
                Bạn là một giáo viên và chuyên gia khảo thí xuất sắc. Hãy xây dựng một Đề kiểm tra chuẩn sư phạm kèm Đáp án chi tiết.
                
                THÔNG TIN CHUNG:
                - Môn học: {mon_hoc}, Cấp độ: {lop}
                - Thời gian làm bài: {thoi_gian}
                - Phạm vi kiến thức/Chủ đề: '{chu_de}'
                - Hình thức: {hinh_thuc} (Gồm {so_cau_tn} câu trắc nghiệm khách quan 4 lựa chọn và {so_cau_tl} câu tự luận).
                - Yêu cầu cấu trúc/mức độ: {yeu_cau_ma_tran}

                CẤU TRÚC BẮT BUỘC TRẢ VỀ (Phân chia rõ ràng):
                **PHẦN 1: MA TRẬN ĐỀ KIỂM TRA** (Kẻ bảng markdown rõ ràng phân bố các mức độ: Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao).
                **PHẦN 2: NỘI DUNG ĐỀ KIỂM TRA** (Trình bày khoa học. Trắc nghiệm có 4 đáp án A, B, C, D xuống dòng rõ ràng).
                **PHẦN 3: ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM** (Bảng đáp án trắc nghiệm. Hướng dẫn chấm chi tiết từng bước, có thang điểm cụ thể cho từng ý của câu tự luận).

                LƯU Ý KỸ THUẬT:
                - Sử dụng Markdown để trình bày.
                - Mọi công thức Toán/Lý/Hóa/Sinh BẮT BUỘC dùng cú pháp LaTeX ($...$ cho inline hoặc $$...$$ cho block).
                - Tuyệt đối KHÔNG dùng ký tự ">" ở đầu các dòng.
                
                TÀI LIỆU THAM CHIẾU (Dùng làm ngữ cảnh ra đề):
                {file_context[:8000]}
                """
                
                try:
                    content = ai_engine.generate_text(prompt)
                    st.session_state['de_kt_content'] = content
                    st.session_state['de_kt_meta'] = {
                        "title": chu_de.replace(" ", "_"), 
                        "mon": mon_hoc, 
                        "lop": lop, 
                        "thoi_gian": thoi_gian
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi hệ thống AI: {e}")

    if c2.button("🗑️ XÓA DỮ LIỆU ĐỀ"):
        st.session_state.pop('de_kt_content', None)
        st.session_state.pop('de_kt_meta', None)
        st.rerun()

    # 3. Hiển thị kết quả và Nút Tải Word
    if st.session_state.get('de_kt_content'):
        st.markdown("---")
        st.markdown(st.session_state['de_kt_content'])
        
        try:
            # Lazy Import để xuất Word
            root_path = str(Path(__file__).resolve().parents[2])
            if root_path not in sys.path:
                sys.path.insert(0, root_path)
            from export.export_word import WordExportEngine

            data_export = st.session_state['de_kt_meta'].copy()
            data_export["ai_generated_content"] = st.session_state['de_kt_content']
            data_export["is_de_kt"] = True 
            
            word_bytes = WordExportEngine.export_to_word(data_export)
            
            st.download_button(
                label="📥 TẢI FILE ĐỀ KIỂM TRA (WORD)", 
                data=word_bytes, 
                file_name=f"De_KT_{st.session_state['de_kt_meta']['title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
        except Exception as e:
            st.error(f"❌ Có lỗi trong quá trình đóng gói file Word: {e}")
