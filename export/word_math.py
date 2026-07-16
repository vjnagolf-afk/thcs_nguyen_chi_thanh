import re
class MathRenderer:
    @staticmethod
    def normalize(text: str) -> str:
        # Xử lý các lỗi LaTeX hay gặp do AI trả về
        text = text.replace(r'\perp', '⊥').replace(r'\circ', '°').replace(r'\ne', '≠')
        return text

    @classmethod
    def render_inline_math(cls, paragraph, latex_str):
        clean = cls.normalize(latex_str.replace('$', ''))
        run = paragraph.add_run(clean)
        run.font.name = 'Times New Roman'
        run.font.italic = True
