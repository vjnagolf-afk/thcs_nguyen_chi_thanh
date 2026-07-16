from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class AIEngine:
    def __init__(self, api_key):
        """Khởi tạo kết nối với Google Gemini bằng API Key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        logger.info("AI Engine initialized successfully.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_text(self, prompt, model_name="gemini-1.5-flash"):
        """Xử lý văn bản thuần túy. Sử dụng tên bản ổn định, không dùng -latest"""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Lỗi khi gọi API {model_name}: {str(e)}")
            # Xử lý an toàn: Nếu tên model không tồn tại, lùi về bản cũ nhất
            if "NotFound" in str(e) or "models/" in str(e):
                logger.warning(f"Không tìm thấy {model_name}, lùi về gemini-pro...")
                try:
                    backup_model = genai.GenerativeModel('gemini-pro')
                    return backup_model.generate_content(prompt).text
                except Exception as e_backup:
                    raise Exception(f"Lỗi cả bản chính và dự phòng: {str(e_backup)}")
            raise Exception(f"Lỗi từ Google: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_with_image(self, prompt, image, model_name="gemini-1.5-pro"):
        """Xử lý đa phương thức (Hình ảnh + Văn bản)"""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            logger.error(f"Lỗi gọi API {model_name} (Image): {str(e)}")
            if "NotFound" in str(e):
                logger.warning("Đang lùi về bản dự phòng gemini-pro-vision...")
                try:
                    backup_model = genai.GenerativeModel('gemini-pro-vision')
                    return backup_model.generate_content([prompt, image]).text
                except Exception as e_backup:
                    raise Exception(f"Lỗi ảnh dự phòng: {str(e_backup)}")
            raise Exception(f"Lỗi từ Google (Ảnh): {str(e)}")
