import docx
from docx.shared import Pt, Inches, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

class BaseStyleSetup:
    @staticmethod
    def setup_base_styles(doc: docx.Document):
        """Thiết lập kích thước trang A4 và Margins chuẩn hành chính Giáo dục"""
        for section in doc.sections:
            section.page_height = Inches(11.69)
            section.page_width = Inches(8.27)
            section.top_margin = Inches(0.79)     # 2.0 cm
            section.bottom_margin = Inches(0.79)  # 2.0 cm
            section.left_margin = Inches(1.18)    # 3.0 cm
            section.right_margin = Inches(0.79)   # 2.0 cm

        # Cấu hình phông chữ hệ thống mẫu dùng chung tốc độ cao
        styles_config = {
            'Normal': (13, False, False, 0, 6),
            'Heading 1': (16, True, False, 12, 6),
            'Heading 2': (14, True, False, 8, 4),
            'Heading 3': (13, True, True, 6, 2),
            'List Bullet': (13, False, False, 0, 3),
            'List Number': (13, False, False, 0, 3)
        }

        for name, (size, bold, italic, before, after) in styles_config.items():
            style = doc.styles[name]
            style.font.name = 'Times New Roman'
            style.font.size = Pt(size)
            style.font.bold = bold
            style.font.italic = italic
            style.font.color.rgb = RGBColor(0, 0, 0)
            style.paragraph_format.space_before = Pt(before)
            style.paragraph_format.space_after = Pt(after)
            if 'Heading' in name:
                style.paragraph_format.keep_with_next = True


class XmlHelpers:
    @staticmethod
    def set_font_safely(run, font_name: str = "Times New Roman"):
        """Sửa lỗi trùng lặp thẻ rFonts khi cập nhật đè phần tử XML của Word"""
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:eastAsia'), font_name)
        rFonts.set(qn('w:cs'), font_name)

    @staticmethod
    def apply_paragraph_shading(paragraph, color_hex: str = "F5F5F5"):
        """Đổ màu nền xám nguyên block bao phủ trọn đoạn văn bản"""
        pPr = paragraph._element.get_or_add_pPr()
        shd = pPr.find(qn("w:shd"))
        if shd is None:
            shd = OxmlElement("w:shd")
            pPr.append(shd)
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), color_hex)

    @staticmethod
    def apply_bottom_border(paragraph, color_hex: str = "CCCCCC", size: int = 8):
        """Tạo đường kẻ ngang (HR) native bằng Paragraph Bottom Border"""
        pPr = paragraph._element.get_or_add_pPr()
        pBdr = pPr.find(qn("w:pBdr"))
        if pBdr is None:
            pBdr = OxmlElement("w:pBdr")
            pPr.append(pBdr)
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), str(size))
        bottom.set(qn("w:space"), "4")
        bottom.set(qn("w:color"), color_hex)
        pBdr.append(bottom)
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

class BlockRenderer:
    @classmethod
    def render_heading(cls, doc, node: dict, text_renderer, math_renderer):
        level = min(max(node.get("level", 1), 1), 3)
        p = doc.add_paragraph(style=f'Heading {level}')
        if level == 1:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        text_renderer.render_inline_tokens(p, node.get("tokens", []), math_renderer)
        for run in p.runs:
            XmlHelpers.set_font_safely(run, "Times New Roman")

    @classmethod
    def render_list_item(cls, doc, node: dict, text_renderer, math_renderer):
        style_name = 'List Number' if node.get("style") == "number" else 'List Bullet'
        p = doc.add_paragraph(style=style_name)
        
        # Thụt lề treo (Hanging Indent) chuẩn chỉnh cho danh sách đa cấp của AI
        level = node.get("level", 1)
        base_left = 0.25 * level
        p.paragraph_format.left_indent = Inches(base_left + 0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        
        text_renderer.render_inline_tokens(p, node.get("tokens", []), math_renderer)

    @classmethod
    def render_checkbox(cls, doc, node: dict, text_renderer, math_renderer):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25 * node.get("level", 1))
        
        box_char = "☑ " if node.get("checked", False) else "☐ "
        run_box = p.add_run(box_char)
        XmlHelpers.set_font_safely(run_box, "MS Gothic")  # Font native tối ưu hiển thị ô vuông
        run_box.bold = True
        
        text_renderer.render_inline_tokens(p, node.get("tokens", []), math_renderer)


class ContainerRenderer:
    @classmethod
    def render_code_block(cls, doc, node: dict):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        XmlHelpers.apply_paragraph_shading(p, "F5F5F5")
        
        run = p.add_run(node.get("text", ""))
        run.font.size = Pt(10.5)
        XmlHelpers.set_font_safely(run, "Courier New")

    @classmethod
    def render_callout(cls, doc, node: dict, text_renderer, math_renderer):
        style = node.get("style", "quote")
        bg_color = "FFF5F5" if style == "warning" else ("F0F7FF" if style == "tip" else "F9F9F9")
        border_color = "FF3B30" if style == "warning" else ("007AFF" if style == "tip" else "8E8E93")
        
        # Thiết lập bảng 1 ô bọc khối Callout nâng cao
        table = doc.add_table(rows=1, cols=1)
        table.alignment = docx.enum.table.WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        table.columns.width = Inches(6.3)
        
        cell = table.cell(0, 0)
        tcPr = cell._element.get_or_add_tcPr()
        
        # Đổ màu nền ô hệ thống
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:fill'), bg_color)
        tcPr.append(shd)
        
        # Thiết lập đường viền trái dày dặn, xóa 3 biên còn lại
        borders = OxmlElement('w:tcBorders')
        left_b = OxmlElement('w:left')
        left_b.set(qn('w:val'), 'single')
        left_b.set(qn('w:sz'), '24')  # Độ dày viền ~3pt
        left_b.set(qn('w:color'), border_color)
        borders.append(left_b)
        
        for side in ['top', 'bottom', 'right']:
            b = OxmlElement(f'w:{side}')
            b.set(qn('w:val'), 'none')
            borders.append(b)
        tcPr.append(borders)

        # Ghi nội dung đệ quy tokens vào khối Callout bọc
        p = cell.paragraphs
        for i, child in enumerate(node.get("children", [])):
            if i > 0: 
                p = cell.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            if child.get("type") == "paragraph":
                text_renderer.render_inline_tokens(p, child.get("tokens", []), math_renderer)
