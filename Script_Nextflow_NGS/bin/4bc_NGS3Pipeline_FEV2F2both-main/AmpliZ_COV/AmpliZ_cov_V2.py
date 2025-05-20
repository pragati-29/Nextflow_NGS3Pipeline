# -*- coding: utf-8 -*-
"""
Created on Thus 7th NOV 12:57:37 2024

@author: Prabir
"""
#Z score + P value + percentile -> CNV output

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from matplotlib.patches import Rectangle


###
main_sample_ID = sys.argv[1]
project_name = "Somatic_Patient_Samples_January_25"
if "-cf" in main_sample_ID:
    stype = '1'
else:
    stype = '0'

if stype == '0':
    df_baseline = pd.read_csv("/home/ubuntu/Programs/NGS3Pipeline/AmpliZ_COV/Input/FEV2F2both_Solid_merged_Baseline.csv", header=0)
elif stype == '1':
    df_baseline = pd.read_csv("/home/ubuntu/Programs/NGS3Pipeline/AmpliZ_COV/Input/FEV2F2both_cfDNA_merged_Baseline.csv", header=0)

df_baseline_filt = df_baseline
print (".. Running : Copy Files from basespace - " + main_sample_ID)


# copy the main sample file to the MS_Cov folder
copy_command = "cp /home/ubuntu/basespace/Projects/" + project_name + "/AppResults/" + main_sample_ID + "/Files/"+ main_sample_ID +".qc-coverage-region-1_read_cov_report.bed MS_Cov/"
os.system(copy_command)

# open the main sample file
df_main_sample = pd.read_csv("MS_Cov/" + main_sample_ID + ".qc-coverage-region-1_read_cov_report.bed", header = 0, sep='\t')
# drop the columns gene_id, read1_cvg and read2_cvg
df_main_sample = df_main_sample.drop(['gene_id', 'read1_cvg', 'read2_cvg'], axis=1)

# rename the column total_cvg to the main sample ID and name to gene_name
df_main_sample.rename(columns={'total_cvg': main_sample_ID}, inplace=True)
df_main_sample.rename(columns={'name': 'gene_name'}, inplace=True)
#df_main_sample['gene_name'] = df_main_sample['gene_name'].str.split("+", regex=False).str[0]
df_main_sample['gene_name'] = df_main_sample['gene_name'].str.split("+").str[0]
df_main_sample['gene_name'] = df_main_sample['gene_name'].str.strip()

# create the Combined_info column in the main sample file
df_main_sample['Combined_info'] = df_main_sample['#chrom'].astype(str) + ":" + df_main_sample['start'].astype(str) + ":" + df_main_sample['end'].astype(str) + ":" + df_main_sample['gene_name']

# move the Combined_info column to the 5th column
df_main_sample = df_main_sample[['#chrom', 'start', 'end', 'gene_name', 'Combined_info', main_sample_ID]]

df_main_sample_filt = df_main_sample

# merge the baseline and main sample files
df_merged = pd.merge(df_main_sample_filt, df_baseline_filt, on=['#chrom', 'start', 'end', 'gene_name', 'Combined_info'], how='left')

# print to csv
df_merged.to_excel(main_sample_ID + "_whole_int_Coverage.xlsx", index=False)

# read in the domain database
df_domain = pd.read_csv("/home/ubuntu/Programs/NGS3Pipeline/AmpliZ_COV/Input/Domain_DB.csv", header = 0)

# get the domain info for the gene based on the Combined_info column
df_domain_filt = df_domain[df_domain['Combined_info'].isin(df_merged['Combined_info'])]

# merge the domain info with the merged file
df_merged_domain = pd.merge(df_domain_filt, df_merged, on=['Combined_info'], how='left')
df_merged_domain_samples = df_merged_domain.columns

# remove the common columns
df_merged_domain_samples = df_merged_domain_samples.drop(['#chrom', 'start', 'end', 'gene_name', 'Combined_info'])

# move the Combined_info column to the 5th column and the domain columns to the 6th column without altering the other columns
df_merged_domain = df_merged_domain[['#chrom', 'start', 'end', 'gene_name', 'Combined_info'] + list(df_merged_domain_samples)]

