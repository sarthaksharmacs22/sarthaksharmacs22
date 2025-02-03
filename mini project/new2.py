import smtplib
import cv2
import face_recognition
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from deepface import DeepFace
from collections import Counter

print("Script started successfully!")

class Student:
    def __init__(self, roll_number, name, student_id, face_encoding):
        self.roll_number = roll_number
        self.name = name
        self.student_id = student_id
        self.login_time = None
        self.logout_time = None
        self.attendance_duration = 0
        self.face_encoding = face_encoding
        self.is_logged_in = False
        self.last_seen = None  # Tracks the last time the student was detected
        self.emotion_history = []

    def login(self):
        if not self.is_logged_in:
            self.login_time = datetime.now()
            self.is_logged_in = True
            self.last_seen = self.login_time  # Initialize last seen time
            print(f"{self.name} logged in at {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def logout(self):
        if self.is_logged_in:
            self.logout_time = datetime.now()
            duration = (self.logout_time - self.login_time).total_seconds() / 60  # Convert to minutes
            self.attendance_duration += duration
            self.is_logged_in = False
            print(f"{self.name} logged out at {self.logout_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{self.name} attended for {duration:.2f} minutes.")
        else:
            print(f"{self.name} was not logged in.")
        
    def get_stable_emotion(self, new_emotion):
        self.emotion_history.append(new_emotion)
        if len(self.emotion_history) > 5:
            self.emotion_history.pop(0)
        return Counter(self.emotion_history).most_common(1)[0][0]
    
    def get_details(self):
        dominant_emotion = self.get_stable_emotion('neutral')  # Default to neutral if no emotions detected
        return {
            'Roll Number': self.roll_number,
            'Name': self.name,
            'Student ID': self.student_id,
            'Login Time': self.login_time.strftime('%Y-%m-%d %H:%M:%S') if self.login_time else 'N/A',
            'Logout Time': self.logout_time.strftime('%Y-%m-%d %H:%M:%S') if self.logout_time else 'N/A',
            'Attendance Duration (minutes)': round(self.attendance_duration, 2),
            'Dominant Emotion': dominant_emotion
        }

class OnlineClass:
    def __init__(self):
        self.students = {}
        self.attendance_records = pd.DataFrame()
        self.grace_period = 30  # Grace period in seconds

    def add_student(self, roll_number, name, student_id, face_image_path):
        face_encoding = self.get_face_encoding(face_image_path)
        if face_encoding is None:
            print(f"Face not detected in the image for {name}.")
            return
        if student_id in self.students:
            print(f"Student with ID {student_id} already exists.")
        else:
            student = Student(roll_number, name, student_id, face_encoding)
            self.students[student_id] = student
            print(f"Student {name} added successfully.")
    
    def get_face_encoding(self, image_path):
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            return face_encodings[0]
        else:
            return None
    
    def detect_and_analyze_face(self):
        video_capture = cv2.VideoCapture(0)
        logged_in_students = {}

        print("Starting face detection. Press 'q' to quit.")
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to grab frame")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            current_time = datetime.now()

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(
                    [student.face_encoding for student in self.students.values()],
                    face_encoding
                )
                if True in matches:
                    matched_student = list(self.students.values())[matches.index(True)]
                    if not matched_student.is_logged_in:
                        matched_student.login()
                    matched_student.last_seen = current_time
                    logged_in_students[matched_student.student_id] = matched_student

                    # Emotion Analysis
                    face_roi = frame[top:bottom, left:right]
                    try:
                        analysis = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                        dominant_emotion = analysis['dominant_emotion']
                        matched_student.get_stable_emotion(dominant_emotion)
                        print(f"{matched_student.name} emotion: {dominant_emotion}")
                    except Exception as e:
                        print("DeepFace analysis error:", e)

            for student_id, student in list(logged_in_students.items()):
                if current_time - student.last_seen > timedelta(seconds=self.grace_period):
                    student.logout()
                    logged_in_students.pop(student_id)

            # Draw rectangles around detected faces
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            cv2.imshow("Detected Faces", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Logout any remaining logged in students
        for student in logged_in_students.values():
            student.logout()

        video_capture.release()
        cv2.destroyAllWindows()

    def save_attendance_to_excel(self, file_name):
        records = [student.get_details() for student in self.students.values()]
        self.attendance_records = pd.DataFrame(records)
        self.attendance_records.to_excel(file_name, index=False)
        print(f"Attendance saved to {file_name}")

    def send_email_with_attachment(self, recipient_email, file_name):
        sender_email = "sarthak.sharma_cs22@gla.ac.in"
        password = "rpoj yaxc elsz flld"  # Replace with your actual password or use environment variables
        subject = "Attendance Report"
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText("Please find the attached attendance report.", 'plain'))
        with open(file_name, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_name)}")
            msg.attach(part)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
            print(f"Email sent to {recipient_email}")

if __name__ == '__main__':
    online_class = OnlineClass()

    # Add student(s) to the online class.
    online_class.add_student(
        roll_number=2215001595,
        name="Sarthak Sharma",
        student_id="Sarthak Sharma",
        face_image_path="sarthak_face.jpg" 
    )
    
    # Start the face detection and emotion analysis process.
    online_class.detect_and_analyze_face()

    # Save the attendance report to an Excel file.
    attendance_file = "attendance_report.xlsx"
    online_class.save_attendance_to_excel(attendance_file)

    # Send the attendance report via email.
    # Replace with the recipient's email address.
    online_class.send_email_with_attachment(
        recipient_email="sarthak.sharma_cs22@gla.ac.in",
        file_name=attendance_file
    )
    
    # Keep the console open until you press Enter.
    input("Press Enter to exit...")
