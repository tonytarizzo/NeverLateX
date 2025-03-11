import serial
import csv
import time
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import StandardScaler
import tensorflow.keras.backend as K
from tensorflow.keras import layers
from all_sensors.all_sensors.characters import get_complete_set
from datetime import datetime

# For UI
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import queue

# === Functions ===
def report_predicted_characters(predicted_characters):
    print("🔠 Predicted Characters: 🔠")
    for timestamp, letter in predicted_characters.items():
        print(f"{timestamp}: {letter}")

def ctc_loss(y_true, y_pred):
    # Transpose y_pred if using logits_time_major=True (to [max_time, batch_size, num_classes])
    y_pred = tf.transpose(y_pred, [1, 0, 2])
    y_true = tf.cast(y_true, tf.int32)
    logit_length = tf.fill([tf.shape(y_pred)[1]], tf.shape(y_pred)[0])
    label_length = tf.reduce_sum(tf.cast(tf.not_equal(y_true, 0), tf.int32), axis=1)
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
        tf.fill([tf.shape(logits)[0]], tf.shape(logits)[1])
    )
    dense_predictions = tf.sparse.to_dense(decoded_predictions[0], default_value=0)
    predicted_texts = [
        ''.join(num_to_char(index).numpy().decode('utf-8') for index in prediction if index > 0)
        for prediction in dense_predictions
    ]
    return predicted_texts

# === Setup Characters & Model ===
blank_token = '-'
dataset = get_complete_set()
characters = set(char for label in dataset for char in label)
# Create StringLookup layers
char_to_num = layers.StringLookup(vocabulary=list(characters), mask_token=None, oov_token=blank_token)
num_to_char = layers.StringLookup(vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True)

# === Configuration ===
serial_port = '/dev/tty.usbmodem101'  # Adjust as needed (e.g., 'COM3' for Windows)
baud_rate = 9600                     # Must match Arduino's baud rate
model_folder = "all_sensors/model_parameters"
model_filename = "cnn_model.h5"      # Change if using another model
prediction_file_name = "predicted_characters.csv"
max_sequence_length = 64             # Ensure consistency with model training

# Load Trained Model
model_path = os.path.join(model_folder, model_filename)
if os.path.exists(model_path):
    print(f"✅ Loading model from: {model_path}")
    model = load_model(model_path, custom_objects={'ctc_loss_fn': ctc_loss})
else:
    print(f"❌ ERROR: Model file {model_path} not found!")
    model = None  # Prevent crashes if model is missing

# Prepare CSV Logging
current_directory = os.getcwd()
prediction_path = os.path.join(current_directory, "all_sensors/predicted_data", prediction_file_name)

# Define character set (ensure order matches training data)
noise = ['noise']
all_characters = noise + dataset

# Buffer for sensor data and predictions
all_buffer = []
predicted_characters = {}

# Initialize StandardScaler (must be consistent with training)
scaler = StandardScaler()

# Define feature set for CSV logging 
feature_set = ['Timestamp', 'Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z', 
               'Mag_X', 'Mag_Y', 'Mag_Z', 'Force1', 'Force2', 'Force3', 'Letter']

# === Setup a Queue to Communicate Predictions to the UI ===
prediction_queue = queue.Queue()

def serial_reading_thread(stop_event):
    """
    Thread function to continuously read from the serial port,
    perform predictions, and push new predictions to the prediction_queue.
    """
    try:
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser, \
             open(prediction_path, mode='w', newline='') as prediction_file:
            
            prediction_writer = csv.writer(prediction_file)
            prediction_writer.writerow(['Timestamp', 'Best Prediction'])
            
            while not stop_event.is_set():
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if not line:
                        continue

                    # === Handle Start/Stop Recording ===
                    if line == 'System Deactivated':
                        print("🛑 Recording stopped. Processing prediction...\n")
                        if model is not None and len(all_buffer) > 0:
                            all_data_np = np.array(all_buffer, dtype=np.float32)
                            all_data_np = scaler.fit_transform(all_data_np)
                            all_data_np = pad_sequences([all_data_np], maxlen=max_sequence_length, 
                                                         padding='post', dtype='float32')
                            all_data_np = all_data_np.reshape(1, all_data_np.shape[1], all_data_np.shape[2])
                            
                            preds = model.predict(all_data_np)
                            pred = decode_predictions(preds, num_to_char)
                            
                            # Get current timestamp
                            now = datetime.now()
                            timestamp = now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}"
                            predicted_characters[timestamp] = pred
                            prediction_writer.writerow([timestamp, pred])
                            print(f"🔠 Best Prediction: {pred}")
                            
                            # Push prediction to UI queue
                            prediction_queue.put((timestamp, pred))
                        all_buffer.clear()
                    
                    elif line == 'System Activated':
                        print("✅ System activated. Start predicting...")
                        all_buffer.clear()
                    
                    # === Read Sensor Data ===
                    elif len(line.split(',')) == len(feature_set) - 2:
                        data = line.split(',')
                        # Append sensor data (cast to float)
                        all_buffer.append([float(value) for value in data[0:len(feature_set)]])
                
                except Exception as e:
                    print(f"⚠️ Error processing data: {e}")
                    report_predicted_characters(predicted_characters)
                    break
    except Exception as e:
        print(f"❌ Failed to open serial port or file: {e}")
        report_predicted_characters(predicted_characters)

    report_predicted_characters(predicted_characters)

# === Tkinter UI Setup ===
def start_ui(stop_event):
    root = tk.Tk()
    root.title("NeverLateX Real-Time Handwriting Predictions")
    root.configure(bg="white")
    
    # Title label with project information
    title_text = ("This UI shows predictions of real-time handwriting using a sensor-equipped pen "
                  "developed by NeverLateX team for the AML lab project for MSc in AML at Imperial College London")
    title_label = tk.Label(root, text=title_text, bg="white", fg="black",
                           font=("Helvetica", 12, "italic"), wraplength=600, justify="center")
    title_label.pack(pady=(10, 20))
    
    # ScrolledText widget to display predictions
    text_area = ScrolledText(root, width=80, height=20, bg="white", relief="flat", borderwidth=0)
    text_area.pack(padx=10, pady=10)
    text_area.configure(state='disabled')
    
    # Configure tag for predictions (bold blue text)
    text_area.tag_configure("prediction", foreground="#003af5", font=("Helvetica", 14, "bold"))
    
    def poll_predictions():
        """Check queue for new predictions and update the UI."""
        try:
            while True:
                timestamp, pred = prediction_queue.get_nowait()
                message = f"[{timestamp}] => {pred}\n"
                text_area.configure(state='normal')
                text_area.insert(tk.END, message, "prediction")
                text_area.see(tk.END)
                text_area.configure(state='disabled')
        except queue.Empty:
            pass
        # Continue polling every 100ms
        if not stop_event.is_set():
            root.after(100, poll_predictions)
    
    poll_predictions()
    root.mainloop()
    stop_event.set()

if __name__ == "__main__":
    # Create a stop event to signal threads to stop gracefully
    stop_event = threading.Event()
    
    # Start the serial reading thread (daemon thread so it terminates with the main thread)
    serial_thread = threading.Thread(target=serial_reading_thread, args=(stop_event,), daemon=True)
    serial_thread.start()
    
    # Start the UI in the main thread
    start_ui(stop_event)
    
    # Wait for serial thread to finish after UI closes
    serial_thread.join()
