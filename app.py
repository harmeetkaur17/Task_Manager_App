from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, Task, User
from datetime import datetime
import os


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create tables
with app.app_context():
    db.create_all()

@app.route("/")
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template("index.html", tasks=tasks)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

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
        user_id=current_user.id,
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
