import pandas as pd
import numpy as np

num_files = 50
folder_path = "test_data/fajar_data/"
output_folder_path = "test_data/fajar_data_calibrated/"
for i in range(num_files):
    # === Load Data ===
    file_path = f"all_data_{i+1}.csv"  
    file_path = folder_path + file_path
    df = pd.read_csv(file_path)

    # === Step 1: Compute Roll & Pitch from Accelerometer ===
    def compute_roll_pitch(acc_x, acc_y, acc_z):
        roll = np.arctan2(-acc_y, acc_z) * 180.0 / np.pi
        pitch = np.arctan2(acc_x, np.sqrt(acc_y**2 + acc_z**2)) * 180.0 / np.pi
        return roll, pitch

    df["Roll"], df["Pitch"] = zip(*df.apply(lambda row: compute_roll_pitch(row["Acc_X"], row["Acc_Y"], row["Acc_Z"]), axis=1))

    # === Step 3: Gravity Compensation ===
    def apply_gravity_compensation(acc_x, acc_y, acc_z, roll, pitch):
        gravity_x = -np.sin(np.radians(pitch)) * 1000
        gravity_y = np.cos(np.radians(pitch)) * np.sin(np.radians(roll)) * 1000
        gravity_z = np.cos(np.radians(pitch)) * np.cos(np.radians(roll)) * 1000

        lin_acc_x = acc_x - gravity_x
        lin_acc_y = acc_y - gravity_y
        lin_acc_z = acc_z - gravity_z

        return lin_acc_x, lin_acc_y, lin_acc_z

    df["Lin_Acc_X"], df["Lin_Acc_Y"], df["Lin_Acc_Z"] = zip(*df.apply(
        lambda row: apply_gravity_compensation(row["Acc_X"], row["Acc_Y"], row["Acc_Z"], row["Roll"], row["Pitch"]),
        axis=1
    ))

    # === Step 4: Save Calibrated Data ===
    output_file_path = f"all_data_{i+1}.csv"  
    output_file_path = output_folder_path + output_file_path
    df.to_csv(output_file_path, index=False)

    print(f"Calibration complete! Saved as '{output_file_path}'")
