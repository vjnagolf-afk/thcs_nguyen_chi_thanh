from loguru import logger
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class AIEngine:
    def __init__(self, api_key):
        """Khởi tạo kết nối với Google Gemini bằng API Key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        logger.info("AI Engine initialized successfully.")
        
        # Cấu hình sẵn 2 bộ não cho các tác vụ khác nhau:
        # 1. Flash: Tốc độ cực nhanh, nhẹ, lý tưởng cho KHBD, RAG, sinh văn bản thông thường
        self.flash_model = 'gemini-1.5-flash'
        
        # 2. Pro: Cực kỳ thông minh, suy luận logic toán học, lý, hóa sắc bén, đọc hiểu đồ thị đỉnh cao
        self.pro_model = 'gemini-1.5-pro'

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_text(self, prompt, use_pro=False):
        """
        Xử lý văn bản thuần túy. 
        Đã đổi tên hàm từ `ask` thành `generate_text` để khớp với hệ sinh thái.
        """
        model_name = self.pro_model if use_pro else self.flash_model
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Lỗi khi gọi API {model_name} (Text): {str(e)}")
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_with_image(self, prompt, image, use_pro=True):
        """
        VŨ KHÍ BÍ MẬT CHO ĐỀ KIỂM TRA: Xử lý đa phương thức (Hình ảnh + Văn bản).
        - Nhận diện đồ thị, mạch điện, biểu đồ, hình học không gian.
        - Mặc định dùng bản Pro (use_pro=True) vì cần khả năng suy luận hình ảnh cao cấp.
        """
        model_name = self.pro_model if use_pro else self.flash_model
        try:
            model = genai.GenerativeModel(model_name)
            # Truyền vào một list chứa cả câu lệnh (prompt) và hình ảnh (đối tượng PIL.Image)
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            logger.error(f"Lỗi khi gọi API {model_name} (Image): {str(e)}")
            raise e
