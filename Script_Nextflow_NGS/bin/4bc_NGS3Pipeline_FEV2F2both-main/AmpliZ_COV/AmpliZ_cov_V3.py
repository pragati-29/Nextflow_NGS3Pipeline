# -*- coding: utf-8 -*-
"""
Created on Thus 7th NOV 12:57:37 2024

@author: Prabir
"""
# Z score + P value + percentile -> CNV output

import sys
import os
import pandas as pd
import numpy as np
from scipy.stats import norm

###
main_sample_ID = sys.argv[1]
print(f'---- {main_sample_ID}: Initiating -------')
project_name = sys.argv[2]
#project_name = "Somatic_Patient_Samples_December_24"
if "-cf" in main_sample_ID:
    stype = '1'
else:
    stype = '0'

if stype == '0':
    df_baseline = pd.read_csv("path/4bc_NGS3Pipeline_FEV2F2both/AmpliZ_COV/Input/FEV2F2both_Solid_merged_Baseline.csv", header=0)
elif stype == '1':
    df_baseline = pd.read_csv("path/4bc_NGS3Pipeline_FEV2F2both/AmpliZ_COV/Input/FEV2F2both_cfDNA_merged_Baseline.csv", header=0)

print(".. Running : Copy Files from basespace - " + main_sample_ID)

# copy the main sample file to the MS_Cov folder
ms_cov_dir = "MS_Cov"
os.makedirs(ms_cov_dir, exist_ok=True)
copy_command = f"cp {project_name}/AppResults/{main_sample_ID}/Files/{main_sample_ID}.qc-coverage-region-1_read_cov_report.bed {ms_cov_dir}/"
os.system(copy_command)

# open the main sample file
df_main_sample = pd.read_csv(f"{ms_cov_dir}/{main_sample_ID}.qc-coverage-region-1_read_cov_report.bed", header=0, sep='\t')
# drop the columns gene_id, read1_cvg and read2_cvg
df_main_sample = df_main_sample.drop(['gene_id', 'read1_cvg', 'read2_cvg'], axis=1)

# rename the column total_cvg to the main sample ID and name to gene_name
df_main_sample.rename(columns={'total_cvg': main_sample_ID}, inplace=True)
df_main_sample.rename(columns={'name': 'gene_name'}, inplace=True)
df_main_sample['gene_name'] = df_main_sample['gene_name'].str.split("+").str[0].str.strip()

# create the Combined_info column in the main sample file
df_main_sample['Combined_info'] = df_main_sample['#chrom'].astype(str) + ":" + df_main_sample['start'].astype(str) + ":" + df_main_sample['end'].astype(str) + ":" + df_main_sample['gene_name']

# move the Combined_info column to the 5th column
df_main_sample = df_main_sample[['#chrom', 'start', 'end', 'gene_name', 'Combined_info', main_sample_ID]]

# merge the baseline and main sample files
df_merged = pd.merge(df_main_sample, df_baseline, on=['#chrom', 'start', 'end', 'gene_name', 'Combined_info'], how='left')

# print to Excel
df_merged.to_excel(main_sample_ID + "_whole_int_Coverage.xlsx", index=False)

# read in the domain database
df_domain = pd.read_csv("path/4bc_NGS3Pipeline_FEV2F2both/AmpliZ_COV/Input/Domain_DB.csv", header=0)

# get the domain info for the gene based on the Combined_info column
df_domain_filt = df_domain[df_domain['Combined_info'].isin(df_merged['Combined_info'])]

# merge the domain info with the merged file
df_merged_domain = pd.merge(df_domain_filt, df_merged, on=['Combined_info'], how='left')

# sort by Combined_info column alphabetically
df_merged_domain = df_merged_domain.sort_values(by=['Combined_info'])
print(".. Input File is preparing for : " + main_sample_ID)

# print to Excel
df_merged_domain.to_excel(main_sample_ID + "_whole_Coverage_Domain.xlsx", index=False)
output_file = main_sample_ID + "_whole_int_Coverage.xlsx"
###

file_path = output_file
gene_list_file = 'path/4bc_NGS3Pipeline_FEV2F2both/Ampliz_cov_V2_test/gene_list.txt'
with open(gene_list_file, 'r') as file:
    gene_list = [line.strip() for line in file.readlines()]

# read the file
df = pd.read_excel(file_path, sheet_name='Sheet1', engine='openpyxl')

main_sample = main_sample_ID
print(".. Running : Z Score Calculating for - " + main_sample)
results = pd.DataFrame(columns=['Gene Name', 'DAZ_Score', 'DAP_Value', 'DA_Percentile'])

