# =====================================================================
# FILE: models/khbd.py (ĐỐI TƯỢNG QUẢN LÝ DỮ LIỆU KẾ HOẠCH BÀI DẠY)
# =====================================================================

class KHBD:
    def __init__(self, ten_bai_hoc, mon_hoc, lop, so_tiet, yeu_cau, ai_generated_content):
        self.ten_bai_hoc = ten_bai_hoc
        self.mon_hoc = mon_hoc
        self.lop = lop
        self.so_tiet = so_tiet
        self.yeu_cau = yeu_cau
        self.ai_generated_content = ai_generated_content

    def to_dict(self):
        """Chuyển đổi thành Dictionary giống hệt cấu trúc khbd_meta cũ của thầy"""
        return {
            "title": self.ten_bai_hoc,
            "mon": self.mon_hoc,
            "lop": self.lop,
            "so_tiet": self.so_tiet,
            "yeu_cau": self.yeu_cau,
            "ai_generated_content": self.ai_generated_content
        }

    @classmethod
    def from_dict(cls, data):
        if not data: return None
        return cls(
            ten_bai_hoc=data.get("title", ""),
            mon_hoc=data.get("mon", ""),
            lop=data.get("lop", ""),
            so_tiet=data.get("so_tiet", 2),
            yeu_cau=data.get("yeu_cau", ""),
            ai_generated_content=data.get("ai_generated_content", "")
        )
