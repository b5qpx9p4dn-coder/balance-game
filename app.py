from flask import Flask, render_template, request, redirect, session, flash
from db import get_db, init_db


app = Flask(__name__)
app.secret_key ="testkey"

init_db()

@app.route("/")
def home():

    db = get_db()

 

    posts = db.execute("SELECT * FROM posts").fetchall()

    return render_template("index.html", posts=posts)


@app.route("/write", methods=["GET", "POST"])
def write():

    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect("/")
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

    return redirect(f"/post/{post_id}")


@app.route("/edit/<int:post_id>", methods =["GET","POST"])
def edit(post_id):
    db=get_db()
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect("/login")

    
    post = db.execute("""
        SELECT * FROM posts WHERE id = ?
    """, (post_id,)).fetchone()
    if post is None: 
        flash("글이 없습니다.")
        return redirect("/")
    if post["user_id"] != session.get("user_id"):
        flash("권한이 없습니다.")
        return redirect("/")

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
        flash("수정 완료")
        return redirect("/")
    

    return render_template("edit.html", post = post)
@app.route("/delete/<int:post_id>", methods =["POST"])
def delete(post_id):
    db=get_db()
 
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect("/login")
  
    post = db.execute("""
        SELECT * FROM posts WHERE id =?
    """,(post_id,)).fetchone()

    if post is None:
        flash("글 없음")
        return redirect("/")


    if post["user_id"] != session.get("user_id"):
        flash("권한이 없습니다.")
        return redirect("/")

        

    db.execute("""
        DELETE FROM posts
        WHERE id = ?
    """,(post_id,))
    db.commit()
    flash("삭제 완료")
    return redirect("/")

  
   

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]

        if not username or not password or not password2:
            flash("모든 항목을 입력해주세요")
            return render_template("register.html", username = username)

        if password != password2:
            flash("비밀번호가 일치하지 않습니다")
            return redirect("/register")

        db = get_db()

        user = db.execute("""
            SELECT * FROM users
            WHERE username = ?
        """,(username,)).fetchone()

        if user:
            flash(" 이미 존재하는 아이디입니다.")
            return redirect("/register")

        db.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """,(username, password))

        db.commit()
        flash("화원가입 완료")
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
        flash("아이디 혹은 비밀번호가 틀렸습니다.")
        return redirect("/login")
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

    comments = db.execute("""
        SELECT comments.*, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE post_id = ?
        ORDER BY comments.id DESC

    """,(post_id,)).fetchall()
    
    return render_template(
        "detail.html", 
        post=post,
        percent_a = percent_a,
        percent_b = percent_b,
        total=total,
        comments=comments
    )


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(f"/post/{post_id}")
    content = request.form["content"]

    db = get_db()
    db.execute("""
        INSERT INTO comments (content, post_id, user_id)
        VALUES (?,?,?)
    """,(content, post_id, session["user_id"]))
    db.commit()
    return redirect(f"/post/{post_id}")

if __name__ == "__main__":
    app.run(debug=True)

