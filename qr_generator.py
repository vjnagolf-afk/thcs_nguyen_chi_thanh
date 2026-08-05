# -*- coding: utf-8 -*-
import streamlit as st
import io

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

st.set_page_config(page_title="Tạo Mã QR Sạch", page_icon="🎯", layout="centered")

st.markdown("## 🎯 Trợ lý Tạo Mã QR Sạch Cho Giáo Viên")
st.write("Công cụ tạo mã QR nhanh chóng, không chứa quảng cáo hay yêu cầu đăng nhập.")

# Ô nhập đường link cần tạo QR
target_link = st.text_input("Dán đường link cần chuyển thành mã QR:", placeholder="VD: https://thcsnguyenchithanh-lhd.streamlit.app/...")

if target_link:
    if HAS_QRCODE:
        # Tạo mã QR
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(target_link)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        # Chuyển đổi sang định dạng hiển thị và tải về
        buf = io.BytesIO()
        img_qr.save(buf, format="PNG")
        
        st.markdown("### 📱 Mã QR của bạn:")
        st.image(buf.getvalue(), caption="Quét mã để truy cập trực tiếp", width=300)
        
        # Nút tải ảnh QR về máy
        st.download_button(
            label="📥 Tải ảnh mã QR (.PNG)",
            data=buf.getvalue(),
            file_name="ma_qr_giao_vien.png",
            mime="image/png",
            type="primary"
        )
    else:
        st.error("⚠️ Máy chủ chưa cài đặt thư viện tạo QR. Vui lòng chạy lệnh: `pip install qrcode[pil]`")
