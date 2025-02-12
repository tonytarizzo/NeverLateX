#include "AK09918.h"
#include "ICM20600.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// === OLED Display Configuration ===
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1  // Reset pin (not used)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

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
#define FORCE_SENSOR_PIN A0 

// === Optical Sensor (TCRT5000L) Setup ===
#define OPTIC_SENSOR_DIGITAL_PIN 3  // Digital Input (Presence Detection)
#define OPTIC_SENSOR_ANALOG_PIN A1  // Analog Input (Reflectance Level)

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

    // Initialize OLED Display
    if (!display.begin(SSD1306_I2C_ADDRESS, 0x3C)) {
        while (1);  // Stop if OLED fails
    }
    
    // Show "Waiting" screen initially
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(10, 20);
    display.println("Waiting...");
    display.display();
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
        } else {
            Serial.println("System Deactivated");
        }
    }

    // Perform actions based on the system state
    if (systemActive) {
        readSensors();
    }

    // Check for incoming prediction from Python
    if (Serial.available()) {
        String prediction = Serial.readStringUntil('\n'); // Read prediction from Python
        
        // Update OLED display
        display.clearDisplay();
        display.setCursor(10, 20);
        display.setTextSize(2);
        display.print("Pred: ");
        display.println(prediction);
        display.display();
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
    int forceReading = analogRead(FORCE_SENSOR_PIN);

    // === Get Optical Sensor Data (TCRT5000L) ===
    int optic_analog = analogRead(OPTIC_SENSOR_ANALOG_PIN);  

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
    Serial.print(forceReading);
    Serial.print(", ");
    Serial.println(optic_analog); 
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
