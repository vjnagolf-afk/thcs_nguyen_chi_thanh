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
    def generate_text(self, prompt, model_name="gemini-1.5-flash-latest"):
        """Xử lý văn bản thuần túy. Hỗ trợ truyền tên model động từ UI, mặc định là Flash."""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Lỗi khi gọi API {model_name} (Text): {str(e)}")
            # Cơ chế dự phòng: Nếu Google đổi tên model, tự động lùi về bản ổn định
            if "NotFound" in str(e):
                logger.warning(f"Không tìm thấy {model_name}. Tự động chuyển sang model dự phòng (gemini-pro)...")
                try:
                    backup_model = genai.GenerativeModel('gemini-pro')
                    response = backup_model.generate_content(prompt)
                    return response.text
                except Exception as backup_error:
                    logger.error(f"Lỗi khi gọi model dự phòng: {str(backup_error)}")
                    raise backup_error
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_with_image(self, prompt, image, model_name="gemini-1.5-pro-latest"):
        """Xử lý đa phương thức (Hình ảnh + Văn bản). Mặc định là Pro vì cần suy luận ảnh."""
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            logger.error(f"Lỗi khi gọi API {model_name} (Image): {str(e)}")
            if "NotFound" in str(e):
                logger.warning(f"Không tìm thấy {model_name}. Tự động chuyển sang bản dự phòng...")
                try:
                    backup_model = genai.GenerativeModel('gemini-pro-vision')
                    response = backup_model.generate_content([prompt, image])
                    return response.text
                except Exception as backup_error:
                    raise backup_error
            raise e
