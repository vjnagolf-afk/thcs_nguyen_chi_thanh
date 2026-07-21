# -*- coding: utf-8 -*-
"""
exceptions.py - Quản lý các lỗi ngoại lệ riêng của Exam Engine.
"""

class ExamEngineError(Exception):
    """Lỗi chung cao nhất của toàn bộ hệ thống Exam Engine."""
    pass

class ExamContractError(ExamEngineError):
    """Lỗi khi dữ liệu cấu trúc đề (Exam Contract) đầu vào không hợp lệ."""
    pass

class ExamOutputError(ExamEngineError):
    """Lỗi khi kết quả JSON do AI trả về bị sai cấu trúc hoặc thiếu trường."""
    pass

class AIProviderError(ExamEngineError):
    """Lỗi kết nối, tràn token hoặc từ chối dịch vụ từ phía các nhà cung cấp AI."""
    pass
# -*- coding: utf-8 -*-
"""
prompts.py - Bộ khung Prompt chuyên dụng biên soạn đề thi.
"""
import json
from typing import Any, Dict

def build_system_prompt() -> str:
    """Xây dựng prompt hệ thống định hình vai trò chuyên gia nghiêm ngặt."""
    return (
        "Bạn là một chuyên gia khảo thí giáo dục hàng đầu, am hiểu sâu sắc chương trình GDPT 2018.\n"
        "Nhiệm vụ của bạn là biên soạn nội dung kiểm tra cực kỳ chuẩn xác, làm việc như một hệ thống kiểm định đề thi.\n\n"
        "NGUYÊN TẮC TUYỆT ĐỐI:\n"
        "1. EXAM CONTRACT LÀ NGUỒN SỰ THẬT DUY NHẤT. Tuyệt đối không tự ý thêm/bớt câu, thay đổi cấu trúc điểm số hoặc định dạng câu hỏi.\n"
        "2. CÔNG THỨC TOÁN - LÝ - HÓA: Tất cả biểu thức phải dùng ký hiệu LaTeX (Ví dụ: $F = ma$, $\\frac{1}{2}mv^2$, $H_2O$). Không dùng text thuần.\n"
        "3. ĐẦU RA DUY NHẤT: Chỉ trả về một chuỗi JSON Object duy nhất khớp chính xác với cấu trúc yêu cầu. KHÔNG giải thích dông dài, KHÔNG bao bọc Markdown.\n"
        "4. ĐỐI VỚI CÂU TRẮC NGHIỆM NHIỀU LỰA CHỌN (NLC): Bắt buộc có chính xác 4 phương án A, B, C, D. Không được thiếu, đáp án đúng phải thuộc một trong bốn phương án này."
    )

def build_user_prompt(contract: Dict[str, Any], outline_text: str, additional_materials: str = "") -> str:
    """Truyền dữ liệu hợp đồng, đề cương và yêu cầu các trường dữ liệu JSON."""
    contract_json = json.dumps(contract, ensure_ascii=False, indent=2)
    return (
        f"HÃY TẠO ĐỀ KIỂM TRA THEO ĐÚNG CẤU TRÚC JSON DỰA TRÊN CÁC DỮ LIỆU SAU:\n\n"
        f"=== 1. EXAM CONTRACT ===\n{contract_json}\n\n"
        f"=== 2. PHẠM VI KIẾN THỨC ĐƯỢC PHÉP ===\n{outline_text}\n\n"
        f"=== 3. TÀI LIỆU BỔ SUNG ===\n{additional_materials}\n\n"
        f"=== YÊU CẦU ĐẦU RA JSON BẮT BUỘC ===\n"
        f"Cấu trúc JSON tổng thể phải gồm các key sau:\n"
        f"1. knowledge_scope (mô tả phạm vi)\n"
        f"2. questions (mảng chứa thông tin chi tiết từng câu hỏi)\n"
        f"3. matrix (ma trận đề thi)\n"
        f"4. specification (bản đặc tả)\n"
        f"5. answer_key (đáp án ngắn gọn)\n"
        f"6. validation_notes (ghi chú kiểm định nếu thiếu thông tin)\n\n"
        f"Trong mảng 'questions', mỗi câu hỏi bắt buộc chứa đầy đủ các trường: "
        f"question_no, question_type, points, cognitive_level, knowledge_topic, question_text, answer, explanation, figure_required, figure_description.\n"
        f"Nếu câu hỏi là NLC, trường 'options' bắt buộc chứa định dạng dict: {{\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}}.\n"
        f"Nếu câu hỏi tự luận, bắt buộc bổ sung trường 'marking_guide'."
    )
