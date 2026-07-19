# ============================================================
# ai_engine_2.py
# AI ENGINE CORE v2.0 - OPENROUTER EDITION
# Hệ sinh thái số THCS Nguyễn Chí Thanh
#
# MỤC ĐÍCH:
# - Dùng riêng cho:
#   1. Viết sáng kiến
#   2. Chấm sáng kiến
#
# KHÔNG THAY ĐỔI:
# - utils/ai_engine.py
# - AI Engine Core v1.1
#
# TƯƠNG THÍCH:
# - generate_text(prompt)
# - generate_vision(prompt, image)
# - test_connection()
# - get_stats()
#
# API:
# OpenRouter
# https://openrouter.ai/api/v1
#
# API KEY:
# sk-or-v1-...
# ============================================================


import os
import io
import json
import time
import hashlib
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
# OPENAI SDK
# ============================================================

try:

    from openai import OpenAI

except ImportError:

    OpenAI = None


# ============================================================
# STREAMLIT SECRETS
# ============================================================

try:

    import streamlit as st

except ImportError:

    st = None


# ============================================================
# OPENROUTER CONFIGURATION
# ============================================================


OPENROUTER_BASE_URL = (

    "https://openrouter.ai/api/v1"

)


# ============================================================
# MODEL PRICES
#
# USD / 1M TOKENS
#
# Giá chỉ dùng để ước tính.
# Có thể cập nhật theo giá thực tế của OpenRouter.
# ============================================================


