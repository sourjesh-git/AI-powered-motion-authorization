# src/serial_listener.py

import serial
import time

SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

def wait_for_trigger():
    """
    Opens serial port, waits for 'motion', then returns True.
    Keeps the port open for 'resume' command later.
    """
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"🔌 Listening to serial port {SERIAL_PORT} for 'motion'...")

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip().lower()
            if line:
                print(f"📨 Received: {line}")
            if "motion" in line:
                print("🎯 Motion detected via ESP!")
                return ser  # Keep serial open for sending 'resume'

    except serial.SerialException as e:
        print(f"❌ Serial connection error: {e}")
        return None
    except KeyboardInterrupt:
        print("\n🚪 Exiting via Ctrl+C")
        return None
