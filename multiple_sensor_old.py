import serial
import time
import math

# Serial setup
SERIAL_PORT = "COM3"  # Update to your Arduino's serial port
BAUD_RATE = 9600

# Sensor states
class SensorState:
    OFF = 0
    IMU = 1
    FLEX = 2
    FORCE = 3

current_state = SensorState.OFF
button_pressed = False

# Function to read IMU data
def read_imu(data):
    # Parse the data for accelerometer and magnetometer readings
    acc_x, acc_y, acc_z = map(int, data["acc"].split(","))
    mag_x, mag_y, mag_z = map(int, data["mag"].split(","))

    # Calculate roll and pitch
    roll = math.atan2(acc_y, acc_z)
    pitch = math.atan2(-acc_x, math.sqrt(acc_y ** 2 + acc_z ** 2))

    print(f"IMU Data:")
    print(f"Acc: X={acc_x}, Y={acc_y}, Z={acc_z}")
    print(f"Mag: X={mag_x}, Y={mag_y}, Z={mag_z}")
    print(f"Roll: {math.degrees(roll):.2f}°, Pitch: {math.degrees(pitch):.2f}°")

# Function to read force sensor data
def read_force_sensor(data):
    force_value = int(data["force"])
    print(f"Force Sensor Reading: {force_value}")

# Function to read flex sensor data
def read_flex_sensor(data):
    flex_value = int(data["flex"])
    print(f"Flex Sensor Reading: {flex_value}")

# Function to handle serial data
def process_serial_data(serial_line):
    try:
        data = eval(serial_line.decode("utf-8").strip())
        if "button" in data and data["button"] == "pressed":
            global current_state, button_pressed
            button_pressed = True
            current_state = (current_state + 1) % 4  # Cycle through states

        if current_state == SensorState.IMU:
            read_imu(data)
        elif current_state == SensorState.FLEX:
            read_flex_sensor(data)
        elif current_state == SensorState.FORCE:
            read_force_sensor(data)
    except Exception as e:
        print(f"Error processing data: {e}")

# Main loop
def main():
    global button_pressed
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    time.sleep(2)  # Wait for Arduino to reset

    print("System Initialized. Listening for data...")

    while True:
        if ser.in_waiting > 0:
            serial_line = ser.readline()
            process_serial_data(serial_line)

        if button_pressed:
            button_pressed = False
            print(f"Current State: {['OFF', 'IMU', 'FLEX', 'FORCE'][current_state]}")

if __name__ == "__main__":
    main()
