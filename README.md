
# 🔒 Intruder Detection System with ESP32, Camera & ML

A smart intruder detection pipeline using an **ESP32** with **ultrasonic sensor**, a **webcam**, a **TensorFlow Lite ML model**, and a **Streamlit dashboard**. Upon detecting motion, it captures images, classifies for intruders, and sends an **email alert**. A real-time dashboard logs detections and offers a **live CCTV stream** with **role-based access control**.

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
| 🧠 Database | NeonDB (PostgreSQL) |
| 🌐 Dashboard | Streamlit |
| 👥 Auth | streamlit-authenticator |
| 🔁 Live Stream | IP Webcam / CCTV (via `utils/cctv_stream.py`) |

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
    → Send alert notification with image and live location on Telegram
    → Log to NeonDB and .log file
5. Send 'resume' command to ESP32
6. Streamlit dashboard displays live logs and stream
```

---

## 🛠️ How It Works

### 1. **ESP32 Setup**:
   - Constantly checks distance via ultrasonic sensor.
   - If object detected within 20cm:
     - Sends `motion` to laptop via serial.
     - Pauses distance tracking until it receives `resume`.

### 2. **System Pipeline**:
   - Waits for `motion` on serial port.
   - Captures 5 images via webcam.
   - Feeds each image to a TensorFlow Lite model.
   - If model detects unauthorized person:
     - Sends an email with image attached.
     - Sends alert notification with image and live location on Telegram
     - Logs to `.log` file and NeonDB.
   - Tells ESP32 to resume motion detection.

### 3. **Streamlit Dashboard**:
   - Secure login with **username/password**.
   - **Roles**: Admin, Viewer, Guest
     - Admin: View all logs and images.
     - Viewer: View logs with image paths only.
     - Guest: View stream and masked images.
   - View real-time logs from file and database.
   - Enable **Live CCTV Stream** by entering IP camera URL.

---

## 📁 Directory Structure

```
project/
├── src/
│   ├── camera.py             # Handles webcam image capture
│   ├── predictor.py          # Predicts using TFLite Model
│   ├── notifier_telegram.py  # Sends telegram notifications     
│   ├── serial_listener.py    # Listens to ESP32 serial data
│   └── notifier.py           # Sends email alerts
├── utils/
│   ├── cctv_stream.py        # Starts IP webcam stream
│   ├── get_tg_chatID.py      # Sets the TG ChatID for the account
│   ├── import_logs_to_db.py  # Imports the log file values to NeonDB
│   ├── hash_passwords.py     # To get hashed passwords for different roles
├── data/
│   └── captured/         # Stores captured images (gitignored)
├── config/
│   └── credentials.yaml  # Auth credentials and roles (gitignored)
├── logs/
│   └── detections.log    # Local log of alerts
├── .env                  # Email credentials and config (gitignored)
├── example.env           # Example env file                 
├── .gitignore
├── main.py               # Entry point for detection pipeline
├── app.py                # Streamlit dashboard
├── db.py                 # NeonDB interactions
├──test_db.py             # Test DB Connection      
├── manual_trigger.py
├── requirements.txt     # Sets a manual trigger to check TG and Email notifications with the Sensor trigger
```

---

## 🛑 .gitignore

```gitignore
# Ignore Python virtual environments
venv/

# Ignore dotenv environment variables
.env

# Ignore captured image data
data/captured/
Images/
utils/hash_passwords.py

# Ignore system files
src/__pycache__/
*.pyc

# VSCode and OS metadata
.vscode/
.DS_Store
Thumbs.db

#Ignore credentials for authoerization
/config/credentials.yaml    

---

## 📷 Sample Output

```bash
🔌 Listening to serial port COM3 for 'motion'...
🎯 Motion detected via ESP!
📸 Capturing images...
🧠 Prediction: Intruder (1.00) - image1.jpg
🚨 Intruder detected!
📧 Sending email alert...
📨 Email sent with image: image1.jpg
💾 Logged to DB and file
```

---

## ✅ To Run

### Detection Pipeline:
```bash
python main.py
```

### Dashboard:
```bash
streamlit run app.py
```

---

## 👨‍💻 Author

IIITK 2022 ECE BATCH PROJECT  
Sourjesh Mukherjee 2022BEC0007  
Suchit Paul Santosh 2022BEC0006  
Aadith Abhimanyu 2022BEC0015  

---

## 📜 License

MIT License — free to use and modify!
