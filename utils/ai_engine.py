from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class AIEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Danh sách ưu tiên model (Sắp xếp từ hiện đại nhất đến dự phòng)
        self.model_priority = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest"
        ]
        logger.info("AI Engine initialized with priority list.")

    def get_model(self, index=0):
        """Lấy tên model theo thứ tự ưu tiên"""
        if index < len(self.model_priority):
            return self.model_priority[index]
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_text(self, prompt, attempt=0):
        """
        Cơ chế tự chọn model: 
        Thử từ model ưu tiên nhất -> Nếu lỗi quota/không khả dụng -> Thử model dự phòng.
        """
        model_name = self.get_model(attempt)
        if not model_name:
            raise Exception("Tất cả các model dự phòng đều không khả dụng.")

        try:
            model = genai.GenerativeModel(model_name)
            return model.generate_content(prompt).text
        except Exception as e:
            # Nếu gặp lỗi (đặc biệt là 429 - Quota), thử sang model dự phòng ở lượt tiếp theo
            logger.warning(f"Model {model_name} thất bại, đang chuyển sang dự phòng...")
            return self.generate_text(prompt, attempt=attempt + 1)

    # Tương tự cho generate_with_image với danh sách ưu tiên riêng
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5), reraise=True)
    def generate_with_image(self, prompt, image, attempt=0):
        # Ưu tiên các model hỗ trợ hình ảnh/suy luận cao
        image_priority = ["gemini-2.5-pro", "gemini-3.1-pro-preview"]
        model_name = image_priority[attempt] if attempt < len(image_priority) else None
        
        if not model_name:
            raise Exception("Các model hình ảnh dự phòng đều không khả dụng.")
            
        try:
            model = genai.GenerativeModel(model_name)
            return model.generate_content([prompt, image]).text
        except Exception:
            return self.generate_with_image(prompt, image, attempt=attempt + 1)
