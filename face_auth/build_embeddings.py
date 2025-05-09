import os
import uuid
import cv2
import pickle
import numpy as np
from datetime import datetime
from deepface import DeepFace

# Constants
EMBEDDINGS_PATH = "data/embeddings/authorized_embeddings.pkl"
CAPTURED_DIR = "data/captured"
MODEL_NAME = "Facenet"
ENFORCE_DETECTION = False
DISTANCE_THRESHOLD = 0.4

def capture_image():
    print("[INFO] Accessing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Camera could not be opened.")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise Exception("Failed to capture image.")

    os.makedirs(CAPTURED_DIR, exist_ok=True)
    image_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
    image_path = os.path.join(CAPTURED_DIR, image_name)
    cv2.imwrite(image_path, frame)
    print(f"[INFO] Image captured and saved to: {image_path}")
    return image_path

def extract_embedding(image_path):
    print("[INFO] Extracting face embedding from captured image...")
    try:
        embedding_obj = DeepFace.represent(
            img_path=image_path,
            model_name=MODEL_NAME,
            enforce_detection=ENFORCE_DETECTION
        )
        return np.array(embedding_obj[0]["embedding"])
    except Exception as e:
        raise Exception(f"Failed to extract embedding: {e}")

def load_embeddings():
    print(f"[INFO] Loading known embeddings from: {EMBEDDINGS_PATH}")
    if not os.path.exists(EMBEDDINGS_PATH):
        raise FileNotFoundError(f"Embeddings file not found at: {EMBEDDINGS_PATH}")
    
    with open(EMBEDDINGS_PATH, "rb") as f:
        embeddings_db = pickle.load(f)

    return embeddings_db

def verify_identity(input_embedding, embeddings_db):
    print("[INFO] Verifying identity...")
    best_match = None
    best_distance = float("inf")

    for name, embeddings in embeddings_db.items():
        for i, stored_embedding in enumerate(embeddings):
            distance = np.linalg.norm(input_embedding - stored_embedding)
            print(f"[DEBUG] Compared with {name} [sample {i+1}]: distance = {distance:.4f}")
            if distance < best_distance:
                best_distance = distance
                best_match = name

    if best_distance < DISTANCE_THRESHOLD:
        return "verified", best_match, best_distance
    else:
        return "unverified", "unknown", best_distance

def main():
    try:
        image_path = capture_image()
        embedding = extract_embedding(image_path)
        embeddings_db = load_embeddings()
        status, identity, best_distance = verify_identity(embedding, embeddings_db)

        result = {
            "status": status,
            "identity": identity,
            "distance": best_distance,
            "image_path": image_path,
        }

        print(f"[RESULT] {result}")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
