params.input_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/fastq_test_Nextflow"
params.sample_file = "/home/pragati_4bc/NGS3Pipeline_Nextflow/fastq_test_Nextflow/test_ngs3_nextflow_Copy.csv"
params.output_dir = "output"
params.project = "old"
params.project_name = "New_Project"
process Renaming{
    publishDir params.output_dir, mode:'copy'
    output:
        path "output.csv"
    script:
    """
    Rename_combined.py "${params.input_dir}" "${params.sample_file}" "output.csv"
    """
}
process create_project{
    publishDir params.output_dir, mode:'copy'
    input:
        path sample_file
        val project_name
    output:
        path "created_proj.csv"
    script:
    """
    Create_project.py --sample_file "${sample_file}" --project_name "${project_name}"
    """
}
process extract_and_upload_samples {
    publishDir params.output_dir, mode:'copy'
    input:
        path sample_file
    output:
        path "new_file_test.csv"
    script:
    """
    extract_and_upload_samples.py "${sample_file}" "${params.input_dir}" new_file_test.csv
    """
}
process preprocessing_for_launch{
    publishDir params.output_dir, mode:'copy'
    input:
        path sample_file
    output:
        path "test_file.csv"
    script:
    """
    preprocessing_for_launch.py "${sample_file}" test_file.csv
    """
    
}
process Target_first{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    Target_First.py "${sample_file}"
    """
}
process Indiegene_GE_Som{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    Indiegene_GE_som.py "${sample_file}"
    """

}
process Indiegene_GE_germ {
    input:
        path sample_file
    output:
        stdout
    script:
    """
    Indiegene_GE_germ.py "${sample_file}"
    """
}
process Indiegene_CE_som{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    Indiegene_CE_som.py "${sample_file}"
    """
}
process Indiegene_CE_germ{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    Indiegene_CE_germ.py "${sample_file}"
    """
}
process SE8_som{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    SE8_som.py "${sample_file}"
    """
}
process SE8_germ{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    SE8_germ.py "${sample_file}"
    """
}
process CDS{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    CDS.py "${sample_file}"
    """
}
process RNA_CT{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    RNA_CT.py "${sample_file}"
    """
}
process RNA_SE8{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    RNA_ST8.py "${sample_file}"
    """
}
process Indiegene_CEFu{
    input:
        path sample_file
    output:
        stdout
    script:
    """
    Indiegene_CEFu.py "${sample_file}"
    """
}

process QC{
    input:
        path output_loc
        path sample_file
    output:
        stdout
    script:
    """
    VCF_download_QC_extract.py "${output_loc}" "${sample_file}"
    """
}

process CNV_FeV2{
    publishDir params.output_dir, mode:'copy'
    input:
        path output_loc
        path sample_file
    output:
        path "*", optional: true
    script:
    """
    bash ${projectDir}/bin/CNV_New.sh "${params.output_dir}" "${params.sample_file}"
    
    """
}
process CNV_Indiegene{
    publishDir "${params.output_dir}/CNV/Indiegene", mode:'copy'
    input:
        path output_loc
        path sample_file
    output:
        path "*", optional: true
    script:    
    """
    bash ${projectDir}/bin/cnv_annotation_somatic_CE.sh "${params.output_dir}" "${params.sample_file}"
    
    """
}

process DNA_fusion{
    publishDir "${params.output_dir}/Fusion", mode:'copy'
    input:
        path output_dir
        path sample_file
    output:
        path "*_fusions", optional: true
        path "*intersected.bam", optional: true
        path "*intersected.bam.bai", optional: true
    script:
    """
    awk -F',' 'BEGIN {OFS=","} {if (NR>1) print \$(NF-2)}' "${sample_file}" > ${projectDir}/bin/FuSeq_WES_v1.0.0/list_test.txt
    bash ${projectDir}/bin/FuSeq_WES_v1.0.0/FuSeq_BAM_FUS_auto.sh "${params.output_dir}" "${sample_file}"
    """       
}
process Hotspot{
    publishDir "${params.output_dir}/Hotspot", mode:'copy'
    input:
        path output_dir
        path sample_file
    output:
        path "*_alt_pipeline.vcf", optional: true
        path "*_Hotspot_V2.xlsx", optional: true
    script:
        """
        Alternate_VariantCaller_to_Hotspot_V2_09_Apr_24.py "." "${sample_file}"
        """
}

process Gene_Coverage {
    publishDir "${params.output_dir}/GeneCoverage", mode:'copy'
    input:
        path input_dir
        path sample_file
    output:
        path "*"
    script:
    """
    Gene_Coverage_via_Mosdepth_V2.py "${sample_file}" Test.xlsx
    """
}

workflow{
    QC(params.output_dir,params.sample_file)
    CNV_FeV2(params.output_dir,params.sample_file)
    CNV_Indiegene(params.output_dir,params.sample_file)
    DNA_fusion(params.output_dir,params.sample_file)
    //Hotspot(params.output_dir,params.sample_file)
    //Gene_Coverage(params.output_dir,params.sample_file)
}
