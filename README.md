# 🔒 Intruder Detection System with ESP32, Camera & ML

A smart intruder detection pipeline using an **ESP32** with **ultrasonic sensor**, a **webcam**, and a **TensorFlow Lite ML model** running on a laptop. Upon detecting motion, it captures images, classifies for intruders, and sends an **email alert** if needed.

---

## 🚀 Tech Stack

| Layer | Technology |
|------|-------------|
| 📦 Microcontroller | ESP32 (Ultrasonic HC-SR04 sensor) |
| 🖥️ Host System | Python 3 |
| 🤖 ML Model | TensorFlow Lite |
| 📷 Image Capture | OpenCV |
| 📬 Email Alert | SMTP via `smtplib` |
| 📡 Serial Comm | PySerial |
| 🔐 Secrets Mgmt | python-dotenv |
| 🗃️ Storage | Local filesystem (image capture) |

---

## 🧠 Project Architecture

```plaintext
ESP32 (Ultrasonic Sensor)
        |
    [Serial via USB]
        |
     Laptop (Python)
        |
1. Wait for 'motion' trigger from ESP32
2. Capture 5 images using webcam
3. Run image classification (TFLite model)
4. If intruder found:
    → Send alert email with image
5. Send 'resume' command to ESP32
```

---

## 🛠️ How It Works

1. **ESP32 Setup**:
   - Constantly checks distance via ultrasonic sensor.
   - If object detected within 20cm:
     - Sends `motion` to laptop via serial.
     - Pauses distance tracking until it receives `resume`.

2. **Laptop Pipeline**:
   - Waits for `motion` on serial port.
   - Captures 5 images via webcam.
   - Feeds each image to a TensorFlow Lite model.
   - If model detects unauthorized person:
     - Sends an email with image attached.
   - Tells ESP32 to resume motion detection.

---

## 📁 Directory Structure

```
project/
├── src/
│   ├── camera.py         # Handles webcam image capture
│   ├── predictor.py      # Loads and runs TFLite model
│   ├── serial_listener.py# Listens to ESP32 serial data
│   └── notifier.py       # Sends email alerts
├── data/
│   └── captured/         # Stores captured images (gitignored)
├── .env                  # Email credentials and config (gitignored)
├── .gitignore
├── main.py               # Entry point
```

---

## 🔐 Environment Variables (`.env`)

```env
EMAIL_SENDER=your@email.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECEIVER=alert@destination.com
```

> Use an App Password if using Gmail with 2FA.

---

## 🛑 .gitignore

```gitignore
# Ignore virtual env
venv/

# Ignore env secrets
.env

# Ignore captured image data
data/captured/
```

---

## 📷 Sample Output

```
🔌 Listening to serial port COM3 for 'motion'...
🎯 Motion detected via ESP!
📸 Capturing images...
🧠 Prediction: Intruder (1.00) - image1.jpg
🚨 Intruder detected!
📧 Sending email alert...
📨 Email sent with image: image1.jpg
```

---

## 📌 Notes

- Program terminates after the **first intruder detection**.
- Avoids false triggers by verifying object using ML model.
- You can easily extend this to:
  - Push alerts to mobile devices
  - Upload alerts to cloud
  - Log events in a database

---

## ✅ To Run

1. Plug in ESP32 with the ultrasonic sensor.
2. Set up the `.env` file.
3. Activate your Python virtual environment.
4. Run the pipeline:

```bash
python main.py
```

---

## 👨‍💻 Author

Made with ❤️ by [Your Name]

---

## 📜 License

MIT License — free to use and modify!
