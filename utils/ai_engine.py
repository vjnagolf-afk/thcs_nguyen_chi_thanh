import os
import json
import hashlib
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
    def __init__(self, keys: Dict[str, str]):
        """Khởi tạo với bộ keys của nhiều nhà cung cấp"""
        self.keys = keys
        self.token_usage = {"gemini": 0, "openai": 0, "claude": 0}
        self.cost_estimate = 0.0
        
        # ✅ Ưu tiên nhà cung cấp (Router)
        self.provider_priority = ["gemini", "openai", "claude"]
        
        # Khởi tạo Gemini
        if keys.get("gemini"):
            genai.configure(api_key=keys["gemini"])
            self.gemini_models = self._auto_detect_gemini_models()
        
        # Khởi tạo OpenAI/Claude (Sẽ import khi cần để tránh nặng hệ thống)
        self.openai_client = None
        if keys.get("openai"):
            import openai
            self.openai_client = openai.Client(api_key=keys["openai"])

        logger.info("🚀 AI Engine Core Initialized successfully.")

    # ==========================================
    # 1. TỰ ĐỘNG PHÁT HIỆN MODEL (Auto-discovery)
    # ==========================================
    def _auto_detect_gemini_models(self) -> Dict[str, str]:
        """✅ Tự động quét các model đang sống của Google"""
        available = {"text": "gemini-1.5-flash", "vision": "gemini-1.5-pro"} # Mặc định an toàn
        try:
            models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            
            # Smart routing: Tìm model mới nhất
            if any("3.5-flash" in m for m in models):
                available["text"] = "models/gemini-3.5-flash"
            elif any("2.5-flash" in m for m in models):
                available["text"] = "models/gemini-2.5-flash"
                
            if any("3.1-pro" in m for m in models):
                available["vision"] = "models/gemini-3.1-pro-preview"
                
            logger.info(f"Detected Gemini Models: {available}")
        except Exception as e:
            logger.warning(f"Không thể tự phát hiện model, dùng mặc định. Lỗi: {e}")
        return available

    # ==========================================
    # 2. CACHING & TOKEN TRACKING
    # ==========================================
    def _get_cache_key(self, prompt: str, kwargs: dict) -> str:
        """Tạo mã băm cho prompt để làm khóa Cache"""
        raw = prompt + json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(raw.encode()).hexdigest()

    def _update_stats(self, provider: str, tokens: int):
        """✅ Thống kê Token và tính chi phí (Giả lập)"""
        self.token_usage[provider] = self.token_usage.get(provider, 0) + tokens
        # Ví dụ: 0.0001$ / 1k token
        self.cost_estimate += (tokens / 1000) * 0.0001 

    # ==========================================
    # 3. ROUTER LÕI & QUẢN LÝ QUOTA FALLBACK
    # ==========================================
    def generate_text(self, prompt: str, memory: Optional[ChatMemory] = None, use_cache: bool = True, **kwargs) -> str:
        """✅ Hàm sinh văn bản thống nhất có Caching và Fallback"""
        
        # 1. Ghép ngữ cảnh nếu có Memory
        full_prompt = prompt
        if memory:
            full_prompt = f"Ngữ cảnh:\n{memory.get_context_string()}\n\nCâu hỏi mới: {prompt}"

        # 2. Kiểm tra Cache
        cache_key = self._get_cache_key(full_prompt, kwargs)
        if use_cache and isinstance(api_cache, dict) and cache_key in api_cache:
            logger.success("⚡ Lấy kết quả từ Cache!")
            return api_cache[cache_key]
        elif use_cache and not isinstance(api_cache, dict):
            if cache_key in api_cache:
                logger.success("⚡ Lấy kết quả từ Cache!")
                return api_cache[cache_key]

        # 3. Chuỗi Fallback (Chain of Responsibility)
        last_error = None
        for provider in self.provider_priority:
            if not self.keys.get(provider):
                continue
                
            try:
                logger.info(f"Đang gọi AI qua nhà cung cấp: {provider.upper()}")
                response_text = self._call_provider(provider, full_prompt, **kwargs)
                
                # Lưu vào Cache và Memory
                if use_cache:
                    api_cache[cache_key] = response_text
                if memory:
                    memory.add_message("User", prompt)
                    memory.add_message("AI", response_text)
                    
                # Cập nhật Token (Giả lập 1 từ ~ 1.3 token)
                self._update_stats(provider, len(full_prompt.split()) + len(response_text.split()))
                return response_text
                
            except Exception as e:
                logger.warning(f"⚠️ Lỗi {provider.upper()} (Quota/Network): {str(e)}. Tự động chuyển nguồn...")
                last_error = e

        raise Exception(f"❌ Toàn bộ AI đều quá tải hoặc hết Quota. Lỗi cuối cùng: {str(last_error)}")

    def _call_provider(self, provider: str, prompt: str, **kwargs) -> str:
        """Thực thi gọi API cụ thể cho từng nhà cung cấp"""
        if provider == "gemini":
            model_name = kwargs.get("model", self.gemini_models["text"])
            model = genai.GenerativeModel(model_name)
            return model.generate_content(prompt).text
            
        elif provider == "openai":
            if not self.openai_client: raise ValueError("Chưa cấu hình OpenAI")
            response = self.openai_client.chat.completions.create(
                model=kwargs.get("model", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
            
        # Tương tự cho Claude/OpenRouter...
        raise NotImplementedError(f"Nhà cung cấp {provider} đang được xây dựng.")

    # ==========================================
    # 4. CÁC TÍNH NĂNG NÂNG CAO (RAG, VISION, TTS)
    # ==========================================
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_vision(self, prompt: str, image_bytes: Any) -> str:
        """✅ Xử lý Đa phương thức (Hình ảnh + Text)"""
        # Ưu tiên Gemini cho Vision vì miễn phí và mạnh
        try:
            model = genai.GenerativeModel(self.gemini_models["vision"])
            # (Thực tế sẽ cần chuyển đổi image_bytes sang cấu trúc PIL hoặc Blob)
            response = model.generate_content([prompt, image_bytes])
            return response.text
        except Exception as e:
            logger.exception("Lỗi Vision API")
            raise

    def rag_query(self, query: str, documents: List[str]) -> str:
        """✅ Hàm chuẩn cho RAG: Chèn tài liệu vào Prompt"""
        context = "\n".join(documents)
        prompt = f"Dựa vào các tài liệu sau, hãy trả lời câu hỏi.\n\n[TÀI LIỆU]:\n{context}\n\n[CÂU HỎI]: {query}"
        return self.generate_text(prompt, use_cache=False) # RAG thường không nên cache cứng

    def generate_image(self, prompt: str):
        """✅ Sinh ảnh (Dự phòng cho DALL-E 3 hoặc Midjourney via OpenRouter)"""
        if "openai" in self.keys and self.openai_client:
            response = self.openai_client.images.generate(
                model="dall-e-3", prompt=prompt, n=1, size="1024x1024"
            )
            return response.data[0].url
        raise Exception("Tính năng sinh ảnh yêu cầu API Key OpenAI.")
        
    def get_stats(self) -> dict:
        """Trả về thống kê sử dụng"""
        return {"tokens": self.token_usage, "estimated_cost_usd": self.cost_estimate}
