import sqlite3

conn = sqlite3.connect("attendance.db")
cur = conn.cursor()

# USERS TABLE
cur.execute("""
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# UNITS TABLE
cur.execute("""
CREATE TABLE units (
    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_name TEXT NOT NULL,
    lecturer_id INTEGER,
    FOREIGN KEY (lecturer_id) REFERENCES users(user_id)
)
""")

# SESSIONS TABLE
cur.execute("""
CREATE TABLE sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER,
    date TEXT,
    started_by INTEGER,
    FOREIGN KEY (unit_id) REFERENCES units(unit_id)
)
""")

# ATTENDANCE TABLE
cur.execute("""
CREATE TABLE attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    student_name TEXT,
    marked_at TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
)
""")

conn.commit()
conn.close()

print("Database created successfully")