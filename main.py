import os
import time
from dotenv import load_dotenv

from src.serial_listener import wait_for_trigger
from src.camera import capture_images
from src.predictor import predict
from src.notifier import send_alert

# Load email credentials from .env
load_dotenv()

VERIFIED_LABEL = "Authorized"  # Update if your model uses a different label

def run_pipeline():
    print("\n📸 Capturing images...")
    image_paths = capture_images(num_images=5, delay=2)

    for img_path in image_paths:
        label, confidence = predict(img_path)
        print(f"🧠 Prediction: {label} ({confidence:.2f}) - {img_path}")

        if label != VERIFIED_LABEL:
            print(f"🚨 Intruder detected in image: {img_path}")
            print("\n📧 Sending email alert...")
            send_alert(img_path)
            return True  # Intruder found

    print("\n✅ No intruder detected. All clear.")
    return False  # No intruder

if __name__ == "__main__":
    while True:
        # Step 1: Listen for motion
        ser = wait_for_trigger()
        if not ser:
            print("👋 Exiting program.")
            break

        # Step 2: Run image capture and detection pipeline
        intruder_found = run_pipeline()

        # Step 3: Close serial port
        ser.close()

        if intruder_found:
            print("🛑 Alert sent. Exiting to avoid ESP32 reboot logs.")
            break  # Exit after one alert
        else:
            # Resume ESP32 detection only if nothing suspicious
            print("📨 Sending 'resume' to ESP32...")
            try:
                ser = wait_for_trigger(open_only=True)  # Optional: Re-open if needed
                ser.write(b"resume\n")
                time.sleep(0.5)
                ser.close()
            except Exception as e:
                print(f"⚠️ Error sending 'resume': {e}")

            print("\n🔁 Waiting for next trigger...\n")
