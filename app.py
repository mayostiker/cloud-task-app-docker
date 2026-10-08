from flask import Flask, render_template, request, redirect
from database import get_connection

app = Flask(__name__)

@app.route("/")
def home():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, title, completed, created_at "
        "FROM tasks ORDER BY created_at DESC"
    )

    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    task = request.form.get("task")

    if task:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO tasks (title) VALUES (%s)",
            (task,)
        )

        connection.commit()

        cursor.close()
        connection.close()

    return redirect("/")

@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE tasks SET completed = TRUE WHERE id = %s",
        (task_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")
@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = %s",
        (task_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