# Updated Calculation Logic (from Script 1)
baseline_zone_lower = -1.5
baseline_zone_upper = 1.5
amplification_threshold = 2
delection_threshold = -2
buffer_zone = 0.5
amplification_svm = amplification_threshold + buffer_zone
neutral_upper = delection_threshold + buffer_zone
neutral_lower = amplification_threshold - buffer_zone

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

    # Handle zero std deviation or missing baseline data
    baseline_std.replace(0, np.nan, inplace=True)
    z_scores_main = (normalized_read_depth[main_sample] - baseline_mean) / baseline_std
    z_scores_main = np.nan_to_num(z_scores_main)  # Replace NaN with 0

    # Calculate P-values and percentiles with NaN handling
    p_values = 2 * (1 - norm.cdf(np.abs(z_scores_main)))
    p_values = np.nan_to_num(p_values, nan=1)  # Replace NaN with 1
    percentiles_main = [norm.cdf(z) * 100 if not np.isnan(z) else 50 for z in z_scores_main]

    # Mean calculations with NaN handling
    mean_z_score = np.nanmean(z_scores_main)
    mean_p_value = np.nanmean(p_values)
    mean_percentile = np.nanmean(percentiles_main)

    regions_in_baseline_zone = ((z_scores_main >= baseline_zone_lower) & (z_scores_main <= baseline_zone_upper)).sum()
    regions_above_amplification_buffer = (z_scores_main > amplification_svm).sum()
    regions_above_baseline_zone = ((z_scores_main > 1.5) & (z_scores_main <= 2.5)).sum()

    total_regions = len(z_scores_main)
    percent_baseline_zone = (regions_in_baseline_zone / total_regions) * 100
    percent_above_baseline_zone = (regions_above_baseline_zone / total_regions) * 100
    percent_amplified_zone = (regions_above_amplification_buffer / total_regions) * 100

    if mean_z_score > 4:
        likelihood_tag = "Gain - High Likelihood"
    elif 2.5 <= mean_z_score <= 4:
        likelihood_tag = "Gain - Moderate Likelihood"
    elif 1.5 <= mean_z_score < 2.5:
        likelihood_tag = "Gain - Marginal Likelihood"
    elif -1.5 <= mean_z_score < 1.5:
        likelihood_tag = "Within Baseline"
    elif -2.5 <= mean_z_score < -1.5:
        likelihood_tag = "Loss - Marginal Likelihood"
    elif -4 <= mean_z_score < -2.5:
        likelihood_tag = "Loss - Moderate Likelihood"
    else:
        likelihood_tag = "Loss - High Likelihood"

    os.makedirs("Output", exist_ok=True)
    results = pd.concat([results, pd.DataFrame({
        'Gene Name': [gene_name],
        'DAZ_Score': [mean_z_score],
        'DAP_Value': [mean_p_value],
        'DA_Percentile': [mean_percentile],
        'Amp Status': [likelihood_tag],
        'Baseline Zone Reg (%)': [percent_baseline_zone],
        'Grayzone Reg (%)': [percent_above_baseline_zone],
        'Above Amp Reg (%)': [percent_amplified_zone]
    })], ignore_index=True, sort=False)

# Ensure numeric columns are consistent
numeric_columns = [
    'Baseline Zone Reg (%)',
    'Grayzone Reg (%)',
    'Above Amp Reg (%)',
    'DAZ_Score',
    'DAP_Value',
    'DA_Percentile'
]
results[numeric_columns] = results[numeric_columns].apply(pd.to_numeric, errors='coerce')

output_file = main_sample + "CNV_results.csv"
results.to_csv(output_file, index=False, float_format='%.6f')
print(f'.. Statistical Results saved to : {output_file}')


def find_files(sample_id, directory="."):
    csv_file = None
    txt_file = None

    for file in os.listdir(directory):
        if sample_id in file and file.endswith('CNV_results.csv'):
            csv_file = os.path.join(directory, file)
        elif sample_id in file and file.endswith('_R_cnv_combined_final.txt'):
            txt_file = os.path.join(directory, file)
    
    return csv_file, txt_file

sample_id = main_sample

csv_file, txt_file = find_files(sample_id)

if csv_file and txt_file:
    file1 = pd.read_csv(txt_file, sep='\t')
    file2 = pd.read_csv(csv_file)

    results = file1.merge(file2, left_on='Gene', right_on='Gene Name', how='left')

    # Rename headers in the final output to include '4bc_cohort_', 
    # and rename "Amp Status" to "Amp_Status_4bc_Cohort".
    results.rename(
        columns={
            'DAZ_Score': '4bc_cohort_DAZ_Score',
            'DAP_Value': '4bc_cohort_DAP_Value',
            'DA_Percentile': '4bc_cohort_DA_Percentile',
            'Baseline Zone Reg (%)': '4bc_cohort_Baseline Zone Reg (%)',
            'Grayzone Reg (%)': '4bc_cohort_Grayzone Reg (%)',
            'Above Amp Reg (%)': '4bc_cohort_Above Amp Reg (%)',
            'Amp Status': 'Amp_Status_4bc_Cohort'
        },
        inplace=True
    )

    # Reorder columns (optional) so the renamed columns are in the same relative position
    results = results[
        [
            'Chromosome', 'Start', 'End', 'Predicted_copy_number', 'Type_of_alteration',
            'MedianRatio', 'Gene', '4bc_cohort_DAZ_Score', '4bc_cohort_DAP_Value',
            '4bc_cohort_DA_Percentile', 'Amp_Status_4bc_Cohort',
            '4bc_cohort_Baseline Zone Reg (%)', '4bc_cohort_Grayzone Reg (%)',
            '4bc_cohort_Above Amp Reg (%)'
        ]
    ]

    # Format numeric columns
    results['4bc_cohort_DAP_Value'] = results['4bc_cohort_DAP_Value'].apply(
        lambda x: f'{float(x):.6f}' if pd.notnull(x) else ''
    )

    output_file = f'Output/{sample_id}_stat_cntf_cnv_combined.txt'
    results.to_csv(output_file, sep='\t', index=False, float_format='%.6f')

    print(f'Results saved to {output_file}')
else:
    print("CSV or TXT file not found for the given sample ID.")

print(" ")
print(f'---- {main_sample}: Completed -------')
print(" ")
os.system("rm " + main_sample + "CNV_results.csv")
os.system("rm " + main_sample + "_whole_int_Coverage.xlsx")
os.system("rm " + main_sample + "_whole_Coverage_Domain.xlsx")
