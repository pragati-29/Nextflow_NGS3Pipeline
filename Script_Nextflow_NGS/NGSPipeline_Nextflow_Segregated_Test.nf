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


workflow{
    Renaming()
    if (params.project == "new") {
       project_output = create_project(Renaming.out, params.project_name)
    } else {
        project_output = Renaming.out
    }
    extract_and_upload_samples(project_output)
    preprocessing_for_launch(extract_and_upload_samples.out)
    Target_first(preprocessing_for_launch.out)
    Indiegene_GE_Som(preprocessing_for_launch.out)
    Indiegene_GE_germ(preprocessing_for_launch.out)
    Indiegene_CE_som(preprocessing_for_launch.out)
    Indiegene_CE_germ(preprocessing_for_launch.out)
    SE8_som(preprocessing_for_launch.out)
    SE8_germ(preprocessing_for_launch.out)
    CDS(preprocessing_for_launch.out)
    RNA_CT(preprocessing_for_launch.out)
    RNA_SE8(preprocessing_for_launch.out)
    Indiegene_CEFu(preprocessing_for_launch.out)
}
