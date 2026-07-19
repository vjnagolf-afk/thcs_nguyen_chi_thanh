# ============================================================
# ai_engine.py
# AI ENGINE CORE v1.2 (Kiến trúc OpenRouter Độc lập)
# Hệ sinh thái số THCS Nguyễn Chí Thanh
# ============================================================
import os
import json
import hashlib
import time
import io
from typing import List, Dict, Any, Optional
from loguru import logger

# ============================================================
# CACHE
# ============================================================
try:
    from cachetools import TTLCache
    api_cache = TTLCache(maxsize=1000, ttl=86400)
except ImportError:
    api_cache = {}

# ============================================================
# IMAGE
# ============================================================
try:
    from PIL import Image
except ImportError:
    Image = None

# ============================================================
# TOKENIZER
# ============================================================
try:
    import tiktoken
except ImportError:
    tiktoken = None

# ============================================================
# SDK PROVIDERS
# ============================================================
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

# Lấy cấu hình model mặc định từ Secrets, phòng hờ nếu không có sẽ dùng Gemini 2.5 Flash
DEFAULT_OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")

# ============================================================
# MODEL PRICE TABLE (Bao gồm cả mã định danh OpenRouter)
# USD / 1M tokens
# ============================================================
MODEL_PRICES = {
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00},
    # Ánh xạ giá cho OpenRouter tương ứng
    "google/gemini-2.5-flash": {"input": 0.30, "output": 2.50},
    "google/gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "anthropic/claude-3-5-sonnet": {"input": 3.00, "output": 15.00}
}
# ============================================================
# CHAT MEMORY
# ============================================================
class ChatMemory:
    def __init__(self, max_history=10):
        self.history = []
        self.max_history = max_history

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]

    def get_context_string(self):
        return "\n".join([f"{m['role']}: {m['content']}" for m in self.history])


