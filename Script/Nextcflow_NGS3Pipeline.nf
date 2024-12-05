// Parameters
params.input_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/sample"
params.reads = "$params.input_dir/*_{R1_001,R2_001}.fastq.gz"
println "${params.input_dir}"
params.output_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/Output"
//params.project_id_file = "/media/bioinfoa/bioinfo2/Pragati/NGS3Pipeline_Nextflow/project_ids.txt"
params.project_id_DNA_somatic = "" //"439358925"
params.project_id_DNA_Germline = "" //"439405970"
params.project_id_RNA = "" //"439358924"
process Renaming {

    script:
	""" echo "hello" > out_test.txt"""
//"""python3 /media/bioinfoa/bioinfo2/Pragati/NGS3Pipeline_Nextflow/Rename_combined.py "${params.input_dir}"
//"""
}
process upload_bs{
    publishDir params.somatic_folder, mode:"copy"
    publishDir params.germline_folder, mode:"copy"
    publishDir params.RNA, mode:"copy"
input:
    tuple val(sample_id), path(reads)
output:
    "*"
script:
"""
 if [[ $sample_id =~ -F- ]]; then
	bs upload dataset --project=$params.project_id_DNA_somatic ${reads[0]} ${reads[1]}
 elif [[ $sample_id =~ -B- ]]; then
	bs upload dataset --project=$params.project_id_DNA_Germline ${reads[0]} ${reads[1]}
 elif [[ $sample_id =~ -CT- ]]; then
	bs upload dataset --project=$params.project_id_RNA ${reads[0]} ${reads[1]}
 fi
"""
}
// Workflow Definition
workflow {
    Renaming()
    //upload_bs("${params.input_dir}","${params.project_id_DNA_somatic}", "${params.project_id_DNA_Germline}","${params.project_id_RNA}","${params.sam_pattern}")
	Channel
        .fromFilePairs(params.reads, checkIfExists: true)
        .set { read_pairs_ch }
	upload_bs(read_pairs_ch)
}
