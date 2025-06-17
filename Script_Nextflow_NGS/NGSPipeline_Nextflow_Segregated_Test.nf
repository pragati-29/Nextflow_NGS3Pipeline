// Input Parameters:
params.input_dir = "path/to/input_dir"
params.sample_file = "path/to/nf_MANIFEST.csv"
params.output_dir = "path/to/output"
params.project = "old"
params.project_name = "New_Project"

// Upstream Processes:
process Renaming {
    publishDir params.output_dir, mode: 'copy'

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

    output:
    path "nf_final_MANIFEST.csv"

    script:
    """
    preprocessing_for_launch.py "${sample_file}" nf_final_MANIFEST.csv
    """
}
process Target_first {
    input:
    path sample_file

    output:
    stdout

    script:
    """
    Target_First.py "${sample_file}"
    """
}
process Indiegene_GE_Som {
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
process Indiegene_CE_som {
    input:
    path sample_file

    output:
    stdout

    script:
    """
    Indiegene_CE_som.py "${sample_file}"
    """
}
process Indiegene_CE_germ {
    input:
    path sample_file

    output:
    stdout

    script:
    """
    Indiegene_CE_germ.py "${sample_file}"
    """
}
process SE8_som {
    input:
    path sample_file

    output:
    stdout

    script:
    """
    SE8_som.py "${sample_file}"
    """
}
process SE8_germ {
    input:
    path sample_file

    output:
    stdout

    script:
    """
    SE8_germ.py "${sample_file}"
    """
}
process CDS {
    input:
    path sample_file

    output:
    stdout

    script:
    """
    CDS.py "${sample_file}"
    """
}
process RNA_CT {
    input:
    path sample_file

    output:
    stdout

    script:
    """
    RNA_CT.py "${sample_file}"
    """
}
process RNA_SE8 {
    input:
    path sample_file

    output:
    stdout

    script:
    """
    RNA_ST8.py "${sample_file}"
    """
}
process Indiegene_CEFu {
    input:
    path sample_file

    output:
    stdout

    script:
    """
    Indiegene_CEFu.py "${sample_file}"
    """
}
// Downstream processes:
process CopySetupScript {
    input:
    val output_dir

    output:
    stdout

    script:
    """
    cd "${params.output_dir}"
    #basemount basespace
    cd
    cp ${projectDir}/bin/setup.sh "${params.output_dir}"/setup.sh
    """
}

process QC {
    input:
    path output_loc
    path sample_file
    val setup

    output:
    stdout

    script:
    """
    VCF_download_QC_extract.py --output_dir "${params.output_dir}" --csv_file "${params.sample_file}"
    """
}

process CNV_FeV2 {
    publishDir params.output_dir, mode: 'copy'

    input:
    path output_loc
    path sample_file
    val setup

    output:
    path "*", optional: true

    script:
    """
    #bash ${projectDir}/bin/CNV_New.sh "${params.output_dir}" "${params.sample_file}"
    if awk -F',' 'NR>1 && \$1 == "TARGET_FIRST"' "${params.sample_file}" | grep -q .; then
        echo "Running CNV_FeV2 because TARGET_FIRST is present"
        bash ${projectDir}/bin/CNV_somatic_FeV2.sh "${params.output_dir}" "${params.sample_file}"
    else
        echo "Skipping CNV_FeV2: TARGET_FIRST not found in first column"
    fi
    """
}
process CNV_Indiegene {
    publishDir "${params.output_dir}/CNV/Indiegene", mode: 'copy'

    input:
    path output_loc
    path sample_file
    val setup

    output:
    path "*", optional: true

    script:
    """
    awk -F',' 'NR > 1 && \$1 == "INDIEGENE"' "${params.sample_file}" | while IFS=',' read -r test_name sample_type kit project file_name; do
        echo "Running CNV_Indiegene for sample:"
        bash ${projectDir}/bin/cnv_annotation_somatic_CE.sh "${params.output_dir}" "${params.sample_file}"
    done
    """
}

process DNA_fusion {
    publishDir "${params.output_dir}/Fusion", mode: 'copy'

    input:
    path output_dir
    path sample_file
    val setup

    output:
    path "*_fusions", optional: true
    path "*intersected.bam", optional: true
    path "*intersected.bam.bai", optional: true

    script:
    """
    awk -F',' 'BEGIN {OFS=","} NR > 1 {print \$(NF-2), \$4}' "${params.sample_file}" > "${projectDir}/bin/FuSeq_WES_v1.0.0/list_test.txt"
    bash ${projectDir}/bin/FuSeq_WES_v1.0.0/FuSeq_BAM_FUS_auto.sh "${params.output_dir}" "${params.sample_file}"
    """
}
process Hotspot {
    publishDir "${params.output_dir}/Hotspot", mode: 'copy'

    input:
    path output_dir
    path sample_file
    val setup

    output:
    path "*_alt_pipeline.vcf", optional: true
    path "*_Hotspot_V2.xlsx", optional: true

    script:
    """
    source "${params.output_dir}/setup.sh"
    Alternate_VariantCaller_to_Hotspot_V2_09_Apr_24.py "${output_dir}" "${sample_file}"
    """
}

process Gene_Coverage {
    publishDir "${params.output_dir}/GeneCoverage", mode: 'copy'

    input:
    path input_dir
    path sample_file
    val setup

    output:
    path "*"

    script:
    """
    source "${params.output_dir}/setup.sh"
    Gene_Coverage_via_Mosdepth_V2.py "${sample_file}" Gene_Coverage_Results.xlsx "${input_dir}"
    """
}

workflow {
    copy_setup = CopySetupScript(params.output_dir)
    QC(params.output_dir, params.sample_file, copy_setup)
    CNV_FeV2(params.output_dir, params.sample_file, copy_setup)
    CNV_Indiegene(params.output_dir, params.sample_file, copy_setup)
    DNA_fusion(params.output_dir, params.sample_file, copy_setup)
    Hotspot(params.output_dir, params.sample_file, copy_setup)
    Gene_Coverage(params.output_dir, params.sample_file, copy_setup)
}
