"""
====================================================
AI Teacher Assistant
Module: Xây dựng Quizizz Online
File: modules/ho_tro_gv/xd_quizizz.py

Chức năng:
- Giáo viên tạo bài Quiz
- Nhập câu hỏi trắc nghiệm
- Học sinh làm bài
- Tự động chấm điểm
- Lưu kết quả

Version: 1.0
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

DB_FILE = os.path.join(
    DB_FOLDER,
    "quizizz.db"
)



def create_database():

    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)


    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()


    # Bảng bài kiểm tra

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



    # Bảng câu hỏi

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



    # Bảng kết quả

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


def add_exam(
        title,
        subject,
        grade,
        topic
):

    conn = sqlite3.connect(DB_FILE)

    conn.execute(
    """
    INSERT INTO exams
    (
        title,
        subject,
        grade,
        topic,
        created
    )

    VALUES(?,?,?,?,?)

    """,
    (
        title,
        subject,
        grade,
        topic,
        str(datetime.now())
    )
    )


    conn.commit()

    conn.close()





def get_exams():

    conn = sqlite3.connect(DB_FILE)

    data = conn.execute(
        """
        SELECT *
        FROM exams
        ORDER BY id DESC
        """
    ).fetchall()


    conn.close()

    return data





def add_question(
        exam_id,
        content,
        a,
        b,
        c,
        d,
        answer
):

    conn = sqlite3.connect(DB_FILE)


    conn.execute(
    """
    INSERT INTO questions
    (
        exam_id,
        content,
        option_a,
        option_b,
        option_c,
        option_d,
        answer
    )

    VALUES(?,?,?,?,?,?,?)

    """,
    (
        exam_id,
        content,
        a,
        b,
        c,
        d,
        answer
    )
    )


    conn.commit()

    conn.close()





def get_questions(exam_id):

    conn = sqlite3.connect(DB_FILE)


    data = conn.execute(
    """
    SELECT *
    FROM questions
    WHERE exam_id=?

    """,
    (exam_id,)
    ).fetchall()


    conn.close()

    return data





def save_result(
        student,
        exam_id,
        score
):

    conn = sqlite3.connect(DB_FILE)


    conn.execute(
    """
    INSERT INTO results
    (
        student,
        exam_id,
        score,
        submitted
    )

    VALUES(?,?,?,?)

    """,
    (
        student,
        exam_id,
        score,
        str(datetime.now())
    )
    )


    conn.commit()

    conn.close()





def get_results():

    conn = sqlite3.connect(DB_FILE)


    data = conn.execute(
    """
    SELECT *
    FROM results
    """
    ).fetchall()


    conn.close()

    return data






# ==================================================
# GIAO DIỆN GIÁO VIÊN
# ==================================================


def teacher_view():


    st.subheader(
        "👨‍🏫 Giáo viên - Xây dựng Quiz"
    )



    tab1, tab2 = st.tabs(
        [
            "➕ Tạo bài",
            "📊 Kết quả"
        ]
    )



    with tab1:


        st.write(
            "### Tạo bài kiểm tra"
        )


        title = st.text_input(
            "Tên bài Quiz"
        )


        subject = st.text_input(
            "Môn học"
        )


        grade = st.text_input(
            "Khối lớp"
        )


        topic = st.text_input(
            "Chủ đề"
        )



        if st.button(
            "💾 Lưu bài Quiz"
        ):


            add_exam(
                title,
                subject,
                grade,
                topic
            )


            st.success(
                "Đã tạo bài Quiz"
            )




        st.divider()



        exams = get_exams()


        if exams:


            exam_dict = {

                e[1]:e[0]

                for e in exams

            }


            selected = st.selectbox(
                "Chọn bài để thêm câu hỏi",
                exam_dict.keys()
            )


            exam_id = exam_dict[selected]



            st.write(
                "### Thêm câu hỏi"
            )



            content = st.text_area(
                "Nội dung câu hỏi"
            )



            a = st.text_input(
                "Phương án A"
            )


            b = st.text_input(
                "Phương án B"
            )


            c = st.text_input(
                "Phương án C"
            )


            d = st.text_input(
                "Phương án D"
            )


            answer = st.selectbox(
                "Đáp án đúng",
                [
                    "A",
                    "B",
                    "C",
                    "D"
                ]
            )



            if st.button(
                "➕ Thêm câu hỏi"
            ):


                add_question(
                    exam_id,
                    content,
                    a,
                    b,
                    c,
                    d,
                    answer
                )


                st.success(
                    "Đã thêm câu hỏi"
                )




    with tab2:


        st.write(
            "### Danh sách kết quả"
        )


        data=get_results()


        if data:


            df=pd.DataFrame(
                data,
                columns=[
                    "ID",
                    "Học sinh",
                    "Bài",
                    "Điểm",
                    "Thời gian"
                ]
            )


            st.dataframe(
                df,
                use_container_width=True
            )


        else:

            st.info(
                "Chưa có kết quả"
            )







# ==================================================
# GIAO DIỆN HỌC SINH
# ==================================================


def student_view():


    st.subheader(
        "👩‍🎓 Học sinh làm bài"
    )


    student = st.text_input(
        "Họ tên học sinh"
    )



    exams=get_exams()



    if not exams:

        st.warning(
            "Chưa có bài kiểm tra"
        )

        return



    exam_dict={

        e[1]:e[0]

        for e in exams

    }



    selected=st.selectbox(
        "Chọn bài kiểm tra",
        exam_dict.keys()
    )



    exam_id=exam_dict[selected]



    questions=get_questions(
        exam_id
    )



    answers={}



    for i,q in enumerate(questions):


        st.write(
            f"### Câu {i+1}"
        )


        st.write(
            q[2]
        )


        answers[i]=st.radio(
            "",
            [
                q[3],
                q[4],
                q[5],
                q[6]
            ],
            key=f"q{i}"
        )



    if st.button(
        "📤 Nộp bài"
    ):


        correct=0



        for i,q in enumerate(questions):


            options=[

                q[3],
                q[4],
                q[5],
                q[6]

            ]


            index=[
                "A",
                "B",
                "C",
                "D"
            ].index(
                q[7]
            )



            if answers[i]==options[index]:

                correct+=1




        score=0


        if questions:

            score = round(
                correct /
                len(questions)
                *10,
                2
            )



        save_result(
            student,
            exam_id,
            score
        )


        st.success(
            f"🎉 Điểm của em: {score}/10"
        )







# ==================================================
# HÀM CHÍNH GỌI TỪ APP.PY
# ==================================================


def run():


    create_database()



    st.title(
        "📝 AI Quizizz - Kiểm tra trực tuyến"
    )



    mode = st.sidebar.radio(
        "Vai trò",
        [
            "👨‍🏫 Giáo viên",
            "👩‍🎓 Học sinh"
        ]
    )



    if mode=="👨‍🏫 Giáo viên":

        teacher_view()


    else:

        student_view()
