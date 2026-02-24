import cv2
import numpy as np
import face_recognition
import os
import sqlite3
from datetime import datetime

# ---------------- CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_PATH = os.path.join(BASE_DIR, "Images_Attendance")
MATCH_THRESHOLD = 0.45   # stricter threshold


# ---------------- LOAD MULTIPLE ENCODINGS PER PERSON ----------------
def load_known_faces():
    known_faces = {}

    if not os.path.exists(IMAGES_PATH):
        raise FileNotFoundError("Images folder missing")

    for file in os.listdir(IMAGES_PATH):
        if file.startswith("."):
            continue

        path = os.path.join(IMAGES_PATH, file)
        img = cv2.imread(path)

        if img is None:
            continue

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)

        if len(encodings) == 0:
            print(f"Skipping {file} (no face)")
            continue

        # Extract name before underscore
        name = os.path.splitext(file)[0].split("_")[0].upper()

        if name not in known_faces:
            known_faces[name] = []

        known_faces[name].append(encodings[0])

    if len(known_faces) == 0:
        raise RuntimeError("No faces loaded")

    print("Loaded faces:", {k: len(v) for k, v in known_faces.items()})
    return known_faces


# ---------------- DATABASE FUNCTION ----------------
def mark_attendance_sqlite(db_path, session_id, name):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT 1 FROM attendance
        WHERE session_id=? AND name=?
    """, (session_id, name))

    if cur.fetchone() is None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO attendance(session_id,name,marked_at)
            VALUES(?,?,?)
        """, (session_id, name, now))
        conn.commit()

    conn.close()


# ---------------- IMPROVED MATCHING LOGIC ----------------
def find_best_match(known_faces, face_encoding):
    best_name = "UNKNOWN"
    best_distance = 1.0

    for name, enc_list in known_faces.items():
        distances = face_recognition.face_distance(enc_list, face_encoding)
        avg_distance = np.mean(distances)

        if avg_distance < best_distance:
            best_distance = avg_distance
            best_name = name

    if best_distance > MATCH_THRESHOLD:
        return "UNKNOWN", best_distance

    return best_name, best_distance


# ---------------- MAIN CAMERA FUNCTION ----------------
def run_attendance(session_id, unit, room, db_path):
    known_faces = load_known_faces()
    print(f"Running session: {unit} | {room}")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam")

    while True:
        ok, img = cap.read()
        if not ok:
            continue

        small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(small)
        face_encodings = face_recognition.face_encodings(small, face_locations)

        for encoding, loc in zip(face_encodings, face_locations):
            name, distance = find_best_match(known_faces, encoding)

            y1, x2, y2, x1 = loc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

            if name != "UNKNOWN":
                mark_attendance_sqlite(db_path, session_id, name)
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)

            label = f"{name} ({distance:.2f})"

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.rectangle(img, (x1, y2-35), (x2, y2), color, cv2.FILLED)
            cv2.putText(img, label, (x1+6, y2-6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        cv2.imshow(f"Attendance | {unit}", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
