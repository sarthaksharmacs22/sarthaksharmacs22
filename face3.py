from datetime import datetime
import cv2
import face_recognition
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import numpy as np
import pandas as pd

class Student:
    def __init__(self, name, email, login_id, face_encoding):
        self.name = name
        self.email = email
        self.login_id = login_id
        self.login_time = None
        self.logout_time = None
        self.attendance_duration = 0
        self.face_encoding = face_encoding
    
    def login(self):
        self.login_time = datetime.now()
        print(f"{self.name} logged in at {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def logout(self):
        if self.login_time is None:
            print(f"{self.name} hasn't logged in yet!")
            return
        self.logout_time = datetime.now()
        duration = (self.logout_time - self.login_time).total_seconds() / 60  # convert to minutes
        self.attendance_duration += duration
        print(f"{self.name} logged out at {self.logout_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{self.name} attended for {duration:.2f} minutes.")
        
    def get_details(self):
        return {
            'Name': self.name,
            'Email': self.email,
            'Login ID': self.login_id,
            'Total Attendance (minutes)': self.attendance_duration
        }

class OnlineClass:
    def __init__(self):
        self.students = {}
        self.email_sent = False
    
    def add_student(self, name, email, login_id, face_image_path):
        face_encoding = self.get_face_encoding(face_image_path)
        if face_encoding is None:
            print(f"Face not detected in the image for {name}.")
            return
        if login_id in self.students:
            print(f"Student with Login ID {login_id} already exists.")
        else:
            student = Student(name, email, login_id, face_encoding)
            self.students[login_id] = student
            print(f"Student {name} added successfully.")
    
    def get_face_encoding(self, image_path):
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            return face_encodings[0]
        else:
            return None
    
    def student_login(self, login_id):
        if login_id in self.students:
            self.students[login_id].login()
        else:
            print(f"No student found with Login ID {login_id}.")
    
    def student_logout(self, login_id):
        if login_id in self.students:
            self.students[login_id].logout()
        else:
            print(f"No student found with Login ID {login_id}.")
    
    def get_student_details(self, login_id):
        if login_id in self.students:
            details = self.students[login_id].get_details()
            for key, value in details.items():
                print(f"{key}: {value}")
        else:
            print(f"No student found with Login ID {login_id}.")
    
    def get_all_students(self):
        return [student.get_details() for student in self.students.values()]
    
    def detect_and_analyze_face(self):
        # Initialize the webcam
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            print("Error: Could not open webcam.")
            return
        
        detected_faces = set()

        while True:
            # Capture frame-by-frame
            ret, frame = video_capture.read()
            if not ret:
                break

            # Convert the image from BGR to RGB
            rgb_frame = frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(
                    [student.face_encoding for student in self.students.values()], 
                    face_encoding
                )
                if True in matches:
                    matched_student = list(self.students.values())[matches.index(True)]
                    print(f"Face matched with {matched_student.name}.")
                    if matched_student.login_id not in detected_faces:
                        detected_faces.add(matched_student.login_id)
                        self.student_login(matched_student.login_id)
                else:
                    print("Face not recognized.")

            # Display the resulting frame with the detected face
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            cv2.imshow('Video', frame)

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything is done, release the capture and destroy the windows
        video_capture.release()
        cv2.destroyAllWindows()

    def send_email(self, to_email, subject, body):
        sender_email = "your_email@gmail.com"
        sender_password = "clmx dtnv igcw tmpg"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

    def send_email_with_attachment(self, to_email, subject, body, attachment_path):
        sender_email = "your_email@gmail.com"
        sender_password = "your_app_password"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {attachment_path}')
                msg.attach(part)
        except Exception as e:
            print(f"Failed to attach file: {str(e)}")
            return

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                print(f"Attendance report sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

# Example usage
if __name__ == "__main__":
    online_class = OnlineClass()
    
    # Add students with their face image
    online_class.add_student("John Doe", "john@example.com", "john123", "john_face.jpg")
    online_class.add_student("Jane Smith", "jane@example.com", "jane123", "jane_face.jpg")
    
    # Open webcam and detect faces
    online_class.detect_and_analyze_face()
    
    # Generate attendance report and send email
    attendance_data = online_class.get_all_students()
    df = pd.DataFrame(attendance_data)
    df.to_csv('attendance_report.csv', index=False)
    print("Attendance report generated: attendance_report.csv")
    online_class.send_email_with_attachment("sarthak.sharma_cs22@gla.ac.in", "Attendance Report", "Please find the attached attendance report.", "attendance_report.csv")
