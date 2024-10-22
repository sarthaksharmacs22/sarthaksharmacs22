from PIL import Image
import face_recognition

def get_face_encoding(image_path):
    try:
        with Image.open(image_path) as img:
            print(f"Opening image: {image_path}")
            print(f"Image mode: {img.mode}")  # Should print "RGB"
            image = face_recognition.load_image_file(image_path)
            print("Image loaded successfully.")
            face_encodings = face_recognition.face_encodings(image)
            print(f"Number of face encodings found: {len(face_encodings)}")
            return face_encodings
    except Exception as e:
        print(f"An error occurred: {e}")

get_face_encoding(r"C:\Users\sarth\OneDrive\Desktop\java\john_face_rgb.jpg")
def get_face_encoding(image_path):
    try:
        with Image.open(image_path) as img:
            print(f"Opening image: {image_path}")
            print(f"Image mode: {img.mode}")  # Should print "RGB"
            image = face_recognition.load_image_file(image_path)
            print("Image loaded successfully.")
            face_encodings = face_recognition.face_encodings(image)
            print(f"Number of face encodings found: {len(face_encodings)}")
            return face_encodings
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function to test
face_encodings = get_face_encoding(r"C:\Users\sarth\OneDrive\Desktop\java\john_face_rgb.jpg")
print("Face encodings:", face_encodings)
