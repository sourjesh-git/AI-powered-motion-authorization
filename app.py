import streamlit as st
import os
from PIL import Image
import glob
import time

LOG_FILE = "logs/detections.log"
CAPTURE_DIR = "data/captured"

st.set_page_config(page_title="Intruder Detection Dashboard", layout="centered")

st.title("AI Powered Motion Authorization")
st.subheader("Intruder/Authorization Dashboard")
st.markdown("This dashboard displays the latest intruder detection logs and captured images.")

# --- Live update toggle ---
auto_refresh = st.checkbox("🔁 Auto-refresh every 5 seconds", value=False)

# --- Read latest log with intruder alert ---
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

# --- Get latest captured image (any) ---
def get_latest_captured_image():
    files = glob.glob(os.path.join(CAPTURE_DIR, "*.jpg"))
    if not files:
        return None
    latest = max(files, key=os.path.getctime)
    return latest

# --- Section 1: Intruder detection from logs ---
def display_latest_intruder_log():
    st.subheader("🚨 Last Intruder Detection")
    timestamp, image_path = read_latest_log()

    if not timestamp or not image_path or not os.path.exists(image_path):
        st.info("No intruder has been detected yet.")
        return

    st.write(f"**Time:** {timestamp}")
    st.image(image_path, caption="Intruder Captured Image", use_container_width=True)

# --- Section 2: Latest camera capture ---
def display_latest_capture():
    st.subheader("📸 Latest Captured Image")
    latest_img = get_latest_captured_image()

    if not latest_img:
        st.info("No images have been captured yet.")
        return

    st.image(latest_img, caption="Most Recent Capture", use_container_width=True)

# --- Section 3: Full detection log viewer ---
def display_full_log():
    st.subheader("📜 View Full Detection Log")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            st.text(f.read())
    else:
        st.warning("No log file found.")

# --- Run sections ---
# display_latest_intruder_log()
display_latest_capture()
display_full_log()

# --- Optional auto-refresh ---
if auto_refresh:
    time.sleep(5)
    st.rerun()
