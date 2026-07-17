# ============================================================
# ai_engine.py
# AI ENGINE CORE v1.1
# Hệ sinh thái số THCS Nguyễn Chí Thanh
#
# Chỉ nâng cấp phương thức kết nối AI:
# - Gemini google-genai SDK mới
# - System Instruction
# - Token tracking
# - Cost tracking theo model
# - Claude SDK parsing
# - Memory chống duplicate fallback
#
# Không thay đổi interface hệ thống
# ============================================================


import os
import json
import hashlib
import time
import io

from typing import (
    List,
    Dict,
    Any,
    Optional
)

from loguru import logger


# ============================================================
# CACHE
# ============================================================

try:

    from cachetools import TTLCache

    api_cache = TTLCache(
        maxsize=1000,
        ttl=86400
    )

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
# GOOGLE GEMINI SDK
# ============================================================

try:

    from google import genai
    from google.genai import types


except ImportError:

    genai = None
    types = None



# ============================================================
# OPENAI
# ============================================================

try:

    import openai


except ImportError:

    openai = None



# ============================================================
# CLAUDE
# ============================================================

try:

    import anthropic


except ImportError:

    anthropic = None



# ============================================================
# MODEL PRICE TABLE
# USD / 1M tokens
# ============================================================

MODEL_PRICES = {


    "gemini-2.5-flash":
    {
        "input": 0.30,
        "output": 2.50
    },


    "gemini-2.5-pro":
    {
        "input": 1.25,
        "output": 10.00
    },


    "gpt-4o-mini":
    {
        "input": 0.15,
        "output": 0.60
    },


    "claude-3-5-sonnet-20240620":
    {
        "input": 3.00,
        "output": 15.00
    }

}



# ============================================================
# CHAT MEMORY
# ============================================================

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


            self.history = (
                self.history[
                    -self.max_history*2:
                ]
            )



    def get_context_string(
        self
    ):

        return "\n".join(

            [

                f"{m['role']}: {m['content']}"

                for m in self.history

            ]

        )



