# !!!!!!!!! MAKE SURE TO CHECK THE MAX SEQUENCE LENGTH !!!!!!!!!

import serial
import csv
import time
from datetime import datetime
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import StandardScaler
import tensorflow.keras.backend as K

# working directory should be NeverLateX
# run command: sudo python3 /Users/tunakisaga/Documents/GitHub/NeverLateX/all_sensors/all_sensors_with_prediction.py

# === Functions ===
def report_predicted_characters(predicted_characters):
    print("🔠 Predicted Characters: 🔠")
    for timestamp, letter in predicted_characters.items():
        print(f"{timestamp}: {letter}")
        
def ctc_loss_fn(y_true, y_pred):
    # Cast labels to int32
    y_true = tf.cast(y_true, dtype=tf.int32)

    # Input length: Number of time steps for each input
    input_length = tf.fill([tf.shape(y_pred)[0]], tf.shape(y_pred)[1])

    # Label length: Actual length of each label
    label_length = tf.reduce_sum(tf.cast(tf.not_equal(y_true, 0), dtype=tf.int32), axis=1)

    # Compute CTC loss
    return tf.reduce_mean(
        tf.nn.ctc_loss(
            labels=y_true,
            logits=y_pred,
            label_length=label_length,
            logit_length=input_length,
            logits_time_major=False,
            blank_index=-1,  # Use the last class as the blank label
        )
    )
    
# Define label-to-character mapping based on provided mapping
index_to_char = {
    1: "A", 53: "B", 43: "C", 42: "D", 13: "E", 27: "F", 21: "G", 15: "H", 40: "I",
    49: "J", 4: "K", 61: "L", 22: "M", 6: "N", 20: "O", 57: "P", 62: "Q", 38: "R",
    16: "S", 56: "T", 2: "U", 52: "V", 29: "W", 59: "X", 36: "Y", 48: "Z", 47: "a",
    17: "b", 32: "c", 19: "d", 14: "e", 54: "f", 30: "g", 11: "h", 55: "i", 5: "j",
    44: "k", 18: "l", 9: "m", 46: "n", 34: "o", 28: "p", 8: "q", 10: "r", 45: "s",
    23: "t", 60: "u", 39: "v", 12: "w", 41: "x", 58: "y", 35: "z", 51: "0", 24: "1",
    3: "2", 26: "3", 33: "4", 37: "5", 50: "6", 31: "7", 7: "8", 25: "9"
}
          
def decode_predictions(pred, index_to_char=index_to_char):
    input_length = np.ones(pred.shape[0]) * pred.shape[1]
    decoded_preds, _ = tf.keras.ops.ctc_decode(pred, sequence_lengths=input_length, strategy="beam_search", top_paths=2)
    decoded_texts = []
    for decoded_seq in decoded_preds:
        decoded_text = "".join([index_to_char[idx] for idx in decoded_seq.numpy()[0] if idx in index_to_char])
        decoded_texts.append(decoded_text)
        
    print(f"Decoded Texts: {decoded_texts}")

    return decoded_texts[0], decoded_texts[1]  # Return best and second-best predictions
           
# === Configuration ===
serial_port = '/dev/tty.usbmodem101'  # Change as needed (e.g., 'COM3' for Windows)
baud_rate = 9600  # Must match Arduino's baud rate
model_folder = "model_parameters"  # Folder containing trained models (.h5)
model_filename = "cnn_model.h5"  # Change based on the model to use ("cnn_model.h5" or "cldnn_model.h5")
file_name = "all_data.csv"
prediction_file_name = "predicted_characters.csv"
max_sequence_length = 64  # Ensure consistency with model training

# === Load Trained Model ===
model_path = os.path.join(model_folder, model_filename)
if os.path.exists(model_path):
    print(f"✅ Loading model from: {model_path}")
    model = load_model(model_path, custom_objects={'ctc_loss_fn': ctc_loss_fn})
else:
    print(f"❌ ERROR: Model file {model_path} not found!")
    model = None  # Prevent crashes if model is missing

