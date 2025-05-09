import cv2
import os
import pickle
import numpy as np
from datetime import datetime
from deepface import DeepFace
from numpy.linalg import norm

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings", "authorized_embeddings.pkl")
CAPTURED_DIR = os.path.join(BASE_DIR, "..", "data", "captured")
THRESHOLD = 0.4  # Strict matching
ALLOWED_IDENTITIES = {"sourjesh", "Dhwani", "Pradipth", "Chiru", "Suchit"}

# Cosine distance function
def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (norm(a) * norm(b))

# Load known embeddings
def load_embeddings(path=EMBEDDINGS_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Embeddings file not found at: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)

# Extract embedding from image
def extract_embedding(image_path):
    try:
        embedding_obj = DeepFace.represent(
            img_path=image_path,
            model_name="Facenet",
            detector_backend="mtcnn",
            enforce_detection=True
        )
        if isinstance(embedding_obj, list) and embedding_obj:
            return np.array(embedding_obj[0]["embedding"])
    except Exception as e:
        print(f"[ERROR] Failed to extract embedding from {image_path}: {e}")
    return None

# Compare captured embedding with known embeddings
def verify_embedding(target_embedding, known_embeddings, threshold=THRESHOLD):
    min_distance = float("inf")
    best_match = None

    print("\n[DEBUG] Comparing with known embeddings:\n")

    for name, embeddings_list in known_embeddings.items():
        for i, known_embedding in enumerate(embeddings_list):
            distance = cosine_distance(target_embedding, np.array(known_embedding))
            print(f"  → Compared with {name} [sample {i+1}]: distance = {round(distance, 4)}")

            if distance < min_distance:
                min_distance = distance
                best_match = name

    if min_distance <= threshold:
        print(f"[INFO] Closest match: {best_match} with distance = {round(min_distance, 4)}")
        return {"status": "authorized", "identity": best_match, "distance": round(min_distance, 4)}
    else:
        print(f"[INFO] Distance {round(min_distance, 4)} exceeds {threshold} → Intruder.")
        return {"status": "intruder", "identity": None, "distance": round(min_distance, 4)}
    
def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("[ERROR] Failed to capture image from webcam.")
        return None

    if not os.path.exists(CAPTURED_DIR):
        os.makedirs(CAPTURED_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_path = os.path.join(CAPTURED_DIR, f"capture_{timestamp}.jpg")
    cv2.imwrite(img_path, frame)
    print(f"[INFO] Image captured and saved to: {img_path}")
    return img_path

# Main logic
def main():
    print("[INFO] Capturing image from webcam...")
    img_path = capture_image()

    if img_path:
        print("[INFO] Extracting face embedding...")
        embedding = extract_embedding(img_path)

        if embedding is not None:
            print("[INFO] Verifying identity...")
            known_embeddings = load_embeddings()
            result = verify_embedding(embedding, known_embeddings)
            result["image_path"] = img_path
            print("[RESULT]", result)
        else:
            print("[ERROR] No face detected or embedding failed.")

if __name__ == "__main__":
    main()
