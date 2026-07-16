import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class StyleManager:
    @staticmethod
    def setup_base_styles(doc):
        for section in doc.sections:
            section.page_height = Inches(11.69)
            section.page_width = Inches(8.27)
            section.top_margin = Inches(0.79)
            section.bottom_margin = Inches(0.79)
            section.left_margin = Inches(1.18)
            section.right_margin = Inches(0.79)
        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(13)

    @staticmethod
    def render_heading(doc, node, MathRenderer):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER  # CĂN GIỮA TIÊU ĐỀ
        text = "".join([t['content'] for t in node['tokens']])
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(16)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
