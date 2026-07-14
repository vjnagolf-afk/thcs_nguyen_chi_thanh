from loguru import logger
import streamlit as st
from google.generativeai import GenerativeModel, configure
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class AIEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        configure(api_key=api_key)
        logger.info("AI Engine initialized.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def ask(self, prompt, model_name="gemini-1.5-flash"):
        try:
            model = GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error calling {model_name}: {str(e)}")
            # Logic dự phòng tự động chuyển model sẽ được tích hợp sâu hơn ở đây
            raise e
