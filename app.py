from flask import Flask, render_template, request, redirect, session, flash
import sqlite3

import os

print("DB PATH =", os.path.abspath("database.db"))

app = Flask(__name__)
app.secret_key = "python_project"
current_user_id = None

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS User(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    level TEXT,
    xp INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM User WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            conn.close()

            return """
            <script>
            alert('이미 가입된 이메일입니다.');
            window.location.href='/signup';
            </script>
            """

        cursor.execute(
            "INSERT INTO User(name,email,password,level) VALUES(?,?,?,?)",
            (name, email, password, None)
        )

        conn.commit()
        conn.close()

        return """
        <script>
        if(confirm('회원가입이 완료되었습니다. 로그인 하시겠습니까?')){
            window.location.href='/login';
        }else{
            window.location.href='/';
        }
        </script>
        """

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM User WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            global current_user_id
            current_user_id = user[0]

            # level 컬럼 확인
            if user[4] is None:
                return redirect("/level_test")
            else:
                return redirect("/dashboard")

        else:
            return "이메일 또는 비밀번호가 틀렸습니다."

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    global current_user_id

    if current_user_id is None:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT level, xp FROM User WHERE user_id=?",
        (current_user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template(
        "dashboard.html",
        level=user[0],
        xp=user[1],
        logged_in=True
)

@app.route("/learning")
def learning():

    global current_user_id

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT level FROM User WHERE user_id=?",
        (current_user_id,)
    )

    result = cursor.fetchone()

    print("current_user_id =", current_user_id)
    print("result =", result)

    conn.close()

    if result is None:
        return "사용자를 찾을 수 없습니다."

    level = result[0]

    print("level =", level)

    if level == "Beginner":
        return render_template("learning_beginner.html")

    elif level == "Intermediate":
        return render_template("learning_intermediate.html")

    elif level == "Advanced":
        return render_template("learning_advanced.html")

    else:
        return f"level 값이 이상함: {level}"

@app.route("/complete_learning", methods=["POST"])
def complete_learning():

    global current_user_id

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE User
        SET xp = xp + 10
        WHERE user_id = ?
        """,
        (current_user_id,)
    )

    conn.commit()
    conn.close()

    flash(" XP +10 획득!")

    return redirect("/dashboard")

@app.route("/wrong_answer")
def wrong_answer():

    wrong_answers = session.get("wrong_answers", [])

    return render_template(
        "wrong_answer.html",
        wrong_answers=wrong_answers
    )

@app.route("/level_test", methods=["GET", "POST"])
def level_test():

    if request.method == "POST":

        score = 0
        wrong_answers = []

        questions = {
            "q1": ("Python 출력 함수는?", "print()"),
            "q2": ("사용자 입력 함수는?", "input()"),
            "q3": ("리스트(List) 표기법은?", "[ ]"),
            "q4": ("조건문은?", "if"),
            "q5": ("반복문은?", "for")
        }

        for q in questions:

            if request.form.get(q) == "correct":
                score += 1

            else:
                wrong_answers.append({
                    "question": questions[q][0],
                    "answer": questions[q][1]
                })

        session["wrong_answers"] = wrong_answers

        if score <= 2:
            level = "Beginner"

        elif score <= 4:
            level = "Intermediate"

        else:
            level = "Advanced"

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE User SET level=? WHERE user_id=?",
            (level, current_user_id)
        )

        conn.commit()
        conn.close()

        return render_template(
            "course.html",
            level=level,
            score=score
        )

    return render_template("level_test.html")

@app.route("/logout")
def logout():

    global current_user_id

    current_user_id = None

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)

