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
from tensorflow.keras import layers
from all_sensors.all_sensors.characters import get_complete_set
from sklearn.preprocessing import StandardScaler, LabelEncoder

# working directory should be NeverLateX
# run command: sudo python3 /Users/tunakisaga/Documents/GitHub/NeverLateX/all_sensors/all_sensors_with_prediction.py

# === Functions ===
def report_predicted_characters(predicted_characters):
    print("🔠 Predicted Characters: 🔠")
    for timestamp, letter in predicted_characters.items():
        print(f"{timestamp}: {letter}")

# Define a blank token for CTC decoding
dataset = get_complete_set()
characters = set(char for label in dataset for char in label)

##################################################################################################################################
           
# === Configuration ===
serial_port = '/dev/tty.usbmodem101'  # Change as needed (e.g., 'COM3' for Windows)
baud_rate = 115200  # Must match Arduino's baud rate
model_folder = "all_sensors/model_parameters"  # Folder containing trained models (.h5)
model_filename = "cldnn_cce_model.h5"  # Change based on the model to use ("cnn_model.h5" or "cldnn_model.h5")
file_name = "all_data.csv"
prediction_file_name = "predicted_characters.csv"
max_sequence_length = 1010  # Ensure consistency with model training

# === Load Trained Model ===
model_path = os.path.join(model_folder, model_filename)
if os.path.exists(model_path):
    print(f"✅ Loading model from: {model_path}")
    model = load_model(model_path)
else:
    print(f"❌ ERROR: Model file {model_path} not found!")
    model = None  # Prevent crashes if model is missing

# === Prepare CSV Logging ===
current_directory = os.getcwd()
file_path = os.path.join(current_directory, "all_sensors/test_data", file_name)
prediction_path = os.path.join(current_directory, "all_sensors/predicted_data",prediction_file_name)

# Define character set (ensure order matches training data)
noise = ['noise']
all_characters = noise + dataset

i = 0  # Tracks which character is being recorded
all_buffer = []  # Buffer to store all data during recording
predicted_characters = {}

# Initialize StandardScaler for consistency with training
scaler = StandardScaler()

# Define feature set for CSV
feature_set = ['Timestamp', 'Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z', 'Force1', 'Force2', 'Force3', 'Letter']

# === Open Serial Connection & CSV File ===
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(file_path, mode='w', newline='') as file, open(prediction_path, mode='w', newline='') as prediction_file:
        writer = csv.writer(file)
        writer.writerow(feature_set)

        prediction_writer = csv.writer(prediction_file)
        prediction_writer.writerow(['Timestamp', 'Best Prediction', 'Actual_Letter'])
        
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

                        prediction = model.predict(all_data_np)
                        label_encoder = LabelEncoder()
                        predicted_label = label_encoder.inverse_transform([np.argmax(prediction)])
                        predicted_label = predicted_label[0]
                        # Get current timestamp
                        now = datetime.now()
                        timestamp = str(now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}")
                        predicted_characters[timestamp] = predicted_label  # Store best prediction
                        prediction_writer.writerow([timestamp, predicted_label, all_characters[i]])
                        print(f"🔠 Best Prediction: {predicted_label}")   
                        
                    all_buffer.clear()  # Reset buffer after prediction
                    
                elif line == 'System Activated' and not firstLetter:
                    i += 1   
                    if i == len(all_characters)+1:
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


    