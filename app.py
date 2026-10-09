
import os
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
)
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_connection

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable must be set")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            return "All fields are required", 400

        if len(password) < 8:
            return "Password must be at least 8 characters", 400

        password_hash = generate_password_hash(password)
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
                """,
                (username, email, password_hash),
            )
            connection.commit()

        except Exception as exc:
            connection.rollback()
            if getattr(exc, "errno", None) == 1062:
                return "Username or email already exists", 400
            app.logger.exception("Registration failed")
            return "Registration failed. Please try again.", 500

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id, username, password_hash
                FROM users
                WHERE username = %s
                """,
                (username,),
            )
            user = cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("home"))

        return "Invalid username or password", 401

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, title, completed, created_at
            FROM tasks
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (session["user_id"],),
        )
        tasks = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
@login_required
def add_task():
    task = request.form.get("task", "").strip()

    if task:
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO tasks (user_id, title) VALUES (%s, %s)",
                (session["user_id"], task),
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    return redirect(url_for("home"))


@app.route("/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE tasks
            SET completed = TRUE
            WHERE id = %s AND user_id = %s
            """,
            (task_id, session["user_id"]),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s AND user_id = %s",
            (task_id, session["user_id"]),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
