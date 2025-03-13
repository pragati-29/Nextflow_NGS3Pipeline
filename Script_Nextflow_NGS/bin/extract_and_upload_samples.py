#!/usr/bin/env python3
import pandas as pd
import subprocess
import argparse
import time
import os

parser = argparse.ArgumentParser(description="Extract project and biosample IDs, upload datasets, and generate a CSV output.")
parser.add_argument("sample_file", help="Path to the input sample CSV file")
parser.add_argument("input_dir", help="Path to the directory containing input FASTQ files")
parser.add_argument("output_file", help="Path to save the output CSV file")
args = parser.parse_args()

var1 = pd.read_csv(args.sample_file)
project_ids = []
biosample_ids = []

bs_proj_list_cmnd = "bs list project"
result_cmnd = subprocess.run(bs_proj_list_cmnd, shell=True, capture_output=True, text=True)
bs_samp_list = result_cmnd.stdout.strip()
print(bs_samp_list)

for i, j in zip(var1['Project_name'], var1['Sample_ID']):
    print(j)
    command = "bs list project | grep -w '" + i + "' | awk -F '|' '{print $3}' | sed 's/ //g'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    project_id = result.stdout.strip()
    print(project_id)
    project_ids.append(project_id)
    
    command1 = f"bs upload dataset --project={project_id} {args.input_dir}/{j}_S1_L001_R1_001.fastq.gz {args.input_dir}/{j}_S1_L001_R2_001.fastq.gz"
    result1 = subprocess.run(command1, shell=True, capture_output=True, text=True)
    print(result1.stdout)
    print(command1)
    time.sleep(15)
    command_biosamp = "bs get biosample -n " + str(j) + " –terse | grep Id | head -1 | grep -Eo '[0-9]{1,}'"
    biosamp_run = subprocess.run(command_biosamp, shell=True, capture_output=True, text=True)
    biosample_id = biosamp_run.stdout.strip()
    biosample_ids.append(biosample_id)

var1['Project_ID'] = project_ids
print(biosample_ids)
var1['Biosample_ID'] = biosample_ids
var1.to_csv(args.output_file, index=False)