MODEL_PRICES = {


    # --------------------------------------------------------
    # GOOGLE GEMINI
    # --------------------------------------------------------

    "google/gemini-2.5-flash":

    {

        "input": 0.30,

        "output": 2.50

    },


    "google/gemini-2.5-pro":

    {

        "input": 1.25,

        "output": 10.00

    },


    # --------------------------------------------------------
    # OPENAI
    # --------------------------------------------------------

    "openai/gpt-4o-mini":

    {

        "input": 0.15,

        "output": 0.60

    },


    # --------------------------------------------------------
    # ANTHROPIC
    # --------------------------------------------------------

    "anthropic/claude-3.5-sonnet":

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
    Quản lý lịch sử hội thoại.
    Tương thích với ChatMemory trong ai_engine.py
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

                    -self.max_history * 2:

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
# AI ENGINE 2
# ============================================================


class AIEngine2:


    # ========================================================
    # MODEL CONFIG
    # ========================================================


    MODELS = {


        # Model mặc định cho văn bản

        "text":

        "google/gemini-2.5-flash",


        # Model mạnh hơn cho sáng kiến

        "writing":

        "google/gemini-2.5-flash",


        # Model dùng cho phân tích chuyên sâu

        "analysis":

        "google/gemini-2.5-flash",


        # Model vision

        "vision":

        "google/gemini-2.5-flash"

    }


    # ========================================================
    # FALLBACK MODELS
    # ========================================================


    FALLBACK_MODELS = [

        "google/gemini-2.5-flash",

        "openai/gpt-4o-mini",

        "anthropic/claude-3.5-sonnet"

    ]


    # ========================================================
    # INIT
    # ========================================================


    def __init__(

        self,

        api_key: str = None,

        system_prompt: str = None,

        model: str = None,

        fallback_models: List[str] = None

    ):


        # ----------------------------------------------------
        # LOAD API KEY
        # ----------------------------------------------------


        self.api_key = (

            api_key

            or

            self._load_api_key()

        )


        if not self.api_key:

            raise Exception(

                "Chưa cấu hình OpenRouter API Key."

            )


        # ----------------------------------------------------
        # CHECK API KEY FORMAT
        # ----------------------------------------------------


        if not self.api_key.startswith(

            "sk-or-v1-"

        ):

            logger.warning(

                "API Key không có định dạng "
                "sk-or-v1- của OpenRouter."

            )


        # ----------------------------------------------------
        # OPENROUTER MODEL
        # ----------------------------------------------------


        self.model = (

            model

            or

            self._load_model()

            or

            self.MODELS["text"]

        )


        # ----------------------------------------------------
        # SYSTEM PROMPT
        # ----------------------------------------------------


        self.system_prompt = (

            system_prompt

            or

            """

Bạn là AI Teacher Assistant của hệ sinh thái số
THCS Nguyễn Chí Thanh.

Nhiệm vụ:

- Hỗ trợ giáo viên THCS.
- Bám sát Chương trình GDPT 2018.
- Phân tích có hệ thống.
- Trả lời chính xác.
- Ưu tiên tính thực tiễn.
- Không tự bịa dữ liệu.
- Nếu thiếu thông tin quan trọng, phải nêu rõ.
- Trình bày kết quả rõ ràng, có cấu trúc.

Khi xử lý sáng kiến kinh nghiệm:

- Đánh giá khách quan.
- Không thiên vị.
- Phân biệt rõ:
  + Nhận xét
  + Minh chứng
  + Suy luận
  + Đề xuất cải thiện.

"""

        )


        # ----------------------------------------------------
        # FALLBACK MODELS
        # ----------------------------------------------------


        self.fallback_models = (

            fallback_models

            or

            self.FALLBACK_MODELS

        )


        # ----------------------------------------------------
        # TOKEN USAGE
        # ----------------------------------------------------


        self.token_usage = {}


        # ----------------------------------------------------
        # COST ESTIMATE
        # ----------------------------------------------------


        self.cost_estimate = {}


        # ----------------------------------------------------
        # REQUEST COUNTER
        # ----------------------------------------------------


        self.request_count = 0


        self.success_count = 0


        self.error_count = 0


        # ----------------------------------------------------
        # CLIENT
        # ----------------------------------------------------


        if OpenAI is None:

            raise Exception(

                "Thiếu thư viện openai. "

                "Hãy cài đặt: pip install openai"

            )


        self.client = OpenAI(

            api_key=self.api_key,

            base_url=OPENROUTER_BASE_URL,

            timeout=120.0

        )


        logger.info(

            "AI Engine 2 initialized - "

            "OpenRouter"

        )


    # ========================================================
    # LOAD API KEY
    # ========================================================


    def _load_api_key(

        self

    ):


        # ----------------------------------------------------
        # 1. ENVIRONMENT VARIABLE
        # ----------------------------------------------------


        key = os.getenv(

            "OPENROUTER_API_KEY"

        )


        if key:

            return key


        # ----------------------------------------------------
        # 2. STREAMLIT SECRETS
        # ----------------------------------------------------


        if st is not None:

            try:

                if (

                    "OPENROUTER_API_KEY"

                    in st.secrets

                ):

                    return st.secrets[

                        "OPENROUTER_API_KEY"

                    ]


                if (

                    "openrouter_api_key"

                    in st.secrets

                ):

                    return st.secrets[

                        "openrouter_api_key"

                    ]


                if "OPENROUTER" in st.secrets:

                    section = st.secrets[

                        "OPENROUTER"

                    ]


                    if (

                        "API_KEY"

                        in section

                    ):

                        return section[

                            "API_KEY"

                        ]


            except Exception as e:

                logger.warning(

                    f"Không đọc được Streamlit Secrets: {e}"

                )


        return None


    # ========================================================
    # LOAD MODEL
    # ========================================================


    def _load_model(

        self

    ):


        # ----------------------------------------------------
        # ENV
        # ----------------------------------------------------


        model = os.getenv(

            "OPENROUTER_MODEL"

        )


        if model:

            return model


        # ----------------------------------------------------
        # STREAMLIT SECRETS
        # ----------------------------------------------------


        if st is not None:

            try:

                if (

                    "OPENROUTER_MODEL"

                    in st.secrets

                ):

                    return st.secrets[

                        "OPENROUTER_MODEL"

                    ]

            except Exception:

                pass


        return None


    # ========================================================
    # CACHE KEY
    # ========================================================


    def _get_cache_key(

        self,

        prompt: str,

        kwargs: Dict[str, Any]

    ):


        raw = (

            prompt

            +

            json.dumps(

                kwargs,

                sort_keys=True,

                default=str

            )

        )


        return hashlib.sha256(

            raw.encode(

                "utf-8"

            )

        ).hexdigest()


    # ========================================================
    # TOKEN ESTIMATION
    # ========================================================


    def _estimate_tokens(

        self,

        text: str

    ):


        if not text:

            return 0


        if tiktoken:

            try:

                encoding = (

                    tiktoken.get_encoding(

                        "cl100k_base"

                    )

                )


                return len(

                    encoding.encode(

                        text

                    )

                )


            except Exception:

                pass


        # Ước tính cho tiếng Việt

        return max(

            1,

            int(

                len(text.split())

                * 1.3

            )

        )


    # ========================================================
    # UPDATE STATISTICS
    # ========================================================


    def _update_stats(

        self,

        model: str,

        input_tokens: int,

        output_tokens: int

    ):


        total_tokens = (

            input_tokens

            +

            output_tokens

        )


        self.token_usage[model] = (

            self.token_usage.get(

                model,

                0

            )

            +

            total_tokens

        )


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


    # ========================================================
    # NORMALIZE RESPONSE
    # ========================================================


    def _extract_response_text(

        self,

        response

    ):


        try:

            text = (

                response.choices[0]

                .message.content

            )


            if text:

                return text


        except Exception:

            pass


        return ""


    # ========================================================
    # GENERATE TEXT
    # ========================================================


    def generate_text(

        self,

        prompt: str,

        memory: Optional[ChatMemory] = None,

        use_cache=True,

        **kwargs

    ):


        if not prompt:

            raise ValueError(

                "Prompt không được để trống."

            )


        # ----------------------------------------------------
        # MEMORY
        # ----------------------------------------------------


        full_prompt = prompt


        if memory:

            context = (

                memory.get_context_string()

            )


            if context:

                full_prompt = (

                    "NGỮ CẢNH HỘI THOẠI:\n"

                    +

                    context

                    +

                    "\n\n"

                    +

                    "YÊU CẦU MỚI:\n"

                    +

                    prompt

                )


        # ----------------------------------------------------
        # CACHE
        # ----------------------------------------------------


        cache_key = (

            self._get_cache_key(

                full_prompt,

                kwargs

            )

        )


        if (

            use_cache

            and

            cache_key in api_cache

        ):

            logger.info(

                "AI Engine 2: Lấy dữ liệu từ Cache"

            )


            return api_cache[cache_key]


        # ----------------------------------------------------
        # MODEL ORDER
        # ----------------------------------------------------


        requested_model = (

            kwargs.get(

                "model"

            )

            or

            kwargs.get(

                "model_name"

            )

            or

            self.model

        )


        models_to_try = [

            requested_model

        ]


        for fallback in self.fallback_models:

            if fallback not in models_to_try:

                models_to_try.append(

                    fallback

                )


        # ----------------------------------------------------
        # REQUEST PARAMETERS
        # ----------------------------------------------------


        temperature = kwargs.get(

            "temperature",

            0.7

        )


        max_tokens = kwargs.get(

            "max_tokens",

            8192

        )


        system_prompt = kwargs.get(

            "system_prompt",

            self.system_prompt

        )


        last_error = None


        self.request_count += 1


        # ----------------------------------------------------
        # TRY MODELS
        # ----------------------------------------------------


        for model_name in models_to_try:


            try:

                logger.info(

                    f"OpenRouter request: "

                    f"{model_name}"

                )


                response = (

                    self.client.chat.completions.create(

                        model=model_name,

                        messages=[

                            {

                                "role":

                                "system",

                                "content":

                                system_prompt

                            },

                            {

                                "role":

                                "user",

                                "content":

                                full_prompt

                            }

                        ],

                        temperature=temperature,

                        max_tokens=max_tokens

                    )

                )


                result = (

                    self._extract_response_text(

                        response

                    )

                )


                if not result:

                    raise Exception(

                        "AI trả về nội dung rỗng."

                    )


                # ------------------------------------------------
                # CACHE
                # ------------------------------------------------


                if use_cache:

                    api_cache[cache_key] = (

                        result

                    )


                # ------------------------------------------------
                # MEMORY
                # ------------------------------------------------


                if memory:

                    if (

                        not memory.history

                        or

                        memory.history[-1][

                            "content"

                        ]

                        != prompt

                    ):

                        memory.add_message(

                            "User",

                            prompt

                        )


                    memory.add_message(

                        "AI",

                        result

                    )


                # ------------------------------------------------
                # TOKEN
                # ------------------------------------------------


                input_tokens = (

                    self._estimate_tokens(

                        full_prompt

                    )

                )


                output_tokens = (

                    self._estimate_tokens(

                        result

                    )

                )


                self._update_stats(

                    model_name,

                    input_tokens,

                    output_tokens

                )


                self.success_count += 1


                logger.success(

                    f"OpenRouter thành công: "

                    f"{model_name}"

                )


                return result


            except Exception as e:


                last_error = e


                self.error_count += 1


                logger.warning(

                    f"Model {model_name} lỗi: "

                    f"{e}"

                )


                time.sleep(1)


        raise Exception(

            "AI Engine 2 - Tất cả model "

            "OpenRouter lỗi: "

            f"{last_error}"

        )


    # ========================================================
    # GENERATE VISION
    # ========================================================


    def generate_vision(

        self,

        prompt: str,

        image_bytes: Any,

        **kwargs

    ):


        if Image is None:

            raise Exception(

                "Thiếu Pillow."

            )


        # ----------------------------------------------------
        # IMAGE INPUT
        # ----------------------------------------------------


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


        if image is None:

            raise Exception(

                "Ảnh không hợp lệ."

            )


        # ----------------------------------------------------
        # CONVERT TO DATA URL
        # ----------------------------------------------------


        image_buffer = io.BytesIO()


        image.save(

            image_buffer,

            format="PNG"

        )


        image_base64 = (

            __import__(

                "base64"

            )

            .b64encode(

                image_buffer.getvalue()

            )

            .decode(

                "utf-8"

            )

        )


        image_url = (

            "data:image/png;base64,"

            +

            image_base64

        )


        # ----------------------------------------------------
        # MODEL
        # ----------------------------------------------------


        model_name = (

            kwargs.get(

                "model"

            )

            or

            self.MODELS["vision"]

        )


        system_prompt = kwargs.get(

            "system_prompt",

            self.system_prompt

        )


        temperature = kwargs.get(

            "temperature",

            0.5

        )


        max_tokens = kwargs.get(

            "max_tokens",

            8192

        )


        # ----------------------------------------------------
        # REQUEST
        # ----------------------------------------------------


        response = (

            self.client.chat.completions.create(

                model=model_name,

                messages=[

                    {

                        "role":

                        "system",

                        "content":

                        system_prompt

                    },

                    {

                        "role":

                        "user",

                        "content":

                        [

                            {

                                "type":

                                "text",

                                "text":

                                prompt

                            },

                            {

                                "type":

                                "image_url",

                                "image_url":

                                {

                                    "url":

                                    image_url

                                }

                            }

                        ]

                    }

                ],

                temperature=temperature,

                max_tokens=max_tokens

            )

        )


        result = (

            self._extract_response_text(

                response

            )

        )


        if not result:

            raise Exception(

                "AI Vision trả về nội dung rỗng."

            )


        # ----------------------------------------------------
        # STATS
        # ----------------------------------------------------


        input_tokens = (

            self._estimate_tokens(

                prompt

            )

        )


        output_tokens = (

            self._estimate_tokens(

                result

            )

        )


        self._update_stats(

            model_name,

            input_tokens,

            output_tokens

        )


        return result


    # ========================================================
    # RAG QUERY
    # ========================================================


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

========================
TÀI LIỆU:
{context}

========================

CÂU HỎI:
{query}

"""


        return self.generate_text(

            prompt,

            use_cache=False

        )


    # ========================================================
    # TEST CONNECTION
    # ========================================================


    def test_connection(

        self

    ):


        try:


            result = (

                self.generate_text(

                    "Kiểm tra kết nối AI. "

                    "Chỉ trả lời: OK.",

                    use_cache=False,

                    max_tokens=50

                )

            )


            return {

                "status":

                True,

                "message":

                result

            }


        except Exception as e:


            return {

                "status":

                False,

                "message":

                str(e)

            }


    # ========================================================
    # GET STATS
    # ========================================================


    def get_stats(

        self

    ):


        return {

            "engine":

            "AIEngine2",

            "provider":

            "OpenRouter",

            "model":

            self.model,

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

            "request_count":

            self.request_count,

            "success_count":

            self.success_count,

            "error_count":

            self.error_count,

            "base_url":

            OPENROUTER_BASE_URL

        }
