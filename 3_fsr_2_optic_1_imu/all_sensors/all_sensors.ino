#include "AK09918.h"
#include "ICM20600.h"
#include <Wire.h>

// === IMU Setup ===
AK09918 ak09918;
ICM20600 icm20600(true);

int16_t acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z;
int32_t mag_x, mag_y, mag_z;
int32_t offset_x, offset_y, offset_z;

// === Button Setup ===
#define BUTTON_PIN 12
bool buttonPressed = false;
bool systemActive = false;

// === Force Sensor Setup ===
#define FORCE_SENSOR1_PIN A0 
#define FORCE_SENSOR2_PIN ??
#define FORCE_SENSOR3_PIN ??

// === Optical Sensor (TCRT5000L) Setup ===
#define OPTIC_SENSOR1_ANALOG_PIN A1
#define OPTIC_SENSOR2_ANALOG_PIN ??

void setup() {
    // Initialize Serial Communication
    Serial.begin(9600);

    // Initialize I2C and Peripherals
    Wire.begin();

    // Initialize IMU
    ak09918.initialize();
    icm20600.initialize();
    ak09918.switchMode(AK09918_POWER_DOWN);
    ak09918.switchMode(AK09918_CONTINUOUS_100HZ);

    // Calibrate IMU
    calibrateIMU();

    // Button Setup
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    // Serial.println("Press button to activate/deactivate system");
}

void loop() {
    // Check button state
    static bool lastButtonState = HIGH;
    bool currentButtonState = digitalRead(BUTTON_PIN);

    if (lastButtonState == HIGH && currentButtonState == LOW) {
        buttonPressed = true;
        delay(100);  // Debounce delay
    }
    lastButtonState = currentButtonState;

    if (buttonPressed) {
        systemActive = !systemActive;  // Toggle system state
        buttonPressed = false;

        // Notify the user of the current state
        if (systemActive) {
            Serial.println("System Activated");
            // digitalWrite(OPTIC_SENSOR_DIGITAL_PIN, HIGH);
        } else {
            Serial.println("System Deactivated");
        }
    }

    // Perform actions based on the system state
    if (systemActive) {
        readSensors();
    }

    delay(100);  // Adjust the delay as needed
}

void readSensors() {
    // === Get Accelerometer Data ===
    acc_x = icm20600.getAccelerationX();
    acc_y = icm20600.getAccelerationY();
    acc_z = icm20600.getAccelerationZ();

    // === Get Gyroscope Data ===
    gyro_x = icm20600.getGyroscopeX();
    gyro_y = icm20600.getGyroscopeY();
    gyro_z = icm20600.getGyroscopeZ();

    // === Get Magnetometer Data ===
    ak09918.getData(&mag_x, &mag_y, &mag_z);

    // Adjust magnetometer data for offsets
    mag_x -= offset_x;
    mag_y -= offset_y;
    mag_z -= offset_z;

    // === Get Force Sensor Data ===
    int forceReading1 = analogRead(FORCE_SENSOR1_PIN);
    int forceReading2 = analogRead(FORCE_SENSOR2_PIN);
    int forceReading3 = analogRead(FORCE_SENSOR3_PIN);

    // // === Get Optical Sensor Data (TCRT5000L) ===
    int optic1_analog = analogRead(OPTIC_SENSOR1_ANALOG_PIN);  
    int optic2_analog = analogRead(OPTIC_SENSOR2_ANALOG_PIN);

    // === Output All Data to Serial Monitor (CSV Format) ===
    Serial.print(acc_x);
    Serial.print(", ");
    Serial.print(acc_y);
    Serial.print(", ");
    Serial.print(acc_z);
    Serial.print(", ");
    Serial.print(gyro_x);
    Serial.print(", ");
    Serial.print(gyro_y);
    Serial.print(", ");
    Serial.print(gyro_z);
    Serial.print(", ");
    Serial.print(mag_x);
    Serial.print(", ");
    Serial.print(mag_y);
    Serial.print(", ");
    Serial.print(mag_z);
    Serial.print(", ");
    Serial.print(forceReading1);
    Serial.print(", ");
    Serial.print(forceReading2);
    Serial.print(", ");
    Serial.print(forceReading3);
    Serial.print(", ");
    Serial.print(optic1_analog);
    Serial.print(", ");
    Serial.println(optic2_analog);
}

void calibrateIMU() {
    int32_t value_x_min = INT32_MAX, value_x_max = INT32_MIN;
    int32_t value_y_min = INT32_MAX, value_y_max = INT32_MIN;
    int32_t value_z_min = INT32_MAX, value_z_max = INT32_MIN;

    // Calibrate magnetometer offsets using 100 samples
    for (int i = 0; i < 100; i++) {
        ak09918.getData(&mag_x, &mag_y, &mag_z);
        value_x_min = min(value_x_min, mag_x);
        value_x_max = max(value_x_max, mag_x);
        value_y_min = min(value_y_min, mag_y);
        value_y_max = max(value_y_max, mag_y);
        value_z_min = min(value_z_min, mag_z);
        value_z_max = max(value_z_max, mag_z);
        delay(50);
    }

    offset_x = (value_x_min + value_x_max) / 2;
    offset_y = (value_y_min + value_y_max) / 2;
    offset_z = (value_z_min + value_z_max) / 2;

    Serial.println("IMU Calibration Complete");
}