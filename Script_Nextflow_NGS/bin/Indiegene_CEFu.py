#!/usr/bin/env python3
import pandas as pd
import subprocess
import argparse

# Argument parsing
parser = argparse.ArgumentParser(description="Process sample file input")
parser.add_argument("sample_file", help="Path to the input CSV file")
args = parser.parse_args()

# Read CSV file
file1 = pd.read_csv(args.sample_file)

# Group Biosample_IDs by Capturing_Kit and Somatic_Germline
grouped_samp = file1.groupby(["Capturing_Kit", "Somatic_Germline"])["Biosample_ID"].apply(
    lambda x: ",".join(map(str, map(int, x)))
)

# Process the data
for test_name, capr_kit, proj_id, appsession_name, bed_id, liq_tm, vc_af_call, vc_af_filt, cnv_base, noise_base, germ_som, vc_type,sample_type in zip(
    file1["Test_Name"],
    file1["Capturing_Kit"],
    file1["Project_ID"],
    file1["appsession_name"],
    file1["bed_id"],
    file1["liquid_tumor"],
    file1["vc-af-call-threshold"],
    file1["vc-af-filter-threshold"],
    file1["cnv_baseline_Id"],
    file1["baseline-noise-bed"],
    file1["Somatic_Germline"],
    file1["vc_type"],
    file1["Sample_Type"],
):
    if germ_som == "somatic" and test_name == "INDIEGENE" and sample_type == "DNA":
        print(germ_som,test_name,sample_type,capr_kit)
        if capr_kit == "CEFu":
            print(capr_kit)
            biosamp_CE_som = ", ".join(map(str, [grouped_samp.loc["CEFu", "somatic"]]))
            command_bs_launch = (
                f'bs launch application -n "DRAGEN Enrichment" '
                f"--app-version 3.9.5 -o project-id:{proj_id} "
                f"-o app-session-name:{appsession_name} -l {appsession_name} "
                f"-o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 "
                f"-o fixed-bed:custom -o target_bed_id:{bed_id} "
                f"-o input_list.sample-id:biosamples/{biosamp_CE_som} "
                f"-o picard_checkbox:1 -o liquid_tumor:{liq_tm} "
                f"-o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} "
                f"-o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 "
                f"-o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 "
                f"-o {noise_base} -o vcf-site-filter:1 -o cnv_checkbox:1 "
                f"-o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 "
                f"-o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 "
                f'-o commandline-disclaimer:true -o arbitrary:"--read-trimmers:adapter --trim-adapter-read1" '
                f"-o additional-file:25600057590 -o automation-sex:unknown"
            )
            bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
            print("STDOUT:", bs_launch_run.stdout)
            print("STDERR:", bs_launch_run.stderr)
