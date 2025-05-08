import os
import pickle
import numpy as np
from deepface import DeepFace
from deepface.commons import functions

# Updated paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings", "authorized_embeddings.pkl")
CAPTURED_DIR = os.path.join(BASE_DIR, "..", "data", "captured")
THRESHOLD = 0.6  # Euclidean distance threshold for FaceNet

def load_embeddings(path=EMBEDDINGS_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Embeddings file not found at: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)

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

def verify_embedding(target_embedding, known_embeddings, threshold=THRESHOLD):
    best_match = None
    min_distance = float("inf")

    for name, known_embedding in known_embeddings.items():
        distance = np.linalg.norm(target_embedding - known_embedding)
        if distance < min_distance:
            min_distance = distance
            best_match = name

    if min_distance <= threshold:
        return {"status": "authorized", "identity": best_match, "distance": round(min_distance, 4)}
    else:
        return {"status": "intruder", "identity": None, "distance": round(min_distance, 4)}

def verify_latest_image():
    try:
        images = sorted(
            [f for f in os.listdir(CAPTURED_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
            key=lambda x: os.path.getmtime(os.path.join(CAPTURED_DIR, x)),
            reverse=True
        )
        if not images:
            return {"status": "failed", "reason": "No captured images found."}

        latest_image_path = os.path.join(CAPTURED_DIR, images[0])
        print(f"[INFO] Verifying latest image: {latest_image_path}")

        known_embeddings = load_embeddings()
        target_embedding = extract_embedding(latest_image_path)

        if target_embedding is None:
            return {"status": "failed", "reason": "Face detection or embedding failed."}

        result = verify_embedding(target_embedding, known_embeddings)
        result["image_path"] = latest_image_path
        return result

    except Exception as e:
        return {"status": "failed", "reason": str(e)}

if __name__ == "__main__":
    output = verify_latest_image()
    print(output)
