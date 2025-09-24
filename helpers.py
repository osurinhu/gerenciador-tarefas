from datetime import datetime
from flask import redirect, render_template, session
from functools import wraps
import sqlite3


# Decorate routes to require login.
# http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Show error for the user
def render_error(message="", error=""):
    return render_template("error.html",message=message, error=error)

# Query for task in the db
def query_tasks(active=None):

    # Set db connection
    with sqlite3.connect("taskmanager.db") as con:
        cur = con.cursor()

    match active:
        case "active":
            # Query for tasks
            query = cur.execute("SELECT title, description, datentime, id FROM tasks WHERE user_id = ? AND active = 1 ORDER BY datentime", [session["user_id"]]).fetchall()

        case "disabled":
            # Query for tasks
            query = cur.execute("SELECT title, description, datentime, id FROM tasks WHERE user_id = ? AND active = 0 ORDER BY datentime", [session["user_id"]]).fetchall()

        case None:
            # Query for tasks
            query = cur.execute("SELECT title, description, datentime, id FROM tasks WHERE user_id = ? ORDER BY datentime", [session["user_id"]]).fetchall()


    # Managing query data
    tasks = []
    for row in query:

        task = {}

        task["title"] = row[0]
        task["description"] = row[1]

        date_object = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")

        task["date"] = date_object.strftime("%B %d, %Y")
        task["jsdate"] = date_object.strftime("%m-%d-%Y")
        task["time"] = date_object.strftime("%H:%M")
        task["id"] = row[3]

        tasks.append(task)

    return tasks
