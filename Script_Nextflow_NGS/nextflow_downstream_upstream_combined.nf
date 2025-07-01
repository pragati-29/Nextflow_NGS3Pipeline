// Input Parameters:
params.input_dir = "path/to/input_dir"
params.sample_file = "path/to/nf_MANIFEST.csv"
params.output_dir = "path/to/output"
params.project = "old"
params.project_name = "New_Project"

// Upstream Processes:
process Renaming {
    publishDir params.output_dir, mode: 'copy'

    input:
    val setup

    script:
    """
    Rename_combined.py "${params.input_dir}" "${params.sample_file}" "bs_compliant_sample_renamed.csv"
    """

    output:
    path "bs_compliant_sample_renamed.csv"
}
process create_project {
    publishDir params.output_dir, mode: 'copy'

    input:
    path sample_file
    val project_name
    val setup

    script:
    """
    Create_project.py --sample_file "${sample_file}" --project_name "${project_name}"
    """

    output:
    path "created_proj.csv"
}
process extract_and_upload_samples {
    publishDir params.output_dir, mode: 'copy'

    input:
    path sample_file
    val setup

    script:
    """
    bs_preanalysis.py "${sample_file}" "${params.input_dir}" preanalysis_details.csv
    """

    output:
    path "preanalysis_details.csv"
}
process preprocessing_for_launch {
    publishDir params.output_dir, mode: 'copy'

    input:
    path sample_file
    val setup

    script:
    """
    preprocessing_for_launch.py "${sample_file}" nf_final_MANIFEST.csv
    """

    output:
    path "nf_final_MANIFEST.csv"
}
process Target_first {
    input:
    path sample_file
    val setup

    script:
    """
    Target_First.py "${sample_file}"
    """

    output:
    stdout
}
process Indiegene_GE_Som {
    input:
    path sample_file
    val setup

    script:
    """
    Indiegene_GE_som.py "${sample_file}"
    """

    output:
    stdout
}
process Indiegene_GE_germ {
    input:
    path sample_file
    val setup

    script:
    """
    Indiegene_GE_germ.py "${sample_file}"
    """

    output:
    stdout
}
process Indiegene_CE_som {
    input:
    path sample_file
    val setup

    script:
    """
    Indiegene_CE_som.py "${sample_file}"
    """

    output:
    stdout
}
process Indiegene_CE_germ {
    input:
    path sample_file
    val setup

    script:
    """
    Indiegene_CE_germ.py "${sample_file}"
    """

    output:
    stdout
}
process SE8_som {
    input:
    path sample_file
    val setup

    script:
    """
    SE8_som.py "${sample_file}"
    """

    output:
    stdout
}
process SE8_germ {
    input:
    path sample_file
    val setup

    script:
    """
    SE8_germ.py "${sample_file}"
    """

    output:
    stdout
}
process CDS {
    input:
    path sample_file
    val setup

    script:
    """
    CDS.py "${sample_file}"
    """

    output:
    stdout
}
process RNA_CT {
    input:
    path sample_file
    val setup

    script:
    """
    RNA_CT.py "${sample_file}"
    """

    output:
    stdout
}
process RNA_ST8 {
    input:
    path sample_file
    val setup

    script:
    """
    RNA_ST8.py "${sample_file}"
    """

    output:
    stdout
}
process Indiegene_CEFu {
    input:
    path sample_file
    val setup

    script:
    """
    Indiegene_CEFu.py "${sample_file}"
    """

    output:
    stdout
}
// Downstream processes:
process CopySetupScript {
    input:
    val output_dir

    script:
    """
    cp ${projectDir}/bin/setup.sh "${params.output_dir}"/setup.sh
    #chmod +x "${params.output_dir}"/setup.sh
    sh "${params.output_dir}"/setup.sh
    """

    output:
    stdout
}

process QC {
    input:
    path output_dir
    path sample_file
    val setup
    val bs_status

    script:
    """
    VCF_download_QC_extract.py --output_dir "${output_dir}" --csv_file "${output_dir}/${sample_file}"
    """

    output:
    stdout
}


process CNV_FeV2 {
    publishDir params.output_dir, mode: 'copy'

    input:
    path output_dir
    path sample_file
    val setup
    val bs_status

    script:
    """
    #bash ${projectDir}/bin/CNV_New.sh "${params.output_dir}" "${params.output_dir}/${sample_file}"
    bash ${projectDir}/bin/CNV_somatic_FeV2.sh "${params.output_dir}" "${params.output_dir}/${sample_file}"
    """

    output:
    path "*", optional: true
}
process CNV_Indiegene {
    publishDir "${params.output_dir}/Indiegene", mode: 'copy'

    input:
    path output_loc
    path sample_file
    val setup
    val bs_status

    script:
    """
    bash ${projectDir}/bin/cnv_annotation_somatic_CE.sh "${params.output_dir}" "${params.output_dir}/${sample_file}"
    """

    output:
    path "*", optional: true
}

