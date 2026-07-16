from docx.oxml import OxmlElement
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

class XmlHelpers:
    @staticmethod
    def set_font_safely(run, font_name: str = "Times New Roman"):
        """Sửa điểm 1: Tìm và cập nhật rFonts hiện có, tránh tạo trùng lặp thẻ XML"""
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
    def apply_paragraph_shading(paragraph, color_hex: str = "F4F4F4"):
        """Sửa điểm 7: Đổ màu nền xám (Shading) nguyên khối cho cả Paragraph Code Block"""
        pPr = paragraph._element.get_or_add_pPr()
        shd = pPr.find(qn("w:shd"))
        if shd is None:
            shd = OxmlElement("w:shd")
            pPr.append(shd)
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), color_hex)

    @staticmethod
    def apply_bottom_border(paragraph, color_hex: str = "B4B4B4", size: int = 12):
        """Sửa điểm 6: Tạo đường kẻ ngang (HR) native bằng Paragraph Bottom Border cực đẹp"""
        pPr = paragraph._element.get_or_add_pPr()
        pBdr = pPr.find(qn("w:pBdr"))
        if pBdr is None:
            pBdr = OxmlElement("w:pBdr")
            pPr.append(pBdr)
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), str(size))  # 12 = 1.5 pt
        bottom.set(qn("w:space"), "4")
        bottom.set(qn("w:color"), color_hex)
        pBdr.append(bottom)
from docx.shared import Pt, Inches, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH

class BaseStyleSetup:
    @staticmethod
    def setup_base_styles(doc):
        # 1. Định dạng trang A4 & Margins
        for section in doc.sections:
            section.page_height = Inches(11.69)
            section.page_width = Inches(8.27)
            section.top_margin = Inches(0.79)
            section.bottom_margin = Inches(0.79)
            section.left_margin = Inches(1.18)
            section.right_margin = Inches(0.79)

        # Helper cấu hình thuộc tính font của một Style hệ thống
        def configure_style(style_obj, font_size, bold=False, italic=False, color=(0,0,0), space_after=6, space_before=0):
            style_obj.font.name = 'Times New Roman'
            style_obj.font.size = Pt(font_size)
            style_obj.font.bold = bold
            style_obj.font.italic = italic
            style_obj.font.color.rgb = RGBColor(*color)
            style_obj.paragraph_format.space_after = Pt(space_after)
            style_obj.paragraph_format.space_before = Pt(space_before)

        # 2. Cập nhật các Style Hệ thống chuẩn (Sửa điểm 3)
        configure_style(doc.styles['Normal'], 13, space_after=6)
        configure_style(doc.styles['Heading 1'], 16, bold=True, space_before=12, space_after=6)
        configure_style(doc.styles['Heading 2'], 14, bold=True, space_before=8, space_after=4)
        configure_style(doc.styles['Heading 3'], 13, bold=True, italic=True, space_before=6, space_after=2)
        configure_style(doc.styles['List Bullet'], 13, space_after=3)
        configure_style(doc.styles['List Number'], 13, space_after=3)
        
        # Thiết lập chống mồ côi dòng cho toàn bộ Heading
        doc.styles['Heading 1'].paragraph_format.keep_with_next = True
        doc.styles['Heading 2'].paragraph_format.keep_with_next = True
        doc.styles['Heading 3'].paragraph_format.keep_with_next = True
from typing import List, Dict, Any
from docx.shared import RGBColor
from styles.xml_helpers import XmlHelpers

class TextRenderer:
    @classmethod
    def render_inline_tokens(cls, paragraph, tokens: List[Dict[str, Any]], math_renderer: Any):
        """Sửa điểm 8: Hỗ trợ link, highlight, subscript, superscript, bold, italic,..."""
        if not tokens:
            return

        for token in tokens:
            t_type = token.get("type")
            
            if t_type in ["text", "bold", "italic", "underline", "strike", "subscript", "superscript", "highlight"]:
                content = token.get("content") or token.get("text", "")
                run = paragraph.add_run(content)
                XmlHelpers.set_font_safely(run, "Times New Roman")
                
                # Áp thuộc tính định dạng trực tiếp
                if t_type == "bold": run.bold = True
                elif t_type == "italic": run.italic = True
                elif t_type == "underline": run.underline = True
                elif t_type == "strike": run.font.strike = True
                elif t_type == "subscript": run.font.subscript = True      # Hạ chỉ số (H₂SO₄) không cần gọi Math
                elif t_type == "superscript": run.font.superscript = True  # Nâng số mũ (x²) không cần gọi Math
                elif t_type == "highlight": run.font.highlight_color = 4   # Màu vàng mặc định

            elif t_type == "inline_math":
                if math_renderer:
                    math_renderer.render_inline_math(paragraph, token.get("content", ""))
                else:
                    run = paragraph.add_run(f" {token.get('content')} ")
                    run.font.italic = True
                    XmlHelpers.set_font_safely(run, "Times New Roman")
# --- heading_renderer.py ---
from docx.enum.text import WD_ALIGN_PARAGRAPH
from renderers.text_renderer import TextRenderer
from styles.xml_helpers import XmlHelpers

class HeadingRenderer:
    @classmethod
    def render(cls, doc, node: dict, math_renderer: Any):
        level = min(max(node.get("level", 1), 1), 3) # Giới hạn từ Heading 1 -> Heading 3
        p = doc.add_paragraph(style=f'Heading {level}')
        
        # Nếu là tiêu đề chương mục lớn cấp 1, tự động căn giữa theo Mã 1 của trường
        if level == 1:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        TextRenderer.render_inline_tokens(p, node.get("tokens", []), math_renderer)
        
        # Sửa điểm 4: Áp dụng helper đồng bộ cho toàn bộ runs tạo ra, tránh viết lặp
        for run in p.runs:
            XmlHelpers.set_font_safely(run, "Times New Roman")


