# -*- coding: utf-8 -*- 
"""
============================================================
AI ENGINE TRUNG TÂM: QUẢN LÝ KẾ T NỐI HYBRID (GEMINI & OPENAI)
FILE: utils/ai_engine.py
============================================================
"""
import os
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# Thử nghiệm import cả 2 thư viện AI hàng đầu
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class AIEngine:
    """
    Lớp điều phối AI Engine trung tâm nâng cấp.
    Tự động nhận diện khóa OpenAI (sk-proj-...) hoặc Gemini API Key từ người dùng.
    """
    def __init__(self, default_model: str = "gemini-2.5-flash"):
        self.default_model = default_model
        self._configure_client()

    def _get_active_api_key(self) -> str:
        """Kiểm tra và lấy API Key theo thứ tự ưu tiên: Session State -> Streamlit Secrets -> Environment."""
        # 1. Ưu tiên key do người dùng nhập trực tiếp trên giao diện (kiểm tra cả 2 biến phổ biến)
        user_key = st.session_state.get("user_api_key") or st.session_state.get("openai_api_key")
        if user_key and str(user_key).strip():
            return str(user_key).strip()

        # 2. Lấy từ Streamlit Secrets nếu có cấu hình
        try:
            if hasattr(st, "secrets"):
                if "GEMINI_API_KEY" in st.secrets:
                    return str(st.secrets["GEMINI_API_KEY"]).strip()
                if "OPENAI_API_KEY" in st.secrets:
                    return str(st.secrets["OPENAI_API_KEY"]).strip()
        except Exception:
            pass

        # 3. Lấy từ biến môi trường hệ thống
        env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if env_key and str(env_key).strip():
            return str(env_key).strip()

        return ""

    def _is_openai_key(self, api_key: str) -> bool:
        """Hàm bổ trợ kiểm tra xem khóa nhập vào có phải của OpenAI hay không"""
        return api_key.startswith("sk-")

    def _configure_client(self):
        """Cấu hình thư viện AI tương ứng với API Key hợp lệ."""
        api_key = self._get_active_api_key()
        if not api_key:
            return
            
        if self._is_openai_key(api_key):
            if OpenAI is None:
                logger.error("Thư viện 'openai' chưa được cài đặt.")
        else:
            if genai is not None:
                try:
                    genai.configure(api_key=api_key)
                except Exception:
                    pass
    def generate_text(self, prompt: str, model_name: str = None, temperature: float = 0.7, max_tokens: int = None, use_cache: bool = False) -> str:
        """
        Phương thức chuẩn hóa để gọi sinh văn bản từ AI.
        Tự động điều phối luồng xử lý tùy theo loại API Key được nạp vào hệ thống.
        """
        api_key = self._get_active_api_key()
        if not api_key:
            return "❌ Chưa tìm thấy API Key. Vui lòng nhập OpenAI Key (sk-...) hoặc Gemini Key ở thanh bên (Sidebar)."

        target_model = model_name or self.default_model

        # PHÂN NHÁNH 1: XỬ LÝ NẾU LÀ KHÓA OPENAI (sk-proj-...)
        if self._is_openai_key(api_key):
            if OpenAI is None:
                return "❌ Thư viện 'openai' chưa được cài đặt trên máy chủ để chạy khóa sk-proj-."
            try:
                # Tự động ánh xạ model tương ứng từ yêu cầu của giao diện sang OpenAI
                # Nếu giáo viên chọn bản "Pro" hoặc "Tư duy" -> Dùng gpt-4o, ngược lại dùng gpt-4o-mini tốc độ cao
                openai_model = "gpt-4o" if any(x in str(target_model) for x in ["Pro", "Tư duy", "pro"]) else "gpt-4o-mini"
                
                client = OpenAI(api_key=api_key)
                
                kwargs = {
                    "model": openai_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature
                }
                if max_tokens:
                    kwargs["max_tokens"] = max_tokens
                    
                response = client.chat.completions.create(**kwargs)
                if response.choices[0].message.content:
                    return response.choices[0].message.content.strip()
                return "⚠️ OpenAI không trả về nội dung văn bản hợp lệ."
            except Exception as e:
                return f"❌ Lỗi khi gọi Lõi OpenAI Engine: {str(e)}"

        # PHÂN NHÁNH 2: XỬ LÝ NẾU LÀ KHÓA GEMINI (Giữ nguyên logic gốc của thầy)
        else:
            if genai is None:
                return "❌ Thư viện 'google-generativeai' chưa được cài đặt trên máy chủ."
            try:
                genai.configure(api_key=api_key)
            except Exception as e:
                return f"❌ Lỗi cấu hình Gemini API Key: {str(e)}"

            model_mapping = {
                "3.1 Flash-Lite": "gemini-2.5-flash-lite",
                "3.5 Flash": "gemini-2.5-flash",
                "3.1 Pro": "gemini-2.5-pro",
                "Tư duy mở rộng": "gemini-2.5-pro",
                "google/gemini-2.5-flash": "gemini-2.5-flash"
            }
            resolved_model_name = model_mapping.get(target_model, target_model)
            
            try:
                generation_config = {"temperature": temperature}
                if max_tokens:
                    generation_config["max_output_tokens"] = max_tokens
                    
                model = genai.GenerativeModel(model_name=resolved_model_name)
                response = model.generate_content(prompt, generation_config=generation_config)
                
                if hasattr(response, "text") and response.text:
                    return response.text.strip()
                return "⚠️ AI Gemini không trả về nội dung văn bản hợp lệ."
            except Exception as e:
                return f"❌ Lỗi khi gọi Lõi Gemini Engine: {str(e)}"

    def generate(self, prompt: str) -> str:
        """Bổ sung phương thức tương thích ngược với một số module gọi hàm .generate()"""
        return self.generate_text(prompt)
