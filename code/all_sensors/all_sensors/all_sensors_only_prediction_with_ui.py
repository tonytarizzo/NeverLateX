import serial
import csv
import time
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import layers
from characters import get_complete_set
from datetime import datetime
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import queue
from tkinter import Label, PhotoImage
from PIL import Image, ImageTk  # Required for resizing the image

# === Configuration ===
serial_port = '/dev/tty.usbmodem101' 
baud_rate = 115200
model_folder = "all_sensors/model_parameters"
model_filename = "cldnn_full_model.h5"
prediction_file_name = "predicted_characters.csv"
window_size = 1500  # Can be any value
window_step = int(window_size/4) # Move forward by this step

# === Setup Character Encoding ===
blank_token = 'BLANK'
dataset = get_complete_set()
characters = set(char for label in dataset for char in label)
char_to_num = layers.StringLookup(vocabulary=list(characters), mask_token=None, oov_token=blank_token)
num_to_char = layers.StringLookup(vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True)

# === CSV Logging Setup ===
current_directory = os.getcwd()
prediction_path = os.path.join(current_directory, "all_sensors/predicted_data", prediction_file_name)
feature_set = ['Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z',
               'Mag_X', 'Mag_Y', 'Mag_Z', 'Force1', 'Force2', 'Force3']

# === Buffer and Queue ===
all_buffer = []
predicted_characters = {}
scaler = StandardScaler()
prediction_queue = queue.Queue()

# === Load Model and Get Expected Input Shape ===
model_path = os.path.join(model_folder, model_filename)
try:
    model = load_model(model_path, custom_objects={'ctc_loss': lambda y_true, y_pred: y_pred})
    model_input_shape = model.input_shape[1]  # Get expected time step length
    print(f"Model loaded successfully! Expected input time steps: {model_input_shape}")
except Exception as e:
    print(f"Error loading model: {e}")

# === Adjust Window Size Dynamically ===
def adjust_window_size(data, target_size):
    """
    Adjusts the window size dynamically to fit the model's input shape.
    - Truncate if too long
    - Pad with zeros if too short
    """
    if len(data) > target_size:
        return data[:target_size]  # Truncate
    elif len(data) < target_size:
        pad_width = target_size - len(data)
        return np.pad(data, ((0, pad_width), (0, 0)), mode='constant')  # Zero padding
    return data

# === Decode Predictions ===
def decode_predictions(logits, num_to_char):
    decoded_predictions, _ = tf.nn.ctc_greedy_decoder(
        tf.transpose(logits, [1, 0, 2]),  
        tf.fill([tf.shape(logits)[0]], tf.shape(logits)[1])
    )
    dense_predictions = tf.sparse.to_dense(decoded_predictions[0], default_value=0)
    predicted_texts = [
        ''.join(num_to_char(index).numpy().decode('utf-8') for index in prediction if index > 0)
        for prediction in dense_predictions
    ]
    return predicted_texts

# === Predict in Chunks and Merge Outputs ===
def process_chunks_and_predict(buffer):
    """
    Process the buffered data in smaller chunks, pass them to the model, 
    and concatenate outputs for better predictions.
    """
    chunk_size = model_input_shape  # Each chunk should match the model's expected size
    predictions = []

    for i in range(0, len(buffer) - chunk_size + 1, chunk_size // 2):  # Overlapping chunks
        chunk = np.array(buffer[i:i + chunk_size], dtype=np.float32)

        # Standardize the data
        chunk = scaler.fit_transform(chunk)

        # Ensure it matches the expected model input shape
        chunk = adjust_window_size(chunk, model_input_shape)

        # Reshape for model
        chunk = chunk.reshape(1, model_input_shape, chunk.shape[1])

        # Predict
        preds = model.predict(chunk)
        decoded = decode_predictions(preds, num_to_char)
        
        predictions.append(decoded[0])  # Append the result

    # Merge all predictions smoothly
    return ''.join(predictions)

# === Serial Reading Thread with Chunk-Based Processing ===
def serial_reading_thread(stop_event, all_buffer=all_buffer):
    try:
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser, \
             open(prediction_path, mode='w', newline='') as prediction_file:

            prediction_writer = csv.writer(prediction_file)
            prediction_writer.writerow(['Timestamp', 'Best Prediction'])

            while not stop_event.is_set():
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue

                if line == 'System Deactivated':
                    all_buffer.clear()

                elif line == 'System Activated':
                    all_buffer.clear()

                elif len(line.split(',')) == len(feature_set):
                    data = line.split(',')
                    #print(data)  # Debugging output

                    sensor_values = [float(value) for value in data]
                    all_buffer.append(sensor_values)

                    if len(all_buffer) >= window_size:
                        # Predict on chunks of data and concatenate results
                        prediction = process_chunks_and_predict(all_buffer)

                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                        predicted_characters[timestamp] = prediction
                        prediction_writer.writerow([timestamp, prediction])
                        prediction_queue.put((timestamp, prediction))

                        # Move the sliding window forward
                        all_buffer = all_buffer[window_step:]

    except Exception as e:
        print(f"Error: {e}")

# === Tkinter UI Setup ===
def start_ui(stop_event):
    root = tk.Tk()
    root.title("Real-Time Handwriting Prediction")
    window_width = 600
    window_height = 400
    root.geometry(f"{window_width}x{window_height}")  # Set initial window size

    # === Add Description Text at the Top ===
    description_text = (
        "This UI shows predictions of real-time handwriting using a sensor-equipped pen "
        "developed by the NeverLateX team for the AML lab project "
        "for MSc in AML at Imperial College London."
    )
    description_label = Label(root, text=description_text, wraplength=550, justify="center", font=("Arial", 10))
    description_label.pack(pady=10)

    # === Load and Resize Logo Dynamically ===
    logo_path = "/Users/tunakisaga/Desktop/Repos/NeverLateX/all_sensors/all_sensors/Imperial_College_London_new_logo.png"
    
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        logo_width = window_width // 5  # 1/10th of the window width
        # Keep the aspect ratio
        logo_size = (logo_width, int(logo_width * img.height / img.width))
        img = img.resize(logo_size, Image.LANCZOS)
        logo = ImageTk.PhotoImage(img)

        logo_label = Label(root, image=logo)
        logo_label.image = logo  # Keep reference to prevent garbage collection
        logo_label.pack(pady=5)  # Ensure it is centered below the text

    # === Prediction Display Area ===
    text_area = ScrolledText(root, width=80, height=15)
    text_area.pack(padx=10, pady=10)
    text_area.configure(state='disabled')

    # === Poll Predictions and Update UI ===
    def poll_predictions():
        try:
            while True:
                timestamp, pred = prediction_queue.get_nowait()
                message = f"[{pred}"
                text_area.configure(state='normal')
                text_area.insert(tk.END, message)
                text_area.see(tk.END)
                text_area.configure(state='disabled')
        except queue.Empty:
            pass
        if not stop_event.is_set():
            root.after(100, poll_predictions)

    poll_predictions()
    root.mainloop()
    stop_event.set()

# === Main Execution ===
if __name__ == "__main__":
    stop_event = threading.Event()
    serial_thread = threading.Thread(target=serial_reading_thread, args=(stop_event,), daemon=True)
    serial_thread.start()
    start_ui(stop_event)
    serial_thread.join()
