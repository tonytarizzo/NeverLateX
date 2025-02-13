import pandas as pd
import os

# === Function to Trim Leading & Trailing Zero-Force Rows ===
def trim_force_zeros(sub_df, force_column="Force"):
    """Removes leading and trailing zero-force rows while preserving inner zeros."""
    force_values = sub_df[force_column].values

    # Find indices where force is nonzero
    nonzero_indices = [i for i, v in enumerate(force_values) if v > 0]

    if nonzero_indices:
        start, end = min(nonzero_indices), max(nonzero_indices)
        return sub_df.iloc[start : end + 1]  # Keep only relevant rows
    else:
        return sub_df  # If all zeros, return as is

# === Function to Process Multiple Files ===
def process_files(file_paths, directories):
    for file_path, directory in zip(file_paths, directories):
        try:
            # Load dataset
            print(f"📂 Processing: {file_path}")
            df = pd.read_csv(file_path)

            # Identify columns
            force_column = "Force"  # Adjust column name if necessary
            label_column = "Letter"  # Adjust label column if necessary

            # Convert force values to numeric
            df[force_column] = pd.to_numeric(df[force_column], errors="coerce")

            # Apply trimming function to each letter group
            cleaned_df = df.groupby(label_column, group_keys=False).apply(trim_force_zeros)

            # Generate output file path within the same folder as the original
            cleaned_file_path = file_path.replace(".csv", "_cleaned.csv")
            cleaned_file_path = os.path.join(directory, cleaned_file_path)

            # Save cleaned dataset
            cleaned_df.to_csv(cleaned_file_path, index=False)
            print(f"✅ Cleaned dataset saved as {cleaned_file_path}\n")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

# === User Input for Multiple File Paths ===
file_paths = [
    os.path.join(os.getcwd(), "test_data", "all_data_1.csv") # Add more file paths as needed
]
directories = [os.path.dirname(file_path) for file_path in file_paths]

# Process all files
process_files(file_paths, directories)
