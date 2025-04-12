import time
from src.camera import capture_images
from src.predictor import predict
from src.notifier_telegram import send_tg_message, send_tg_photo, send_tg_location
from src.notifier import send_alert

VERIFIED_LABEL = "Authorized"

def run_manual_trigger():
    print("📸 Capturing images...")
    image_paths = capture_images(num_images=5, delay=2)

    for img in image_paths:
        label, confidence = predict(img)
        print(f"🧠 Prediction: {label} ({confidence:.2f})")

        if VERIFIED_LABEL.lower() in label.lower():
            send_tg_message(f"✅ Authorized detected ({confidence:.2f})")
            send_tg_photo(img, caption="Authorized Person")
            return

        else:
            send_tg_message(f"🚨 Intruder detected! Confidence: {confidence:.2f}")
            send_tg_photo(img, caption="Intruder Alert")
            send_tg_location()
            send_alert(image_path=img)
            return

if __name__ == "__main__":
    run_manual_trigger()
