#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sun Jul  2 21:56:10 2023

@author: Prabir
"""
import pandas as pd
import subprocess
import os
import sys
import glob
import numpy as np


path = os.getcwd()
print (path)
csv = glob.glob(os.path.join(path,"*.csv"))
df = pd.read_csv(csv[0])
Folder_name = sys.argv[1]
print (Folder_name)
Batch_ID = sys.argv[2]

column1_data = df['Raw_Name_R1_FastQ']
column2_data = df['Raw_Name_R2_FastQ']
sample_ID = df['Sample_ID_Main']
print (sample_ID)
fastqgz_files = glob.glob("*.fastq.gz")

if not fastqgz_files:
    for index, row in df.iterrows():
        column1_value = row['Raw_Name_R1_FastQ']
        column2_value = row['Raw_Name_R2_FastQ']
        sample_ID = row['Sample_ID_Main'][0:6]

        # Use the data in AWS CLI command
        aws_command_1 = f'aws s3 cp s3://bucket-name/{Folder_name}/Reads/ {path} --recursive --exclude "*" --include "{column1_value}" --profile=wiprodata'
        aws_command_2 = f'aws s3 cp s3://bucket-name/{Folder_name}/Reads/ {path} --recursive --exclude "*" --include "{column2_value}" --profile=wiprodata'

        print(aws_command_1)
        print(aws_command_2)

        # Execute the AWS CLI command using subprocess
        subprocess.run(aws_command_1, shell=True)
        subprocess.run(aws_command_2, shell=True)

    print("--Download done--")

    loc_drag39_file = 'path/4bc_NGS3Pipeline_FEV2F2both/Dragen_shell/dragen39.sh'
    loc_renm_file = 'path/4bc_NGS3Pipeline_FEV2F2both/Renaming.py'
    loc_renm_S1_file = 'path/4bc_NGS3Pipeline_FEV2F2both/Renaming-S1.py'

    os.system('cp ' + loc_drag39_file + ' ' + path)
    os.system('cp ' + loc_renm_file + ' ' + path)
    os.system('cp ' + loc_renm_S1_file + ' ' + path)
    os.system('chmod 777 *')

    command_s1 = 'python3 Renaming-S1.py'
    os.system(command_s1)

    command = 'python3 Renaming.py'
    os.system(command)

else:
    # If FASTQ.gz files are present
    print("FASTQ.gz files found. Skipping download and processing.")

    loc_drag39_file = 'path/4bc_NGS3Pipeline_FEV2F2both/Dragen_shell/dragen39.sh'
    loc_renm_file = 'path/4bc_NGS3Pipeline_FEV2F2both/Renaming.py'
    loc_renm_S1_file = 'path/4bc_NGS3Pipeline_FEV2F2both/Renaming-S1.py'
    
    os.system('cp ' + loc_drag39_file + ' ' + path)
    os.system('cp ' + loc_renm_file + ' ' + path)
    os.system('cp ' + loc_renm_S1_file + ' ' + path)
    os.system('chmod 777 *')
    
    command_s1 = 'python3 Renaming-S1.py'
    os.system(command_s1)

    command = 'python3 Renaming.py'
    os.system(command)
    
file_list=glob.glob("*R2_001.fastq.gz")
samples=[]
for file in file_list:
    sample= file.split("_")
    samples.append(sample[0])
    
dragen39file=path+'/dragen39.sh'
# Read in the file
with open(dragen39file, 'r') as file :
    filedata = file.read()

import datetime

current_date = datetime.datetime.now().strftime("%d_%b_%y")
formatted_date = os.path.splitext(current_date)[0]

print(formatted_date)

test = df['Test_Name'][0]
sample = df['Sample_Type'][0]
sample_type = df['Capturing_Kit'][0]
project_name = df['Project_name'][0]

if "GE" in sample_type:
    bed_id=int(32335159063)
elif "CE" in sample_type:
    bed_id=int(25985869859)
elif "SE8" in sample_type:
    bed_id=int(23683257154)
elif "FEV2F2both" in sample_type:
    bed_id=int(34857530934)
elif "CDS" in sample_type:
    bed_id=int(31946210817)
elif "CEfu" in sample_type:
    bed_id=int(32246847276)
elif "FUS" in sample_type:
    bed_id=int(34857530935)
else:
    bed_id=int()
print (sample_type)

pid = df['Project_ID'][0]
appsession_name = formatted_date + "_" + Batch_ID + "_"+ test + "_" + sample_type


with open(dragen39file, 'w') as file:
    file.write(filedata)

if "DNA" in sample:
    if ("-cf-" in ':'.join(samples))*("-CE" not in ':'.join(samples)) ==1:
        print ("FEV2F2both cfDNA samples present in the folder")
        bscmd = "bs launch application -n \"DRAGEN Enrichment\" --app-version 3.9.5 -o project-id:" + str(pid) + " -o app-session-name:"+ appsession_name +" -l "+ appsession_name +" -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:" + str(bed_id) + " -o input_list.sample-id:$bsids -o picard_checkbox:1 -o liquid_tumor:1 -o af-filtering:1 -o vc-af-call-threshold:1 -o vc-af-filter-threshold:5 -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:\"--read-trimmers:adapter --trim-adapter-read1\" -o additional-file:25600057590 -o automation-sex:unknown"
    elif ("-FEV2F2both-" in ':'.join(samples))*("-CE" not in ':'.join(samples)) ==1:
        print ("FEV2F2both samples present in the folder")
        bscmd = "bs launch application -n \"DRAGEN Enrichment\" --app-version 3.9.5 -o project-id:" + str(pid) + " -o app-session-name:"+ appsession_name +" -l "+ appsession_name +" -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:" + str(bed_id) + " -o input_list.sample-id:$bsids -o picard_checkbox:1 -o af-filtering:1 -o vc-af-call-threshold:5 -o vc-af-filter-threshold:10 -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:\"--read-trimmers:adapter --trim-adapter-read1\" -o additional-file:25600057590 -o automation-sex:unknown"
    elif ("-FUS-" in ':'.join(samples))*("-CE" not in ':'.join(samples)) ==1:
        print ("FUS samples present in the folder")
        bscmd = "bs launch application -n \"DRAGEN Enrichment\" --app-version 3.9.5 -o project-id:" + str(pid) + " -o app-session-name:"+ appsession_name +" -l "+ appsession_name +" -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:" + str(bed_id) + " -o input_list.sample-id:$bsids -o picard_checkbox:1 -o af-filtering:1 -o vc-af-call-threshold:5 -o vc-af-filter-threshold:10 -o sv_checkbox:1 -o sq-filtering:1 -o tmb:0 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:\"--read-trimmers:adapter --trim-adapter-read1\" -o additional-file:25600057590 -o automation-sex:unknown"

filedata = filedata.replace('{{samplenames}}', str(samples).strip("[]").replace("'","").replace(",",""))
filedata = filedata.replace('{{location}}', path)
filedata = filedata.replace('{{app-session-name}}', appsession_name) 
filedata = filedata.replace('{{pid}}', str(pid))
filedata = filedata.replace('{{project_name}}', project_name)
filedata = filedata.replace('{{bscmd}}', bscmd)

with open(dragen39file, 'w') as file:
    file.write(filedata)
os.system("bash " + dragen39file)