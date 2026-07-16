import os
import json
import hashlib
import time
import io
import streamlit as st

from typing import List, Dict, Any, Optional
from loguru import logger

# 1. Quản lý Caching
try:
    from cachetools import TTLCache
    api_cache = TTLCache(maxsize=1000, ttl=86400) 
except ImportError:
    api_cache = {}

# 2. Xử lý Ảnh (Vision)
try:
    from PIL import Image
except ImportError:
    Image = None

# 3. Các Thư viện SDK AI (Import an toàn)
try:
    from google import genai
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None


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
    Kiến trúc Client Pool, Multi-Key Fallback, Timeout & Retry an toàn.
    """
    
    # Đã loại bỏ tiền tố "models/" cho tương thích 100% với SDK google-genai
    MODELS = {
        "flash": "gemini-2.5-flash",
        "pro": "gemini-2.5-pro"
    }

    def __init__(self, api_key: str = None, keys: Dict[str, str] = None):
        self.keys = keys if keys is not None else {}
        if api_key and "gemini" not in self.keys:
            self.keys["gemini"] = api_key
            
        self.token_usage = {"gemini": 0, "openai": 0, "claude": 0}
        self.cost_estimate = 0.0
        
        # Hàng đợi Endpoints
        self.active_endpoints = []
        
        # Connection Pools (Lưu trữ Client đã khởi tạo)
        self.gemini_clients = {}
        self.openai_clients = {}
        self.claude_clients = {}

        # 1. Nạp danh sách Gemini Keys
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

        # 4. KHỞI TẠO CLIENT POOLS (Chỉ tạo 1 lần duy nhất)
        for provider, key in self.active_endpoints:
            if provider == "gemini":
                if genai is None:
                    logger.error("Thiếu SDK Google mới. Hãy chạy: pip install google-genai")
                else:
                    self.gemini_clients[key] = genai.Client(api_key=key)
                    
            elif provider == "openai":
                if openai is not None:
                    # Gán sẵn timeout vào Client để chống treo
                    self.openai_clients[key] = openai.Client(api_key=key, timeout=60.0)
                    
            elif provider == "claude":
                if anthropic is not None:
                    # Gán sẵn timeout vào Client
                    self.claude_clients[key] = anthropic.Anthropic(api_key=key, timeout=60.0)

        # 5. Tự động nhận diện Model Gemini (Sử dụng SDK mới)
        self.gemini_models = {"text": self.MODELS["flash"], "vision": self.MODELS["pro"]}
        if self.gemini_clients:
            self.gemini_models = self._auto_detect_gemini_models()
            self.MODELS["flash"] = self.gemini_models["text"]
            self.MODELS["pro"] = self.gemini_models["vision"]

        logger.info(f"🚀 AI Engine Core Initialized. Active Endpoints: {len(self.active_endpoints)}")

    # ==========================================
    # 1. TỰ ĐỘNG PHÁT HIỆN MODEL (SDK google-genai mới)
    # ==========================================
    def _auto_detect_gemini_models(self) -> Dict[str, str]:
        available = {"text": self.MODELS["flash"], "vision": self.MODELS["pro"]} 
        if not self.gemini_clients:
            return available
            
        # Mượn Client đầu tiên để quét Model
        first_key = list(self.gemini_clients.keys())[0]
        client = self.gemini_clients[first_key]
        
        try:
            # Lọc sạch tiền tố "models/" nếu API của Google trả về dạng cũ
            clean_models = [m.name.replace("models/", "") for m in client.models.list()]
            
            flash_model = next((m for m in clean_models if "flash" in m.lower()), None)
            pro_model = next((m for m in clean_models if "pro" in m.lower()), None)
            
            if flash_model: available["text"] = flash_model
            if pro_model: available["vision"] = pro_model
                
            logger.info(f"Detected Gemini Models: {available}")
        except Exception as e:
            logger.warning(f"Không thể tự phát hiện model SDK mới, dùng mặc định. Lỗi: {e}")
        return available

    # ==========================================
    # 2. CACHING & TOKEN TRACKING
    # ==========================================
    def _get_cache_key(self, prompt: str, kwargs: dict) -> str:
        raw = prompt + json.dumps(kwargs, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _update_stats(self, provider: str, estimated_tokens: int):
        self.token_usage[provider] = self.token_usage.get(provider, 0) + estimated_tokens
        self.cost_estimate += (estimated_tokens / 1000) * 0.0001 

    # ==========================================
    # 3. ROUTER LÕI & MULTI-KEY FALLBACK
    # ==========================================
    def generate_text(self, prompt: str, memory: Optional[ChatMemory] = None, use_cache: bool = True, **kwargs) -> str:
        full_prompt = prompt
        if memory:
            full_prompt = f"Ngữ cảnh:\n{memory.get_context_string()}\n\nCâu hỏi mới: {prompt}"

        # Kiểm tra Cache
        cache_key = self._get_cache_key(full_prompt, kwargs)
        if use_cache and cache_key in api_cache:
            logger.success("⚡ Lấy kết quả từ Cache!")
            return api_cache[cache_key]

        last_error = None

        # Vòng lặp Duyệt qua từng Endpoint
        for provider, api_key in self.active_endpoints:
            # Thử 2 lần cho MỖI Endpoint
            for attempt in range(2): 
                try:
                    response_text = self._call_provider(provider, api_key, full_prompt, **kwargs)
                    
                    # Lưu Cache & Memory
                    if use_cache:
                        api_cache[cache_key] = response_text
                    if memory:
                        memory.add_message("User", prompt)
                        memory.add_message("AI", response_text)
                    
                    est_tokens = int((len(full_prompt.split()) + len(response_text.split())) * 1.3)
                    self._update_stats(provider, est_tokens)
                    
                    return response_text
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    logger.warning(f"⚠️ Lỗi {provider.upper()} (Key: ...{api_key[-4:]}) - Lần {attempt+1}: {e}")
                    last_error = e
                    
                    # Fast-Fail: Chuyển Key ngay nếu Hết Quota/Bị cấm/Không tìm thấy
                    if "429" in error_msg or "quota" in error_msg or "403" in error_msg or "exhausted" in error_msg or "404" in error_msg:
                        logger.warning(f"⏩ Bỏ qua Key/Model này do lỗi (Quota/404). Chuyển nhà cung cấp / Key tiếp theo...")
                        break 
                    
                    time.sleep(2) 

        if not self.active_endpoints:
            raise ValueError("❌ Không có API Key nào được cấu hình.")
            
        raise Exception(f"❌ Toàn bộ kho AI Key đều quá tải hoặc hết Quota. Lỗi cuối: {last_error}")

    def _call_provider(self, provider: str, api_key: str, prompt: str, **kwargs) -> str:
        """Thực thi gọi API từ Connection Pool đã tạo sẵn ở __init__"""
        
        if provider == "gemini":
            client = self.gemini_clients.get(api_key)
            if not client: raise ValueError("Lỗi Client Gemini")
            
            model_name = kwargs.get("model_name") or kwargs.get("model") or self.gemini_models["text"]
            logger.info(f"Provider: GEMINI | Model: {model_name} | Prompt length: {len(prompt)}")
            
            # Sử dụng cú pháp của google-genai
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
            
        elif provider == "openai":
            client = self.openai_clients.get(api_key)
            if not client: raise ValueError("Chưa cấu hình OpenAI")
            
            model_name = kwargs.get("model_name") or kwargs.get("model") or "gpt-4o-mini"
            logger.info(f"Provider: OPENAI | Model: {model_name} | Prompt length: {len(prompt)}")
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
            
        elif provider == "claude":
            client = self.claude_clients.get(api_key)
            if not client: raise ValueError("Chưa cấu hình Claude")
            
            model_name = kwargs.get("model_name") or kwargs.get("model") or "claude-3-5-sonnet-20240620"
            logger.info(f"Provider: CLAUDE | Model: {model_name} | Prompt length: {len(prompt)}")
            
            response = client.messages.create(
                model=model_name,
                max_tokens=kwargs.get("max_tokens", 8192),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
            
        raise NotImplementedError(f"Nhà cung cấp {provider} đang được xây dựng.")

    # ==========================================
    # 4. CÁC TÍNH NĂNG NÂNG CAO (VISION, RAG)
    # ==========================================
    def generate_vision(self, prompt: str, image_bytes: Any) -> str:
        """✅ Xử lý Đa phương thức (Sử dụng PIL.Image chuẩn mực)"""
        
        # 1. Chuyển đổi an toàn sang PIL.Image
        if isinstance(image_bytes, bytes):
            if Image is None:
                raise Exception("Thiếu thư viện xử lý ảnh. Hãy chạy: pip install Pillow")
            img = Image.open(io.BytesIO(image_bytes))
        else:
            img = image_bytes  # Giả định đã là PIL.Image nếu không phải bytes

        # 2. Tìm Gemini Key đầu tiên còn sống
        gemini_key = next((k for p, k in self.active_endpoints if p == "gemini"), None)
        if not gemini_key:
            raise Exception("Tính năng Vision yêu cầu ít nhất 1 API Key của Gemini.")
            
        client = self.gemini_clients[gemini_key]
        
        # 3. Gọi SDK Mới
        for attempt in range(2):
            try:
                logger.info(f"Provider: GEMINI VISION | Prompt length: {len(prompt)}")
                response = client.models.generate_content(
                    model=self.gemini_models["vision"],
                    contents=[prompt, img]
                )
                return response.text
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
            client = self.openai_clients[openai_key]
            response = client.images.generate(
                model="dall-e-3", prompt=prompt, n=1, size="1024x1024"
            )
            return response.data[0].url
        raise Exception("Tính năng sinh ảnh yêu cầu API Key OpenAI.")
        
    def get_stats(self) -> dict:
        """Trả về thống kê sử dụng"""
        return {"tokens": self.token_usage, "estimated_cost_usd": self.cost_estimate}
