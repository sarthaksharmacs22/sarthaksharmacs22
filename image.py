from PIL import Image

def convert_to_rgb(image_path, output_path):
    try:
        with Image.open(image_path) as img:
            print(f"Original image mode: {img.mode}")
            rgb_img = img.convert('RGB')
            print(f"Converted image mode: {rgb_img.mode}")
            rgb_img.save(output_path)
            print(f"Image saved successfully to: {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

convert_to_rgb(r"C:\Users\sarth\OneDrive\Desktop\java\john_face.jpg", r"C:\Users\sarth\OneDrive\Desktop\java\john_face_rgb.jpg")
from PIL import Image

def convert_to_rgb(image_path, output_path):
    try:
        # Open the image
        with Image.open(image_path) as img:
            print(f"Opening image: {image_path}")
            print(f"Image mode: {img.mode}")  # Check original image mode

            # Convert to RGB mode
            rgb_img = img.convert('RGB')
            print(f"Converted image mode: {rgb_img.mode}")

            # Save the image
            rgb_img.save(output_path)
            print(f"Image saved successfully to: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Define paths
input_image_path = r"C:\Users\sarth\OneDrive\Desktop\java\jane_face.jpg"
output_image_path = r"C:\Users\sarth\OneDrive\Desktop\java\jane_face_rgb.jpg"

# Convert and save image
convert_to_rgb(input_image_path, output_image_path)
