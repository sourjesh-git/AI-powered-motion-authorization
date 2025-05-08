import os
import time
from dotenv import load_dotenv

from src.serial_listener import wait_for_trigger
from src.camera import capture_images
from src.predictor import predict
from src.notifier import send_alert  # Email
from src.notifier_telegram import send_telegram_alert, send_tg_location  # Telegram
from db import log_detection_to_db 

# Load environment variables
load_dotenv()

VERIFIED_LABEL = "Authorized"
LOG_PATH = "logs/detections.log"

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

    for img_path in image_paths:
        try:
            label, confidence = predict(img_path)
        except Exception as e:
            log_callback(f"⚠️ Prediction failed for {img_path}: {e}")
            continue

        log_callback(f"🧠 Prediction: {label} ({confidence:.2f}) - {img_path}")

        if VERIFIED_LABEL.lower() in label.lower():
            log_callback(f"✅ Authorized person detected: {img_path}")
            log_event("AUTHORIZED", img_path)
            return "authorized"
        else:
            log_callback(f"🚨 Intruder detected: {img_path}")
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