# sort by Combined_info column alphabetically
df_merged_domain = df_merged_domain.sort_values(by=['Combined_info'])
print (".. Input File is preparing for : "+ main_sample_ID)
# print to xlsx
df_merged_domain.to_excel(main_sample_ID + "_whole_Coverage_Domain.xlsx", index=False)
output_file = main_sample_ID + "_whole_int_Coverage.xlsx"
###


file_path = output_file
gene_list_file = '/home/ubuntu/Programs/NGS3Pipeline/AmpliZ_COV/gene_list.txt'
with open(gene_list_file, 'r') as file:
    gene_list = [line.strip() for line in file.readlines()]

#df = pd.read_excel(file_path, sheet_name='Sheet1')
df = pd.read_excel(file_path, sheet_name='Sheet1', engine='openpyxl')

main_sample = main_sample_ID
print (".. Running : Z Score Calculating for - "+ main_sample)
results = pd.DataFrame(columns=['Gene Name', 'DAZ_Score', 'DAP_Value', 'DA_Percentile'])

for gene_name in gene_list:
    gene_df = df[df['gene_name'] == gene_name].copy()
    if gene_df.empty:
        continue

    gene_df['Region Length'] = gene_df['end'] - gene_df['start']
    all_samples = [col for col in gene_df.columns[5:] if col not in ['Region Length']]
    baseline_samples = [col for col in all_samples if col != main_sample]

    read_depth_data = gene_df.iloc[:, 5:-1].astype(float)
    normalized_read_depth = read_depth_data.div(gene_df['Region Length'].values, axis=0)

    baseline_mean = normalized_read_depth[baseline_samples].mean(axis=1)
    baseline_std = normalized_read_depth[baseline_samples].std(axis=1)
    baseline_std.replace(0, np.nan, inplace=True)

    z_scores_main = (normalized_read_depth[main_sample] - baseline_mean) / baseline_std

    p_values = 2 * (1 - norm.cdf(np.abs(z_scores_main)))
    percentiles_main = [norm.cdf(z) * 100 for z in z_scores_main]

    mean_z_score = z_scores_main.mean()
    mean_p_value = p_values.mean()
    mean_percentile = np.mean(percentiles_main)

    results = pd.concat([results, pd.DataFrame({
        'Gene Name': [gene_name],
        'DAZ_Score': [mean_z_score],
        'DAP_Value': [mean_p_value],
        'DA_Percentile': [mean_percentile]
    })], ignore_index=True)

output_file = main_sample + "CNV_results.csv"
results.to_csv(output_file, index=False)

print(f'.. Statistical Results saved to : {output_file}')


def find_files(sample_id, directory="."):
    csv_file = None
    txt_file = None

    for file in os.listdir(directory):
        if sample_id in file and file.endswith('CNV_results.csv'):
            csv_file = os.path.join(directory, file)
        elif sample_id in file and file.endswith('_R_cnv_combined.txt'):
            txt_file = os.path.join(directory, file)
    
    return csv_file, txt_file

sample_id = main_sample

csv_file, txt_file = find_files(sample_id)

if csv_file and txt_file:
    file1 = pd.read_csv(txt_file, sep='\t')
    file2 = pd.read_csv(csv_file)

    results = file1.merge(file2, left_on='Gene', right_on='Gene Name', how='left')

    results = results[['Chromosome', 'Start', 'End', 'Predicted_copy_number', 
                       'Type_of_alteration', 'MedianRatio', 'Gene', 
                       'DAZ_Score', 'DAP_Value', 'DA_Percentile']]
    results['DAP_Value'] = results['DAP_Value'].apply(lambda x: f'{x:.6f}')

    output_file = f'{sample_id}_stat_cntf_cnv_combined.txt'
    results.to_csv(output_file, sep='\t', index=False)

    print(f'Results saved to {output_file}')
else:
    print("CSV or TXT file not found for the given sample ID.")
print (" ")
print(f'---- {main_sample}: Completed -------')
print (" ")
os.system("rm " +main_sample + "_whole_int_Coverage.xlsx")
os.system("rm " +main_sample + "_whole_Coverage_Domain.xlsx")
#os.system("mkdir Stat_Control_Combined")
#os.system("mv " +main_sample + "_stat_cntf_combined.txt .")
