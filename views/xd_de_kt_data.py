# -*- coding: utf-8 -*-
"""
============================================================
DATA & LOGIC: XÂY DỰNG ĐỀ KIỂM TRA & MA TRẬN ĐỀ
FILE: views/xd_de_kt_data.py
============================================================
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)

def init_session_state_de_kt():
    defaults = {
        "de_kt_result": None,
        "de_kt_processing": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def generate_de_kt_ai(ai_engine, prompt, model_name="3.5 Flash"):
    """
    Tương thích với AIEngine truyền từ app.py giống như các module khác.
    """
    if ai_engine is None:
        raise RuntimeError("Chưa truyền AI Engine.")
    
    # Hỗ trợ cả 2 chuẩn gọi hàm của AIEngine tùy chỉnh hoặc Client gốc
    if hasattr(ai_engine, "generate_text"):
        return str(ai_engine.generate_text(prompt)).strip()
    if hasattr(ai_engine, "generate"):
        return str(ai_engine.generate(prompt)).strip()
    
    # Nếu truyền thẳng google-genai client gốc
    try:
        response = ai_engine.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return getattr(response, "text", "").strip()
    except Exception as e:
        logger.error("Lỗi gọi AI đề kiểm tra: %s", e)
        raise RuntimeError(f"Máy chủ AI phản hồi lỗi: {e}")

def build_prompt_de_kt(thong_tin, ma_trận, noi_dung):
    return f"""
BẠN LÀ CHUYÊN GIA KHẢO THÍ VÀ ĐO LƯỜNG GIÁO DỤC CHUẨN GDPT 2018.
Nhiệm vụ: Xây dựng Ma trận, Bản đặc tả và Đề kiểm tra (kèm Đáp án & Hướng dẫn chấm) chi tiết.

THÔNG TIN ĐỀ KIỂM TRA:
{thong_tin}

YÊU CẦU MA TRẬN VÀ CẤU TRÚC:
{ma_trận}

NGUỒN KIẾN THỨC CỐT LÕI:
{noi_dung}

YÊU CẦU ĐẦU RA:
Trình bày rõ ràng bằng định dạng Markdown, bao gồm:
1. Ma trận đề kiểm tra (Tỉ lệ % Nhận biết, Thông hiểu, Vận dụng).
2. Bản đặc tả kỹ thuật đề kiểm tra.
3. Đề kiểm tra chính thức (Trắc nghiệm + Tự luận).
4. Hướng dẫn chấm và Biểu điểm chi tiết.
"""
