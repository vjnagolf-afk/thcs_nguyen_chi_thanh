from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class AIEngine:
    def __init__(self, api_key):
        """Khởi tạo kết nối với Google Gemini bằng API Key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        logger.info("AI Engine initialized successfully.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
    def generate_text(self, prompt, model_name="gemini-1.5-flash"):
        """Xử lý văn bản thuần túy"""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Chuyển về bản dự phòng nếu model bị sai tên
            if "NotFound" in str(e) or "models/" in str(e):
                logger.warning(f"Không tìm thấy {model_name}, lùi về gemini-pro...")
                try:
                    backup_model = genai.GenerativeModel('gemini-pro')
                    return backup_model.generate_content(prompt).text
                except Exception as e_backup:
                    logger.exception("Lỗi khi gọi model dự phòng (gemini-pro):")
                    raise  # Giữ nguyên traceback của e_backup

            # In đầy đủ traceback và lỗi gốc ra log, sau đó re-raise
            logger.exception(f"Lỗi gốc từ Google API ({model_name}):")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
    def generate_with_image(self, prompt, image, model_name="gemini-1.5-pro"):
        """Xử lý đa phương thức (Hình ảnh + Văn bản)"""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            if "NotFound" in str(e) or "models/" in str(e):
                logger.warning(f"Không tìm thấy {model_name}, lùi về gemini-pro-vision...")
                try:
                    backup_model = genai.GenerativeModel('gemini-pro-vision')
                    return backup_model.generate_content([prompt, image]).text
                except Exception as e_backup:
                    logger.exception("Lỗi khi gọi model dự phòng (gemini-pro-vision):")
                    raise 

            logger.exception(f"Lỗi gốc từ Google API ({model_name}):")
            raise
