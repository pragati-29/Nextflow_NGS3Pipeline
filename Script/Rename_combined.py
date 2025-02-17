#!/usr/bin/env python3

import os
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Rename files in the specified folder with custom rules.")
parser.add_argument("folder", type=str, help="Path to the folder containing the files to rename.")
args = parser.parse_args()

# Get the folder path from the user
folder_path = args.folder

# Check if the folder exists
if not os.path.isdir(folder_path):
    print(f"Error: The folder '{folder_path}' does not exist.")
    exit(1)

# List all files in the folder
filenames = os.listdir(folder_path)

# Process each file in the folder
for filename in filenames:
    old_filename = os.path.join(folder_path, filename)  # Full path to the original file

    # Skip directories
    if not os.path.isfile(old_filename):
        continue

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

