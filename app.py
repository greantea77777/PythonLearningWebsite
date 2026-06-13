from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
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

    if current_user_id is None:
        return redirect("/login")

    return render_template("learning.html")

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

    return redirect("/dashboard")

@app.route("/wrong_answer")
def wrong_answer():

    global current_user_id

    if current_user_id is None:
        return redirect("/login")

    return render_template("wrong_answer.html")

@app.route("/level_test", methods=["GET", "POST"])
def level_test():

    if request.method == "POST":

        score = 0

        answers = ["q1", "q2", "q3", "q4", "q5"]

        for answer in answers:
            if request.form.get(answer) == "correct":
                score += 1

        if score <= 2:
            level = "Beginner"

        elif score <= 4:
            level = "Intermediate"

        else:
            level = "Advanced"

        # DB에 레벨 저장
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

