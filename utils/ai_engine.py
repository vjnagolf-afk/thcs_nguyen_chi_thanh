import os
import json
import hashlib
import streamlit as st

from typing import List, Dict, Any, Optional
from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

# Cấu hình Cache cục bộ (Mô phỏng in-memory caching để giảm API calls)
try:
    from cachetools import TTLCache
    # Cache lưu tối đa 1000 kết quả trong 24 giờ
    api_cache = TTLCache(maxsize=1000, ttl=86400) 
except ImportError:
    api_cache = {}

class ChatMemory:
    """✅ Quản lý bộ nhớ hội thoại (Conversation Memory)"""
    def __init__(self, max_history=10):
        self.history = []
        self.max_history = max_history

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]

    def get_context_string(self) -> str:
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history])


class AIEngine:
    """
    TỔNG ĐỘNG CƠ AI - TRÁI TIM CỦA HỆ SINH THÁI SỐ
    Hỗ trợ Đa nền tảng, Tự động Fallback, Quản lý Quota, Caching và Đa phương thức.
    """
    
    # Biến lớp mặc định
    MODELS = {
        "flash": "gemini-1.5-flash",
        "pro": "gemini-1.5-pro"
    }

    def __init__(self, api_key: str = None, keys: Dict[str, str] = None):
        """Khởi tạo hỗ trợ cả chuẩn cũ (app.py gọi api_key) và chuẩn mới đa nền tảng (keys)"""
        self.keys = keys if keys is not None else {}
        
        if api_key and "gemini" not in self.keys:
            self.keys["gemini"] = api_key
            
        self.token_usage = {"gemini": 0, "openai": 0, "claude": 0}
        self.cost_estimate = 0.0
        # Thứ tự ưu tiên Fallback: Gemini -> OpenAI -> Claude
        self.provider_priority = ["gemini", "openai", "claude"]
        
        # 1. Khởi tạo Gemini
        if self.keys.get("gemini"):
            genai.configure(api_key=self.keys["gemini"])
            logger.info(f"Gemini key: {self.keys['gemini'][:12]}...")
            
            # Quét model trước khi in log để tránh lỗi AttributeError
            self.gemini_models = self._auto_detect_gemini_models()
            logger.info(f"Gemini models: {self.gemini_models}")
            
            self.MODELS["flash"] = self.gemini_models["text"]
            self.MODELS["pro"] = self.gemini_models["vision"]
        
        # 2. Khởi tạo OpenAI (nếu có)
        self.openai_client = None
        if self.keys.get("openai"):
            try:
                import openai
                self.openai_client = openai.Client(api_key=self.keys["openai"])
                logger.info("OpenAI API Initialized.")
            except ImportError:
                logger.warning("Chưa cài thư viện openai. Chạy: pip install openai")

        # 3. Khởi tạo Claude / Anthropic (nếu có)
        self.claude_client = None
        if self.keys.get("claude"):
            try:
                import anthropic
                self.claude_client = anthropic.Anthropic(api_key=self.keys["claude"])
                logger.info("Claude API Initialized.")
            except ImportError:
                logger.warning("Chưa cài thư viện anthropic. Chạy: pip install anthropic")

        logger.info("🚀 AI Engine Core Initialized successfully.")

    # ==========================================
    # 1. TỰ ĐỘNG PHÁT HIỆN MODEL (Auto-discovery)
    # ==========================================
    def _auto_detect_gemini_models(self) -> Dict[str, str]:
        """✅ Tự động quét các model đang sống của Google"""
        available = {"text": "models/gemini-1.5-flash", "vision": "models/gemini-1.5-pro"} 
        try:
            models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            
            if any("1.5-flash" in m for m in models):
                available["text"] = "models/gemini-1.5-flash"
            elif any("pro" in m for m in models):
                available["text"] = "models/gemini-1.5-pro"
                
            if any("1.5-pro" in m for m in models):
                available["vision"] = "models/gemini-1.5-pro"
                
            logger.info(f"Detected Gemini Models: {available}")
        except Exception as e:
            logger.warning(f"Không thể tự phát hiện model, dùng mặc định. Lỗi: {e}")
        return available

    # ==========================================
    # 2. CACHING & TOKEN TRACKING
    # ==========================================
    def _get_cache_key(self, prompt: str, kwargs: dict) -> str:
        raw = prompt + json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(raw.encode()).hexdigest()

    def _update_stats(self, provider: str, tokens: int):
        self.token_usage[provider] = self.token_usage.get(provider, 0) + tokens
        self.cost_estimate += (tokens / 1000) * 0.0001 

    # ==========================================
    # 3. ROUTER LÕI & QUẢN LÝ QUOTA FALLBACK
    # ==========================================
    def generate_text(self, prompt: str, memory: Optional[ChatMemory] = None, use_cache: bool = True, **kwargs) -> str:
        """✅ Hàm sinh văn bản thống nhất có Caching và Fallback an toàn"""
        
        full_prompt = prompt
        if memory:
            full_prompt = f"Ngữ cảnh:\n{memory.get_context_string()}\n\nCâu hỏi mới: {prompt}"

        # Kiểm tra Cache
        cache_key = self._get_cache_key(full_prompt, kwargs)
        if use_cache and cache_key in api_cache:
            logger.success("⚡ Lấy kết quả từ Cache!")
            return api_cache[cache_key]

        last_error = None
        has_valid_provider = False

        # Vòng lặp Fallback tự động
        for provider in self.provider_priority:
            if not self.keys.get(provider):
                continue
                
            has_valid_provider = True
            try:
                logger.info(f"Đang gọi AI qua nhà cung cấp: {provider.upper()}")
                response_text = self._call_provider(provider, full_prompt, **kwargs)
                
                # Lưu Cache & Memory
                if use_cache:
                    api_cache[cache_key] = response_text
                if memory:
                    memory.add_message("User", prompt)
                    memory.add_message("AI", response_text)
                    
                self._update_stats(provider, len(full_prompt.split()) + len(response_text.split()))
                return response_text
                
            except Exception as e:
                logger.warning(f"⚠️ Lỗi {provider.upper()}: {str(e)}. Tự động chuyển nguồn...")
                last_error = e

        if not has_valid_provider:
            raise ValueError("❌ Không có API Key của nhà cung cấp AI nào được cấu hình.")
            
        error_msg = str(last_error) if last_error else "Lỗi không xác định"
        raise Exception(f"❌ Toàn bộ AI đều quá tải hoặc hết Quota. Lỗi cuối cùng: {error_msg}")

    def _call_provider(self, provider: str, prompt: str, **kwargs) -> str:
        """Thực thi gọi API cụ thể cho từng nhà cung cấp"""
        if provider == "gemini":
            model_name = kwargs.get("model_name") or kwargs.get("model") or self.gemini_models["text"]
            model = genai.GenerativeModel(model_name)
            return model.generate_content(prompt).text
            
        elif provider == "openai":
            if not self.openai_client: raise ValueError("Chưa cấu hình OpenAI")
            model_name = kwargs.get("model_name") or kwargs.get("model") or "gpt-4o-mini"
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
            
        elif provider == "claude":
            if not self.claude_client: raise ValueError("Chưa cấu hình Claude")
            model_name = kwargs.get("model_name") or kwargs.get("model") or "claude-3-5-sonnet-20240620"
            response = self.claude_client.messages.create(
                model=model_name,
                max_tokens=kwargs.get("max_tokens", 8192),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
            
        raise NotImplementedError(f"Nhà cung cấp {provider} đang được xây dựng.")

    # ==========================================
    # 4. CÁC TÍNH NĂNG NÂNG CAO (RAG, VISION, TTS)
    # ==========================================
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_vision(self, prompt: str, image_bytes: Any) -> str:
        """✅ Xử lý Đa phương thức (Hình ảnh + Text)"""
        try:
            model = genai.GenerativeModel(self.gemini_models["vision"])
            response = model.generate_content([prompt, image_bytes])
            return response.text
        except Exception as e:
            logger.exception("Lỗi Vision API")
            raise

    def rag_query(self, query: str, documents: List[str]) -> str:
        """✅ Hàm chuẩn cho RAG: Chèn tài liệu vào Prompt"""
        context = "\n".join(documents)
        prompt = f"Dựa vào các tài liệu sau, hãy trả lời câu hỏi.\n\n[TÀI LIỆU]:\n{context}\n\n[CÂU HỎI]: {query}"
        return self.generate_text(prompt, use_cache=False)

    def generate_image(self, prompt: str):
        """✅ Sinh ảnh (Dự phòng cho DALL-E 3 hoặc Midjourney)"""
        if "openai" in self.keys and self.openai_client:
            response = self.openai_client.images.generate(
                model="dall-e-3", prompt=prompt, n=1, size="1024x1024"
            )
            return response.data[0].url
        raise Exception("Tính năng sinh ảnh yêu cầu API Key OpenAI.")
        
    def get_stats(self) -> dict:
        """Trả về thống kê sử dụng"""
        return {"tokens": self.token_usage, "estimated_cost_usd": self.cost_estimate}
