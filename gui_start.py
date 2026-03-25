import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "attendance.db")


def start_recognition():

    root.destroy()

    from attendance import run_attendance

    unit = "From Dashboard"
    room = "Auto Room"

    run_attendance(session_id, unit, room, DB_PATH)

# Get session id from Flask
session_id = int(sys.argv[1])
print("SESSION STARTED:", session_id)

# GUI
root = tk.Tk()
root.title("Face Recognition Attendance")
root.geometry("400x200")
root.resizable(False, False)

label = tk.Label(
    root,
    text=f"Session ID: {session_id}",
    font=("Segoe UI", 14, "bold")
)
label.pack(pady=20)

start_btn = tk.Button(
    root,
    text="Start Face Recognition",
    font=("Segoe UI", 13, "bold"),
    bg="#2ecc71",
    fg="white",
    command=start_recognition
)

start_btn.pack(pady=20)

root.mainloop()