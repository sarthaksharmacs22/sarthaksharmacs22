import cv2
import face_recognition
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta

class Student:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.face_encoding = None
        self.login_time = None
        self.logout_time = None
        self.total_attendance_duration = 0.0  # Track total attendance time
        self.current_session_duration = 0.0  # Track duration of current session

    def set_face_encoding(self, encoding):
        self.face_encoding = encoding

    def start_session(self):
        self.login_time = datetime.now()
        self.logout_time = None  # Clear the previous logout time
        print(f"{self.name} logged in at {self.login_time}")

    def end_session(self):
        self.logout_time = datetime.now()
        if self.login_time:
            session_duration = (self.logout_time - self.login_time).total_seconds() / 60
            self.total_attendance_duration += session_duration
            self.current_session_duration = session_duration
            print(f"{self.name} logged out at {self.logout_time}. Session duration: {round(session_duration, 2)} minutes.")
        else:
            self.current_session_duration = 0

        self.login_time = None  # Reset login time for next session

    def get_details(self):
        return {
            'Name': self.name,
            'Email': self.email,
            'Login Time': self.login_time,
            'Logout Time': self.logout_time,
            'Total Attendance (minutes)': round(self.total_attendance_duration, 2)  # Total duration across sessions
        }

class OnlineClass:
    def __init__(self):
        self.students = {}
        self.email_sent = False
        self.grace_period = 30  # Grace period of 30 seconds

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

            current_time = datetime.now()

            # Process each detected face in the frame
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
                else:
                    # Check for logout due to grace period expiry
                    for student in list(logged_in_students.values()):
                        if current_time - student.login_time > timedelta(seconds=self.grace_period):
                            student.end_session()
                            logged_in_students.pop(student.name, None)
                            self.email_sent = False

            # Draw a rectangle around detected faces
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            cv2.imshow('Detected Faces', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.generate_attendance_report()

    def generate_attendance_report(self):
        # Collect details for all students and save to CSV
        data = [student.get_details() for student in self.students.values()]
        df = pd.DataFrame(data)
        df.to_csv('attendance_report.csv', index=False)
        print("Attendance report generated: attendance_report.csv")
        
        # Display attendance in the terminal
        print(df)

        # Send email if not sent
        if not self.email_sent:
            self.send_email_with_attachment('attendance_report.csv')
            self.email_sent = True

    def send_email_with_attachment(self, attachment_path):
        from_email = 'sarthak.sharma_cs22@gla.ac.in'
        to_email = 'sarthak.sharma_cs22@gla.ac.in'
        password = 'rpoj yaxc elsz flld'  # Gmail app password

        subject = 'Attendance Report'
        body = 'Please find attached the attendance report.'

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_path, 'rb') as attachment:
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
