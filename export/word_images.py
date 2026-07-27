# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_images.py
Nhiệm vụ: Module chuyên trách xử lý, chuẩn hóa và chèn hình ảnh 
vào tài liệu Word. Hỗ trợ đa nguồn: URL mạng, Base64 từ PDF, File local.
Tự động tính toán tỷ lệ khung hình và chèn Caption.
============================================================
"""

import os
import re
import json
import base64
import requests
import logging
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

logger = logging.getLogger(__name__)

# Bộ nhớ đệm tĩnh lưu trữ các ảnh mạng đã tải
_IMAGE_CACHE = {}

def _normalize_image_source(source):
    """
    Chuẩn hóa đa dạng nguồn ảnh thành luồng BytesIO và trích xuất Metadata.
    """
    metadata = {}
    stream = None
    original_source_text = str(source)[:100]

    if isinstance(source, str) and source.strip().startswith('{'):
        try: source = json.loads(source)
        except Exception: pass

    if isinstance(source, dict):
        metadata = source
        actual_source = source.get('base64') or source.get('url') or source.get('path') or source.get('data')
        if not actual_source: raise ValueError("Dictionary thiếu trường dữ liệu ảnh (base64/url/path).")
        source = actual_source

    if isinstance(source, bytes): stream = BytesIO(source)
    elif isinstance(source, BytesIO): stream = source
    elif isinstance(source, str):
        source = source.strip()
        
        # Base64 từ PDF/Docx
        if source.startswith('data:image'):
            try:
                b64_data = re.sub(r'^data:image/.+;base64,', '', source)
                b64_data += "=" * ((4 - len(b64_data) % 4) % 4)
                stream = BytesIO(base64.b64decode(b64_data))
            except Exception as e: raise ValueError(f"Lỗi giải mã Data URI: {e}")
        elif len(source) > 100 and not source.startswith('http') and not os.path.exists(source):
            try:
                b64_data = source + "=" * ((4 - len(source) % 4) % 4)
                stream = BytesIO(base64.b64decode(b64_data))
            except Exception: pass
            
        # Tải từ Internet
        if stream is None and re.match(r'^https?://', source):
            if source in _IMAGE_CACHE: stream = BytesIO(_IMAGE_CACHE[source])
            else:
                try:
                    resp = requests.get(source, timeout=10)
                    if resp.status_code == 200:
                        _IMAGE_CACHE[source] = resp.content
                        stream = BytesIO(resp.content)
                except Exception as e: raise ValueError(f"Lỗi tải URL mạng: {e}")
                    
        # File cục bộ
        if stream is None and os.path.exists(source):
            try:
                with open(source, 'rb') as f: stream = BytesIO(f.read())
            except Exception as e: raise ValueError(f"Lỗi đọc file nội bộ: {e}")

    if stream is None:
        raise ValueError(f"Nguồn ảnh không hợp lệ hoặc không tải được: {original_source_text}")
    return stream, metadata


def insert_image_to_paragraph(paragraph, image_source, width=None, height=None, max_width=Inches(6.0)):
    """Chèn hình ảnh vào một Paragraph, tự động co giãn chống vỡ lề trang."""
    try:
        stream, metadata = _normalize_image_source(image_source)
        run = paragraph.add_run()
        
        kwargs = {}
        if width: kwargs['width'] = width
        if height: kwargs['height'] = height

        if not width and not height:
            try:
                from PIL import Image
                img = Image.open(stream)
                w_px, h_px = img.size
                stream.seek(0)
                limit_w = max_width.inches if max_width else 6.0
                if (w_px / 96.0) > limit_w: kwargs['width'] = Inches(limit_w)
            except Exception:
                kwargs['width'] = max_width or Inches(6.0)

        picture = run.add_picture(stream, **kwargs)
        
        # Chèn Caption nếu có
        caption = metadata.get('caption') or metadata.get('alt_text')
        if caption and str(caption).strip() != "None" and str(caption).strip() != "":
            # Lọc bỏ các chữ như IMG_P1_1 nếu caption chỉ là ID thô
            if not re.match(r'^IMG_P\d+_\d+$', str(caption).strip()):
                run.add_break()
                cap_run = paragraph.add_run(f"Hình: {caption}")
                cap_run.italic = True
                cap_run.font.size = Pt(11)
                cap_run.font.name = 'Times New Roman'

        return picture
    except Exception as e:
        logger.error(f"Lỗi chèn ảnh: {e}")
        err_run = paragraph.add_run(f"\n[Không thể chèn hình ảnh: {str(e)}]\n")
        err_run.italic, err_run.font.color.rgb = True, RGBColor(255, 0, 0)
        return None


def insert_image_to_docx(doc: Document, image_path_or_url: str):
    if not image_path_or_url: return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    insert_image_to_paragraph(p, image_path_or_url)
