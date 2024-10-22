from datetime import datetime
import cv2
import face_recognition

class Student:
    def __init__(self, name, email, login_id, face_encoding):
        self.name = name
        self.email = email
        self.login_id = login_id
        self.login_time = None
        self.logout_time = None
        self.attendance_duration = 0
        self.face_encoding = face_encoding
        self.is_logged_in = False
    
    def login(self):
        if not self.is_logged_in:
            self.login_time = datetime.now()
            self.is_logged_in = True
            print(f"{self.name} logged in at {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def logout(self):
        if self.is_logged_in:
            self.logout_time = datetime.now()
            duration = (self.logout_time - self.login_time).total_seconds() / 60  # convert to minutes
            self.attendance_duration += duration
            self.is_logged_in = False
            print(f"{self.name} logged out at {self.logout_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{self.name} attended for {duration:.2f} minutes.")
        else:
            print(f"{self.name} was not logged in.")
        
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
        # Open the webcam
        video_capture = cv2.VideoCapture(0)

        logged_in_students = set()

        while True:
            # Capture a single frame of video
            ret, frame = video_capture.read()

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(
                    [student.face_encoding for student in self.students.values()], 
                    face_encoding
                )
                if True in matches:
                    matched_student = list(self.students.values())[matches.index(True)]
                    matched_student.login()  # Log in the student if not already logged in
                    logged_in_students.add(matched_student.login_id)  # Track logged-in students

                else:
                    print("Face not recognized.")
            
            # Display the resulting image with the detected face
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            cv2.imshow("Detected Faces", frame)

            # Press 'q' on the keyboard to exit the webcam view
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Log out all logged-in students when exiting
        for login_id in logged_in_students:
            self.student_logout(login_id)

        # Release the webcam and close windows
        video_capture.release()
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    online_class = OnlineClass()
    
    # Add students with their face image
    online_class.add_student("John Doe", "john@example.com", "john123", "john_face.jpg")
    online_class.add_student("Jane Smith", "jane@example.com", "jane123", "jane_face.jpg")
    
    # Detect and analyze face using the webcam
    online_class.detect_and_analyze_face()
    
    # Get student details after the session
    online_class.get_student_details("john123")
    online_class.get_student_details("jane123")
 