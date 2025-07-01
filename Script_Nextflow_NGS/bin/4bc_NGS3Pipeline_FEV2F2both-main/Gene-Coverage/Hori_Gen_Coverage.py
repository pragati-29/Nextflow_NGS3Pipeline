# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 13:14:28 2024

@author: Vyomesh
"""

import pandas as pd
import os,sys,glob

path_1 = sys.argv[1]
print ("Gene coverage file path : -",path_1)
file1 = glob.glob(os.path.join(path_1,"*.csv"))
print (file1)
list_df = pd.read_csv(file1[0])
print ("Print Dataframe:",list_df)
# Dictionary mapping capturing kits to their respective BED files #Full path requried
bed_files = {
    "CDS": "/home/ubuntu/Programs/NGS3Pipeline/CDS/CNV/TarGT_First_v2_CDS_GRCh37_13_Mar_23.bed",
    "FEV2F2both": "path/4bc_NGS3Pipeline_FEV2F2both/CNV/TarGT_First_v2_CDS_and_FEV2F2_GRCh37_30_Mar_23.bed",
    "GE": "/home/ubuntu/Programs/NGS3Pipeline/Germline/CNV/GERMLINE_Panel_163_GRCh37_13_Mar_23.bed",
    "SE8":"./hgencov_commonfiles/SureSelect_V8_Coverde_Modified.bed",
    "CE":"./hgencov_commonfiles/Indiegene_Target_2109PD006-V1_4BaseCare_1K_DNA_GRCh37.bed",
    "CEFu":"./hgencov_commonfiles/Indiegene_Target_2109PD006-V1_4BaseCare_1K_DNA_GRCh37_plus_TarGT_First_Fusion2_Only.bed"
}

# Load the input CSV file into a DataFrame
#list_df = pd.read_csv(input_filename)  # Contains columns Sample_ID, Project_name, Capturing_Kit, Sample_Type
output_file = sys.argv[2]

path_2 = os.path.dirname(path_1.rstrip('/'))
print (path_2)
# Create an empty DataFrame to hold all sample data
compiled_df = pd.DataFrame()
compiled_file_name = f"{path_2}/Gene-Coverage/{output_file}_Hori_GenCov.xlsx"
# Iterate through each sample's details in the input DataFrame
for sample, project_name in zip(list_df['Sample_ID'],list_df['Project_name']):
    # Construct the path to the coverage report file for the sample
    path_cov_file = glob.glob(f"{path_2}/basespace/Projects/{project_name}/AppResults/{sample}*/Files/{sample}*.qc-coverage-region-1_cov_report.bed")
    os.system("cp " + path_cov_file[0] + " ./")
    loc_path = glob.glob(f"{sample}*.qc-coverage-region-1_cov_report.bed")

    # Read the coverage report into a DataFrame
    df_cov = pd.read_csv(loc_path[0], sep="\t")
    os.system("chmod 777 " + loc_path[0])

    # Extract relevant columns and rename percentage coverage column for clarity
    df_cov_sample = df_cov[['#chrom', 'start', 'end', 'pct_above_5']].rename(columns={'pct_above_5': f'Coverage_avg_{sample}'})

    # Append the grouped data to the compiled DataFrame
    compiled_df = pd.concat([compiled_df, df_cov_sample], ignore_index=True)
Capturing_Kit = list_df['Capturing_Kit'][0]
#Capturing_Kit = final_file_name.split('-')[2]
# Determine the appropriate BED file for the capturing kit used
bed_file_id = bed_files[Capturing_Kit]

# Construct the path to the BED file
path_bed_file = bed_file_id

# Read the BED file into a DataFrame
df_bed = pd.read_csv(path_bed_file, sep="\t", header=None, names=['#chrom', 'start', 'end', 'Gene', 'Combined'])

# Merge the coverage data with BED file data to add gene annotations
df_cov_sg = pd.merge(compiled_df, df_bed[['#chrom', 'start', 'end', 'Gene']], on=['#chrom', 'start', 'end'], how='left')

# Rearrange columns to position 'Gene' column after 'end' column
df_cov_sg.insert(df_cov_sg.columns.get_loc('end') + 1, 'Gene', df_cov_sg.pop('Gene'))

# Select coverage columns
coverage_cols = [col for col in df_cov_sg.columns if col.startswith('Coverage_avg_')]

# Calculate mean coverage percentage across selected columns for each gene
df_cov_sg_grouped = (df_cov_sg.groupby('Gene')[coverage_cols].mean().reset_index())

# Round to two decimal places and add percentage sign
for col in coverage_cols:
    df_cov_sg_grouped[col] = df_cov_sg_grouped[col].round(2).astype(str) + '%'

# Save the compiled data to a single Excel file
df_cov_sg_grouped.to_excel(compiled_file_name, index=False)

os.system("rm *.bed")

print(f"A compiled file named '{compiled_file_name}' has been generated with all sample data appended together.")
