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
    publishDir params.output_dir, mode: 'copy'

    input:
    path sample_file
    val setup

    script:
    """
    # Step 1: Run the main Target_First script
    Target_First.py "${sample_file}"
    """

    output:
    path "FEV2_bs_status_complete.txt"
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
    path "INDIEGENE_bs_status_complete.txt"
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
    path file_in from a_out

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
    path file_in from a_out

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
    path file_in from a_out

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
    path file_in from a_out

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
    path file_in from a_out

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
    path file_in from a_out

    script:
    """
    source "${params.output_dir}/setup.sh"
    Gene_Coverage_via_Mosdepth_V2.py "${sample_file}" Gene_Coverage_Results.xlsx "${input_dir}"
    """

    output:
    path "*"
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
    Indiegene_CE_som(preprocessing_for_launch.out, copy_setup)
    Channel.fromPath(['FEV2_bs_status_complete.txt', 'INDIEGENE_bs_status_complete.txt']).set { a_out } //combined_out  (comb_comp_marker = target_first_out.mix(indiegene_ce_out)  )
    QC(params.output_dir, preprocessing_for_launch.out, copy_setup, Target_first.out)
    CNV_FeV2(params.output_dir, preprocessing_for_launch.out, copy_setup, Target_first.out)
    CNV_Indiegene(params.output_dir, preprocessing_for_launch.out, copy_setup, Target_first.out)
    DNA_fusion(params.output_dir, preprocessing_for_launch.out, copy_setup, Target_first.out)
    Hotspot(params.output_dir, preprocessing_for_launch.out, copy_setup, Target_first.out)
    Gene_Coverage(params.output_dir, preprocessing_for_launch.out, copy_setup, Target_first.out)
}
