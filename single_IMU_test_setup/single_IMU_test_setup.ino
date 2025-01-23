#include "AK09918.h"
#include "ICM20600.h"
#include <Wire.h>

// IMU setup
AK09918 ak09918;
ICM20600 icm20600(true);
int16_t acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z;
int32_t mag_x, mag_y, mag_z;
int32_t offset_x, offset_y, offset_z;

void setup() {
    // Initialize serial communication
    Serial.begin(9600);

    // Initialize I2C and IMU
    Wire.begin();
    ak09918.initialize();
    icm20600.initialize();
    ak09918.switchMode(AK09918_POWER_DOWN);
    ak09918.switchMode(AK09918_CONTINUOUS_100HZ);

    // Calibrate IMU
    calibrateIMU();

    // System ready message
    // Serial.println("IMU System Initialized");
}

void loop() {
    // Continuously read and output IMU data
    readIMU();
    delay(500); // Adjust the delay as needed
}

void readIMU() {
    // Get accelerometer data
    acc_x = icm20600.getAccelerationX();
    acc_y = icm20600.getAccelerationY();
    acc_z = icm20600.getAccelerationZ();

    // Get gyroscope data
    gyro_x = icm20600.getGyroscopeX();
    gyro_y = icm20600.getGyroscopeY();
    gyro_z = icm20600.getGyroscopeZ();

    // Get magnetometer data
    ak09918.getData(&mag_x, &mag_y, &mag_z);

    // Adjust magnetometer data for offsets
    mag_x -= offset_x;
    mag_y -= offset_y;
    mag_z -= offset_z;

    /* // Output IMU data to Serial Monitor
    Serial.println("IMU Data:");
    Serial.print("Acc (X, Y, Z): ");
    Serial.print(acc_x); Serial.print(", ");
    Serial.print(acc_y); Serial.print(", ");
    Serial.println(acc_z);

    Serial.print("Gyro (X, Y, Z): ");
    Serial.print(gyro_x); Serial.print(", ");
    Serial.print(gyro_y); Serial.print(", ");
    Serial.println(gyro_z);

    Serial.print("Mag (X, Y, Z): ");
    Serial.print(mag_x); Serial.print(", ");
    Serial.print(mag_y); Serial.print(", ");
    Serial.println(mag_z); */

    // Output IMU data to Serial Monitor
    Serial.print(acc_x); Serial.print(", ");
    Serial.print(acc_y); Serial.print(", ");
    Serial.println(acc_z); Serial.print(", ");
    Serial.print(gyro_x); Serial.print(", ");
    Serial.print(gyro_y); Serial.print(", ");
    Serial.println(gyro_z); Serial.print(", ");
    Serial.print(mag_x); Serial.print(", ");
    Serial.print(mag_y); Serial.print(", ");
    Serial.println(mag_z);
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

    // Serial.println("IMU Calibration Complete");
}
