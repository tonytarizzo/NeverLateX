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
# run command: sudo python3 /Users/tunakisaga/Documents/GitHub/NeverLateX/all_sensors/all_sensors_without_prediction.py
           
# === Configuration ===
serial_port = '/dev/tty.usbmodem101'  # Change as needed (e.g., 'COM3' for Windows)
baud_rate = 9600  # Must match Arduino's baud rate
model_folder = "model_parameters"  # Folder containing trained models (.h5)
model_filename = "cnn_model.h5"  # Change based on the model to use ("cnn_model.h5" or "cldnn_model.h5")
file_name = "all_data.csv"
max_sequence_length = 27  # Ensure consistency with model training

# === Prepare CSV Logging ===
current_directory = os.getcwd()
file_path = os.path.join(current_directory, file_name)

# Define character set (ensure order matches training data)
noise = ['noise']
english_alphabet_capital = [chr(i) for i in range(65, 91)]  # 'A' to 'Z'
english_alphabet_lower = [chr(i) for i in range(97, 123)]  # 'a' to 'z'
numbers = [str(i) for i in range(10)]  # '0' to '9'
all_characters = noise + english_alphabet_capital + english_alphabet_lower + numbers
char_to_index = {char: idx for idx, char in enumerate(all_characters)}

i = 0  # Tracks which character is being recorded
all_buffer = []  # Buffer to store all data during recording

# Initialize StandardScaler for consistency with training
scaler = StandardScaler()

# === Open Serial Connection & CSV File ===
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        feature_set = ['Timestamp', 'Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z', 'Force', 'IR_A', 'Letter']
        writer.writerow(feature_set)
        
        print(f"📡 Logging data from {serial_port} to {file_path}...")
        print("📌 Press Ctrl+C to stop logging.")

        firstLetter = True
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()

                # === Handle Start/Stop Recording ===
                if line == 'System Deactivated':
                    print("🛑 Recording stopped.")
                        
                    all_buffer.clear()  # Reset buffer after prediction
                    
                elif line == 'System Activated' and not firstLetter:
                    i += 1   
                    if i == len(all_characters):
                        print("✅ All characters successfully recorded.")
                        i = 0

                elif line == 'System Activated':
                    print("✅ System started recording...")
                    all_buffer.clear()

                elif len(line.split(',')) == (len(feature_set)-2):
                    print(line)  # Debugging
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
                    all_buffer.append([float(value) for value in data[1:(len(feature_set)-1)]])  # Exclude timestamp and label
                    
                    firstLetter = False

            except Exception as e:
                print(f"⚠️ Error reading data: {e}")
                break

except KeyboardInterrupt:
    print("\n🛑 Logging stopped by user.")
except Exception as e:
    print(f"❌ Failed to open serial port or file: {e}")


    