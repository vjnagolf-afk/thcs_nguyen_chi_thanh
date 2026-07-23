# -*- coding: utf-8 -*-
import streamlit as st

def render_xd_chuyen_doi(ai_engine=None):
    st.markdown("### 🔄 Trợ lý Xử lý, Làm sạch & Chuyển đổi Dữ liệu")
    st.caption("Sử dụng AI để định dạng lại các văn bản lộn xộn, chuyển văn bản thành bảng biểu, hoặc viết lại câu chữ chuyên nghiệp hơn.")
    
    with st.container(border=True):
        loai_chuyen_doi = st.radio(
            "Chọn thao tác mong muốn:",
            [
                "Chuyển đoạn văn thô thành Bảng dữ liệu (Markdown/Excel)", 
                "Làm sạch văn bản (Xóa khoảng trắng thừa, sửa lỗi gõ phím)", 
                "Chuyển đổi văn phong (Từ nôm na sang Hành chính/Sư phạm)"
            ],
            horizontal=True
        )
        
        van_ban_goc = st.text_area("Dán văn bản gốc cần xử lý vào đây:", height=200, placeholder="Ví dụ dán một đoạn copy bị lỗi font hoặc lủng củng...")
        
        btn_chuyen_doi = st.button("⚙️ Thực thi Chuyển đổi bằng AI", type="primary", use_container_width=True)

    if btn_chuyen_doi:
        if not van_ban_goc.strip():
            st.warning("⚠️ Vui lòng cung cấp văn bản gốc.")
        else:
            with st.spinner("AI đang xử lý và định dạng lại dữ liệu..."):
                prompt = f"""
                Nhiệm vụ của bạn là: {loai_chuyen_doi}.
                Hãy xử lý đoạn văn bản thô dưới đây đúng theo yêu cầu.
                
                VĂN BẢN GỐC:
                {van_ban_goc}
                
                LƯU Ý: 
                - Nếu yêu cầu là tạo bảng, hãy sử dụng Markdown Table hợp lệ.
                - Trả về trực tiếp kết quả, không cần giải thích dông dài.
                """
                if ai_engine:
                    try:
                        result = ai_engine.generate_text(prompt)
                        st.markdown("---")
                        st.success("✅ Dữ liệu đã được xử lý xong!")
                        st.markdown(result)
                        
                        st.download_button(
                            "⬇️ Tải kết quả (.txt)",
                            data=result,
                            file_name="DuLieu_DaXuLy.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Lỗi AI: {e}")
                else:
                    st.error("❌ Chưa kết nối AI Engine.")
