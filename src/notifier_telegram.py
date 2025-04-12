import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_tg_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def send_tg_photo(image_path, caption=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as photo:
        files = {"photo": photo}
        data = {"chat_id": CHAT_ID, "caption": caption or ""}
        requests.post(url, files=files, data=data)

def send_tg_location():
    ip_info = requests.get("https://ipinfo.io/json").json()
    if 'loc' in ip_info:
        lat, lon = ip_info['loc'].split(',')
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendLocation"
        payload = {"chat_id": CHAT_ID, "latitude": lat, "longitude": lon}
        requests.post(url, data=payload)

def send_telegram_alert(image_path, location_info=None):
    caption = "🚨 Intruder Alert!"

    if location_info:
        caption += f"\n\n📍 Location: {location_info.get('city', 'Unknown')}, {location_info.get('country', '')}"

    send_tg_message(caption)
    send_tg_photo(image_path, caption)
    send_tg_location()
