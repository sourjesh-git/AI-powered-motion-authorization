# src/notifier.py

import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
RECEIVER_EMAIL = SENDER_EMAIL  # Send alert to yourself

def send_alert(image_path):
    """
    Sends an email alert with the intruder's image.
    """
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        print("❌ Email credentials not found. Check your .env file.")
        return

    subject = "🚨 Intruder Detected!"
    body = "An unrecognized person was detected. See attached image."

    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.set_content(body)

    # Attach image
    with open(image_path, 'rb') as f:
        img_data = f.read()
        msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=os.path.basename(image_path))

    # Send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"📩 Alert email sent with image: {image_path}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
