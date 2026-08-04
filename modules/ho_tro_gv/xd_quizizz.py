# -*- coding: utf-8 -*-
"""
====================================================
AI Teacher Assistant
Module: Xây dựng Quizizz Online (Hỗ trợ Import Excel)
File: modules/ho_tro_gv/xd_quizizz.py
====================================================
"""

import streamlit as st
import sqlite3
import os
from datetime import datetime
import pandas as pd

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
# GIAO DIỆN GIÁO VIÊN
# ==================================================

def teacher_view():
    st.subheader("👨‍🏫 Giáo viên - Xây dựng Quiz & Nhập liệu")

    tab1, tab2 = st.tabs(["➕ Tạo bài & Thêm câu hỏi", "📊 Kết quả học sinh"])

    with tab1:
        st.write("### 1. Tạo bài kiểm tra mới")
        title = st.text_input("Tên bài Quiz", key="exam_title")
        subject = st.text_input("Môn học", key="exam_subj")
        grade = st.text_input("Khối lớp", key="exam_grade")
        topic = st.text_input("Chủ đề", key="exam_topic")

        if st.button("💾 Lưu bài Quiz"):
            if title.strip():
                add_exam(title, subject, grade, topic)
                st.success("✅ Đã tạo bài Quiz thành công!")
                st.rerun()
            else:
                st.warning("⚠️ Vui lòng nhập tên bài Quiz.")

        st.divider()

        exams = get_exams()
        if exams:
            exam_dict = {e[1]: e[0] for e in exams}
            selected = st.selectbox("Chọn bài Quiz để thêm câu hỏi", exam_dict.keys())
            exam_id = exam_dict[selected]

            st.write(f"### 2. Thêm câu hỏi cho bài: **{selected}**")
            
            # CHỌN HÌNH THỨC THÊM CÂU HỎI
            hinh_thuc = st.radio("Chọn phương thức nhập câu hỏi:", ["✍️ Nhập từng câu thủ công", "📁 Tải lên tệp Excel/CSV hàng loạt"], horizontal=True)

            if "thủ công" in hinh_thuc:
                content = st.text_area("Nội dung câu hỏi")
                a = st.text_input("Phương án A")
                b = st.text_input("Phương án B")
                c = st.text_input("Phương án C")
                d = st.text_input("Phương án D")
                answer = st.selectbox("Đáp án đúng", ["A", "B", "C", "D"])

                if st.button("➕ Thêm câu hỏi này"):
                    if content.strip():
                        add_question(exam_id, content, a, b, c, d, answer)
                        st.success("✅ Đã thêm câu hỏi thành công!")
                    else:
                        st.warning("⚠️ Nội dung câu hỏi không được để trống.")
            else:
                st.info("💡 **Hướng dẫn file mẫu:** Tải lên file Excel (.xlsx) hoặc CSV gồm các cột: `content`, `option_a`, `option_b`, `option_c`, `option_d`, `answer` (đáp án viết hoa A, B, C hoặc D).")
                
                uploaded_csv = st.file_uploader("Tải lên file câu hỏi:", type=["csv", "xlsx"])
                if uploaded_csv:
                    try:
                        if uploaded_csv.name.endswith('.csv'):
                            df_import = pd.read_csv(uploaded_csv)
                        else:
                            df_import = pd.read_excel(uploaded_csv)

                        st.write("🔍 Xem trước dữ liệu tải lên:", df_import.head())

                        if st.button("🚀 XÁC NHẬN IMPORT VÀO HỆ THỐNG"):
                            count = 0
                            for _, row in df_import.iterrows():
                                add_question(
                                    exam_id,
                                    str(row.get("content", "")),
                                    str(row.get("option_a", "")),
                                    str(row.get("option_b", "")),
                                    str(row.get("option_c", "")),
                                    str(row.get("option_d", "")),
                                    str(row.get("answer", "A")).strip().upper()
                                )
                                count += 1
                            st.success(f"🎉 Đã nhập thành công {count} câu hỏi vào hệ thống!")
                    except Exception as e:
                        st.error(f"❌ Lỗi đọc file: {e}")
        else:
            st.info("💡 Vui lòng tạo ít nhất một bài Quiz ở phía trên trước khi thêm câu hỏi.")

    with tab2:
        st.write("### 📊 Danh sách kết quả kiểm tra của học sinh")
        data = get_results()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Học sinh", "Bài kiểm tra ID", "Điểm số", "Thời gian nộp"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Chưa có kết quả nộp bài nào.")

# ==================================================
# GIAO DIỆN HỌC SINH
# ==================================================

def student_view():
    st.subheader("👩‍🎓 Học sinh làm bài kiểm tra")

    student = st.text_input("Họ tên học sinh / Tên nhóm")
    exams = get_exams()

    if not exams:
        st.warning("⚠️ Hiện tại chưa có bài kiểm tra nào được tạo.")
        return

    exam_dict = {e[1]: e[0] for e in exams}
    selected = st.selectbox("Chọn bài kiểm tra", exam_dict.keys())
    exam_id = exam_dict[selected]

    questions = get_questions(exam_id)

    if not questions:
        st.warning("⚠️ Bài kiểm tra này chưa có câu hỏi nào.")
        return

    answers = {}
    for i, q in enumerate(questions):
        st.write(f"### Câu {i+1}: {q[2]}")
        options = [q[3], q[4], q[5], q[6]]
        answers[i] = st.radio(f"Chọn đáp án câu {i+1}:", options, key=f"q_{exam_id}_{i}")

    if st.button("📤 NỘP BÀI VÀ CHẤM ĐIỂM", type="primary"):
        if not student.strip():
            st.error("❌ Vui lòng nhập họ tên trước khi nộp bài!")
            return

        correct = 0
        for i, q in enumerate(questions):
            options = [q[3], q[4], q[5], q[6]]
            try:
                correct_index = ["A", "B", "C", "D"].index(q[7].strip().upper())
                if answers[i] == options[correct_index]:
                    correct += 1
            except ValueError:
                pass

        score = round(correct / len(questions) * 10, 2)
        save_result(student, exam_id, score)
        st.success(f"🎉 Nộp bài thành công! Điểm của em: **{score} / 10** ({correct}/{len(questions)} câu đúng)")

# ==================================================
# HÀM CHÍNH GỌI TỪ APP.PY
# ==================================================

def run(ai_engine_cu=None):
    create_database()
    st.title("📝 AI Quizizz - Hệ thống Kiểm tra Trực tuyến")

    mode = st.sidebar.radio("Chọn vai trò:", ["👨‍🏫 Giáo viên", "👩‍🎓 Học sinh"])

    if mode == "👨‍🏫 Giáo viên":
        teacher_view()
    else:
        student_view()

def render_xd_quizizz(ai_engine_cu=None):
    run(ai_engine_cu)
