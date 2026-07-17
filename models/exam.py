# =====================================================================
# FILE: models/exam.py (ĐỐI TƯỢNG QUẢN LÝ DỮ LIỆU ĐỀ KIỂM TRA CHUẨN)
# =====================================================================

class Exam:
    def __init__(self, exam_type, custom_req, tn_total, c1, c2, c3, c4, tl_scores, ai_generated_content):
        """
        Khởi tạo đối tượng lưu trữ toàn bộ thông số cấu trúc của một đề thi
        """
        self.exam_type = exam_type          # Hình thức đề (TNKQ, Tự luận, Hỗn hợp)
        self.custom_req = custom_req        # Yêu cầu đặc biệt/Chủ đề kiến thức thực tế
        self.tn_total = int(tn_total or 0)  # Tổng số câu trắc nghiệm khách quan
        
        # Số lượng câu hỏi thành phần từng dạng
        self.c1 = int(c1 or 0)              # Nhiều lựa chọn
        self.c2 = int(c2 or 0)              # Đúng / Sai
        self.c3 = int(c3 or 0)              # Điền khuyết
        self.c4 = int(c4 or 0)              # Trả lời ngắn
        
        # Mảng điểm số chi tiết phần tự luận
        self.tl_scores = tl_scores if isinstance(tl_scores, list) else []
        self.tl_total = len(self.tl_scores) # Tổng số câu tự luận
        
        # Chuỗi văn bản thô chứa toàn bộ câu hỏi và hướng dẫn chấm từ AI Gemini
        self.ai_generated_content = ai_generated_content

    def to_dict(self):
        """
        Chuyển đổi đối tượng sang định dạng Dictionary phục vụ việc lưu cache Session State
        """
        return {
            "type": self.exam_type,
            "custom_req": self.custom_req,
            "tn_total": self.tn_total,
            "c1": self.c1,
            "c2": self.c2,
            "c3": self.c3,
            "c4": self.c4,
            "tl_scores": self.tl_scores,
            "ai_generated_content": self.ai_generated_content
        }

    @classmethod
    def from_dict(cls, data_dict):
        """
        Khởi tạo đối tượng Exam từ một Dictionary có sẵn trong bộ nhớ đệm
        """
        if not data_dict:
            return None
        return cls(
            exam_type=data_dict.get("type", "Trắc nghiệm kết hợp tự luận"),
            custom_req=data_dict.get("custom_req", ""),
            tn_total=data_dict.get("tn_total", 0),
            c1=data_dict.get("c1", 0),
            c2=data_dict.get("c2", 0),
            c3=data_dict.get("c3", 0),
            c4=data_dict.get("c4", 0),
            tl_scores=data_dict.get("tl_scores", []),
            ai_generated_content=data_dict.get("ai_generated_content", "")
        )
