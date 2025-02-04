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

# working directory should be NeverLateX
# run command: sudo python3 /Users/tunakisaga/Documents/GitHub/NeverLateX/IMU_and_force_and_optic_to_CSV_setup/without_prediction.py

""" # === Functions ===
def report_predicted_letters(predicted_letters):
    print("🔠 Predicted Letters: 🔠")
    for timestamp, letter in predicted_letters.items():
        print(f"{timestamp}: {letter}")
        
def ctc_loss_fn(y_true, y_pred):
    # Cast labels to int32
    y_true = tf.cast(y_true, dtype=tf.int32)

    # Input length: Number of time steps for each input
    input_length = tf.fill([tf.shape(y_pred)[0]], tf.shape(y_pred)[1])

    # Label length: Actual length of each label
    label_length = tf.reduce_sum(tf.cast(tf.not_equal(y_true, 0),
                                         dtype=tf.int32), axis=1)

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
          
class CTCAccuracy(tf.keras.metrics.Metric):
    def __init__(self, name="ctc_accuracy", **kwargs):
        super(CTCAccuracy, self).__init__(name=name, **kwargs)
        self.correct_predictions = self.add_weight(name="correct", initializer="zeros", dtype=tf.float32)
        self.total_samples = self.add_weight(name="total", initializer="zeros", dtype=tf.float32)

    def update_state(self, y_true, y_pred, sample_weight=None):
        # Decode predictions using greedy search
        y_pred_decoded, _ = K.ctc_decode(y_pred,
                                         input_length=tf.fill([tf.shape(y_pred)[0]], tf.shape(y_pred)[1]),
                                         greedy=True)

        # Ensure we are working with a sparse tensor before converting to dense
        if isinstance(y_pred_decoded[0], tf.SparseTensor):
            y_pred_dense = tf.sparse.to_dense(y_pred_decoded[0], default_value=-1)
        else:
            y_pred_dense = y_pred_decoded[0]  # If already dense, use it directly

        # Convert ground truth labels to int32
        y_true_dense = tf.cast(y_true, dtype=tf.int32)
        y_pred_dense = tf.cast(y_pred_dense, dtype=tf.int32)  # Ensure both are int32

        # Compute correct predictions by checking element-wise equality
        correct = tf.reduce_sum(tf.cast(tf.reduce_all(tf.equal(y_true_dense, y_pred_dense), axis=-1), dtype=tf.float32))
        total = tf.cast(tf.shape(y_true_dense)[0], dtype=tf.float32)

        # Update the accuracy metric
        self.correct_predictions.assign_add(correct)
        self.total_samples.assign_add(total)

    def result(self):
        return self.correct_predictions / (self.total_samples + K.epsilon())

    def reset_state(self):
        self.correct_predictions.assign(0.0)
        self.total_samples.assign(0.0) """
           
# === Configuration ===
serial_port = '/dev/tty.usbmodem101'  # Change as needed (e.g., 'COM3' for Windows)
baud_rate = 9600  # Must match Arduino's baud rate
model_folder = "model_parameters"  # Folder containing trained models (.h5)
model_filename = "cnn_model.h5"  # Change based on the model to use ("cnn_model.h5" or "cldnn_model.h5")
file_name = "imu_data.csv"
""" prediction_file_name = "predicted_letters.csv" """
max_sequence_length = 27  # Ensure consistency with model training

""" # === Load Trained Model ===
model_path = os.path.join(model_folder, model_filename)
if os.path.exists(model_path):
    print(f"✅ Loading model from: {model_path}")
    model = load_model(model_path, custom_objects={'ctc_loss_fn': ctc_loss_fn, 'CTCAccuracy': CTCAccuracy})
else:
    print(f"❌ ERROR: Model file {model_path} not found!")
    model = None  # Prevent crashes if model is missing """

# === Prepare CSV Logging ===
current_directory = os.getcwd()
file_path = os.path.join(current_directory, file_name)
""" prediction_path = os.path.join(current_directory, prediction_file_name) """

# Define character set (ensure order matches training data)
noise = ['noise']
english_alphabet_capital = [chr(i) for i in range(65, 91)]  # 'A' to 'Z'
english_alphabet_lower = [chr(i) for i in range(97, 123)]  # 'a' to 'z'
numbers = [str(i) for i in range(10)]  # '0' to '9'
all_characters = noise + english_alphabet_capital + english_alphabet_lower + numbers
char_to_index = {char: idx for idx, char in enumerate(all_characters)}

i = 0  # Tracks which character is being recorded
imu_buffer = []  # Buffer to store IMU data during recording
""" predicted_letters = {} """

# Initialize StandardScaler for consistency with training
scaler = StandardScaler()

# === Open Serial Connection & CSV File ===
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z', 'Force', 'Optic_D', 'Optic_A', 'Letter'])

        """ prediction_writer = csv.writer(prediction_file)
        prediction_writer.writerow(['Timestamp', 'Predicted_Letter', 'Actual_Letter']) """
        
        print(f"📡 Logging data from {serial_port} to {file_path}...")
        print("📌 Press Ctrl+C to stop logging.")

        firstLetter = True
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()

                # === Handle Start/Stop Recording ===
                if line == 'IMU System Deactivated':
                    print("🛑 Recording stopped.")

                    """ if model is not None and len(imu_buffer) > 0:
                        # Convert buffered data to NumPy array
                        imu_data_np = np.array(imu_buffer, dtype=np.float32)

                        # Normalize using the same scaler as in training
                        imu_data_np = scaler.fit_transform(imu_data_np)

                        # Pad the sequence to match model's expected input size
                        imu_data_np = pad_sequences([imu_data_np], maxlen=max_sequence_length, padding='post', dtype='float32')

                        # Reshape for model (batch_size=1, time_steps, features)
                        imu_data_np = imu_data_np.reshape(1, imu_data_np.shape[1], imu_data_np.shape[2])

                        # Make prediction
                        predictions = model.predict(imu_data_np)
                        predicted_label_index = np.argmax(predictions)  # Get the predicted class index
                        predicted_letter = all_characters[predicted_label_index]

                        print(f"🔠 **Predicted Letter: {predicted_letter}**")
                        
                        # Get current timestamp
                        now = datetime.now()
                        timestamp = str(now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}")
                        # Store predicted letter for later analysis
                        predicted_letters[timestamp] = predicted_letter              
                        prediction_data = [timestamp, predicted_letter, all_characters[i]]
                        # Write to CSV
                        prediction_writer.writerow(prediction_data)  """   
                        
                    imu_buffer.clear()  # Reset buffer after prediction
                    
                elif line == 'IMU System Activated' and not firstLetter:
                    i += 1   
                    if i == len(all_characters):
                        print("✅ All characters successfully recorded.")
                        i = 0

                elif line == 'IMU System Activated':
                    print("✅ System started recording...")
                    imu_buffer.clear()

                # === Read IMU Data ===
                elif len(line.split(',')) == 12:
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
                    imu_buffer.append([float(value) for value in data[1:13]])  # Exclude timestamp and label
                    
                    firstLetter = False

            except Exception as e:
                print(f"⚠️ Error reading data: {e}")
                """ report_predicted_letters(predicted_letters) """
                break

except KeyboardInterrupt:
    print("\n🛑 Logging stopped by user.")
    """ report_predicted_letters(predicted_letters) """
except Exception as e:
    print(f"❌ Failed to open serial port or file: {e}")
    """ report_predicted_letters(predicted_letters) """


    