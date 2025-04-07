import numpy as np
from PIL import Image
import tensorflow as tf  # Or use tflite_runtime.interpreter if you're on Raspberry Pi
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.tflite")
LABELS_PATH = os.path.join(BASE_DIR, "model", "labels.txt")

# Load labels
def load_labels():
    with open(LABELS_PATH, "r") as f:
        return [line.strip() for line in f.readlines()]

# Load model
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Image input size (height, width)
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

labels = load_labels()

def preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((width, height))
    image_array = np.asarray(image, dtype=np.float32)  # Convert to float32
    image_array = image_array / 255.0  # Normalize to [0, 1]
    input_data = np.expand_dims(image_array, axis=0)
    return input_data

def predict(image_path):
    input_data = preprocess_image(image_path)

    # Set tensor
    interpreter.set_tensor(input_details[0]['index'], input_data)

    # Run inference
    interpreter.invoke()

    # Get output
    output_data = interpreter.get_tensor(output_details[0]['index'])[0]
    top_result_index = int(np.argmax(output_data))
    confidence = float(output_data[top_result_index])

    label = labels[top_result_index]
    return label, confidence
