import os
from flask import Flask, render_template, send_file, request, redirect, url_for, session
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "attendance.db")


# DATABASE CONNECTION
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# HOME REDIRECT
@app.route("/")
def home():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("lecturer_dashboard"))


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"].strip()

        conn = get_db_connection()

        print("LOGIN ATTEMPT:", email, password)

        user = conn.execute(
            "SELECT * FROM users WHERE LOWER(email)=LOWER(?) AND password=?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            print("USER FOUND:", dict(user))

            session["user_id"] = user["user_id"]
            session["role"] = user["role"]
            session["name"] = user["name"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("lecturer_dashboard"))

        print("LOGIN FAILED")
        return "Invalid Login"

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ADMIN DASHBOARD
@app.route("/admin")
def admin_dashboard():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()

    lecturers = conn.execute(
        "SELECT * FROM users WHERE role='lecturer'"
    ).fetchall()

    units = conn.execute("""
        SELECT units.*, users.name as lecturer_name
        FROM units
        LEFT JOIN users
        ON units.lecturer_id = users.user_id
    """).fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        lecturers=lecturers,
        units=units
    )


# LECTURER DASHBOARD
@app.route("/lecturer")
def lecturer_dashboard():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    conn = get_db_connection()

    units = conn.execute(
        "SELECT * FROM units WHERE lecturer_id=?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "lecturer_dashboard.html",
        units=units,
        lecturer=session["name"]
    )


# VIEW UNIT ATTENDANCE
@app.route("/unit/<int:unit_id>")
def view_unit(unit_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    conn = get_db_connection()

    records = conn.execute("""
        SELECT attendance.attendance_id,
               attendance.session_id,
               attendance.student_name,
               attendance.marked_at
        FROM attendance
        JOIN sessions
        ON attendance.session_id = sessions.session_id
        WHERE sessions.unit_id=?
        ORDER BY attendance.marked_at DESC
    """, (unit_id,)).fetchall()

    conn.close()

    return render_template(
        "unit_attendance.html",
        records=records
    )


# START SESSION
@app.route("/start_session/<int:unit_id>")
def start_session(unit_id):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO sessions (unit_id, started_at, started_by)
        VALUES (?, datetime('now'), ?)
    """, (unit_id, session["user_id"]))

    session_id = cur.lastrowid

    conn.commit()
    conn.close()

    os.system(f'python gui_start.py {session_id}')

    return redirect(url_for("lecturer_dashboard"))


# DOWNLOAD REPORT
@app.route("/download")
def download():

    conn = get_db_connection()

    df = pd.read_sql_query(
        "SELECT attendance_id, session_id, student_name, marked_at FROM attendance",
        conn
    )

    conn.close()

    file = "attendance_report.xlsx"
    df.to_excel(file, index=False)

    return send_file(file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)