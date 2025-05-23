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
from characters import get_complete_set
import unicodedata


# working directory should be NeverLateX
# run command: sudo python3 /Users/tunakisaga/Documents/GitHub/NeverLateX/all_sensors/all_sensors_without_prediction.py

# === Configuration ===
# serial_port = '/dev/tty.usbmodem101'  # Change as needed (e.g., 'COM3' for Windows)
serial_port = '/dev/tty.usbmodem1101'
# serial_port = 'COM5' # For windows / fajar's PC
baud_rate = 115200  # Must match Arduino's baud rate
file_name = "all_data.csv"
max_sequence_length = 64  # Ensure consistency with model training

# # === Prepare CSV Logging ===
# current_directory = os.getcwd()
# file_path = os.path.join(current_directory, "all_sensors\\all_sensors\\full_prototype_dataset", file_name)

# === Prepare CSV Logging ===
current_directory = os.getcwd()
# folder_path = os.path.join(current_directory, "test_data\\full_prototype_dataset")
folder_path = os.path.join(current_directory, "test_data/full_prototype_dataset")

# Ensure the directory exists
os.makedirs(folder_path, exist_ok=True)

# Generate a unique file name
base_file_name = "new_all_data"
file_extension = ".csv"

file_number = 30
file_name = f"{base_file_name}{file_number}{file_extension}"
file_path = os.path.join(folder_path, file_name)

# Check if the file already exists, and increment the number if needed
while os.path.exists(file_path):
    file_number += 1
    file_name = f"{base_file_name}{file_number}{file_extension}"
    file_path = os.path.join(folder_path, file_name)

# print(f"📁 Saving data to: {file_path}")


# Define character set (ensure order matches training data)
noise = ['noise']
dataset = get_complete_set()
all_characters = noise + dataset

# print("🔍 Character set:", all_characters)


i = 0  # Tracks which character is being recorded
feature_set = ['Timestamp', 'Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z', 'Force1', 'Force2', 'Force3', 'Letter']

# Initialize StandardScaler for consistency with training
scaler = StandardScaler()

buffer = []  # Buffer to store all data during recording

# === Open Serial Connection & CSV File ===
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(feature_set)
        
        print(f"📡 Logging data from {serial_port} to {file_path}...")
        print("📌 Press Ctrl+C to stop logging.")

        firstLetter = True
        while True:
            try:
                line = unicodedata.normalize('NFC', ser.readline().decode('utf-8').strip())

                # === Handle Start/Stop Recording ===
                if line == 'System Deactivated':
                    print("🛑 Recording stopped.")
                    
                elif line == 'System Activated' and not firstLetter:
                    i += 1   
                    if i == len(all_characters)+1:
                        print("✅ All characters successfully recorded.")
                        i = 0

                elif line == 'System Activated':
                    print("✅ System started recording...")

                elif len(line.split(',')) == (len(feature_set)-2):
                    
                    # print(line)  # Debugging
                    data = line.split(',')

                    # Get current timestamp
                    now = datetime.now()
                    timestamp = now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}"
                    data = [timestamp] + data
                    data = data + [all_characters[i]]
                    
                    print(data)

                    # Write to CSV
                    writer.writerow(data)
                    print("Current letter: ", f"{all_characters[i]}, writing to file...")
                    
                    firstLetter = False

            except Exception as e:
                print(f"⚠️ Error reading data: {e}")
                break

except KeyboardInterrupt:
    print("\n🛑 Logging stopped by user.")
except Exception as e:
    print(f"❌ Failed to open serial port or file: {e}")


    