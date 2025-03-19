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

# === Configuration ===
serial_port = '/dev/tty.usbmodem101' 
baud_rate = 9600
model_folder = "all_sensors/model_parameters"
model_filename = "CLDNN.h5"
prediction_file_name = "predicted_characters.csv"
max_sequence_length = 188

# Sliding Window Configuration
window_size = 48  # Change from 64 to match model expectation
window_step = 24  # Adjust step size accordingly

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

# === Decoding Predictions ===
def ctc_loss_fn(y_true, y_pred):
    # Transpose y_pred if using logits_time_major=True (to [max_time, batch_size, num_classes])
    y_pred = tf.transpose(y_pred, [1, 0, 2])

    # Ensure y_true is of type int32 (or another allowed type)
    y_true = tf.cast(y_true, tf.int32)  # Cast to int32

    # Calculate input length (logit length) and label length
    logit_length = tf.fill([tf.shape(y_pred)[1]], tf.shape(y_pred)[0])  # shape: (batch_size,)
    label_length = tf.reduce_sum(tf.cast(tf.not_equal(y_true, 0), tf.int32), axis=1)  # shape: (batch_size,)

    # Compute the CTC loss using tf.nn.ctc_loss
    loss = tf.nn.ctc_loss(
        labels=y_true,
        logits=y_pred,
        label_length=label_length,
        logit_length=logit_length,
        logits_time_major=True,
        blank_index=0
    )

    return loss

def decode_predictions(logits, num_to_char):
    # Use CTC greedy decoder to convert logits to sequences
    decoded_predictions, _ = tf.nn.ctc_greedy_decoder(
        tf.transpose(logits, [1, 0, 2]),  # Transpose for time-major format
        tf.fill([tf.shape(logits)[0]], tf.shape(logits)[1])  # Input length
    )

    # Convert the sparse tensor to dense format
    dense_predictions = tf.sparse.to_dense(decoded_predictions[0], default_value=0)

    # Convert from numeric indices to characters using `num_to_char` mapping
    predicted_texts = [
        ''.join(num_to_char(index).numpy().decode('utf-8') for index in prediction if index > 0)
        for prediction in dense_predictions
    ]

    return predicted_texts

# === Serial Reading with Sliding Window ===
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
                    
                    # Keep printing the data to console
                    print(data)
                    
                    sensor_values = [float(value) for value in data[:len(feature_set)]]
                    all_buffer.append(sensor_values)

                    while len(all_buffer) >= window_size:
                        window_data = all_buffer[:window_size]

                        window_np = np.array(window_data, dtype=np.float32)
                        window_np = scaler.fit_transform(window_np)
                        window_np = window_np.reshape(1, window_size, window_np.shape[1])  # Ensure shape is (1, 48, feature_dim)

                        preds = model.predict(window_np)

                        pred = decode_predictions(preds, num_to_char)

                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                        predicted_characters[timestamp] = pred
                        prediction_writer.writerow([timestamp, pred])
                        prediction_queue.put((timestamp, pred))

                        all_buffer = all_buffer[window_step:]

    except Exception as e:
        print(f"Error: {e}")

# === Tkinter UI Setup ===
def start_ui(stop_event):
    root = tk.Tk()
    root.title("Real-Time Predictions")
    text_area = ScrolledText(root, width=80, height=20)
    text_area.pack(padx=10, pady=10)
    text_area.configure(state='disabled')

    def poll_predictions():
        try:
            while True:
                timestamp, pred = prediction_queue.get_nowait()
                message = f"[{timestamp}] => {pred}\n"
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

# === Load Trained Model ===
model_path = os.path.join(model_folder, model_filename)
try:
    model = load_model(model_path, custom_objects={'ctc_loss': ctc_loss_fn})
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

# === Main Execution ===
if __name__ == "__main__":
    stop_event = threading.Event()
    serial_thread = threading.Thread(target=serial_reading_thread, args=(stop_event,), daemon=True)
    serial_thread.start()
    start_ui(stop_event)
    serial_thread.join()
