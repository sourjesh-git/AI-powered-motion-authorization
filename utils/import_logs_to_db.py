import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import log_detection_to_db
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = "logs/detections.log"

def import_existing_logs():
    if not os.path.exists(LOG_FILE):
        print("❌ Log file not found.")
        return

    with open(LOG_FILE, "r") as file:
        for line in file:
            line = line.strip()
            if not line or "|" not in line:
                continue
            parts = line.split(" | ")
            if len(parts) == 3:
                timestamp, status, image_path = parts
                log_detection_to_db(timestamp, status, image_path)

    print("✅ Existing logs imported to NeonDB.")

if __name__ == "__main__":
    import_existing_logs()
