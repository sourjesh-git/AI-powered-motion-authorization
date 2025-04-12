import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
updates = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
print(updates.json())
