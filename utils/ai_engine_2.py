# -*- coding: utf-8 -*-
"""
============================================================
AI ENGINE 2: TRỢ LÝ AI CHUYÊN SÂU PHỤ TRỢ
FILE: utils/ai_engine_2.py
ĐÃ NÂNG CẤP LÊN BỘ SDK GOOGLE.GENAI MỚI NHẤT CHỐNG DEPRECATED.
============================================================
"""

import os
import logging
import streamlit as st

# Sử dụng SDK mới nhất theo chuẩn 2026 của Google
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class AIEngine2:
    """
    Lớp AI Engine phụ trợ, chuyên phục vụ các tác vụ chuyên sâu như 
    thẩm định KHBD, lập Ma trận Đề kiểm tra, Chấm bài tự luận/ảnh, v.v.
    Đã được tái cấu trúc để tương thích 100% với SDK google.genai.
    """

    def __init__(self, default_model: str = "gemini-2.5-flash"):
        self.default_model = default_model
        self.client = None
        self._configure_client()

    def _get_active_api_key(self) -> str:
        """Lấy API Key từ Session State, Streamlit Secrets hoặc Biến môi trường."""
        user_key = st.session_state.get("user_api_key")
        if user_key and str(user_key).strip():
            return str(user_key).strip()

        try:
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                secret_key = st.secrets["GEMINI_API_KEY"]
                if secret_key and str(secret_key).strip():
                    return str(secret_key).strip()
        except Exception:
            pass

        env_key = os.environ.get("GEMINI_API_KEY")
        if env_key and str(env_key).strip():
            return str(env_key).strip()

        return ""

    def _configure_client(self):
        """Khởi tạo Client của Google GenAI."""
        if genai is None:
            return
        
        api_key = self._get_active_api_key()
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.error(f"Lỗi khởi tạo GenAI Client: {e}")

    def generate_text(self, prompt: str, model_name: str = None, temperature: float = 0.7, max_tokens: int = None) -> str:
        """
        Sinh văn bản chuyên sâu phục vụ các module văn bản thông thường.
        """
        if genai is None:
            return "❌ Thư viện 'google-genai' chưa được cài đặt."

        api_key = self._get_active_api_key()
        if not api_key:
            return "❌ Chưa tìm thấy Gemini API Key. Vui lòng nhập API Key ở thanh bên (Sidebar)."

        # Tái khởi tạo client để luôn cập nhật Key mới nhất từ giao diện
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            return f"❌ Lỗi cấu hình API Key: {str(e)}"

        target_model = model_name or self.default_model
        model_mapping = {
            "3.1 Flash-Lite": "gemini-2.5-flash", # Ánh xạ về các model an toàn của 2.5
            "3.5 Flash": "gemini-2.5-flash",
            "3.1 Pro": "gemini-2.5-pro",
            "Tư duy mở rộng": "gemini-2.5-pro",
            "google/gemini-2.5-flash": "gemini-2.5-flash"
        }
        resolved_model_name = model_mapping.get(target_model, target_model)

        try:
            # Thiết lập thông số theo chuẩn SDK mới
            config_kwargs = {"temperature": temperature}
            if max_tokens:
                config_kwargs["max_output_tokens"] = max_tokens

            config = types.GenerateContentConfig(**config_kwargs)

            # Gọi API
            response = self.client.models.generate_content(
                model=resolved_model_name,
                contents=prompt,
                config=config
            )
            
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            
            return "⚠️ AI Engine 2 không trả về nội dung hợp lệ."

        except Exception as e:
            return f"❌ Lỗi khi gọi AI Engine 2: {str(e)}"

    def generate_multimodal(self, contents: list, model_name: str = "gemini-2.5-pro", temperature: float = 0.5) -> str:
        """
        Hàm đặc biệt: Hỗ trợ truyền vào danh sách (List) gồm Text và Hình ảnh (PIL.Image).
        Chuyên dùng cho module Chấm bài viết (Đọc chữ viết tay).
        Khuyên dùng gemini-2.5-pro cho độ chính xác thị giác (Vision) cao nhất.
        """
        if genai is None:
            return "❌ Thư viện 'google-genai' chưa được cài đặt."

        api_key = self._get_active_api_key()
        if not api_key:
            return "❌ Chưa tìm thấy Gemini API Key."

        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            return f"❌ Lỗi cấu hình API Key: {str(e)}"

        # Các tác vụ đọc ảnh cần Model Pro để tránh sai sót
        target_model = model_name if model_name else "gemini-2.5-pro"
        
        try:
            config = types.GenerateContentConfig(temperature=temperature)
            
            # Gửi toàn bộ mảng dữ liệu Đa phương thức (Văn bản + Các ảnh đính kèm)
            response = self.client.models.generate_content(
                model=target_model,
                contents=contents,
                config=config
            )
            
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            return "⚠️ AI Engine 2 (Multimodal) không trả về kết quả."

        except Exception as e:
            return f"❌ Lỗi khi gọi AI Engine 2 xử lý Đa phương thức: {str(e)}"

    def generate(self, prompt: str) -> str:
        """Hỗ trợ tương thích ngược với phương thức .generate() cũ"""
        return self.generate_text(prompt)
