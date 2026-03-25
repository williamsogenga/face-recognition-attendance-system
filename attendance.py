import cv2
import face_recognition
import os
import sqlite3
from datetime import datetime


def run_attendance(session_id, unit, room, DB_PATH):

    print("Session:", session_id, unit, room)

    path = "faces"

    images = []
    names = []

    for file in os.listdir(path):

        img = cv2.imread(f"{path}/{file}")
        images.append(img)
        names.append(os.path.splitext(file)[0])

    def encode_faces(images):

        encodings = []

        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodings.append(encode)

        return encodings

    known_encodings = encode_faces(images)

    print("Faces Loaded:", names)

    cap = cv2.VideoCapture(0)

    marked = set()

    while True:

        success, frame = cap.read()

        small = cv2.resize(frame, (0,0), None, 0.25, 0.25)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        for encodeFace, faceLoc in zip(encodings, faces):

            matches = face_recognition.compare_faces(known_encodings, encodeFace)
            distances = face_recognition.face_distance(known_encodings, encodeFace)

            matchIndex = distances.argmin()

            if matches[matchIndex]:

                name = names[matchIndex].upper()

                if name not in marked:

                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()

                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    cur.execute("""
                        INSERT INTO attendance (session_id, student_name, marked_at)
                        VALUES (?, ?, ?)
                    """, (session_id, name, now))

                    conn.commit()
                    conn.close()

                    marked.add(name)

                    print("Attendance Marked:", name)

                y1,x2,y2,x1 = faceLoc

                y1*=4
                x2*=4
                y2*=4
                x1*=4

                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(frame,name,(x1,y2+20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,(255,255,255),2)

        cv2.imshow("Face Attendance", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()