from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class AIEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        logger.info("AI Engine initialized.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_text(self, prompt, model_name="gemini-1.5-flash"):
        """Sử dụng 1.5 Flash hoặc Pro. Không fallback sang model cũ."""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Lỗi gọi {model_name}: {str(e)}")
            # Không lùi về model cũ, ném lỗi để tenacity thử lại đúng model đó
            raise 

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_with_image(self, prompt, image, model_name="gemini-1.5-pro"):
        """Sử dụng 1.5 Pro (Hỗ trợ tốt nhất cho hình ảnh)"""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            logger.error(f"Lỗi gọi {model_name} với hình ảnh: {str(e)}")
            raise
