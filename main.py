import os
import time
from dotenv import load_dotenv

from src.serial_listener import wait_for_trigger
from src.camera import capture_images
from src.predictor import predict
from src.notifier import send_alert
from db import log_detection_to_db  # <- Add this

# Load environment variables
load_dotenv()

VERIFIED_LABEL = "Authorized"
LOG_PATH = "logs/detections.log"

def log_event(status, image_path):
    """Log detection to file and database."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # File logging
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} | {status} | {image_path}\n")

    # Database logging
    log_detection_to_db(timestamp, status, image_path)


def run_pipeline():
    print("\n📸 Capturing images...")
    image_paths = capture_images(num_images=5, delay=2)

    if not image_paths:
        print("❌ No images captured.")
        return "none"

    for img_path in image_paths:
        try:
            label, confidence = predict(img_path)
        except Exception as e:
            print(f"⚠️ Prediction failed for {img_path}: {e}")
            continue

        print(f"🧠 Prediction: {label} ({confidence:.2f}) - {img_path}")

        if VERIFIED_LABEL.lower() in label.lower():
            print(f"✅ Authorized person detected: {img_path}")
            log_event("AUTHORIZED", img_path)
            return "authorized"
        else:
            print(f"🚨 Intruder detected: {img_path}")
            print("📧 Sending alert email...")
            try:
                send_alert(img_path)
            except Exception as e:
                print(f"⚠️ Failed to send email: {e}")
            log_event("ALERT", img_path)
            return "intruder"

    print("⚠️ No conclusive prediction made.")
    return "none"

if __name__ == "__main__":
    print("🔌 Starting intruder detection system...")

    while True:
        ser = wait_for_trigger()
        if not ser:
            print("👋 Exiting program.")
            break

        result = run_pipeline()
        ser.close()

        if result == "intruder":
            print("🛑 Intruder alert handled. Exiting.")
            break

        elif result == "authorized":
            print("🟢 Authorized detection complete. Exiting.")
            break

        else:
            # If nothing conclusive, resume ESP32
            print("📨 Sending 'resume' to ESP32...")
            try:
                ser = wait_for_trigger()
                ser.write(b"resume\n")
                time.sleep(0.5)
                ser.close()
            except Exception as e:
                print(f"⚠️ Failed to send 'resume': {e}")
            print("\n🔁 Waiting for next motion trigger...\n")
