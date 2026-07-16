import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

# Cấu hình Cache cục bộ 
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
        
        # ✅ Thứ tự ưu tiên nhà cung cấp
        self.provider_priority = ["gemini", "openai", "claude"]
        
        # Khởi tạo Gemini
        if keys.get("gemini"):
            genai.configure(api_key=keys["gemini"])
            self.gemini_models = self._auto_detect_gemini_models()
            
        # Khởi tạo OpenAI
        self.openai_client = None
        if keys.get("openai"):
            import openai
            self.openai_client = openai.Client(api_key=keys["openai"])
            
        logger.info("🚀 AI Engine Core Initialized successfully.")

    # ==========================================
    # 1. TỰ ĐỘNG PHÁT HIỆN MODEL (Auto-discovery)
    # ==========================================
    def _auto_detect_gemini_models(self) -> Dict[str, str]:
        """✅ Tự động quét các model đang hoạt động hiệu quả nhất của Google"""
        available = {"text": "gemini-1.5-flash", "vision": "gemini-1.5-flash"} 
        try:
            models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            
            # Khớp chuỗi tìm model tối ưu nhất hiện có
            for m_name in models:
                clean_name = m_name.replace("models/", "")
                if "2.5-flash" in clean_name:
                    available["text"] = clean_name
                    available["vision"] = clean_name
                    break
                elif "1.5-flash" in clean_name:
                    available["text"] = clean_name
                    available["vision"] = clean_name
            logger.info(f"Detected Gemini Models: {available}")
        except Exception as e:
            logger.warning(f"Không thể tự phát hiện model, dùng mặc định: {available}. Lỗi: {e}")
        return available

    # ==========================================
    # 2. CACHING & TOKEN TRACKING
    # ==========================================
    def _get_cache_key(self, prompt: str, kwargs: dict) -> str:
        """Tạo mã băm cho prompt để làm khóa Cache"""
        raw = prompt + json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(raw.encode()).hexdigest()

    def _update_stats(self, provider: str, tokens: int):
        """✅ Thống kê Token và tính chi phí giả lập"""
        self.token_usage[provider] = self.token_usage.get(provider, 0) + tokens
        self.cost_estimate += (tokens / 1000) * 0.0001 

    # ==========================================
    # 3. ROUTER LÕI & QUẢN LÝ QUOTA FALLBACK
    # ==========================================
    def generate_text(self, prompt: str, memory: Optional[ChatMemory] = None, use_cache: bool = True, **kwargs) -> str:
        """✅ Hàm sinh văn bản thống nhất có Caching và Fallback"""
        # 1. Ghép ngữ cảnh bộ nhớ hội thoại
        full_prompt = prompt
        if memory:
            full_prompt = f"Ngữ cảnh:\n{memory.get_context_string()}\n\nCâu hỏi mới: {prompt}"

        # 2. Kiểm tra bộ nhớ Cache (Rút gọn tối ưu logic)
        cache_key = self._get_cache_key(full_prompt, kwargs)
        if use_cache and cache_key in api_cache:
            logger.success("⚡ Lấy kết quả thành công từ Cache!")
            return api_cache[cache_key]

        # 3. Chuỗi Fallback tự động hoán đổi khi lỗi nguồn cấp
        last_error = RuntimeError("Không tìm thấy nhà cung cấp dịch vụ AI nào được cấu hình API Key hợp lệ.")
        
        for provider in self.provider_priority:
            if not self.keys.get(provider):
                continue
            try:
                logger.info(f"Đang gọi AI qua nhà cung cấp: {provider.upper()}")
                response_text = self._call_provider(provider, full_prompt, **kwargs)
                
                # Cập nhật dữ liệu lưu trữ sau khi thành công
                if use_cache:
                    api_cache[cache_key] = response_text
                if memory:
                    memory.add_message("User", prompt)
                    memory.add_message("AI", response_text)
                    
                # Ước lượng Token sử dụng
                self._update_stats(provider, len(full_prompt.split()) + len(response_text.split()))
                return response_text
            except Exception as e:
                logger.warning(f"⚠️ Lỗi mạng/Hết hạn mức {provider.upper()}: {str(e)}. Tự động đổi nguồn...")
                last_error = e
                
        raise Exception(f"❌ Toàn bộ hệ thống AI đều quá tải hoặc hết Quota. Lỗi hệ thống cuối cùng: {str(last_error)}")

    def _call_provider(self, provider: str, prompt: str, **kwargs) -> str:
        """Thực thi trực tiếp API tương ứng từ nhà cung cấp"""
        if provider == "gemini":
            model_name = kwargs.get("model", self.gemini_models["text"])
            model = genai.GenerativeModel(model_name)
            return model.generate_content(prompt).text
            
        elif provider == "openai":
            if not self.openai_client:
                raise ValueError("Chưa cấu hình API Key cấp quyền cho nhà cung cấp OpenAI")
            response = self.openai_client.chat.completions.create(
                model=kwargs.get("model", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
            
        raise NotImplementedError(f"Nhà cung cấp mạng {provider} hiện chưa được tích hợp hệ thống.")

    # ==========================================
    # 4. CÁC TÍNH NĂNG NÂNG CAO (RAG, VISION, TTS)
    # ==========================================
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_vision(self, prompt: str, image_bytes: Any) -> str:
        """✅ Xử lý đa phương thức phân tích Hình ảnh + Văn bản"""
        try:
            model = genai.GenerativeModel(self.gemini_models["vision"])
            # Thêm hỗ trợ bọc trực tiếp gói dữ liệu ảnh thô cho thư viện SDK Google mới
            image_data = [{"mime_type": "image/jpeg", "data": image_bytes}] if isinstance(image_bytes, bytes) else image_bytes
            response = model.generate_content([prompt, image_data])
            return response.text
        except Exception as e:
            logger.exception("Gặp lỗi nghiêm trọng tại Vision API")
            raise

    def rag_query(self, query: str, documents: List[str]) -> str:
        """✅ Trích xuất thông tin ngữ cảnh mở rộng RAG"""
        context = "\n".join(documents)
        prompt = f"Dựa vào các tài liệu sau, hãy trả lời câu hỏi.\n\n[TÀI LIỆU]:\n{context}\n\n[CÂU HỎI]: {query}"
        return self.generate_text(prompt, use_cache=False)

    def generate_image(self, prompt: str):
        """✅ Khởi tạo tác vụ sinh ảnh nghệ thuật số"""
        if self.openai_client:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        raise Exception("Tính năng sinh ảnh yêu cầu cấu hình API Key OpenAI hợp lệ.")

    def get_stats(self) -> dict:
        """Trả về báo cáo thống kê sử dụng tài nguyên"""
        return {"tokens": self.token_usage, "estimated_cost_usd": self.cost_estimate}