# ============================================================
# AI ENGINE
# ============================================================

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

        keys: Dict[str,str] = None,

        system_prompt: str = None

    ):


        self.keys = (

            keys

            if keys is not None

            else {}

        )



        if api_key:

            self.keys["gemini"] = api_key



        # =========================
        # SYSTEM INSTRUCTION
        # =========================

        self.system_prompt = (

            system_prompt

            or

            """
Bạn là AI Teacher Assistant.

Nhiệm vụ:
- Hỗ trợ giáo viên THCS.
- Bám sát CT GDPT 2018.
- Trả lời có cấu trúc.
- Ưu tiên tính chính xác và khả năng áp dụng.
"""

        )



        # =========================
        # TOKEN / COST
        # =========================


        self.token_usage = {


            "gemini-2.5-flash":0,

            "gemini-2.5-pro":0,

            "gpt-4o-mini":0,

            "claude-3-5-sonnet-20240620":0

        }



        self.cost_estimate = {


            "gemini-2.5-flash":0,

            "gemini-2.5-pro":0,

            "gpt-4o-mini":0,

            "claude-3-5-sonnet-20240620":0

        }



        # =========================
        # CLIENT POOL
        # =========================


        self.active_endpoints = []

        self.gemini_clients = {}

        self.openai_clients = {}

        self.claude_clients = {}



        # =========================
        # LOAD GEMINI KEY
        # =========================


        if self.keys.get("gemini"):


            if isinstance(
                self.keys["gemini"],
                str
            ):


                gemini_keys = [

                    k.strip()

                    for k

                    in self.keys["gemini"].split(",")

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


# ---------------- HẾT PHẦN 1/3 ----------------
        # =========================
        # LOAD OPENAI KEY
        # =========================

        if self.keys.get("openai"):

            self.active_endpoints.append(

                (
                    "openai",
                    self.keys["openai"]
                )

            )



        # =========================
        # LOAD CLAUDE KEY
        # =========================

        if self.keys.get("claude"):

            self.active_endpoints.append(

                (
                    "claude",
                    self.keys["claude"]
                )

            )



        # =========================
        # INIT CLIENT POOL
        # =========================

        for provider, key in self.active_endpoints:



            if provider == "gemini":


                if genai is None:

                    logger.error(
                        "Thiếu thư viện google-genai"
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

            f"AI Engine v1.1 initialized - "
            f"{len(self.active_endpoints)} endpoints"

        )



    # =====================================================
    # CACHE KEY
    # =====================================================

    def _get_cache_key(

        self,

        prompt,

        kwargs

    ):


        raw = (

            prompt

            +

            json.dumps(

                kwargs,

                sort_keys=True

            )

        )


        return hashlib.sha256(

            raw.encode()

        ).hexdigest()



    # =====================================================
    # TOKEN ESTIMATION
    # =====================================================

    def _estimate_tokens(

        self,

        text,

        provider="gemini"

    ):


        if tiktoken:


            try:


                encoding = tiktoken.get_encoding(

                    "cl100k_base"

                )


                return len(

                    encoding.encode(text)

                )


            except Exception:

                pass



        return int(

            len(text.split())

            *

            1.3

        )



    # =====================================================
    # COST UPDATE
    # =====================================================

    def _update_stats(

        self,

        model,

        input_tokens,

        output_tokens

    ):


        total_tokens = (

            input_tokens

            +

            output_tokens

        )


        if model in self.token_usage:


            self.token_usage[model] += total_tokens



        else:


            self.token_usage[model] = total_tokens



        if model in MODEL_PRICES:


            price = MODEL_PRICES[model]


            cost = (

                input_tokens

                *

                price["input"]

                /

                1_000_000

            )


            cost += (

                output_tokens

                *

                price["output"]

                /

                1_000_000

            )


            self.cost_estimate[model] = (

                self.cost_estimate.get(
                    model,
                    0
                )

                +

                cost

            )



    # =====================================================
    # GENERATE TEXT
    # =====================================================

    def generate_text(

        self,

        prompt: str,

        memory: Optional[ChatMemory] = None,

        use_cache=True,

        **kwargs

    ):


        full_prompt = prompt



        if memory:


            context = memory.get_context_string()



            if context:


                full_prompt = (

                    "Ngữ cảnh hội thoại:\n"

                    +

                    context

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


            logger.info(
                "Lấy dữ liệu từ Cache"
            )


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



                # tránh duplicate memory khi fallback


                if memory:


                    if (

                        not memory.history

                        or

                        memory.history[-1]["content"]

                        !=

                        prompt

                    ):


                        memory.add_message(

                            "User",

                            prompt

                        )



                    memory.add_message(

                        "AI",

                        result

                    )



                input_tokens = self._estimate_tokens(

                    full_prompt,

                    provider

                )


                output_tokens = self._estimate_tokens(

                    result,

                    provider

                )



                self._update_stats(

                    model_name,

                    input_tokens,

                    output_tokens

                )



                return result



            except Exception as e:


                last_error = e


                logger.warning(

                    f"{provider.upper()} lỗi: {e}"

                )


                time.sleep(2)



        raise Exception(

            f"Tất cả AI Provider lỗi: {last_error}"

        )



    # =====================================================
    # PROVIDER ROUTER
    # =====================================================

    def _call_provider(

        self,

        provider,

        api_key,

        prompt,

        **kwargs

    ):


        # =========================
        # GEMINI
        # =========================

        if provider == "gemini":


            client = self.gemini_clients[api_key]



            model_name = (

                kwargs.get("model")

                or

                kwargs.get("model_name")

                or

                self.MODELS["flash"]

            )



            response = client.models.generate_content(


                model=model_name,


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

                    ),


                    system_instruction=

                    kwargs.get(

                        "system_prompt",

                        self.system_prompt

                    )

                )

            )



            return (

                response.text,

                model_name

            )



        # =========================
        # OPENAI
        # =========================

        elif provider == "openai":


            client = self.openai_clients[api_key]



            model_name = kwargs.get(

                "model",

                "gpt-4o-mini"

            )



            response = client.chat.completions.create(


                model=model_name,


                messages=[

                    {

                        "role":"system",

                        "content":
                        self.system_prompt

                    },

                    {

                        "role":"user",

                        "content":
                        prompt

                    }

                ]

            )



            return (

                response.choices[0].message.content,

                model_name

            )



        # =========================
        # CLAUDE
        # =========================

        elif provider == "claude":


            client = self.claude_clients[api_key]



            model_name = kwargs.get(

                "model",

                "claude-3-5-sonnet-20240620"

            )



            response = client.messages.create(


                model=model_name,


                max_tokens=

                kwargs.get(

                    "max_tokens",

                    8192

                ),


                system=self.system_prompt,


                messages=[

                    {

                        "role":"user",

                        "content":prompt

                    }

                ]

            )



            text_parts = []



            for block in response.content:


                if hasattr(

                    block,

                    "text"

                ):


                    text_parts.append(

                        block.text

                    )



            return (

                "\n".join(text_parts),

                model_name

            )



        raise Exception(

            "Provider không hỗ trợ"

        )
            # =====================================================
    # VISION
    # =====================================================

    def generate_vision(

        self,

        prompt: str,

        image_bytes: Any

    ):


        if Image is None:

            raise Exception(
                "Thiếu Pillow. Cài đặt: pip install Pillow"
            )



        # Chuyển bytes -> PIL Image

        if isinstance(

            image_bytes,

            bytes

        ):


            image = Image.open(

                io.BytesIO(

                    image_bytes

                )

            )


        else:

            image = image_bytes



        gemini_key = next(

            (

                key

                for provider, key

                in self.active_endpoints

                if provider == "gemini"

            ),

            None

        )



        if not gemini_key:

            raise Exception(

                "Vision yêu cầu Gemini API Key"

            )



        client = self.gemini_clients[gemini_key]



        model_name = self.gemini_models["vision"]



        try:


            response = client.models.generate_content(

                model=model_name,


                contents=[

                    prompt,

                    image

                ],


                config=types.GenerateContentConfig(

                    system_instruction=self.system_prompt,

                    temperature=0.5

                )

            )


            return response.text



        except Exception as e:


            error = str(e).lower()



            # fallback model

            if (

                "404" in error

                or

                "not found" in error

            ):


                logger.warning(

                    "Vision model lỗi, chuyển Gemini Flash"

                )



                response = client.models.generate_content(

                    model="gemini-2.5-flash",


                    contents=[

                        prompt,

                        image

                    ]

                )


                return response.text



            raise e





    # =====================================================
    # RAG QUERY
    # =====================================================

    def rag_query(

        self,

        query: str,

        documents: List[str]

    ):


        context = "\n\n".join(

            documents

        )



        prompt = f"""

Bạn là trợ lý AI giáo viên.

Hãy trả lời dựa trên tài liệu cung cấp.

=====================
TÀI LIỆU:
{context}

=====================

CÂU HỎI:
{query}

"""


        return self.generate_text(

            prompt,

            use_cache=False

        )





    # =====================================================
    # IMAGE GENERATION
    # =====================================================

    def generate_image(

        self,

        prompt: str

    ):


        openai_key = next(

            (

                key

                for provider, key

                in self.active_endpoints

                if provider == "openai"

            ),

            None

        )



        if not openai_key:


            raise Exception(

                "Cần OpenAI API Key để sinh ảnh"

            )



        client = self.openai_clients[openai_key]



        response = client.images.generate(

            model="dall-e-3",

            prompt=prompt,

            n=1,

            size="1024x1024"

        )



        return response.data[0].url





    # =====================================================
    # TEST CONNECTION
    # =====================================================

    def test_connection(

        self

    ):


        try:


            result = self.generate_text(

                "Kiểm tra kết nối AI. Trả lời OK."

            )


            return {


                "status": True,

                "message": result

            }



        except Exception as e:


            return {


                "status": False,

                "message": str(e)

            }





    # =====================================================
    # STATISTICS
    # =====================================================

    def get_stats(

        self

    ):


        return {


            "token_usage":

            self.token_usage,


            "cost_usd":

            self.cost_estimate,


            "total_cost":

            round(

                sum(

                    self.cost_estimate.values()

                ),

                6

            ),


            "active_endpoints":

            len(

                self.active_endpoints

            )

        }
