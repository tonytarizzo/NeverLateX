import serial
import csv
import time

# Configuration
serial_port = '/dev/tty.usbmodem101'  # Replace with your Arduino's serial port (e.g., 'COM3' for Windows, '/dev/ttyUSB0' for Linux)
baud_rate = 9600  # Must match the Arduino serial baud rate
output_file = 'imu_data.csv'  # Output file name

# Open the serial connection and CSV file
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(output_file, mode='w', newline='') as file:
        # Create a CSV writer and write the header row
        writer = csv.writer(file)
        writer.writerow(['Acc_X', 'Acc_Y', 'Acc_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z'])

        print(f"Logging data from {serial_port} to {output_file}...")
        print("Press Ctrl+C to stop logging.")

        # Continuously read data from Arduino
        while True:
            try:
                # Read a line from the serial port
                line = ser.readline().decode('utf-8').strip()

                # If the line is not empty, process it
                if line:
                    print(line)  # Print the raw data for debugging
                    data = line.split(',')  # Split the line into individual values

                    """ # Ensure the data has 9 values (for all 9 axes)
                    if len(data) == 3:
                        writer.writerow(data)  # Save the data to the CSV file
                    else:
                        print("Invalid data format received. Skipping.") """
                    writer.writerow(data)  # Save the data to the CSV file
            except Exception as e:
                print(f"Error reading data: {e}")
                break
except KeyboardInterrupt:
    print("\nLogging stopped.")
except Exception as e:
    print(f"Failed to open serial port or file: {e}")
