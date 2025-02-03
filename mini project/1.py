from deepface import DeepFace

# Analyze an image
result = DeepFace.analyze(img_path="sarthak_face.jpg", actions=['age', 'gender', 'emotion', 'race'])

print("Analysis Results:")
print(result)
