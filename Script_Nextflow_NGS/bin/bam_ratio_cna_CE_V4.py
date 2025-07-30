#!/usr/bin/env python
# coding: utf-8
"""
Created on Mon May 27 05:45:00 2024

@author: Bhumika
"""
import pandas as pd
import glob
import os
import argparse

parser = argparse.ArgumentParser(description="Process CNV .bam_ratio.txt files using BED reference.")
parser.add_argument("bed_file", help="Path to the BED file")
parser.add_argument("gene_list", help="Path to the gene list file (gene_list_CE.txt)")
args = parser.parse_args()

# Function to filter genes based on genelist.txt and add "CNA_Scope_Status" column
def add_scope_status(input_file, gene_list_file):
    # Read the gene list
    with open(gene_list_file, 'r') as file:
        gene_list = [line.strip() for line in file]

    # Read the input file
    df = pd.read_csv(input_file, sep='\t')

    # Add the "CNA_Scope_Status" column based on whether the gene is in the gene list
    df['CNA_Scope_Status'] = df['Gene'].apply(lambda x: 'In Scope' if x in gene_list else 'Not in Scope')

    # Save the modified DataFrame back to the same file
    df.to_csv(input_file, index=False, sep='\t')

# Step 1: Read Data1 into a DataFrame
data1_path = args.bed_file
data1 = pd.read_csv(data1_path, sep='\t', header=None, names=['Chromosome', 'Start', 'End', 'Gene'])

# Concatenate Chromosome, Start, and End columns in Data1 to create a mapping key
data1['Combined_Location'] = data1['Chromosome'].str.replace('chr', '') + ':' + data1['Start'].astype(str) + '-' + data1['End'].astype(str)

# Get the current working directory
current_dir = os.getcwd()

# Use glob to find all files ending with .bam_ratio.txt in the current directory
file_pattern = os.path.join(current_dir, "*.bam_ratio.txt")
files = glob.glob(file_pattern)

# Path to the gene list file
gene_list_file = args.gene_list  # Change this to the correct path of genelist.txt

# Process each file
for file in files:
    # Read Data2 from the file
    data2 = pd.read_csv(file, sep='\t')
    
    # Rename 'Gene' column to 'Combined_Location' in Data2
    data2.rename(columns={'Gene': 'Combined_Location'}, inplace=True)
    
    # Merge the two DataFrames on the 'Combined_Location' column
    merged_data = pd.merge(data2, data1, on='Combined_Location', how='left')
    
    # Remove unnecessary columns from the merged DataFrame
    columns_to_remove = ['Chromosome_y', 'Start_y', 'End']
    merged_data.drop(columns=columns_to_remove, errors='ignore', inplace=True)
    
    # Save the merged DataFrame to a CSV file
    merged_output_file = os.path.splitext(file)[0] + '_mod_original.csv'
    merged_data.to_csv(merged_output_file, index=False)
    
    
    # Clean columns and calculate median ratio (only positive ratios)
    merged_data.drop(columns=['MedianRatio', 'CopyNumber'], errors='ignore', inplace=True)
    median_ratios = merged_data[merged_data['Ratio'] > 0].groupby('Gene')['Ratio'].median().reset_index().rename(columns={'Ratio': 'MedianRatio'})
    merged_data = pd.merge(merged_data, median_ratios, on='Gene', how='left')
    
    # Check for NaN values in MedianRatio
    if merged_data['MedianRatio'].isnull().any():
        print(f"Warning: NaN values found in MedianRatio for {file}. Filling NaNs with 0.")
        merged_data['MedianRatio'].fillna(0, inplace=True)    

    # Replace -1 with the gene-specific median ratios
    merged_data['Ratio'] = merged_data.apply(
        lambda row: row['MedianRatio'] if row['Ratio'] == -1 else row['Ratio'], axis=1
    )
    
    merged_data['CopyNumber'] = (merged_data['MedianRatio'] * 2).round().astype(int)
    
    # Save the final result to a CSV file
    final_output_file = os.path.splitext(file)[0] + '_mod.csv'
    merged_data.to_csv(final_output_file, index=False, columns=['Chromosome_x', 'Start_x', 'Ratio', 'MedianRatio', 'CopyNumber', 'Combined_Location', 'Gene'])    
    
    # Extract end positions from Combined_Location
    merged_data['End_x'] = merged_data['Combined_Location'].apply(lambda x: int(x.split('-')[1]))
    
    # Group by Chromosome_x, Gene, CopyNumber, and MedianRatio and aggregate Start_x and End_x
    result = merged_data.groupby(['Chromosome_x', 'Gene', 'CopyNumber', 'MedianRatio']).agg({'Start_x': 'min', 'End_x': 'max'}).reset_index()
    
    # Add the Type_of_alteration column based on CopyNumber values
    result['Type_of_alteration'] = result['CopyNumber'].apply(lambda x: 'Loss' if x in [0, 1] else 'Gain')
    
    # Rename columns to match the desired output
    result.rename(columns={
        'Chromosome_x': 'Chromosome',
        'Start_x': 'Start',
        'End_x': 'End',
        'CopyNumber': 'Predicted_copy_number'
    }, inplace=True)

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
    
    # Construct the final output filename
    base_name = os.path.basename(file)
    name_parts = base_name.split('.bam_ratio')[0]
    final_output_file = f"{name_parts}_R_cnv_combined.txt"
    
    # Save the final DataFrame to the TXT file
    result.to_csv(final_output_file, index=False, sep='\t')  
    
    print(f"Processed and saved {file} as {final_output_file}")
    print(result.head())
    
    # Add CNA_Scope_Status based on genelist.txt
    add_scope_status(final_output_file, gene_list_file)
    print(f"Added CNA_Scope_Status to {final_output_file}")
    
    # Filter the genes
    #filtered_output_file = f"{name_parts}_R_cnv_combined.txt"
    #filter_genes(final_output_file, gene_list_file, filtered_output_file)
    #print(f"Filtered data saved as {filtered_output_file}")
