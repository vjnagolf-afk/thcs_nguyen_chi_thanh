import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class TableRenderer:
    """
    Chịu trách nhiệm render các cấu trúc bảng (Table) phức tạp:
    Ma trận, Đặc tả, và Bảng dữ liệu từ Markdown.
    """

    @staticmethod
    def build_khbd_header(doc, data_cache):
        """Render header cho Kế hoạch bài dạy"""
        doc.add_heading("KẾ HOẠCH BÀI DẠY", level=1)
        # Logic vẽ header KHBD cũ của thầy ở đây

    @staticmethod
    def build_matrix_table(doc, data_cache):
        """Render bảng Ma trận đề kiểm tra"""
        doc.add_heading("MA TRẬN ĐỀ KIỂM TRA", level=2)
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Nội dung"
        hdr_cells[1].text = "Nhận biết"
        hdr_cells[2].text = "Thông hiểu"
        hdr_cells[3].text = "Vận dụng"
        
        # Thêm logic đổ dữ liệu từ data_cache vào đây nếu cần chi tiết
        doc.add_paragraph("Bảng ma trận đang được khởi tạo theo dữ liệu từ AI.")

    @staticmethod
    def build_specification_table(doc, data_cache):
        """Render bảng Đặc tả đề kiểm tra"""
        doc.add_heading("BẢNG ĐẶC TẢ", level=2)
        doc.add_paragraph("Bảng đặc tả đang được khởi tạo...")

    @staticmethod
    def render_ast_table(doc, node, StyleManager, MathRenderer):
        """Render bảng Markdown thông thường (từ Parser)"""
        rows = node.get("rows", [])
        headers = node.get("headers", [])
        cols = node.get("cols", 1)

        table = doc.add_table(rows=len(rows) + 1, cols=cols)
        table.style = 'Table Grid'

        # Điền Header
        for i, header_cell in enumerate(headers):
            if i < cols:
                table.rows[0].cells[i].text = "".join([t['content'] for t in header_cell])

        # Điền Rows
        for r_idx, row in enumerate(rows):
            for c_idx, cell in enumerate(row):
                if c_idx < cols:
                    cell_text = "".join([t['content'] for t in cell])
                    table.rows[r_idx + 1].cells[c_idx].text = cell_text
