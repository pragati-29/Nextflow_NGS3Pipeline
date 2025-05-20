# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 12:30:41 2023

@author: Vyomesh

"""
import os
import sys
import pandas as pd
import time
import glob

path_1 = sys.argv[1]
print ("CNV coverage file path : -",path_1)
input_filename = glob.glob(os.path.join(path_1,"*.csv"))

path_2 = os.path.dirname(path_1.rstrip('/'))
print (path_2)
#path_1 = os.getcwd()
#path_1 = sys.argv[1]
#input_filename = "W-171-TarGT_First_samples.csv"  # sys.argv[1]
#input_filename = glob.glob(os.path.join(path_1,"*.csv"))
#cap_kit_file = "FEV2F2both"  # sys.argv[2]
#output_file = 'W-171-FEV2F2both_output_file.xlsx'  # sys.argv[3]
output_file = sys.argv[2] if len(sys.argv) > 1 else 'CNV_results.xlsx'
#list_df = pd.read_csv(input_filename)
list_df = pd.read_csv(input_filename[0]) #list can be substituted by file generated via sample_ID.py
print (list_df)
cap_kit_file = list_df['Capturing_Kit'][1]
project_mapping = dict(zip(list_df['Sample_ID'], list_df['Project_name']))

samples_to_retry = []  # List to store samples that need retrying

for sample in list_df['Sample_ID']:
    print("########## Starting copying target region coverage bed from basespace #################")
    project_name = project_mapping[sample].strip("('),")
    # Construct the source and destination file paths
    source_file_path = f"{path_2}/basespace/Projects/{project_name}/AppResults/{sample}*/Files/{sample}*.qc-coverage-region-1_read_cov_report.bed"
    print (source_file_path)
    destination_file_path = f"{path_1}/"
    
    # Check if the source file exists
    if os.path.exists(source_file_path):
        cmd_1 = f"cp {source_file_path} {destination_file_path}"
        print("Running the command: " + cmd_1)
        os.system(cmd_1)
        print("########## Ending copying target region coverage bed from basespace #################")
    else:
        # If the source file doesn't exist, add the sample to the list for retrying
        cmd_2 = f"/home/ubuntu/bs/bs download appresult -o {path_1} --extension .qc-coverage-region-1_read_cov_report.bed --name {sample}*"
        print(f"File not found for sample {sample}. Running alternative command: {cmd_2}")
        os.system(cmd_2)
        samples_to_retry.append(sample)

# Retry for up to 2 minutes (12 attempts with 10-second intervals) for each sample
for sample in samples_to_retry:
    for _ in range(25):
        cmd_2 = f"/home/ubuntu/bs/bs download appresult -o {path_1} --extension .qc-coverage-region-1_read_cov_report.bed --name {sample}*"
        os.system(cmd_2)
        time.sleep(10)  # Wait for 10 seconds before checking again

        # Check if the source file exists after waiting
        source_file_path = f"{path_1}/{sample}*.qc-coverage-region-1_read_cov_report.bed"
        if os.path.exists(source_file_path):
            print(f"File found for sample {sample}. Download successful.")
            break  # Exit the loop if the file is found
            
        print(f"File not found for sample {sample}. Retrying...")
    
    # Wait for 2 minutes before attempting the next sample
    time.sleep(1)  # Sleep for 2 minutes

print("All retries complete.")




# Define a function to process and modify a single file
def process_file(file_path):
    # Extract the sample ID from the file name
    sample_id = sample

    # Read the data from the file into a DataFrame
    df = pd.read_csv(path_1 + file_path, sep='\t')

    # Rename the 'total_cvg' column with the sample ID as suffix
    df.rename(columns={'total_cvg': f'total_cvg_{sample_id}-S1'}, inplace=True)
    df.rename(columns={'name': 'gene_name'}, inplace=True)
    columns_to_drop = ['gene_id', 'read1_cvg', 'read2_cvg']
    df = df.drop(columns=columns_to_drop)


    return df

# read the file into a pandas dataframe
files = {
    "CE": "Indiegene_Target_2109PD006-V1_4BaseCare_1K_DNA_GRCh37.bed",
    "CT": "Indiegene_Target_2109PD008-V1_4BaseCare_RNA_Fusion_GRCh37.bed",
    "SE8": "SureSelectXT_V8_Covered.bed",
    "FE": "sorted_TarGT_First_hg19.bed",
    "Roche": "Roche_hg19.bed",
    "SE7":"SureSelectV7_covered.bed",
    "FEV2": "TarGT_First_v2_CDS_GRCh37_13_Mar_23.bed",
    "FEV2F2both": "TarGT_First_v2_FEV2F2both_cnv_coverage.bed",
    "GE": "GERMLINE_Panel_163_GRCh37_13_Mar_23.bed",
    "CEFU": "Indiegene_Target_2109PD006-V1_4BaseCare_1K_DNA_GRCh37_plus_TarGT_First_Fusion2_Only.bed"
}
if cap_kit_file not in files:
    raise ValueError("Unknown cap_kit_file value")
file_1 = files[cap_kit_file]
print (file_1)
Cap_all_gene_kit = pd.read_csv("/home/ubuntu/Programs/NGS3Pipeline/FEV2F2both/"+ file_1, sep='\t', header=None, names=['#chrom', 'start', 'end', 'gene_name','Combined_info'],index_col=False)

# Initialize an empty DataFrame to store the combined data
df_2 = Cap_all_gene_kit

# Process each file and append to df_2
for sample in list_df['Sample_ID']:
    file_name=sample+"-S1.qc-coverage-region-1_read_cov_report.bed"
    df = process_file(file_name)
    # Merge the data based on the columns 'chrom', 'start', and 'end'
    if df_2 is None:
        df_2 = df
    else:
        df_2 = pd.merge(df_2, df, on=['#chrom', 'start', 'end','gene_name'], how='left')

# Sort the combined DataFrame based on the specified columns
#df_2 = df_2.sort_values(by=['#chrom', 'start', 'end'])

# Reset the index of the combined DataFrame
df_2 = df_2.reset_index(drop=True)

# Save the resulting DataFrame in Excel format

df_2.to_excel(path_1 + output_file, index=False)
