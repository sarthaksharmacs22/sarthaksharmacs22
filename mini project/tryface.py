import cv2
import face_recognition
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import numpy as np

class OnlineClass:
    def __init__(self):
        self.students = {}
        self.attendance_records = pd.DataFrame(columns=["Roll No", "Name", "Student ID", "Login Time", "Logout Time", "Total Duration"])
        self.last_detection_time = None
        self.logged_in = False
        self.current_student = None
        self.grace_period = timedelta(seconds=30)  # 30 seconds grace period

    def add_student(self, name, email, student_id, face_image_path):
        roll_no = len(self.students) + 1
        self.students[roll_no] = {
            "Name": name,
            "Email": email,
            "Student ID": student_id,
            "Face Image": face_image_path,
            "Encoding": self.get_face_encoding(face_image_path)
        }
        print(f"Student {name} added successfully.")

    def get_face_encoding(self, face_image_path):
        image = face_recognition.load_image_file(face_image_path)
        encoding = face_recognition.face_encodings(image)
        return encoding[0] if encoding else None

    def send_email(self, recipient_email, subject, body):
        sender_email = "sarthak.sharma_cs22@gla.ac.in"
        password = "rpoj yaxc elsz flld"  # Your app-specific password

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent to {recipient_email} at {datetime.now()}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def detect_and_analyze_face(self):
        video_capture = cv2.VideoCapture(0)
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to grab frame")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if face_encodings:
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    matches = face_recognition.compare_faces(
                        [student['Encoding'] for student in self.students.values()], face_encoding)
                    face_distances = face_recognition.face_distance(
                        [student['Encoding'] for student in self.students.values()], face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        roll_no = best_match_index + 1
                        student = self.students[roll_no]

                        # Check if the student is already logged in
                        if not self.logged_in or self.current_student != roll_no:
                            self.current_student = roll_no
                            self.login_student(student)

                        self.last_detection_time = datetime.now()
                        break
            else:
                # Log out if no face detected and grace period expired
                if self.logged_in and (datetime.now() - self.last_detection_time) > self.grace_period:
                    self.logout_student(self.current_student)

            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

    def login_student(self, student):
        self.logged_in = True
        self.current_student_info = student  # Store current student info for logout
        login_time = datetime.now()
        self.last_detection_time = login_time
        print(f"{student['Name']} logged in at {login_time}")

    def logout_student(self, roll_no):
        if self.logged_in:
            self.logged_in = False
            logout_time = datetime.now()
            duration = (logout_time - self.last_detection_time).total_seconds() / 60
            record = {
                "Roll No": roll_no,
                "Name": self.students[roll_no]['Name'],
                "Student ID": self.students[roll_no]['Student ID'],
                "Login Time": self.last_detection_time,
                "Logout Time": logout_time,
                "Total Duration": duration
            }
            self.attendance_records = pd.concat([self.attendance_records, pd.DataFrame([record])], ignore_index=True)
            print(f"{self.students[roll_no]['Name']} logged out at {logout_time}")

            # Send email using the stored current student info
            self.send_email(self.current_student_info['Email'], "Attendance Notification",
                            f"Dear {self.current_student_info['Name']},\n\nYou have attended for {duration:.2f} minutes.\n\nBest regards,\nOnline Class System")
            self.save_attendance_to_excel("attendance.xlsx")

    def save_attendance_to_excel(self, file_name):
        self.attendance_records.to_excel(file_name, index=False)
        print(f"Attendance saved to {file_name}")

if __name__ == "__main__":
    online_class = OnlineClass()
    online_class.add_student("John Doe", "sarthak.sharma_cs22@gla.ac.in", "john123", "john_face.jpg")
    online_class.detect_and_analyze_face()
