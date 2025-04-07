import os
import time
from dotenv import load_dotenv

from src.serial_listener import wait_for_trigger
from src.camera import capture_images
from src.predictor import predict
from src.notifier import send_alert

# Load email credentials from .env
load_dotenv()

VERIFIED_LABEL = "Authorized"
LOG_PATH = "logs/detections.log"

def log_intruder(image_path):
    """Append timestamped intruder info to log file."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | ALERT | {image_path}\n")

def log_authorized(image_path):
    """Optional: Log authorized detection (for debugging or future features)."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | AUTHORIZED | {image_path}\n")

def run_pipeline():
    print("\n📸 Capturing images...")
    image_paths = capture_images(num_images=5, delay=2)

    for img_path in image_paths:
        label, confidence = predict(img_path)
        print(f"🧠 Prediction: {label} ({confidence:.2f}) - {img_path}")

        if VERIFIED_LABEL.lower() in label.lower():
            print(f"✅ Authorized person detected in image: {img_path}")
            log_authorized(img_path)
            return "authorized"

        else:
            print(f"🚨 Intruder detected in image: {img_path}")
            print("\n📧 Sending email alert...")
            send_alert(img_path)
            log_intruder(img_path)
            return "intruder"

    return "none"  # Shouldn't hit this if at least one prediction was made

if __name__ == "__main__":
    while True:
        ser = wait_for_trigger()
        if not ser:
            print("👋 Exiting program.")
            break

        result = run_pipeline()
        ser.close()

        if result == "intruder":
            print("🛑 Intruder alert sent. Exiting.")
            break

        elif result == "authorized":
            print("🟢 Authorized person verified. Exiting.")
            break

        else:
            # Only resume ESP32 if nothing was classified at all
            print("📨 Sending 'resume' to ESP32...")
            try:
                ser = wait_for_trigger()  # Removed open_only param
                ser.write(b"resume\n")
                time.sleep(0.5)
                ser.close()
            except Exception as e:
                print(f"⚠️ Error sending 'resume': {e}")
            print("\n🔁 Waiting for next trigger...\n")
