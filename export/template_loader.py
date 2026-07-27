# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/template_loader.py
Nhiệm vụ: Tải Template KHBD chuẩn của trường làm nền tảng.
Chỉ tạo Document trống nếu template vật lý bị mất.
============================================================
"""

import os
import logging
from docx import Document
from .word_styles import apply_standard_margins, setup_document_styles

logger = logging.getLogger(__name__)

TEMPLATE_PATH = "templates/khbd_mau.docx"

def get_word_document() -> Document:
    """
    Tải file template Word gốc để giữ nguyên Header/Footer và Cấu trúc.
    Đồng thời áp dụng các chuẩn hóa lề, font, justify.
    """
    doc = None
    
    # 1. Tải Template nếu tồn tại
    if os.path.exists(TEMPLATE_PATH):
        try:
            doc = Document(TEMPLATE_PATH)
            logger.info(f"Đã tải thành công template: {TEMPLATE_PATH}")
        except Exception as e:
            logger.error(f"Lỗi khi đọc file template {TEMPLATE_PATH}: {e}. Đang dùng Document trống.")
    
    # 2. Khởi tạo Document trống nếu không có template
    if doc is None:
        logger.warning("Khởi tạo Document Word trống (Không tìm thấy Template).")
        doc = Document()
    
    # 3. Chuẩn hóa Lề và Font (Quét qua các section để ép lề 2.0 - 1.5 cm)
    for section in doc.sections:
        apply_standard_margins(section)
        
    setup_document_styles(doc)
    
    return doc
