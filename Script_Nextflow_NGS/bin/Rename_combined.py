#!/usr/bin/env python3

import os
import argparse
import pandas as pd

# Set up argument parser
parser = argparse.ArgumentParser(description="Rename files in the specified folder with custom rules.")
parser.add_argument("folder", type=str, help="Path to the folder containing the files to rename.")
parser.add_argument("csv_file", type=str, help="Path to the CSV file containing sample names to rename.")
args = parser.parse_args()

# Get folder path and CSV file path
folder_path = args.folder
csv_file = args.csv_file

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
    sample_names = set(sample_df.iloc[:, 4].astype(str))  # Assuming first column contains sample names
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit(1)

# List all files in the folder
filenames = os.listdir(folder_path)

# Process each file in the folder
for filename in filenames:
    old_filename = os.path.join(folder_path, filename)  # Full path to the original file

    # Skip directories
    if not os.path.isfile(old_filename):
        continue

    # Check if file is already renamed (contains "_S1_L001_R1_001" or "_S1_L001_R2_001")
    if "_S1_L001_R1_001" in filename or "_S1_L001_R2_001" in filename:
        continue  # Skip already renamed files

    # Extract sample name (assuming it's the first part before "_R1" or "_R2")
    sample_name = filename.split("_R1")[0] if "_R1" in filename else filename.split("_R2")[0]
    
    # Check if sample is in the CSV list
    if sample_name not in sample_names:
        continue  # Skip files that are not in the CSV

    # Start transformations
    new_filename = filename

    # Add -S1 before _R1 or _R2
    if '_R1' in filename:
        new_filename = new_filename.replace('_R1', '-S1_R1')
    if '_R2' in filename:
        new_filename = new_filename.replace('_R2', '-S1_R2')

    # Remove "_001" and replace "_" with "-"
    new_filename = new_filename.replace("_001", "")
    new_filename = new_filename.replace("_", "-")

    # Apply detailed renaming rules for R1 and R2
    new_filename = new_filename.replace("-R1.", "_S1_L001_R1_001.")
    new_filename = new_filename.replace("-R2.", "_S1_L001_R2_001.")

    # Full path for the new filename
    new_filename = os.path.join(folder_path, new_filename)

    # Rename the file
    os.rename(old_filename, new_filename)

    print(f"Renamed: {old_filename} -> {new_filename}")
