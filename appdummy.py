import streamlit as st
import requests
import time

# URL of your Flask backend
FLASK_API_URL = "http://127.0.0.1:5000"

st.title("🛡️ Intruder Detection System (Dummy UI)")

if st.button("🚀 Start Detection"):
    st.write("Starting detection...")
    try:
        # Step 1: Start detection
        response = requests.post(f"{FLASK_API_URL}/start-detection")
        response.raise_for_status()
        task_id = response.json().get("task_id")

        if not task_id:
            st.error("Failed to retrieve task ID.")
        else:
            st.success(f"Detection started. Task ID: {task_id}")
            status_placeholder = st.empty()
            logs_placeholder = st.empty()

            # Step 2: Poll for status and logs
            while True:
                # Fetch task status
                status_response = requests.get(f"{FLASK_API_URL}/task-status/{task_id}")
                status_json = status_response.json()
                status = status_json.get("status", "unknown")
                status_placeholder.info(f"Task Status: {status}")

                # Fetch logs
                logs_response = requests.get(f"{FLASK_API_URL}/task-logs/{task_id}")
                logs = logs_response.json().get("logs", [])
                logs_text = "\n".join(logs)
                logs_placeholder.markdown(f"**Progress:**\n```{logs_text}```")

                if status in ["completed", "error", "intruder", "authorized", "none"]:
                    break

                time.sleep(2)  # Poll every 2 seconds

            # Step 3: Show result
            result_response = requests.get(f"{FLASK_API_URL}/task-results/{task_id}")
            result_json = result_response.json()
            result = result_json.get("detection_result", "No result found.")

            if result == "intruder":
                st.error("🚨 Intruder detected!")
            elif result == "authorized":
                st.success("✅ Authorized person.")
            elif result == "none":
                st.warning("⚠️ Detection inconclusive.")
            else:
                st.write(result)

    except Exception as e:
        st.error(f"❌ Request failed: {e}")
