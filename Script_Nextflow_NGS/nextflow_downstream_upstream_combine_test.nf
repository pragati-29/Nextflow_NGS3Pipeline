nextflow.enable.dsl = 2

// ------------------ PARAMETERS ------------------
params.input_dir    = "/absolute/path/to/input_dir"
params.sample_file  = "/absolute/path/to/nf_final_MANIFEST.csv"
params.output_dir   = "/absolute/path/to/output_dir"
params.project      = "old"
params.project_name = "New_Project"

// ------------------ PROCESSES ------------------

process CopySetupScript {
    input:
    val output_dir
    output:
    stdout
    script:
    """
    cp ${projectDir}/bin/setup.sh "${output_dir}"/setup.sh
    sh "${output_dir}"/setup.sh
    """
}

process Renaming {
    publishDir params.output_dir, mode: 'copy'
    input:
    val setup
    output:
    path "bs_compliant_sample_renamed.csv"
    script:
    """
    Rename_combined.py "${params.input_dir}" "${params.sample_file}" "bs_compliant_sample_renamed.csv"
    """
}

process create_project {
    publishDir params.output_dir, mode: 'copy'
    input:
    path sample_file
    val project_name
    val setup
    output:
    path "created_proj.csv"
    script:
    """
    Create_project.py --sample_file "${sample_file}" --project_name "${project_name}"
    """
}

process extract_and_upload_samples {
    publishDir params.output_dir, mode: 'copy'
    input:
    path sample_file
    val setup
    output:
    path "preanalysis_details.csv"
    script:
    """
    bs_preanalysis.py "${sample_file}" "${params.input_dir}" preanalysis_details.csv
    """
}

process preprocessing_for_launch {
    publishDir params.output_dir, mode: 'copy'
    input:
    path sample_file
    val setup
    output:
    path "nf_final_MANIFEST.csv"
    script:
    """
    preprocessing_for_launch.py "${sample_file}" nf_final_MANIFEST.csv
    """
}

process CheckAppSession {
    publishDir "${params.output_dir}/bs_status", mode: 'copy'
    input:
    tuple val(appsession_name), val(project_name)
    output:
    path "bs_ready_${appsession_name}.txt"
    script:
    """
    bs_status_check.py --appsession-name "${appsession_name}" \
                       --project "${project_name}" \
                       --mount-dir "${params.output_dir}/basespace"
    """
}

process QC {
    input:
    tuple path(output_dir), path(sample_file), val(setup), path(bs_flag)
    output:
    stdout
    script:
    """
    VCF_download_QC_extract.py --output_dir "${output_dir}" --csv_file "${sample_file}"
    """
}

process CNV_FeV2 {
    publishDir params.output_dir, mode: 'copy'
    input:
    tuple path(output

