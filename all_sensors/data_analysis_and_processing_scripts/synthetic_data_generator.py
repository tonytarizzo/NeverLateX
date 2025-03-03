import pandas as pd
import numpy as np
import os

# === Load Original Dataset ===
file_path = os.path.join(os.getcwd(), "all_sensors/test_data", "all_data_1.csv")  # Adjust if necessary
df = pd.read_csv(file_path)

# Extract directory from the file path
directory = os.path.dirname(file_path)

# Identify columns
feature_columns = df.columns[1:-1]  # Assuming first column is timestamp & last column is label
label_column = df.columns[-1]  # Last column is the letter (label)

# Convert sensor values to numeric
df[feature_columns] = df[feature_columns].apply(pd.to_numeric, errors='coerce')

# === Data Augmentation Functions ===
def add_gaussian_noise(data, noise_level=0.02):
    """Add Gaussian noise while keeping zeros unchanged."""
    noise = np.random.normal(loc=0, scale=noise_level, size=data.shape)
    data_with_noise = data + noise
    data_with_noise[data == 0] = 0  # Keep original zeros
    return data_with_noise

def jitter(data, jitter_level=0.01):
    """Apply jittering (small random shifts) while keeping zeros unchanged."""
    jitter_values = np.random.uniform(-jitter_level, jitter_level, size=data.shape)
    jittered_data = data + jitter_values
    jittered_data[data == 0] = 0  # Keep original zeros
    return jittered_data

def scale_variation(data, scale_range=(0.9, 1.1)):
    """Scale sensor values randomly within a given range while keeping zeros unchanged."""
    scale_factor = np.random.uniform(scale_range[0], scale_range[1], size=(1, data.shape[1]))
    scaled_data = data * scale_factor
    scaled_data[data == 0] = 0  # Keep original zeros
    return scaled_data

# === Generate and Save Synthetic Data Separately ===
num_synthetic_samples = 5  # Number of synthetic datasets

for i in range(num_synthetic_samples):
    augmented_df = df.copy()

    # Apply transformations only to numeric columns (exclude labels)
    augmented_df[feature_columns] = add_gaussian_noise(augmented_df[feature_columns])
    augmented_df[feature_columns] = jitter(augmented_df[feature_columns])
    augmented_df[feature_columns] = scale_variation(augmented_df[feature_columns])

    # Preserve labels
    augmented_df[label_column] = df[label_column]

    # Generate output file path within the same folder as the original
    synthetic_file_path = os.path.join(directory, f"synthetic_data_{i+1}.csv")
    augmented_df.to_csv(synthetic_file_path, index=False)
    print(f"✅ Synthetic dataset saved as {synthetic_file_path}")
