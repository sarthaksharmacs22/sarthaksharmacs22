import cv2

def test_camera():
    cap = cv2.VideoCapture(0)  # Try changing 0 to 1 if the camera is not opening

    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    print("Webcam opened. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        cv2.imshow('Camera Test', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

test_camera()
