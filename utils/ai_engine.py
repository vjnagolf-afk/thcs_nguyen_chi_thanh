# ai_engine.py
"""
AI Engine Core
Hệ sinh thái số giáo dục THCS Nguyễn Chí Thanh

Nguyên tắc:
- Không thay đổi kiến trúc hệ thống
- Không thay đổi interface các module đang sử dụng
- Chỉ chuẩn hóa kết nối AI SDK
"""

import os
import json
import hashlib
import time
import io

from typing import List, Dict, Any, Optional
from loguru import logger


# ==============================
# CACHE
# ==============================

try:
    from cachetools import TTLCache

    api_cache = TTLCache(
        maxsize=1000,
        ttl=86400
    )

except ImportError:
    api_cache = {}



# ==============================
# IMAGE
# ==============================

try:
    from PIL import Image

except ImportError:
    Image = None



# ==============================
# AI SDK
# ==============================

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



# ======================================================
# MEMORY
# ======================================================

class ChatMemory:
    """
    Quản lý lịch sử hội thoại
    """

    def __init__(
        self,
        max_history=10
    ):

        self.history = []
        self.max_history = max_history



    def add_message(
        self,
        role: str,
        content: str
    ):

        self.history.append(
            {
                "role": role,
                "content": content
            }
        )


        if len(self.history) > self.max_history * 2:

            self.history = self.history[
                -self.max_history * 2:
            ]



    def get_context_string(self):

        return "\n".join(
            [
                f"{x['role']}: {x['content']}"
                for x in self.history
            ]
        )



# ======================================================
# AI ENGINE
# ======================================================

