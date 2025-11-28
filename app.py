from flask import Flask, render_template, request, redirect, url_for
from config import Config
from models import db, Task
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    description = request.form.get("description")
    priority = request.form.get("priority")
    due_date = request.form.get("due_date")

    task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=datetime.strptime(due_date, "%Y-%m-%d") if due_date else None,
    )

    db.session.add(task)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    task = Task.query.get_or_404(id)

    if request.method == "POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        task.priority = request.form.get("priority")
        task.due_date = datetime.strptime(request.form.get("due_date"), "%Y-%m-%d") if request.form.get("due_date") else None
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("edit_task.html", task=task)

@app.route("/delete/<int:id>")
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/toggle/<int:id>")
def toggle(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
