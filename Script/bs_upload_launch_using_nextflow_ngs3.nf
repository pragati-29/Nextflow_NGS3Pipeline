params.input_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/sample/sample"
params.bs_samp_list = "/home/pragati_4bc/NGS3Pipeline_Nextflow/sample/sample/bs_project_list.txt"
params.sample_file = "/home/pragati_4bc/NGS3Pipeline_Nextflow/sample/sample/test_ngs3_nextflow_Copy.csv"
params.bed_file = "/home/pragati_4bc/NGS3Pipeline_Nextflow/sample/sample/TarGT_First_v2_FEV2F2both_cnv_coverage.bed"

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
        command = f"grep {i} ${bs_samp_list} | awk -F '|' '{{print \$3}}' | sed 's/ //g'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        project_id = result.stdout.strip()
        project_ids.append(project_id)
        #command1 = f"bs upload dataset --project={project_id} {j}_S1_L001_R1_001.fastq.gz {j}_S1_L001_R2_001.fastq.gz"
        #result1 = subprocess.run(command1, shell=True, capture_output=True, text=True)
        #print(result1.stdout)
        #print(result1.stderr)
        command_biosamp = "bs get biosample -n " + str(j) + " –terse | grep Id | head -1 | grep -Eo '[0-9]{1,}'"
        biosamp_run = subprocess.run(command_biosamp, shell=True, capture_output=True, text=True)
        biosample_id = biosamp_run.stdout.strip()
        print(j)
        biosample_ids.append(biosample_id)
    var1['Project_ID'] = project_ids
    print(biosample_ids)
    var1['Biosample_ID'] = biosample_ids
    updated_file = "${sample_file}".replace("test_ngs3_nextflow_Copy.csv", "test_ngs3_nextflow_Copy.csv")
    var1.to_csv(updated_file, index=False)
    """
}

process bs_launch {
    input:
        path sample_file
    output:
        stdout
    script:
    """
    #!/bin/bash
    current_date=\$(date +'%d_%b_%y')
    formatted_date=\$(basename "\$current_date")
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
        if [[ \$samples =~ -cf- ]] && ! [[ "\$samples" =~ -CE ]]; then
            echo "FEV2F2both cfDNA samples present in the folder"
            bs launch application -n \"DRAGEN Enrichment\" --app-version 3.9.5 -o project-id:\$project_id -o app-session-name:\$appsession_name -l \$appsession_name -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:\$bed_id -o input_list.sample-id:biosamples/\$biosam_id -o picard_checkbox:1 -o liquid_tumor:1 -o af-filtering:1 -o vc-af-call-threshold:1 -o vc-af-filter-threshold:5 -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:\"--read-trimmers:adapter --trim-adapter-read1\" -o additional-file:25600057590 -o automation-sex:unknown
        elif [[ \$samples =~ -FEV2F2both- ]] && ! [[ \$samples =~ -CE ]]; then
            echo "FEV2F2both samples present in the folder"
            bs launch application -n \"DRAGEN Enrichment\" --app-version 3.9.5 -o project-id:\$project_id -o app-session-name:\$appsession_name -l \$appsession_name -o vc-type:1 -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom -o target_bed_id:\$bed_id -o input_list.sample-id:biosamples/\$biosam_id -o picard_checkbox:1 -o af-filtering:1 -o vc-af-call-threshold:5 -o vc-af-filter-threshold:10 -o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 -o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true -o arbitrary:\"--read-trimmers:adapter --trim-adapter-read1\" -o additional-file:25600057590 -o automation-sex:unknown
        fi
    fi
    """
}

workflow {
    extract_and_upload_samples(params.bs_samp_list, params.sample_file)
    bs_launch(params.sample_file)
}
