# -*- coding: utf-8 -*-
"""
============================================================
AI ENGINE TRUNG TÂM: QUẢN LÝ KẾT NỐI GEMINI API
FILE: utils/ai_engine.py
============================================================
"""

import os
import streamlit as st

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class AIEngine:
    """
    Lớp điều phối AI Engine trung tâm của toàn bộ hệ thống.
    Hỗ trợ lấy API Key từ Session State (người dùng nhập), Secrets hoặc biến môi trường.
    """

    def __init__(self, default_model: str = "gemini-2.5-flash"):
        self.default_model = default_model
        self._configure_client()

    def _get_active_api_key(self) -> str:
        """Kiểm tra và lấy API Key theo thứ tự ưu tiên: Session State -> Streamlit Secrets -> Environment."""
        # 1. Ưu tiên key do người dùng nhập trực tiếp trên giao diện
        user_key = st.session_state.get("user_api_key")
        if user_key and str(user_key).strip():
            return str(user_key).strip()

        # 2. Lấy từ Streamlit Secrets nếu có cấu hình
        try:
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                secret_key = st.secrets["GEMINI_API_KEY"]
                if secret_key and str(secret_key).strip():
                    return str(secret_key).strip()
        except Exception:
            pass

        # 3. Lấy từ biến môi trường hệ thống
        env_key = os.environ.get("GEMINI_API_KEY")
        if env_key and str(env_key).strip():
            return str(env_key).strip()

        return ""

    def _configure_client(self):
        """Cấu hình thư viện google.generativeai với API Key hợp lệ."""
        if genai is None:
            return
        
        api_key = self._get_active_api_key()
        if api_key:
            try:
                genai.configure(api_key=api_key)
            except Exception:
                pass

    def generate_text(self, prompt: str, model_name: str = None, temperature: float = 0.7, max_tokens: int = None, use_cache: bool = False) -> str:
        """
        Phương thức chuẩn hóa để gọi sinh văn bản từ AI.
        Tương thích với tất cả các module trong toàn hệ thống.
        """
        if genai is None:
            return "❌ Thư viện 'google-generativeai' chưa được cài đặt trên máy chủ."

        api_key = self._get_active_api_key()
        if not api_key:
            return "❌ Chưa tìm thấy Gemini API Key. Vui lòng nhập API Key ở thanh bên (Sidebar) hoặc cấu hình trong Secrets."

        # Cấu hình lại mỗi lần gọi để đảm bảo nhận diện key mới nhất từ user
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            return f"❌ Lỗi cấu hình API Key: {str(e)}"

        # Ánh xạ tên model linh hoạt
        target_model = model_name or self.default_model
        model_mapping = {
            "3.1 Flash-Lite": "gemini-2.5-flash-lite",
            "3.5 Flash": "gemini-2.5-flash",
            "3.1 Pro": "gemini-2.5-pro",
            "Tư duy mở rộng": "gemini-2.5-pro",
            "google/gemini-2.5-flash": "gemini-2.5-flash"
        }
        resolved_model_name = model_mapping.get(target_model, target_model)

        try:
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            model = genai.GenerativeModel(model_name=resolved_model_name)
            response = model.generate_content(prompt, generation_config=generation_config)
            
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            
            return "⚠️ AI không trả về nội dung văn bản hợp lệ."

        except Exception as e:
            return f"❌ Lỗi khi gọi AI Engine: {str(e)}"

    def generate(self, prompt: str) -> str:
        """Bổ sung phương thức tương thích ngược với một số module gọi hàm .generate()"""
        return self.generate_text(prompt)
