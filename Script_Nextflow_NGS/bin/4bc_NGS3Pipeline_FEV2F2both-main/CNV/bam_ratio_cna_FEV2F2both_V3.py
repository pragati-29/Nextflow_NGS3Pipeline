#!/usr/bin/env python
# coding: utf-8
"""
Created on Mon May 27 05:45:00 2024

@author: Bhumika
"""
import pandas as pd
import glob
import os

# Step 1: Read Data1 into a DataFrame
data1_path = "/path/4bc_NGS3Pipeline_FEV2F2both/CNV/TarGT_First_v2_CDS_GRCh37_13_Mar_23.bed"
data1 = pd.read_csv(data1_path, sep='\t', header=None, names=['Chromosome', 'Start', 'End', 'Gene'])

# Concatenate Chromosome, Start, and End columns in Data1 to create a mapping key
data1['Combined_Location'] = data1['Chromosome'].str.replace('chr', '') + ':' + data1['Start'].astype(str) + '-' + data1['End'].astype(str)

# Get the current working directory
current_dir = os.getcwd()

# Use glob to find all files ending with .bam_ratio.txt in the current directory
file_pattern = os.path.join(current_dir, "*.bam_ratio.txt")
files = glob.glob(file_pattern)

def process_file(file, data1):
    # Read and merge data
    data2 = pd.read_csv(file, sep='\t').rename(columns={'Gene': 'Combined_Location'})
    merged_data = pd.merge(data2, data1, on='Combined_Location', how='left').drop(columns=['Chromosome_y', 'Start_y', 'End'], errors='ignore')
    
    # Save intermediate result
    merged_data.to_csv(os.path.splitext(file)[0] + '_mod_original.csv', index=False)
    
    # Clean columns and calculate median ratio (only positive ratios)
    merged_data.drop(columns=['MedianRatio', 'CopyNumber'], errors='ignore', inplace=True)
    median_ratios = merged_data[merged_data['Ratio'] > 0].groupby('Gene')['Ratio'].median().reset_index().rename(columns={'Ratio': 'MedianRatio'})
    merged_data = pd.merge(merged_data, median_ratios, on='Gene', how='left')
    
    # Replace -1 with the gene-specific median ratios
    merged_data['Ratio'] = merged_data.apply(
        lambda row: row['MedianRatio'] if row['Ratio'] == -1 else row['Ratio'], axis=1
    )    
    
    merged_data['CopyNumber'] = (merged_data['MedianRatio'] * 2).round().astype(int)
    
    # Save the final merged data
    merged_data.to_csv(os.path.splitext(file)[0] + '_mod.csv', index=False, columns=[
        'Chromosome_x', 'Start_x', 'Ratio', 'MedianRatio', 'CopyNumber', 'Combined_Location', 'Gene'
    ])

    # Extract and group final results
    merged_data['End_x'] = merged_data['Combined_Location'].apply(lambda x: int(x.split('-')[1]))
    result = merged_data.groupby(['Chromosome_x', 'Gene', 'CopyNumber', 'MedianRatio']).agg({
        'Start_x': 'min', 'End_x': 'max'
    }).reset_index().rename(columns={
        'Chromosome_x': 'Chromosome', 'Start_x': 'Start', 'End_x': 'End', 'CopyNumber': 'Predicted_copy_number'
    })
    result['Type_of_alteration'] = result['Predicted_copy_number'].apply(lambda x: 'Loss' if x in [0, 1] else 'Gain')

    # Custom sorting function for chromosomes
    def chromosome_sort_key(chromosome):
        if chromosome == 'X':
            return float('inf')  # Place X at the end
        elif chromosome == 'Y':
            return float('inf')  # Place Y at the end
        else:
            try:
                return float(chromosome)  # Numeric chromosomes
            except ValueError:
                return float('inf')  # Any non-numeric chromosomes (in case of errors)

    # Add a sorting column
    result['SortKey'] = result['Chromosome'].apply(chromosome_sort_key)

    # Sort the DataFrame
    result = result.sort_values(by='SortKey')

    # Drop the sorting column
    result = result.drop(columns=['SortKey'])

    # Ensure correct column order in the final output
    result = result[['Chromosome', 'Start', 'End', 'Predicted_copy_number', 'Type_of_alteration', 'MedianRatio', 'Gene']]

    # Save final result as a .txt file
    base_name = os.path.basename(file).split('.bam_ratio')[0]
    result.to_csv(f"{base_name}_R_cnv_combined_org.txt", index=False, sep='\t')
    
    # Filter out specified genes [retaining PIK3CA & KRAS]
    genes_to_filter = ['MSH2', 'MSH6', 'PMS1', 'IDH1', 'PMS2', 'MLH3', 'MAP2K1', 'MAP2K2']
    filtered_result = result[~result['Gene'].isin(genes_to_filter)]
    
    # Save final filtered result as a .txt file
    filtered_result.to_csv(f"{base_name}_R_cnv_combined_final.txt", index=False, sep='\t')
    

    print(f"Processed and saved {file}")

# Process each file
for file in files:
    process_file(file, data1)