# --- list_renderer.py ---
from docx.shared import Inches
from renderers.text_renderer import TextRenderer

class ListRenderer:
    @classmethod
    def render(cls, doc, node: dict, math_renderer: Any):
        style_name = 'List Number' if node.get("style") == "number" else 'List Bullet'
        p = doc.add_paragraph(style=style_name)
        
        # Sửa điểm 5: Cấu hình thụt lề treo (Hanging Indent) chuẩn chỉnh cho dòng văn bản dài
        level = node.get("level", 1)
        base_left = 0.25 * level
        
        p.paragraph_format.left_indent = Inches(base_left + 0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)  # Thụt dòng đầu ra phía trước dấu bullet
        
        TextRenderer.render_inline_tokens(p, node.get("tokens", []), math_renderer)
# --- code_renderer.py ---
from docx.shared import Pt, Inches, RGBColor
from styles.xml_helpers import XmlHelpers

class CodeRenderer:
    @classmethod
    def render(cls, doc, node: dict):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        
        # Sửa điểm 7: Đổ phủ nền xám toàn khối đoạn mã
        XmlHelpers.apply_paragraph_shading(p, "F5F5F5")
        
        run = p.add_run(node.get("text", ""))
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(40, 40, 40)
        XmlHelpers.set_font_safely(run, "Courier New")


# --- table_renderer.py --- (Sửa điểm 9)
from renderers.text_renderer import TextRenderer

class TableRenderer:
    @classmethod
    def render(cls, doc, node: dict, math_renderer: Any):
        headers = node.get("headers", [])
        rows = node.get("rows", [])
        if not headers and not rows:
            return
            
        # Khởi tạo bảng hệ thống với Style lưới chuẩn Word
        table = doc.add_table(rows=0, cols=node.get("cols", 1))
        table.style = 'Table Grid'
        
        # Render hàng đầu (Header)
        if headers:
            hdr_cells = table.add_row().cells
            for idx, cell_node in enumerate(headers):
                p = hdr_cells[idx].paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                TextRenderer.render_inline_tokens(p, cell_node.get("content", []), math_renderer)
                for run in p.runs: run.bold = True
                
        # Render các hàng dữ liệu nội dung (Rows)
        for row_data in rows:
            row_cells = table.add_row().cells
            for idx, cell_node in enumerate(row_data):
                p = row_cells[idx].paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                TextRenderer.render_inline_tokens(p, cell_node.get("content", []), math_renderer)


# --- image_renderer.py --- (Sửa điểm 10)
from docx.shared import Inches
import io
import requests

class ImageRenderer:
    @classmethod
    def render(cls, doc, node: dict):
        """Tự động tải ảnh từ URL do AI đề xuất và ép kích thước an toàn vừa trang giáo án"""
        url = node.get("url", "")
        alt = node.get("alt", "image")
        if not url:
            return
        try:
            p = doc.add_paragraph()
            p.alignment = 1  # Căn giữa ảnh
            
            # Nếu là đường dẫn URL, thực hiện tải luồng bytes về bộ nhớ tạm
            if url.startswith("http"):
                response = requests.get(url, timeout=5)
                image_stream = io.BytesIO(response.content)
                p.add_run().add_picture(image_stream, width=Inches(5.0))
            else:
                # Nếu là đường dẫn file cục bộ trong hệ thống trường
                p.add_run().add_picture(url, width=Inches(5.0))
        except Exception as e:
            p.add_run(f"[Không hiển thị được hình ảnh: {alt} - Đường dẫn: {url}]")
from styles.base_styles import BaseStyleSetup
from styles.xml_helpers import XmlHelpers

from renderers.text_renderer import TextRenderer
from renderers.heading_renderer import HeadingRenderer
from renderers.list_renderer import ListRenderer
from renderers.code_renderer import CodeRenderer
from renderers.table_renderer import TableRenderer
from renderers.image_renderer import ImageRenderer

class StyleManager:
    @staticmethod
    def setup_base_styles(doc):
        """Kế thừa thiết lập cấu hình trang từ BaseStyleSetup"""
        BaseStyleSetup.setup_base_styles(doc)

    @classmethod
    def render_ast_to_word(cls, doc, ast_nodes: list, math_renderer: Any):
        """Nhạc trưởng điều phối duyệt cây AST của Tokenizer và phân phối về đúng Module chuyên trách"""
        for node in ast_nodes:
            n_type = node.get("type")
            
            if n_type == "paragraph":
                p = doc.add_paragraph()
                TextRenderer.render_inline_tokens(p, node.get("tokens", []), math_renderer)
                
            elif n_type == "heading":
                HeadingRenderer.render(doc, node, math_renderer)
                
            elif n_type == "list_item":
                ListRenderer.render(doc, node, math_renderer)
                
            elif n_type == "code":
                CodeRenderer.render(doc, node)
                
            elif n_type == "table":
                TableRenderer.render(doc, node, math_renderer)
                
            elif n_type == "image":
                ImageRenderer.render(doc, node)
                
            elif n_type == "hr":
                # Sửa điểm 6: Tạo một paragraph trống và áp viền dưới native cực tinh tế
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(12)
                XmlHelpers.apply_bottom_border(p, color_hex="CCCCCC", size=8)
                
            elif n_type == "display_math":
                # Kích hoạt bộ chuyển đổi XML OMML chuẩn nếu gặp khối phương trình độc lập
                if math_renderer:
                    math_renderer.render_display_math(doc, node.get("content", ""))
