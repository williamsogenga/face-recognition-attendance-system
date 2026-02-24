import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "attendance.db")

UNITS = [
    "COMP 326 - OOP with Java",
    "INTE 221 - Web Applications Programming",
    "INTE 223 - Assembly Language Programming",
    "INTE 226 - System Analysis and Design",
    "INTE 321 - Distributed Systems"
]

ROOMS = [
    "Lab 1",
    "Lab 2",
    "Room A1",
    "Room B12",
    "Computer Lab"
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit TEXT,
            room TEXT,
            started_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            name TEXT,
            marked_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def start_session():
    unit = unit_var.get()
    room = room_var.get()

    if unit == "Select Unit" or room == "Select Room":
        messagebox.showerror("Missing Info", "Please select both unit and room.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO sessions (unit, room, started_at)
        VALUES (?, ?, ?)
    """, (unit, room, started_at))

    session_id = cur.lastrowid
    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Session Started",
        f"Unit: {unit}\nRoom: {room}\nSession ID: {session_id}"
    )

    from attendance import run_attendance
    run_attendance(session_id, unit, room, DB_PATH)


# ---------------- GUI ----------------
init_db()

root = tk.Tk()
root.title("Face Attendance System")
root.geometry("520x260")

tk.Label(root, text="Start Attendance Session",
         font=("Segoe UI", 16, "bold")).pack(pady=15)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Unit:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=10, pady=10)
unit_var = tk.StringVar(value="Select Unit")
ttk.Combobox(frame, textvariable=unit_var,
             values=UNITS, width=40, state="readonly").grid(row=0, column=1)

tk.Label(frame, text="Room:", font=("Segoe UI", 11)).grid(row=1, column=0, padx=10, pady=10)
room_var = tk.StringVar(value="Select Room")
ttk.Combobox(frame, textvariable=room_var,
             values=ROOMS, width=40, state="readonly").grid(row=1, column=1)

tk.Button(root, text="Start Session",
          font=("Segoe UI", 12, "bold"),
          command=start_session).pack(pady=20)

root.mainloop()
