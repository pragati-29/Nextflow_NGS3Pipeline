#!/usr/bin/env python3
import os
import argparse
import pandas as pd

# Set up argument parser
parser = argparse.ArgumentParser(description="Rename files in the specified folder with custom rules.")
parser.add_argument("folder", type=str, help="Path to the folder containing the files to rename.")
parser.add_argument("csv_file", type=str, help="Path to the CSV file containing sample names to rename.")
parser.add_argument("output_csv", type=str, help="Path to save the updated CSV file.")
args = parser.parse_args()

# Get folder path and CSV file path
folder_path = args.folder
csv_file = args.csv_file
output_csv = args.output_csv

# Check if the folder exists
if not os.path.isdir(folder_path):
    print(f"Error: The folder '{folder_path}' does not exist.")
    exit(1)

# Check if the CSV file exists
if not os.path.isfile(csv_file):
    print(f"Error: The CSV file '{csv_file}' does not exist.")
    exit(1)

# Read sample names from the CSV
try:
    sample_df = pd.read_csv(csv_file)

    # Ensure CSV has the expected structure
    if "file_name" not in sample_df.columns:
        print("Error: CSV must contain 'file_name' column.")
        exit(1)

    sample_names = set(sample_df["file_name"].astype(str))
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit(1)

# List all files in the folder
filenames = os.listdir(folder_path)
renamed_files = {}  # Dictionary to store original-to-new filename mapping

# Process each file in the folder
for filename in filenames:
    old_filepath = os.path.join(folder_path, filename)

    # Skip directories
    if not os.path.isfile(old_filepath):
        continue

    # Check if file is already renamed
    if "_S1_L001_R1_001" in filename or "_S1_L001_R2_001" in filename:
        sample_name = filename.split("_")[0]
        renamed_files[sample_name] = filename.split("_")[0]  # Store already renamed files
        continue

    # Extract sample name safely
    if "_R1" in filename:
        sample_name = filename.split("_R1")[0]
    elif "_R2" in filename:
        sample_name = filename.split("_R2")[0]
    else:
        sample_name = filename.split("_")[0]  # Default extraction

    # Check if sample is in CSV list
    if sample_name not in sample_names:
        continue

    # Apply renaming rules
    new_filename = filename.replace("_001", "").replace("_", "-")

    if "-R1" in new_filename:
        new_filename = new_filename.replace("-R1", "_S1_L001_R1_001")
    if "-R2" in new_filename:
        new_filename = new_filename.replace("-R2", "_S1_L001_R2_001")

    # Ensure the new filename does not already exist
    new_filepath = os.path.join(folder_path, new_filename)
    if os.path.exists(new_filepath):
        print(f"Skipping: {new_filepath} already exists.")
        continue

    # Store mapping
    renamed_files[sample_name] = new_filename.split("_")[0] 

    # Rename the file
    os.rename(old_filepath, new_filepath)
    print(f"Renamed: {old_filepath} -> {new_filepath}")

# Update sample_df with new names
sample_df["Sample_ID"] = sample_df["file_name"].map(renamed_files)

# Replace NaN values with "Not Found"
sample_df["Sample_ID"].fillna("Not Found", inplace=True)

# Save the updated DataFrame
sample_df.to_csv(output_csv, index=False)
print(f"Updated filenames saved to {output_csv}")
