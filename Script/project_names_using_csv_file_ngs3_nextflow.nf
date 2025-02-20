params.input_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/fastq_test_Nextflow"
params.sample_file = "/home/pragati_4bc/NGS3Pipeline_Nextflow/fastq_test_Nextflow/test_ngs3_nextflow_Copy.csv"
params.output_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/fastq_test_Nextflow/Output"
process Renaming{
    script:
        """python3 ${params.input_dir}/Rename_combined.py "${params.input_dir}" """
}
process extract_and_upload_samples {
    publishDir params.output_dir, mode:'copy'

    input:
        path sample_file
    output:
        path "new_file_test.csv"
    script:
    """
    #!/usr/bin/env python
    import pandas as pd
    import subprocess
    var1 = pd.read_csv("${sample_file}")
    project_ids = []
    biosample_ids = []
    bs_proj_list_cmnd = f"bs list project"
    result_cmnd = subprocess.run(bs_proj_list_cmnd, shell=True, capture_output=True, text=True)
    bs_samp_list = result_cmnd.stdout.strip()
    print(bs_samp_list)
    for i, j in zip(var1['Project_name'], var1['Sample_ID']):
        print(j)
        #command = f"{bs_samp_list} | grep {i} | awk -F '|' '{print \$3}' | sed 's/ //g'" 
        command = "bs list project" + " | grep " + i + " | awk -F" + r" '|' '{print \$3}' | sed 's/ //g'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        project_id = result.stdout.strip()
        print(project_id)
        project_ids.append(project_id)
        command1 = f"bs upload dataset --project={project_id} $params.input_dir/{j}_S1_L001_R1_001.fastq.gz $params.input_dir/{j}_S1_L001_R2_001.fastq.gz"
        print(command1)
        #result1 = subprocess.run(command1, shell=True, capture_output=True, text=True)
        #print(result1.stdout)
        #print(result1.stderr)
        command_biosamp = "bs get biosample -n " + str(j) + " –terse | grep Id | head -1 | grep -Eo '[0-9]{1,}'"
        biosamp_run = subprocess.run(command_biosamp, shell=True, capture_output=True, text=True)
        biosample_id = biosamp_run.stdout.strip()
        biosample_ids.append(biosample_id)
    var1['Project_ID'] = project_ids
    print(biosample_ids)
    var1['Biosample_ID'] = biosample_ids
    var1.to_csv("new_file_test.csv", index=False)
    """
}
process preprocessing_for_launch {
    publishDir params.output_dir, mode:'copy'
    input:
        path sample_file
    output:
        path "test_file.csv"
    script:
    """
    #!/usr/bin/env python
    import pandas as pd
    import csv
    import re
    from datetime import datetime

    current_date = datetime.now().strftime("%d_%b_%y")
    bed_id_mapping = {"GE": 32335159063,"CE": 25985869859,"SE8": 23683257154,"FEV2F2both": 34857530934,"CDS": 31946210817,"CEfu": 32246847276}
    cnv_baseline = "cnv-baseline-id:26595964844,26596768352,26596768352,26597000441,26596302077,26596768331,26596296009,26596677367,26596984439,26596440110,26596089873,26596890400,26596199853,26595963870,26597226773,26596302095,26597235779,26596296030,26595984910,26595972945,26596669273,26596477171,26596089892,26595984889,26596677388,26596477187,26596861347,26596268048,26596565254,26596669289,26596247018,26595984929,26596477204,26596302112,26596199870,26596302128,26596477221,26595972961,26596302145,26595984953,26595991950,26595972980,26596199887,26596049977,26596565272,26596669311,26609829389,26596565288,26596302164"
    baseline_noise = "baseline-noise-bed:26693875133"
    cnv_baseline_se8 = "cnv-baseline-id:25791243964,25791291016,25791291033,25791291050,25791406163,25791440084,25791528878,25791528895,25791582119,25791582931,25791595964,25791595981,25791598767,25791637964,25791670919,25791679146,25791679164,25791681916,25791681933"
    baseline_noise_se8 = "baseline-noise-bed:25849773923"
    input_file = "${sample_file}"
    df = pd.read_csv(input_file)
    pattern_B = re.compile(r"-B[0-9]+|BB[0-9]+|B[0-9]+|-B")
    pattern_F = re.compile(r"-F[0-9]+|FF[0-9]+|F[0-9]+|-F")
    df["bed_id"] = df["Capturing_Kit"].map(bed_id_mapping)
    df["liquid_tumor"] = df["Sample_ID"].apply(lambda x: 1 if "-cf-" in x.lower() else 0) 
    df["vc_type"] = df["Sample_ID"].apply(lambda x: 0 if pattern_B.search(x) else 1)
    df["Somatic_Germline"] = df["Sample_ID"].apply(lambda x: "germline" if pattern_B.search(x) else ("somatic" if pattern_F.search(x) else "unknown"))
    df["appsession_name"] = df.apply(lambda row: f"{current_date}_{row['Test_Name']}_{row['Sample_Type']}_{row['Capturing_Kit']}_{row['Somatic_Germline']}", axis=1)
    df["vc-af-call-threshold"] = df["Sample_ID"].apply(lambda x: 1 if "-cf-" in x else 5)
    df["vc-af-filter-threshold"] = df["Sample_ID"].apply(lambda x: 5 if "-cf-" in x else 10)
    df["cnv_baseline_Id"] = df.apply(lambda row: cnv_baseline if ("INDIEGENE" in row["Test_Name"].upper() and row["Capturing_Kit"] == "CE" and row["Somatic_Germline"] in ["somatic", "germline"]) else (cnv_baseline_se8 if ("ABSOLUTE" in row["Test_Name"].upper() and row["Capturing_Kit"] == "SE8" and row["Somatic_Germline"] in ["somatic", "germline"]) else row["cnv_baseline_Id"]), axis=1)
    df["baseline-noise-bed"] = df.apply(lambda row: baseline_noise if ("INDIEGENE" in row["Test_Name"].upper() and row["Capturing_Kit"] == "CE" and row["Somatic_Germline"] == "somatic" ) else (baseline_noise_se8 if ("ABSOLUTE" in row["Test_Name"].upper() and row["Capturing_Kit"] == "SE8" and row["Somatic_Germline"] == "somatic") else row["baseline-noise-bed"]), axis=1)
    df.to_csv("test_file.csv", index=False)
    """    
}
process bs_launch{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    #!/usr/bin/env python
    import pandas as pd
    import subprocess
    file1 = pd.read_csv("${sample_file}")
    grouped_samp=file1.groupby(["Capturing_Kit","Somatic_Germline"])["Biosample_ID"].apply(lambda x: ",".join(map(str, map(int, x))))
    print(grouped_samp)
    biosamp_FEV2 =", ".join(map(str, [grouped_samp.loc["FEV2F2both", "somatic"]]))
    print(biosamp_FEV2)
    biosamp_CE_som=", ".join(map(str, [grouped_samp.loc["CE", "somatic"]]))
    print(biosamp_CE_som)
    biosamp_GE_som=", ".join(map(str, [grouped_samp.loc["GE", "somatic"]]))
    biosamp_SE8_som=", ".join(map(str, [grouped_samp.loc["SE8", "somatic"]]))
    biosamp_CE_germ=", ".join(map(str, [grouped_samp.loc["CE", "germline"]]))
    biosamp_GE_germ=", ".join(map(str, [grouped_samp.loc["GE", "germline"]]))
    biosamp_SE8_germ=", ".join(map(str, [grouped_samp.loc["SE8", "germline"]]))
    for test_name,capr_kit,proj_id, appsession_name, bed_id, liq_tm,vc_af_call, vc_af_filt,cnv_base,noise_base,germ_som , vc_type in zip(file1['Test_Name'],file1['Capturing_Kit'],file1['Project_ID'],file1['appsession_name'],file1['bed_id'],file1['liquid_tumor'],file1['vc-af-call-threshold'],file1['vc-af-filter-threshold'],file1['cnv_baseline_Id'],file1['baseline-noise-bed'],file1['Somatic_Germline'],file1['vc_type']):
        if "somatic" in germ_som:
            if "TARGT_FIRST" in test_name:
                if "FEV2F2both" in capr_kit:
                    command_bs_launch = f"bs launch application -n" +f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_FEV2} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:"+f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                    print(command_bs_launch)
                    bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                    bs_launch = bs_launch_run.stdout.strip()
                    print("STDOUT:", bs_launch_run.stdout)
                    print("STDERR:", bs_launch_run.stderr)
            elif "INDIEGENE" in test_name:
                if "CE" in capr_kit: 
                    biosamp=",".join(map(str, grouped_samp.loc["CE", "somatic"]))
                    command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_CE_som} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o {noise_base} -o vcf-site-filter:1 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                    print(command_bs_launch)
                    bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                    bs_launch = bs_launch_run.stdout.strip()
                    print("STDOUT:", bs_launch_run.stdout)
                    print("STDERR:", bs_launch_run.stderr)
                elif "GE" in capr_kit:
                    biosamp=",".join(map(str, grouped_samp.loc["GE", "somatic"]))
                    command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_GE_som} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:0 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                    print(command_bs_launch)
                    bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                    bs_launch = bs_launch_run.stdout.strip()
                    print("STDOUT:", bs_launch_run.stdout)
                    print("STDERR:", bs_launch_run.stderr)
            elif "ABSOLUTE" in test_name:
                if "SE8" in capr_kit:
                    command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_SE8_som} -o picard_checkbox:1 -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o {noise_base} -o vcf-site-filter:1 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                    print(command_bs_launch)
                    bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                    bs_launch = bs_launch_run.stdout.strip()
                    print("STDOUT:", bs_launch_run.stdout)
                    print("STDERR:", bs_launch_run.stderr)
        elif "germline" in germ_som:
            if "INDIEGENE" in test_name: 
                if "CE" in capr_kit:
                    command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_CE_germ} -o picard_checkbox:1 -o sv_checkbox:1 -o tmb:0 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                    bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                    bs_launch = bs_launch_run.stdout.strip()
                    print("STDOUT:", bs_launch_run.stdout)
                    print("STDERR:", bs_launch_run.stderr)
                elif "GE" in capr_kit:
                    command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_GE_germ} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:0 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                    print(command_bs_launch)
                    bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                    bs_launch = bs_launch_run.stdout.strip()
                    print("STDOUT:", bs_launch_run.stdout)
                    print("STDERR:", bs_launch_run.stderr)
            elif "ABSOLUTE" in test_name:
                if "SE8" in capr_kit:
                    command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_SE8_germ} -o picard_checkbox:1 -o sv_checkbox:1 -o tmb:0 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o cnv_gcbias_checkbox:1 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
                    print(command_bs_launch)
                    bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                    bs_launch = bs_launch_run.stdout.strip()
                    print("STDOUT:", bs_launch_run.stdout)
                    print("STDERR:", bs_launch_run.stderr)
    """
}
workflow {
    //Renaming() 
    extract_and_upload_samples(params.sample_file)
    preprocessing_for_launch(extract_and_upload_samples.out)
    bs_launch(preprocessing_for_launch.out)
}