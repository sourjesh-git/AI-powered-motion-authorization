from flask import Flask, jsonify, request
import threading
import sys
import time
import os
from dotenv import load_dotenv
from queue import Queue

# Add source root to Python path so Flask can import main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import wait_and_run_pipeline  # Use this to include ESP32 trigger

# Load environment variables
load_dotenv()
task_logs = {}

app = Flask(__name__)

# Queue and status track ing
task_queue = Queue()
task_status = {}

def background_task(task_id):
    """
    This function runs the detection pipeline (with ESP32 trigger)
    in the background and updates the task status and logs.
    """
    def log_callback(msg):
        task_logs[task_id].append(f"{time.strftime('%H:%M:%S')} | {msg}")

    try:
        task_logs[task_id] = []  # Initialize log list

        # Wait for trigger and run pipeline with logging
        status = wait_and_run_pipeline(log_callback=log_callback)
        
        task_status[task_id] = {
            "status": status,
            "message": "Task completed successfully"
        }

    except Exception as e:
        task_status[task_id] = {
            "status": "error",
            "message": str(e)
        }
        task_logs[task_id].append(f"❌ Error: {str(e)}")

@app.route("/start-detection", methods=["POST"])
def start_detection():
    """
    Start the detection process (with ESP32 trigger) in background.
    """
    task_id = str(int(time.time()))
    task_status[task_id] = {"status": "running", "message": "Task started."}

    thread = threading.Thread(target=background_task, args=(task_id,))
    thread.start()

    return jsonify({"task_id": task_id, "status": "Task started."}), 202

@app.route("/task-status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    if task_id not in task_status:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(task_status[task_id])

@app.route("/task-results/<task_id>", methods=["GET"])
def get_task_results(task_id):
    if task_id not in task_status or task_status[task_id]["status"] == "running":
        return jsonify({"error": "Task not completed yet."}), 400
    
    result = task_status[task_id]
    if result["status"] == "error":
        return jsonify({"error": result["message"]}), 500

    return jsonify({
        "status": result["status"],
        "message": result["message"],
        "detection_result": result["status"]
    })

@app.route("/")
def index():
    return "Intruder Detection API is running."

@app.route("/task-logs/<task_id>", methods=["GET"])
def get_task_logs(task_id):
    if task_id not in task_logs:
        return jsonify({"logs": []})
    return jsonify({"logs": task_logs[task_id]})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
