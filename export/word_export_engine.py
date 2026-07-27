# -*- coding: utf-8 -*-
"""
============================================================
MODULE: export/word_export_engine.py
Nhiệm vụ: Cung cấp Class Wrapper giao tiếp để giữ tính 
tương thích ngược. Điều phối trực tiếp đến export_word.py.
============================================================
"""

from .export_word import WordExportEngine as CoreWordExportEngine

class WordExportEngine(CoreWordExportEngine):
    """
    Lớp kế thừa lớp CoreWordExportEngine từ export_word.py.
    Dành cho các file cũ gọi trực tiếp module này.
    """
    pass