class AIEngine:

    MODELS = {

        "flash":
            "gemini-2.5-flash",

        "pro":
            "gemini-2.5-pro"
    }



    def __init__(
        self,
        api_key: str = None,
        keys: Dict[str,str] = None
    ):


        self.keys = (
            keys
            if keys is not None
            else {}
        )


        if api_key:

            self.keys["gemini"] = api_key



        self.token_usage = {

            "gemini":0,
            "openai":0,
            "claude":0
        }


        self.cost_estimate = 0.0



        self.active_endpoints = []



        self.gemini_clients = {}
        self.openai_clients = {}
        self.claude_clients = {}



        # ==========================
        # GEMINI KEYS
        # ==========================

        if self.keys.get("gemini"):


            if isinstance(
                self.keys["gemini"],
                str
            ):

                gemini_keys = [
                    x.strip()
                    for x in
                    self.keys["gemini"].split(",")
                ]

            else:

                gemini_keys = self.keys["gemini"]



            for key in gemini_keys:

                if key:

                    self.active_endpoints.append(
                        (
                            "gemini",
                            key
                        )
                    )



        # ==========================
        # OPENAI
        # ==========================

        if self.keys.get("openai"):

            self.active_endpoints.append(
                (
                    "openai",
                    self.keys["openai"]
                )
            )



        # ==========================
        # CLAUDE
        # ==========================

        if self.keys.get("claude"):

            self.active_endpoints.append(
                (
                    "claude",
                    self.keys["claude"]
                )
            )



        # ==========================
        # CLIENT POOL
        # ==========================


        for provider,key in self.active_endpoints:


            if provider == "gemini":


                if genai is None:

                    logger.error(
                        "Thiếu google-genai"
                    )

                else:

                    self.gemini_clients[key] = (
                        genai.Client(
                            api_key=key
                        )
                    )



            elif provider == "openai":


                if openai:

                    self.openai_clients[key] = (
                        openai.Client(
                            api_key=key,
                            timeout=60
                        )
                    )



            elif provider == "claude":


                if anthropic:

                    self.claude_clients[key] = (
                        anthropic.Anthropic(
                            api_key=key,
                            timeout=60
                        )
                    )



        self.gemini_models = {

            "text":
                self.MODELS["flash"],

            "vision":
                self.MODELS["pro"]

        }



        logger.info(
            f"AI Engine initialized: {len(self.active_endpoints)} endpoints"
        )



    # ==================================================
    # CACHE
    # ==================================================

    def _get_cache_key(
        self,
        prompt,
        kwargs
    ):

        raw = (
            prompt +
            json.dumps(
                kwargs,
                sort_keys=True
            )
        )

        return hashlib.sha256(
            raw.encode()
        ).hexdigest()



    def _update_stats(
        self,
        provider,
        tokens
    ):

        self.token_usage[provider] += tokens

        self.cost_estimate += (
            tokens / 1000
        ) * 0.0001



    # ==================================================
    # GENERATE TEXT
    # ==================================================

    def generate_text(
        self,
        prompt: str,
        memory: Optional[ChatMemory]=None,
        use_cache=True,
        **kwargs
    ):


        full_prompt = prompt


        if memory:

            full_prompt = (
                "Ngữ cảnh:\n"
                +
                memory.get_context_string()
                +
                "\n\nCâu hỏi mới:\n"
                +
                prompt
            )



        cache_key = self._get_cache_key(
            full_prompt,
            kwargs
        )



        if use_cache and cache_key in api_cache:

            return api_cache[cache_key]



        last_error = None



        for provider,key in self.active_endpoints:


            try:

                result = self._call_provider(
                    provider,
                    key,
                    full_prompt,
                    **kwargs
                )


                if use_cache:

                    api_cache[cache_key] = result



                if memory:

                    memory.add_message(
                        "User",
                        prompt
                    )

                    memory.add_message(
                        "AI",
                        result
                    )



                self._update_stats(
                    provider,
                    int(len(result.split())*1.3)
                )


                return result



            except Exception as e:

                last_error = e

                logger.warning(
                    f"{provider} lỗi: {e}"
                )

                time.sleep(2)



        raise Exception(
            f"Tất cả AI provider lỗi: {last_error}"
        )



    # ==================================================
    # PROVIDER ROUTER
    # ==================================================

    def _call_provider(
        self,
        provider,
        api_key,
        prompt,
        **kwargs
    ):



        if provider == "gemini":


            client = self.gemini_clients[api_key]


            model = (
                kwargs.get("model")
                or
                kwargs.get("model_name")
                or
                self.MODELS["flash"]
            )


            response = client.models.generate_content(

                model=model,

                contents=prompt,

                config=types.GenerateContentConfig(

                    temperature=
                    kwargs.get(
                        "temperature",
                        0.7
                    ),

                    max_output_tokens=
                    kwargs.get(
                        "max_tokens",
                        4096
                    )

                )

            )


            return response.text



        elif provider == "openai":


            client = self.openai_clients[api_key]


            response = client.chat.completions.create(

                model=
                kwargs.get(
                    "model",
                    "gpt-4o-mini"
                ),

                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]

            )


            return (
                response
                .choices[0]
                .message
                .content
            )



        elif provider == "claude":


            client = self.claude_clients[api_key]


            response = client.messages.create(

                model=
                kwargs.get(
                    "model",
                    "claude-3-5-sonnet-20240620"
                ),

                max_tokens=8192,

                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]

            )


            return response.content[0].text



        raise Exception(
            "Provider không hỗ trợ"
        )



    # ==================================================
    # VISION
    # ==================================================

    def generate_vision(
        self,
        prompt,
        image_bytes
    ):


        if Image is None:

            raise Exception(
                "Thiếu Pillow"
            )


        if isinstance(
            image_bytes,
            bytes
        ):

            img = Image.open(
                io.BytesIO(
                    image_bytes
                )
            )

        else:

            img = image_bytes



        key = next(

            (
                k
                for p,k
                in self.active_endpoints
                if p=="gemini"
            ),

            None
        )



        if not key:

            raise Exception(
                "Cần Gemini Key"
            )



        response = self.gemini_clients[key].models.generate_content(

            model=self.gemini_models["vision"],

            contents=[
                prompt,
                img
            ]

        )


        return response.text



    # ==================================================
    # RAG
    # ==================================================

    def rag_query(
        self,
        query,
        documents:List[str]
    ):


        context="\n".join(
            documents
        )


        prompt=f"""

Dựa vào tài liệu sau:

{context}


Câu hỏi:

{query}

"""


        return self.generate_text(
            prompt,
            use_cache=False
        )



    # ==================================================
    # IMAGE
    # ==================================================

    def generate_image(
        self,
        prompt
    ):

        raise Exception(
            "Chức năng sinh ảnh giữ nguyên mở rộng sau"
        )



    # ==================================================
    # STATS
    # ==================================================

    def get_stats(self):

        return {

            "tokens":
                self.token_usage,

            "estimated_cost_usd":
                self.cost_estimate
        }
