import serial
import csv
import time
from datetime import datetime

# Configuration
serial_port = '/dev/tty.usbmodem101'  # Replace with your Arduino's serial port (e.g., 'COM3' for Windows, '/dev/ttyUSB0' for Linux)
baud_rate = 9600  # Must match the Arduino serial baud rate
output_file = 'imu_data.csv'  # Output file name

english_alphabet_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

all_characters = english_alphabet_letters + numbers
i=0

# Open the serial connection and CSV file
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(output_file, mode='w', newline='') as file:
        # Create a CSV writer and write the header row
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z', 'Force', 'Letter'])

        print(f"Logging data from {serial_port} to {output_file}...")
        print("Press Ctrl+C to stop logging.")

        firstLetter = True
        # Continuously read data from Arduino
        while True:
            try:
                # Read a line from the serial port
                line = ser.readline().decode('utf-8').strip()

                # If the line is not empty, process it
                if line == 'IMU System Deactivated':
                    print("Recording stopped.")
                elif line == 'IMU System Activated' and firstLetter is False:
                    i += 1   
                elif line == 'IMU System Activated' and firstLetter:       
                    print("System started.")      
                elif len(line.split(',')) == 10:
                    print(line)  # Print the raw data for debugging
                    data = line.split(',')  # Split the line into individual values
                    # Get the current timestamp with milliseconds
                    now = datetime.now()
                    timestamp = now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}"
                    data = [timestamp] + data
                    data = data + [all_characters[i]]
                    print("data: ",data)
                    writer.writerow(data)   
                    print("Data written to file")
                    firstLetter = False
                    
            except Exception as e:
                print(f"Error reading data: {e}")
                break
except KeyboardInterrupt:
    print("\nLogging stopped.")
except Exception as e:
    print(f"Failed to open serial port or file: {e}")
