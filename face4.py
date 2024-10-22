import cv2
import face_recognition
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
import pandas as pd

# Configuration
EMAIL_ADDRESS = 'sarthak.sharma_cs22@gla.ac.in'
EMAIL_PASSWORD = 'clmx dtnv igcw tmpg'
TO_EMAIL = 'sarthak.sharma_cs22@gla.ac.in'

# Define a class for student management
class Student:
    def __init__(self, name, email, face_encoding):
        self.name = name
        self.email = email
        self.face_encoding = face_encoding
        self.login_time = None
        self.logout_time = None

    def set_login_time(self, login_time):
        self.login_time = login_time

    def set_logout_time(self, logout_time):
        self.logout_time = logout_time

    def get_details(self):
        return f"Name: {self.name}, Email: {self.email}, Login Time: {self.login_time}, Logout Time: {self.logout_time}"

# Define a class for managing the online class
class OnlineClass:
    def __init__(self):
        self.students = {}
        self.attendance = []

    def add_student(self, name, email, face_image_path):
        image = face_recognition.load_image_file(face_image_path)
        face_encoding = face_recognition.face_encodings(image)[0]
        
        student = Student(name, email, face_encoding)
        self.students[name] = student
        print(f"Student {name} added successfully.")

    def send_email(self, subject, body, to_email):
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
                print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def generate_attendance_report(self):
        # Calculate attendance duration
        attendance_data = []
        for student in self.students.values():
            if student.login_time and student.logout_time:
                duration = (student.logout_time - student.login_time).total_seconds() / 60
                attendance_data.append({
                    'Name': student.name,
                    'Login Time': student.login_time,
                    'Logout Time': student.logout_time,
                    'Duration (minutes)': duration
                })

        df = pd.DataFrame(attendance_data)
        df.to_csv('attendance_report.csv', index=False)
        print("Attendance report generated: attendance_report.csv")

    def send_attendance_report(self):
        self.send_email(
            subject="Attendance Report",
            body="Please find the attached attendance report.",
            to_email=TO_EMAIL
        )

    def detect_and_analyze_face(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not access the webcam.")
            return

        print("Webcam opened. Press 'q' to quit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(
                    [student.face_encoding for student in self.students.values()],
                    face_encoding
                )
                if True in matches:
                    matched_student = list(self.students.values())[matches.index(True)]
                    if matched_student.login_time is None:
                        matched_student.set_login_time(datetime.now())
                        print(f"{matched_student.name} logged in at {matched_student.login_time}")
                    else:
                        matched_student.set_logout_time(datetime.now())
                        print(f"{matched_student.name} logged out at {matched_student.logout_time}")
                        self.attendance.append(matched_student)
                        print(f"{matched_student.name} attended for {(matched_student.logout_time - matched_student.login_time).total_seconds() / 60:.2f} minutes.")
                else:
                    print("Face not recognized.")

            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            cv2.imshow('Detected Faces', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# Example Usage
online_class = OnlineClass()
online_class.add_student('John Doe', 'john@example.com', 'john_face.jpg')
online_class.add_student('Jane Smith', 'jane@example.com', 'jane_face.jpg')
online_class.detect_and_analyze_face()
online_class.generate_attendance_report()
online_class.send_attendance_report()
