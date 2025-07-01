#!/usr/bin/env python3
# Shebang line to specify that this script should be run with Python 3

import pandas as pd
import subprocess
import argparse


# Initialize argument parser with a description of the script's purpose
parser = argparse.ArgumentParser(description="Process sample file input")

# Add a required command-line argument for the input CSV file path
parser.add_argument("sample_file", help="Path to the input CSV file")

# Parse the command-line arguments
args = parser.parse_args()

# Read the input CSV file into a pandas DataFrame
file1 = pd.read_csv(args.sample_file)

# Group the DataFrame by 'Capturing_Kit' and 'Somatic_Germline', then aggregate 'Biosample_ID'
# by joining the IDs into a comma-separated string after converting to integers
grouped_samp = file1.groupby(["Capturing_Kit", "Somatic_Germline"])["Biosample_ID"].apply(lambda x: ",".join(map(str, map(int, x))))

# Iterate over multiple columns of the DataFrame simultaneously using zip
# Each iteration retrieves values for the specified columns
for test_name, capr_kit, proj_id, appsession_name, bed_id, liq_tm, vc_af_call, vc_af_filt, cnv_base, noise_base, germ_som, vc_type, sample_type in zip(
    file1['Test_Name'], file1['Capturing_Kit'], file1['Project_ID'], file1['appsession_name'], 
    file1['bed_id'], file1['liquid_tumor'], file1['vc-af-call-threshold'], file1['vc-af-filter-threshold'], 
    file1['cnv_baseline_Id'], file1['baseline-noise-bed'], file1['Somatic_Germline'], file1['vc_type'], file1['Sample_Type']):

    # Check if the sample is germline, the test is ABSOLUTE, and the sample type is DNA
    if germ_som == "germline" and test_name == "ABSOLUTE" and sample_type == "DNA":
        # Print the germline/somatic status for debugging or logging
        print(germ_som)
        
        # Check if the capturing kit is SE8
        if capr_kit == "SE8":
            # Retrieve and format the biosample IDs for SE8 germline samples
            biosamp_SE8_germ = (", ".join(map(str, [grouped_samp.loc["SE8", "germline"]])))
            # Print the biosample IDs for debugging or logging
            print(biosamp_SE8_germ)
            
            # Convert bed_id to an integer
            bed_id = int(bed_id)
            
            # Construct a shell command for launching a bioinformatics application (DRAGEN Enrichment)
            command_bs_launch = (
                f'bs launch application -n "DRAGEN Enrichment" --app-version 3.9.5 '
                f'-o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} '
                f'-o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom '
                f'-o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_SE8_germ} '
                f'-o picard_checkbox:1 -o sv_checkbox:1 -o tmb:0 '
                f'-o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 '
                f'-o cnv_gcbias_checkbox:1 -o {cnv_base} -o hla:1 -o nirvana:1 '
                f'-o commandline-disclaimer:true -o arbitrary:"--read-trimmers:adapter --trim-adapter-read1" '
                f'-o additional-file:25600057590 -o automation-sex:unknown'
            )
            # Print the constructed command for debugging or logging
            print(command_bs_launch)
            
            # Execute the shell command and capture its output
            bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
            
            # Print the standard output of the command
            print("STDOUT:", bs_launch_run.stdout)
            
            # Print the standard error of the command, if any
            print("STDERR:", bs_launch_run.stderr)