# === Prepare CSV Logging ===
current_directory = os.getcwd()
file_path = os.path.join(current_directory, "test_data", file_name)
prediction_path = os.path.join(current_directory, "predicted_data",prediction_file_name)

# Define character set (ensure order matches training data)
noise = ['noise']
english_alphabet_capital = [chr(i) for i in range(65, 91)]  # 'A' to 'Z'
english_alphabet_lower = [chr(i) for i in range(97, 123)]  # 'a' to 'z'
numbers = [str(i) for i in range(10)]  # '0' to '9'
all_characters = noise + english_alphabet_capital + english_alphabet_lower + numbers
char_to_index = {char: idx for idx, char in enumerate(all_characters)}

i = 0  # Tracks which character is being recorded
all_buffer = []  # Buffer to store all data during recording
predicted_characters = {}

# Initialize StandardScaler for consistency with training
scaler = StandardScaler()

# Define feature set for CSV
feature_set = ['Timestamp', 'Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z', 'Force', 'IR_A', 'Letter']

# === Open Serial Connection & CSV File ===
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(file_path, mode='w', newline='') as file, open(prediction_path, mode='w', newline='') as prediction_file:
        writer = csv.writer(file)
        writer.writerow(feature_set)

        prediction_writer = csv.writer(prediction_file)
        prediction_writer.writerow(['Timestamp', 'Best Prediction', 'Second Best Prediction', 'Actual_Letter'])
        
        print(f"📡 Logging data from {serial_port} to {file_path}...")
        print("📌 Press Ctrl+C to stop logging.")

        firstLetter = True
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                
                print("Line: ", line)

                # === Handle Start/Stop Recording ===
                if line == 'System Deactivated':
                    print("🛑 Recording stopped.")

                    if model is not None and len(all_buffer) > 0:
                        all_data_np = np.array(all_buffer, dtype=np.float32)
                        all_data_np = scaler.fit_transform(all_data_np)
                        all_data_np = pad_sequences([all_data_np], maxlen=max_sequence_length, padding='post', dtype='float32')
                        all_data_np = all_data_np.reshape(1, all_data_np.shape[1], all_data_np.shape[2])

                        preds = model.predict(all_data_np)
                        best_pred, second_best_pred = decode_predictions(preds)

                        # Get current timestamp
                        now = datetime.now()
                        timestamp = str(now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}")
                        predicted_characters[timestamp] = best_pred  # Store best prediction
                        prediction_writer.writerow([timestamp, best_pred, second_best_pred, all_characters[i]])
                        print(f"🔠 Best Prediction: {best_pred}, 🔹 Second Best: {second_best_pred}")   
                        
                    all_buffer.clear()  # Reset buffer after prediction
                    
                elif line == 'System Activated' and not firstLetter:
                    i += 1   
                    if i == len(all_characters):
                        print("✅ All characters successfully recorded.")
                        i = 0

                elif line == 'System Activated':
                    print("✅ System started recording...")
                    all_buffer.clear()

                # === Read All Data ===
                elif len(line.split(',')) == len(feature_set)-2:
                    
                    print("Data: ")
                    
                    data = line.split(',')

                    # Get current timestamp
                    now = datetime.now()
                    timestamp = now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}"
                    data = [timestamp] + data
                    data = data + [all_characters[i]]

                    # Write to CSV
                    writer.writerow(data)
                    print("Current letter: ", f"{all_characters[i]}, writing to file...")

                    # Store in buffer for prediction
                    all_buffer.append([float(value) for value in data[1:len(data)-1]])  # Exclude timestamp and label
                    firstLetter = False

            except Exception as e:
                print(f"⚠️ Error reading data: {e}")
                report_predicted_characters(predicted_characters)
                break

except KeyboardInterrupt:
    print("\n🛑 Logging stopped by user.")
    report_predicted_characters(predicted_characters)
except Exception as e:
    print(f"❌ Failed to open serial port or file: {e}")
    report_predicted_characters(predicted_characters)


    