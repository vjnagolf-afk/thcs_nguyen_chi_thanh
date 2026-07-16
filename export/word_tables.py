class TableRenderer:
    @staticmethod
    def render_ast_table(doc, node, StyleManager, MathRenderer):
        rows = node.get("rows", [])
        if not rows: return
        
        table = doc.add_table(rows=len(rows), cols=len(rows[0]))
        table.style = 'Table Grid'
        
        for r_idx, row in enumerate(rows):
            for c_idx, cell_data in enumerate(row):
                # Xử lý join content tokens
                content = "".join([t['content'] for t in cell_data['content']])
                table.rows[r_idx].cells[c_idx].text = content
