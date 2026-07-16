from loguru import logger
import google.generativeai as genai


class AIEngine:
    """
    AI Engine trung tâm
    -------------------
    - Quản lý kết nối Gemini
    - Quản lý model
    - Tự động fallback khi model lỗi
    """

    # ==========================
    # Cấu hình Model
    # ==========================

    DEFAULT_MODEL = "gemini-3.5-flash"

    FALLBACK_MODEL = "gemini-2.0-flash"

    # Các model được phép sử dụng
    MODELS = {
        "flash": "gemini-3.5-flash",
        "pro": "gemini-2.5-pro",
    }

    # ==========================

    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)

    # ====================================================

    def _call(self, model_name, prompt):
        """
        Hàm gọi Gemini.
        Không nên gọi trực tiếp từ module khác.
        """

        model = genai.GenerativeModel(model_name)

        response = model.generate_content(prompt)

        if hasattr(response, "text"):
            return response.text

        return str(response)

    # ====================================================

    def generate_text(self, prompt, model_name=None):
        """
        Sinh văn bản.

        Parameters
        ----------
        prompt : str

        model_name : str | None

        Nếu None -> dùng DEFAULT_MODEL
        """

        if not model_name:
            model_name = self.DEFAULT_MODEL

        try:

            logger.info(f"Đang sử dụng model: {model_name}")

            return self._call(model_name, prompt)

        except Exception as e:

            logger.warning(
                f"Model {model_name} lỗi: {e}"
            )

            # Nếu model đang dùng KHÔNG phải fallback
            # thì chuyển sang fallback.

            if model_name != self.FALLBACK_MODEL:

                try:

                    logger.info(
                        f"Chuyển sang model dự phòng: {self.FALLBACK_MODEL}"
                    )

                    return self._call(
                        self.FALLBACK_MODEL,
                        prompt
                    )

                except Exception as e2:

                    logger.error(
                        f"Fallback thất bại: {e2}"
                    )

            raise Exception(
                "Hệ thống AI hiện không phản hồi. Vui lòng thử lại sau."
            )

    # ====================================================

    def generate_with_image(
        self,
        prompt,
        image,
        model_name=None
    ):
        """
        Sinh nội dung từ ảnh.
        """

        if not model_name:
            model_name = self.DEFAULT_MODEL

        try:

            model = genai.GenerativeModel(model_name)

            response = model.generate_content(
                [prompt, image]
            )

            return response.text

        except Exception as e:

            logger.exception(e)

            raise Exception(
                "Không thể xử lý hình ảnh."
            )
