#!/usr/bin/env python3
import pandas as pd
import subprocess
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description="Process sample file input for CE Germline with DNA condition")
parser.add_argument("sample_file", help="Path to the input CSV file")
args = parser.parse_args()

# Read CSV file
file1 = pd.read_csv(args.sample_file)

# Group Biosample_ID by Capturing_Kit and Somatic_Germline
grouped_samp = file1.groupby(["Capturing_Kit", "Somatic_Germline"])["Biosample_ID"].apply(
    lambda x: ",".join(map(str, map(int, x)))
)
print(grouped_samp)
# Process each row in the file
for test_name, capr_kit, proj_id, appsession_name, bed_id, liq_tm, vc_af_call, vc_af_filt, cnv_base, germ_som, vc_type, sample_type in zip(
    file1['Test_Name'], file1['Capturing_Kit'], file1['Project_ID'], file1['appsession_name'], 
    file1['bed_id'], file1['liquid_tumor'], file1['vc-af-call-threshold'], 
    file1['vc-af-filter-threshold'], file1['cnv_baseline_Id'], file1['Somatic_Germline'], 
    file1['vc_type'], file1['Sample_Type']  # Assuming Sample_Type column exists for DNA condition
):
    print(sample_type,germ_som,test_name,capr_kit)
    if "germline" in germ_som and "INDIEGENE" in test_name and "DNA" in sample_type:
        if capr_kit == "CE":
            biosamp_CE_germ = ", ".join(map(str, [grouped_samp.loc["CE", "germline"]]))
            command_bs_launch = (
                f'bs launch application -n "DRAGEN Enrichment" --app-version 3.9.5 '
                f"-o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} "
                f"-o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom "
                f"-o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_CE_germ} "
                f"-o picard_checkbox:1 -o sv_checkbox:1 -o tmb:0 -o cnv_checkbox:1 -o cnv_ref:1 "
                f"-o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o {cnv_base} -o cnv_gcbias_checkbox:1 "
                f"-o hla:1 -o nirvana:1 -o commandline-disclaimer:true "
                f'-o arbitrary:"--read-trimmers:adapter --trim-adapter-read1" '
                f"-o additional-file:25600057590 -o automation-sex:unknown"
            )
            bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
            print("STDOUT:", bs_launch_run.stdout)
            print("STDERR:", bs_launch_run.stderr)
