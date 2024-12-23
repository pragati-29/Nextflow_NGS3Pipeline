params.input_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/sample/sample"
params.reads = "$params.input_dir/*_{R1_001,R2_001}.fastq.gz"
//params.project_name_somatic = "DNA_Test_Somatic_Nextflow_NGS3Pipeline_3Dec2024"
//params.project_name_germline ="DNA_Test_Germline_Nextflow_NGS3Pipeline_3Dec2024"
//params.project_name_rna = "RNA_Test_Somatic_Nextflow_NGS3Pipeline_2Dec2024"
params.project_name = "DNA_Test_Somatic_Nextflow_NGS3Pipeline_3Dec2024"
params.bs_samp_list = "/home/pragati_4bc/bs_project_list.txt"

process Renaming {
    script:
	""" echo "hello" > out_test.txt"""
//"""python3 /workspace/gitpod/hello-nextflow/ggal_test/Rename_combined.py "${params.input_dir}" """
}
process bs_list {
    input:
        path input_file
        val project_name
    output:
        stdout
    script:
    """
    grep "$project_name" $input_file | awk -F '|' '{print \$3}' | sed 's/ //g'
    """
}
process upload_bs{
input:
    tuple val(sample_id), path(reads)
    val project
script:
"""
 shopt -s nocasematch
 if [[ ($sample_id =~ -F- || $sample_id =~ -Z- || $sample_id =~ -F[0-9]+ || $sample_id =~ -B[0-9]+ || $sample_id =~ -cf-) && ! ($sample_id =~ -CT- || $sample_id =~ -ST8-) ]]; then
    bs upload dataset --project="${project}" ${reads[0]} ${reads[1]}
 elif [[ $sample_id =~ -B- && ! $sample_id =~ -cf- ]]; then
    bs upload dataset --project="${project}" ${reads[0]} ${reads[1]}
 elif [[ $sample_id =~ -CT- || $sample_id =~ -ST8- ]]; then
    bs upload dataset --project="${project}" ${reads[0]} ${reads[1]}
 fi
"""
}
workflow {
    Renaming()
    //upload_bs("${params.input_dir}","${params.project_id_DNA_somatic}", "${params.project_id_DNA_Germline}","${params.project_id_RNA}","${params.sam_pattern}")
    bs_list(params.bs_samp_list,params.project_name)
	Channel
        .fromFilePairs(params.reads, checkIfExists: true)
        .set { read_pairs_ch }
    
	upload_channel=upload_bs(read_pairs_ch, bs_list.out)
}
