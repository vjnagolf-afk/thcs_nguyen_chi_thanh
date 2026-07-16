from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class AIEngine:
    def __init__(self, api_key):
        """Khởi tạo kết nối với Google Gemini bằng API Key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # 1. Kiểm tra API Key thực sự được truyền vào
        logger.info(f"API Key: {self.api_key[:10]}...") 
        logger.info("AI Engine initialized.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_text(self, prompt, model_name="gemini-1.5-flash"):
        """Xử lý văn bản thuần túy"""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            # 3. Hiển thị lỗi gốc (403, 404, 429...)
            logger.exception("Gemini Error (Text)")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_with_image(self, prompt, image, model_name="gemini-1.5-pro"):
        """Xử lý đa phương thức (Hình ảnh + Văn bản)"""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text
        except Exception:
            # 3. Hiển thị lỗi gốc (403, 404, 429...)
            logger.exception("Gemini Error (Image)")
            raise
