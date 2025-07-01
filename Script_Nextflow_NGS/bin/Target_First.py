#!/usr/bin/env python3
import pandas as pd
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="Process TARGET_FIRST test samples")
    parser.add_argument("sample_file", help="Path to the input CSV file")
    args = parser.parse_args()

    file1 = pd.read_csv(args.sample_file)
    grouped_samp = file1.groupby(["Capturing_Kit", "Somatic_Germline"])['Biosample_ID'].apply(lambda x: ",".join(map(str, map(int, x))))

    for test_name, capr_kit, proj_id, appsession_name, bed_id, liq_tm, vc_af_call, vc_af_filt, vc_type, germ_som,sample_type in zip(
            file1['Test_Name'], file1['Capturing_Kit'], file1['Project_ID'], file1['appsession_name'], file1['bed_id'],
            file1['liquid_tumor'], file1['vc-af-call-threshold'], file1['vc-af-filter-threshold'], file1['vc_type'],
            file1['Somatic_Germline'],file1["Sample_Type"]):
        
        if "somatic" in germ_som and "TARGET_FIRST" in test_name and "DNA" in sample_type:
            if "FEV2F2both" in capr_kit:
                biosamp_FEV2 = ",".join(map(str, [grouped_samp.loc["FEV2F2both", "somatic"]]))
                command_bs_launch = (
                    f"bs launch application -n 'DRAGEN Enrichment' --app-version 3.9.5 "
                    f"-o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} "
                    f"-o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom "
                    f"-o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_FEV2} "
                    f"-o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 "
                    f"-o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} "
                    f"-o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 "
                    f"-o hla:1 -o nirvana:1 -o commandline-disclaimer:true "
                    f"-o arbitrary:'--read-trimmers:adapter --trim-adapter-read1' "
                    f"-o additional-file:25600057590 -o automation-sex:unknown"
                )
                print(command_bs_launch)
                bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                print("STDOUT:", bs_launch_run.stdout)
                print("STDERR:", bs_launch_run.stderr)

if __name__ == "__main__":
    main()
