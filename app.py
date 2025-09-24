from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, render_error, query_tasks

# Configure application
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():

    # Query for tasks in te db
    tasks = query_tasks("active")
    return render_template("index.html", tasks=tasks, tcount=len(tasks))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # Forget any user_id
        session.clear()

        # Check if inputs are not empty
        if not request.form.get("username") or not request.form.get("password"):
            return render_error("Provide a username and a password.", 400)

        # Set db connection
        with sqlite3.connect("taskmanager.db") as con:
            cur = con.cursor()

            # Query username
            row = cur.execute(
                "SELECT * FROM users WHERE username = ?",
                [request.form.get("username")]
            ).fetchone()

            if not row or not check_password_hash(row[2], request.form.get("password")):
                return render_error("Incorrect username and/or password.", 403)

            # Set session
            session["user_id"] = row[0]

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    # Clear session
    session.clear()

    # Redirect user
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Check if inputs are not empty
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return render_error("Provide a username a password and confirm the password.", 400)

        # Check if confirmation matches password
        if request.form.get("password") != request.form.get("confirmation"):
            return render_error("Password don't match confirmation.")

        # Set db connection
        with sqlite3.connect("taskmanager.db") as con:
            cur = con.cursor()

            # Check if username is already used
            usr = cur.execute("SELECT username FROM users WHERE username = ?", [request.form.get("username")])
            if usr.fetchone():
                return render_error("Username is already used.", 400)

            # Add account into the db
            cur.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                [request.form.get("username"), generate_password_hash(request.form.get("password"))]
                )

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/addtask", methods=["GET", "POST"])
def addtask():
    if request.method == "POST":

        # Check if inputs are not empty
        if not request.form.get("title") or not request.form.get("description") or not request.form.get("date") or not request.form.get("time"):
            return render_error("All fields need to be completed.",400)

        # Check if title and description are too long
        if len(request.form.get("title")) > 250:
            return render_error("Title too long, 250 characters length limit", 403)

        if len(request.form.get("description")) > 1000:
            return render_error("Descripition too long, 1000 characters length limit", 403)

        # Manage date time data
        datentime = str(request.form.get("date") + " " + request.form.get("time") + ":00")

        # Set db connection
        with sqlite3.connect("taskmanager.db") as con:
            cur = con.cursor()

            # Add task to the db
            cur.execute(
            "INSERT INTO tasks (title, description, datentime, user_id, active) VALUES (?, ?, ?, ?, 1)",
            [request.form.get("title"), request.form.get("description"), datentime, session["user_id"]]
            )

        return redirect("/")
    else:
        return render_template("addtask.html")

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":

        # Set db connection
        with sqlite3.connect("taskmanager.db") as con:
            cur = con.cursor()

            # Remove task from the db
            cur.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", [request.form.get("deleted_task"), session["user_id"]])

        return redirect("/delete")

    else:
        tasks = query_tasks()
        return render_template("delete.html", tasks=tasks, tcount=len(tasks))


@app.route("/disable", methods=["GET", "POST"])
@login_required
def disable():
    if request.method == "POST":
        with sqlite3.connect("taskmanager.db") as con:
            cur = con.cursor()

            # Disable task
            cur.execute("UPDATE tasks SET active = 0 WHERE id = ? AND user_id = ?", [request.form.get("disabled_task"), session["user_id"]])
        return redirect("/")
    else:
        return render_error(error=405)

@app.route("/history")
@login_required
def history():
        tasks = query_tasks()
        return render_template("history .html", tasks=tasks, tcount=len(tasks))


@app.route("/test")
def test():
    return render_error("test page")
