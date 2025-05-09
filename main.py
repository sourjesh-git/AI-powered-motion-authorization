import os
import time
from dotenv import load_dotenv

from src.serial_listener import wait_for_trigger
from src.camera import capture_images
from src.predict_with_embed import verify_captured_images, load_model, load_embeddings
from src.notifier import send_alert  # Email
from src.notifier_telegram import send_telegram_alert, send_tg_location  # Telegram
from db import log_detection_to_db 

# Load environment variables
load_dotenv()

# Constants
MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "mtcnn"
ENFORCE_DETECTION = False  # For inference, allow fallback even if face not found
THRESHOLD = 0.4  # Cosine distance threshold
EMBEDDINGS_PATH = os.path.join("face_auth", "embeddings", "authorized_embeddings.pkl")
VERIFIED_LABEL = "Authorized"
LOG_PATH = "logs/detections.log"

# Load model and embeddings
model = load_model()
embeddings_db = load_embeddings(EMBEDDINGS_PATH)

def log_event(status, image_path):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} | {status} | {image_path}\n")

    log_detection_to_db(timestamp, status, image_path)

def run_pipeline(log_callback=print):  # Default to print if no callback
    log_callback("\n📸 Capturing images...")
    image_paths = capture_images(num_images=5, delay=2)

    if not image_paths:
        log_callback("❌ No images captured.")
        return "none"

    results = verify_captured_images(image_paths, model, embeddings_db)

    for name, img_path, score in results:
        if score is not None:
            if VERIFIED_LABEL.lower() in name.lower():
                if score < THRESHOLD:  # Only proceed if score is below the threshold
                    log_callback(f"✅ Authorized person detected: {name} ({score:.2f}) - {img_path}")
                    log_event("AUTHORIZED", img_path)
                    return "authorized"
                else:
                    log_callback(f"⚠️ Authorized person detected, but score above threshold: {name} ({score:.2f}) - {img_path}")
                    return "none"  # No need to take further action

            else:  # Intruder detected
                if score < THRESHOLD:  # Only proceed if score is below the threshold
                    log_callback(f"🚨 Intruder detected: {name} ({score:.2f}) - {img_path}")
                    log_event("ALERT", img_path)

                    log_callback("📧 Sending email alert...")
                    try:
                        send_alert(img_path)
                    except Exception as e:
                        log_callback(f"⚠️ Email failed: {e}")

                    log_callback("📨 Sending Telegram alert...")
                    try:
                        location = send_tg_location()
                        send_telegram_alert(img_path, location)
                    except Exception as e:
                        log_callback(f"⚠️ Telegram failed: {e}")

                    return "intruder"
                else:
                    log_callback(f"⚠️ Detected potential intruder, but score above threshold: {name} ({score:.2f}) - {img_path}")
                    return "none"  # No need to take further action

    log_callback("⚠️ No conclusive prediction made.")
    return "none"


def wait_and_run_pipeline(log_callback=print):
    log_callback("🔌 Flask-triggered detection started...")

    ser = wait_for_trigger()
    if not ser:
        log_callback("❌ Trigger not received. Exiting.")
        return "no_trigger"

    result = run_pipeline(log_callback=log_callback)
    ser.close()
    return result

if __name__ == "__main__":
    print("🔌 Starting intruder detection system...")

    while True:
        ser = wait_for_trigger()
        if not ser:
            print("👋 Exiting program.")
            break

        result = run_pipeline()
        ser.close()

        if result in ["intruder", "authorized"]:
            print("✅ Detection handled. Exiting.")
            break

        print("📨 Sending 'resume' to ESP32...")
        try:
            ser = wait_for_trigger()
            ser.write(b"resume\n")
            time.sleep(0.5)
            ser.close()
        except Exception as e:
            print(f"⚠️ Resume send failed: {e}")
        print("\n🔁 Waiting for next trigger...\n")
