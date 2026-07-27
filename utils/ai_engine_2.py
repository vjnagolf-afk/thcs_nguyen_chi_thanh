# -*- coding: utf-8 -*-
"""
============================================================
AI ENGINE 2: TRỢ LÝ AI CHUYÊN SÂU PHỤ TRỢ
FILE: utils/ai_engine_2.py
NÂNG CẤP: TÍCH HỢP SMART ROUTER (TỰ ĐỘNG CHUYỂN MẠCH GEMINI / OPENAI)
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
    Lớp AI Engine phụ trợ, chuyên phục vụ các tác vụ chuyên sâu.
    Tích hợp bộ định tuyến nhận diện tự động API Key (Gemini hoặc OpenAI).
    """

    def __init__(self, default_model: str = "gemini-2.5-flash"):
        self.default_model = default_model

    def _get_active_api_key(self) -> str:
        """Lấy API Key từ Session State, Streamlit Secrets hoặc Biến môi trường."""
        user_key = st.session_state.get("user_api_key")
        if user_key and str(user_key).strip():
            return str(user_key).strip(' "\'')

        try:
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                secret_key = st.secrets["GEMINI_API_KEY"]
                if secret_key and str(secret_key).strip():
                    return str(secret_key).strip(' "\'')
        except Exception:
            pass

        env_key = os.environ.get("GEMINI_API_KEY")
        if env_key and str(env_key).strip():
            return str(env_key).strip(' "\'')

        return ""

    def generate_text(self, prompt: str, model_name: str = None, temperature: float = 0.7, max_tokens: int = None) -> str:
        """
        Sinh văn bản chuyên sâu. Tự động Route sang OpenAI nếu Key bắt đầu bằng sk- / proj-
        """
        api_key = self._get_active_api_key()
        if not api_key:
            return "❌ Chưa tìm thấy API Key. Vui lòng nhập API Key ở thanh bên (Sidebar)."

        target_model = model_name or self.default_model

        # ----------------------------------------------------
        # 1. SMART ROUTER -> CHUYỂN HƯỚNG OPENAI (GPT)
        # ----------------------------------------------------
        if api_key.startswith("sk-") or "proj-" in api_key:
            try:
                import openai
                oai_client = openai.OpenAI(api_key=api_key)
                
                # Ánh xạ tên model cho OpenAI
                oai_model = "gpt-4o" if "pro" in target_model.lower() else "gpt-4o-mini"
                
                response = oai_client.chat.completions.create(
                    model=oai_model,
                    messages=[
                        {"role": "system", "content": "Bạn là chuyên gia giáo dục đỉnh cao."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens if max_tokens else 8192
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"❌ Lỗi khi gọi OpenAI API: {str(e)}"

        # ----------------------------------------------------
        # 2. CHẠY MẶC ĐỊNH LÀ GEMINI (GOOGLE GENAI)
        # ----------------------------------------------------
        if genai is None:
            return "❌ Thư viện 'google-genai' chưa được cài đặt."

        model_mapping = {
            "3.1 Flash-Lite": "gemini-2.5-flash", 
            "3.5 Flash": "gemini-2.5-flash",
            "3.1 Pro": "gemini-2.5-pro",
            "Tư duy mở rộng": "gemini-2.5-pro",
            "google/gemini-2.5-flash": "gemini-2.5-flash"
        }
        resolved_model_name = model_mapping.get(target_model, target_model)

        try:
            client = genai.Client(api_key=api_key)
            config_kwargs = {"temperature": temperature}
            if max_tokens:
                config_kwargs["max_output_tokens"] = max_tokens

            config = types.GenerateContentConfig(**config_kwargs)

            # Gọi API Google
            response = client.models.generate_content(
                model=resolved_model_name,
                contents=prompt,
                config=config
            )
            
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            
            return "⚠️ AI Engine 2 không trả về nội dung hợp lệ."

        except Exception as e:
            err_str = str(e)
            # Bắt cụ thể lỗi API sai để thông báo tiếng Việt rõ ràng
            if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
                return "❌ Lỗi: API Key Gemini không hợp lệ. Vui lòng kiểm tra lại Key (Phải bắt đầu bằng chữ AIza... và không có khoảng trắng)."
            return f"❌ Lỗi khi gọi AI Engine 2: {err_str}"

    def generate_multimodal(self, contents: list, model_name: str = "gemini-2.5-pro", temperature: float = 0.5) -> str:
        """
        Hàm Multimodal đọc ảnh (chuyên dụng cho module Chấm Viết).
        Hỗ trợ cả Gemini và GPT-4o.
        """
        api_key = self._get_active_api_key()
        if not api_key:
            return "❌ Chưa tìm thấy API Key."

        # ----------------------------------------------------
        # 1. ROUTER MULTIMODAL CHO OPENAI
        # ----------------------------------------------------
        if api_key.startswith("sk-") or "proj-" in api_key:
            try:
                import openai
                import base64
                from io import BytesIO
                
                oai_client = openai.OpenAI(api_key=api_key)
                messages_content = []
                
                for item in contents:
                    if isinstance(item, str):
                        messages_content.append({"type": "text", "text": item})
                    else:
                        # Convert PIL Image sang Base64
                        buffered = BytesIO()
                        item.save(buffered, format="JPEG")
                        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                        messages_content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}
                        })

                response = oai_client.chat.completions.create(
                    model="gpt-4o", # Bắt buộc dùng GPT-4o để xử lý ảnh
                    messages=[{"role": "user", "content": messages_content}],
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"❌ Lỗi OpenAI Đa phương thức: {str(e)}"

        # ----------------------------------------------------
        # 2. GEMINI MULTIMODAL
        # ----------------------------------------------------
        if genai is None:
            return "❌ Thư viện 'google-genai' chưa được cài đặt."

        try:
            client = genai.Client(api_key=api_key)
            target_model = model_name if model_name else "gemini-2.5-pro"
            config = types.GenerateContentConfig(temperature=temperature)
            
            response = client.models.generate_content(
                model=target_model,
                contents=contents,
                config=config
            )
            
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            return "⚠️ AI Engine 2 (Multimodal) không trả về kết quả."

        except Exception as e:
            err_str = str(e)
            if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
                return "❌ Lỗi: API Key Gemini không hợp lệ (Phải bắt đầu bằng AIza...)."
            return f"❌ Lỗi Đa phương thức: {err_str}"

    def generate(self, prompt: str) -> str:
        """Hỗ trợ tương thích ngược"""
        return self.generate_text(prompt)
