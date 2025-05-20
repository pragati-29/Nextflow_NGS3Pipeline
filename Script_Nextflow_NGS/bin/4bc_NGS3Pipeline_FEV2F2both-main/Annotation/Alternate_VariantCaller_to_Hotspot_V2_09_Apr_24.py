# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 14:49:12 2023

@Code: Vyomesh
Ex. python3 Alternate_VariantCaller_to_Hotspot_V2_09_Apr_24.py W-210-DNA-FEV2F2both-samples.csv
"""
import os
import pandas as pd
import sys
import logging
import glob
from datetime import datetime
import re

system_name=os.getlogin()
print(system_name)

common_file_dir="path/Common_files/"
print(common_file_dir)

print("\n VCF Calling by Alternative Method and Hotspot for SomaticDNA or cf-DNA \n")
path_1 = sys.argv[1]
print (path_1)
local_path = path_1
print(local_path)
file1 = glob.glob(os.path.join(path_1,"*.csv"))
print (file1)
input_filename = pd.read_csv(file1[0]) #list can be substituted by file generated via sample_ID.py
print ("Print Dataframe:",input_filename)
path_2 = os.path.dirname(path_1.rstrip('/'))
output_filename = "TFirst" #input_filename.split('_')[0]
print(input_filename)
print(output_filename)

# Read the list.txt file into a DataFrame
list_df = input_filename

# Create a dictionary to map project names to sample IDs and test names
project_mapping = dict(zip(list_df['Sample_ID'], zip(list_df['Project_name'])))
system_name="ubuntu"

#system_name=os.getlogin()  #system_name = getpass.getuser() add import getpass
for sample, Capturing_Kit in zip(list_df['Sample_ID'], list_df['Capturing_Kit']):
        project_name = project_mapping[sample]
        project_name = project_name[0].strip("('),")  
        path_to_bam = f"{path_2}/basespace/Projects/{project_name}/AppResults/{sample}*/Files/{sample}*.bam"
        if Capturing_Kit=="FEV2F2both" or Capturing_Kit=="CDS" or Capturing_Kit=="GE":
            if "-cf" in sample:
                comd_1="freebayes -f "+common_file_dir+"hg19.fasta -F 0.008 -t "+common_file_dir+"all_hotspot_variant_gs.bed "+path_to_bam+" > " + path_1 + "/"+sample+"_alt_pipeline.vcf"
                sample_type="cfDNA"
                print(comd_1)
                os.system(comd_1)
            elif "-F" in sample  or "-B" in sample and "-cf" not in sample:
                comd_1="freebayes -f "+common_file_dir+"hg19.fasta -F 0.008 -t "+common_file_dir+"all_hotspot_variant_gs.bed "+path_to_bam+" > " + path_1 + "/"+sample+"_alt_pipeline.vcf" 
                sample_type="somatic"
                print(comd_1)
                os.system(comd_1)
        elif Capturing_Kit=="CE" or Capturing_Kit=="CEFu":
            if "-cf" in sample:
                comd_1="freebayes -f "+common_file_dir+"hg19.fasta -F 0.008 -t "+common_file_dir+"all_hotspot_variant_gs.bed "+path_to_bam+" > " + path_1 + "/"+sample+"_alt_pipeline.vcf"
                print(comd_1)
                os.system(comd_1)
            elif "-F" in sample or "-B" in sample and "-cf" not in sample:
                comd_1="freebayes -f "+common_file_dir+"hg19.fasta -F 0.008 -t "+common_file_dir+"all_hotspot_variant_gs.bed "+path_to_bam+" > " + path_1 + "/"+sample+"_alt_pipeline.vcf"
                print(comd_1)
                os.system(comd_1)
        elif Capturing_Kit=="SE8":
            if "-cf" in sample:
                comd_1="freebayes -f "+common_file_dir+"hg19.fasta -F 0.008 -t "+common_file_dir+"all_hotspot_variant_gs.bed "+path_to_bam+" > " + path_1 + "/"+sample+"_alt_pipeline.vcf"
                print(comd_1)
                os.system(comd_1)
            elif "-F" in sample or "-B" in sample and "-cf" not in sample:
                comd_1="freebayes -f "+common_file_dir+"hg19.fasta -F 0.008 -t "+common_file_dir+"all_hotspot_variant_gs.bed "+path_to_bam+" > " + path_1 + "/"+sample+"_alt_pipeline.vcf"
                print(comd_1)
                os.system(comd_1)
        else:
            print("Invlid Capturing Kit and Notation For Sample:" + sample )
        comd_igv_report="create_report " + path_1 + "/"+sample+"_alt_pipeline.vcf --fasta /home/ubuntu/Freebayes_Test_Runs/Common_files/hg19.fasta --ideogram /home/ubuntu/Programs/IGV_Linux_2.9.2/igv/genomes/cytoBand.txt --flanking 300 --info-columns DP SAF SAR SRR SRF --tracks " + path_1 + "/"+sample+"_alt_pipeline.vcf "+path_to_bam+" /home/ubuntu/Programs/IGV_Linux_2.9.2/igv/genomes/ncbiRefGene.txt --output " + path_1 + "/"+sample+"_hotspot.html"
        print(comd_igv_report)
        os.system(comd_igv_report)
           
        
custom_header = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", "Sample_Depth_Info","Sample_ID"]
# Initialize an empty DataFrame with the custom header
df_combined = pd.DataFrame(columns=custom_header)

#comment added Vyomesh J 09-April-24    
for ids in list_df['Sample_ID']:
    vcf_file_path = path_1 + "/" + ids + "_alt_pipeline.vcf"
    try:
        # Read the VCF file into a DataFrame
        df = pd.read_csv(vcf_file_path, sep='\t', comment='#', header=None, names=custom_header)
        
        # Add a "Sample_ID" column with the value based on the input file name
        df['Sample_ID'] = ids
        
        # Reorder columns to match the custom header order 
        df = df[custom_header]
        # Reset the index of the DataFrame
        df.reset_index(drop=True, inplace=True)        
        # Append the current DataFrame to the combined DataFrame
        df_combined = pd.concat([df_combined, df], ignore_index=False)
    except Exception as e: 
        print(f"Error reading VCF file {vcf_file_path}: {str(e)}")

# Remove duplicate entries from df_combined based on all columns
df_combined = df_combined.drop_duplicates()

# Split the "Sample_Depth_Info" column using the ":" separator and create new columns
df_combined[['GT','DP','AD', 'RO', 'QR', 'AO', 'QA', 'GL']] = df_combined['Sample_Depth_Info'].str.split(':', expand=True)

#Modified 20 April 24 Vyomesh J
# Define a function to extract desired fields from a variant info string
def extract_fields(variant_info):
    pattern = r'(SRF=\d+;|SRR=\d+;|SAF=\d+;|SAR=\d+;)'
    extracted_fields = re.findall(pattern, variant_info)
    return ''.join(extracted_fields)

# Define a function to generate comment based on SAF and SAR values
def generate_comment(variant_info):
    pattern = r'SAF=(\d+);SAR=(\d+);'
    match = re.search(pattern, variant_info)
    if match:
        SAF_value = int(match.group(1))
        SAR_value = int(match.group(2))
        if SAF_value == SAR_value:
            return 'NO_STRAND_BIAS'
        else:
            return 'STRAND_BIAS'
    else:
        return 'NA'

# Apply the function to each row in the 'info' column
df_combined['STRAND_INFO'] = df_combined['INFO'].apply(lambda x: extract_fields(x))
# Apply the function to each row in the 'Strand_info' column to generate comment
df_combined['COMMENT'] = df_combined['STRAND_INFO'].apply(lambda x: generate_comment(x))

# Drop specific columns with headers "GT," "GL," "QA," and "QR"
columns_to_drop = ['GT', 'GL', 'QA', 'QR','AD','INFO','FORMAT','ID','FILTER','Sample_Depth_Info']
df_combined = df_combined.drop(columns=columns_to_drop)
#MODIFIED ON 30-May-24 Vyomesh J
# Define a function to calculate the AO_percentage
def calculate_ao_percentage(row):
    dp = int(row['DP'])
    ao_values = row['AO'].split(',')
    ao_percentages = [(int(ao) / dp) * 100 for ao in ao_values]
    return ','.join([str(round(percentage, 2)) for percentage in ao_percentages])

# Apply the function to create the AO_percentage column
df_combined['AO_percentage'] = df_combined.apply(calculate_ao_percentage, axis=1)

# Load gene coordinates based on sample ID pattern
def load_gene_coordinates(sample_id):
    if 'FEV2F2both' in sample_id:
        return pd.read_csv(common_file_dir+'TarGT_First_v2_CDS_and_FEV2F2_GRCh37_30_Mar_23.bed', sep='\t', header=None, names=['CHR', 'START', 'END', 'GENE_NAME'])
    elif 'CDS' in sample_id:
        return pd.read_csv(common_file_dir+'TarGT_First_v2_CDS_and_FEV2F2_GRCh37_30_Mar_23.bed', sep='\t', header=None, names=['CHR', 'START', 'END', 'GENE_NAME'])
    elif 'GE' in sample_id:
        return pd.read_csv(common_file_dir+'GERMLINE_Panel_163_GRCh37_13_Mar_23.bed', sep='\t', header=None, names=['CHR', 'START', 'END', 'GENE_NAME'])
    elif 'CE' in sample_id or 'CEFu' in sample_id:
        return pd.read_csv(common_file_dir+'Indiegene_Target_2109PD006-V1_4BaseCare_1K_DNA_GRCh37_plus_TarGT_First_Fusion2_Only.bed', sep='\t', header=None, names=['CHR', 'START', 'END', 'GENE_NAME'])
    elif 'SE8' in sample_id:
        return pd.read_csv(common_file_dir+'SureSelect_V8_Coverde_Modified.bed', sep='\t', header=None, names=['CHR', 'START', 'END', 'GENE_NAME'])
    else:
        return None

# Function to tag gene names based on "POS" and sample ID pattern
def tag_gene_name(row):
    gene_coordinates = load_gene_coordinates(row['Sample_ID'])
    if gene_coordinates is not None:
        for index, gene_row in gene_coordinates.iterrows():
            if row['#CHROM'] == gene_row['CHR'] and gene_row['START'] <= int(row['POS']) <= gene_row['END']:
                return gene_row['GENE_NAME']
    return None

# Apply the function to tag gene names
df_combined['GENE_NAME'] = df_combined.apply(tag_gene_name, axis=1)
output_excel_file = path_1 + "/"+ output_filename+"_"+sample_type+"_Hotspot_V2.xlsx"
df_combined.to_excel(output_excel_file, index=False)
