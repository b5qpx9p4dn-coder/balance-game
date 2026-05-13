from flask import Flask, render_template, request, redirect, session
from db import get_db


app = Flask(__name__)
app.secret_key ="testkey"
@app.route("/")
def home():

    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        option_a TEXT,
        option_b TEXT,
        vote_a INTEGER DEFAULT 0,
        vote_b INTEGER DEFAULT 0
    )
    """)
    
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    db.commit()

    posts = db.execute("SELECT * FROM posts").fetchall()

    return render_template("index.html", posts=posts)


@app.route("/write", methods=["GET", "POST"])
def write():

    if "user_id" not in session:
        return redirect("/login")

    if request.method =="POST":
        title = request.form["title"]
        option_a = request.form["option_a"]
        option_b = request.form["option_b"]

        db = get_db()

        db.execute("""
        INSERT INTO posts (title, option_a, option_b, user_id)
        VALUES (?,?,?,?)
        """,(title, option_a, option_b, session["user_id"]))

        db.commit()

        return redirect("/")
    return render_template("write.html")

@app.route("/vote/<int:post_id>/<option>")
def vote(post_id, option):
    db = get_db()

    if option == "a":
        db.execute("""
        UPDATE posts
        SET vote_a = vote_a +1
        WHERE id =?

        """,(post_id,))
    else:
        db.execute("""
        UPDATE posts
        SET vote_b = vote_b + 1
        WHERE id = ?
        """,(post_id,))
    db.commit()

    return redirect("/")


@app.route("/edit/<int:post_id>", methods =["GET","POST"])
def edit(post_id):

    if "user_id" not in session:
        return "로그인 필요"

    db=get_db()

    post = db.execute("""
        SELECT * FROM posts WHERE id = ?
    """, (post_id,)).fetchone()
    if post is None: 
        return "글 없음"
    if post["user_id"] != session.get("user_id"):
        return "권한 없음"

    if request.method == "POST":

        title = request.form["title"]
        option_a = request.form["option_a"]
        option_b = request.form["option_b"]

        db.execute("""
            UPDATE posts
            SET title = ?, option_a = ?, option_b =?
            WHERE id = ? 
        """, (title, option_a, option_b, post_id))

        db.commit()

        return redirect("/")
    

    return render_template("edit.html", post = post)
@app.route("/delete/<int:post_id>", methods =["POST"])
def delete(post_id):
    if "user_id" not in session:
        return "로그인 필요"
    db=get_db()
    post = db.execute("""
        SELECT * FROM posts WHERE id =?
    """,(post_id,)).fetchone()

    if post is None:
        return "글 없음"

    if post["user_id"] != session.get("user_id"):
        return "권한 없음"

        

    db.execute("""
        DELETE FROM posts
        WHERE id = ?
    """,(post_id,))
    db.commit()
    return redirect("/")
  
   

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        db.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """,(username, password))

        db.commit()

        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db=get_db()

        user = db.execute("""
            SELECT * FROM users
            WHERE username = ? AND password =?
        """, (username, password)).fetchone()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")
        return "로그인 실패"
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/post/<int:post_id>")
def post_detail(post_id):
    db=get_db()

    post = db.execute("""
        SELECT * FROM posts WHERE id = ?
    """, (post_id,)).fetchone()

    if post is None:
        return "글 없음"
    total = post["vote_a"] + post["vote_b"]
    if total >0:
        percent_a = round(post["vote_a"]/ total *100)
        percent_b = 100 - percent_a
    else:
        percent_a = percent_b = 0
    
    return render_template(
        "detail.html", 
        post=post,
        percent_a = percent_a,
        percent_b = percent_b,
        total=total
    )
if __name__ == "__main__":
    app.run(debug=True)