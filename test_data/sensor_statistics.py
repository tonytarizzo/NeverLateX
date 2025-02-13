import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# === Load Dataset ===
file_path = "/Users/tunakisaga/Documents/GitHub/NeverLateX/test_data/all_data_1.csv"  # Adjust if neecessary
df = pd.read_csv(file_path)

# === Identify Feature & Label Columns ===
feature_columns = df.columns[1:-1]  # All sensor data except the timestamp & label
label_column = df.columns[-1]  # The last column is the letter (label)

# Convert numerical data
df[feature_columns] = df[feature_columns].apply(pd.to_numeric, errors='coerce')

# === Summary Statistics by Letter ===
letter_stats = df.groupby(label_column)[feature_columns].describe()
print("\n📊 **Summary Statistics by Letter:**\n", letter_stats)

# === Create Subplots for Sensor Evolution ===
letters = df[label_column].unique()

for letter in letters:
    fig, axes = plt.subplots(3, 2, figsize=(12, 10))  # Create a 3x2 grid of plots
    fig.suptitle(f"Sensor Evolution for Letter: {letter}", fontsize=14, fontweight='bold')

    subset = df[df[label_column] == letter]

    # Plot Acceleration Values Over Time
    subset.plot(y=["Acc_X", "Acc_Y", "Acc_Z"], title="Acceleration (X, Y, Z)", ax=axes[0, 0])
    axes[0, 0].set_ylabel("Acceleration")

    # Plot Gyroscope Values Over Time
    subset.plot(y=["Gyro_X", "Gyro_Y", "Gyro_Z"], title="Gyroscope (X, Y, Z)", ax=axes[0, 1])
    axes[0, 1].set_ylabel("Gyroscope")

    # Plot Magnetometer Values Over Time
    subset.plot(y=["Mag_X", "Mag_Y", "Mag_Z"], title="Magnetometer (X, Y, Z)", ax=axes[1, 0])
    axes[1, 0].set_ylabel("Magnetometer")

    # Plot Force Sensor Values Over Time
    subset.plot(y=["Force"], title="Force Sensor Values", ax=axes[1, 1], color="red")
    axes[1, 1].set_ylabel("Force")

    # Plot Optic Sensor (`IR_A`) Values Over Time
    subset.plot(y=["IR_A"], title="Optic Sensor (IR_A)", ax=axes[2, 0], color="purple")
    axes[2, 0].set_ylabel("Optic Sensor (IR_A)")

    # Scatter Plot: Force vs. Optic Sensor (`IR_A`)
    sns.scatterplot(x=subset["Force"], y=subset["IR_A"], ax=axes[2, 1])
    axes[2, 1].set_title("Force vs. Optic Sensor (IR_A)")
    axes[2, 1].set_xlabel("Force")
    axes[2, 1].set_ylabel("IR_A (Optic Sensor)")

    plt.tight_layout()
    plt.show()

# === Correlation Analysis Between Force & Optic Sensors (`IR_A`) ===
corr_matrix = df[["Force", "IR_A"]].corr()
print("\n🔍 **Correlation Between Force and Optic Sensor (IR_A):**\n", corr_matrix)

# === Heatmap of Correlations ===
plt.figure(figsize=(6, 5))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Between Force and Optic Sensor (IR_A)")
plt.show()
