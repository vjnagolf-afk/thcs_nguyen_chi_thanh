# -*- coding: utf-8 -*-
"""
============================================================
AI ENGINE 2: TRỢ LÝ AI CHUYÊN SÂU PHỤ TRỢ
FILE: utils/ai_engine_2.py
============================================================
"""

import os
import streamlit as st

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class AIEngine2:
    """
    Lớp AI Engine phụ trợ, chuyên phục vụ các tác vụ chuyên sâu như 
    thẩm định KHBD (chuẩn công văn 5512), phân tích sáng kiến, v.v.
    Đảm bảo tính độc lập hoặc chia sẻ chung cấu hình với AIEngine chính.
    """

    def __init__(self, default_model: str = "gemini-2.5-flash"):
        self.default_model = default_model
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
        """Cấu hình google.generativeai."""
        if genai is None:
            return
        
        api_key = self._get_active_api_key()
        if api_key:
            try:
                genai.configure(api_key=api_key)
            except Exception:
                pass

    def generate_text(self, prompt: str, model_name: str = None, temperature: float = 0.7, max_tokens: int = None) -> str:
        """
        Sinh văn bản chuyên sâu phục vụ các module thẩm định, quét lỗi giáo án.
        """
        if genai is None:
            return "❌ Thư viện 'google-generativeai' chưa được cài đặt."

        api_key = self._get_active_api_key()
        if not api_key:
            return "❌ Chưa tìm thấy Gemini API Key. Vui lòng nhập API Key ở thanh bên (Sidebar)."

        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            return f"❌ Lỗi cấu hình API Key: {str(e)}"

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
            
            return "⚠️ AI Engine 2 không trả về nội dung hợp lệ."

        except Exception as e:
            return f"❌ Lỗi khi gọi AI Engine 2: {str(e)}"

    def generate(self, prompt: str) -> str:
        """Hỗ trợ tương thích ngược với phương thức .generate()"""
        return self.generate_text(prompt)
