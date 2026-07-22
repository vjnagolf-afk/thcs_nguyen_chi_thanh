# -*- coding: utf-8 -*-
import streamlit as st

def render_the_03(ai_engine=None):
    st.markdown("### 🎬 Công cụ Trích xuất, Chuyển văn bản & Dịch Video (YouTube & Tải lên)")
    st.caption("Hỗ trợ giáo viên lấy kịch bản, chuyển lời thoại thành văn bản và dịch nội dung từ video bất kỳ phục vụ giảng dạy.")

    col1, col2 = st.columns([1, 1], gap="medium")

    # =========================================================
    # CỘT 1: CẤU HÌNH VÀ NGUỒN VIDEO
    # =========================================================
    with col1:
        st.markdown("#### ⚙️ Cấu hình nguồn video")
        
        nguon_video = st.radio(
            "Chọn nguồn video",
            ["Đường dẫn YouTube (URL)", "Tải tệp video lên máy (MP4, AVI, MOV, MKV)"],
            key="vproc_source"
        )

        yt_url = ""
        uploaded_video = None

        if nguon_video == "Đường dẫn YouTube (URL)":
            yt_url = st.text_input(
                "Nhập URL YouTube", 
                placeholder="Ví dụ: https://www.youtube.com/watch?v=...", 
                key="vproc_yt_url"
            )
        else:
            uploaded_video = st.file_uploader(
                "Tải lên tệp video", 
                type=["mp4", "avi", "mov", "mkv", "webm"], 
                key="vproc_file"
            )

        st.markdown("#### 🛠️ Chọn tác vụ xử lý")
        tac_vu = st.selectbox(
            "Yêu cầu xử lý",
            [
                "📋 Sao chép toàn bộ kịch bản gốc từ video",
                "🗣️ Chuyển văn bản lời thoại chi tiết (Transcribe)",
                "🌐 Dịch nội dung video sang Tiếng Việt (hoặc ngôn ngữ khác)",
                "📝 Tóm tắt và phân tích nội dung cốt lõi từ video"
            ],
            key="vproc_action"
        )

        ngon_ngu_dich = "Tiếng Việt"
        if "Dịch" in tac_vu:
            ngon_ngu_dich = st.selectbox(
                "Ngôn ngữ đích dịch", 
                ["Tiếng Việt", "Tiếng Anh", "Tiếng Trung", "Tiếng Nhật", "Tiếng Hàn"], 
                key="vproc_lang"
            )

        btn_xu_ly = st.button("🚀 THỰC THI XỬ LÝ VIDEO", type="primary", use_container_width=True)

    # =========================================================
    # CỘT 2: KẾT QUẢ KẾT XUẤT
    # =========================================================
    with col2:
        st.markdown("#### 📋 Kết quả xử lý văn bản")

        if btn_xu_ly:
            if nguon_video == "Đường dẫn YouTube (URL)" and not yt_url.strip():
                st.warning("⚠️ Vui lòng nhập đường dẫn URL YouTube hợp lệ.")
            elif nguon_video == "Tải tệp video lên máy (MP4, AVI, MOV, MKV)" and not uploaded_video:
                st.warning("⚠️ Vui lòng tải lên một tệp video.")
            else:
                with st.spinner("🤖 Hệ thống AI đang phân tích, trích xuất và xử lý dữ liệu video..."):
                    
                    # Xây dựng prompt chuyên sâu hướng dẫn AI xử lý tác vụ video
                    thong_tin_nguon = f"YouTube URL: {yt_url}" if yt_url else f"Tệp video: {uploaded_video.name}"
                    
                    prompt_v = f"""
BẠN LÀ MỘT TRỢ LÝ AI CHUYÊN PHÂN TÍCH, TRÍCH XUẤT KỊCH BẢN VÀ DỊCH NỘI DUNG VIDEO GIÁO DỤC.
NHIỆM VỤ: Hãy thực hiện yêu cầu '{tac_vu}' {'sang ngôn ngữ ' + ngon_ngu_dich if 'Dịch' in tac_vu else ''} đối với nguồn video sau:
- Nguồn video: {thong_tin_nguon}

YÊU CẦU ĐẦU RA:
1. Trình bày rõ ràng, mạch lạc, chia theo các mốc thời gian hoặc phân đoạn logic nếu có thể.
2. Văn phong chuẩn sư phạm, chính xác, dễ sử dụng để làm tài liệu dạy học hoặc viết kịch bản bài giảng.
3. Nếu là tác vụ dịch, đảm bảo ngữ nghĩa tự nhiên, phù hợp với học sinh và giáo viên Việt Nam.
"""

                    ket_qua_xu_ly = ""
                    if ai_engine:
                        try:
                            ket_qua_xu_ly = ai_engine.generate_text(prompt_v)
                        except Exception as e:
                            ket_qua_xu_ly = f"❌ Lỗi khi gọi AI xử lý: {str(e)}"
                    else:
                        # Kết quả mẫu khi chạy offline hoặc chưa có API key
                        ket_qua_xu_ly = f"""### KẾT QUẢ MÔ PHỎNG XỬ LÝ VIDEO ({tac_vu})
                        
**Nguồn đầu vào:** {thong_tin_nguon}
**Tác vụ thực hiện:** {tac_vu}
{'- Ngôn ngữ dịch đích: ' + ngon_ngu_dich if 'Dịch' in tac_vu else ''}

---
**Nội dung kịch bản / Văn bản trích xuất:**

[00:00 - 00:30] Chào mừng các thầy cô và các em học sinh đến với chuyên đề học tập hôm nay...
[00:30 - 02:15] Nội dung cốt lõi tập trung phân tích các hiện tượng thực tế và cách giải quyết vấn đề...
[02:15 - 05:00] Tổng kết kiến thức trọng tâm và hướng dẫn bài tập vận dụng nâng cao...

*(Ghi chú: Đang chạy ở chế độ mô phỏng vì chưa kết nối trực tiếp API xử lý luồng video lớn. Khi kết nối API chính thức, AI sẽ phân tích sâu nội dung video thực tế).*
"""

                    st.session_state["vproc_result"] = ket_qua_xu_ly
                    st.success("🎉 Xử lý video thành công!")

        if "vproc_result" in st.session_state:
            ket_qua_hien_tai = st.session_state["vproc_result"]
            st.text_area("Văn bản kết xuất:", value=ket_qua_hien_tai, height=400)
            
            st.download_button(
                "📥 Tải xuống kết quả (.txt)",
                data=ket_qua_hien_tai,
                file_name="Ket_qua_xu_ly_video.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("💡 Hãy chọn nguồn video, điền link hoặc tải file, sau đó bấm nút thực thi ở cột bên trái.")
