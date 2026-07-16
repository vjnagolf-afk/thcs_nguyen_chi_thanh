import os
import json
import hashlib
import time
import streamlit as st

from typing import List, Dict, Any, Optional
from loguru import logger
import google.generativeai as genai

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
    Kiến trúc cấp doanh nghiệp: Đa Key, Fallback thông minh, Timeout & Retry an toàn.
    """
    
    # 1. Thống nhất Model mặc định (Dùng chuẩn models/...)
    MODELS = {
        "flash": "models/gemini-2.5-flash",
        "pro": "models/gemini-2.5-pro"
    }

    def __init__(self, api_key: str = None, keys: Dict[str, str] = None):
        self.keys = keys if keys is not None else {}
        if api_key and "gemini" not in self.keys:
            self.keys["gemini"] = api_key
            
        self.token_usage = {"gemini": 0, "openai": 0, "claude": 0}
        self.cost_estimate = 0.0
        
        # Hàng đợi Endpoints (Góp ý 12: Danh sách các điểm cuối cần chạy tuần tự)
        self.active_endpoints = []

        # 1. Nạp danh sách Gemini Keys (Hỗ trợ 1 key hoặc nhiều key cách nhau bằng dấu phẩy)
        if self.keys.get("gemini"):
            g_keys = [k.strip() for k in self.keys["gemini"].split(",")] if isinstance(self.keys["gemini"], str) else self.keys["gemini"]
            for k in g_keys:
                if k: self.active_endpoints.append(("gemini", k))

        # 2. Nạp OpenAI Key
        if self.keys.get("openai"):
            self.active_endpoints.append(("openai", self.keys["openai"]))

        # 3. Nạp Claude Key
        if self.keys.get("claude"):
            self.active_endpoints.append(("claude", self.keys["claude"]))

        # Khởi tạo tự động nhận diện Model Gemini (Chỉ cần mượn Key Gemini đầu tiên để quét)
        self.gemini_models = {"text": self.MODELS["flash"], "vision": self.MODELS["pro"]}
        first_gemini_key = next((k for p, k in self.active_endpoints if p == "gemini"), None)
        if first_gemini_key:
            genai.configure(api_key=first_gemini_key)
            self.gemini_models = self._auto_detect_gemini_models()
            self.MODELS["flash"] = self.gemini_models["text"]
            self.MODELS["pro"] = self.gemini_models["vision"]

        logger.info(f"🚀 AI Engine Core Initialized. Active Endpoints: {len(self.active_endpoints)}")

    # ==========================================
    # 1. TỰ ĐỘNG PHÁT HIỆN MODEL (BỀN VỮNG)
    # ==========================================
    def _auto_detect_gemini_models(self) -> Dict[str, str]:
        """✅ Tự động quét Model bằng Keyword thay vì hardcode phiên bản (Góp ý 2)"""
        available = {"text": self.MODELS["flash"], "vision": self.MODELS["pro"]} 
        try:
            models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            
            # Quét bằng chuỗi ký tự linh hoạt
            flash_model = next((m for m in models if "flash" in m.lower()), None)
            pro_model = next((m for m in models if "pro" in m.lower()), None)
            
            if flash_model: available["text"] = flash_model
            if pro_model: available["vision"] = pro_model
                
            logger.info(f"Detected Gemini Models: {available}")
        except Exception as e:
            logger.warning(f"Không thể tự phát hiện model, dùng mặc định. Lỗi: {e}")
        return available

    # ==========================================
    # 2. CACHING & TOKEN TRACKING
    # ==========================================
    def _get_cache_key(self, prompt: str, kwargs: dict) -> str:
        """✅ Sử dụng SHA256 cho an toàn với prompt dài (Góp ý 6)"""
        raw = prompt + json.dumps(kwargs, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _update_stats(self, provider: str, estimated_tokens: int):
        self.token_usage[provider] = self.token_usage.get(provider, 0) + estimated_tokens
        self.cost_estimate += (estimated_tokens / 1000) * 0.0001 

    # ==========================================
    # 3. ROUTER LÕI & MULTI-KEY FALLBACK
    # ==========================================
    def generate_text(self, prompt: str, memory: Optional[ChatMemory] = None, use_cache: bool = True, **kwargs) -> str:
        """✅ Sinh văn bản với Retry/Fallback tuấn tự trên toàn bộ kho API Keys"""
        
        full_prompt = prompt
        if memory:
            full_prompt = f"Ngữ cảnh:\n{memory.get_context_string()}\n\nCâu hỏi mới: {prompt}"

        # Kiểm tra Cache
        cache_key = self._get_cache_key(full_prompt, kwargs)
        if use_cache and cache_key in api_cache:
            logger.success("⚡ Lấy kết quả từ Cache!")
            return api_cache[cache_key]

        last_error = None

        # Vòng lặp Hàng đợi (Duyệt qua từng Key của Gemini -> OpenAI -> Claude)
        for provider, api_key in self.active_endpoints:
            # Góp ý 3: Retry 2 lần cho MỖI Endpoint
            for attempt in range(2): 
                try:
                    response_text = self._call_provider(provider, api_key, full_prompt, **kwargs)
                    
                    # Lưu Cache & Memory
                    if use_cache:
                        api_cache[cache_key] = response_text
                    if memory:
                        memory.add_message("User", prompt)
                        memory.add_message("AI", response_text)
                    
                    # Ước lượng Token (Góp ý 8: Hệ số nhân 1.3 theo cấu trúc tiếng Việt)
                    est_tokens = int((len(full_prompt.split()) + len(response_text.split())) * 1.3)
                    self._update_stats(provider, est_tokens)
                    
                    return response_text
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    logger.warning(f"⚠️ Lỗi {provider.upper()} (Key: ...{api_key[-4:]}) - Lần {attempt+1}: {e}")
                    last_error = e
                    
                    # Kỹ thuật Fast-Fail: Nếu hết Quota (429) hoặc Cấm (403), không cần Retry, nhảy Key kế tiếp
                    if "429" in error_msg or "quota" in error_msg or "403" in error_msg or "exhausted" in error_msg:
                        logger.warning(f"⏩ Bỏ qua Key này do cạn Quota. Chuyển nhà cung cấp / Key tiếp theo...")
                        break # Phá vòng lặp attempt, đi tới Key kế tiếp trong active_endpoints
                    
                    time.sleep(2) # Nghỉ 2s trước khi Retry với các lỗi 500/503

        if not self.active_endpoints:
            raise ValueError("❌ Không có API Key nào được cấu hình.")
            
        raise Exception(f"❌ Toàn bộ kho AI Key đều quá tải hoặc hết Quota. Lỗi cuối: {last_error}")

    def _call_provider(self, provider: str, api_key: str, prompt: str, **kwargs) -> str:
        """Thực thi gọi API cụ thể, chèn Log và giới hạn Timeout 60s (Góp ý 4, 7)"""
        
        if provider == "gemini":
            genai.configure(api_key=api_key)
            model_name = kwargs.get("model_name") or kwargs.get("model") or self.gemini_models["text"]
            logger.info(f"Provider: GEMINI | Model: {model_name} | Prompt length: {len(prompt)}")
            
            model = genai.GenerativeModel(model_name)
            # Giới hạn timeout 60s thông qua request_options
            return model.generate_content(prompt, request_options={"timeout": 60}).text
            
        elif provider == "openai":
            model_name = kwargs.get("model_name") or kwargs.get("model") or "gpt-4o-mini"
            logger.info(f"Provider: OPENAI | Model: {model_name} | Prompt length: {len(prompt)}")
            
            import openai
            client = openai.Client(api_key=api_key)
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                timeout=60 # Giới hạn chống treo máy
            )
            return response.choices[0].message.content
            
        elif provider == "claude":
            model_name = kwargs.get("model_name") or kwargs.get("model") or "claude-3-5-sonnet-20240620"
            logger.info(f"Provider: CLAUDE | Model: {model_name} | Prompt length: {len(prompt)}")
            
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model_name,
                max_tokens=kwargs.get("max_tokens", 8192),
                messages=[{"role": "user", "content": prompt}],
                timeout=60 # Giới hạn chống treo máy
            )
            return response.content[0].text
            
        raise NotImplementedError(f"Nhà cung cấp {provider} đang được xây dựng.")

    # ==========================================
    # 4. CÁC TÍNH NĂNG NÂNG CAO (VISION, RAG)
    # ==========================================
    def generate_vision(self, prompt: str, image_bytes: Any) -> str:
        """✅ Xử lý Đa phương thức (Tìm key Gemini đầu tiên để chạy kèm Retry thủ công)"""
        gemini_key = next((k for p, k in self.active_endpoints if p == "gemini"), None)
        if not gemini_key:
            raise Exception("Tính năng Vision yêu cầu ít nhất 1 API Key của Gemini.")
            
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(self.gemini_models["vision"])
        
        for attempt in range(2):
            try:
                logger.info(f"Provider: GEMINI VISION | Prompt length: {len(prompt)}")
                return model.generate_content([prompt, image_bytes], request_options={"timeout": 60}).text
            except Exception as e:
                logger.warning(f"Lỗi Vision Lần {attempt+1}: {e}")
                if attempt == 1: raise e
                time.sleep(2)

    def rag_query(self, query: str, documents: List[str]) -> str:
        """✅ Hàm chuẩn cho RAG: Chèn tài liệu vào Prompt"""
        context = "\n".join(documents)
        prompt = f"Dựa vào các tài liệu sau, hãy trả lời câu hỏi.\n\n[TÀI LIỆU]:\n{context}\n\n[CÂU HỎI]: {query}"
        return self.generate_text(prompt, use_cache=False)

    def generate_image(self, prompt: str):
        """✅ Sinh ảnh (Dự phòng cho DALL-E 3)"""
        openai_key = next((k for p, k in self.active_endpoints if p == "openai"), None)
        if openai_key:
            import openai
            client = openai.Client(api_key=openai_key)
            response = client.images.generate(
                model="dall-e-3", prompt=prompt, n=1, size="1024x1024"
            )
            return response.data[0].url
        raise Exception("Tính năng sinh ảnh yêu cầu API Key OpenAI.")
        
    def get_stats(self) -> dict:
        """Trả về thống kê sử dụng"""
        return {"tokens": self.token_usage, "estimated_cost_usd": self.cost_estimate}