# ============================================================
# AI ENGINE
# ============================================================
class AIEngine:
    MODELS = {
        "flash": "gemini-2.5-flash",
        "pro": "gemini-2.5-pro"
    }

    def __init__(self, api_key: str = None, keys: Dict[str, str] = None, system_prompt: str = None):
        self.keys = keys if keys is not None else {}
        if api_key:
            self.keys["gemini"] = api_key

        self.system_prompt = (
            system_prompt or """
Bạn là AI Teacher Assistant.
Nhiệm vụ:
- Hỗ trợ giáo viên THCS.
- Bám sát CT GDPT 2018.
- Trả lời có cấu trúc.
- Ưu tiên tính chính xác và khả năng áp dụng.
"""
        )

        # Khởi tạo bảng lưu trữ token và chi phí
        self.token_usage = {k: 0 for k in MODEL_PRICES.keys()}
        self.cost_estimate = {k: 0 for k in MODEL_PRICES.keys()}

        self.active_endpoints = []
        self.gemini_clients = {}
        self.openai_clients = {}
        self.claude_clients = {}
        self.openrouter_clients = {}  # Pool lưu trữ Client OpenRouter độc lập

        # 1. LOAD GEMINI KEY
        if self.keys.get("gemini"):
            gemini_keys = [k.strip() for k in self.keys["gemini"].split(",")] if isinstance(self.keys["gemini"], str) else self.keys["gemini"]
            for key in gemini_keys:
                if key:
                    self.active_endpoints.append(("gemini", key))

        # 2. LOAD OPENAI / OPENROUTER KEY (Kiểm tra và phân loại ngay từ đầu vào)
        if self.keys.get("openai"):
            openai_key = self.keys["openai"].strip()
            if openai_key.startswith("sk-or-v1"):
                self.active_endpoints.append(("openrouter", openai_key))
            else:
                self.active_endpoints.append(("openai", openai_key))

        # 3. LOAD CLAUDE KEY
        if self.keys.get("claude"):
            self.active_endpoints.append(("claude", self.keys["claude"]))

        # =========================
        # INIT CLIENT POOL
        # =========================
        for provider, key in self.active_endpoints:
            if provider == "gemini":
                if genai is None:
                    logger.error("Thiếu thư viện google-genai")
                else:
                    self.gemini_clients[key] = genai.Client(api_key=key)
            elif provider == "openai":
                if openai:
                    self.openai_clients[key] = openai.Client(api_key=key, timeout=60)
            elif provider == "openrouter":
                if openai:
                    # Sửa lỗi địa chỉ: Cấu hình chuẩn endpoint OpenRouter
                    self.openrouter_clients[key] = openai.Client(
                        api_key=key,
                        base_url="https://openrouter.ai/api/v1",
                        timeout=60
                    )
            elif provider == "claude":
                if anthropic:
                    self.claude_clients[key] = anthropic.Anthropic(api_key=key, timeout=60)

        self.gemini_models = {
            "text": self.MODELS["flash"],
            "vision": self.MODELS["pro"]
        }
        logger.info(f"AI Engine v1.2 initialized - {len(self.active_endpoints)} endpoints")
    # =====================================================
    # CACHE KEY
    # =====================================================
    def _get_cache_key(self, prompt, kwargs):
        raw = prompt + json.dumps(kwargs, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    # =====================================================
    # TOKEN ESTIMATION
    # =====================================================
    def _estimate_tokens(self, text, provider="gemini"):
        if tiktoken:
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(text))
            except Exception:
                pass
        return int(len(text.split()) * 1.3)

    # =====================================================
    # COST UPDATE
    # =====================================================
    def _update_stats(self, model, input_tokens, output_tokens):
        total_tokens = input_tokens + output_tokens
        if model in self.token_usage:
            self.token_usage[model] += total_tokens
        else:
            self.token_usage[model] = total_tokens

        if model in MODEL_PRICES:
            price = MODEL_PRICES[model]
            cost = (input_tokens * price["input"] / 1_000_000)
            cost += (output_tokens * price["output"] / 1_000_000)
            self.cost_estimate[model] = self.cost_estimate.get(model, 0) + cost

    # =====================================================
    # GENERATE TEXT
    # =====================================================
    def generate_text(self, prompt: str, memory: Optional[ChatMemory] = None, use_cache=True, **kwargs):
        full_prompt = prompt
        if memory:
            context = memory.get_context_string()
            if context:
                full_prompt = (
                    "Ngữ cảnh hội thoại:\n"
                    + context
                    + "\n\nCâu hỏi mới:\n"
                    + prompt
                )
        cache_key = self._get_cache_key(full_prompt, kwargs)
        if use_cache and cache_key in api_cache:
            logger.info("Lấy dữ liệu từ Cache")
            return api_cache[cache_key]

        last_error = None
        for provider, api_key in self.active_endpoints:
            try:
                result, model_name = self._call_provider(
                    provider,
                    api_key,
                    full_prompt,
                    **kwargs
                )
                if use_cache:
                    api_cache[cache_key] = result
                
                if memory:
                    if (not memory.history or memory.history[-1]["content"] != prompt):
                        memory.add_message("User", prompt)
                        memory.add_message("AI", result)
                        
                input_tokens = self._estimate_tokens(full_prompt, provider)
                output_tokens = self._estimate_tokens(result, provider)
                self._update_stats(model_name, input_tokens, output_tokens)
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"{provider.upper()} lỗi: {e}")
                time.sleep(2)

        raise Exception(f"Tất cả AI Provider lỗi: {last_error}")

    # =====================================================
    # PROVIDER ROUTER
    # =====================================================
    def _call_provider(self, provider, api_key, prompt, **kwargs):
        # ==========================================
        # 1. GEMINI (Google SDK gốc)
        # ==========================================
        if provider == "gemini":
            client = self.gemini_clients[api_key]
            model_name = (
                kwargs.get("model")
                or kwargs.get("model_name")
                or self.MODELS["flash"]
            )
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=kwargs.get("temperature", 0.7),
                    max_output_tokens=kwargs.get("max_tokens", 4096),
                    system_instruction=kwargs.get("system_prompt", self.system_prompt)
                )
            )
            return (response.text, model_name)

        # ==========================================
        # 2. OPENAI (OpenAI SDK gốc - Chỉ chạy key sk-proj-)
        # ==========================================
        elif provider == "openai":
            client = self.openai_clients[api_key]
            model_name = (
                kwargs.get("model")
                or kwargs.get("model_name")
                or "gpt-4o-mini"
            )
            current_system_prompt = kwargs.get("system_prompt", self.system_prompt)
            openai_messages = []
            if current_system_prompt:
                openai_messages.append({"role": "system", "content": current_system_prompt})
            openai_messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model_name,
                messages=openai_messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096)
            )
            return (response.choices.message.content, model_name)

        # ==========================================
        # 3. OPENROUTER (Nhánh độc lập chuẩn hóa)
        # ==========================================
        elif provider == "openrouter":
            client = self.openrouter_clients[api_key]
            # Sửa lỗi chọn sai model: Lấy trực tiếp từ biến môi trường của thầy
            model_name = (
                kwargs.get("model")
                or kwargs.get("model_name")
                or DEFAULT_OPENROUTER_MODEL
            )
            current_system_prompt = kwargs.get("system_prompt", self.system_prompt)
            or_messages = []
            if current_system_prompt:
                or_messages.append({"role": "system", "content": current_system_prompt})
            or_messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model_name,
                messages=or_messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096)
            )
            return (response.choices.message.content, model_name)

        # ==========================================
        # 4. CLAUDE (Anthropic SDK gốc)
        # ==========================================
        elif provider == "claude":
            client = self.claude_clients[api_key]
            model_name = (
                kwargs.get("model")
                or kwargs.get("model_name")
                or "claude-3-5-sonnet-20240620"
            )
            current_system_prompt = kwargs.get("system_prompt", self.system_prompt)

            response = client.messages.create(
                model=model_name,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7),
                system=current_system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return (response.content.text, model_name)

        else:
            raise ValueError(f"Provider {provider} không được hỗ trợ.")
