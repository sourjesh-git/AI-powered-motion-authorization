import streamlit as st
import cv2
import time

def start_stream(cctv_url):
    st.subheader("📹 Live CCTV Feed")

    # Initialize stream control state
    if 'stream_active' not in st.session_state:
        st.session_state.stream_active = True
    else:
        st.session_state.stream_active = True  # Ensure it's turned on each time this function runs

    cap = cv2.VideoCapture(cctv_url)
    if not cap.isOpened():
        st.error("❌ Unable to access the CCTV stream.")
        st.session_state.stream_active = False
        return

    frame_placeholder = st.empty()

    # Stop button (with unique key to avoid Streamlit duplicate ID error)
    stop_button = st.button("❌ Stop Stream", key="stop_stream_btn")
    if stop_button:
        st.session_state.stream_active = False

    # Main loop
    while st.session_state.stream_active:
        ret, frame = cap.read()
        if not ret:
            st.warning("⚠️ Failed to read from stream.")
            break
        frame_placeholder.image(frame, channels="BGR", use_container_width=True)
        time.sleep(0.03)  # ~30 FPS

        # Use the session state flag to break the loop (avoid placing another button here)

    cap.release()
    frame_placeholder.empty()
    st.success("✅ Stream ended.")
    st.session_state.stream_active = False
