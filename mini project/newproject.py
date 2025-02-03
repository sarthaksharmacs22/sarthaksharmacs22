import cv2
import pandas as pd
from datetime import datetime
from deepface import DeepFace

# Initialize attendance DataFrame
attendance_data = pd.DataFrame(columns=["Name", "Login Time", "Logout Time", "Attendance Duration", "Dominant Emotion"])

# Face cascade for detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Known users' data (pre-stored images for recognition)
known_users = {
    "Sarthak_Sharmaq": "sarthak_face.jpg",  # Add image paths for known users
}

# Attendance tracking variables
attendance_log = {}
grace_period_seconds = 30
logout_threshold_seconds = 15

def calculate_duration(login_time, logout_time):
    """Calculate attendance duration in minutes."""
    fmt = "%Y-%m-%d %H:%M:%S"
    duration = datetime.strptime(logout_time, fmt) - datetime.strptime(login_time, fmt)
    return max(duration.total_seconds() // 60, 0)  # Convert to minutes

def recognize_face_and_analyze_emotion(frame, faces):
    """Recognize faces and analyze emotions."""
    global attendance_log
    for (x, y, w, h) in faces:
        face_roi = frame[y:y + h, x:x + w]
        try:
            # Perform emotion analysis
            analysis = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
            
            # Check if the result is a list (DeepFace can return multiple faces)
            if isinstance(analysis, list):
                analysis = analysis[0]  # Get the first face if there are multiple
            dominant_emotion = analysis.get('dominant_emotion', 'Unknown')

            # Perform face recognition
            recognized_name = "Unknown"
            for user_name, user_image in known_users.items():
                match = DeepFace.verify(face_roi, user_image, enforce_detection=False)
                if match.get("verified", False):
                    recognized_name = user_name
                    break

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Log attendance
            if recognized_name != "Unknown":
                if recognized_name not in attendance_log:
                    attendance_log[recognized_name] = {
                        "Login Time": now,
                        "Last Seen": now,
                        "Dominant Emotion": dominant_emotion
                    }
                    print(f"[INFO] {recognized_name} logged in at {now} with emotion: {dominant_emotion}")
                else:
                    # Update last seen and emotion
                    attendance_log[recognized_name]["Last Seen"] = now
                    attendance_log[recognized_name]["Dominant Emotion"] = dominant_emotion

        except Exception as e:
            print(f"[ERROR] Emotion/Face recognition failed: {e}")

def update_attendance_sheet():
    """Save attendance log to Excel."""
    global attendance_log, attendance_data
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for name, details in list(attendance_log.items()):
        # Calculate logout time and attendance duration
        logout_time = details["Last Seen"]
        login_time = details["Login Time"]
        duration_minutes = calculate_duration(login_time, logout_time)

        # Check if user is inactive for more than the logout threshold
        time_since_last_seen = (datetime.strptime(now, "%Y-%m-%d %H:%M:%S") - 
                                datetime.strptime(logout_time, "%Y-%m-%d %H:%M:%S")).total_seconds()
        if time_since_last_seen > logout_threshold_seconds:
            # Log out the user
            attendance_data = pd.concat([attendance_data, pd.DataFrame([{
                "Name": name,
                "Login Time": login_time,
                "Logout Time": logout_time,
                "Attendance Duration": f"{duration_minutes} minutes",
                "Dominant Emotion": details["Dominant Emotion"]
            }])], ignore_index=True)
            del attendance_log[name]
            print(f"[INFO] {name} logged out due to inactivity.")

    # Save attendance to Excel
    attendance_data.to_excel("attendance_with_emotions.xlsx", index=False)
    print("[INFO] Attendance saved to 'attendance_with_emotions.xlsx'.")

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Recognize faces and analyze emotions
    recognize_face_and_analyze_emotion(frame, faces)

    # Draw rectangles around faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Display the video feed
    cv2.imshow("Facial - Attendance with Emotion Analysis", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Save final attendance to Excel
update_attendance_sheet()
