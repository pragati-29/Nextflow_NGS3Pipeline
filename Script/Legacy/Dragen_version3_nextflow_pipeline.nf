params.input_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/Dragen_val_sample"
params.bs_samp_list = "/home/pragati_4bc/NGS3Pipeline_Nextflow/Dragen_val_sample/bs_project_list.txt"
params.sample_file = "/home/pragati_4bc/NGS3Pipeline_Nextflow/Dragen_val_sample/test_ngs3_nextflow_Copy.csv"
//params.bed_file = "/home/pragati_4bc/NGS3Pipeline_Nextflow/sample/sample/TarGT_First_v2_FEV2F2both_cnv_coverage.bed"
params.output_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/Dragen_val_sample/Output"
process Renaming{
    script:
        """python3 ${params.input_dir}/Rename_combined.py "${params.input_dir}/demo" """
}

process extract_and_upload_samples {
    publishDir params.output_dir, mode:'copy'

    input:
        path bs_samp_list
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
    from datetime import datetime

    current_date = datetime.now().strftime("%d_%b_%y")
    bed_id_mapping = {"GE": 32335159063,"CE": 25985869859,"SE8": 23683257154,"FEV2F2both": 34857530934,"CDS": 31946210817,"CEfu": 32246847276}
    cnv_baseline = "cnv-baseline-id:26595964844,26596768352,26596768352,26597000441,26596302077,26596768331,26596296009,26596677367,26596984439,26596440110,26596089873,26596890400,26596199853,26595963870,26597226773,26596302095,26597235779,26596296030,26595984910,26595972945,26596669273,26596477171,26596089892,26595984889,26596677388,26596477187,26596861347,26596268048,26596565254,26596669289,26596247018,26595984929,26596477204,26596302112,26596199870,26596302128,26596477221,26595972961,26596302145,26595984953,26595991950,26595972980,26596199887,26596049977,26596565272,26596669311,26609829389,26596565288,26596302164"
    baseline_noise = "baseline-noise-bed:26693875133"
    input_file = "${sample_file}"
    df = pd.read_csv(input_file)
    df["appsession_name"] = df.apply(lambda row: f"{current_date}_{row['Test_Name']}_{row['Sample_Type']}", axis=1)
    df["bed_id"] = df["Capturing_Kit"].map(bed_id_mapping)
    df["liquid_tumor"] = df["Sample_ID"].apply(lambda x: 1 if "cf" in x.lower() else 0)
    df["vc-af-call-threshold"] = df["Sample_ID"].apply(lambda x: 1 if "cf" in x.lower() else 5)
    df["vc-af-filter-threshold"] = df["Sample_ID"].apply(lambda x: 5 if "cf" in x.lower() else 10)
    df["cnv_baseline_Id"] = df.apply(lambda row: cnv_baseline if (row["Test_Name"] == "INDIEGENE" and row["Capturing_Kit"] == "CE") else "",axis=1)
    df["baseline-noise-bed"] = df.apply(lambda row: baseline_noise if (row["Test_Name"] == "INDIEGENE" and row["Capturing_Kit"] == "CE") else "",axis=1)
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
    print(file1)
    for test_name,biosamp, proj_id, appsession_name, bed_id, liq_tm,vc_af_call, vc_af_filt,cnv_base,noise_base in zip(file1['Test_Name'],file1['Biosample_ID'],file1['Project_ID'],file1['appsession_name'],file1['bed_id'],file1['liquid_tumor'],file1['vc-af-call-threshold'],file1['vc-af-filter-threshold'],file1['cnv_baseline_Id'],file1['baseline-noise-bed']):
        if "TARGT_First" in test_name:
            command_bs_launch = f"bs launch application -n" +f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:"+f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
            print(command_bs_launch)
            bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
            bs_launch = bs_launch_run.stdout.strip()
            print("STDOUT:", bs_launch_run.stdout)
            print("STDERR:", bs_launch_run.stderr)
        elif "INDIEGENE" in test_name:
            command_bs_launch = f"bs launch application -n" + f' "DRAGEN Enrichment"' + f" --app-version 3.9.5 -o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp} -o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o {noise_base} -o vcf-site-filter:1 -o cnv_checkbox:1 -o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 -o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:" +f'"--read-trimmers:adapter --trim-adapter-read1"' + f" -o additional-file:25600057590 -o automation-sex:unknown"
            print(command_bs_launch)
            bs_launch_run = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
            bs_launch = bs_launch_run.stdout.strip()
            print("STDOUT:", bs_launch_run.stdout)
            print("STDERR:", bs_launch_run.stderr)
        
    """
}

/*process preprocessing_for_launch {
    input:
        path sample_file
    output:
        stdout
    script:
    """
    #!/usr/bin/env python
    import csv
    from datetime import datetime
    current_date = datetime.now().strftime("%d_%b_%y")
    bed_id_mapping = {"GE": 32335159063,"CE": 25985869859,"SE8": 23683257154,"FEV2F2both": 34857530934,"CDS": 31946210817,"CEfu": 32246847276}
    bed_id = []
    appsession_name = []
    input_file = "${sample_file}" 
    output_file = "${sample_file}"
    with open("${sample_file}", newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        header.extend(["bed_id", "appsession_name"])
        rows = []
        for row in reader:
            test, sample, sample_type, project_name, samples, project_id, biosam_id = row[:7]
            appsession_name = f"{current_date}_{test}_{sample_type}"
            bed_id = next((value for key, value in bed_id_mapping.items() if key in sample_type), "")
            row.extend([bed_id, appsession_name])
            rows.append(row)
    with open(output_file, mode="w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)  # Write the updated header
        writer.writerows(rows)
    """    
}*/
/*process bs_launch {
    input:
        path sample_file
    output:
        stdout
    script:
    """
    #!/bin/bash
    current_date=\$(date +'%d_%b_%y')
    formatted_date=\$(basename "\$current_date")
    while IFS=',' read -r test sample sample_type project_name samples project_id biosam_id; do
    if [[ "\$test" == "Test" ]]; then
        # Skip header row
        continue
    fi
        test=\$(awk -F, 'NR==2 {print \$1}' "${sample_file}")
        sample=\$(awk -F, 'NR==2 {print \$2}' "${sample_file}")
        sample_type=\$(awk -F, 'NR==2 {print \$3}' "${sample_file}")
        project_name=\$(awk -F, 'NR==2 {print \$4}' "${sample_file}")
        samples=\$(awk -F, 'NR==2 {print \$5}' "${sample_file}")
        project_id=\$(awk -F, 'NR==2 {print \$6}' "${sample_file}")
        appsession_name="\${formatted_date}_\${test}_\${sample_type}"
        biosam_id=\$(awk -F, 'NR==2 {print \$7}' "${sample_file}")
        echo "\$appsession_name"
        echo "\$sample"
        echo "\$samples"
        echo "\$sample_type"
        echo "\$project_name"
        echo "\$project_id"
        echo "\$biosam_id"
        # Logic for bed_id
        if [[ \$sample_type =~ GE ]]; then
            bed_id=32335159063
        elif [[ \$sample_type =~ CE ]]; then
            bed_id=25985869859
        elif [[ \$sample_type =~ SE8 ]]; then
            bed_id=23683257154
        elif [[ \$sample_type =~ FEV2F2both ]]; then
            bed_id=34857530934
        elif [[ \$sample_type =~ CDS ]]; then
            bed_id=31946210817
        elif [[ \$sample_type =~ CEfu ]]; then
            bed_id=32246847276
        else
            bed_id=""
        fi
        if [[ \$sample =~ DNA ]]; then
            if [[ \$sample_type =~ FEV2F2both ]]; then
                if [[ \$samples =~ -cf- ]] && ! [[ \$samples =~ -CE ]]; then
                    echo "FEV2F2both cfDNA samples present in the folder"
                    #project_id=\$(awk -F',' -v sample_type=\$sample_type -v samples=\$samples '\$5 == \$sample_type && \$3 == "\$samples {print \$6}' "${sample_file}")
                    sample_list=\$(awk -F',' -v project_id=\$project_id -v sample_type=CDS '\$6 == project_id && \$3 == sample_type && NR > 1 {printf "%s", (NR > 2 ? "," : ""); printf "%d", \$7}' "${sample_file}")
                    #bs launch application -n \"DRAGEN Enrichment\" --app-version 3.9.5 -o project-id:\$project_id -o app-session-name:\$appsession_name -l \$appsession_name -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:\$bed_id -o input_list.sample-id:biosamples/\$sample_list -o picard_checkbox:1 -o liquid_tumor:1 -o af-filtering:1 -o vc-af-call-threshold:1 -o vc-af-filter-threshold:5 -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:\"--read-trimmers:adapter --trim-adapter-read1\" -o additional-file:25600057590 -o automation-sex:unknown
                elif [[ \$samples =~ -FEV2F2both- ]] && ! [[ \$samples =~ -CE ]]; then
                    echo "FEV2F2both samples present in the folder"
                    #project_id=\$(awk -F',' -v sample_type=\$sample_type '\$5 == \$sample_type && \$3 == "FEV2F2both" {print \$6}' "${sample_file}")
                    echo "\$project_id"
                    sample_list=\$(awk -F',' -v project_id=\$project_id -v sample_type=CDS '\$6 == project_id && \$3 == sample_type && NR > 1 {printf "%s", (NR > 2 ? "," : ""); printf "%d", \$7}' "${sample_file}")
                    echo "bs launch application -n \"DRAGEN Enrichment\" --app-version 3.9.5 -o project-id:\$project_id -o app-session-name:\$appsession_name -l \$appsession_name -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:\$bed_id -o input_list.sample-id:biosamples/\$sample_list -o picard_checkbox:1 -o af-filtering:1 -o vc-af-call-threshold:5 -o vc-af-filter-threshold:10 -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:\"--read-trimmers:adapter --trim-adapter-read1\" -o additional-file:25600057590 -o automation-sex:unknown"
                fi
            elif [[ \$sample_type =~ CDS ]]; then
                if [[ \$samples =~ -cf- ]] && ! [[ \$samples =~ -CE ]]; then
                    echo "CDS cfDNA samples present in the folder"
                    #project_id=\$(awk -F',' -v sample_type=\$sample_type '\$5 == \$sample_type && \$3 == "FEV2F2both" {print \$6}' "${sample_file}")
                    sample_list=\$(awk -F',' -v project_id=\$project_id -v sample_type=CDS '\$6 == project_id && \$3 == sample_type && NR > 1 {printf "%s", (NR > 2 ? "," : ""); printf "%d", \$7}' "${sample_file}")
                    #bs launch application -n \"DRAGEN Enrichment\" --app-version 3.9.5 -o project-id:\$project_id -o app-session-name:\$appsession_name -l \$appsession_name -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:\$bed_id -o input_list.sample-id:biosamples/\$sample_list -o picard_checkbox:1 -o liquid_tumor:1 -o af-filtering:1 -o vc-af-call-threshold:1 -o vc-af-filter-threshold:5 -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:\"--read-trimmers:adapter --trim-adapter-read1\" -o additional-file:25600057590 -o automation-sex:unknown
                elif [[ \$samples =~ -CDS- ]] && ! [[ \$samples =~ -CE ]]; then
                    echo "CDS somatic samples present in the folder"
                    #project_id=\$(awk -F',' -v sample_type=\$sample_type '\$5 == \$sample_type && \$3 == "FEV2F2both" {print \$6}' "${sample_file}")
                    echo "awk -F',' '\$5 == \$sample_type && \$3 == "FEV2F2both" {print \$6}' "${sample_file}""
                    sample_list=\$(awk -F',' -v project_id=\$project_id -v sample_type=CDS '\$6 == project_id && \$3 == sample_type && NR > 1 {printf "%s", (NR > 2 ? "," : ""); printf "%d", \$7}' "${sample_file}")
                    echo "bs launch application -n \"DRAGEN Enrichment\" --app-version 3.9.5 -o project-id:\$project_id -o app-session-name:\$appsession_name -l \$appsession_name -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:\$bed_id -o input_list.sample-id:biosamples/\$sample_list -o picard_checkbox:1 -o af-filtering:1 -o vc-af-call-threshold:5 -o vc-af-filter-threshold:10 -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:\"--read-trimmers:adapter --trim-adapter-read1\" -o additional-file:25600057590 -o automation-sex:unknown"
                fi
            fi
        fi
    done < <(tail -n +2 "${sample_file}")
    """
}*/
workflow {
    //Renaming() 
    extract_and_upload_samples(params.bs_samp_list, params.sample_file)
    preprocessing_for_launch(extract_and_upload_samples.out)
    bs_launch(preprocessing_for_launch.out)
}
