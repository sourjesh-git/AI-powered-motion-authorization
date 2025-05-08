import os
import pickle
from tqdm import tqdm
from deepface import DeepFace
from deepface.commons import functions

# Constants
MODEL_NAME = "Facenet"
TARGET_SIZE = (160, 160)
ENFORCE_DETECTION = True
DETECTOR_BACKEND = "mtcnn"  # More reliable than opencv
KNOWN_FACES_DIR = os.path.join(os.path.dirname(__file__), "known_faces")
OUTPUT_EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), "embeddings", "authorized_embeddings.pkl")

def load_model(model_name=MODEL_NAME):
    print(f"[INFO] Loading DeepFace backend model: {model_name}")
    model = DeepFace.build_model(model_name)
    print("[INFO] Model loaded successfully.")
    return model

def get_embedding(model, img_path):
    try:
        face = functions.preprocess_face(
            img=img_path,
            target_size=TARGET_SIZE,
            enforce_detection=ENFORCE_DETECTION,
            detector_backend=DETECTOR_BACKEND
        )
        embedding = model.predict(face)[0].tolist()
        return embedding
    except Exception as e:
        print(f"[ERROR] Failed to process {img_path}: {e}")
        return None

def build_embeddings():
    if not os.path.exists(KNOWN_FACES_DIR):
        raise FileNotFoundError(f"Known faces directory not found: {KNOWN_FACES_DIR}")
    
    model = load_model()
    embeddings_db = {}

    print(f"[INFO] Scanning known faces in: {KNOWN_FACES_DIR}")
    for filename in tqdm(os.listdir(KNOWN_FACES_DIR), desc="Embedding Faces"):
        filepath = os.path.join(KNOWN_FACES_DIR, filename)

        if not os.path.isfile(filepath):
            continue

        name = os.path.splitext(filename)[0]
        embedding = get_embedding(model, filepath)

        if embedding:
            embeddings_db[name] = embedding
        else:
            print(f"[WARN] Skipping '{filename}' due to detection failure.")

    if not embeddings_db:
        raise RuntimeError("No embeddings were generated. Check face images or detection settings.")

    os.makedirs(os.path.dirname(OUTPUT_EMBEDDINGS_PATH), exist_ok=True)
    with open(OUTPUT_EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(embeddings_db, f)

    print(f"[SUCCESS] Stored {len(embeddings_db)} embeddings at: {OUTPUT_EMBEDDINGS_PATH}")

if __name__ == "__main__":
    build_embeddings()
