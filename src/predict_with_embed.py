import os
import pickle
import numpy as np
from deepface import DeepFace
from src.camera import capture_images
from datetime import datetime
from scipy.spatial.distance import cosine

# Constants
MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "mtcnn"
ENFORCE_DETECTION = False  # For inference, allow fallback even if face not found
THRESHOLD = 0.4  # Cosine distance threshold
EMBEDDINGS_PATH = os.path.join("face_auth", "embeddings", "authorized_embeddings.pkl")

def load_model():
    print("[INFO] Loading DeepFace model...")
    model = DeepFace.build_model(MODEL_NAME)
    print("[INFO] Model loaded successfully.")
    return model

def load_embeddings(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ERROR] Embeddings file not found: {path}")
    with open(path, "rb") as f:
        data = pickle.load(f)
    print(f"[INFO] Loaded embeddings for {len(data)} authorized people.")
    return data

def get_embedding(model, image_path):
    try:
        reps = DeepFace.represent(
            img_path=image_path,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=ENFORCE_DETECTION
        )
        if isinstance(reps, list) and reps:
            return np.array(reps[0]["embedding"])
    except Exception as e:
        print(f"[WARN] Failed to process {image_path}: {e}")
    return None

def compare_embedding(embedding, embeddings_db):
    best_match = None
    best_score = float("inf")

    for person, embeddings in embeddings_db.items():
        for ref_embedding in embeddings:
            score = cosine(embedding, ref_embedding)
            if score < best_score:
                best_score = score
                best_match = person
    print(f"[DEBUG] Best match: {best_match}, score: {best_score}")
    return best_match, best_score

def verify_captured_images(image_paths, model, embeddings_db):
    print(f"[INFO] Starting verification on {len(image_paths)} images.")
    results = []

    for img_path in image_paths:
        print(f"\n[INFO] Processing image: {img_path}")
        embedding = get_embedding(model, img_path)

        if embedding is None:
            print("[RESULT] ❌ Face not detected or embedding failed.")
            results.append(("Unknown", img_path, None))
            continue

        name, score = compare_embedding(embedding, embeddings_db)

        if score < THRESHOLD:
            print(f"[RESULT] ✅ Authorized person: {name} (cosine distance: {score:.4f})")
            results.append((name, img_path, score))
        else:
            print(f"[RESULT] 🚨 Intruder detected! (closest: {name}, distance: {score:.4f})")
            results.append(("Intruder", img_path, score))

    return results

def save_results(results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"verification_results_{timestamp}.txt"
    with open(result_file, "w") as f:
        for name, path, score in results:
            if score is not None:
                f.write(f"{name}: {os.path.basename(path)} (score: {score:.4f})\n")
            else:
                f.write(f"{name}: {os.path.basename(path)} (no face detected)\n")
    print(f"[INFO] Results saved to {result_file}")

if __name__ == "__main__":
    print("\n[INFO] Starting prediction workflow...\n")
    
    try:
        model = load_model()
        embeddings_db = load_embeddings(EMBEDDINGS_PATH)
    except Exception as e:
        print(f"[ERROR] {e}")
        exit(1)

    captured_paths = capture_images(num_images=5, delay=2)
    
    if not captured_paths:
        print("[ERROR] No images captured.")
    else:
        results = verify_captured_images(captured_paths, model, embeddings_db)
        
        print("\n[SUMMARY]")
        for name, path, score in results:
            if score is not None:
                print(f"- {name}: {os.path.basename(path)} (score: {score:.4f})")
            else:
                print(f"- {name}: {os.path.basename(path)} (no face detected)")
        
        save_results(results)
