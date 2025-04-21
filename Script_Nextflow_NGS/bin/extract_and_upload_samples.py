#!/usr/bin/env python3
import pandas as pd
import subprocess
import argparse
import os
import time

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Extract project and biosample IDs, upload datasets, and generate a CSV output.")
parser.add_argument("sample_file", help="Path to the input sample CSV file")
parser.add_argument("input_dir", help="Path to the directory containing input FASTQ files")
parser.add_argument("output_file", help="Path to save the output CSV file")
args = parser.parse_args()

# Read the input sample CSV file into a pandas DataFrame
var1 = pd.read_csv(args.sample_file)

# Initialize lists to store project and biosample IDs
project_ids = []
biosample_ids = []

# Run 'bs list project' command to list available projects
bs_proj_list_cmnd = "bs list project"
result_cmnd = subprocess.run(bs_proj_list_cmnd, shell=True, capture_output=True, text=True)
bs_samp_list = result_cmnd.stdout.strip()
print(bs_samp_list)  # Print the list of projects for debugging

# Iterate over Project_name and Sample_ID columns in the input CSV
for i, j in zip(var1['Project_name'], var1['Sample_ID']):
    print(j)  # Print the sample ID for tracking progress
    
    # Construct and run command to extract project ID by matching project name
    command = "bs list project | grep -w '" + i + "' | awk -F '|' '{print $3}' | sed 's/ //g'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    project_id = result.stdout.strip()  # Remove whitespace from project ID
    print(project_id)  # Print the project ID for debugging
    project_ids.append(project_id)  # Store the project ID
    
    # Construct and run command to upload FASTQ files for the sample to the project
    command1 = f"bs upload dataset --project={project_id} {args.input_dir}/{j}_S1_L001_R1_001.fastq.gz {args.input_dir}/{j}_S1_L001_R2_001.fastq.gz"
    result1 = subprocess.run(command1, shell=True, capture_output=True, text=True)
    print(result1.stdout)  # Print the upload command output for debugging
    print(command1)  # Print the upload command itself for verification
    
    # Wait 15 seconds to avoid overwhelming the server
    time.sleep(15)
    
    # Construct and run command to extract biosample ID for the sample
    command_biosamp = "bs get biosample -n " + str(j) + " –terse | grep Id | head -1 | grep -Eo '[0-9]{1,}'"
    biosamp_run = subprocess.run(command_biosamp, shell=True, capture_output=True, text=True)
    biosample_id = biosamp_run.stdout.strip()  # Remove whitespace from biosample ID
    biosample_ids.append(biosample_id)  # Store the biosample ID

# Add project and biosample IDs as new columns in the DataFrame
var1['Project_ID'] = project_ids
print(biosample_ids)  # Print biosample IDs for debugging
var1['Biosample_ID'] = biosample_ids

# Save the updated DataFrame to the output CSV file
var1.to_csv(args.output_file, index=False)