# -*- coding: utf-8 -*-
"""
engine.py - Phần 1: Khởi tạo cấu hình và nạp thư viện hệ thống.
"""
import os
import json
import re
from typing import Any, Dict, Optional
from loguru import logger

# Nhập các cấu phần đã tách từ các file trước
from exceptions import ExamEngineError, ExamContractError, ExamOutputError, AIProviderError
import prompts

class ExamAIEngine:
    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        primary_model: str = "claude-3-5-sonnet-20241022", 
        fallback_openai_model: str = "gpt-4o",
        fallback_gemini_model: str = "gemini-2.5-pro",
        fallback_openrouter_model: str = "anthropic/claude-3.5-sonnet"
    ):
        # Thiết lập API Key (Ưu tiên tham số truyền vào, sau đó đến biến môi trường)
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")

        # Thiết lập danh sách mô hình chạy chính và chạy dự phòng
        self.primary_model = primary_model
        self.fallback_openai = fallback_openai_model
        self.fallback_gemini = fallback_gemini_model
        self.fallback_openrouter = fallback_openrouter_model

        # Biến trạng thái lưu vết mô hình phản hồi thành công gần nhất
        self.last_provider = None
        self.last_model = None
    # === (Tiếp tục lớp ExamAIEngine) ===

    @staticmethod
    def _clean_json_text(text: str) -> str:
        """Lọc bỏ ký tự rác hoặc khối markdown bao bọc để lấy chuỗi JSON gốc."""
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start:end + 1]
        return text.strip()

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        """Chuyển đổi chuỗi văn bản sạch thành cấu trúc Dictionary trong Python."""
        cleaned = ExamAIEngine._clean_json_text(text)
        if not cleaned:
            raise ExamOutputError("AI trả về nội dung trống hoặc không chứa cấu trúc JSON.")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON không hợp lệ: {e}")
            raise ExamOutputError(f"AI trả về JSON không hợp lệ: {e}")

    @staticmethod
    def validate_exam_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
        """Thẩm định cấu trúc file Hợp đồng đề thi gốc trước khi gửi lệnh cho AI."""
        if not isinstance(contract, dict):
            raise ExamContractError("Exam Contract phải là một dictionary.")
        
        required_keys = ["subject", "grade", "duration", "total_score", "question_blueprint"]
        for key in required_keys:
            if key not in contract:
                raise ExamContractError(f"Exam Contract thiếu trường bắt buộc: {key}")
        
        total_score = float(contract.get("total_score", 0))
        if abs(total_score - 10.0) > 0.01:
            raise ExamContractError(f"Tổng điểm thiết lập phải bằng 10.0. Hiện tại: {total_score}")
        
        blueprint = contract.get("question_blueprint", [])
        if not blueprint:
            raise ExamContractError("Exam Contract chưa định nghĩa danh sách câu hỏi.")
        
        question_numbers = []
        for item in blueprint:
            for field in ["question_no", "question_type", "points"]:
                if field not in item:
                    raise ExamContractError(f"Cấu trúc blueprint thiếu trường: {field}")
            question_numbers.append(int(item["question_no"]))
            if float(item["points"]) < 0:
                raise ExamContractError(f"Câu hỏi số {item['question_no']} có số điểm âm.")
        
        if sorted(question_numbers) != list(range(1, len(question_numbers) + 1)):
            raise ExamContractError("Số thứ tự câu hỏi không liên tục bắt đầu từ Câu 1.")
            
        return contract
    # === (Tiếp tục lớp ExamAIEngine) ===

    def _call_anthropic(self, sys_p: str, usr_p: str) -> str:
        """Cổng kết nối chính: Anthropic Claude API."""
        if not self.anthropic_api_key: 
            raise AIProviderError("Thiếu ANTHROPIC_API_KEY.")
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_api_key, timeout=180)
            response = client.messages.create(
                model=self.primary_model, max_tokens=8192, temperature=0.2,
                system=sys_p, messages=[{"role": "user", "content": usr_p}]
            )
            self.last_provider, self.last_model = "anthropic", self.primary_model
            return response.content.text
        except Exception as e: 
            raise AIProviderError(f"Anthropic lỗi: {e}")

    def _call_openai(self, sys_p: str, usr_p: str) -> str:
        """Cổng kết nối dự phòng 1: OpenAI GPT API."""
        if not self.openai_api_key: 
            raise AIProviderError("Thiếu OPENAI_API_KEY.")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.fallback_openai, temperature=0.2, response_format={"type": "json_object"},
                messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": usr_p}]
            )
            self.last_provider, self.last_model = "openai", self.fallback_openai
            return response.choices.message.content
        except Exception as e: 
            raise AIProviderError(f"OpenAI lỗi: {e}")

    def _call_gemini(self, sys_p: str, usr_p: str) -> str:
        """Cổng kết nối dự phòng 2: Google GenAI API."""
        if not self.gemini_api_key: 
            raise AIProviderError("Thiếu GEMINI_API_KEY.")
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=self.gemini_api_key)
            response = client.models.generate_content(
                model=self.fallback_gemini, contents=usr_p,
                config=types.GenerateContentConfig(system_instruction=sys_p, temperature=0.2, response_mime_type="application/json")
            )
            self.last_provider, self.last_model = "gemini", self.fallback_gemini
            return response.text
        except Exception as e: 
            raise AIProviderError(f"Gemini lỗi: {e}")

    def _call_openrouter(self, sys_p: str, usr_p: str) -> str:
        """Cổng kết nối dự phòng 3: Cổng định tuyến OpenRouter HTTP."""
        if not self.openrouter_api_key: 
            raise AIProviderError("Thiếu OPENROUTER_API_KEY.")
        try:
            import requests
            response = requests.post(
                "https://openrouter.ai",
                headers={"Authorization": f"Bearer {self.openrouter_api_key}", "Content-Type": "application/json"},
                json={"model": self.fallback_openrouter, "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": usr_p}], "temperature": 0.2, "response_format": {"type": "json_object"}},
                timeout=240
            )
            if response.status_code != 200: 
                raise AIProviderError(f"HTTP Lỗi mã trạng thái: {response.status_code}")
            self.last_provider, self.last_model = "openrouter", self.fallback_openrouter
            return response.json()["choices"]["message"]["content"]
        except Exception as e: 
            raise AIProviderError(f"OpenRouter lỗi: {e}")
    # === (Tiếp tục và kết thúc lớp ExamAIEngine) ===

    @staticmethod
    def validate_exam_result(result: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
        """Chương trình hậu kiểm tự động bằng thuật toán Python (Đảm bảo cấu trúc điểm, số câu)."""
        if not isinstance(result, dict):
            raise ExamOutputError("Đầu ra từ AI không tạo được thực thể JSON Object.")
        
        questions = result.get("questions", [])
        blueprint = contract["question_blueprint"]
        
        if len(questions) != len(blueprint):
            raise ExamOutputError(f"Số lượng câu hỏi AI tạo ({len(questions)}) lệch so với Hợp đồng ({len(blueprint)}).")
        
        blueprint_map = {int(item["question_no"]): item for item in blueprint}
        seen_questions = set()
        total_points = 0.0
        
        for q in questions:
            q_no = int(q.get("question_no", 0))
            if q_no in seen_questions:
                raise ExamOutputError(f"Phát hiện trùng lặp Số câu {q_no} trong kết quả của AI.")
            seen_questions.add(q_no)
            
            if q_no not in blueprint_map:
                raise ExamOutputError(f"Câu hỏi số {q_no} AI tự ý sinh thêm ngoài danh mục.")
                
            expected = blueprint_map[q_no]
            if str(expected["question_type"]).upper() != str(q.get("question_type", "")).upper():
                raise ExamOutputError(f"Câu {q_no}: Sai loại dạng câu hỏi.")
                
            actual_points = float(q.get("points", 0))
            if abs(float(expected["points"]) - actual_points) > 0.01:
                raise ExamOutputError(f"Câu {q_no}: Sai điểm số cấp phát.")
                
            if str(expected["question_type"]).upper() in ["NLC", "MULTIPLE_CHOICE"]:
                options = q.get("options")
                if not isinstance(options, dict) or not all(k in options for k in ["A", "B", "C", "D"]):
                    raise ExamOutputError(f"Câu {q_no}: Thiếu hoặc lệch cấu trúc phương án A-B-C-D.")
                if str(q.get("answer", "")).strip().upper() not in ["A", "B", "C", "D"]:
                    raise ExamOutputError(f"Câu {q_no}: Đáp án trắc nghiệm không hợp lệ.")
            
            total_points += actual_points
            
        if abs(total_points - float(contract["total_score"])) > 0.01:
            raise ExamOutputError(f"Tổng điểm các câu ({total_points}) không khớp với tổng điểm bài thi ({contract['total_score']}).")
            
        return result

    def generate_exam(self, exam_contract: Dict[str, Any], outline_text: str, additional_materials: str = "") -> Dict[str, Any]:
        """Hàm điều phối lõi của hệ thống, tự động kích hoạt vòng lặp dự phòng dự toán chuyển dòng."""
        logger.info("🛠️ Đang kiểm tra tính hợp lệ của Exam Contract...")
        clean_contract = self.validate_exam_contract(exam_contract)
        
        system_prompt = prompts.build_system_prompt()
        user_prompt = prompts.build_user_prompt(clean_contract, outline_text, additional_materials)
        
        # Danh sách định tuyến mô hình xếp theo thứ tự ưu tiên giảm dần
        providers = [
            ("Anthropic (Claude)", self._call_anthropic),
            ("OpenAI (GPT)", self._call_openai),
            ("Google (Gemini)", self._call_gemini),
            ("OpenRouter Cổng dự phòng", self._call_openrouter)
        ]
        
        raw_response = None
        for name, provider_func in providers:
            try:
                logger.info(f"🚀 Gửi yêu cầu qua kênh: {name}...")
                raw_response = provider_func(system_prompt, user_prompt)
                if raw_response: 
                    break  # Đã nhận được chuỗi phản hồi, thoát khỏi vòng lặp Fallback
            except AIProviderError as err:
                logger.warning(f"⚠ Kênh {name} xảy ra lỗi: {err}. Tự động chuyển mô hình...")
                continue
                
        if not raw_response:
            raise ExamEngineError("❌ Toàn bộ các nhà cung cấp AI chính và dự phòng đều thất bại.")
            
        logger.info(f"💾 Nhận phản hồi thành công từ [{self.last_provider.upper()}]. Đang phân tích cú pháp JSON...")
        parsed_json = self._parse_json(raw_response)
        
        logger.info("🧪 Tiến hành chạy chương trình hậu kiểm thuật toán Python...")
        return self.validate_exam_result(parsed_json, clean_contract)
