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
from characters import get_complete_set

# working directory should be NeverLateX
# run command: sudo python3 /Users/tunakisaga/Documents/GitHub/NeverLateX/all_sensors/all_sensors_only_prediction.py

# === Functions ===
def report_predicted_characters(predicted_characters):
    print("🔠 Predicted Characters: 🔠")
    for timestamp, letter in predicted_characters.items():
        print(f"{timestamp}: {letter}")
        
def ctc_loss(y_true, y_pred):
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

# Define a blank token for CTC decoding
blank_token = '-'
dataset = get_complete_set()
characters = set(char for label in dataset for char in label)
# Update the StringLookup layers with the extended vocabulary
char_to_num = layers.StringLookup(
    vocabulary=list(characters), mask_token=None, oov_token=blank_token
)
num_to_char = layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True
)

##################################################################################################################################
           
# === Configuration ===
serial_port = '/dev/tty.usbmodem101'  # Change as needed (e.g., 'COM3' for Windows)
baud_rate = 9600  # Must match Arduino's baud rate
model_folder = "all_sensors/model_parameters"  # Folder containing trained models (.h5)
model_filename = "cnn_model.h5"  # Change based on the model to use ("cnn_model.h5" or "cldnn_model.h5")
prediction_file_name = "predicted_characters.csv"
max_sequence_length = 64  # Ensure consistency with model training

# === Load Trained Model ===
model_path = os.path.join(model_folder, model_filename)
if os.path.exists(model_path):
    print(f"✅ Loading model from: {model_path}")
    model = load_model(model_path, custom_objects={'ctc_loss_fn': ctc_loss})
else:
    print(f"❌ ERROR: Model file {model_path} not found!")
    model = None  # Prevent crashes if model is missing

# === Prepare CSV Logging ===
current_directory = os.getcwd()
prediction_path = os.path.join(current_directory, "all_sensors/predicted_data", prediction_file_name)

# Define character set (ensure order matches training data)
noise = ['noise']
all_characters = noise + dataset

all_buffer = []  # Buffer to store all data during recording
predicted_characters = {}

# Initialize StandardScaler for consistency with training
scaler = StandardScaler()

# Define feature set for CSV 
feature_set = ['Timestamp', 'Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z', 'Force1', 'Force2', 'Force3', 'Letter']

# === Open Serial Connection & CSV File ===
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(prediction_path, mode='w', newline='') as prediction_file:
        prediction_writer = csv.writer(prediction_file)
        prediction_writer.writerow(['Timestamp', 'Best Prediction'])

        while True:
            try:
                line = ser.readline().decode('utf-8').strip()

                # === Handle Start/Stop Recording ===
                if line == 'System Deactivated':
                    print("🛑 Recording stopped. See the prediction below:\n")

                    if model is not None and len(all_buffer) > 0:
                        all_data_np = np.array(all_buffer, dtype=np.float32)
                        all_data_np = scaler.fit_transform(all_data_np)
                        all_data_np = pad_sequences([all_data_np], maxlen=max_sequence_length, padding='post', dtype='float32')
                        all_data_np = all_data_np.reshape(1, all_data_np.shape[1], all_data_np.shape[2])

                        preds = model.predict(all_data_np)
                        pred = decode_predictions(preds)

                        # Get current timestamp
                        now = datetime.now()
                        timestamp = str(now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}")
                        predicted_characters[timestamp] = pred  # Store best prediction
                        prediction_writer.writerow([timestamp, pred])
                        print(f"🔠 Best Prediction: {pred}")
                        
                    all_buffer.clear()  # Reset buffer after prediction

                elif line == 'System Activated':
                    print("✅ System started predicting...")
                    all_buffer.clear()

                # === Read All Data ===
                elif len(line.split(',')) == len(feature_set)-2:
                    data = line.split(',')
                    # Store in buffer for prediction
                    all_buffer.append([float(value) for value in data[0:len(feature_set)]])  # Exclude timestamp and label  
                    firstLetter = False

            except Exception as e:
                print(f"⚠️ Error predicting data: {e}")
                report_predicted_characters(predicted_characters)
                break

except KeyboardInterrupt:
    print("\n🛑 Prediction stopped by user.")
    report_predicted_characters(predicted_characters)
except Exception as e:
    print(f"❌ Failed to open serial port or file: {e}")
    report_predicted_characters(predicted_characters)


    