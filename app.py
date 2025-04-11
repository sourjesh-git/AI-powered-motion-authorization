import streamlit as st
import os
import time
import glob
import yaml
from PIL import Image
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
from utils.cctv_stream import start_stream
from dotenv import load_dotenv
from db import get_connection, log_detection_to_db, fetch_logs


load_dotenv()

# ---------------- CONFIG ----------------
LOG_FILE = "logs/detections.log"
CAPTURE_DIR = "data/captured"
st.set_page_config(page_title="Intruder Detection Dashboard", layout="centered")

# ---------------- AUTHENTICATION ----------------
with open("config/credentials.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Username/password is incorrect")

elif authentication_status is None:
    st.warning("Please enter your username and password")

elif authentication_status:
    # --- Sidebar ---
    authenticator.logout("Logout", "sidebar")
    st.sidebar.write(f"Welcome, **{name}** ({username})")

    # --- Get User Role from YAML ---
    user_role = config['credentials']['usernames'][username]['role']

    # ---------------- DASHBOARD HEADER ----------------
    st.title("AI Powered Motion Authorization")
    st.subheader("Intruder/Authorization Dashboard")
    st.markdown("This dashboard displays the latest intruder detection logs and captured images.")

    auto_refresh = st.checkbox("🔁 Auto-refresh every 5 seconds", value=False)

    # ----------------- HELPERS -----------------
    def read_latest_log():
        if not os.path.exists(LOG_FILE):
            return None, None
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        for line in reversed(lines):
            if "ALERT" in line:
                parts = line.strip().split(" | ")
                if len(parts) == 3:
                    timestamp, status, image_path = parts
                    return timestamp, image_path
        return None, None

    def log_detection(status, image_path):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} | {status} | {image_path}\n"

        # Log to file
        os.makedirs("logs", exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(log_line)

        # Log to NeonDB
        log_detection_to_db(timestamp, status, image_path)

    def get_latest_captured_image():
        files = glob.glob(os.path.join(CAPTURE_DIR, "*.jpg"))
        if not files:
            return None
        latest = max(files, key=os.path.getctime)
        return latest

    def display_latest_intruder_log():
        st.subheader("🚨 Last Intruder Detection")
        timestamp, image_path = read_latest_log()
        if not timestamp or not image_path or not os.path.exists(image_path):
            st.info("No intruder has been detected yet.")
            return
        st.write(f"**Time:** {timestamp}")
        st.image(image_path, caption="Intruder Captured Image", use_container_width=True)

    def display_latest_capture():
        st.subheader("📸 Latest Captured Image")
        latest_img = get_latest_captured_image()
        if not latest_img:
            st.info("No images have been captured yet.")
            return
        st.image(latest_img, caption="Most Recent Capture", use_container_width=True)

    def display_full_log():
        st.subheader("📜 View Full Detection Log")
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                st.text(f.read())
        else:
            st.warning("No log file found.")

    def display_db_logs():
        st.subheader("🗄 Logs from Database")
        logs = fetch_logs()
        if not logs:
            st.info("No logs in the database yet.")
            return

        for log in logs:
            try:
                # Handle both 3-field and 4-field log tuples
                if len(log) == 4:
                    _, timestamp, status, image_path = log
                elif len(log) == 3:
                    timestamp, status, image_path = log
                else:
                    continue  # Skip malformed rows

                st.markdown(f"**Time:** {timestamp}  |  **Status:** {status}")
                if image_path and os.path.exists(image_path):
                    st.image(image_path, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying log: {e}")

    # ---------------- DISPLAY SECTIONS ----------------
    if user_role == "Admin":
        display_latest_intruder_log()

    display_latest_capture()

    if user_role == "Admin":
        display_full_log()

    # ---------------- AUTO REFRESH ----------------
    if auto_refresh:
        time.sleep(5)
        st.rerun()

    if user_role == "Admin":
        st.subheader("🟢 Admin Tools")

    if st.button("Start Live CCTV Stream"):
        cctv_url = os.getenv("CCTV_STREAM_URL")
        if cctv_url:
            start_stream(cctv_url)
        else:
            st.error("CCTV URL not set in .env file")

    if user_role == "Admin":
        display_db_logs()
