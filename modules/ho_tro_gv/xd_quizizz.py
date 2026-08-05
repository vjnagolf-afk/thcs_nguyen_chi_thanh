# -*- coding: utf-8 -*-
"""
====================================================
AI Teacher Assistant
Module: Xây dựng Quizizz Online (Cố định thông số Pusher)
File: modules/ho_tro_gv/xd_quizizz.py
====================================================
"""

import streamlit as st
import sqlite3
import os
import time
import urllib.parse as urlparse
from datetime import datetime
import pandas as pd

# Thử import thư viện QR Code
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

# ==================================================
# CỐ ĐỊNH CẤU HÌNH PUSHER (KHÔNG CẦN NHẬP LẠI)
# ==================================================
PUSHER_CONFIG = {
    "app_id": "2183142",
    "key": "0be832d21ee9699e6bc6",
    "secret": "bbeb85de773a4dfbb85f",
    "cluster": "ap1"
}

# ==================================================
# CẤU HÌNH DATABASE
# ==================================================

DB_FOLDER = "data"
DB_FILE = os.path.join(DB_FOLDER, "quizizz.db")

def create_database():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exams
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        subject TEXT,
        grade TEXT,
        topic TEXT,
        created TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        content TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        answer TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student TEXT,
        exam_id INTEGER,
        score REAL,
        submitted TEXT
    )
    """)

    conn.commit()
    conn.close()

# ==================================================
# XỬ LÝ DỮ LIỆU
# ==================================================

def add_exam(title, subject, grade, topic):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO exams (title, subject, grade, topic, created) VALUES (?, ?, ?, ?, ?)",
        (title, subject, grade, topic, str(datetime.now()))
    )
    conn.commit()
    conn.close()

def get_exams():
    conn = sqlite3.connect(DB_FILE)
    data = conn.execute("SELECT * FROM exams ORDER BY id DESC").fetchall()
    conn.close()
    return data

def add_question(exam_id, content, a, b, c, d, answer):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO questions (exam_id, content, option_a, option_b, option_c, option_d, answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (exam_id, content, a, b, c, d, answer)
    )
    conn.commit()
    conn.close()

def get_questions(exam_id):
    conn = sqlite3.connect(DB_FILE)
    data = conn.execute("SELECT * FROM questions WHERE exam_id=?", (exam_id,)).fetchall()
    conn.close()
    return data

def save_result(student, exam_id, score):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO results (student, exam_id, score, submitted) VALUES (?, ?, ?, ?)",
        (student, exam_id, score, str(datetime.now()))
    )
    conn.commit()
    conn.close()

def get_results():
    conn = sqlite3.connect(DB_FILE)
    data = conn.execute("SELECT * FROM results").fetchall()
    conn.close()
    return data

# ==================================================
# GIAO DIỆN HỆ THỐNG
# ==================================================

def render_xd_quizizz(ai_engine_cu=None):
    create_database()
    st.markdown("### ⚡ Trợ lý Tạo Bộ Câu Hỏi & Tổ Chức Quiz Trực Tuyến")
    st.info("💡 **Góc chuyên gia:** Quét QR code kết nối học sinh, trình chiếu link bất kỳ lên tivi, đồng bộ thời gian thực và chấm điểm tự động!")

    tab_tao_de, tab_nhung = st.tabs([
        "🛠️ 1. Soạn thảo Bộ câu hỏi & Import Excel", 
        "🏆 2. Phòng Thi Đấu Real-time & Chấm Điểm"
    ])

    # ========================================================
    # TAB 1: SOẠN THẢO & IMPORT
    # ========================================================
    with tab_tao_de:
        with st.container(border=True):
            st.markdown("#### 🎯 Chọn phương thức nạp dữ liệu (Nguồn AI hoặc Excel)")
            
            nguon_nhap = st.radio(
                "Nguồn dữ liệu đầu vào:",
                [
                    "✍️ Nhập chủ đề trực tiếp", 
                    "📁 Trích xuất từ tệp (PDF, Word, Ảnh)", 
                    "📺 Trích xuất từ YouTube (Link video)", 
                    "🌐 Trích xuất từ trang web (URL)"
                ],
                horizontal=True,
                label_visibility="collapsed"
            )

            input_data_content = ""
            uploaded_file = None
            extracted_images = []

            if "Nhập chủ đề" in nguon_nhap:
                input_data_content = st.text_input("Nhập chủ đề bài kiểm tra:", placeholder="VD: Định luật Ôm, Phản ứng hóa học lớp 9...")
            elif "Trích xuất từ tệp" in nguon_nhap:
                uploaded_file = st.file_uploader("Tải lên tài liệu (PDF, Word, TXT, Ảnh):", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
                if uploaded_file:
                    with st.spinner("Đang đọc dữ liệu từ tệp..."):
                        # Xử lý trích xuất đơn giản
                        extracted_text = "Đã nhận tệp tài liệu"
            elif "YouTube" in nguon_nhap:
                input_data_content = st.text_input("Dán đường dẫn (URL) Video YouTube:", placeholder="https://www.youtube.com/watch?v=...")
            else:
                input_data_content = st.text_input("Dán đường dẫn (URL) Trang web tài liệu:", placeholder="https://vi.wikipedia.org/wiki/...")

            st.markdown("---")
            col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
            with col_cfg1:
                so_luong = st.number_input("Tổng số câu hỏi:", min_value=5, max_value=50, value=10, step=5)
            with col_cfg2:
                do_kho = st.selectbox("Mức độ khó:", ["Nhận biết", "Thông hiểu", "Vận dụng", "Hỗn hợp"])
            with col_cfg3:
                do_ut_cau_hoi = st.multiselect(
                    "Các dạng câu hỏi:",
                    ["Trắc nghiệm (4 lựa chọn)", "Đúng / Sai"],
                    default=["Trắc nghiệm (4 lựa chọn)"]
                )

            them_chi_tiet = st.text_area("Yêu cầu thêm (Tuỳ chọn):", height=70, placeholder="VD: Tập trung vào phần bài tập tính toán...")
            btn_tao_quiz = st.button("🚀 TẠO BỘ CÂU HỎI THÔNG MINH", type="primary", use_container_width=True)

        if btn_tao_quiz:
            st.success("✅ Đã khởi tạo cấu hình AI thành công!")

        st.divider()
        st.markdown("### 💾 Quản lý Bài Kiểm Tra & Thêm Câu Hỏi")
        
        col_quanly1, col_quanly2 = st.columns(2)
        with col_quanly1:
            st.write("#### Tạo mới bài Quiz")
            new_title = st.text_input("Tên bài Quiz")
            new_subj = st.text_input("Môn học")
            new_grade = st.text_input("Khối lớp")
            new_top = st.text_input("Chủ đề")
            if st.button("💾 Lưu bài Quiz mới"):
                if new_title.strip():
                    add_exam(new_title, new_subj, new_grade, new_top)
                    st.success("✅ Đã lưu bài Quiz!")
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập tên bài Quiz.")

        with col_quanly2:
            st.write("#### Thêm câu hỏi vào bài")
            exams = get_exams()
            if exams:
                exam_dict = {e[1]: e[0] for e in exams}
                selected_ex = st.selectbox("Chọn bài Quiz", exam_dict.keys())
                ex_id = exam_dict[selected_ex]

                hinh_thuc_nhap = st.radio("Cách thêm câu hỏi:", ["✍️ Nhập thủ công", "📁 Tải lên file Excel/CSV"], horizontal=True)
                if "thủ công" in hinh_thuc_nhap:
                    q_content = st.text_area("Nội dung câu hỏi")
                    oa = st.text_input("Đáp án A")
                    ob = st.text_input("Đáp án B")
                    oc = st.text_input("Đáp án C")
                    od = st.text_input("Đáp án D")
                    ans_val = st.selectbox("Đáp án đúng", ["A", "B", "C", "D"])
                    if st.button("➕ Thêm câu"):
                        if q_content.strip():
                            add_question(ex_id, q_content, oa, ob, oc, od, ans_val)
                            st.success("✅ Đã thêm câu hỏi!")
                else:
                    up_file = st.file_uploader("Tải file Excel/CSV mẫu:", type=["csv", "xlsx"])
                    if up_file:
                        try:
                            df_imp = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
                            if st.button("🚀 XÁC NHẬN IMPORT HÀNG LOẠT"):
                                for _, r in df_imp.iterrows():
                                    add_question(ex_id, str(r.get("content","")), str(r.get("option_a","")), str(r.get("option_b","")), str(r.get("option_c","")), str(r.get("option_d","")), str(r.get("answer","A")).strip().upper())
                                st.success("🎉 Import thành công hàng loạt câu hỏi!")
                        except Exception as e:
                            st.error(f"Lỗi đọc file: {e}")
            else:
                st.info("Chưa có bài Quiz nào được tạo.")

    # ========================================================
    # TAB 2: PHÒNG THI ĐẤU REAL-TIME & CHẤM ĐIỂM
    # ========================================================
    with tab_nhung:
        st.markdown("#### 🏆 Phòng Thi Đấu Trực Tuyến & Chấm Điểm Tự Động")
        
        query_params = st.query_params
        default_phong = query_params.get("phong", "")
        default_role_idx = 1 if default_phong else 0

        vai_tro = st.radio(
            "Thầy/Cô đang mở máy tính này với vai trò gì?", 
            ["🖥️ Giáo viên (Host - Trình chiếu & Chấm điểm)", "📱 Học sinh (Client - Gửi đáp án)"], 
            index=default_role_idx,
            horizontal=True
        )
        
        st.markdown("---")

        try:
            import pusher
            pusher_client = pusher.Pusher(
                app_id=PUSHER_CONFIG["app_id"],
                key=PUSHER_CONFIG["key"],
                secret=PUSHER_CONFIG["secret"],
                cluster=PUSHER_CONFIG["cluster"],
                ssl=True
            )
            
            # =========================================
            # MÀN HÌNH GIÁO VIÊN
            # =========================================
            if "Giáo viên" in vai_tro:
                st.markdown("### 👑 BẢNG ĐIỀU KHIỂN & CHẤM ĐIỂM GIÁO VIÊN")
                
                col_host1, col_host2 = st.columns([1, 2])
                
                with col_host1:
                    st.markdown("#### 1. Mời Học Sinh (QR Code)")
                    ma_phong = st.text_input("Mã Phòng thi:", value="123456")
                    app_url = st.text_input("Link phần mềm này:", placeholder="VD: https://thcsnguyenchithanh-lhd.streamlit.app")
                    
                    if app_url and HAS_QRCODE:
                        parsed = urlparse.urlparse(app_url)
                        query_dict = urlparse.parse_qs(parsed.query)
                        query_dict["phong"] = [ma_phong]
                        new_query = urlparse.urlencode(query_dict, doseq=True)
                        deep_link = urlparse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
                        
                        qr = qrcode.QRCode(version=1, box_size=5, border=2)
                        qr.add_data(deep_link)
                        qr.make(fit=True)
                        img_qr = qr.make_image(fill_color="black", back_color="white")
                        buf = io.BytesIO()
                        img_qr.save(buf, format="PNG")
                        st.image(buf.getvalue(), caption=f"Quét để vào phòng: {ma_phong}", width=200)
                    elif not HAS_QRCODE:
                        st.warning("Cài đặt `pip install qrcode[pil]` để tạo mã QR.")

                    st.markdown("#### 3. Đáp Án Chuẩn (Để chấm điểm)")
                    dap_an_dung = st.selectbox("Chọn đáp án đúng cho câu hiện tại:", ["Chưa chọn", "A", "B", "C", "D"])

                with col_host2:
                    st.markdown("#### 2. Trình Chiếu Câu Hỏi Lên Tivi")
                    embed_input = st.text_input("Dán Link bất kỳ (Quizizz, Blooket, Web sưu tầm...):", placeholder="VD: Link bài tập được chia sẻ...")
                    target_url = embed_input.strip()
                    if "src=" in target_url:
                        try:
                            import re
                            match = re.search(r'src=["\'](.*?)["\']', target_url)
                            if match: target_url = match.group(1)
                        except: pass
                    if target_url:
                        st.components.v1.iframe(target_url, height=450, scrolling=True)
                    else:
                        st.info("💡 Dán link vào ô trên để hiển thị câu hỏi lên màn hình tivi cho học sinh quan sát.")

                st.markdown("---")
                st.markdown("#### 🏆 BẢNG KẾT QUẢ & CHẤM ĐIỂM TRỰC TUYẾN")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🚀 PHÁT TÍN HIỆU BẮT ĐẦU TRẢ LỜI", type="primary", use_container_width=True):
                        current_time = time.time()
                        pusher_client.trigger(f'phong-{ma_phong}', 'cau_moi', {'thoi_gian': current_time})
                        st.success("✅ Đã phát tín hiệu mở cổng trả lời cho học sinh!")
                with col_btn2:
                    if st.button("🛑 KHÓA CỔNG TRẢ LỜI", use_container_width=True):
                        pusher_client.trigger(f'phong-{ma_phong}', 'het_gio', {'message': 'stop'})
                        st.error("🛑 Đã khóa cổng trả lời!")

                # RADAR NHẬN ĐÁP ÁN & CHẤM ĐIỂM TRỰC TIẾP
                html_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                  <script src="https://js.pusher.com/8.0/pusher.min.js"></script>
                  <style>
                    body {{ font-family: sans-serif; font-size: 14px; margin: 0; background: #f9f9f9; color: #333; }}
                    .container {{ display: flex; gap: 15px; }}
                    .box {{ flex: 1; height: 260px; overflow-y: auto; background: #1e1e1e; color: #00ff00; padding: 12px; border-radius: 8px; font-family: monospace; line-height: 1.4; }}
                    .score-board {{ flex: 1; height: 260px; overflow-y: auto; background: #fff; color: #333; padding: 12px; border-radius: 8px; border: 1px solid #ccc; }}
                    h4 {{ margin: 0 0 8px 0; font-size: 14px; color: #555; }}
                    .correct {{ color: #4caf50; font-weight: bold; }}
                    .incorrect {{ color: #f44336; font-weight: bold; }}
                  </style>
                </head>
                <body>
                  <div class="container">
                    <div class="box">
                      <h4>📡 Nhật ký kết nối (Live Log):</h4>
                      <div id="log">[Hệ thống] Sẵn sàng nhận đáp án cố định...<br></div>
                    </div>
                    <div class="score-board">
                      <h4>🏆 Danh sách đáp án học sinh gửi về:</h4>
                      <div id="results">Chưa có học sinh gửi đáp án.<br></div>
                    </div>
                  </div>
                  <script>
                    var pusher = new Pusher('{PUSHER_CONFIG["key"]}', {{ cluster: '{PUSHER_CONFIG["cluster"]}' }});
                    var channel = pusher.subscribe('phong-{ma_phong}');
                    var logDiv = document.getElementById('log');
                    var resDiv = document.getElementById('results');
                    var studentAnswers = {{}};
                    var startTime = 0;
                    var correctAns = "{dap_an_dung}";

                    channel.bind('hs_vao_phong', function(data) {{
                      logDiv.innerHTML += '👋 [' + data.nhom + '] đã vào phòng.<br>';
                      logDiv.scrollTop = logDiv.scrollHeight;
                    }});

                    channel.bind('cau_moi', function(data) {{
                      startTime = data.thoi_gian;
                      studentAnswers = {{}};
                      resDiv.innerHTML = 'Đang chờ đáp án vòng mới...<br>';
                      logDiv.innerHTML += '<br>🚀 BẮT ĐẦU CÂU HỎI MỚI!<br>';
                      logDiv.scrollTop = logDiv.scrollHeight;
                    }});

                    channel.bind('nop_dap_an', function(data) {{
                      var timeTaken = startTime > 0 ? (data.thoi_gian - startTime).toFixed(2) + 's' : '';
                      studentAnswers[data.nhom] = {{ ans: data.dap_an, time: timeTaken }};
                      
                      var html = '<ul>';
                      for (var student in studentAnswers) {{
                        var item = studentAnswers[student];
                        var status = "";
                        if (correctAns !== "Chưa chọn") {{
                          status = (item.ans === correctAns) ? '<span class="correct"> ✔️ Đúng (+1đ)</span>' : '<span class="incorrect"> ❌ Sai</span>';
                        }}
                        html += '<li><b>' + student + '</b> chọn: <span style="font-size:16px; color:blue;">' + item.ans + '</span> (' + item.time + ')' + status + '</li>';
                      }}
                      html += '</ul>';
                      resDiv.innerHTML = html;
                      logDiv.innerHTML += '🎯 [' + data.nhom + '] vừa chọn ' + data.dap_an + '<br>';
                      logDiv.scrollTop = logDiv.scrollHeight;
                    }});
                  </script>
                </body>
                </html>
                """
                st.components.v1.html(html_code, height=300, scrolling=True)

            # =========================================
            # MÀN HÌNH HỌC SINH
            # =========================================
            else:
                st.markdown("### 📱 TAY CẦM ĐIỀU KHIỂN HỌC SINH")
                
                if "hs_nhom" not in st.session_state:
                    st.session_state["hs_nhom"] = ""
                if "hs_phong" not in st.session_state:
                    st.session_state["hs_phong"] = ""

                if not st.session_state["hs_nhom"]:
                    st.info("Nhập thông tin để kết nối vào phòng thi.")
                    nhap_phong = st.text_input("Mã Phòng:", value=default_phong)
                    nhap_ten = st.text_input("Tên Nhóm / Tên Học sinh:")
                    
                    if st.button("🚪 VÀO PHÒNG THI", type="primary", use_container_width=True):
                        if nhap_phong and nhap_ten:
                            st.session_state["hs_phong"] = nhap_phong
                            st.session_state["hs_nhom"] = nhap_ten
                            try:
                                pusher_client.trigger(
                                    f'phong-{nhap_phong}', 
                                    'hs_vao_phong', 
                                    {'nhom': nhap_ten}
                                )
                            except: pass
                            st.rerun()
                        else:
                            st.error("Vui lòng nhập đủ Mã phòng và Tên!")
                
                else:
                    st.success(f"🟢 Thí sinh: **{st.session_state['hs_nhom']}** | Phòng: **{st.session_state['hs_phong']}**")
                    st.markdown("#### 📺 Quan sát câu hỏi trên tivi và chọn đáp án:")
                    
                    def send_answer(ans):
                        try:
                            pusher_client.trigger(
                                f'phong-{st.session_state["hs_phong"]}', 
                                'nop_dap_an', 
                                {'nhom': st.session_state['hs_nhom'], 'dap_an': ans, 'thoi_gian': time.time()}
                            )
                            st.success(f"✅ Đã gửi đáp án **{ans}** lên hệ thống!")
                        except:
                            st.error("Lỗi kết nối mạng.")

                    st.markdown("""
                    <style>
                    div[data-testid="stButton"] button { height: 90px; font-size: 28px; font-weight: bold; }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("🟥 A", use_container_width=True): send_answer("A")
                        if st.button("🟦 C", use_container_width=True): send_answer("C")
                    with c2:
                        if st.button("🟨 B", use_container_width=True): send_answer("B")
                        if st.button("🟩 D", use_container_width=True): send_answer("D")
                        
                    if st.button("Thoát phòng"):
                        st.session_state["hs_nhom"] = ""
                        st.session_state["hs_phong"] = ""
                        st.query_params.clear()
                        st.rerun()

        except ImportError:
            st.error("❌ Thư viện kết nối chưa cài đặt. Vui lòng chạy: `pip install pusher qrcode[pil]`")
        except Exception as e:
            st.error(f"❌ Lỗi kết nối Pusher: {e}")
