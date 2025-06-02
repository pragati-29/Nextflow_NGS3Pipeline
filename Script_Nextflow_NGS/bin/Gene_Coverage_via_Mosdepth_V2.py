#!/usr/bin/env python
# coding: utf-8

"""
Created on Wed Jun  7 23:23:37 2023

@Coded: Vyomesh J
@Validation (In Progress): Prabir
"""

import pandas as pd
import glob
import os
import sys
import subprocess

# Read the list.txt file into a DataFrame
#input_csv = sys.argv[1]
#list_df = pd.read_csv(input_csv)
#path = os.getcwd()
path_1 = sys.argv[1]
file1 = sys.argv[2]
location = sys.argv[3]
#os.system(f"basemount-cmd refresh {location}/basespace")

list_df = pd.read_csv(path_1) #list can be substituted by file generated via sample_ID.py
print ("Print Dataframe:",list_df)
#taking environment variable mosdepth
mosdepth_path = os.environ.get("mosdepth")
print("mosdepth_path: ", mosdepth_path)
# Create a dictionary to map project names to sample IDs and test names
#Approach One
#Open the command.sh file in write mode
with open("command.sh", "w") as file:
    # Iterate over each sample
    for sample, project_name in zip(list_df['Sample_ID'],list_df['Project_name']):
        # Get the corresponding project name and test name for the current sample
        shell_cmd = f"""ls {location}/basespace/Projects/{project_name}/AppResults/{sample}/Files/*.bed | awk -F/ '!($NF ~ /{sample}/) {{ print $0 }}'"""
        result =  subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
        bed_file_path = result.stdout.strip()
        print(result)
        print(shell_cmd)
        print (bed_file_path)
        #bed_file_path =f"/home/bioinfo4home/bioinfo4/ubuntu/Projects/{project_name}/AppResults/{sample}*/Files/TarGT_First_v2_CDS_and_FEV2F2_GRCh37_30_Mar_23.bed"
        # Create the command with the updated project name and test name
        command = f"{mosdepth_path} --by {bed_file_path} --thresholds 1,10,20,50,100 {sample} {location}/basespace/Projects/{project_name}/AppResults/{sample}/Files/{sample}.bam"
        
        # Write the command to the command.sh file
        print(f"Printing command in sh file for sample {sample}:") 
        file.write(f"{command}\n")
    print("The command.sh file has been created successfully.")

#Running the mosedepth
print("Running Mosdepth for Gene Coverage.")
os.system("sh command.sh")
print("Compressed threshold files are generated.")

#unzipping the gz thrshold files
for sample in list_df['Sample_ID']:
    threshold_bed_file = f"{sample}.thresholds.bed.gz"
    gunzip_command = f"gunzip {threshold_bed_file}"
    os.system(gunzip_command)
print("The compressed threshold file have been extracted.")

print("Creating the  final Gene Coverage excel sheet.")
# Get the unique test names
unique_panel_ids = list_df['Capturing_Kit'].unique()

# Get the file name from command-line arguments e.g. python script.py Gene_Coverage_H_B-138_results.xlsx
Final_file_name = sys.argv[2] if len(sys.argv) > 1 else 'Gene_Coverage_H_B-Unknown_results.xlsx'


# Create an Excel writer object to save the results
excel_writer = pd.ExcelWriter(Final_file_name)

# Iterate over each unique test name
for panel_id in unique_panel_ids:
    # Filter the samples based on the test name
    filtered_samples = list_df[list_df['Capturing_Kit'] ==  panel_id]

    # Get the list of sample IDs for the current test name
    sample_ids = filtered_samples['Sample_ID'].tolist()

    # Specify the files path for merging
    files_path = "*.bed"

    # Initialize an empty DataFrame to store the merged data for the current test name
    merged_df = pd.DataFrame()
    sample_ids_merged = []

    # Iterate over each file and merge the data for samples in the current test name
    files = glob.glob(files_path)
    for file in files:
        # Extract the sample ID from the file name
        sample_id = file.split('/')[-1].split('.')[0]

        # Check if the sample ID belongs to the current test name
        if sample_id in sample_ids:
            # Read the current file into a DataFrame
            df = pd.read_csv(file, sep='\t', header="infer")

            # Merge the 1X column into the merged DataFrame using the sample ID as the column header
            merged_df[sample_id] = df['1X']
            sample_ids_merged.append(sample_id)
            # Set the first_file to the current file for the first sample in the current test name
            if len(sample_ids_merged) == 1:
                first_file = pd.read_csv(file, sep='\t', header="infer", usecols=[0, 1, 2, 3])

    # Add the Total_Base column to the first_file DataFrame
    first_file["Total_Base"] = first_file["end"] - first_file["start"]
    merged_df = pd.concat([first_file, merged_df], axis=1)

    # Perform calculations and create the gen_cov_{column}_percent columns
    for column in merged_df.columns[5:]:
        merged_df[f'Coverage_avg_{column}'] = merged_df[column] / merged_df['Total_Base'] * 100

    # Filter the desired columns in merged_df
    merged_df = merged_df.filter(regex='Coverage_avg_.*|chrom|start|end|region|Total_Base')

    # Create a DataFrame for grouped data without chrom, start, end, and Total_Base columns
    grouped_df = merged_df.drop(['#chrom', 'start', 'end', 'Total_Base'], axis=1)

    # Apply mean() to the grouped data by region (gene)
    grouped_df = grouped_df.groupby('region').mean()

    # Convert the numeric values to string and add the percent sign
    grouped_df = grouped_df.astype(str) + '%'
    
    # Save the grouped_df to the Excel writer object with the Capturing_Kit as the sheet name
    grouped_df.to_excel(excel_writer, sheet_name=panel_id, index=True)

# Save the Excel file
excel_writer.save()


# Print the confirmation message
print("The results have been saved to",Final_file_name)

#Removing file that are not required
extensions_to_remove = [
    '.mosdepth.global.dist.txt',
    '.mosdepth.region.dist.txt',
    '.mosdepth.summary.txt',
    '.per-base.bed.gz',
    '.per-base.bed.gz.csi',
    '.regions.bed.gz',
    '.regions.bed.gz.csi'
]

# Specify the directory path where the files are located
directory_path = os.getcwd()

# Loop through each file with the specified extensions in the directory
for extension in extensions_to_remove:
    file_pattern = os.path.join(directory_path, f'*{extension}')
    files_to_remove = glob.glob(file_pattern)
    
    # Remove each file
    for file in files_to_remove:
        os.remove(file)
print("Keeping only the required files and deleting the other files.")    
print("Process Completed")   
