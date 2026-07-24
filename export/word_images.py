# -*- coding: utf-8 -*-
import io
import base64
import requests
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def insert_image_to_docx(doc, img_path_or_url: str, width_cm: float = 14.5):
    """Hàm tải và nhúng hình ảnh vào văn bản, tự động căn giữa và bo hẹp tỷ lệ chống vỡ khung lề."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run()
    
    try:
        # Trường hợp đường dẫn ảnh dạng URL internet công khai
        if img_path_or_url.startswith("http"):
            response = requests.get(img_path_or_url, timeout=12)
            image_stream = io.BytesIO(response.content)
            run.add_picture(image_stream, width=Cm(width_cm))
            
        # Trường hợp chuỗi nhị phân ảnh mã hóa Base64 (từ biểu đồ matplotlib/plotly trên giao diện)
        elif img_path_or_url.startswith("data:image"):
            base64_data = img_path_or_url.split(",")[1]
            image_stream = io.BytesIO(base64.b64decode(base64_data))
            run.add_picture(image_stream, width=Cm(width_cm))
            
        # Trường hợp tệp tin nội bộ lưu trữ cục bộ trên máy chủ
        else:
            run.add_picture(img_path_or_url, width=Cm(width_cm))
            
        # Tự động chèn một dòng chú thích chữ nghiêng ngay dưới ảnh
        caption_p = doc.add_paragraph()
        caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_run = caption_p.add_run("Hình vẽ minh họa nội dung bài học")
        caption_run.font.italic = True
        caption_run.font.size = Pt(10)
        caption_p.paragraph_format.space_after = Pt(12)
        
    except Exception as e:
        run.text = f"\n[⚠️ Không thể hiển thị hoặc tải tệp hình ảnh: {str(e)}]\n"
        run.font.color.rgb = requests.structures.CaseInsensitiveDict({'red': (255, 0, 0)}) # Đánh dấu chữ lỗi màu đỏ
