import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Load Dataset ===
file_path = os.path.join(os.getcwd(), "all_sensors/test_data", "all_data_1.csv")  # Adjust if necessary
df = pd.read_csv(file_path)

# === Identify Feature & Label Columns ===
feature_columns = [col for col in df.columns[1:-1] if col != "IR_A"]  # Exclude the optical sensor
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
    subset.plot(y=["Force1", "Force2", "Force3"], title="Force Sensors (Force1, Force2, Force3)", ax=axes[1, 1], color=["red", "green", "blue"])
    axes[1, 1].set_ylabel("Force Sensors")

    # Remove unused plots
    axes[2, 0].remove()
    axes[2, 1].remove()

    plt.tight_layout()
    plt.show()

# === Correlation Analysis Between Remaining Sensors ===
remaining_columns = [col for col in df.columns if col not in ["IR_A", label_column]]
corr_matrix = df[remaining_columns].corr()
print("\n🔍 **Correlation Matrix of Remaining Sensors:**\n", corr_matrix)

# === Heatmap of Correlations ===
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Matrix of Remaining Sensors")
plt.show()
