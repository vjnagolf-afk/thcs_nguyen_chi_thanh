from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class AIEngine:
    def __init__(self, api_key):
        """Khởi tạo kết nối với Google Gemini bằng API Key cá nhân của giáo viên"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # 1. Kiểm tra API Key thực sự được truyền vào (Debug Log)
        if self.api_key:
            logger.info(f"API Key: {self.api_key[:10]}...") 
        else:
            logger.error("API Key trống!")
            
        logger.info("AI Engine initialized.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_text(self, prompt, model_name="gemini-1.5-flash"):
        """
        Xử lý văn bản thuần túy.
        Sử dụng model chuẩn, không lùi phiên bản (fallback) để tránh lỗi 404.
        """
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            # 3. Hiển thị lỗi gốc (403, 404, 429...) thông qua logger.exception
            logger.exception("Gemini Error (Text)")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_with_image(self, prompt, image, model_name="gemini-1.5-pro"):
        """
        Xử lý đa phương thức (Hình ảnh + Văn bản).
        Sử dụng model chuẩn, không lùi phiên bản.
        """
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text
        except Exception:
            # 3. Hiển thị lỗi gốc (403, 404, 429...) thông qua logger.exception
            logger.exception("Gemini Error (Image)")
            raise
