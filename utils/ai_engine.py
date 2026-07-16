from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class AIEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        logger.info(f"AI Engine initialized with key: {self.api_key[:10]}...")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_text(self, prompt, model_name="gemini-3.5-flash"):
        """Sử dụng Gemini 3.5 Flash cho các tác vụ văn bản"""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            logger.exception(f"Lỗi khi gọi {model_name}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_with_image(self, prompt, image, model_name="gemini-3.1-pro-preview"):
        """Sử dụng Gemini 3.1 Pro cho các tác vụ đa phương thức"""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text
        except Exception:
            logger.exception(f"Lỗi khi gọi {model_name} với hình ảnh")
            raise
