#!/usr/bin/env python3
import pandas as pd
import subprocess
import argparse

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Process sample file input")
parser.add_argument("sample_file", help="Path to the input CSV file")
args = parser.parse_args()

# Load the CSV file into a DataFrame
file1 = pd.read_csv(args.sample_file)

# Group by 'Capturing_Kit' and 'Somatic_Germline', joining Biosample_IDs by comma
grouped_samp = file1.groupby(["Capturing_Kit", "Somatic_Germline"])["Biosample_ID"].apply(
    lambda x: ",".join(map(str, map(int, x)))  # Convert IDs to int then string
)

# Loop through each row of the DataFrame to process matching conditions
for test_name, capr_kit, proj_id, appsession_name, bed_id, liq_tm, vc_af_call, vc_af_filt, germ_som, vc_type, sample_type in zip(
    file1["Test_Name"],
    file1["Capturing_Kit"],
    file1["Project_ID"],
    file1["appsession_name"],
    file1["bed_id"],
    file1["liquid_tumor"],
    file1["vc-af-call-threshold"],
    file1["vc-af-filter-threshold"],
    file1["Somatic_Germline"],
    file1["vc_type"],
    file1["Sample_Type"]
):
    # Apply filtering conditions for specific pipeline configuration
    if "somatic" in germ_som and "ABSOLUTE" in test_name and "ST8" in capr_kit and "RNA" in sample_type:
        # Get the grouped biosample IDs for the specific key
        biosamp_ST8_germ = ", ".join(map(str, [grouped_samp.loc["ST8", "somatic"]]))

        # Construct the `bs launch` command for the RNA pipeline
        command_bs_launch = (
            f'bs launch application -n "DRAGEN RNA Pipeline" '
            f"--app-version 3.6.3 -o project-id:{proj_id} "
            f"-o app-session-name:{appsession_name} -l {appsession_name} "
            f"-o output_format:BAM -o coverage_list.coverage_bed_id:23683257154 "
            f"-o sample-id:biosamples/{biosamp_ST8_germ} "
            f"-o ht-ref:hg19-altaware-cnv-anchor.v8 -o gene_fusion:1 "
            f"-o quantification_checkbox:1 -o commandline-disclaimer:true"
        )

        # Print and execute the command
        print(command_bs_launch)
        bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)

        # Output logs for debugging
        print("STDOUT:", bs_launch_run.stdout)
        print("STDERR:", bs_launch_run.stderr)