process DNA_fusion {
    publishDir "${params.output_dir}/Fusion", mode: 'copy'

    input:
    path output_dir
    path sample_file
    val setup
    val bs_status

    script:
    """
    awk -F',' 'BEGIN {OFS=","} NR > 1 {print \$(NF-2), \$4}' "${output_dir}/${sample_file}" > "${projectDir}/bin/FuSeq_WES_v1.0.0/list_test.txt"
    bash ${projectDir}/bin/FuSeq_WES_v1.0.0/FuSeq_BAM_FUS_auto.sh "${params.output_dir}" "${output_dir}/${sample_file}"
    """

    output:
    path "*_fusions", optional: true
    path "*intersected.bam", optional: true
    path "*intersected.bam.bai", optional: true
}
process Hotspot {
    publishDir "${params.output_dir}/Hotspot", mode: 'copy'

    input:
    path output_dir
    path sample_file
    val setup
    val bs_status

    script:
    """
    source "${params.output_dir}/setup.sh"
    Alternate_VariantCaller_to_Hotspot_V2_09_Apr_24.py "${output_dir}" "${output_dir}/${sample_file}"
    """

    output:
    path "*_alt_pipeline.vcf", optional: true
    path "*_Hotspot_V2.xlsx", optional: true
}

process Gene_Coverage {
    publishDir "${params.output_dir}/GeneCoverage", mode: 'copy'

    input:
    path input_dir
    path sample_file
    val setup
    val bs_status

    output:
    path "*"

    script:
    """
    source "${params.output_dir}/setup.sh"
    Gene_Coverage_via_Mosdepth_V2.py "${sample_file}" Gene_Coverage_Results.xlsx "${input_dir}"
    """
}
process bs_status_analysis {
    publishDir "${params.output_dir}", mode: 'copy'

    input:
    path output_dir
    path sample_file
    val setup
    val dummy_tf
    val dummy_ge_som
    val dummy_ge_germ
    val dummy_ce_som
    val dummy_ce_germ
    val dummy_se8_som
    val dummy_se8_germ
    val dummy_cds
    val dummy_rna_ct
    val dummy_rna_st8
    val dummy_cefu

    script:
    """
    bs_status_check.py "${sample_file}" --mount-dir "${params.output_dir}/basespace"
    """

    output:
    path "bs_status_complete.txt"
}

workflow {
    copy_setup = CopySetupScript(params.output_dir)
    Renaming(copy_setup)
    if (params.project == "new") {
        project_output = create_project(Renaming.out, params.project_name, copy_setup)
    }
    else {
        project_output = Renaming.out
    }
    extract_and_upload_samples(project_output, copy_setup)
    preprocessing_for_launch(extract_and_upload_samples.out, copy_setup)
    Target_first(preprocessing_for_launch.out, copy_setup)
    Indiegene_GE_Som(preprocessing_for_launch.out, copy_setup)
    Indiegene_GE_germ(preprocessing_for_launch.out, copy_setup)
    Indiegene_CE_som(preprocessing_for_launch.out, copy_setup)
    Indiegene_CE_germ(preprocessing_for_launch.out, copy_setup)
    SE8_som(preprocessing_for_launch.out, copy_setup)
    SE8_germ(preprocessing_for_launch.out, copy_setup)
    CDS(preprocessing_for_launch.out, copy_setup)
    RNA_CT(preprocessing_for_launch.out, copy_setup)
    RNA_ST8(preprocessing_for_launch.out, copy_setup)
    Indiegene_CEFu(preprocessing_for_launch.out, copy_setup)
    bs_status = bs_status_analysis(params.output_dir, preprocessing_for_launch.out, copy_setup, Target_first.out, Indiegene_GE_Som.out, Indiegene_GE_germ.out, Indiegene_CE_som.out, Indiegene_CE_germ.out, SE8_som.out, SE8_germ.out, CDS.out, RNA_CT.out, RNA_ST8.out, Indiegene_CEFu.out)
    QC(params.output_dir, preprocessing_for_launch.out, copy_setup, bs_status)
    CNV_FeV2(params.output_dir, preprocessing_for_launch.out, copy_setup, bs_status)
    CNV_Indiegene(params.output_dir, preprocessing_for_launch.out, copy_setup, bs_status)
    DNA_fusion(params.output_dir, preprocessing_for_launch.out, copy_setup, bs_status)
    Hotspot(params.output_dir, preprocessing_for_launch.out, copy_setup, bs_status)
    Gene_Coverage(params.output_dir, preprocessing_for_launch.out, copy_setup, bs_status)
}
