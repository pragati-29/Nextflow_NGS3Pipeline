params.input_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/Dragen_val_sample"
params.bs_samp_list = "/home/pragati_4bc/NGS3Pipeline_Nextflow/Dragen_val_sample/bs_project_list.txt"
params.sample_file = "/home/pragati_4bc/NGS3Pipeline_Nextflow/Dragen_val_sample/test_ngs3_nextflow_Copy.csv"
process Renaming{
    script:
        """python3 ${params.input_dir}/Rename_combined.py "${params.input_dir}/demo" """
}
process extract_and_upload_samples {

    input:
        path bs_samp_list
        path sample_file
    output:
        stdout
    script:
    """
    #!/usr/bin/env python
    import pandas as pd
    import subprocess
    var1 = pd.read_csv("${sample_file}")
    project_ids = []
    biosample_ids = []
    for i, j in zip(var1['Project_name'], var1['Sample_ID']):
        print(j)
        command = f"grep {i} ${bs_samp_list} | awk -F '|' '{{print \$3}}' | sed 's/ //g'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        project_id = result.stdout.strip()
        print(project_id)
        project_ids.append(project_id)
        command1 = f"bs upload dataset --project={project_id} {j}_S1_L001_R1_001.fastq.gz {j}_S1_L001_R2_001.fastq.gz"
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
    updated_file = "${sample_file}".replace("test_ngs3_nextflow_Copy.csv", "test_ngs3_nextflow_Copy.csv")
    var1.to_csv(updated_file, index=False)
    """
}
process preprocessing_for_launch {
    input:
        path sample_file
    output:
        stdout
    script:
    """
    #!/usr/bin/env python
    import pandas as pd
    import csv
    from datetime import datetime

    current_date = datetime.now().strftime("%d_%b_%y")
    bed_id_mapping = {"GE": 32335159063,"CE": 25985869859,"SE8": 23683257154,"FEV2F2both": 34857530934,"CDS": 31946210817,"CEfu": 32246847276}
    cnv_baseline = "cnv-baseline-id:26595964844,26596768352,26596768352,26597000441,26596302077,26596768331,26596296009,26596677367,26596984439,26596440110,26596089873,26596890400,26596199853,26595963870,26597226773,26596302095,26597235779,26596296030,26595984910,26595972945,26596669273,26596477171,26596089892,26595984889,26596677388,26596477187,26596861347,26596268048,26596565254,26596669289,26596247018,26595984929,26596477204,26596302112,26596199870,26596302128,26596477221,26595972961,26596302145,26595984953,26595991950,26595972980,26596199887,26596049977,26596565272,26596669311,26609829389,26596565288,26596302164"
    baseline_noise = "baseline-noise-bed:26693875133"
    input_file = "${sample_file}"
    output_file = "${sample_file}"
    df = pd.read_csv(input_file)
    df["appsession_name"] = df.apply(lambda row: f"{current_date}_{row['Test_Name']}_{row['Sample_Type']}", axis=1)
    df["bed_id"] = df["Capturing_Kit"].map(bed_id_mapping)
    df["liquid_tumor"] = df["Sample_ID"].apply(lambda x: 1 if "cf" in x.lower() else 0)
    df["vc-af-call-threshold"] = df["Sample_ID"].apply(lambda x: 1 if "cf" in x.lower() else 5)
    df["vc-af-filter-threshold"] = df["Sample_ID"].apply(lambda x: 5 if "cf" in x.lower() else 10)
    df["cnv_baseline_Id"] = df.apply(lambda row: cnv_baseline if (row["Test_Name"] == "INDIEGENE" and row["Capturing_Kit"] == "CE") else "",axis=1)
    df["baseline-noise-bed"] = df.apply(lambda row: baseline_noise if (row["Test_Name"] == "INDIEGENE" and row["Capturing_Kit"] == "CE") else "",axis=1)
    df.to_csv(output_file, index=False)
    print(f"Updated CSV file has been saved as '{output_file}'.") 
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
    print(file1)
    for test_name,biosamp, proj_id, appsession_name, bed_id, liq_tm,vc_af_call, vc_af_filt,cnv_base,noise_base in zip(file1['Test_Name'],file1['Biosample_ID'],file1['Project_ID'],file1['appsession_name'],file1['bed_id'],file1['liquid_tumor'],file1['vc-af-call-threshold'],file1['vc-af-filter-threshold'],file1['cnv_baseline_Id'],file1['baseline-noise-bed']):
        if "TARGT_First" in test_name:
            command_bs_launch = f"bs launch application -n" +f' "DRAGEN Enrichment"' + f" --app-version 4.2.7 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:"+f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
            print(command_bs_launch)
            bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
            bs_launch = bs_launch_run.stdout.strip()
            print("STDOUT:", bs_launch_run.stdout)
            print("STDERR:", bs_launch_run.stderr)
        elif "INDIEGENE" in test_name:
            command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 4.2.7 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o {noise_base} -o vcf-site-filter:1 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
            print(command_bs_launch)
            bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
            bs_launch = bs_launch_run.stdout.strip()
            print("STDOUT:", bs_launch_run.stdout)
            print("STDERR:", bs_launch_run.stderr)
        
    """
}
workflow {
    //Renaming() 
    //extract_and_upload_samples(params.bs_samp_list, params.sample_file)
    //preprocessing_for_launch(params.sample_file)
    bs_launch(params.sample_file)
}
