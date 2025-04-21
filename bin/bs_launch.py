#!/usr/bin/env python3
import pandas as pd
import subprocess
import argparse
    
parser = argparse.ArgumentParser(description="Process sample file input")
parser.add_argument("sample_file", help="Path to the input CSV file")
args = parser.parse_args()

file1 = pd.read_csv(args.sample_file)
grouped_samp=file1.groupby(["Capturing_Kit","Somatic_Germline"])["Biosample_ID"].apply(lambda x: ",".join(map(str, map(int, x))))
for test_name,capr_kit,proj_id, appsession_name, bed_id, liq_tm,vc_af_call, vc_af_filt,cnv_base,noise_base,germ_som , vc_type in zip(file1['Test_Name'],file1['Capturing_Kit'],file1['Project_ID'],file1['appsession_name'],file1['bed_id'],file1['liquid_tumor'],file1['vc-af-call-threshold'],file1['vc-af-filter-threshold'],file1['cnv_baseline_Id'],file1['baseline-noise-bed'],file1['Somatic_Germline'],file1['vc_type']):
    if "somatic" in germ_som:
        if "TARGET_FIRST" in test_name:
            if "FEV2F2both" in capr_kit:
                biosamp_FEV2 =", ".join(map(str, [grouped_samp.loc["FEV2F2both", "somatic"]]))
                command_bs_launch = f"bs launch application -n" +f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_FEV2} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:"+f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                print(command_bs_launch)
                bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                bs_launch = bs_launch_run.stdout.strip()
                print("STDOUT:", bs_launch_run.stdout)
                print("STDERR:", bs_launch_run.stderr)
        elif "INDIEGENE" in test_name:
            if "CE" in capr_kit: 
                biosamp_CE_som=", ".join(map(str, [grouped_samp.loc["CE", "somatic"]]))
                command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_CE_som} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o {noise_base} -o vcf-site-filter:1 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                print(command_bs_launch)
                bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                bs_launch = bs_launch_run.stdout.strip()
                print("STDOUT:", bs_launch_run.stdout)
                print("STDERR:", bs_launch_run.stderr)
            elif "GE" in capr_kit:
                biosamp_GE_som=", ".join(map(str, [grouped_samp.loc["GE", "somatic"]]))
                command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_GE_som} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:0 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                print(command_bs_launch)
                bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                bs_launch = bs_launch_run.stdout.strip()
                print("STDOUT:", bs_launch_run.stdout)
                print("STDERR:", bs_launch_run.stderr)
        elif "ABSOLUTE" in test_name:
            if "SE8" in capr_kit:
                biosamp_SE8_som=", ".join(map(str, [grouped_samp.loc["SE8", "somatic"]]))
                command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_SE8_som} -o picard_checkbox:1 -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o {noise_base} -o vcf-site-filter:1 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                print(command_bs_launch)
                bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                bs_launch = bs_launch_run.stdout.strip()
                print("STDOUT:", bs_launch_run.stdout)
                print("STDERR:", bs_launch_run.stderr)
    elif "germline" in germ_som:
        if "INDIEGENE" in test_name: 
            if "CE" in capr_kit:
                biosamp_CE_germ=", ".join(map(str, [grouped_samp.loc["CE", "germline"]]))
                command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_CE_germ} -o picard_checkbox:1 -o sv_checkbox:1 -o tmb:0 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                bs_launch = bs_launch_run.stdout.strip()
                print("STDOUT:", bs_launch_run.stdout)
                print("STDERR:", bs_launch_run.stderr)
            elif "GE" in capr_kit:
                biosamp_GE_germ=", ".join(map(str, [grouped_samp.loc["GE", "germline"]]))
                command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_GE_germ} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:0 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                print(command_bs_launch)
                bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                bs_launch = bs_launch_run.stdout.strip()
                print("STDOUT:", bs_launch_run.stdout)
                print("STDERR:", bs_launch_run.stderr)
        elif "ABSOLUTE" in test_name:
            if "SE8" in capr_kit:
                biosamp_SE8_germ=", ".join(map(str, [grouped_samp.loc["SE8", "germline"]]))
                command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_SE8_germ} -o picard_checkbox:1 -o sv_checkbox:1 -o tmb:0 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o cnv_gcbias_checkbox:1 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                print(command_bs_launch)
                bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                bs_launch = bs_launch_run.stdout.strip()
                print("STDOUT:", bs_launch_run.stdout)
                print("STDERR:", bs_launch_run.stderr)
