import cv2
import face_recognition
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from time import sleep

class Student:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.face_encoding = None
        self.login_time = None
        self.logout_time = None
        self.attendance_duration = 0.0

    def set_face_encoding(self, encoding):
        self.face_encoding = encoding

    def start_session(self):
        self.login_time = datetime.now()

    def end_session(self):
        self.logout_time = datetime.now()
        if self.login_time:
            self.attendance_duration += (self.logout_time - self.login_time).total_seconds() / 60
        self.login_time = None

    def get_details(self):
        return {
            'Name': self.name,
            'Email': self.email,
            'Login Time': self.login_time,
            'Logout Time': self.logout_time,
            'Duration (minutes)': self.attendance_duration
        }

class OnlineClass:
    def __init__(self):
        self.students = {}
        self.email_sent = False

    def add_student(self, name, email, image_path):
        student = Student(name, email)
        self.students[name] = student
        student_image = face_recognition.load_image_file(image_path)
        student_encoding = face_recognition.face_encodings(student_image)[0]
        student.set_face_encoding(student_encoding)
        print(f"Student {name} added successfully.")

    def detect_and_analyze_face(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not access the webcam.")
            return

        print("Webcam opened. Press 'q' to quit.")
        logged_in_students = {}

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
                    if matched_student.name not in logged_in_students:
                        matched_student.start_session()
                        logged_in_students[matched_student.name] = matched_student
                        print(f"{matched_student.name} logged in at {datetime.now()}.")
                else:
                    for student in list(logged_in_students.values()):
                        student.end_session()
                        print(f"{student.name} logged out at {datetime.now()}.")
                        self.email_sent = False
                    logged_in_students.clear()

            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            cv2.imshow('Detected Faces', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.generate_attendance_report()

    def generate_attendance_report(self):
        data = [student.get_details() for student in self.students.values()]
        df = pd.DataFrame(data)
        df.to_csv('attendance_report.csv', index=False)
        print("Attendance report generated: attendance_report.csv")
        if not self.email_sent:
            self.send_email_with_attachment('attendance_report.csv')
            self.email_sent = True

    def send_email_with_attachment(self, attachment_path):
        from_email = 'sarthak.sharma_cs22@gla.ac.in'
        to_email = 'sarthak.sharma_cs22@gla.ac.in'
        password = 'clmx dtnv igcw tmpg'

        subject = 'Attendance Report'
        body = 'Please find attached the attendance report.'

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_path, 'rb') as attachment:
            from email.mime.base import MIMEBase
            from email import encoders
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment_path}')
            msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            print(f"Email sent to {to_email}")

if __name__ == "__main__":
    online_class = OnlineClass()
    online_class.add_student('John Doe', 'john@example.com', 'john_face.jpg')
    online_class.add_student('Jane Smith', 'jane@example.com', 'jane_face.jpg')
    online_class.detect_and_analyze_face()
