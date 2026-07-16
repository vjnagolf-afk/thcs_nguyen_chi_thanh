from loguru import logger
import google.generativeai as genai

class AIEngine:
    # Cấu hình tập trung tại đây
    DEFAULT_MODEL = "gemini-3.5-flash"
    FALLBACK_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)

    def _call(self, model_name, prompt):
        """Lớp thực thi (Engine layer)"""
        model = genai.GenerativeModel(model_name)
        return model.generate_content(prompt).text

    def generate_text(self, prompt):
        """
        Lớp trừu tượng (Interface layer)
        Các module chỉ biết gọi hàm này, không cần quan tâm model nào đang chạy.
        """
        try:
            # Thử lần 1 với model chính
            return self._call(self.DEFAULT_MODEL, prompt)
        except Exception as e:
            logger.warning(f"Lỗi ở {self.DEFAULT_MODEL}, chuyển sang fallback: {str(e)}")
            try:
                # Thử lần 2 với model dự phòng
                return self._call(self.FALLBACK_MODEL, prompt)
            except Exception as e_final:
                logger.error(f"Cả hai model đều thất bại: {str(e_final)}")
                raise Exception("Hệ thống AI tạm thời không phản hồi.")

    def generate_with_image(self, prompt, image):
        """Tương tự cho xử lý ảnh"""
        # Logic tương tự có thể mở rộng cho model hình ảnh
        try:
            model = genai.GenerativeModel(self.DEFAULT_MODEL) # Hoặc model riêng cho ảnh
            return model.generate_content([prompt, image]).text
        except Exception as e:
            logger.exception("Lỗi xử lý ảnh")
            raise
